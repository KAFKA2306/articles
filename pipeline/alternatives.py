"""Fail-closed evidence for article topic alternatives; not a semantic truth grader."""
from __future__ import annotations
from urllib.parse import urlparse

KINDS = {"incumbent", "direct", "adjacent", "keep", "merge", "private"}

def alternatives_ready(topic: dict[str, object]) -> bool:
    """Require comparable alternatives and refuse unsupported winner claims.

    This checks the decision record, not whether linked evidence is true.
    """
    items = topic.get("alternatives")
    if not isinstance(items, list) or len(items) < 3:
        return False
    kinds: set[str] = set()
    names: set[str] = set()
    for item in items:
        if not isinstance(item, dict):
            return False
        kind = item.get("kind")
        name = item.get("name")
        if kind not in KINDS or not isinstance(name, str) or not name.strip():
            return False
        if name in names:
            return False
        names.add(name)
        kinds.add(kind)
        if not isinstance(item.get("reader_job"), str) or not item["reader_job"].strip():
            return False
        urls = item.get("primary_urls")
        if not isinstance(urls, list) or not urls or any(
            not isinstance(url, str) or
            urlparse(url).scheme != "https" or not urlparse(url).netloc
            for url in urls
        ):
            return False
        if not isinstance(item.get("tradeoff"), str) or not item["tradeoff"].strip():
            return False
    if not {"incumbent", "direct", "adjacent"}.issubset(kinds):
        return False
    if not isinstance(topic.get("unsearched_scope"), str):
        return False
    decision = topic.get("alternative_decision")
    if not isinstance(decision, dict):
        return False
    verdict = decision.get("verdict")
    if verdict not in {"unresolved", "keep", "merge", "private", "choose"}:
        return False
    if verdict == "choose":
        if decision.get("selected") not in names:
            return False
        comparison = decision.get("comparison")
        if not isinstance(comparison, dict) or not all(
            isinstance(comparison.get(key), str) and comparison[key].strip()
            for key in ("same_reader_job", "same_conditions", "measured_result", "artifact_url")
        ):
            return False
        if urlparse(comparison["artifact_url"]).scheme != "https":
            return False
    return True
