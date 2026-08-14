from __future__ import annotations

import argparse
import json
import os
import platform
import statistics
import subprocess
import sys
import time
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent
VERSIONS_PATH = ROOT / "candidate-versions.json"
ADAPTERS_PATH = ROOT / "candidate-adapters.json"
MUTANTS_PATH = ROOT / "mutants.json"


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def validate_mutants() -> None:
    manifest = read_json(MUTANTS_PATH)
    failures: list[str] = []
    for mutant in manifest.get("mutants", []):
        target = mutant.get("target")
        if not target:
            continue
        path = ROOT / target
        if not path.exists():
            failures.append(f"{mutant['id']}: missing target {target}")
            continue
        operation = mutant.get("operation")
        if operation == "replace_once":
            count = path.read_text(encoding="utf-8").count(mutant["old"])
            if count != 1:
                failures.append(f"{mutant['id']}: replace anchor count={count}, expected=1")
        elif operation == "insert_before":
            count = sum(
                1
                for line in path.read_text(encoding="utf-8").splitlines()
                if mutant["anchor"] in line
            )
            if count != 1:
                failures.append(f"{mutant['id']}: insert anchor count={count}, expected=1")
        elif operation not in {
            "touch_input",
            "change_dependency_input",
            "run_hook_runners",
            "repeat_without_change",
            "introduce_forbidden_dependency",
        }:
            failures.append(f"{mutant['id']}: unknown operation {operation}")
    if failures:
        raise ValueError("invalid mutant manifest:\n" + "\n".join(failures))


def validate_manifests() -> tuple[dict[str, Any], dict[str, Any]]:
    versions = read_json(VERSIONS_PATH)
    adapters = read_json(ADAPTERS_PATH)
    if versions.get("schema_version") != 1 or adapters.get("schema_version") != 1:
        raise ValueError("unsupported manifest schema")
    pinned = versions.get("candidates", {})
    if not pinned:
        raise ValueError("candidate version manifest is empty")
    for name, record in pinned.items():
        if not record.get("version") or not record.get("source"):
            raise ValueError(f"candidate {name!r} is not exactly pinned with provenance")
    for adapter_name, adapter in adapters.get("adapters", {}).items():
        if not adapter.get("responsibility") or not adapter.get("fixture"):
            raise ValueError(f"adapter {adapter_name!r} lacks responsibility or fixture")
        for package_key in adapter.get("packages", []):
            if package_key not in pinned:
                raise ValueError(f"adapter {adapter_name!r} references unpinned package {package_key!r}")
        command_forms = [key for key in ("check", "check_sequence") if key in adapter]
        if not command_forms and adapter.get("mode") not in {
            "contract_test",
            "scenario_commands_required",
            "config_required",
        }:
            raise ValueError(f"adapter {adapter_name!r} has no executable or declared setup mode")
    validate_mutants()
    return versions, adapters


def percentile(values: list[float], fraction: float) -> float:
    ordered = sorted(values)
    if not ordered:
        raise ValueError("no values")
    if len(ordered) == 1:
        return ordered[0]
    pos = (len(ordered) - 1) * fraction
    lo = int(pos)
    hi = min(lo + 1, len(ordered) - 1)
    weight = pos - lo
    return ordered[lo] * (1 - weight) + ordered[hi] * weight


def run_once(command: list[str], cwd: Path) -> dict[str, Any]:
    started = time.perf_counter_ns()
    completed = subprocess.run(
        command,
        cwd=cwd,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        env=os.environ.copy(),
        check=False,
    )
    return {
        "command": command,
        "exit_code": completed.returncode,
        "elapsed_ms": (time.perf_counter_ns() - started) / 1_000_000,
        "stdout": completed.stdout,
        "stderr": completed.stderr,
    }


def run_sequence(commands: list[list[str]], cwd: Path) -> dict[str, Any]:
    started = time.perf_counter_ns()
    steps = [run_once(command, cwd) for command in commands]
    return {
        "steps": steps,
        "exit_code": 0 if all(step["exit_code"] == 0 for step in steps) else 1,
        "elapsed_ms": (time.perf_counter_ns() - started) / 1_000_000,
    }


def execute_adapter(adapter_name: str, cwd: Path, warmups: int, repetitions: int) -> dict[str, Any]:
    versions, manifest = validate_manifests()
    adapter = manifest["adapters"][adapter_name]
    if "check" in adapter:
        runner = lambda: run_once(adapter["check"], cwd)
    elif "check_sequence" in adapter:
        runner = lambda: run_sequence(adapter["check_sequence"], cwd)
    else:
        raise ValueError(f"adapter {adapter_name!r} requires fixture-specific execution")
    for _ in range(warmups):
        runner()
    runs = [runner() for _ in range(repetitions)]
    elapsed = [float(run["elapsed_ms"]) for run in runs]
    return {
        "schema_version": 1,
        "evidence_class": "raw_harness_observation",
        "candidate": adapter_name,
        "responsibility": adapter["responsibility"],
        "fixture": adapter["fixture"],
        "pinned_packages": {key: versions["candidates"][key]["version"] for key in adapter.get("packages", [])},
        "runner": {"platform": platform.platform(), "python": sys.version.split()[0]},
        "timing_protocol": {"warmups": warmups, "measured_repetitions": repetitions, "same_process_runner": True},
        "latency_ms": {"samples": elapsed, "median": statistics.median(elapsed), "p25": percentile(elapsed, 0.25), "p75": percentile(elapsed, 0.75)},
        "runs": runs,
        "interpretation_boundary": [
            "Raw observations are not grouped defect counts.",
            "Timing never overrides correctness disqualifiers.",
            "Cross-candidate timing requires equivalent checkout state and runner context.",
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Neutral collector for verification-stack-v2")
    parser.add_argument("--validate-only", action="store_true")
    parser.add_argument("--candidate")
    parser.add_argument("--cwd", type=Path)
    parser.add_argument("--warmups", type=int, default=2)
    parser.add_argument("--repetitions", type=int, default=10)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    validate_manifests()
    if args.validate_only:
        print("verification-stack-v2 manifests and mutant anchors: valid")
        return
    if not args.candidate or args.cwd is None or args.output is None:
        parser.error("execution requires --candidate, --cwd, and --output")
    if args.warmups < 0 or args.repetitions < 10:
        parser.error("protocol requires warmups >= 0 and repetitions >= 10")
    cwd = args.cwd.resolve()
    if not cwd.is_dir():
        parser.error(f"cwd does not exist: {cwd}")
    result = execute_adapter(args.candidate, cwd, args.warmups, args.repetitions)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
