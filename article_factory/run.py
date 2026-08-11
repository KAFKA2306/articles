from __future__ import annotations

import hashlib
import json
import os
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONFIG = json.loads((ROOT / "article_factory" / "config.json").read_text(encoding="utf-8"))
PROMPT = (ROOT / "article_factory" / "prompt.md").read_text(encoding="utf-8")
JST = timezone(timedelta(hours=9))
NOW = datetime.now(JST)
MODEL_ENDPOINT = "https://models.github.ai/inference/chat/completions"
TOKEN = os.environ.get("GITHUB_TOKEN", "")
MODEL = os.environ.get("ARTICLE_MODEL", CONFIG["model"])
MODE = os.environ.get("ARTICLE_MODE", "candidate")


def http_json(url: str, *, headers: dict[str, str] | None = None) -> object:
    req = urllib.request.Request(url, headers=headers or {"User-Agent": "KAFKA2306-article-factory/1.0"})
    with urllib.request.urlopen(req, timeout=20) as response:
        return json.loads(response.read().decode("utf-8"))


def model_call(system: str, user: str, *, temperature: float = 0.2, json_mode: bool = False) -> str:
    if not TOKEN:
        raise RuntimeError("GITHUB_TOKEN is required")
    payload: dict[str, object] = {
        "model": MODEL,
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
        "temperature": temperature,
    }
    if json_mode:
        payload["response_format"] = {"type": "json_object"}
    req = urllib.request.Request(
        MODEL_ENDPOINT,
        data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
        headers={
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {TOKEN}",
            "Content-Type": "application/json",
            "User-Agent": "KAFKA2306-article-factory/1.0",
        },
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=120) as response:
        data = json.loads(response.read().decode("utf-8"))
    return data["choices"][0]["message"]["content"].strip()


def collect_public_github_signals(owner: str) -> list[dict[str, object]]:
    repos = http_json(
        f"https://api.github.com/users/{urllib.parse.quote(owner)}/repos?sort=pushed&direction=desc&per_page=12"
    )
    signals: list[dict[str, object]] = []
    if not isinstance(repos, list):
        return signals
    for repo in repos[:8]:
        if not isinstance(repo, dict) or repo.get("fork"):
            continue
        name = str(repo.get("name", ""))
        default_branch = str(repo.get("default_branch", "main"))
        signal: dict[str, object] = {
            "repo": repo.get("html_url"),
            "name": name,
            "description": repo.get("description"),
            "language": repo.get("language"),
            "pushed_at": repo.get("pushed_at"),
            "stars": repo.get("stargazers_count"),
        }
        try:
            commits = http_json(
                f"https://api.github.com/repos/{urllib.parse.quote(owner)}/{urllib.parse.quote(name)}/commits?sha={urllib.parse.quote(default_branch)}&per_page=1"
            )
            if isinstance(commits, list) and commits:
                latest = commits[0]
                commit = latest.get("commit", {}) if isinstance(latest, dict) else {}
                message = commit.get("message") if isinstance(commit, dict) else None
                signal["latest_commit"] = latest.get("html_url") if isinstance(latest, dict) else None
                signal["latest_commit_message"] = message
        except Exception as exc:
            signal["commit_fetch_error"] = type(exc).__name__
        signals.append(signal)
    return signals


def existing_titles() -> list[str]:
    titles: list[str] = []
    for base in (ROOT / "articles", ROOT / "candidates"):
        if not base.exists():
            continue
        for path in base.glob("*.md"):
            text = path.read_text(encoding="utf-8", errors="ignore")
            match = re.search(r"^#\s+(.+)$", text, flags=re.MULTILINE)
            if match:
                titles.append(match.group(1).strip())
            else:
                fm = re.search(r'^title:\s*["\']?(.+?)["\']?\s*$', text, flags=re.MULTILINE)
                if fm:
                    titles.append(fm.group(1).strip())
    return titles[-40:]


def choose_topic(signals: list[dict[str, object]]) -> dict[str, object]:
    user = f"""
直近の公開GitHubシグナルから技術記事候補を{CONFIG['candidate_count']}件作り、最も強い1件を選んでください。
一般論より、実装証拠・設計判断・失敗・定量検証が揃う題材を優先します。
弱点補強の優先順: backend, infrastructure, product-engineering, technical-leadership, data-engineering, ai-agents。
既存タイトルとの焼き直しは禁止です。

既存タイトル:
{json.dumps(existing_titles(), ensure_ascii=False)}

GitHubシグナル:
{json.dumps(signals, ensure_ascii=False, indent=2)}

JSONのみ返してください。形式:
{{"selected":{{"title":"...","audience":"...","problem":"...","evidence_urls":["..."],"why_unique":"..."}},"alternatives":[...]}}
"""
    return json.loads(model_call("あなたは技術編集長です。証拠の弱いテーマは選びません。", user, json_mode=True))


