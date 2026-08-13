from __future__ import annotations


def check_source(source: str) -> str:
    try:
        compile(source, "<reader-input>", "exec")
    except SyntaxError as exc:
        line = exc.lineno or 0
        message = exc.msg or "SyntaxError"
        return f"SYNTAX_ERROR line={line}: {message}"
    return "COMPILE_OK"


check_source(DEMO_INPUT)
