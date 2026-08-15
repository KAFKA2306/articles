from __future__ import annotations

import hashlib
import json
import os
from datetime import datetime, timedelta
from pathlib import Path

from . import core, filenames
from .editorial import EDITORIAL_AXES, TECHNICAL_AXES

EVALUATION_KIND = str(
    core.CONFIG.get("evaluation_kind", "internal_lapras_rubric_proxy")
)
EDITORIAL_EVALUATION_KIND = str(
    core.CONFIG.get("editorial_evaluation_kind", "story_interest_proxy")
)
AXIS_KEYS = list(TECHNICAL_AXES)
STORY_KEYS = list(EDITORIAL_AXES)


def strip_pipeline_meta(text: str) -> str:
    return core.strip_internal_meta(text)


def review_rank_key(
    review: dict[str, object],
    source_report: dict[str, object],
) -> tuple[float, float, float, float, float, float, int, int]:
    minimum_axis = min(float(review[key]) for key in AXIS_KEYS)
    minimum_story_axis = min(float(review[key]) for key in STORY_KEYS)
    own_count = len(source_report.get("own_github", []))
    valid_count = len(source_report.get("valid_urls", []))
    return (
        float(review["story_overall"]),
        float(review["interest"]),
        float(review["discovery"]),
        float(review["overall"]),
        minimum_story_axis,
        minimum_axis,
        own_count,
        valid_count,
    )


def improve_candidate(
    article: str,
    *,
    review_rounds: int = 1,
) -> tuple[str, dict[str, object], dict[str, object], bool, int]:
    best: tuple[str, dict[str, object], dict[str, object], bool] | None = None
    best_key: tuple[int, int, float, float, float, float, float, float, int, int] | None = None
    target = float(core.CONFIG["quality_gate"]["target_overall"])
    story_target = float(core.CONFIG["quality_gate"]["target_story_overall"])
    attempts_used = 0

    for attempt in range(int(core.CONFIG["revision_limit"]) + 1):
        sources_ok, source_report = core.source_gate(article)
        review = core.aggregate_evaluations(article, rounds=review_rounds)
        review["evaluation_kind"] = EVALUATION_KIND
        review["editorial_evaluation_kind"] = EDITORIAL_EVALUATION_KIND
        key = (
            int(core.passes_quality(review, sources_ok)),
            int(sources_ok),
            *review_rank_key(review, source_report),
        )
        if best_key is None or key > best_key:
            best = (article, review, source_report, sources_ok)
            best_key = key
        attempts_used = attempt
        if (
            core.passes_quality(review, sources_ok)
            and float(review["overall"]) >= target
            and float(review["story_overall"]) >= story_target
        ):
            break
        if attempt < int(core.CONFIG["revision_limit"]):
            article = core.revise(article, review, source_report)

    assert best is not None
    return best[0], best[1], best[2], best[3], attempts_used


def generate_public_candidate() -> Path:
    signals = core.collect_public_github_signals(str(core.CONFIG["owner"]))
    topics = core.choose_topic(signals)
    selected = topics.get("selected", topics)
    topic = selected if isinstance(selected, dict) else topics
    article = core.draft_article(topic, signals)
    article, review, sources, sources_ok, attempts = improve_candidate(
        article,
        review_rounds=1,
    )
    return core.save_candidate(
        article,
        {
            "idea_source": "public-github",
            "evaluation_kind": EVALUATION_KIND,
            "editorial_evaluation_kind": EDITORIAL_EVALUATION_KIND,
            "topic_selection": topics,
            "candidate_review": review,
            "candidate_sources": sources,
            "sources_ok": sources_ok,
            "revision_attempts": attempts,
        },
    )


def is_month_end(moment: datetime) -> bool:
    """Calendar helper retained for historical reports/tests, not publication authority."""
    return (moment + timedelta(days=1)).month != moment.month


def scheduled_publish_allowed() -> bool:
    """Only an explicit human-triggered pipeline run may select a Zenn draft."""
    return os.environ.get("ARTICLE_MANUAL") == "1"


