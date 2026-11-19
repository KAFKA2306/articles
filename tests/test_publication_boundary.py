from __future__ import annotations

import os
import tempfile
import unittest
from datetime import datetime
from pathlib import Path
from unittest.mock import patch

from pipeline import core, selection
from pipeline.publication_diff import PublicationState, parse_state


class PublicationBoundaryTests(unittest.TestCase):
    def test_draft_selection_requires_explicit_manual_authority(self) -> None:
        with patch.dict(os.environ, {}, clear=True):
            self.assertFalse(selection.scheduled_publish_allowed())
        with patch.dict(os.environ, {"ARTICLE_MANUAL": "0"}, clear=True):
            self.assertFalse(selection.scheduled_publish_allowed())
        with patch.dict(os.environ, {"ARTICLE_MANUAL": "1"}, clear=True):
            self.assertTrue(selection.scheduled_publish_allowed())

    def test_calendar_month_end_is_not_publication_authority(self) -> None:
        month_end = datetime(2028, 2, 29, tzinfo=core.JST)
        with (
            patch.dict(os.environ, {}, clear=True),
            patch.object(core, "now_jst", return_value=month_end),
            patch.object(core, "published_this_month") as check_publication_limit,
        ):
            self.assertIsNone(selection.publish_best())
        check_publication_limit.assert_not_called()

    def test_core_materializes_only_unpublished_articles(self) -> None:
        moment = datetime(2026, 8, 15, 10, tzinfo=core.JST)
        article = '<!-- factory_meta: {"title": "internal"} -->\n\n# Reader title\n\nReader text.\n'
        with (
            tempfile.TemporaryDirectory() as directory,
            patch.object(core, "now_jst", return_value=moment),
        ):
            with patch.object(core, "ROOT", Path(directory)):
                draft = core.publish(article, {}, {}, slug="reader-article-123")
                content = draft.read_text(encoding="utf-8")
        self.assertEqual(PublicationState(False, "2026-08-15 10:00"), parse_state(content))
        self.assertIn('title: "Reader title"', content)
        self.assertTrue(content.endswith("Reader text.\n"))
        self.assertNotIn("factory_meta", content)

    def test_non_release_article_commits_skip_zenn_deploy(self) -> None:
        workflow = (
            core.ROOT / ".github" / "workflows" / "article-pipeline.yml"
        ).read_text(encoding="utf-8")
        self.assertIn("[skip ci]", workflow)
        self.assertIn("without Zenn deploy", workflow)


if __name__ == "__main__":
    unittest.main()
