from __future__ import annotations

import argparse
import re
import subprocess
from dataclasses import dataclass


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
    published_match = re.search(r"^published:\s*(true|false)\s*(?:#.*)?$", front, re.MULTILINE)
    published_at_match = re.search(r"^published_at:\s*([^#\n]+?)\s*(?:#.*)?$", front, re.MULTILINE)
    return PublicationState(
        published=bool(published_match and published_match.group(1) == "true"),
        published_at=(published_at_match.group(1).strip() if published_at_match else None),
    )


def validate_transition(
    changes: list[tuple[str, PublicationState | None, PublicationState | None]],
) -> list[str]:
    errors: list[str] = []
    promotions: list[str] = []
    for path, old, new in changes:
        if new is None:
            continue
        old_published = old.published if old else False
        if new.published and not old_published:
            promotions.append(path)
        if old and old.published_at is not None and old.published_at != new.published_at:
            errors.append(
                f"{path}: published_at is immutable once specified "
                f"({old.published_at!r} -> {new.published_at!r})"
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


def collect_changes(base: str, head: str) -> list[tuple[str, PublicationState | None, PublicationState | None]]:
    output = _git("diff", "--name-only", base, head, "--", "articles/*.md")
    changes: list[tuple[str, PublicationState | None, PublicationState | None]] = []
    for path in (line.strip() for line in output.splitlines()):
        if not path:
            continue
        changes.append((path, parse_state(_show(base, path)), parse_state(_show(head, path))))
    return changes


def main() -> int:
    parser = argparse.ArgumentParser(description="Guard Zenn publication transitions before deploy.")
    parser.add_argument("--base", required=True)
    parser.add_argument("--head", required=True)
    args = parser.parse_args()

    changes = collect_changes(args.base, args.head)
    errors = validate_transition(changes)
    if errors:
        for error in errors:
            print(f"PUBLICATION_DIFF_FAIL: {error}")
        return 1
    promoted = [path for path, old, new in changes if new and new.published and not (old and old.published)]
    print(f"PUBLICATION_DIFF_PASS: promotions={len(promoted)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
