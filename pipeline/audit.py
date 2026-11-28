from __future__ import annotations

from pathlib import Path

from . import evidence_gate

ROOT = Path(__file__).resolve().parents[1]
FORBIDDEN_PRIVATE_MARKERS = ("PRIVATE_GRAPHITI_DIARY:", "PRIVATE_WEEKLY_CONTEXT:")


def main() -> int:
    required = (
        "README.md",
        "AGENTS.md",
        ".github/workflows/article-pipeline-ci.yml",
        ".github/workflows/zenn-manual-release.yml",
        ".github/workflows/zenn-production-verify.yml",
        "pipeline/evidence_gate.py",
        "pipeline/zenn_slug.py",
        "pipeline/publication_diff.py",
    )
    missing = [item for item in required if not (ROOT / item).is_file()]
    if missing:
        raise SystemExit("AUDIT_FAIL: required files missing: " + ", ".join(missing))
    leaked = []
    for path in sorted((ROOT / "articles").glob("*.md")):
        text = path.read_text(encoding="utf-8")
        for marker in FORBIDDEN_PRIVATE_MARKERS:
            if marker in text:
                leaked.append(f"{path}: private marker {marker}")
    if leaked:
        raise SystemExit("AUDIT_FAIL: " + "; ".join(leaked))
    evidence_gate.main()
    print("AUDIT_PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