def draft_article(topic: dict[str, object], signals: list[dict[str, object]]) -> str:
    user = f"""
以下の契約に従って日本語の完成記事を書いてください。Markdown本文のみ。front matterは不要です。

{PROMPT}

選定テーマ:
{json.dumps(topic, ensure_ascii=False, indent=2)}

利用可能な一次証拠:
{json.dumps(signals, ensure_ascii=False, indent=2)}

重要:
- GitHub上で確認できない実装事実を創作しない。
- 外部仕様を断定する場合は公式一次情報URLを本文の直後に付ける。
- URLを確信できない場合、その外部仕様自体を削除する。
- 最後に「一次情報・再現証拠」節を設け、本文で実際に使ったURLだけを列挙する。
- 最低でもKAFKA2306 GitHub URLを2件、外部の公式一次情報を1件含める。
"""
    return model_call("あなたは一次証拠を最優先するシニア技術ライターです。", user, temperature=0.25)


URL_RE = re.compile(r"https://[^\s)\]>\"']+")


def verify_url(url: str) -> bool:
    try:
        parsed = urllib.parse.urlparse(url)
        host = parsed.netloc.lower()
        if host not in set(CONFIG["allowed_primary_source_hosts"]):
            return False
        if host == "zenn.dev" and not parsed.path.startswith("/zenn/articles/"):
            return False
        req = urllib.request.Request(url, headers={"User-Agent": "KAFKA2306-article-factory/1.0"})
        with urllib.request.urlopen(req, timeout=15) as response:
            response.read(512)
            return 200 <= int(response.status) < 400
    except Exception:
        return False


def source_gate(article: str) -> tuple[bool, dict[str, object]]:
    urls = sorted(set(URL_RE.findall(article)))
    valid = [url for url in urls if verify_url(url)]
    own = [url for url in valid if url.startswith("https://github.com/KAFKA2306/")]
    external = [url for url in valid if url not in own]
    gate = CONFIG["quality_gate"]
    ok = len(valid) >= gate["minimum_primary_sources"] and len(own) >= gate["minimum_own_github_evidence"] and len(external) >= 1
    return ok, {"all_urls": urls, "valid_urls": valid, "own_github": own, "external_primary": external}


def evaluate(article: str) -> dict[str, object]:
    user = f"""
LAPRAS AI Reviewの5軸に合わせてこの記事を厳格に評価してください。
0.0〜5.0。overallは5軸の算術平均。甘く採点しないでください。

{PROMPT}

ARTICLE:
{article}

JSONのみ返してください。
"""
    result = json.loads(model_call("あなたは独立した技術記事査読者です。", user, temperature=0.0, json_mode=True))
    axes = ["logic", "utility", "readability", "originality", "clarity"]
    values = [float(result.get(key, 0.0)) for key in axes]
    result["overall"] = round(sum(values) / len(values), 3)
    return result


