from __future__ import annotations

import hashlib
import json
import shutil
import subprocess
import tempfile
import time
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent
CONFIG_REL = Path("benchmarks/verification-stack-v2/hooks/.pre-commit-config.yaml")
FIXTURE_REL = Path("benchmarks/verification-stack-v2/hooks/fixtures/input.txt")


def run(command: list[str], cwd: Path) -> dict[str, Any]:
    start = time.perf_counter_ns()
    p = subprocess.run(command, cwd=cwd, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)
    return {"command": command, "exit_code": p.returncode, "elapsed_ms": (time.perf_counter_ns() - start) / 1_000_000, "stdout": p.stdout, "stderr": p.stderr}


def git(cwd: Path, *args: str) -> str:
    p = subprocess.run(["git", *args], cwd=cwd, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
    return p.stdout


def sha(value: str) -> str:
    return hashlib.sha256(value.encode()).hexdigest()


def make_repo(parent: Path, runner: str) -> Path:
    repo = parent / runner
    hook_src = ROOT / "hooks"
    hook_dst = repo / "benchmarks" / "verification-stack-v2" / "hooks"
    hook_dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(hook_src, hook_dst)
    git(repo, "init", "-q")
    git(repo, "config", "user.name", "verification-benchmark")
    git(repo, "config", "user.email", "benchmark@example.invalid")
    git(repo, "add", ".")
    git(repo, "commit", "-q", "-m", "baseline")
    return repo


def evaluate(runner: str, repo: Path) -> dict[str, Any]:
    command = [runner, "run", "--all-files", "--config", str(CONFIG_REL)]
    before = (repo / FIXTURE_REL).read_bytes()
    first = run(command, repo)
    diff = git(repo, "diff", "--binary")
    names = [line for line in git(repo, "diff", "--name-only").splitlines() if line]
    after_first = (repo / FIXTURE_REL).read_bytes()
    first_content_sha = hashlib.sha256(after_first).hexdigest()
    second = run(command, repo)
    after_second = (repo / FIXTURE_REL).read_bytes()
    return {
        "runner": runner,
        "first_exit_code": first["exit_code"],
        "second_exit_code": second["exit_code"],
        "first": first,
        "second": second,
        "selected_changed_files": names,
        "diff_sha256": sha(diff),
        "content_changed": before != after_first,
        "idempotent_second_run": after_first == after_second,
        "content_sha256": first_content_sha,
    }


def main() -> None:
    with tempfile.TemporaryDirectory(prefix="verification-v2-hooks-") as raw:
        parent = Path(raw)
        pre_repo = make_repo(parent, "pre-commit")
        prek_repo = make_repo(parent, "prek")
        pre = evaluate("pre-commit", pre_repo)
        prek = evaluate("prek", prek_repo)

    parity = {
        "same_changed_files": pre["selected_changed_files"] == prek["selected_changed_files"],
        "same_diff_sha256": pre["diff_sha256"] == prek["diff_sha256"],
        "same_content_sha256": pre["content_sha256"] == prek["content_sha256"],
        "both_idempotent": pre["idempotent_second_run"] and prek["idempotent_second_run"],
    }
    out = ROOT / "results" / "controlled"
    out.mkdir(parents=True, exist_ok=True)
    (out / "hook-parity.json").write_text(json.dumps({"schema_version": 1, "mutant_id": "HOOK-PATCH-PARITY-001", "pre_commit": pre, "prek": prek, "parity": parity}, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(parity, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
