from __future__ import annotations

import hashlib
import json
import os
import re
import urllib.parse
import urllib.request
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PIPELINE_DIR = ROOT / "pipeline"
CONFIG = json.loads((PIPELINE_DIR / "config.json").read_text(encoding="utf-8"))
PROMPT = (PIPELINE_DIR / "contracts" / "article.md").read_text(encoding="utf-8")
JST = timezone(timedelta(hours=9))
MODEL_ENDPOINT = "https://models.github.ai/inference/chat/completions"
URL_RE = re.compile(r"https://[^\s)\]>\"']+")
PIPELINE_META_RE = re.compile(r"\A<!-- pipeline_meta: [^\n]*-->\s*", flags=re.MULTILINE)
AXIS_KEYS = ["logic", "utility", "readability", "originality", "clarity"]
EVALUATION_KIND = str(CONFIG.get("evaluation_kind", "internal_lapras_rubric_proxy"))


def now_jst() -> datetime:
    return datetime.now(JST)


def output_dir(key: str) -> Path:
    return ROOT / str(CONFIG["paths"][key])


def http_json(url: str, *, headers: dict[str, str] | None = None) -> object:
    request = urllib.request.Request(
        url,
        headers=headers or {"User-Agent": "KAFKA2306-articles/2.0"},
    )
    with urllib.request.urlopen(request, timeout=20) as response:
        return json.loads(response.read().decode("utf-8"))


def model_call(
    system: str,
    user: str,
    *,
    temperature: float = 0.2,
    json_mode: bool = False,
) -> str:
    token = os.environ.get("GITHUB_TOKEN", "")
    if not token:
        raise RuntimeError("GITHUB_TOKEN is required")
    model = os.environ.get("ARTICLE_MODEL", str(CONFIG["model"]))
    payload: dict[str, object] = {
        "model": model,
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
        "temperature": temperature,
    }
    if json_mode:
        payload["response_format"] = {"type": "json_object"}
    request = urllib.request.Request(
        MODEL_ENDPOINT,
        data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
        headers={
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "User-Agent": "KAFKA2306-articles/2.0",
        },
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=120) as response:
        data = json.loads(response.read().decode("utf-8"))
    return str(data["choices"][0]["message"]["content"]).strip()


def collect_public_github_signals(owner: str) -> list[dict[str, object]]:
    repos = http_json(
        f"https://api.github.com/users/{urllib.parse.quote(owner)}/repos"
        "?sort=pushed&direction=desc&per_page=12"
    )
    if not isinstance(repos, list):
        return []

    signals: list[dict[str, object]] = []
    for repo in repos[:8]:
        if not isinstance(repo, dict) or repo.get("fork") or repo.get("private"):
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
                f"https://api.github.com/repos/{urllib.parse.quote(owner)}/"
                f"{urllib.parse.quote(name)}/commits"
                f"?sha={urllib.parse.quote(default_branch)}&per_page=3"
            )
            if isinstance(commits, list):
                signal["recent_commits"] = [
                    {
                        "url": item.get("html_url"),
                        "message": (item.get("commit") or {}).get("message"),
                    }
                    for item in commits[:3]
                    if isinstance(item, dict)
                ]
        except Exception as exc:  # fail-soft for discovery only
            signal["commit_fetch_error"] = type(exc).__name__
        signals.append(signal)
    return signals


def strip_pipeline_meta(text: str) -> str:
    return PIPELINE_META_RE.sub("", text, count=1).lstrip()


def existing_titles() -> list[str]:
    titles: list[str] = []
    for base in (output_dir("published"), output_dir("candidates")):
        if not base.exists():
            continue
        for path in base.rglob("*.md"):
            text = strip_pipeline_meta(
                path.read_text(encoding="utf-8", errors="ignore")
            )
            heading = re.search(r"^#\s+(.+)$", text, flags=re.MULTILINE)
            frontmatter = re.search(
                r'^title:\s*["\']?(.+?)["\']?\s*$',
                text,
                flags=re.MULTILINE,
            )
            if heading:
                titles.append(heading.group(1).strip())
            elif frontmatter:
                titles.append(frontmatter.group(1).strip())
    return titles[-60:]


def choose_topic(signals: list[dict[str, object]]) -> dict[str, object]:
    user = f"""
直近の公開GitHubシグナルから技術記事候補を{CONFIG['candidate_count']}件作り、
最も強い1件を選んでください。
一般論より、実装証拠・設計判断・失敗・定量検証が揃う題材を優先します。
既存記事との焼き直しは禁止です。

既存タイトル:
{json.dumps(existing_titles(), ensure_ascii=False)}

GitHubシグナル:
{json.dumps(signals, ensure_ascii=False, indent=2)}

JSONのみ返してください。
{{"selected":{{"title":"...","audience":"...","problem":"...",
"evidence_urls":["..."],"why_unique":"..."}},"alternatives":[...]}}
"""
    return json.loads(
        model_call(
            "あなたは技術編集長です。公開一次証拠の弱いテーマは選びません。",
            user,
            json_mode=True,
        )
    )


