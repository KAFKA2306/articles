from __future__ import annotations

import os
import unittest
from unittest.mock import patch

from pipeline import core, selection


class PublicationBoundaryTests(unittest.TestCase):
    def test_draft_selection_requires_explicit_manual_authority(self) -> None:
        with patch.dict(os.environ, {}, clear=True):
            self.assertFalse(selection.scheduled_publish_allowed())
        with patch.dict(os.environ, {"ARTICLE_MANUAL": "0"}, clear=True):
            self.assertFalse(selection.scheduled_publish_allowed())
        with patch.dict(os.environ, {"ARTICLE_MANUAL": "1"}, clear=True):
            self.assertTrue(selection.scheduled_publish_allowed())

    def test_calendar_month_end_is_not_publication_authority(self) -> None:
        with patch.dict(os.environ, {}, clear=True):
            self.assertFalse(selection.scheduled_publish_allowed())

    def test_core_materializes_only_unpublished_articles(self) -> None:
        source = (core.ROOT / "pipeline" / "core.py").read_text(encoding="utf-8")
        self.assertIn('"published: false\\n"', source)

    def test_workflow_has_no_scheduled_publication_path(self) -> None:
        workflow = (
            core.ROOT / ".github" / "workflows" / "article-pipeline.yml"
        ).read_text(encoding="utf-8")
        self.assertIn('cron: "0 0 * * 1"', workflow)
        self.assertNotIn('cron: "30 14 28-31 * *"', workflow)
        self.assertIn("select-draft", workflow)
        self.assertIn("Assert automation never grants publication", workflow)
        self.assertNotIn("bootstrap_publish=attempt", workflow)

    def test_contract_makes_human_publication_explicit(self) -> None:
        contract = (
            core.ROOT / "pipeline" / "contracts" / "article.md"
        ).read_text(encoding="utf-8")
        self.assertIn("explicit human approval", contract)
        self.assertIn("published:true", contract)
        self.assertIn("decision rule", contract.lower())


if __name__ == "__main__":
    unittest.main()
