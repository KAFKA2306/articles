from __future__ import annotations

import unittest

from pipeline import core, editorial, selection
from pipeline.graphiti import compact_weekly_record


class PipelineContractTests(unittest.TestCase):

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

    def test_metadata_sanitizer_drops_raw_private_fields(self) -> None:
        result = core.sanitize_metadata(
            {
                "topic": {"title": "public"},
                "private_corpus": "secret",
                "content": "secret",
            }
        )
        self.assertEqual(result, {"topic": {"title": "public"}})

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
