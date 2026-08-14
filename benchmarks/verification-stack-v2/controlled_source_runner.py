from __future__ import annotations

import difflib
import hashlib
import json
import os
import shutil
import subprocess
import tempfile
import time
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent
MUTANTS = json.loads((ROOT / "mutants.json").read_text(encoding="utf-8"))["mutants"]

SCOPES: dict[str, list[str]] = {
    "PY-SYNTAX-001": ["ruff_lint", "black", "pyrefly", "ty", "pyright", "mypy"],
    "PY-FORMAT-001": ["ruff_format", "black"],
    "PY-LINT-001": ["ruff_lint", "flake8"],
    "PY-TYPE-ARG-001": ["pyrefly", "ty", "pyright", "mypy"],
    "PY-TYPE-RETURN-001": ["pyrefly", "ty", "pyright", "mypy"],
    "PY-NAME-001": ["pyrefly", "ty", "pyright", "mypy"],
    "PY-ASYNC-001": ["pyrefly", "ty", "pyright", "mypy"],
    "PY-RUNTIME-001": ["unvalidated_python", "pydantic"],
    "TS-SYNTAX-001": ["biome", "prettier", "oxlint", "eslint", "tsc"],
    "TS-FORMAT-001": ["biome", "prettier"],
    "TS-LINT-001": ["oxlint", "eslint"],
    "TS-TYPE-ARG-001": ["tsc", "oxlint_type_check"],
    "TS-TYPE-RETURN-001": ["tsc", "oxlint_type_check"],
    "TS-PROMISE-001": ["oxlint", "eslint"],
    "TS-RUNTIME-001": ["unvalidated_typescript", "zod"],
}

COMMANDS: dict[str, list[str]] = {
    "ruff_lint": ["ruff", "check", "--no-cache", "--output-format=json", "."],
    "ruff_format": ["ruff", "format", "--check", "."],
    "black": ["black", "--check", "."],
    "flake8": ["flake8", "."],
    "pyrefly": ["pyrefly", "check", "--output-format", "json"],
    "ty": ["ty", "check", "--output-format", "concise", "--no-progress", "."],
    "pyright": ["pyright", "--outputjson", "."],
    "mypy": ["mypy", "--show-error-codes", "--no-error-summary", "src", "tests"],
    "pydantic": ["python", "runtime_validate.py", "tests/payload.json"],
    "biome": ["biome", "format", "."],
    "prettier": ["prettier", "--check", "."],
    "oxlint": ["oxlint", "--type-aware", "."],
    "eslint": ["eslint", "."],
    "tsc": ["tsc", "--noEmit"],
    "oxlint_type_check": ["oxlint", "--type-aware", "--type-check", "."],
    "zod": ["node", "runtime_validate.mjs", "test/payload.json"],
}

FORMAT_WRITE = {
    "ruff_format": ["ruff", "format", "."],
    "black": ["black", "."],
    "biome": ["biome", "format", "--write", "."],
    "prettier": ["prettier", "--write", "."],
}


def tool_root(candidate: str) -> Path:
    if candidate == "eslint":
        return ROOT / "profiles" / "typescript-eslint" / "node_modules"
    return ROOT / "node_modules"


def candidate_env(candidate: str) -> dict[str, str]:
    value = os.environ.copy()
    modules = tool_root(candidate)
    if modules.exists():
        value["PATH"] = str(modules / ".bin") + os.pathsep + value.get("PATH", "")
    return value


def run(command: list[str], cwd: Path, candidate: str | None = None) -> dict[str, Any]:
    start = time.perf_counter_ns()
    p = subprocess.run(command, cwd=cwd, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False, env=candidate_env(candidate or ""))
    return {
        "command": command,
        "exit_code": p.returncode,
        "elapsed_ms": (time.perf_counter_ns() - start) / 1_000_000,
        "stdout": p.stdout,
        "stderr": p.stderr,
    }


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def copy_fixture(name: str, destination: Path, candidate: str | None = None) -> Path:
    src = ROOT / name
    dst = destination / name
    shutil.copytree(src, dst, ignore=shutil.ignore_patterns("node_modules", "dist", ".nx", ".turbo"))
    if name == "typescript":
        modules = tool_root(candidate or "")
        if modules.exists():
            os.symlink(modules, dst / "node_modules", target_is_directory=True)
    return dst