def aggregate_evaluations(article: str, rounds: int = 3) -> dict[str, object]:
    reviews = [evaluate(article) for _ in range(rounds)]
    axes = ["logic", "utility", "readability", "originality", "clarity", "overall"]
    aggregate: dict[str, object] = {"reviews": reviews}
    for key in axes:
        values = sorted(float(review.get(key, 0.0)) for review in reviews)
        aggregate[key] = values[len(values) // 2]
    aggregate["blocking_issues"] = list(dict.fromkeys(
        issue for review in reviews for issue in review.get("blocking_issues", []) if isinstance(issue, str)
    ))
    aggregate["revision_actions"] = list(dict.fromkeys(
        action for review in reviews for action in review.get("revision_actions", []) if isinstance(action, str)
    ))
    return aggregate


def passes_quality(review: dict[str, object], sources_ok: bool) -> bool:
    gate = CONFIG["quality_gate"]
    axis_keys = ["logic", "utility", "readability", "originality", "clarity"]
    return bool(
        sources_ok
        and float(review["overall"]) >= gate["minimum_overall"]
        and all(float(review[key]) >= gate["minimum_axis"] for key in axis_keys)
    )


def revise(article: str, review: dict[str, object], source_report: dict[str, object]) -> str:
    user = f"""
以下の記事を全面改稿してください。情報量を水増しせず、弱点を直接修正してください。
Markdown本文のみ返してください。

品質契約:
{PROMPT}

査読結果:
{json.dumps(review, ensure_ascii=False, indent=2)}

一次情報検証:
{json.dumps(source_report, ensure_ascii=False, indent=2)}

ARTICLE:
{article}

特に、存在確認できないURL・断定・数値は削除し、GitHub一次証拠と再現手順を厚くしてください。
"""
    return model_call("あなたは査読指摘を潰すリビジョン担当です。", user, temperature=0.15)


def article_title(article: str) -> str:
    match = re.search(r"^#\s+(.+)$", article, flags=re.MULTILINE)
    return match.group(1).strip() if match else f"Monthly Engineering Note {NOW:%Y-%m}"


def slug_for(article: str) -> str:
    digest = hashlib.sha256(article.encode("utf-8")).hexdigest()[:8]
    return f"engineering-evidence-{NOW:%Y-%m}-{digest}"


def save_candidate(article: str, meta: dict[str, object]) -> Path:
    out = ROOT / "candidates"
    out.mkdir(parents=True, exist_ok=True)
    slug = slug_for(article)
    path = out / f"{NOW:%Y-%m-%d}-{slug}.md"
    header = f"<!-- factory_meta: {json.dumps(meta, ensure_ascii=False)} -->\n\n"
    path.write_text(header + article.rstrip() + "\n", encoding="utf-8")
    return path


def published_this_month() -> bool:
    base = ROOT / "articles"
    if not base.exists():
        return False
    needle = f"published_at: {NOW:%Y-%m}"
    return any(needle in path.read_text(encoding="utf-8", errors="ignore") for path in base.glob("*.md"))


def candidate_files_this_month() -> list[Path]:
    base = ROOT / "candidates"
    if not base.exists():
        return []
    return sorted(base.glob(f"{NOW:%Y-%m}-*.md"))


def choose_best_candidate(paths: list[Path]) -> str:
    if len(paths) == 1:
        return paths[0].read_text(encoding="utf-8")
    corpus = []
    for path in paths:
        text = path.read_text(encoding="utf-8")
        corpus.append({"path": path.name, "title": article_title(text), "excerpt": text[:3500]})
    result = json.loads(model_call(
        "あなたは月次の技術編集長です。独自性・実用性・一次証拠密度が最も高い1本を選びます。",
        "次の候補から最高品質の1本を選び、JSONで {\"path\":\"...\"} のみ返してください。\n" + json.dumps(corpus, ensure_ascii=False),
        temperature=0.0,
        json_mode=True,
    ))
    selected = str(result.get("path", ""))
    for path in paths:
        if path.name == selected:
            return path.read_text(encoding="utf-8")
    return paths[0].read_text(encoding="utf-8")


def publish(article: str, review: dict[str, object], source_report: dict[str, object]) -> Path:
    out = ROOT / "articles"
    out.mkdir(parents=True, exist_ok=True)
    slug = slug_for(article)
    title = article_title(article).replace('"', "'")
    body = re.sub(r"^#\s+.+?\n", "", article, count=1, flags=re.MULTILINE).lstrip()
    frontmatter = (
        "---\n"
        f'title: "{title}"\n'
        'emoji: "🧭"\n'
        'type: "tech"\n'
        'topics: ["python", "github", "architecture", "ai"]\n'
        "published: true\n"
        f"published_at: {NOW:%Y-%m-%d %H:%M}\n"
        "---\n\n"
    )
    path = out / f"{slug}.md"
    path.write_text(frontmatter + body.rstrip() + "\n", encoding="utf-8")
    reports = ROOT / "reports"
    reports.mkdir(parents=True, exist_ok=True)
    (reports / f"{NOW:%Y-%m}-{slug}.json").write_text(
        json.dumps({"review": review, "sources": source_report, "published_path": str(path.relative_to(ROOT))}, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return path


def generate_fresh() -> tuple[str, dict[str, object]]:
    signals = collect_public_github_signals(CONFIG["owner"])
    topics = choose_topic(signals)
    selected = topics.get("selected", topics)
    article = draft_article(selected if isinstance(selected, dict) else topics, signals)
    return article, {"topic_selection": topics, "signals": signals}


def main() -> int:
    if MODE == "candidate":
        article, meta = generate_fresh()
        sources_ok, source_report = source_gate(article)
        review = aggregate_evaluations(article, rounds=1)
        meta["initial_review"] = review
        meta["initial_sources"] = source_report
        path = save_candidate(article, meta)
        print(f"candidate={path.relative_to(ROOT)} sources_ok={sources_ok} score={review['overall']}")
        return 0

    if MODE != "publish":
        raise ValueError(f"Unknown ARTICLE_MODE={MODE}")
    if published_this_month():
        print("monthly article already published; no-op")
        return 0

    paths = candidate_files_this_month()
    if paths:
        article = choose_best_candidate(paths)
    else:
        article, _ = generate_fresh()

    last_review: dict[str, object] = {}
    last_sources: dict[str, object] = {}
    for attempt in range(CONFIG["revision_limit"] + 1):
        sources_ok, last_sources = source_gate(article)
        last_review = aggregate_evaluations(article, rounds=3)
        print(f"attempt={attempt} sources_ok={sources_ok} score={last_review['overall']}")
        if passes_quality(last_review, sources_ok):
            path = publish(article, last_review, last_sources)
            print(f"published={path.relative_to(ROOT)}")
            return 0
        if attempt < CONFIG["revision_limit"]:
            article = revise(article, last_review, last_sources)

    print(json.dumps({"error": "quality_gate_failed", "review": last_review, "sources": last_sources}, ensure_ascii=False, indent=2))
    return 2


if __name__ == "__main__":
    sys.exit(main())