def draft_article(
    topic: dict[str, object],
    signals: list[dict[str, object]],
) -> str:
    user = f"""
以下の契約に従って日本語の完成記事を書いてください。
Markdown本文のみ。front matterは不要です。

{PROMPT}

選定テーマ:
{json.dumps(topic, ensure_ascii=False, indent=2)}

利用可能な公開一次証拠:
{json.dumps(signals, ensure_ascii=False, indent=2)}

重要:
- GitHub上で確認できない実装事実を創作しない。
- 外部仕様を断定する場合は公式一次情報URLを本文の直後に付ける。
- URLを確信できない場合、その外部仕様自体を削除する。
- 最後に「一次情報・再現証拠」節を設け、本文で実際に使ったURLだけを列挙する。
- 最低でもKAFKA2306 GitHub URLを2件、外部の公式一次情報を1件含める。
"""
    return model_call(
        "あなたは一次証拠を最優先するシニア技術ライターです。",
        user,
        temperature=0.25,
    )


def verify_url(url: str) -> bool:
    try:
        parsed = urllib.parse.urlparse(url)
        host = parsed.netloc.lower()
        if host not in set(CONFIG["allowed_primary_source_hosts"]):
            return False
        if host == "zenn.dev" and not parsed.path.startswith("/zenn/articles/"):
            return False
        request = urllib.request.Request(
            url,
            headers={"User-Agent": "KAFKA2306-articles/2.0"},
        )
        with urllib.request.urlopen(request, timeout=15) as response:
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
    ok = (
        len(valid) >= int(gate["minimum_primary_sources"])
        and len(own) >= int(gate["minimum_own_github_evidence"])
        and len(external) >= 1
    )
    return ok, {
        "all_urls": urls,
        "valid_urls": valid,
        "own_github": own,
        "external_primary": external,
    }


def evaluate(article: str) -> dict[str, object]:
    user = f"""
LAPRAS AI Reviewで公開されている5軸を参考にした内部proxyとして、
この記事を厳格に評価してください。
これはLAPRAS上の実測AI Review値ではありません。
0.0〜5.0で採点し、overallは5軸の算術平均とします。甘く採点しないでください。

{PROMPT}

ARTICLE:
{article}

JSONのみ返してください。
"""
    result = json.loads(
        model_call(
            "あなたは独立した技術記事査読者です。",
            user,
            temperature=0.0,
            json_mode=True,
        )
    )
    values = [float(result.get(key, 0.0)) for key in AXIS_KEYS]
    result["overall"] = round(sum(values) / len(values), 3)
    result["evaluation_kind"] = EVALUATION_KIND
    return result


