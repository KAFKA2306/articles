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


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


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
        responsibility = adapter.get("responsibility")
        fixture = adapter.get("fixture")
        if not responsibility or not fixture:
            raise ValueError(f"adapter {adapter_name!r} lacks responsibility or fixture")
        for package_key in adapter.get("packages", []):
            if package_key not in pinned:
                raise ValueError(
                    f"adapter {adapter_name!r} references unpinned package {package_key!r}"
                )

        command_forms = [key for key in ("check", "check_sequence") if key in adapter]
        mode = adapter.get("mode")
        if not command_forms and mode not in {
            "contract_test",
            "scenario_commands_required",
            "config_required",
        }:
            raise ValueError(f"adapter {adapter_name!r} has no executable or declared setup mode")

    return versions, adapters


def percentile(values: list[float], fraction: float) -> float:
    if not values:
        raise ValueError("no values")
    ordered = sorted(values)
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
    elapsed_ms = (time.perf_counter_ns() - started) / 1_000_000
    return {
        "command": command,
        "exit_code": completed.returncode,
        "elapsed_ms": elapsed_ms,
        "stdout": completed.stdout,
        "stderr": completed.stderr,
    }


def run_sequence(commands: list[list[str]], cwd: Path) -> dict[str, Any]:
    started = time.perf_counter_ns()
    steps = [run_once(command, cwd) for command in commands]
    elapsed_ms = (time.perf_counter_ns() - started) / 1_000_000
    return {
        "steps": steps,
        "exit_code": 0 if all(step["exit_code"] == 0 for step in steps) else 1,
        "elapsed_ms": elapsed_ms,
    }


def execute_adapter(
    adapter_name: str,
    cwd: Path,
    warmups: int,
    repetitions: int,
) -> dict[str, Any]:
    versions, adapter_manifest = validate_manifests()
    adapters = adapter_manifest["adapters"]
    if adapter_name not in adapters:
        raise KeyError(f"unknown adapter: {adapter_name}")

    adapter = adapters[adapter_name]
    if "check" in adapter:
        runner = lambda: run_once(adapter["check"], cwd)
    elif "check_sequence" in adapter:
        runner = lambda: run_sequence(adapter["check_sequence"], cwd)
    else:
        raise ValueError(
            f"adapter {adapter_name!r} requires a fixture-specific command/config before execution"
        )

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
        "pinned_packages": {
            key: versions["candidates"][key]["version"] for key in adapter.get("packages", [])
        },
        "runner": {
            "platform": platform.platform(),
            "python": sys.version.split()[0],
        },
        "timing_protocol": {
            "warmups": warmups,
            "measured_repetitions": repetitions,
            "same_process_runner": True,
        },
        "latency_ms": {
            "samples": elapsed,
            "median": statistics.median(elapsed),
            "p25": percentile(elapsed, 0.25),
            "p75": percentile(elapsed, 0.75),
        },
        "runs": runs,
        "interpretation_boundary": [
            "This file contains raw execution observations, not grouped defect counts.",
            "Diagnostic messages must be mapped to preregistered mutant IDs separately.",
            "Timing does not override a correctness disqualifier.",
            "Cross-candidate timing is comparable only when invoked on equivalent checkout state on the same runner.",
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Neutral collector for verification-stack-v2 preregistered evidence"
    )
    parser.add_argument("--validate-only", action="store_true")
    parser.add_argument("--candidate")
    parser.add_argument("--cwd", type=Path)
    parser.add_argument("--warmups", type=int, default=2)
    parser.add_argument("--repetitions", type=int, default=10)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    validate_manifests()
    if args.validate_only:
        print("verification-stack-v2 manifests: valid")
        return

    if not args.candidate or args.cwd is None or args.output is None:
        parser.error("execution requires --candidate, --cwd, and --output")
    if args.warmups < 0 or args.repetitions < 10:
        parser.error("protocol requires warmups >= 0 and measured repetitions >= 10")

    cwd = args.cwd.resolve()
    if not cwd.is_dir():
        parser.error(f"cwd does not exist: {cwd}")

    result = execute_adapter(args.candidate, cwd, args.warmups, args.repetitions)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
