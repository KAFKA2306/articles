from __future__ import annotations

import sys
from pathlib import Path


def normalize(path: Path) -> None:
    text = path.read_text(encoding="utf-8")
    lines = [line.rstrip(" \t") for line in text.splitlines()]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    for raw in sys.argv[1:]:
        normalize(Path(raw))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
