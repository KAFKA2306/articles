from __future__ import annotations

import tempfile
import unittest
from datetime import datetime
from pathlib import Path
from unittest.mock import patch
from zoneinfo import ZoneInfo

from pipeline.portfolio_revalidate import report, source_urls


class PortfolioRevalidateTests(unittest.TestCase):
    def test_sources_ignore_code_and_html_comments(self) -> None:
        markdown = (
            "Evidence https://docs.python.org/3/\n"
            "<!-- https://example.org/hidden -->\n"
            "~~~text\n"
            "https://example.org/example\n"
            "~~~\n"
        )
        self.assertEqual(source_urls(markdown), {"https://docs.python.org/3/"})

    def test_only_published_articles_are_checked_and_broken_links_flagged(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            directory = Path(tmp) / "articles"
            directory.mkdir()
            (directory / "public.md").write_text(
                "---\ntitle: Test\npublished: true\npublished_at: 2026-11-01\n---\n"
                "https://docs.python.org/3/\n",
                encoding="utf-8",
            )
            (directory / "draft.md").write_text(
                "---\ntitle: Draft\npublished: false\n---\n"
                "https://docs.python.org/other\n",
                encoding="utf-8",
            )
            with patch("pipeline.portfolio_revalidate.probe", return_value="BROKEN") as check:
                summary, requires_action = report(
                    Path(tmp),
                    now=datetime(2026, 11, 12, tzinfo=ZoneInfo("Asia/Tokyo")),
                    workers=1,
                )
            self.assertTrue(requires_action)
            self.assertIn("public", summary)
            self.assertNotIn("draft", summary)
            check.assert_called_once_with("https://docs.python.org/3/")


if __name__ == "__main__":
    unittest.main()
