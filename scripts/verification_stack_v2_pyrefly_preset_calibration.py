from __future__ import annotations

import json
import shutil
import subprocess
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
ROOT = REPO / "benchmarks" / "verification-stack-v2"
FIXTURE = ROOT / "python"
MUTANTS = json.loads((ROOT / "mutants.json").read_text(encoding="utf-8"))["mutants"]
OUTPUT = ROOT / "results" / "controlled" / "pyrefly-preset-calibration.json"

IDS = {
    "PY-SYNTAX-001",
    "PY-TYPE-ARG-001",
    "PY-TYPE-RETURN-001",
    "PY-NAME-001",
    "PY-ASYNC-001",
}

MODES = {
    "no_config": ["pyrefly", "check", "--output-format", "json"],
    "basic": ["pyrefly", "check", "--preset", "basic", "--output-format", "json"],
    "default": ["pyrefly", "check", "--preset", "default", "--output-format", "json"],
}


def run(command: list[str], cwd: Path) -> dict:
    p = subprocess.run(
        command,
        cwd=cwd,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    return {
        "command": command,
        "exit_code": p.returncode,
        "stdout": p.stdout,
        "stderr": p.stderr,
    }


def copy_fixture(parent: Path, name: str) -> Path:
    dst = parent / name
    shutil.copytree(FIXTURE, dst, ignore=shutil.ignore_patterns("__pycache__", ".pyrefly_cache"))
    return dst


def apply_mutant(mutant: dict, fixture: Path) -> None:
    target = Path(mutant["target"])
    path = fixture / Path(*target.parts[1:])
    text = path.read_text(encoding="utf-8")
    if mutant["operation"] == "replace_once":
        old = mutant["old"]
        if text.count(old) != 1:
            raise RuntimeError(f"{mutant['id']}: expected one replacement anchor")
        text = text.replace(old, mutant["new"], 1)
    elif mutant["operation"] == "insert_before":
        anchor = mutant["anchor"]
        lines = text.splitlines()
        matches = [i for i, line in enumerate(lines) if anchor in line]
        if len(matches) != 1:
            raise RuntimeError(f"{mutant['id']}: expected one insertion anchor")
        i = matches[0]
        indent = lines[i][: len(lines[i]) - len(lines[i].lstrip())]
        lines.insert(i, indent + mutant["text"])
        text = "\n".join(lines) + "\n"
    else:
        raise RuntimeError(f"unsupported operation for {mutant['id']}")
    path.write_text(text, encoding="utf-8")


def main() -> None:
    selected = [m for m in MUTANTS if m["id"] in IDS]
    if {m["id"] for m in selected} != IDS:
        raise SystemExit("frozen Pyrefly mutant set is incomplete")

    rows: list[dict] = []
    with tempfile.TemporaryDirectory(prefix="pyrefly-preset-calibration-") as raw:
        parent = Path(raw)
        for mutant in selected:
            for mode, command in MODES.items():
                clean = copy_fixture(parent, f"{mutant['id']}-{mode}-clean")
                mutated = copy_fixture(parent, f"{mutant['id']}-{mode}-mutant")
                baseline = run(command, clean)
                apply_mutant(mutant, mutated)
                observed = run(command, mutated)
                rows.append(
                    {
                        "mutant_id": mutant["id"],
                        "mode": mode,
                        "baseline_exit_code": baseline["exit_code"],
                        "mutant_exit_code": observed["exit_code"],
                        "detected": baseline["exit_code"] == 0 and observed["exit_code"] != 0,
                        "baseline_stdout": baseline["stdout"],
                        "baseline_stderr": baseline["stderr"],
                        "mutant_stdout": observed["stdout"],
                        "mutant_stderr": observed["stderr"],
                    }
                )

    summary = {}
    for mode in MODES:
        scoped = [row for row in rows if row["mode"] == mode]
        summary[mode] = {
            "clean_baselines": sum(row["baseline_exit_code"] == 0 for row in scoped),
            "detected": sum(row["detected"] for row in scoped),
            "in_scope": len(scoped),
            "detected_ids": sorted(row["mutant_id"] for row in scoped if row["detected"]),
            "missed_ids": sorted(row["mutant_id"] for row in scoped if not row["detected"]),
        }

    payload = {
        "schema_version": 1,
        "candidate": "pyrefly",
        "candidate_version": subprocess.check_output(["pyrefly", "--version"], text=True).strip(),
        "purpose": "Isolate preset/configuration effect using the same frozen five-mutant Python static-type corpus.",
        "guardrail": "This calibration compares modes of one pinned candidate; it is not a cross-tool ranking.",
        "summary": summary,
        "rows": rows,
    }
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2, sort_keys=True))

    if any(item["clean_baselines"] != item["in_scope"] for item in summary.values()):
        raise SystemExit("preset calibration has a dirty clean baseline")


if __name__ == "__main__":
    main()
