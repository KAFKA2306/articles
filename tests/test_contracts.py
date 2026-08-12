from __future__ import annotations

from datetime import datetime
import json
import unittest

from pipeline import core, editorial, selection
from pipeline.graphiti import compact_weekly_record


class PipelineContractTests(unittest.TestCase):
    def test_output_paths_are_separated(self) -> None:
        self.assertEqual(
            core.CONFIG["paths"]["candidates"],
            "artifacts/candidates",
        )
        self.assertEqual(
            core.CONFIG["paths"]["reports"],
            "artifacts/reports",
        )
        self.assertEqual(
            core.CONFIG["paths"]["published"],
            "articles",
        )

    def test_proxy_and_publication_contract(self) -> None:
        self.assertEqual(
            core.CONFIG["evaluation_kind"],
            "internal_lapras_rubric_proxy",
        )
        self.assertEqual(
            core.CONFIG["editorial_evaluation_kind"],
            "story_interest_proxy",
        )
        self.assertEqual(
            core.CONFIG["editorial_axes"],
            ["interest", "discovery", "narrative", "context"],
        )
        self.assertEqual(core.CONFIG["monthly_publication_limit"], 1)

    def test_popularity_benchmark_is_not_a_low_engagement_training_set(self) -> None:
        policy = core.CONFIG["benchmark_policy"]
        self.assertEqual(policy["positive_min_likes"], 100)
        self.assertTrue(policy["positive_requires_confirmed_like_count"])
        self.assertEqual(
            policy["below_threshold_role"],
            "non_positive_or_antipattern",
        )
        self.assertEqual(
            policy["lapras_role"],
            "quality_floor_not_objective",
        )
        self.assertTrue(policy["forbid_style_imitation"])

        benchmark_path = (
            core.ROOT / "pipeline" / "benchmarks" / "zenn-positive.json"
        )
        benchmark = json.loads(benchmark_path.read_text(encoding="utf-8"))
        self.assertEqual(benchmark["policy"]["positive_min_likes"], 100)
        self.assertFalse(
            benchmark["policy"]["below_threshold_articles_may_be_used_as_positive_examples"]
        )
        self.assertGreaterEqual(len(benchmark["positive_examples"]), 1)
        for example in benchmark["positive_examples"]:
            self.assertGreaterEqual(example["engagement_floor"], 100)
            self.assertTrue(example["engagement_evidence_url"].startswith("https://"))

    def test_premature_conclusion_is_a_blocking_editorial_pattern(self) -> None:
        self.assertTrue(
            editorial.opening_has_premature_conclusion(
                "具体例の前に書きます。この記事で伝えたい結論は一つです。"
            )
        )
        self.assertFalse(
            editorial.opening_has_premature_conclusion(
                "最初の集計は856行だった。取り直すと7,699行になった。どちらが間違っていたのか。"
            )
        )
        otherwise_passing = {
            "logic": 5.0,
            "utility": 5.0,
            "readability": 5.0,
            "originality": 5.0,
            "clarity": 5.0,
            "overall": 5.0,
            "interest": 5.0,
            "discovery": 5.0,
            "narrative": 5.0,
            "context": 5.0,
            "story_overall": 5.0,
            "blocking_issues": ["premature_conclusion_in_opening"],
        }
        self.assertFalse(
            editorial.passes_quality(otherwise_passing, sources_ok=True)
        )

    def test_story_gate_is_stricter_than_technical_gate(self) -> None:
        review = {
            "logic": 5.0,
            "utility": 5.0,
            "readability": 5.0,
            "originality": 5.0,
            "clarity": 5.0,
            "overall": 5.0,
            "interest": 3.0,
            "discovery": 5.0,
            "narrative": 5.0,
            "context": 5.0,
            "story_overall": 4.5,
        }
        self.assertFalse(editorial.passes_quality(review, sources_ok=True))

    def test_story_ready_requires_one_complete_discovery(self) -> None:
        topic = {
            "central_question": "なぜ件数を増やすほど確定できない値が増えるのか？",
            "surprising_finding": "公開行数が増えても正確な損益計算には直結しない",
            "initial_hypothesis": "取引行を集めれば損益まで復元できる",
            "hypothesis_update": "金額がカテゴリ表示であることを確認して予想を更新する",
            "stakes": "公開データから何を計算できるかの境界が変わる",
            "story_type": "counterintuitive-result",
            "evidence_urls": [
                "https://github.com/KAFKA2306/investor2/a",
                "https://github.com/KAFKA2306/investor2/b",
            ],
            "why_interesting": "データ量と推定可能性が同じ方向に動かない",
        }
        self.assertTrue(editorial.story_ready(topic))
        topic.pop("hypothesis_update")
        self.assertFalse(editorial.story_ready(topic))

    def test_monthly_rank_prefers_story_quality(self) -> None:
        sources = {
            "own_github": ["a", "b"],
            "valid_urls": ["a", "b", "c"],
        }
        technically_higher = {
            "logic": 5.0,
            "utility": 5.0,
            "readability": 5.0,
            "originality": 5.0,
            "clarity": 5.0,
            "overall": 5.0,
            "interest": 4.1,
            "discovery": 4.1,
            "narrative": 4.1,
            "context": 4.1,
            "story_overall": 4.1,
        }
        more_compelling = {
            "logic": 4.2,
            "utility": 4.2,
            "readability": 4.2,
            "originality": 4.2,
            "clarity": 4.2,
            "overall": 4.2,
            "interest": 4.8,
            "discovery": 4.8,
            "narrative": 4.8,
            "context": 4.8,
            "story_overall": 4.8,
        }
        self.assertGreater(
            selection.review_rank_key(more_compelling, sources),
            selection.review_rank_key(technically_higher, sources),
        )

    def test_current_model_backend_contract(self) -> None:
        self.assertEqual(core.CONFIG["model_provider"], "github-copilot-cli")
        source = (core.ROOT / "pipeline" / "core.py").read_text(encoding="utf-8")
        self.assertNotIn("models.github.ai", source)
        self.assertEqual(
            core._strip_code_fence('```json\n{"ok": true}\n```'),
            '{"ok": true}',
        )

    def test_metadata_sanitizer_drops_raw_private_fields(self) -> None:
        result = core.sanitize_metadata(
            {
                "topic": {"title": "public"},
                "private_corpus": "secret",
                "content": "secret",
            }
        )
        self.assertEqual(result, {"topic": {"title": "public"}})

    def test_pipeline_meta_is_removed_before_monthly_review(self) -> None:
        sample = (
            '<!-- pipeline_meta: {"private": false} -->\n\n'
            "# Public article\n"
        )
        self.assertEqual(
            selection.strip_pipeline_meta(sample),
            "# Public article\n",
        )

    def test_legacy_factory_meta_is_also_removed(self) -> None:
        sample = (
            '<!-- factory_meta: {"bootstrap": true} -->\n\n'
            "# Public article\n"
        )
        self.assertEqual(core.strip_internal_meta(sample), "# Public article\n")
        self.assertEqual(selection.strip_pipeline_meta(sample), "# Public article\n")

    def test_true_calendar_month_end(self) -> None:
        self.assertTrue(selection.is_month_end(datetime(2026, 2, 28)))
        self.assertTrue(selection.is_month_end(datetime(2028, 2, 29)))
        self.assertTrue(selection.is_month_end(datetime(2026, 8, 31)))
        self.assertFalse(selection.is_month_end(datetime(2026, 8, 30)))

    def test_weekly_compaction_prefers_human_sections(self) -> None:
        text = """# Weekly Diary

## summary

長い概要。

## decisions

- fail-closeを維持する
- private dataを公開しない

## timeline

- 実装A
- 実装B
"""
        compact = compact_weekly_record("2026-W33.md", text)
        self.assertEqual(compact["summary"], "長い概要。")
        self.assertEqual(
            compact["decisions"],
            ["- fail-closeを維持する", "- private dataを公開しない"],
        )
        self.assertEqual(
            compact["timeline_sample"],
            ["- 実装A", "- 実装B"],
        )


if __name__ == "__main__":
    unittest.main()
