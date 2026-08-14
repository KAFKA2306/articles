from __future__ import annotations

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
WORKSPACE = ROOT / "workspace"
GROUND = json.loads((WORKSPACE / "ground-truth.json").read_text(encoding="utf-8"))
EXPECTED_PROJECTS = set(GROUND["nodes"])


def env() -> dict[str, str]:
    value = os.environ.copy()
    value["NX_DAEMON"] = "false"
    return value


def run(command: list[str], cwd: Path, extra_env: dict[str, str] | None = None) -> dict[str, Any]:
    e = env()
    if extra_env:
        e.update(extra_env)
    start = time.perf_counter_ns()
    p = subprocess.run(command, cwd=cwd, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False, env=e)
    return {"command": command, "exit_code": p.returncode, "elapsed_ms": (time.perf_counter_ns() - start) / 1_000_000, "stdout": p.stdout, "stderr": p.stderr}


def git(cwd: Path, *args: str) -> str:
    p = subprocess.run(["git", *args], cwd=cwd, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
    return p.stdout.strip()


def make_workspace(parent: Path, name: str) -> Path:
    dst = parent / name
    shutil.copytree(WORKSPACE, dst, ignore=shutil.ignore_patterns("node_modules", "dist", ".nx", ".turbo"))
    shared_modules = ROOT / "node_modules"
    if shared_modules.exists():
        os.symlink(shared_modules, dst / "node_modules", target_is_directory=True)
    git(dst, "init", "-q")
    git(dst, "config", "user.name", "verification-benchmark")
    git(dst, "config", "user.email", "benchmark@example.invalid")
    git(dst, "add", ".")
    git(dst, "commit", "-q", "-m", "baseline")
    return dst


def normalize_package(name: str) -> str:
    return name.rsplit("/", 1)[-1].lstrip("@")


def collect_project_names(value: Any) -> set[str]:
    found: set[str] = set()
    if isinstance(value, dict):
        for key, item in value.items():
            if key in {"name", "package", "project"} and isinstance(item, str):
                normalized = normalize_package(item)
                if normalized in EXPECTED_PROJECTS:
                    found.add(normalized)
            elif key in {"task", "taskId", "fullName"} and isinstance(item, str) and "#" in item:
                normalized = normalize_package(item.split("#", 1)[0])
                if normalized in EXPECTED_PROJECTS:
                    found.add(normalized)
            found.update(collect_project_names(item))
    elif isinstance(value, list):
        for item in value:
            found.update(collect_project_names(item))
    elif isinstance(value, str):
        normalized = normalize_package(value)
        if normalized in EXPECTED_PROJECTS:
            found.add(normalized)
    return found


def projects_from_json(result: dict[str, Any]) -> list[str]:
    try:
        value = json.loads(result["stdout"])
    except json.JSONDecodeError:
        return []
    return sorted(collect_project_names(value))


def discover(candidate: str, parent: Path) -> dict[str, Any]:
    repo = make_workspace(parent, f"discover-{candidate}")
    if candidate == "nx":
        raw = run(["nx", "show", "projects", "--json"], repo)
    else:
        raw = run(["turbo", "ls", "--output=json"], repo)
    observed = projects_from_json(raw)
    return {
        "candidate": candidate,
        "expected": sorted(EXPECTED_PROJECTS),
        "observed": observed,
        "correct": raw["exit_code"] == 0 and set(observed) == EXPECTED_PROJECTS,
        "raw": raw,
    }


def mutate_source(repo: Path, rel: str, marker: str) -> None:
    path = repo / rel
    path.write_text(path.read_text(encoding="utf-8") + f"\n// {marker}\n", encoding="utf-8")


def affected(candidate: str, changed_key: str, target: str, parent: Path) -> dict[str, Any]:
    repo = make_workspace(parent, f"affected-{candidate}-{changed_key}")
    base = git(repo, "rev-parse", "HEAD")
    mutate_source(repo, target, changed_key)
    git(repo, "add", target)
    git(repo, "commit", "-q", "-m", changed_key)
    if candidate == "nx":
        result = run(["nx", "show", "projects", "--affected", f"--base={base}", "--head=HEAD", "--json"], repo)
    else:
        result = run(["turbo", "run", "build", "--affected", "--dry=json"], repo, {"TURBO_SCM_BASE": base, "TURBO_SCM_HEAD": "HEAD"})
    projects = projects_from_json(result) if result["exit_code"] == 0 else []
    expected = sorted(GROUND["affected_expectations"][changed_key])
    return {"candidate": candidate, "changed": changed_key, "expected": expected, "observed": projects, "correct": result["exit_code"] == 0 and projects == expected, "raw": result}


def output_hashes(repo: Path) -> dict[str, str]:
    result: dict[str, str] = {}
    for group in ("packages", "apps"):
        for project in (repo / group).iterdir():
            path = project / "dist" / "out.txt"
            if path.exists():
                result[project.name] = hashlib.sha256(path.read_bytes()).hexdigest()
    return dict(sorted(result.items()))


def remove_outputs(repo: Path) -> None:
    for path in repo.glob("packages/*/dist"):
        shutil.rmtree(path)
    for path in repo.glob("apps/*/dist"):
        shutil.rmtree(path)


def build(candidate: str, repo: Path, force: bool = False) -> dict[str, Any]:
    if candidate == "nx":
        command = ["nx", "run-many", "-t", "build"]
        if force:
            command.append("--skip-nx-cache")
    else:
        command = ["turbo", "run", "build"]
        if force:
            command.append("--force")
    return run(command, repo)


def cache_hit(candidate: str, parent: Path) -> dict[str, Any]:
    repo = make_workspace(parent, f"cache-hit-{candidate}")
    first = build(candidate, repo)
    first_hashes = output_hashes(repo)
    remove_outputs(repo)
    second = build(candidate, repo)
    restored = output_hashes(repo)
    return {
        "candidate": candidate,
        "first": first,
        "second": second,
        "first_output_hashes": first_hashes,
        "restored_output_hashes": restored,
        "all_outputs_present": set(restored) == EXPECTED_PROJECTS,
        "byte_identical_restore": first_hashes == restored,
        "correct": first["exit_code"] == 0 and second["exit_code"] == 0 and first_hashes == restored and set(restored) == EXPECTED_PROJECTS,
    }


def cache_invalidation(candidate: str, parent: Path) -> dict[str, Any]:
    baseline_ref = make_workspace(parent, f"invalidate-baseline-{candidate}")
    baseline_run = build(candidate, baseline_ref, force=True)
    baseline_hashes = output_hashes(baseline_ref)

    cached_repo = make_workspace(parent, f"invalidate-cached-{candidate}")
    initial = build(candidate, cached_repo)
    mutate_source(cached_repo, "packages/core/src/value.ts", "cache-invalidation")
    cached_after = build(candidate, cached_repo)
    cached_hashes = output_hashes(cached_repo)

    reference = make_workspace(parent, f"invalidate-reference-{candidate}")
    mutate_source(reference, "packages/core/src/value.ts", "cache-invalidation")
    reference_run = build(candidate, reference, force=True)
    reference_hashes = output_hashes(reference)

    expected_changed = {"core", "ui", "web", "api"}
    changed = {name for name in reference_hashes if reference_hashes.get(name) != baseline_hashes.get(name)}
    return {
        "candidate": candidate,
        "initial": initial,
        "cached_after_change": cached_after,
        "reference_force_run": reference_run,
        "baseline_force_run": baseline_run,
        "cached_output_hashes": cached_hashes,
        "reference_output_hashes": reference_hashes,
        "baseline_output_hashes": baseline_hashes,
        "expected_changed_outputs": sorted(expected_changed),
        "observed_changed_outputs": sorted(changed),
        "matches_cache_free_reference": cached_hashes == reference_hashes,
        "correct": initial["exit_code"] == 0 and cached_after["exit_code"] == 0 and reference_run["exit_code"] == 0 and baseline_run["exit_code"] == 0 and cached_hashes == reference_hashes and changed == expected_changed,
    }


def main() -> None:
    with tempfile.TemporaryDirectory(prefix="verification-v2-workspace-") as raw:
        parent = Path(raw)
        discovery = [discover(candidate, parent) for candidate in ("nx", "turbo")]
        affected_results = []
        targets = {"core": "packages/core/src/value.ts", "ui": "packages/ui/src/value.ts", "docs": "packages/docs/src/value.ts"}
        for candidate in ("nx", "turbo"):
            for key, target in targets.items():
                affected_results.append(affected(candidate, key, target, parent))
        cache_hits = [cache_hit(candidate, parent) for candidate in ("nx", "turbo")]
        invalidations = [cache_invalidation(candidate, parent) for candidate in ("nx", "turbo")]

    boundary = {
        "mutant_id": "WS-BOUNDARY-001",
        "scored_head_to_head": False,
        "nx": {"status": "adjunct_required", "reason": "official OSS enforcement requires ESLint + @nx/enforce-module-boundaries; language-agnostic Conformance requires Nx Enterprise"},
        "turbo": {"status": "experimental", "reason": "turbo boundaries and tags are officially Experimental"},
    }
    out = ROOT / "results" / "controlled"
    out.mkdir(parents=True, exist_ok=True)
    payload = {"schema_version": 2, "protocol_revision": "v2.4", "discovery": discovery, "affected": affected_results, "cache_hit": cache_hits, "cache_invalidation": invalidations, "boundary_capability": boundary}
    (out / "workspace.json").write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({
        "discovery": {x["candidate"]: x["correct"] for x in discovery},
        "affected_correct": sum(x["correct"] for x in affected_results),
        "affected_total": len(affected_results),
        "cache_hit_correct": {x["candidate"]: x["correct"] for x in cache_hits},
        "cache_invalidation_correct": {x["candidate"]: x["correct"] for x in invalidations},
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
