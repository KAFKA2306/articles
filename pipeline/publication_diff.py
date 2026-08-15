from __future__ import annotations

import argparse
import re
import subprocess
from dataclasses import dataclass

from pipeline.zenn_slug import validate_article_paths


@dataclass(frozen=True)
class PublicationState:
    published: bool
    published_at: str | None


def parse_state(text: str | None) -> PublicationState | None:
    if text is None or not text.startswith("---\n"):
        return None
    parts = text.split("---\n", 2)
    if len(parts) < 3:
        return None
    front = parts[1]
    published_match = re.search(
        r"^published:\s*(true|false)\s*(?:#.*)?$", front, re.MULTILINE
    )
    published_at_match = re.search(
        r"^published_at:\s*([^#\n]+?)\s*(?:#.*)?$", front, re.MULTILINE
    )
    return PublicationState(
        published=bool(published_match and published_match.group(1) == "true"),
        published_at=(
            published_at_match.group(1).strip() if published_at_match else None
        ),
    )


def validate_transition(
    changes: list[tuple[str, PublicationState | None, PublicationState | None]],
    *,
    original_published_at: dict[str, str | None] | None = None,
) -> list[str]:
    errors: list[str] = []
    promotions: list[str] = []
    origins = original_published_at or {}

    for path, old, new in changes:
        if new is None:
            continue
        old_published = old.published if old else False
        if new.published and not old_published:
            promotions.append(path)

        if old and old.published_at is not None and old.published_at != new.published_at:
            origin = origins.get(path)
            restoring_origin = origin is not None and new.published_at == origin
            if not restoring_origin:
                errors.append(
                    f"{path}: published_at is immutable once specified "
                    f"({old.published_at!r} -> {new.published_at!r}); "
                    f"only restoration to the first repository value {origin!r} is allowed"
                )

    if len(promotions) > 1:
        errors.append(
            "at most one article may transition to published:true per change; "
            f"found {len(promotions)}: {', '.join(promotions)}"
        )
    return errors


def _git(*args: str, check: bool = True) -> str:
    result = subprocess.run(
        ["git", *args],
        check=check,
        capture_output=True,
        text=True,
    )
    return result.stdout


def _show(ref: str, path: str) -> str | None:
    result = subprocess.run(
        ["git", "show", f"{ref}:{path}"],
        capture_output=True,
        text=True,
    )
    return result.stdout if result.returncode == 0 else None


def find_original_published_at(path: str, head: str) -> str | None:
    """Return the first non-null published_at ever committed for this path."""
    history = _git("log", "--reverse", "--format=%H", head, "--", path)
    for commit in (line.strip() for line in history.splitlines()):
        if not commit:
            continue
        state = parse_state(_show(commit, path))
        if state and state.published_at is not None:
            return state.published_at
    return None


def collect_article_paths(head: str) -> list[str]:
    output = _git("ls-tree", "-r", "--name-only", head, "--", "articles")
    return [
        path
        for path in (line.strip() for line in output.splitlines())
        if path.endswith(".md")
    ]


def collect_changes(
    base: str, head: str
) -> list[tuple[str, PublicationState | None, PublicationState | None]]:
    output = _git("diff", "--name-only", base, head, "--", "articles/*.md")
    changes: list[tuple[str, PublicationState | None, PublicationState | None]] = []
    for path in (line.strip() for line in output.splitlines()):
        if not path:
            continue
        changes.append(
            (path, parse_state(_show(base, path)), parse_state(_show(head, path)))
        )
    return changes


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Guard Zenn publication transitions before deploy."
    )
    parser.add_argument("--base", required=True)
    parser.add_argument("--head", required=True)
    args = parser.parse_args()

    changes = collect_changes(args.base, args.head)
    origins = {
        path: find_original_published_at(path, args.head)
        for path, _old, _new in changes
    }
    errors = validate_article_paths(collect_article_paths(args.head))
    errors.extend(validate_transition(changes, original_published_at=origins))
    if errors:
        for error in errors:
            print(f"PUBLICATION_DIFF_FAIL: {error}")
        return 1

    repaired = [
        path
        for path, old, new in changes
        if old
        and new
        and old.published_at != new.published_at
        and new.published_at == origins.get(path)
    ]
    for path in repaired:
        print(
            f"PUBLICATION_DIFF_REPAIR: {path} restored published_at={origins[path]!r}"
        )

    promoted = [
        path
        for path, old, new in changes
        if new and new.published and not (old and old.published)
    ]
    print(
        f"PUBLICATION_DIFF_PASS: promotions={len(promoted)} repairs={len(repaired)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
