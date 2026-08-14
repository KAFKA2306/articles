from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent
STATE_PATH = ROOT / "state.json"

PHASES = [
    "design_frozen",
    "fixtures_frozen",
    "harness_ready",
    "controlled_results_ready",
    "real_repo_sample_frozen",
    "external_validity_ready",
    "evidence_classified",
    "story_candidates_ready",
    "article_candidate_ready",
]

EXPECTED_MUTANTS = {
    "PY-SYNTAX-001",
    "PY-FORMAT-001",
    "PY-LINT-001",
    "PY-TYPE-ARG-001",
    "PY-TYPE-RETURN-001",
    "PY-NAME-001",
    "PY-ASYNC-001",
    "PY-RUNTIME-001",
    "TS-SYNTAX-001",
    "TS-FORMAT-001",
    "TS-LINT-001",
    "TS-TYPE-ARG-001",
    "TS-TYPE-RETURN-001",
    "TS-PROMISE-001",
    "TS-RUNTIME-001",
    "WS-AFFECTED-CORE-001",
    "WS-AFFECTED-UI-001",
    "WS-AFFECTED-DOCS-001",
    "WS-CACHE-HIT-001",
    "WS-CACHE-INVALIDATE-001",
    "WS-BOUNDARY-001",
    "HOOK-PATCH-PARITY-001",
}

REQUIRED_FIXTURE_FILES = [
    "PROTOCOL.md",
    "FIXTURE_DESIGN.md",
    "RESULTS_SCHEMA.md",
    "EDITORIAL_GOAL.md",
    "AUTONOMY.md",
    "AMENDMENT-v2.1-before-comparison.md",
    "mutants.json",
    "python/pyproject.toml",
    "python/src/verification_fixture/models.py",
    "python/src/verification_fixture/service.py",
    "python/src/verification_fixture/boundary.py",
    "python/tests/test_service.py",
    "python/tests/payload.json",
    "typescript/package.json",
    "typescript/package-lock.json",
    "typescript/tsconfig.json",
    "typescript/src/service.ts",
    "typescript/src/boundary.ts",
    "typescript/test/payload.json",
    "workspace/package.json",
    "workspace/ground-truth.json",
    "workspace/packages/core/package.json",
    "workspace/packages/core/src/value.ts",
    "workspace/packages/ui/package.json",
    "workspace/packages/ui/src/value.ts",
    "workspace/packages/docs/package.json",
    "workspace/packages/docs/src/value.ts",
    "workspace/apps/web/package.json",
    "workspace/apps/web/src/value.ts",
    "workspace/apps/api/package.json",
    "workspace/apps/api/src/value.ts",
    "hooks/.pre-commit-config.yaml",
    "hooks/fixer.py",
    "hooks/fixtures/input.txt",
]


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def json_complete(path: Path) -> bool:
    if not path.exists():
        return False
    value = read_json(path)
    return value.get("status") == "complete"


def fixtures_gate() -> tuple[bool, str | None]:
    missing = [rel for rel in REQUIRED_FIXTURE_FILES if not (ROOT / rel).exists()]
    if missing:
        return False, f"missing_fixture:{missing[0]}"

    manifest = read_json(ROOT / "mutants.json")
    if manifest.get("frozen_before_comparison") is not True:
        return False, "mutant_manifest_not_frozen"
    ids = {item["id"] for item in manifest.get("mutants", [])}
    if ids != EXPECTED_MUTANTS:
        return False, "mutant_set_mismatch"

    for item in manifest["mutants"]:
        target = item.get("target")
        if target and not (ROOT / target).exists():
            return False, f"missing_mutant_target:{item['id']}"
    return True, None


def harness_gate() -> tuple[bool, str | None]:
    required = ["harness.py", "candidate-versions.json", "candidate-adapters.json"]
    for rel in required:
        if not (ROOT / rel).exists():
            return False, f"missing_harness_input:{rel}"
    return True, None


def controlled_results_gate() -> tuple[bool, str | None]:
    path = ROOT / "results" / "controlled" / "summary.json"
    return (True, None) if json_complete(path) else (False, "controlled_results_incomplete")


def real_repo_gate() -> tuple[bool, str | None]:
    path = ROOT / "real-repo-sample.json"
    if not path.exists():
        return False, "real_repo_sample_not_frozen"
    value = read_json(path)
    if value.get("frozen_before_candidate_output_review") is not True:
        return False, "real_repo_sample_not_preregistered"
    return True, None


def external_gate() -> tuple[bool, str | None]:
    path = ROOT / "results" / "external" / "summary.json"
    return (True, None) if json_complete(path) else (False, "external_results_incomplete")


