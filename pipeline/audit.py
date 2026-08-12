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
CANONICAL_RATCHET_KPIS = [
    "publication_pass_rate",
    "primary_source_rate",
    "manual_corrections",
]


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
        core.ROOT / "pipeline" / "editorial.py",
        core.ROOT / "pipeline" / "runtime.py",
        core.ROOT / "pipeline" / "graphiti.py",
        core.ROOT / "pipeline" / "selection.py",
        core.ROOT / "pipeline" / "contracts" / "article.md",
        core.ROOT / "docs" / "ARCHITECTURE.md",
        core.ROOT / "docs" / "EDITORIAL_DESIGN.md",
        core.ROOT / "docs" / "GRAPHITI_WEEKLY.md",
    ]
    for path in required:
        if not path.exists():
            fail(f"required path missing: {path.relative_to(core.ROOT)}")


def audit_config() -> None:
    gate = core.CONFIG["quality_gate"]
    if float(gate["target_overall"]) < 4.0:
        fail("target_overall must be >= 4.0")
    if float(gate["minimum_overall"]) < 3.5:
        fail("minimum_overall must be >= 3.5")
    if float(gate["minimum_axis"]) < 3.5:
        fail("minimum_axis must be >= 3.5")
    if float(gate["target_story_overall"]) < 4.2:
        fail("target_story_overall must be >= 4.2")
    if float(gate["minimum_story_overall"]) < 3.9:
        fail("minimum_story_overall must be >= 3.9")
    if float(gate["minimum_story_axis"]) < 3.7:
        fail("minimum_story_axis must be >= 3.7")
    if float(gate["minimum_interest"]) < 4.0:
        fail("minimum_interest must be >= 4.0")
    if int(gate["minimum_primary_sources"]) < 3:
        fail("minimum_primary_sources must be >= 3")
    if int(gate["minimum_own_github_evidence"]) < 2:
        fail("minimum_own_github_evidence must be >= 2")
    if int(core.CONFIG.get("candidate_count", 0)) < 6:
        fail("candidate_count must be >= 6 for editorial selection")
    if core.CONFIG.get("evaluation_kind") != "internal_lapras_rubric_proxy":
        fail("evaluation_kind must declare internal proxy semantics")
    if core.CONFIG.get("editorial_evaluation_kind") != "story_interest_proxy":
        fail("editorial_evaluation_kind must declare story-interest semantics")
    if list(core.CONFIG.get("editorial_axes", [])) != [
        "interest",
        "discovery",
        "narrative",
        "context",
    ]:
        fail("editorial_axes contract changed")
    if int(core.CONFIG.get("monthly_publication_limit", 0)) != 1:
        fail("monthly_publication_limit must be exactly 1")
    if core.CONFIG.get("model_provider") != "github-copilot-cli":
        fail("model_provider must use github-copilot-cli")
    source = (core.ROOT / "pipeline" / "core.py").read_text(encoding="utf-8")
    if "models.github.ai" in source:
        fail("retired GitHub Models endpoint remains in core.py")

    if list(core.CONFIG.get("ratchet_kpis", [])) != CANONICAL_RATCHET_KPIS:
        fail("ratchet_kpis must be exactly the three canonical outcome KPIs")
    image_policy = core.CONFIG.get("image_policy", {})
    if image_policy.get("objective") != "reader_comprehension":
        fail("image policy must optimize reader comprehension")
    if image_policy.get("fixed_count") is not None:
        fail("image policy must not require a fixed image count")
    if image_policy.get("require_explanatory_value") is not True:
        fail("every generated diagram must have explanatory value")


def audit_editorial_contract() -> None:
    contract = (
        core.ROOT / "pipeline" / "contracts" / "article.md"
    ).read_text(encoding="utf-8")
    required_markers = (
        "ひとつの発見",
        "冒頭300文字",
        "initial_hypothesis",
        "hypothesis_update",
        "story_overall",
        "interest",
        "discovery",
        "narrative",
        "context",
        "一文で持ち帰れる結論",
    )
    for marker in required_markers:
        if marker not in contract:
            fail(f"editorial contract missing: {marker}")

    cli = (core.ROOT / "pipeline" / "cli.py").read_text(encoding="utf-8")
    if "install_editorial_pipeline()" not in cli:
        fail("editorial pipeline is not installed by cli.py")


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
        if "published: true" in text and not re.search(
            r"^published_at: \d{4}-\d{2}-\d{2}",
            text,
            re.MULTILINE,
        ):
            fail(f"published article lacks published_at: {path}")


def main() -> int:
    audit_layout()
    audit_config()
    audit_editorial_contract()
    audit_privacy()
    audit_articles()
    print("AUDIT_PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
