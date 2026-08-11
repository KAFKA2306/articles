from __future__ import annotations

from datetime import datetime
import unittest

from pipeline import core, selection
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
        self.assertEqual(core.CONFIG["monthly_publication_limit"], 1)

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
