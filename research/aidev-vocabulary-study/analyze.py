#!/usr/bin/env python3
"""Compare repeated multiword expressions in matched Agentic-PR and Human-PR corpora.

The input is the public AIDev dataset only. No KAFKA2306 repository content is
used as study data. Inputs are pinned by SHA-256. The analysis balances the two
classes within each repository before computing document-frequency measures.
"""

from __future__ import annotations

import hashlib
import json
import math
import re
import sys
import urllib.request
from collections import Counter
from pathlib import Path
from urllib.parse import urlparse

import numpy as np
import pandas as pd
from scipy.stats import wilcoxon

SEED = "2026-08-16-aidev-vocabulary"
BASE = "https://huggingface.co/datasets/hao-li/AIDev/resolve/main"
INPUTS = {
    "agent": (
        f"{BASE}/pull_request.parquet",
        "08f520b5ef36b6281f82090db09ac14aefc3534ee113886e7bc85131fd8d214c",
    ),
    "human": (
        f"{BASE}/human_pull_request.parquet",
        "910238f8fe5deb544ae82be343232ff6838f271f3de4b4e4787a515336a91248",
    ),
}
TOKEN_RE = re.compile(r"[A-Za-z][A-Za-z0-9_+.-]*")
URL_RE = re.compile(r"https?://\S+|www\.\S+", re.I)
CODE_FENCE_RE = re.compile(r"```.*?```", re.S)
INLINE_CODE_RE = re.compile(r"`[^`]+`")


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def download(name: str, out_dir: Path) -> Path:
    url, expected = INPUTS[name]
    path = out_dir / f"{name}.parquet"
    if not path.exists() or sha256(path) != expected:
        urllib.request.urlretrieve(url, path)
    actual = sha256(path)
    if actual != expected:
        raise RuntimeError(f"{name}: SHA-256 mismatch: {actual} != {expected}")
    return path


def normalize_text(title: object, body: object) -> list[str]:
    text = f"{'' if pd.isna(title) else title}\n{'' if pd.isna(body) else body}"
    text = CODE_FENCE_RE.sub(" ", text)
    text = INLINE_CODE_RE.sub(" ", text)
    text = URL_RE.sub(" ", text)
    return [m.group(0).lower() for m in TOKEN_RE.finditer(text)]


def ngrams(tokens: list[str], n_min: int = 2, n_max: int = 4) -> set[str]:
    result: set[str] = set()
    for n in range(n_min, n_max + 1):
        if len(tokens) >= n:
            result.update(" ".join(tokens[i : i + n]) for i in range(len(tokens) - n + 1))
    return result


def repo_from_url(value: object) -> str | None:
    if pd.isna(value):
        return None
    try:
        parsed = urlparse(str(value))
    except ValueError:
        return None
    parts = [p for p in parsed.path.split("/") if p]
    if parsed.netloc == "api.github.com" and len(parts) >= 3 and parts[0] == "repos":
        return f"{parts[1]}/{parts[2]}".lower()
    if parsed.netloc in {"github.com", "www.github.com"} and len(parts) >= 2:
        return f"{parts[0]}/{parts[1]}".lower()
    return None


def add_repository_key(df: pd.DataFrame, group: str) -> pd.DataFrame:
    url_columns = [c for c in ["repo_url", "repository_url", "html_url", "url"] if c in df.columns]
    keys: list[str | None] = []
    for row in df.itertuples(index=False):
        key = None
        for column in url_columns:
            key = repo_from_url(getattr(row, column))
            if key:
                break
        if key is None and "repo_id" in df.columns:
            value = getattr(row, "repo_id")
            key = None if pd.isna(value) else f"id:{value}"
        keys.append(key)
    out = df.copy()
    out["repo_key"] = keys
    if out["repo_key"].notna().sum() == 0:
        raise RuntimeError(f"{group}: cannot derive repository identity; columns={sorted(df.columns)}")
    return out


def stable_key(group: str, repo_key: object, pr_id: object) -> str:
    raw = f"{SEED}|{group}|{repo_key}|{pr_id}".encode()
    return hashlib.sha256(raw).hexdigest()


def prepare(df: pd.DataFrame, group: str) -> pd.DataFrame:
    required = {"id", "title", "body"}
    missing = required - set(df.columns)
    if missing:
        raise RuntimeError(f"{group}: missing required columns: {sorted(missing)}; columns={sorted(df.columns)}")
    df = add_repository_key(df, group)
    keep = [c for c in ["id", "repo_key", "title", "body", "created_at"] if c in df.columns]
    out = df.loc[:, keep].copy().dropna(subset=["repo_key", "id"])
    out["group"] = group
    out["tokens"] = [normalize_text(t, b) for t, b in zip(out["title"], out["body"])]
    out = out[out["tokens"].map(len) > 0].copy()
    out["ngrams"] = out["tokens"].map(ngrams)
    return out


