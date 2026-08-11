from __future__ import annotations

import json
import os
from datetime import datetime, timedelta
from pathlib import Path

from . import core

EVALUATION_KIND = str(
    core.CONFIG.get("evaluation_kind", "internal_lapras_rubric_proxy")
)
AXIS_KEYS = ["logic", "utility", "readability", "originality", "clarity"]
def strip_pipeline_meta(text: str) -> str:
    return core.strip_internal_meta(text)


def review_rank_key(
    review: dict[str, object],
    source_report: dict[str, object],
) -> tuple[float, float, int, int]:
    minimum_axis = min(float(review[key]) for key in AXIS_KEYS)
    own_count = len(source_report.get("own_github", []))
    valid_count = len(source_report.get("valid_urls", []))
    return (
        float(review["overall"]),
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
    best_key: tuple[int, int, float, float, int, int] | None = None
    target = float(core.CONFIG["quality_gate"]["target_overall"])
    attempts_used = 0

    for attempt in range(int(core.CONFIG["revision_limit"]) + 1):
        sources_ok, source_report = core.source_gate(article)
        review = core.aggregate_evaluations(article, rounds=review_rounds)
        review["evaluation_kind"] = EVALUATION_KIND
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
            "topic_selection": topics,
            "candidate_review": review,
            "candidate_sources": sources,
            "sources_ok": sources_ok,
            "revision_attempts": attempts,
        },
    )


def is_month_end(moment: datetime) -> bool:
    return (moment + timedelta(days=1)).month != moment.month


def scheduled_publish_allowed() -> bool:
    return (
        os.environ.get("ARTICLE_MANUAL") == "1"
        or is_month_end(core.now_jst())
    )


def evaluate_monthly_candidates(paths: list[Path]) -> list[dict[str, object]]:
    evaluated: list[dict[str, object]] = []
    for path in paths:
        article = strip_pipeline_meta(path.read_text(encoding="utf-8"))
        sources_ok, source_report = core.source_gate(article)
        review = core.aggregate_evaluations(article, rounds=3)
        review["evaluation_kind"] = EVALUATION_KIND
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
            f"proxy_score={review['overall']}"
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


def publish_best() -> Path | None:
    if not scheduled_publish_allowed():
        print(
            "publish=skipped reason=not_month_end "
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
        status="selected",
    )
    return core.publish(
        str(selected["article"]),
        dict(selected["review"]),
        dict(selected["source_report"]),
    )
