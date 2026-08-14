from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
RESULTS = ROOT / "results" / "controlled"


def load(name: str):
    return json.loads((RESULTS / name).read_text(encoding="utf-8"))


def main() -> None:
    source = load("source-runtime.json")
    hooks = load("hook-parity.json")
    workspace = load("workspace.json")
    summary = load("summary.json")

    baseline_failures = [
        (row["mutant_id"], row["candidate"], row["baseline_exit_code"])
        for row in source["results"]
        if row["baseline_exit_code"] != 0
    ]
    if baseline_failures:
        raise SystemExit(f"invalid clean source baseline: {baseline_failures}")

    affected_harness_failures = [
        (row["candidate"], row["changed"], row["raw"]["exit_code"])
        for row in workspace["affected"]
        if row["raw"]["exit_code"] != 0
    ]
    if affected_harness_failures:
        raise SystemExit(f"affected harness command failed: {affected_harness_failures}")

    cache_harness_failures: list[tuple[str, str, int]] = []
    for row in workspace["cache_hit"]:
        for phase in ("first", "second"):
            if row[phase]["exit_code"] != 0:
                cache_harness_failures.append((row["candidate"], phase, row[phase]["exit_code"]))
    for row in workspace["cache_invalidation"]:
        for phase in ("initial", "cached_after_change", "reference_force_run", "baseline_force_run"):
            if row[phase]["exit_code"] != 0:
                cache_harness_failures.append((row["candidate"], phase, row[phase]["exit_code"]))
    if cache_harness_failures:
        raise SystemExit(f"cache harness command failed: {cache_harness_failures}")

    if summary.get("status") != "complete":
        raise SystemExit(f"controlled collection incomplete: {summary.get('status')!r}")
    if summary.get("root_fault_records") != 22:
        raise SystemExit(f"unexpected root-fault corpus size: {summary.get('root_fault_records')!r}")
    if set(hooks.get("tools", {})) != {"pre-commit", "prek"}:
        raise SystemExit("hook parity evidence is incomplete")

    # Deliberately do not assert recall, affected-set equality, patch identity,
    # cache correctness, or a winner. Those are measured outcomes, not harness
    # validity requirements.
    print(json.dumps({
        "clean_source_baselines": len(source["results"]),
        "affected_commands_executed": len(workspace["affected"]),
        "cache_candidates_executed": len(workspace["cache_hit"]),
        "root_fault_records": summary["root_fault_records"],
        "repair_valid": True,
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
