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

    candidate_stats: dict[str, dict[str, int]] = defaultdict(lambda: {"in_scope_records": 0, "detected": 0, "baseline_blocking_false_positives": 0})
    mutant_matrix: dict[str, dict[str, bool]] = defaultdict(dict)
    format_quality: dict[str, Any] = {}

    for record in source["results"]:
        candidate = record["candidate"]
        candidate_stats[candidate]["in_scope_records"] += 1
        candidate_stats[candidate]["detected"] += int(bool(record["detected"]))
        candidate_stats[candidate]["baseline_blocking_false_positives"] += int(bool(record["baseline_blocking_false_positive"]))
        mutant_matrix[record["mutant_id"]][candidate] = bool(record["detected"])
        if "format_quality" in record:
            q = record["format_quality"]
            format_quality[f"{record['mutant_id']}::{candidate}"] = {
                "matches_clean_target": q["matches_clean_target"],
                "idempotent": q["idempotent"],
                "smoke_pass": q["smoke_pass"],
                "patch_sha256": q["patch_sha256"],
            }

    hook_parity = hooks["parity"]
    affected_correct = sum(int(item["correct"]) for item in workspace["affected"])
    cache_hit_correct = {item["candidate"]: bool(item["correct"]) for item in workspace["cache_hit"]}
    cache_invalidation_correct = {item["candidate"]: bool(item["correct"]) for item in workspace["cache_invalidation"]}

    summary = {
        "schema_version": 1,
        "status": "complete",
        "interpretation_status": "unclassified",
        "candidate_stats": dict(sorted(candidate_stats.items())),
        "mutant_detection_matrix": {k: dict(sorted(v.items())) for k, v in sorted(mutant_matrix.items())},
        "format_quality": dict(sorted(format_quality.items())),
        "hook_patch_parity": hook_parity,
        "workspace": {
            "affected_correct": affected_correct,
            "affected_total": len(workspace["affected"]),
            "cache_hit_correct": cache_hit_correct,
            "cache_invalidation_correct": cache_invalidation_correct,
            "boundary_capability": workspace["boundary_capability"],
        },
        "guardrails": [
            "complete means evidence collection completed, not that any candidate passed",
            "raw diagnostic counts are not defect counts",
            "candidate_stats do not rank responsibilities against each other",
            "runtime unvalidated controls are negative controls, not candidate authorities",
            "boundary capability is not a scored Nx/Turbo head-to-head because official enforcement surfaces differ in maturity and dependencies",
            "no recommendation or article thesis is authorized by this summary",
        ],
    }
    RESULTS.mkdir(parents=True, exist_ok=True)
    (RESULTS / "summary.json").write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"status": "complete", "source_records": len(source["results"]), "affected": f"{affected_correct}/{len(workspace['affected'])}", "hook_parity": hook_parity}, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
