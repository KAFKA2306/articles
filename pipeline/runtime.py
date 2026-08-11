from __future__ import annotations

import json
from typing import Any

from . import core


def extract_json_object(text: str) -> dict[str, Any]:
    """Extract the first valid JSON object from a model response.

    Copilot CLI silent mode returns only the agent response, but a model can still
    prepend prose or wrap JSON in Markdown. The pipeline contract is an object,
    so scan for the first decodable object and normalize it before callers parse it.
    """
    decoder = json.JSONDecoder()
    for index, char in enumerate(text):
        if char != "{":
            continue
        try:
            value, _ = decoder.raw_decode(text[index:])
        except json.JSONDecodeError:
            continue
        if isinstance(value, dict):
            return value
    raise RuntimeError(
        "Copilot response did not contain a valid JSON object; "
        f"response_prefix={text[:240]!r}"
    )


def install_robust_model_call() -> None:
    """Make JSON-mode calls tolerant of harmless response decoration."""
    original = core.model_call
    if getattr(original, "_articles_json_normalizer", False):
        return

    def wrapped(
        system: str,
        user: str,
        *,
        temperature: float = 0.2,
        json_mode: bool = False,
    ) -> str:
        if not json_mode:
            return original(
                system,
                user,
                temperature=temperature,
                json_mode=False,
            )

        strict_user = (
            user.rstrip()
            + "\n\nOUTPUT CONTRACT:\n"
            + "Return exactly one valid JSON object. Do not add prose before or "
            + "after the object and do not use Markdown fences."
        )
        raw = original(
            system,
            strict_user,
            temperature=temperature,
            json_mode=False,
        )
        normalized = extract_json_object(raw)
        return json.dumps(normalized, ensure_ascii=False)

    setattr(wrapped, "_articles_json_normalizer", True)
    core.model_call = wrapped
