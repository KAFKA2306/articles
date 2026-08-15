from __future__ import annotations

import re
from datetime import datetime
from pathlib import Path

from .zenn_slug import require_valid_slug


SAFE_TITLE_RE = re.compile(r"[^a-z0-9]+")
MANAGED_SLUG_RE = re.compile(
    r"^(?P<date>\d{4}-\d{2}-\d{2})-(?P<number>\d{2})-(?P<title>[a-z0-9]+(?:-[a-z0-9]+)*)$"
)


def normalize_file_title(value: str, *, max_length: int = 36) -> str:
    """Normalize a human-readable ASCII file-title stem for a Zenn slug."""
    normalized = SAFE_TITLE_RE.sub("-", value.lower()).strip("-")
    normalized = re.sub(r"-+", "-", normalized)
    normalized = normalized[:max_length].rstrip("-")
    if not normalized:
        raise ValueError("file_title must contain at least one ASCII letter or digit")
    return normalized


def next_publication_slug(
    file_title: str,
    *,
    moment: datetime,
    published_dir: Path,
    sequence_width: int = 2,
    max_slug_length: int = 50,
) -> str:
    """Return a validated YYYY-MM-DD-NN-title slug without filesystem mutation."""
    date_prefix = moment.strftime("%Y-%m-%d")
    title_budget = max_slug_length - len(date_prefix) - sequence_width - 2
    if title_budget < 1:
        raise ValueError("max_slug_length is too short for the filename contract")
    title = normalize_file_title(file_title, max_length=title_budget)

    used_numbers: list[int] = []
    if published_dir.exists():
        for path in published_dir.glob(f"{date_prefix}-*.md"):
            match = MANAGED_SLUG_RE.fullmatch(path.stem)
            if match:
                used_numbers.append(int(match.group("number")))

    number = max(used_numbers, default=0) + 1
    if number >= 10**sequence_width:
        raise ValueError("daily article sequence exhausted")

    slug = f"{date_prefix}-{number:0{sequence_width}d}-{title}"
    return require_valid_slug(slug)


def is_managed_slug(slug: str) -> bool:
    return MANAGED_SLUG_RE.fullmatch(slug) is not None
