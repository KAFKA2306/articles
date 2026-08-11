from __future__ import annotations

import tempfile
import unittest
from datetime import datetime
from pathlib import Path
from unittest.mock import patch

from pipeline import core
from pipeline.cli import normalize_legacy_candidate_metadata
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

    def test_quality_contract_is_fail_closed(self) -> None:
        self.assertEqual(
            core.CONFIG["evaluation_kind"],
            "internal_lapras_rubric_proxy",
        )
        self.assertEqual(core.CONFIG["monthly_publication_limit"], 1)
        gate = core.CONFIG["quality_gate"]
        self.assertGreaterEqual(float(gate["target_overall"]), 4.0)
        self.assertGreaterEqual(float(gate["minimum_overall"]), 3.5)
        self.assertGreaterEqual(float(gate["minimum_axis"]), 3.5)

    def test_metadata_sanitizer_drops_raw_private_fields(self) -> None:
        result = core.sanitize_metadata(
            {
                "topic": {"title": "public"},
                "private_corpus": "secret",
                "content": "secret",
            }
        )
        self.assertEqual(result, {"topic": {"title": "public"}})

    def test_pipeline_metadata_is_not_part_of_article(self) -> None:
        sample = (
            '<!-- pipeline_meta: {"private": false, '
            '"evidence_urls": ["https://github.com/KAFKA2306/x"]} -->\n\n'
            "# Public article\n"
        )
        self.assertEqual(
            core.strip_pipeline_meta(sample),
            "# Public article\n",
        )

    def test_legacy_factory_metadata_is_normalized_before_pipeline_action(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            candidate = Path(tmp) / "candidate.md"
            candidate.write_text(
                '<!-- factory_meta: {"idea_only": true} -->\n\n# Public article\n',
                encoding="utf-8",
            )
            with patch.object(
                core,
                "candidate_files_this_month",
                return_value=[candidate],
            ):
                self.assertEqual(normalize_legacy_candidate_metadata(), 1)
            migrated = candidate.read_text(encoding="utf-8")
            self.assertTrue(migrated.startswith("<!-- pipeline_meta: "))
            self.assertEqual(core.strip_pipeline_meta(migrated), "# Public article\n")

    def test_month_end_detection_handles_leap_years(self) -> None:
        self.assertTrue(
            core.is_month_end(
                datetime(2026, 2, 28, tzinfo=core.JST)
            )
        )
        self.assertTrue(
            core.is_month_end(
                datetime(2028, 2, 29, tzinfo=core.JST)
            )
        )
        self.assertFalse(
            core.is_month_end(
                datetime(2026, 8, 30, tzinfo=core.JST)
            )
        )
        self.assertTrue(
            core.is_month_end(
                datetime(2026, 8, 31, tzinfo=core.JST)
            )
        )

    def test_rank_key_prefers_minimum_axis_then_evidence_after_overall(self) -> None:
        review = {
            "logic": 4.1,
            "utility": 4.0,
            "readability": 3.8,
            "originality": 4.2,
            "clarity": 4.0,
            "overall": 4.02,
        }
        report = {
            "own_github": ["a", "b"],
            "valid_urls": ["a", "b", "c"],
        }
        self.assertEqual(
            core.review_rank_key(review, report),
            (4.02, 3.8, 2, 3),
        )

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
        self.assertEqual(compact["timeline_sample"], ["- 実装A", "- 実装B"])


if __name__ == "__main__":
    unittest.main()
