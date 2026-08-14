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
    "PY-SYNTAX-001": ["ruff_lint", "pyrefly", "ty", "pyright", "mypy"],
    "PY-FORMAT-001": ["ruff_format", "black"],
    "PY-LINT-001": ["ruff_lint", "flake8"],
    "PY-TYPE-ARG-001": ["pyrefly", "ty", "pyright", "mypy"],
    "PY-TYPE-RETURN-001": ["pyrefly", "ty", "pyright", "mypy"],
    "PY-NAME-001": ["pyrefly", "ty", "pyright", "mypy"],
    "PY-ASYNC-001": ["pyrefly", "ty", "pyright", "mypy"],
    "PY-RUNTIME-001": ["unvalidated_python", "pydantic"],
    "TS-SYNTAX-001": ["oxlint", "eslint", "tsc"],
    "TS-FORMAT-001": ["biome", "prettier"],
    "TS-LINT-001": ["oxlint", "eslint"],
    "TS-TYPE-ARG-001": ["tsc", "oxlint_type_check"],
    "TS-TYPE-RETURN-001": ["tsc", "oxlint_type_check"],
    "TS-PROMISE-001": ["oxlint", "eslint"],
    "TS-RUNTIME-001": ["unvalidated_typescript", "zod"],
}

FORMATTERS = {"ruff_format", "black", "biome", "prettier"}


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


def command_for(candidate: str, mutant_id: str, *, write: bool = False) -> list[str]:
    python_service = "src/verification_fixture/service.py"
    ts_service = "src/service.ts"
    if candidate == "ruff_lint":
        command = ["ruff", "check", "--no-cache", "--output-format=json"]
        if mutant_id == "PY-LINT-001":
            command += ["--select", "F841"]
        return command + [python_service]
    if candidate == "ruff_format":
        return ["ruff", "format", *( [] if write else ["--check"] ), python_service]
    if candidate == "black":
        return ["black", *( [] if write else ["--check"] ), python_service]
    if candidate == "flake8":
        return ["flake8", "--select=F841", python_service]
    if candidate == "pyrefly":
        return ["pyrefly", "check", "--preset", "default", "--output-format", "json"]
    if candidate == "ty":
        return ["ty", "check", "--output-format", "concise", "--no-progress", "."]
    if candidate == "pyright":
        return ["pyright", "--outputjson", "."]
    if candidate == "mypy":
        return ["mypy", "--show-error-codes", "--no-error-summary", "src", "tests"]
    if candidate == "pydantic":
        return ["python", "runtime_validate.py", "tests/payload.json"]
    if candidate == "biome":
        return ["biome", "format", *( ["--write"] if write else [] ), ts_service]
    if candidate == "prettier":
        return ["prettier", "--write" if write else "--check", ts_service]
    if candidate == "oxlint":
        return ["oxlint", "--type-aware", "src"]
    if candidate == "eslint":
        return ["eslint", "src"]
    if candidate == "tsc":
        return ["tsc", "--noEmit"]
    if candidate == "oxlint_type_check":
        return ["oxlint", "--type-aware", "--type-check", "src"]
    if candidate == "zod":
        return ["node", "runtime_validate.mjs", "test/payload.json"]
    raise KeyError(candidate)


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


def execute(candidate: str, mutant_id: str, cwd: Path, *, write: bool = False) -> dict[str, Any]:
    if candidate == "unvalidated_python":
        script = "import json; from pathlib import Path; v=json.loads(Path('tests/payload.json').read_text()); assert isinstance(v, dict)"
        return run(["python", "-c", script], cwd, candidate)
    if candidate == "unvalidated_typescript":
        script = "JSON.parse(require('fs').readFileSync('test/payload.json','utf8'));"
        return run(["node", "-e", script], cwd, candidate)
    return run(command_for(candidate, mutant_id, write=write), cwd, candidate)


def smoke_after_format(fixture: str, cwd: Path, candidate: str) -> list[dict[str, Any]]:
    if fixture == "python":
        return [
            run(["python", "-m", "compileall", "-q", "src"], cwd, candidate),
            run(["python", "-m", "unittest", "discover", "-s", "tests", "-v"], cwd, candidate),
        ]
    # Always use the TS7 compiler baseline for semantic smoke; formatter style is independent of ESLint's TS profile.
    return [run(["tsc", "--noEmit"], cwd, "tsc")]


