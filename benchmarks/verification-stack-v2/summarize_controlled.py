from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent
RESULTS = ROOT / "results" / "controlled"


def read(name: str) -> dict[str, Any]:
    path = RESULTS / name
    if not path.exists():
        raise FileNotFoundError(path)
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> None:
    source = read("source-runtime.json")
    hooks = read("hook-parity.json")
    workspace = read("workspace.json")

    candidate_stats: dict[str, dict[str, int]] = defaultdict(
        lambda: {
            "in_scope_records": 0,
            "detected": 0,
            "raw_mutant_blocking_outputs": 0,
            "baseline_blocking_false_positives": 0,
        }
    )
    mutant_matrix: dict[str, dict[str, bool]] = defaultdict(dict)
    format_quality: dict[str, Any] = {}

    baseline_failures: list[dict[str, str]] = []
    for record in source["results"]:
        candidate = record["candidate"]
        baseline_failed = bool(record["baseline_blocking_false_positive"])
        raw_detected = bool(record["detected"])
        # A non-zero mutant run is only detection evidence when the same
        # candidate accepts its calibrated clean baseline. Otherwise the
        # result is setup/configuration noise, never detection credit.
        effective_detected = raw_detected and not baseline_failed

        candidate_stats[candidate]["in_scope_records"] += 1
        candidate_stats[candidate]["raw_mutant_blocking_outputs"] += int(raw_detected)
        candidate_stats[candidate]["detected"] += int(effective_detected)
        candidate_stats[candidate]["baseline_blocking_false_positives"] += int(baseline_failed)
        mutant_matrix[record["mutant_id"]][candidate] = effective_detected

        if baseline_failed:
            baseline_failures.append(
                {
                    "candidate": candidate,
                    "mutant_id": record["mutant_id"],
                    "kind": "source_baseline",
                }
            )
        if "format_quality" in record:
            q = record["format_quality"]
            format_quality[f"{record['mutant_id']}::{candidate}"] = {
                "matches_candidate_normalized_baseline": q[
                    "matches_candidate_normalized_baseline"
                ],
                "idempotent": q["idempotent"],
                "smoke_pass": q["smoke_pass"],
                "patch_sha256": q["patch_sha256"],
            }
            if not (
                q["matches_candidate_normalized_baseline"]
                and q["idempotent"]
                and q["smoke_pass"]
            ):
                baseline_failures.append(
                    {
                        "candidate": candidate,
                        "mutant_id": record["mutant_id"],
                        "kind": "formatter_calibration",
                    }
                )

    hook_parity = hooks["parity"]
    if not hook_parity.get("both_idempotent", False):
        baseline_failures.append(
            {
                "candidate": "pre-commit/prek",
                "mutant_id": "HOOK-PATCH-PARITY-001",
                "kind": "hook_baseline",
            }
        )

    discovery = {
        item["candidate"]: bool(item["correct"])
        for item in workspace.get("discovery", [])
    }
    for candidate in ("nx", "turbo"):
        if discovery.get(candidate) is not True:
            baseline_failures.append(
                {
                    "candidate": candidate,
                    "mutant_id": "WORKSPACE-DISCOVERY",
                    "kind": "workspace_discovery",
                }
            )

    affected_correct = sum(int(item["correct"]) for item in workspace["affected"])
    cache_hit_correct = {
        item["candidate"]: bool(item["correct"]) for item in workspace["cache_hit"]
    }
    cache_invalidation_correct = {
        item["candidate"]: bool(item["correct"])
        for item in workspace["cache_invalidation"]
    }

    status = "complete" if not baseline_failures else "invalid_baseline"
    baseline_calibration = {
        "status": "pass" if not baseline_failures else "fail",
        "failures": baseline_failures,
        "rule": (
            "No controlled result is recommendation-eligible unless every declared "
            "clean baseline and both workspace discovery gates pass. A blocked mutant "
            "never receives detection credit when its clean baseline also blocks."
        ),
    }

    summary = {
        "schema_version": 3,
        "protocol_revision": "v2.4-integrity-reaudit",
        "status": status,
        "interpretation_status": "unclassified" if status == "complete" else "invalid",
        "baseline_calibration": baseline_calibration,
        "candidate_stats": dict(sorted(candidate_stats.items())),
        "mutant_detection_matrix": {
            k: dict(sorted(v.items())) for k, v in sorted(mutant_matrix.items())
        },
        "format_quality": dict(sorted(format_quality.items())),
        "hook_patch_parity": hook_parity,
        "workspace": {
            "discovery": discovery,
            "affected_correct": affected_correct,
            "affected_total": len(workspace["affected"]),
            "cache_hit_correct": cache_hit_correct,
            "cache_invalidation_correct": cache_invalidation_correct,
            "boundary_capability": workspace["boundary_capability"],
        },
        "guardrails": [
            "complete means the calibrated evidence corpus finished with valid clean baselines; it does not mean every candidate passed every mutant",
            "a mutant failure receives detection credit only when the corresponding clean baseline passes",
            "raw diagnostic counts are not defect counts",
            "candidate_stats do not rank responsibilities against each other",
            "runtime unvalidated controls are negative controls, not candidate authorities",
            "formatter outputs are compared to their own normalized baseline because opinionated canonical styles may differ",
            "boundary capability is not a scored Nx/Turbo head-to-head because official enforcement surfaces differ in maturity and dependencies",
            "no recommendation or article thesis is authorized by this summary",
        ],
    }
    RESULTS.mkdir(parents=True, exist_ok=True)
    (RESULTS / "baseline-calibration.json").write_text(
        json.dumps(baseline_calibration, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    (RESULTS / "summary.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(
        json.dumps(
            {
                "status": status,
                "baseline_calibration": baseline_calibration["status"],
                "source_records": len(source["results"]),
                "affected": f"{affected_correct}/{len(workspace['affected'])}",
                "workspace_discovery": discovery,
                "hook_parity": hook_parity,
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