def evaluate_monthly_candidates(paths: list[Path]) -> list[dict[str, object]]:
    evaluated: list[dict[str, object]] = []
    for path in paths:
        article = strip_pipeline_meta(path.read_text(encoding="utf-8"))
        sources_ok, source_report = core.source_gate(article)
        review = core.aggregate_evaluations(article, rounds=3)
        review["evaluation_kind"] = EVALUATION_KIND
        review["editorial_evaluation_kind"] = EDITORIAL_EVALUATION_KIND
        passes_gate = core.passes_quality(review, sources_ok)
        rank_key = review_rank_key(review, source_report)
        evaluated.append(
            {
                "path": path,
                "article": article,
                "title": core.article_title(article),
                "sources_ok": sources_ok,
                "source_report": source_report,
                "review": review,
                "passes_gate": passes_gate,
                "rank_key": rank_key,
            }
        )
        print(
            f"monthly_candidate={path.name} "
            f"sources_ok={sources_ok} passes_gate={passes_gate} "
            f"technical_score={review['overall']} "
            f"story_score={review['story_overall']} "
            f"interest={review['interest']}"
        )
    return evaluated


def save_monthly_selection_report(
    evaluated: list[dict[str, object]],
    *,
    selected: dict[str, object] | None,
    status: str,
) -> Path:
    month = core.now_jst().strftime("%Y-%m")
    reports = core.output_dir("reports") / month
    reports.mkdir(parents=True, exist_ok=True)
    payload = {
        "month": month,
        "evaluation_kind": EVALUATION_KIND,
        "editorial_evaluation_kind": EDITORIAL_EVALUATION_KIND,
        "status": status,
        "publication_limit": int(
            core.CONFIG.get("monthly_publication_limit", 1)
        ),
        "selected_candidate": (
            selected["path"].name if selected else None
        ),
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
    path = reports / "monthly-selection.json"
    path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return path


def publication_file_title(article: str) -> str:
    """Create the readable ASCII title segment used only for file management."""
    title = core.article_title(article)
    policy = core.CONFIG["filename_policy"]
    max_length = int(policy["title_max_length"])
    prompt = f"""
次の記事タイトルを、ファイル管理用の短い英語kebab-caseへ変換してください。
表示タイトルの翻訳ではなく、内容を識別できる3〜6語程度のASCII識別子です。
半角英小文字 a-z、数字 0-9、ハイフンだけを使い、{max_length}文字以内にしてください。

記事タイトル:
{title}

JSONのみ返してください。
{{"file_title":"example-readable-title"}}
"""
    try:
        result = json.loads(
            core.model_call(
                "あなたは技術記事のファイル命名担当です。意味を保ち、短く安定した識別子だけを作ります。",
                prompt,
                json_mode=True,
            )
        )
        return filenames.normalize_file_title(
            str(result.get("file_title", "")),
            max_length=max_length,
        )
    except Exception:
        try:
            return filenames.normalize_file_title(title, max_length=max_length)
        except ValueError:
            digest = hashlib.sha256(article.encode("utf-8")).hexdigest()[:10]
            return f"article-{digest}"


def publication_slug(article: str) -> str:
    """Resolve and validate the final Zenn slug before any article file exists."""
    policy = core.CONFIG["filename_policy"]
    return filenames.next_publication_slug(
        publication_file_title(article),
        moment=core.now_jst(),
        published_dir=core.output_dir("published"),
        sequence_width=int(policy["sequence_width"]),
        max_slug_length=int(policy["max_slug_length"]),
    )


def publish_best() -> Path | None:
    """Select the strongest current candidate into articles/ as published:false.

    Despite the historical function name, this function is not authorized to
    publish publicly on Zenn. Explicit ARTICLE_MANUAL=1 is required even for
    draft selection/materialization.
    """
    if not scheduled_publish_allowed():
        print(
            "publish=skipped reason=explicit_human_selection_required "
            f"date={core.now_jst():%Y-%m-%d}"
        )
        return None

    if core.published_this_month():
        print("publish=skipped reason=monthly_publication_limit_reached")
        return None

    paths = core.candidate_files_this_month()
    if not paths:
        report = save_monthly_selection_report(
            [],
            selected=None,
            status="no_candidates",
        )
        print(
            "publish=skipped reason=no_candidates "
            f"report={report.relative_to(core.ROOT)}"
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
            f"report={report.relative_to(core.ROOT)}"
        )
        return None

    eligible.sort(
        key=lambda item: (item["rank_key"], str(item["path"].name)),
        reverse=True,
    )
    selected = eligible[0]
    save_monthly_selection_report(
        evaluated,
        selected=selected,
        status="selected_unpublished_draft",
    )
    article = str(selected["article"])
    slug = publication_slug(article)
    return core.publish(
        article,
        dict(selected["review"]),
        dict(selected["source_report"]),
        slug=slug,
    )
