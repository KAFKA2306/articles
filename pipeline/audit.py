from __future__ import annotations

import re

from . import core

LEGACY_ROOT_FILES = {
    "ARTICLE_FACTORY.md",
    "C2H5OH.md",
    "index.html",
}
LEGACY_DIRS = {"article_factory", "candidates", "reports"}
FORBIDDEN_PUBLIC_MARKERS = (
    "PRIVATE_GRAPHITI_DIARY:",
    "PRIVATE_WEEKLY_CONTEXT:",
)


def fail(message: str) -> None:
    raise SystemExit(f"AUDIT_FAIL: {message}")


def audit_layout() -> None:
    for name in LEGACY_ROOT_FILES:
        if (core.ROOT / name).exists():
            fail(f"legacy root file remains: {name}")
    for name in LEGACY_DIRS:
        if (core.ROOT / name).exists():
            fail(f"legacy directory remains: {name}")

    required = [
        core.ROOT / "README.md",
        core.ROOT / "pipeline" / "config.json",
        core.ROOT / "pipeline" / "cli.py",
        core.ROOT / "pipeline" / "core.py",
        core.ROOT / "pipeline" / "graphiti.py",
        core.ROOT / "docs" / "ARCHITECTURE.md",
        core.ROOT / "docs" / "GRAPHITI_WEEKLY.md",
    ]
    for path in required:
        if not path.exists():
            fail(f"required path missing: {path.relative_to(core.ROOT)}")


def audit_config() -> None:
    gate = core.CONFIG["quality_gate"]
    if core.CONFIG.get("evaluation_kind") != "internal_lapras_rubric_proxy":
        fail("evaluation_kind must identify the internal LAPRAS-rubric proxy")
    if int(core.CONFIG.get("monthly_publication_limit", 0)) != 1:
        fail("monthly_publication_limit must be exactly 1")
    if float(gate["target_overall"]) < 4.0:
        fail("target_overall must be >= 4.0")
    if float(gate["minimum_overall"]) < 3.5:
        fail("minimum_overall must be >= 3.5")
    if float(gate["minimum_axis"]) < 3.5:
        fail("minimum_axis must be >= 3.5")
    if int(gate["minimum_primary_sources"]) < 3:
        fail("minimum_primary_sources must be >= 3")
    if int(gate["minimum_own_github_evidence"]) < 2:
        fail("minimum_own_github_evidence must be >= 2")


def audit_privacy() -> None:
    for key in ("candidates", "reports", "published"):
        base = core.output_dir(key)
        if not base.exists():
            continue
        for path in base.rglob("*"):
            if not path.is_file():
                continue
            text = path.read_text(encoding="utf-8", errors="ignore")
            for marker in FORBIDDEN_PUBLIC_MARKERS:
                if marker in text:
                    fail(
                        "private Graphiti context leaked into "
                        f"{path.relative_to(core.ROOT)}"
                    )


def audit_articles() -> None:
    base = core.output_dir("published")
    if not base.exists():
        return
    for path in base.glob("*.md"):
        text = path.read_text(encoding="utf-8", errors="ignore")
        if not text.startswith("---\n"):
            fail(f"missing front matter: {path}")
        if "pipeline_meta:" in text:
            fail(f"candidate metadata leaked into published article: {path}")
        if "published: true" in text and not re.search(
            r"^published_at: \d{4}-\d{2}-\d{2}",
            text,
            re.MULTILINE,
        ):
            fail(f"published article lacks published_at: {path}")


def main() -> int:
    audit_layout()
    audit_config()
    audit_privacy()
    audit_articles()
    print("AUDIT_PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