def formatter_baseline(candidate: str, mutant: dict[str, Any], clean: Path) -> dict[str, Any]:
    write_first = execute(candidate, mutant["id"], clean, write=True)
    check = execute(candidate, mutant["id"], clean)
    write_second = execute(candidate, mutant["id"], clean, write=True)
    smoke = smoke_after_format(mutant["fixture"], clean, candidate)
    target = clean / Path(*Path(mutant["target"]).parts[1:])
    return {
        "write_first": write_first,
        "check": check,
        "write_second": write_second,
        "target_sha256": sha(target.read_bytes()),
        "idempotent": check["exit_code"] == 0 and write_second["exit_code"] == 0,
        "smoke_pass": all(step["exit_code"] == 0 for step in smoke),
        "smoke": smoke,
    }


def format_quality(candidate: str, mutant: dict[str, Any], temp: Path) -> dict[str, Any]:
    clean_root = copy_fixture(mutant["fixture"], temp / "clean-format", candidate)
    clean_baseline = formatter_baseline(candidate, mutant, clean_root)
    normalized_target = clean_root / Path(*Path(mutant["target"]).parts[1:])
    normalized_bytes = normalized_target.read_bytes()

    mutant_root = copy_fixture(mutant["fixture"], temp / "mutant-format", candidate)
    mutant_target = apply_mutant(mutant, mutant_root)
    before = mutant_target.read_bytes()
    check_before = execute(candidate, mutant["id"], mutant_root)
    first = execute(candidate, mutant["id"], mutant_root, write=True)
    after_first = mutant_target.read_bytes()
    second = execute(candidate, mutant["id"], mutant_root, write=True)
    after_second = mutant_target.read_bytes()
    check_after = execute(candidate, mutant["id"], mutant_root)
    diff = "".join(difflib.unified_diff(before.decode().splitlines(True), after_first.decode().splitlines(True)))
    smoke = smoke_after_format(mutant["fixture"], mutant_root, candidate)
    return {
        "candidate_normalized_baseline": clean_baseline,
        "check_before": check_before,
        "write_first": first,
        "write_second": second,
        "check_after": check_after,
        "matches_candidate_normalized_baseline": after_first == normalized_bytes,
        "idempotent": after_first == after_second and check_after["exit_code"] == 0,
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
                if candidate in FORMATTERS:
                    quality = format_quality(candidate, mutant, temp / f"{mutant['id']}-{candidate}-quality")
                    baseline_ok = quality["candidate_normalized_baseline"]["idempotent"] and quality["candidate_normalized_baseline"]["smoke_pass"]
                    record = {
                        "mutant_id": mutant["id"],
                        "root_fault": mutant.get("root"),
                        "responsibility": mutant["responsibility"],
                        "candidate": candidate,
                        "environment_profile": "ts7" if fixture == "typescript" else "python",
                        "baseline_exit_code": 0 if baseline_ok else 1,
                        "baseline_blocking_false_positive": not baseline_ok,
                        "mutant_exit_code": quality["check_before"]["exit_code"],
                        "detected": quality["check_before"]["exit_code"] != 0,
                        "format_quality": quality,
                    }
                    results.append(record)
                    continue

                clean = copy_fixture(fixture, temp / f"{mutant['id']}-{candidate}-clean", candidate)
                mutated = copy_fixture(fixture, temp / f"{mutant['id']}-{candidate}-mutant", candidate)
                baseline = execute(candidate, mutant["id"], clean)
                apply_mutant(mutant, mutated)
                observed = execute(candidate, mutant["id"], mutated)
                results.append({
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
                })

    out = ROOT / "results" / "controlled"
    out.mkdir(parents=True, exist_ok=True)
    (out / "source-runtime.json").write_text(json.dumps({"schema_version": 3, "protocol_revision": "v2.4", "results": results}, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"records": len(results), "output": str(out / 'source-runtime.json')}, indent=2))


if __name__ == "__main__":
    main()
