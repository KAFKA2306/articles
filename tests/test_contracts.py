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

    def test_broad_entry_title_policy_is_canonical(self) -> None:
        policy = core.CONFIG["title_policy"]
        self.assertEqual(policy["minimum_candidates"], 3)
        self.assertEqual(
            policy["candidate_roles"],
            ["general_problem", "concrete_anomaly", "searchable"],
        )
        self.assertTrue(policy["prefer_plain_language_entry"])
        self.assertTrue(policy["technical_terms_after_problem"])
        self.assertTrue(policy["require_selected_from_candidates"])
        self.assertEqual(
            policy["blocking_issue"],
            "narrow_technical_title_entry",
        )

    def test_reader_value_policy_is_canonical(self) -> None:
        policy = core.CONFIG["reader_value_policy"]
        self.assertEqual(
            policy["required_fields"],
            [
                "reader_before",
                "reader_after",
                "design_philosophy",
                "why_this_article",
                "proof_of_value",
                "desired_reader_action",
                "non_goal",
            ],
        )
        self.assertTrue(policy["require_actionable_reader_after"])
        self.assertTrue(policy["forbid_generic_why"])
        self.assertEqual(
            set(policy["blocking_issues"]),
            {
                "weak_reader_value",
                "weak_differentiation",
                "missing_proof_of_value",
                "forced_commercial_cta",
                "technical_value_as_product",
            },
        )

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

    def test_narrow_technical_title_is_a_blocking_editorial_pattern(self) -> None:
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
            "blocking_issues": ["narrow_technical_title_entry"],
        }
        self.assertFalse(
            editorial.passes_quality(otherwise_passing, sources_ok=True)
        )

    def test_reader_value_blockers_are_publication_blockers(self) -> None:
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
        }
        for issue in core.CONFIG["reader_value_policy"]["blocking_issues"]:
            review = dict(otherwise_passing)
            review["blocking_issues"] = [issue]
            with self.subTest(issue=issue):
                self.assertFalse(
                    editorial.passes_quality(review, sources_ok=True)
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

    def test_title_options_require_three_distinct_roles_and_selected_title(self) -> None:
        topic = {
            "title": "バラバラな記録を、あとで使えるデータにするには？",
            "title_options": {
                "general_problem": "バラバラな記録を、あとで使えるデータにするには？",
                "concrete_anomaly": "同じ本が4件に増えた。人間には同じでも機械には別物だった",
                "searchable": "バラバラな記録を使えるデータにする：dry-runで書き込み前に判定する",
            },
        }
        self.assertTrue(editorial.title_options_ready(topic))

        topic["title_options"]["searchable"] = topic["title_options"]["general_problem"]
        self.assertFalse(editorial.title_options_ready(topic))

        topic["title_options"]["searchable"] = "記録を構造化する：dry-runとentity resolution"
        topic["title"] = "3案にないタイトル"
        self.assertFalse(editorial.title_options_ready(topic))

    def test_reader_value_contract_requires_action_proof_and_specific_why(self) -> None:
        topic = {
            "reader_before": "CSVを書き込むまで既存データと衝突する行が分からない",
            "reader_after": "書き込み前に各行の予定actionを確認し、人間確認が必要な行だけ止められる",
            "design_philosophy": "一括適用の速さより非破壊性を優先し、diagnoseとwriteを分離する",
            "why_this_article": "booksの実migrationでCLIとbrowserが同じ診断coreへ収束した判断変更を追う",
            "proof_of_value": "公開commitのfixtureでexisting_holding / review / invalidを判定し、catalog非変更をtestしている",
            "desired_reader_action": "既存importerへno-writeのdiagnose stepを追加する",
            "non_goal": "実書き込み時のtransaction競合までは解決しない",
        }
        self.assertTrue(editorial.value_contract_ready(topic))

        weak_after = dict(topic)
        weak_after["reader_after"] = "dry-runについて理解する"
        self.assertFalse(editorial.value_contract_ready(weak_after))

        generic_why = dict(topic)
        generic_why["why_this_article"] = "分かりやすく解説する"
        self.assertFalse(editorial.value_contract_ready(generic_why))

        missing_proof = dict(topic)
        missing_proof["proof_of_value"] = ""
        self.assertFalse(editorial.value_contract_ready(missing_proof))

    def test_story_ready_requires_one_complete_discovery_and_reader_value(self) -> None:
        topic = {
            "title": "856件が7,699件になった。でも計算ミスではなかった",
            "title_options": {
                "general_problem": "同じデータを数え直したら件数が9倍になった。何を数えたか残していた？",
                "concrete_anomaly": "856件が7,699件になった。でも計算ミスではなかった",
                "searchable": "856件が7,699件になった：集計scopeとprovenanceを保存する",
            },
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
            "reader_before": "同じKPIが更新されると前の値が誤りだったのかscope差なのか分からない",
            "reader_after": "source / scope / methodを比較し、数字が変わった理由を説明できる",
            "design_philosophy": "単一のverified flagより変更理由の追跡可能性を優先し、一次資料と派生集計を分離する",
            "why_this_article": "856→7,699という実数の反転を、17文書の公開evidenceで復元したcaseを扱う",
            "proof_of_value": "17文書と5,026 purchases + 2,673 salesの公開snapshotがある",
            "desired_reader_action": "重要KPIへsource / scope / methodを追加する",
            "non_goal": "7,699をOGE公式合計とは扱わない",
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
