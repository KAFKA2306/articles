from __future__ import annotations

import argparse
import re
from collections.abc import Iterable
from datetime import date
from pathlib import Path


ZENN_SLUG_RE = re.compile(r"^[a-z0-9_-]{12,50}$")
DATED_SLUG_RE = re.compile(
    r"^(?P<date>\d{4}-\d{2}-\d{2})-(?P<sequence>\d{2})-[a-z0-9]+(?:-[a-z0-9]+)*$"
)
FRONTMATTER_RE = re.compile(r"\A---\n(?P<fields>[\s\S]*?)\n---\n")


class InvalidZennSlug(ValueError):
    """Raised before any filesystem mutation when a proposed Zenn slug is invalid."""


def validate_slug(slug: str) -> list[str]:
    if ZENN_SLUG_RE.fullmatch(slug):
        return []
    return [
        f"invalid Zenn slug {slug!r}: expected 12-50 characters using only "
        "lowercase a-z, 0-9, hyphen (-), or underscore (_)"
    ]


def require_valid_slug(slug: str) -> str:
    """Return slug unchanged or raise before a file path is materialized."""
    errors = validate_slug(slug)
    if errors:
        raise InvalidZennSlug(errors[0])
    return slug


def article_path_for_slug(articles_dir: Path, slug: str) -> Path:
    """Build an article path only after validating the exact final slug."""
    return articles_dir / f"{require_valid_slug(slug)}.md"


def create_article_file(articles_dir: Path, slug: str, content: str) -> Path:
    """Atomically create one Zenn article after validating its final slug.

    Invalid slugs fail before mkdir/open. Existing paths fail rather than overwrite.
    """
    path = article_path_for_slug(articles_dir, slug)
    date_errors = validate_new_article(str(path), content)
    if date_errors:
        raise InvalidZennSlug("; ".join(date_errors))
    articles_dir.mkdir(parents=True, exist_ok=True)
    try:
        with path.open("x", encoding="utf-8", newline="\n") as handle:
            handle.write(content)
    except FileExistsError as exc:
        raise FileExistsError(f"article already exists: {path}") from exc
    return path



def validate_article_metadata(path: str, content: str) -> list[str]:
    """The editorial dates are distinct from Zenn's published_at."""
    match = FRONTMATTER_RE.match(content)
    if not match:
        return [f"{path}: missing YAML front matter"]
    fields = match.group("fields")
    dates: dict[str, date] = {}
    errors: list[str] = []
    for key in ("created_at", "updated_at"):
        found = re.search(
            rf"""^{key}:\s*['"]?(\d{{4}}-\d{{2}}-\d{{2}})['"]?\s*$""",
            fields,
            re.MULTILINE,
        )
        if not found:
            errors.append(f"{path}: missing or invalid {key} (YYYY-MM-DD)")
            continue
        try:
            dates[key] = date.fromisoformat(found.group(1))
        except ValueError:
            errors.append(f"{path}: invalid calendar date for {key}")
    if len(dates) == 2 and dates["updated_at"] < dates["created_at"]:
        errors.append(f"{path}: updated_at precedes created_at")
    return errors


def validate_new_article(path: str, content: str) -> list[str]:
    """New articles require dated slugs; published legacy slugs never change."""
    errors = validate_article_metadata(path, content)
    slug = Path(path).stem
    match = DATED_SLUG_RE.fullmatch(slug)
    if not match or validate_slug(slug):
        return [f"{path}: new article slug must use YYYY-MM-DD-NN-title"] + errors
    try:
        date.fromisoformat(match.group("date"))
    except ValueError:
        return [f"{path}: invalid date prefix"] + errors
    created = re.search(
        r"""^created_at:\s*['"]?(\d{4}-\d{2}-\d{2})['"]?\s*$""",
        content.split("---\n", 2)[1] if content.startswith("---\n") else "",
        re.MULTILINE,
    )
    if created and created.group(1) != match.group("date"):
        errors.append(f"{path}: filename date must equal created_at")
    return errors


def validate_article_paths(paths: Iterable[str]) -> list[str]:
    errors: list[str] = []
    for raw_path in paths:
        path = raw_path.replace("\\", "/")
        if not path.startswith("articles/") or not path.endswith(".md"):
            continue
        slug = path.removeprefix("articles/").removesuffix(".md")
        slug_errors = validate_slug(slug)
        errors.extend(f"{path}: {error}" for error in slug_errors)
    return errors


def collect_repository_article_paths(root: Path = Path(".")) -> list[str]:
    articles_dir = root / "articles"
    if not articles_dir.is_dir():
        return []
    return [
        path.relative_to(root).as_posix()
        for path in sorted(articles_dir.rglob("*.md"))
    ]


def validate_repository(root: Path = Path(".")) -> list[str]:
    paths = collect_repository_article_paths(root)
    errors = validate_article_paths(paths)
    for path in paths:
        errors.extend(validate_article_metadata(path, (root / path).read_text(encoding="utf-8")))
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Fail closed when a Zenn article filename is not a valid slug."
    )
    parser.add_argument(
        "--slug",
        action="append",
        default=[],
        help="Validate one proposed slug instead of scanning articles/*.md.",
    )
    parser.add_argument(
        "--root",
        type=Path,
        default=Path("."),
        help="Repository root used for the default full articles scan.",
    )
    args = parser.parse_args()

    if args.slug:
        errors = [
            f"slug {slug!r}: {error}"
            for slug in args.slug
            for error in validate_slug(slug)
        ]
        checked = len(args.slug)
    else:
        paths = collect_repository_article_paths(args.root)
        errors = validate_repository(args.root)
        checked = len(paths)

    if errors:
        for error in errors:
            print(f"ZENN_SLUG_FAIL: {error}")
        return 1

    print(f"ZENN_SLUG_PASS: checked={checked}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
