from __future__ import annotations

import hashlib
import json
import os
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent
OWNER = "KAFKA2306"
CUTOFF = "2025-08-15T00:00:00Z"
OUT = ROOT / "real-repo-sample.json"

EXCLUDED_PREFIXES = (
    ".venv/", "venv/", "env/", "node_modules/", "dist/", "build/", ".next/",
    "coverage/", "vendor/", "third_party/", "third-party/", "site-packages/",
)
PY_MANIFESTS = {"pyproject.toml", "requirements.txt", "Pipfile", "uv.lock"}
JS_LOCKS = {"package-lock.json", "pnpm-lock.yaml", "yarn.lock", "bun.lock", "bun.lockb"}


def api(path: str) -> Any:
    token = os.environ.get("GITHUB_TOKEN")
    if not token:
        raise RuntimeError("GITHUB_TOKEN is required")
    req = urllib.request.Request(
        "https://api.github.com" + path,
        headers={
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
            "User-Agent": "verification-stack-v2",
        },
    )
    with urllib.request.urlopen(req, timeout=60) as response:
        return json.load(response)


def list_repositories() -> list[dict[str, Any]]:
    repos: list[dict[str, Any]] = []
    page = 1
    while True:
        batch = api(
            f"/users/{OWNER}/repos?type=owner&sort=full_name&direction=asc&per_page=100&page={page}"
        )
        repos.extend(batch)
        if len(batch) < 100:
            return repos
        page += 1


def active_universe(repo: dict[str, Any]) -> bool:
    return (
        repo.get("visibility") == "public"
        and not repo.get("archived", False)
        and not repo.get("fork", False)
        and str(repo.get("pushed_at", "")) >= CUTOFF
    )


def tree_for(repo: dict[str, Any]) -> tuple[str, list[dict[str, Any]]]:
    name = repo["name"]
    default = repo["default_branch"]
    commit = api(f"/repos/{OWNER}/{name}/commits/{urllib.parse.quote(default, safe='')}")
    sha = commit["sha"]
    tree_sha = commit["commit"]["tree"]["sha"]
    tree = api(f"/repos/{OWNER}/{name}/git/trees/{tree_sha}?recursive=1")
    if tree.get("truncated"):
        raise RuntimeError(f"recursive tree truncated for {repo['full_name']}")
    return sha, tree["tree"]


def source_paths(tree: list[dict[str, Any]]) -> list[str]:
    return [
        item["path"]
        for item in tree
        if item.get("type") == "blob"
        and not item["path"].startswith(EXCLUDED_PREFIXES)
    ]


def has_test_or_ci(paths: set[str]) -> bool:
    return any(path.startswith(".github/workflows/") for path in paths) or any(
        path.startswith(("tests/", "test/", "__tests__/"))
        or Path(path).name.startswith("test_")
        or Path(path).name.endswith((".test.ts", ".test.tsx", ".spec.ts", ".spec.tsx"))
        for path in paths
    )


def obvious_private_dependency_signal(paths: set[str], tree: list[dict[str, Any]]) -> list[str]:
    # Selection is intentionally conservative but static. Exact installation is tested later with no secrets.
    suspicious_names = {
        ".npmrc", "pip.conf", "pip.ini", ".pypirc"
    }
    return sorted(path for path in paths if Path(path).name in suspicious_names)


def qualify(repo: dict[str, Any]) -> dict[str, Any]:
    sha, tree = tree_for(repo)
    paths_list = source_paths(tree)
    paths = set(paths_list)
    root = {path for path in paths if "/" not in path}
    test_or_ci = has_test_or_ci(paths)
    private_signals = obvious_private_dependency_signal(paths, tree)

    py_files = [path for path in paths if path.endswith(".py")]
    ts_files = [path for path in paths if path.endswith((".ts", ".tsx")) and not path.endswith(".d.ts")]
    tsconfigs = sorted(path for path in paths if Path(path).name.startswith("tsconfig") and path.endswith(".json"))

    python_reasons = {
        "root_manifest": bool(root & PY_MANIFESTS),
        "python_source_count": len(py_files),
        "test_or_ci": test_or_ci,
        "obvious_private_config_signals": private_signals,
    }
    typescript_reasons = {
        "package_json": "package.json" in root,
        "lockfile": bool(root & JS_LOCKS),
        "tsconfig_count": len(tsconfigs),
        "typescript_source_count": len(ts_files),
        "test_or_ci": test_or_ci,
        "obvious_private_config_signals": private_signals,
    }

    python_eligible = (
        python_reasons["root_manifest"]
        and len(py_files) >= 10
        and test_or_ci
        and not private_signals
    )
    typescript_eligible = (
        typescript_reasons["package_json"]
        and typescript_reasons["lockfile"]
        and len(tsconfigs) >= 1
        and len(ts_files) >= 10
        and test_or_ci
        and not private_signals
    )
    digest = hashlib.sha256(repo["full_name"].encode("utf-8")).hexdigest()
    return {
        "repository": repo["full_name"],
        "default_branch": repo["default_branch"],
        "head_sha": sha,
        "pushed_at": repo["pushed_at"],
        "selection_digest": digest,
        "python": {"eligible": python_eligible, **python_reasons},
        "typescript": {"eligible": typescript_eligible, **typescript_reasons},
    }


def choose(records: list[dict[str, Any]], language: str) -> dict[str, Any]:
    eligible = [record for record in records if record[language]["eligible"]]
    if not eligible:
        raise RuntimeError(f"no eligible {language} repository")
    return min(eligible, key=lambda item: item["selection_digest"])


def main() -> None:
    universe = [repo for repo in list_repositories() if active_universe(repo)]
    qualified: list[dict[str, Any]] = []
    failures: list[dict[str, str]] = []
    for repo in universe:
        try:
            qualified.append(qualify(repo))
        except Exception as exc:  # inventory failure is evidence; do not silently substitute.
            failures.append({"repository": repo["full_name"], "error": f"{type(exc).__name__}: {exc}"})

    python_inventory = sorted(
        [record for record in qualified if record["python"]["eligible"]],
        key=lambda item: item["selection_digest"],
    )
    ts_inventory = sorted(
        [record for record in qualified if record["typescript"]["eligible"]],
        key=lambda item: item["selection_digest"],
    )
    selected_python = choose(qualified, "python")
    selected_typescript = choose(qualified, "typescript")

    payload = {
        "schema_version": 1,
        "status": "frozen",
        "frozen_before_candidate_output_review": True,
        "frozen_at_utc": datetime.now(timezone.utc).isoformat(),
        "owner": OWNER,
        "activity_cutoff_utc": CUTOFF,
        "selection_rule": "lexicographically smallest sha256(repository_full_name) among eligible repositories, independently per language",
        "universe_count": len(universe),
        "inventory_failures": failures,
        "python_inventory": python_inventory,
        "typescript_inventory": ts_inventory,
        "selected": {
            "python": selected_python,
            "typescript": selected_typescript,
        },
        "interpretation_boundary": [
            "Repositories are frozen before controlled candidate-level output is inspected for article selection.",
            "Real repositories measure external validity, not total defect recall.",
            "A later no-secret installation failure is recorded as setup incompatibility; it does not trigger post-hoc reselection.",
        ],
    }
    OUT.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({
        "universe": len(universe),
        "python_eligible": len(python_inventory),
        "typescript_eligible": len(ts_inventory),
        "python_selected": selected_python["repository"],
        "typescript_selected": selected_typescript["repository"],
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
