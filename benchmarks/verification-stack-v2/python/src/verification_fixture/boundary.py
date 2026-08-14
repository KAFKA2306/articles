from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def load_unknown_payload(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise TypeError("payload must be an object")
    return value
