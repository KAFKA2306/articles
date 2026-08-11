from __future__ import annotations

import base64
import hashlib
import json
import os
import urllib.parse
import urllib.request

import run as factory

GRAPHITI_REPO = os.environ.get("GRAPHITI_REPO", "KAFKA2306/graphiti")
GRAPHITI_TOKEN = os.environ.get("GRAPHITI_READ_TOKEN", "")
MAX_RECORDS = int(os.environ.get("GRAPHITI_IDEA_RECORDS", "4"))
MAX_CHARS_PER_RECORD = int(os.environ.get("GRAPHITI_IDEA_MAX_CHARS", "18000"))


def github_json(path: str) -> object:
    if not GRAPHITI_TOKEN:
        raise RuntimeError("GRAPHITI_READ_TOKEN is not configured")
    url = f"https://api.github.com/repos/{GRAPHITI_REPO}/{path.lstrip('/')}"
    req = urllib.request.Request(
        url,
        headers={
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {GRAPHITI_TOKEN}",
            "X-GitHub-Api-Version": "2022-11-28",
            "User-Agent": "KAFKA2306-article-factory/1.0",
        },
    )
    with urllib.request.urlopen(req, timeout=20) as response:
        return json.loads(response.read().decode("utf-8"))


def recent_weekly_records() -> list[dict[str, str]]:
    listing = github_json("contents/diary/weekly?ref=main")
    if not isinstance(listing, list):
        return []
    files = sorted(
        (
            item
            for item in listing
            if isinstance(item, dict)
            and item.get("type") == "file"
            and str(item.get("name", "")).endswith(".md")
        ),
        key=lambda item: str(item.get("name", "")),
        reverse=True,
    )[:MAX_RECORDS]

    records: list[dict[str, str]] = []
    for item in files:
        path = str(item["path"])
        payload = github_json(f"contents/{urllib.parse.quote(path, safe='/')}?ref=main")
        if not isinstance(payload, dict) or payload.get("encoding") != "base64":
            continue
        raw = base64.b64decode(str(payload.get("content", ""))).decode("utf-8", errors="replace")
        records.append({
            "name": str(item.get("name", "")),
            "content": raw[:MAX_CHARS_PER_RECORD],
        })
    return records


def extract_public_safe_topic(records: list[dict[str, str]], public_signals: list[dict[str, object]]) -> dict[str, object]:
    digest = hashlib.sha256(
        "\n".join(record["content"] for record in records).encode("utf-8")
    ).hexdigest()[:16]
    private_corpus = "\n\n--- RECORD ---\n\n".join(record["content"] for record in records)

    prompt = f"""
以下はprivateなGraphiti diaryです。記事本文の根拠ではなく、テーマ発見だけに使ってください。

厳守:
- 個人情報、税務、資産、健康、旅行、私生活、勤務先内部情報、未公開情報をテーマにしない。
- private diaryの文章を引用・要約して公開しない。
- 記事化候補は、下記PUBLIC_GITHUB_SIGNALSだけで再現・検証できる技術テーマに限定する。
- 設計判断、失敗、境界条件、fail-close、provenance、API/MCP、CI、データ契約など、他のエンジニアに再利用可能な知見を優先する。
- PUBLIC_GITHUB_SIGNALSに公開証拠が2件以上ないテーマは選ばない。
- Graphiti自体を記事の出典として扱わない。

PRIVATE_GRAPHITI_DIARY:
{private_corpus}

PUBLIC_GITHUB_SIGNALS:
{json.dumps(public_signals, ensure_ascii=False, indent=2)}

JSONのみ返してください:
{{
  "title": "...",
  "audience": "...",
  "problem": "...",
  "why_unique": "...",
  "evidence_urls": ["https://github.com/KAFKA2306/...", "https://github.com/KAFKA2306/..."],
  "design_lessons": ["..."],
  "privacy_check": "PASS"
}}
"""
    result = json.loads(factory.model_call(
        "あなたはprivacy-firstの技術編集長です。private memoryは発想にだけ使い、公開証拠へ必ず再接地します。",
        prompt,
        temperature=0.0,
        json_mode=True,
    ))
    urls = result.get("evidence_urls", [])
    if result.get("privacy_check") != "PASS":
        raise RuntimeError("Graphiti seed privacy gate failed")
    if not isinstance(urls, list) or len(urls) < 2:
        raise RuntimeError("Graphiti seed lacks two public evidence URLs")
    if any(not str(url).startswith("https://github.com/KAFKA2306/") for url in urls):
        raise RuntimeError("Graphiti seed contains non-public-evidence URL")
    result["record_digest"] = digest
    return result


def main() -> int:
    if not GRAPHITI_TOKEN:
        print("graphiti_seed=skipped reason=GRAPHITI_READ_TOKEN_missing")
        return 0

    records = recent_weekly_records()
    if not records:
        print("graphiti_seed=skipped reason=no_records")
        return 0

    public_signals = factory.collect_public_github_signals(factory.CONFIG["owner"])
    topic = extract_public_safe_topic(records, public_signals)
    article = factory.draft_article(topic, public_signals)
    sources_ok, source_report = factory.source_gate(article)
    review = factory.aggregate_evaluations(article, rounds=1)

    meta = {
        "idea_source": "private-graphiti-diary",
        "idea_only": True,
        "raw_private_content_persisted": False,
        "record_count": len(records),
        "record_digest": topic.pop("record_digest", None),
        "topic": topic,
        "initial_review": review,
        "initial_sources": source_report,
    }
    path = factory.save_candidate(article, meta)
    print(
        f"graphiti_candidate={path.relative_to(factory.ROOT)} "
        f"sources_ok={sources_ok} score={review['overall']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