def aggregate_evaluations(
    article: str,
    *,
    rounds: int = 3,
) -> dict[str, object]:
    reviews = [evaluate(article) for _ in range(rounds)]
    aggregate: dict[str, object] = {
        "reviews": reviews,
        "evaluation_kind": EVALUATION_KIND,
    }
    for key in [*AXIS_KEYS, "overall"]:
        values = sorted(float(review.get(key, 0.0)) for review in reviews)
        aggregate[key] = values[len(values) // 2]
    aggregate["blocking_issues"] = list(
        dict.fromkeys(
            issue
            for review in reviews
            for issue in review.get("blocking_issues", [])
            if isinstance(issue, str)
        )
    )
    aggregate["revision_actions"] = list(
        dict.fromkeys(
            action
            for review in reviews
            for action in review.get("revision_actions", [])
            if isinstance(action, str)
        )
    )
    return aggregate


def passes_quality(review: dict[str, object], sources_ok: bool) -> bool:
    gate = CONFIG["quality_gate"]
    return bool(
        sources_ok
        and float(review["overall"]) >= float(gate["minimum_overall"])
        and all(
            float(review[key]) >= float(gate["minimum_axis"])
            for key in AXIS_KEYS
        )
    )


def review_rank_key(
    review: dict[str, object],
    source_report: dict[str, object],
) -> tuple[float, float, int, int]:
    minimum_axis = min(float(review[key]) for key in AXIS_KEYS)
    own_count = len(source_report.get("own_github", []))
    valid_count = len(source_report.get("valid_urls", []))
    return (float(review["overall"]), minimum_axis, own_count, valid_count)


def revise(
    article: str,
    review: dict[str, object],
    source_report: dict[str, object],
) -> str:
    user = f"""
以下の記事を全面改稿してください。情報量を水増しせず、弱点を直接修正してください。
Markdown本文のみ返してください。

品質契約:
{PROMPT}

内部proxy査読結果:
{json.dumps(review, ensure_ascii=False, indent=2)}

一次情報検証:
{json.dumps(source_report, ensure_ascii=False, indent=2)}

ARTICLE:
{article}

存在確認できないURL・断定・数値は削除し、
GitHub一次証拠と再現手順を厚くしてください。
"""
    return model_call(
        "あなたは査読指摘を潰すリビジョン担当です。",
        user,
        temperature=0.15,
    )


def improve_candidate(
    article: str,
    *,
    review_rounds: int = 1,
) -> tuple[str, dict[str, object], dict[str, object], bool, int]:
    best: tuple[str, dict[str, object], dict[str, object], bool] | None = None
    best_key: tuple[int, int, float, float, int, int] | None = None
    target = float(CONFIG["quality_gate"]["target_overall"])
    attempts_used = 0

    for attempt in range(int(CONFIG["revision_limit"]) + 1):
        sources_ok, source_report = source_gate(article)
        review = aggregate_evaluations(article, rounds=review_rounds)
        key = (
            int(passes_quality(review, sources_ok)),
            int(sources_ok),
            *review_rank_key(review, source_report),
        )
        if best_key is None or key > best_key:
            best = (article, review, source_report, sources_ok)
            best_key = key
        attempts_used = attempt

        if passes_quality(review, sources_ok) and float(review["overall"]) >= target:
            break
        if attempt < int(CONFIG["revision_limit"]):
            article = revise(article, review, source_report)

    assert best is not None
    return best[0], best[1], best[2], best[3], attempts_used


def article_title(article: str) -> str:
    match = re.search(r"^#\s+(.+)$", article, flags=re.MULTILINE)
    return match.group(1).strip() if match else f"Engineering Note {now_jst():%Y-%m}"


def slug_for(article: str) -> str:
    digest = hashlib.sha256(article.encode("utf-8")).hexdigest()[:10]
    return f"engineering-evidence-{now_jst():%Y-%m}-{digest}"


def sanitize_metadata(meta: dict[str, object]) -> dict[str, object]:
    forbidden = {
        "raw",
        "raw_text",
        "private_corpus",
        "content",
        "record_content",
        "diary_text",
    }
    clean: dict[str, object] = {}
    for key, value in meta.items():
        if key.lower() in forbidden:
            continue
        clean[key] = value
    return clean


def save_candidate(article: str, meta: dict[str, object]) -> Path:
    month = now_jst().strftime("%Y-%m")
    out = output_dir("candidates") / month
    out.mkdir(parents=True, exist_ok=True)
    slug = slug_for(article)
    path = out / f"{now_jst():%Y-%m-%d}-{slug}.md"
    header = (
        "<!-- pipeline_meta: "
        + json.dumps(sanitize_metadata(meta), ensure_ascii=False)
        + " -->\n\n"
    )
    path.write_text(header + article.rstrip() + "\n", encoding="utf-8")
    return path


def published_this_month() -> bool:
    base = output_dir("published")
    if not base.exists():
        return False
    needle = f"published_at: {now_jst():%Y-%m}"
    return any(
        needle in path.read_text(encoding="utf-8", errors="ignore")
        for path in base.glob("*.md")
    )


def candidate_files_this_month() -> list[Path]:
    base = output_dir("candidates") / now_jst().strftime("%Y-%m")
    if not base.exists():
        return []
    return sorted(base.glob("*.md"))


def is_month_end(moment: datetime) -> bool:
    return (moment + timedelta(days=1)).month != moment.month


def scheduled_publish_allowed() -> bool:
    return bool(
        os.environ.get("ARTICLE_ALLOW_EARLY_PUBLISH") == "1"
        or os.environ.get("GITHUB_EVENT_NAME") == "workflow_dispatch"
        or is_month_end(now_jst())
    )


def evaluate_monthly_candidates(paths: list[Path]) -> list[dict[str, object]]:
    evaluated: list[dict[str, object]] = []
    for path in paths:
        article = strip_pipeline_meta(path.read_text(encoding="utf-8"))
        sources_ok, source_report = source_gate(article)
        review = aggregate_evaluations(article, rounds=3)
        passes_gate = passes_quality(review, sources_ok)
        rank_key = review_rank_key(review, source_report)
        evaluated.append(
            {
                "path": path,
                "article": article,
                "title": article_title(article),
                "sources_ok": sources_ok,
                "source_report": source_report,
                "review": review,
                "passes_gate": passes_gate,
                "rank_key": rank_key,
            }
        )
        print(
            f"monthly_candidate={path.name} sources_ok={sources_ok} "
            f"passes_gate={passes_gate} proxy_score={review['overall']}"
        )
    return evaluated


def save_monthly_selection_report(
    evaluated: list[dict[str, object]],
    *,
    selected: dict[str, object] | None,
    status: str,
) -> Path:
    month = now_jst().strftime("%Y-%m")
    report_dir = output_dir("reports") / month
    report_dir.mkdir(parents=True, exist_ok=True)

    payload = {
        "month": month,
        "evaluation_kind": EVALUATION_KIND,
        "status": status,
        "publication_limit": int(CONFIG.get("monthly_publication_limit", 1)),
        "selected_candidate": selected["path"].name if selected else None,
        "candidates": [
            {
                "path": item["path"].name,
                "title": item["title"],
                "sources_ok": item["sources_ok"],
                "passes_gate": item["passes_gate"],
                "rank_key": list(item["rank_key"]),
                "review": item["review"],
                "sources": item["source_report"],
            }
            for item in evaluated
        ],
    }
    path = report_dir / "monthly-selection.json"
    path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return path


def publish(
    article: str,
    review: dict[str, object],
    source_report: dict[str, object],
) -> Path:
    article = strip_pipeline_meta(article)
    out = output_dir("published")
    out.mkdir(parents=True, exist_ok=True)
    slug = slug_for(article)
    title = article_title(article).replace('"', "'")
    body = re.sub(
        r"^#\s+.+?\n",
        "",
        article,
        count=1,
        flags=re.MULTILINE,
    ).lstrip()
    frontmatter = (
        "---\n"
        f'title: "{title}"\n'
        'emoji: "🧭"\n'
        'type: "tech"\n'
        'topics: ["python", "github", "architecture", "ai"]\n'
        "published: true\n"
        f"published_at: {now_jst():%Y-%m-%d %H:%M}\n"
        "---\n\n"
    )
    path = out / f"{slug}.md"
    path.write_text(frontmatter + body.rstrip() + "\n", encoding="utf-8")

    report_dir = output_dir("reports") / now_jst().strftime("%Y-%m")
    report_dir.mkdir(parents=True, exist_ok=True)
    report = {
        "evaluation_kind": EVALUATION_KIND,
        "review": review,
        "sources": source_report,
        "published_path": str(path.relative_to(ROOT)),
    }
    (report_dir / f"{slug}.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return path


def generate_public_candidate() -> Path:
    signals = collect_public_github_signals(str(CONFIG["owner"]))
    topics = choose_topic(signals)
    selected = topics.get("selected", topics)
    topic = selected if isinstance(selected, dict) else topics
    article = draft_article(topic, signals)
    article, review, source_report, sources_ok, revision_attempts = improve_candidate(
        article,
        review_rounds=1,
    )
    meta = {
        "idea_source": "public-github",
        "topic_selection": topics,
        "evaluation_kind": EVALUATION_KIND,
        "candidate_review": review,
        "candidate_sources": source_report,
        "sources_ok": sources_ok,
        "passes_gate": passes_quality(review, sources_ok),
        "revision_attempts": revision_attempts,
    }
    return save_candidate(article, meta)


def publish_best() -> Path | None:
    if not scheduled_publish_allowed():
        print(
            "publish=skipped reason=not_month_end "
            f"date={now_jst():%Y-%m-%d}"
        )
        return None

    if published_this_month():
        print("publish=skipped reason=monthly_publication_limit_reached")
        return None

    paths = candidate_files_this_month()
    if not paths:
        report = save_monthly_selection_report(
            [],
            selected=None,
            status="no_candidates",
        )
        print(
            "publish=skipped reason=no_candidates "
            f"report={report.relative_to(ROOT)}"
        )
        return None

    evaluated = evaluate_monthly_candidates(paths)
    eligible = [item for item in evaluated if bool(item["passes_gate"])]
    if not eligible:
        report = save_monthly_selection_report(
            evaluated,
            selected=None,
            status="no_candidate_passed_quality_gate",
        )
        print(
            "publish=skipped reason=no_candidate_passed_quality_gate "
            f"report={report.relative_to(ROOT)}"
        )
        return None

    eligible.sort(
        key=lambda item: (
            item["rank_key"],
            str(item["path"].name),
        ),
        reverse=True,
    )
    selected = eligible[0]
    report = save_monthly_selection_report(
        evaluated,
        selected=selected,
        status="selected",
    )

    article = str(selected["article"])
    review = dict(selected["review"])
    source_report = dict(selected["source_report"])
    sources_ok = bool(selected["sources_ok"])

    if not passes_quality(review, sources_ok):
        raise RuntimeError("selected candidate unexpectedly failed quality gate")

    path = publish(article, review, source_report)
    print(
        f"monthly_selection={report.relative_to(ROOT)} "
        f"selected={selected['path'].name} proxy_score={review['overall']}"
    )
    return path