def balance(agent: pd.DataFrame, human: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, dict[str, int]]:
    shared = sorted(set(agent.repo_key) & set(human.repo_key), key=str)
    a_parts: list[pd.DataFrame] = []
    h_parts: list[pd.DataFrame] = []
    eligible = 0
    for repo_key in shared:
        a = agent[agent.repo_key == repo_key].copy()
        h = human[human.repo_key == repo_key].copy()
        n = min(len(a), len(h))
        # At least two documents per class are needed to measure cross-document reuse.
        if n < 2:
            continue
        eligible += 1
        a["_key"] = [stable_key("agent", repo_key, x) for x in a.id]
        h["_key"] = [stable_key("human", repo_key, x) for x in h.id]
        a_parts.append(a.sort_values("_key").head(n).drop(columns="_key"))
        h_parts.append(h.sort_values("_key").head(n).drop(columns="_key"))
    if not a_parts:
        raise RuntimeError(
            "No matched repositories with at least two PRs per class; "
            f"agent_keys={agent.repo_key.nunique()}, human_keys={human.repo_key.nunique()}, shared={len(shared)}"
        )
    a_bal = pd.concat(a_parts, ignore_index=True)
    h_bal = pd.concat(h_parts, ignore_index=True)
    return a_bal, h_bal, {
        "shared_repositories_before_minimum": len(shared),
        "matched_repositories": eligible,
        "balanced_agent_prs": len(a_bal),
        "balanced_human_prs": len(h_bal),
    }


def repo_metrics(df: pd.DataFrame) -> dict[str, float]:
    doc_freq: Counter[str] = Counter()
    document_ngram_events = 0
    word_counts: list[int] = []
    for row in df.itertuples(index=False):
        doc_freq.update(row.ngrams)
        document_ngram_events += len(row.ngrams)
        word_counts.append(len(row.tokens))
    unique = len(doc_freq)
    reused = sum(1 for v in doc_freq.values() if v >= 2)
    reused_events = sum(v for v in doc_freq.values() if v >= 2)
    return {
        "documents": float(len(df)),
        "median_words": float(np.median(word_counts)),
        "unique_ngrams": float(unique),
        "reused_unique_share": float(reused / unique) if unique else math.nan,
        "reused_event_share": float(reused_events / document_ngram_events) if document_ngram_events else math.nan,
    }


def paired_summary(metrics: pd.DataFrame, metric: str) -> dict[str, float | int | None]:
    wide = metrics.pivot(index="repo_key", columns="group", values=metric).dropna()
    delta = wide["agent"] - wide["human"]
    stat = wilcoxon(wide["agent"], wide["human"], zero_method="wilcox", alternative="two-sided") if (delta != 0).any() else None
    rng = np.random.default_rng(20260816)
    values = delta.to_numpy(dtype=float)
    boot = np.array([rng.choice(values, size=len(values), replace=True).mean() for _ in range(10_000)])
    return {
        "repositories": int(len(wide)),
        "agent_mean": float(wide["agent"].mean()),
        "human_mean": float(wide["human"].mean()),
        "mean_paired_difference_agent_minus_human": float(delta.mean()),
        "median_paired_difference_agent_minus_human": float(delta.median()),
        "bootstrap_95pct_ci_mean_difference_low": float(np.quantile(boot, 0.025)),
        "bootstrap_95pct_ci_mean_difference_high": float(np.quantile(boot, 0.975)),
        "wilcoxon_statistic": float(stat.statistic) if stat else None,
        "wilcoxon_p_value": float(stat.pvalue) if stat else None,
    }


def global_reused_phrases(df: pd.DataFrame, minimum_documents: int = 3) -> Counter[str]:
    counts: Counter[str] = Counter()
    for phrases in df.ngrams:
        counts.update(phrases)
    return Counter({k: v for k, v in counts.items() if v >= minimum_documents})


def main() -> None:
    root = Path(__file__).resolve().parent
    data_dir = root / ".data"
    out_dir = root / "results"
    data_dir.mkdir(exist_ok=True)
    out_dir.mkdir(exist_ok=True)

    raw_agent = pd.read_parquet(download("agent", data_dir))
    raw_human = pd.read_parquet(download("human", data_dir))
    agent = prepare(raw_agent, "agent")
    human = prepare(raw_human, "human")
    a_bal, h_bal, counts = balance(agent, human)
    balanced = pd.concat([a_bal, h_bal], ignore_index=True)

    rows: list[dict[str, object]] = []
    for (repo_key, group), part in balanced.groupby(["repo_key", "group"], sort=True):
        rows.append({"repo_key": repo_key, "group": group, **repo_metrics(part)})
    metrics = pd.DataFrame(rows)
    metrics.to_csv(out_dir / "repository_metrics.csv", index=False)

    summaries = {
        metric: paired_summary(metrics, metric)
        for metric in ["median_words", "reused_unique_share", "reused_event_share"]
    }

    top_rows: list[dict[str, object]] = []
    for group, part in [("agent", a_bal), ("human", h_bal)]:
        for phrase, docs in global_reused_phrases(part).most_common(500):
            top_rows.append({"group": group, "phrase": phrase, "documents": docs})
    pd.DataFrame(top_rows).to_csv(out_dir / "top_reused_phrases.csv", index=False)

    result = {
        "study_input": {
            "dataset": "hao-li/AIDev",
            "agent_file": "pull_request.parquet",
            "human_file": "human_pull_request.parquet",
            "input_sha256": {k: v[1] for k, v in INPUTS.items()},
            "no_kafka2306_repositories_used_as_data": True,
        },
        "raw_rows": {"agent": int(len(raw_agent)), "human": int(len(raw_human))},
        "nonempty_text_rows": {"agent": int(len(agent)), "human": int(len(human))},
        "repository_keys": {"agent": int(agent.repo_key.nunique()), "human": int(human.repo_key.nunique())},
        "matching": counts,
        "analysis": summaries,
        "interpretation_boundary": (
            "These are descriptive paired comparisons in AIDev's sampled popular-repository corpus. "
            "They do not identify whether an AI agent caused any phrase, and reused n-grams are not automatically jargon."
        ),
    }
    (out_dir / "summary.json").write_text(json.dumps(result, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise
