from __future__ import annotations

import base64
import hashlib
import json
import os
import re
import urllib.parse
import urllib.request

from . import core

TOKEN_ENV = "GRAPHITI_READ_TOKEN"


def graphiti_repo() -> str:
    return os.environ.get(
        "GRAPHITI_REPO",
        str(core.CONFIG["graphiti"]["repo"]),
    )


def graphiti_token() -> str:
    return os.environ.get(TOKEN_ENV, "")


def github_json(path: str) -> object:
    token = graphiti_token()
    if not token:
        raise RuntimeError(f"{TOKEN_ENV} is not configured")
    url = f"https://api.github.com/repos/{graphiti_repo()}/{path.lstrip('/')}"
    request = urllib.request.Request(
        url,
        headers={
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {token}",
            "X-GitHub-Api-Version": "2022-11-28",
            "User-Agent": "KAFKA2306-articles/2.0",
        },
    )
    with urllib.request.urlopen(request, timeout=20) as response:
        return json.loads(response.read().decode("utf-8"))


def _section(text: str, name: str) -> str:
    pattern = re.compile(
        rf"^##\s+{re.escape(name)}\s*$\n(.*?)(?=^##\s+|\Z)",
        re.IGNORECASE | re.MULTILINE | re.DOTALL,
    )
    match = pattern.search(text)
    return match.group(1).strip() if match else ""


def _first_bullets(text: str, limit: int) -> list[str]:
    bullets: list[str] = []
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("- "):
            bullets.append(stripped)
        if len(bullets) >= limit:
            break
    return bullets


def compact_weekly_record(name: str, text: str) -> dict[str, object]:
    """Reduce a private weekly diary to a readable in-memory view.

    The compact view is still private and must never be persisted to this public repo.
    It exists only to reduce noise before topic discovery.
    """
    summary = _section(text, "brief") or _section(text, "summary")
    highlights = _section(text, "highlights")
    decisions = _section(text, "decisions")
    next_actions = _section(text, "next") or _section(text, "next actions")
    timeline = _section(text, "timeline")

    return {
        "week": name,
        "summary": summary[:5000],
        "highlights": _first_bullets(highlights, 12),
        "decisions": _first_bullets(decisions, 12),
        "next_actions": _first_bullets(next_actions, 8),
        "timeline_sample": _first_bullets(timeline, 16),
    }


def recent_weekly_records() -> list[dict[str, str]]:
    cfg = core.CONFIG["graphiti"]
    weekly_dir = str(cfg["weekly_dir"])
    max_records = int(
        os.environ.get("GRAPHITI_IDEA_RECORDS", str(cfg["max_records"]))
    )
    max_chars = int(
        os.environ.get(
            "GRAPHITI_IDEA_MAX_CHARS",
            str(cfg["max_chars_per_record"]),
        )
    )
    listing = github_json(
        f"contents/{urllib.parse.quote(weekly_dir, safe='/')}?ref=main"
    )
    if not isinstance(listing, list):
        return []
    files = sorted(
        (
            item
            for item in listing
            if isinstance(item, dict)
            and item.get("type") == "file"
            and str(item.get("name", "")).endswith(".md")
            and not str(item.get("name", "")).lower().startswith("readme")
        ),
        key=lambda item: str(item.get("name", "")),
        reverse=True,
    )[:max_records]

    records: list[dict[str, str]] = []
    for item in files:
        path = str(item["path"])
        payload = github_json(
            f"contents/{urllib.parse.quote(path, safe='/')}?ref=main"
        )
        if not isinstance(payload, dict) or payload.get("encoding") != "base64":
            continue
        raw = base64.b64decode(str(payload.get("content", ""))).decode(
            "utf-8",
            errors="replace",
        )
        records.append(
            {
                "name": str(item.get("name", "")),
                "content": raw[:max_chars],
            }
        )
    return records


def extract_public_safe_topic(
    records: list[dict[str, str]],
    public_signals: list[dict[str, object]],
) -> dict[str, object]:
    digest = hashlib.sha256(
        "\n".join(record["content"] for record in records).encode("utf-8")
    ).hexdigest()[:16]
    readable = [
        compact_weekly_record(record["name"], record["content"])
        for record in records
    ]

    prompt = f"""
以下はprivateなGraphiti weekly diaryを読みやすく圧縮した作業用コンテキストです。
記事本文の根拠ではなく、テーマ発見だけに使ってください。

厳守:
- private weeklyの文章を引用・要約して公開しない。
- 個人情報、税務、資産、健康、旅行、私生活、勤務先内部情報、未公開情報をテーマにしない。
- 記事化候補は下記PUBLIC_GITHUB_SIGNALSだけで再現・検証できる技術テーマに限定する。
- PUBLIC_GITHUB_SIGNALSに公開証拠が2件以上ないテーマは選ばない。
- Graphiti自体を記事の出典として扱わない。
- 設計判断、失敗、境界条件、fail-close、provenance、API/MCP、CI、
  データ契約など再利用可能な技術知見を優先する。

PRIVATE_WEEKLY_CONTEXT:
{json.dumps(readable, ensure_ascii=False, indent=2)}

PUBLIC_GITHUB_SIGNALS:
{json.dumps(public_signals, ensure_ascii=False, indent=2)}

JSONのみ返してください:
{{
  "title": "...",
  "audience": "...",
  "problem": "...",
  "why_unique": "...",
  "evidence_urls": [
    "https://github.com/KAFKA2306/...",
    "https://github.com/KAFKA2306/..."
  ],
  "design_lessons": ["..."],
  "privacy_check": "PASS"
}}
"""
    result = json.loads(
        core.model_call(
            "あなたはprivacy-firstの技術編集長です。private memoryは発想にだけ使い、公開証拠へ必ず再接地します。",
            prompt,
            temperature=0.0,
            json_mode=True,
        )
    )
    urls = result.get("evidence_urls", [])
    if result.get("privacy_check") != "PASS":
        raise RuntimeError("Graphiti seed privacy gate failed")
    if not isinstance(urls, list) or len(urls) < 2:
        raise RuntimeError("Graphiti seed lacks two public evidence URLs")
    if any(
        not str(url).startswith("https://github.com/KAFKA2306/")
        for url in urls
    ):
        raise RuntimeError("Graphiti seed contains non-KAFKA2306 evidence URL")
    result["record_digest"] = digest
    return result


def generate_graphiti_candidate() -> str | None:
    if not graphiti_token():
        print(f"graphiti=skipped reason={TOKEN_ENV}_missing")
        return None

    records = recent_weekly_records()
    if not records:
        print("graphiti=skipped reason=no_weekly_records")
        return None

    public_signals = core.collect_public_github_signals(str(core.CONFIG["owner"]))
    topic = extract_public_safe_topic(records, public_signals)
    digest = topic.pop("record_digest", None)
    article = core.draft_article(topic, public_signals)
    sources_ok, source_report = core.source_gate(article)
    review = core.aggregate_evaluations(article, rounds=1)

    meta = {
        "idea_source": "private-graphiti-weekly",
        "idea_only": True,
        "raw_private_content_persisted": False,
        "record_count": len(records),
        "record_digest": digest,
        "topic": topic,
        "initial_review": review,
        "initial_sources": source_report,
    }
    path = core.save_candidate(article, meta)
    print(
        f"graphiti_candidate={path.relative_to(core.ROOT)} "
        f"sources_ok={sources_ok} score={review['overall']}"
    )
    return str(path)
