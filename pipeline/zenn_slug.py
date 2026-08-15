from __future__ import annotations

import argparse
import re
from collections.abc import Iterable
from pathlib import Path


ZENN_SLUG_RE = re.compile(r"^[a-z0-9_-]{12,50}$")


def validate_slug(slug: str) -> list[str]:
    if ZENN_SLUG_RE.fullmatch(slug):
        return []
    return [
        f"invalid Zenn slug {slug!r}: expected 12-50 characters using only "
        "lowercase a-z, 0-9, hyphen (-), or underscore (_)"
    ]


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
    return validate_article_paths(collect_repository_article_paths(root))


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
        errors = validate_article_paths(paths)
        checked = len(paths)

    if errors:
        for error in errors:
            print(f"ZENN_SLUG_FAIL: {error}")
        return 1

    print(f"ZENN_SLUG_PASS: checked={checked}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
