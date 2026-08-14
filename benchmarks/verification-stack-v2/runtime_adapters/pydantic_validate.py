from __future__ import annotations

import json
import sys
from pathlib import Path

from pydantic import BaseModel, Field, ValidationError


class Payload(BaseModel):
    count: int = Field(gt=0)
    label: str


def main() -> int:
    raw = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
    try:
        Payload.model_validate(raw)
    except ValidationError as exc:
        print(exc)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