def apply_mutant(mutant: dict[str, Any], fixture_root: Path) -> Path:
    target = Path(mutant["target"])
    rel = Path(*target.parts[1:])
    path = fixture_root / rel
    text = path.read_text(encoding="utf-8")
    operation = mutant["operation"]
    if operation == "replace_once":
        old = mutant["old"]
        if text.count(old) != 1:
            raise RuntimeError(f"{mutant['id']}: expected exactly one replacement anchor")
        text = text.replace(old, mutant["new"], 1)
    elif operation == "insert_before":
        anchor = mutant["anchor"]
        lines = text.splitlines()
        matches = [i for i, line in enumerate(lines) if anchor in line]
        if len(matches) != 1:
            raise RuntimeError(f"{mutant['id']}: expected exactly one insertion anchor")
        i = matches[0]
        indent = lines[i][: len(lines[i]) - len(lines[i].lstrip())]
        lines.insert(i, indent + mutant["text"])
        text = "\n".join(lines) + "\n"
    else:
        raise RuntimeError(f"unsupported source mutant operation {operation}")
    path.write_text(text, encoding="utf-8")
    return path


def control_run(candidate: str, fixture: str, cwd: Path) -> dict[str, Any]:
    if candidate == "unvalidated_python":
        script = "import json; from pathlib import Path; v=json.loads(Path('tests/payload.json').read_text()); assert isinstance(v, dict)"
        return run(["python", "-c", script], cwd, candidate)
    if candidate == "unvalidated_typescript":
        script = "JSON.parse(require('fs').readFileSync('test/payload.json','utf8'));"
        return run(["node", "-e", script], cwd, candidate)
    return run(COMMANDS[candidate], cwd, candidate)


def smoke_after_format(fixture: str, cwd: Path, candidate: str) -> list[dict[str, Any]]:
    if fixture == "python":
        return [run(["python", "-m", "compileall", "-q", "src"], cwd, candidate), run(["python", "-m", "unittest", "discover", "-s", "tests", "-v"], cwd, candidate)]
    return [run(["tsc", "--noEmit"], cwd, candidate)]


def format_quality(candidate: str, mutant: dict[str, Any], temp: Path) -> dict[str, Any]:
    fixture = mutant["fixture"]
    clean_root = copy_fixture(fixture, temp / "clean-format", candidate)
    mutant_root = copy_fixture(fixture, temp / "mutant-format", candidate)
    clean_target = clean_root / Path(*Path(mutant["target"]).parts[1:])
    mutant_target = apply_mutant(mutant, mutant_root)
    before = mutant_target.read_bytes()
    first = run(FORMAT_WRITE[candidate], mutant_root, candidate)
    after_first = mutant_target.read_bytes()
    second = run(FORMAT_WRITE[candidate], mutant_root, candidate)
    after_second = mutant_target.read_bytes()
    diff = "".join(difflib.unified_diff(before.decode().splitlines(True), after_first.decode().splitlines(True)))
    smoke = smoke_after_format(fixture, mutant_root, candidate)
    return {
        "write_first": first,
        "write_second": second,
        "matches_clean_target": after_first == clean_target.read_bytes(),
        "idempotent": after_first == after_second,
        "patch_sha256": sha(diff.encode()),
        "formatted_target_sha256": sha(after_first),
        "smoke_pass": all(step["exit_code"] == 0 for step in smoke),
        "smoke": smoke,
    }


def main() -> None:
    results: list[dict[str, Any]] = []
    source_mutants = [m for m in MUTANTS if m["id"] in SCOPES]
    with tempfile.TemporaryDirectory(prefix="verification-v2-source-") as raw:
        temp = Path(raw)
        for mutant in source_mutants:
            fixture = mutant["fixture"]
            for candidate in SCOPES[mutant["id"]]:
                clean = copy_fixture(fixture, temp / f"{mutant['id']}-{candidate}-clean", candidate)
                mutated = copy_fixture(fixture, temp / f"{mutant['id']}-{candidate}-mutant", candidate)
                baseline = control_run(candidate, fixture, clean)
                apply_mutant(mutant, mutated)
                observed = control_run(candidate, fixture, mutated)
                record: dict[str, Any] = {
                    "mutant_id": mutant["id"],
                    "root_fault": mutant.get("root"),
                    "responsibility": mutant["responsibility"],
                    "candidate": candidate,
                    "environment_profile": "typescript-eslint" if candidate == "eslint" else ("ts7" if fixture == "typescript" else "python"),
                    "baseline_exit_code": baseline["exit_code"],
                    "baseline_blocking_false_positive": baseline["exit_code"] != 0,
                    "mutant_exit_code": observed["exit_code"],
                    "detected": observed["exit_code"] != 0,
                    "baseline": baseline,
                    "mutant": observed,
                }
                if mutant["id"] in {"PY-FORMAT-001", "TS-FORMAT-001"}:
                    record["format_quality"] = format_quality(candidate, mutant, temp / f"{mutant['id']}-{candidate}-quality")
                results.append(record)

    out = ROOT / "results" / "controlled"
    out.mkdir(parents=True, exist_ok=True)
    (out / "source-runtime.json").write_text(json.dumps({"schema_version": 2, "results": results}, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"records": len(results), "output": str(out / 'source-runtime.json')}, indent=2))


if __name__ == "__main__":
    main()