def classification_gate() -> tuple[bool, str | None]:
    path = ROOT / "evidence-classification.json"
    return (True, None) if json_complete(path) else (False, "evidence_not_classified")


def story_candidates_gate() -> tuple[bool, str | None]:
    path = ROOT / "story-candidates.json"
    if not path.exists():
        return False, "story_candidates_missing"
    value = read_json(path)
    candidates = value.get("candidates", [])
    if len(candidates) < 3:
        return False, "need_three_competing_story_candidates"
    required = {"falsifiable", "measured", "externally_plausible", "decision_changing", "non_obvious", "bounded"}
    for candidate in candidates:
        if not required.issubset(candidate.get("gate", {})):
            return False, "story_candidate_gate_fields_missing"
    return True, None


def article_gate() -> tuple[bool, str | None, str | None]:
    selection_path = ROOT / "story-selection.json"
    if not selection_path.exists():
        return False, "story_selection_missing", None
    selection = read_json(selection_path)
    outcome = selection.get("outcome")
    if outcome == "no_article":
        return True, None, "no_article"
    if outcome != "article_candidate_ready":
        return False, "invalid_story_selection_outcome", None
    candidate = selection.get("candidate_path")
    if not candidate:
        return False, "candidate_path_missing", None
    repo_root = ROOT.parents[1]
    if not (repo_root / candidate).exists():
        return False, "candidate_file_missing", None
    return True, None, "article_candidate_ready"


def advance(state: dict[str, Any]) -> dict[str, Any]:
    if state.get("publication_authorized") is not False:
        raise RuntimeError("publication_authorized must remain false in this controller")

    while True:
        phase = state["phase"]
        if phase == "design_frozen":
            ok, blocker = fixtures_gate()
            if not ok:
                state["blocked_on"] = blocker
                break
            state.update(phase="fixtures_frozen", blocked_on="neutral_harness", last_transition="design_frozen->fixtures_frozen")
        elif phase == "fixtures_frozen":
            ok, blocker = harness_gate()
            if not ok:
                state["blocked_on"] = blocker
                break
            state.update(phase="harness_ready", blocked_on="controlled_results", last_transition="fixtures_frozen->harness_ready")
        elif phase == "harness_ready":
            ok, blocker = controlled_results_gate()
            if not ok:
                state["blocked_on"] = blocker
                break
            state.update(phase="controlled_results_ready", comparison_started=True, blocked_on="real_repo_sample", last_transition="harness_ready->controlled_results_ready")
        elif phase == "controlled_results_ready":
            ok, blocker = real_repo_gate()
            if not ok:
                state["blocked_on"] = blocker
                break
            state.update(phase="real_repo_sample_frozen", real_repo_sample_frozen=True, blocked_on="external_validity", last_transition="controlled_results_ready->real_repo_sample_frozen")
        elif phase == "real_repo_sample_frozen":
            ok, blocker = external_gate()
            if not ok:
                state["blocked_on"] = blocker
                break
            state.update(phase="external_validity_ready", blocked_on="evidence_classification", last_transition="real_repo_sample_frozen->external_validity_ready")
        elif phase == "external_validity_ready":
            ok, blocker = classification_gate()
            if not ok:
                state["blocked_on"] = blocker
                break
            state.update(phase="evidence_classified", blocked_on="story_candidates", last_transition="external_validity_ready->evidence_classified")
        elif phase == "evidence_classified":
            ok, blocker = story_candidates_gate()
            if not ok:
                state["blocked_on"] = blocker
                break
            state.update(phase="story_candidates_ready", blocked_on="story_selection", last_transition="evidence_classified->story_candidates_ready")
        elif phase == "story_candidates_ready":
            ok, blocker, outcome = article_gate()
            if not ok:
                state["blocked_on"] = blocker
                break
            state.update(phase=outcome, blocked_on=None, last_transition=f"story_candidates_ready->{outcome}")
            break
        elif phase in {"article_candidate_ready", "no_article"}:
            state["blocked_on"] = None
            break
        else:
            raise RuntimeError(f"unknown phase: {phase}")
    return state


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write-state", action="store_true")
    args = parser.parse_args()

    state = read_json(STATE_PATH)
    before = json.dumps(state, sort_keys=True)
    state = advance(state)
    after = json.dumps(state, sort_keys=True)
    print(json.dumps(state, indent=2, sort_keys=True))

    if args.write_state and before != after:
        STATE_PATH.write_text(json.dumps(state, indent=2, sort_keys=True) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
