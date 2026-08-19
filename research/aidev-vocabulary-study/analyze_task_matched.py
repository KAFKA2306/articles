#!/usr/bin/env python3
"""Robustness analysis matching Agentic-PR and Human-PR by repository and task type.

This is a post-specified robustness analysis motivated by task-mix confounding in
the repository-only comparison. Task labels come from AIDev's published
`pr_task_type` and `human_pr_task_type` tables. The labels are themselves LLM
classifications, so this analysis does not treat them as ground truth.
"""

from __future__ import annotations

import hashlib
import json
import urllib.request
from pathlib import Path

import pandas as pd

import analyze as base

TASK_INPUTS = {
    "agent_task": (
        f"{base.BASE}/pr_task_type.parquet",
        "f32a97a45ac944f4ea473327e62d8f41361502c2b6b3778e76fb64c2b8896476",
    ),
    "human_task": (
        f"{base.BASE}/human_pr_task_type.parquet",
        "5527d52bfd9605a25d1ed1ef03bce0e1cc217f6ffed936e2be1b80a04123e658",
    ),
}


def download_task(name: str, out_dir: Path) -> Path:
    url, expected = TASK_INPUTS[name]
    path = out_dir / f"{name}.parquet"
    if not path.exists() or base.sha256(path) != expected:
        urllib.request.urlretrieve(url, path)
    actual = base.sha256(path)
    if actual != expected:
        raise RuntimeError(f"{name}: SHA-256 mismatch: {actual} != {expected}")
    return path


def unambiguous_task_labels(df: pd.DataFrame, group: str) -> tuple[pd.DataFrame, dict[str, int]]:
    required = {"id", "type"}
    missing = required - set(df.columns)
    if missing:
        raise RuntimeError(f"{group}: task table missing {sorted(missing)}; columns={sorted(df.columns)}")

    labels = df.loc[:, ["id", "type"]].dropna().copy()
    labels["task_type"] = labels["type"].astype(str).str.strip().str.lower()
    labels = labels[labels["task_type"] != ""].drop(columns="type")

    # Exclude PR IDs with conflicting labels rather than selecting one arbitrarily.
    unique_counts = labels.groupby("id")["task_type"].nunique()
    conflicting_ids = set(unique_counts[unique_counts > 1].index)
    if conflicting_ids:
        labels = labels[~labels["id"].isin(conflicting_ids)]
    labels = labels.drop_duplicates(subset=["id", "task_type"]).drop_duplicates(subset=["id"])

    return labels, {
        "task_table_rows": int(len(df)),
        "labeled_unique_prs": int(labels["id"].nunique()),
        "conflicting_pr_ids_excluded": int(len(conflicting_ids)),
        "task_types": int(labels["task_type"].nunique()),
    }


def stable_stratum_key(group: str, repo_key: str, task_type: str, pr_id: object) -> str:
    raw = f"{base.SEED}|task-matched|{group}|{repo_key}|{task_type}|{pr_id}".encode()
    return hashlib.sha256(raw).hexdigest()


def balance_by_repository_and_task(
    agent: pd.DataFrame, human: pd.DataFrame
) -> tuple[pd.DataFrame, pd.DataFrame, dict[str, int]]:
    agent_keys = set(zip(agent["repo_key"], agent["task_type"]))
    human_keys = set(zip(human["repo_key"], human["task_type"]))
    shared = sorted(agent_keys & human_keys, key=lambda x: (str(x[0]), str(x[1])))

    a_parts: list[pd.DataFrame] = []
    h_parts: list[pd.DataFrame] = []
    retained_strata = 0
    for repo_key, task_type in shared:
        a = agent[(agent.repo_key == repo_key) & (agent.task_type == task_type)].copy()
        h = human[(human.repo_key == repo_key) & (human.task_type == task_type)].copy()
        n = min(len(a), len(h))
        if n == 0:
            continue
        retained_strata += 1
        a["_key"] = [stable_stratum_key("agent", repo_key, task_type, x) for x in a.id]
        h["_key"] = [stable_stratum_key("human", repo_key, task_type, x) for x in h.id]
        a_parts.append(a.sort_values("_key").head(n).drop(columns="_key"))
        h_parts.append(h.sort_values("_key").head(n).drop(columns="_key"))

    if not a_parts:
        raise RuntimeError("No shared repository/task-type strata")

    a_bal = pd.concat(a_parts, ignore_index=True)
    h_bal = pd.concat(h_parts, ignore_index=True)
    return a_bal, h_bal, {
        "shared_repository_task_strata": int(len(shared)),
        "retained_repository_task_strata": int(retained_strata),
        "retained_repositories": int(len(set(a_bal.repo_key) & set(h_bal.repo_key))),
        "balanced_agent_prs": int(len(a_bal)),
        "balanced_human_prs": int(len(h_bal)),
    }


def analyze_scope(
    raw_agent: pd.DataFrame,
    raw_human: pd.DataFrame,
    agent_labels: pd.DataFrame,
    human_labels: pd.DataFrame,
    scope: str,
) -> tuple[pd.DataFrame, dict[str, object]]:
    agent = base.prepare(raw_agent, "agent", scope).merge(agent_labels, on="id", how="inner", validate="many_to_one")
    human = base.prepare(raw_human, "human", scope).merge(human_labels, on="id", how="inner", validate="many_to_one")
    a_bal, h_bal, matching = balance_by_repository_and_task(agent, human)
    balanced = pd.concat([a_bal, h_bal], ignore_index=True)

    rows: list[dict[str, object]] = []
    for (repo_key, group), part in balanced.groupby(["repo_key", "group"], sort=True):
        rows.append({"scope": scope, "repo_key": repo_key, "group": group, **base.repo_metrics(part)})
    metrics = pd.DataFrame(rows)

    sensitivity: dict[str, object] = {}
    for minimum in base.MINIMUM_DOCUMENTS:
        sensitivity[str(minimum)] = {
            metric: base.paired_summary(metrics, metric, minimum)
            for metric in ["median_words", "reused_unique_share", "reused_event_share"]
        }

    return metrics, {
        "labeled_usable_rows": {"agent": int(len(agent)), "human": int(len(human))},
        "matching": matching,
        "minimum_documents_sensitivity": sensitivity,
    }


def main() -> None:
    root = Path(__file__).resolve().parent
    data_dir = root / ".data"
    out_dir = root / "results"
    data_dir.mkdir(exist_ok=True)
    out_dir.mkdir(exist_ok=True)

    raw_agent = pd.read_parquet(base.download("agent", data_dir))
    raw_human = pd.read_parquet(base.download("human", data_dir))
    raw_agent_task = pd.read_parquet(download_task("agent_task", data_dir))
    raw_human_task = pd.read_parquet(download_task("human_task", data_dir))

    agent_labels, agent_label_stats = unambiguous_task_labels(raw_agent_task, "agent")
    human_labels, human_label_stats = unambiguous_task_labels(raw_human_task, "human")

    scopes: dict[str, object] = {}
    metric_frames: list[pd.DataFrame] = []
    for scope in base.SCOPES:
        metrics, summary = analyze_scope(raw_agent, raw_human, agent_labels, human_labels, scope)
        scopes[scope] = summary
        metric_frames.append(metrics)
    pd.concat(metric_frames, ignore_index=True).to_csv(out_dir / "task_matched_repository_metrics.csv", index=False)

    result = {
        "study_input": {
            "dataset": "hao-li/AIDev",
            "revision": base.AIDEV_REVISION,
            "task_input_sha256": {k: v[1] for k, v in TASK_INPUTS.items()},
            "no_kafka2306_repositories_used_as_data": True,
        },
        "task_labels": {"agent": agent_label_stats, "human": human_label_stats},
        "scopes": scopes,
        "analysis_status": "post-specified robustness analysis",
        "interpretation_boundary": (
            "This analysis controls the observed AIDev task-category mix within each repository. "
            "AIDev task types are LLM classifications of PR titles and commit messages, so they may contain measurement error. "
            "Matching on task type does not make the observational comparison causal."
        ),
    }
    (out_dir / "task_matched_summary.json").write_text(
        json.dumps(result, indent=2, sort_keys=True), encoding="utf-8"
    )
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
