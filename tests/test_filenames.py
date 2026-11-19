from __future__ import annotations

import tempfile
import unittest
from datetime import datetime
from pathlib import Path

from pipeline import filenames


class ArticleFilenameTests(unittest.TestCase):

    def test_next_slug_uses_date_and_daily_sequence(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            published = Path(tmp)
            (published / "2026-08-13-01-first-article.md").write_text("x", encoding="utf-8")
            (published / "legacy-article.md").write_text("x", encoding="utf-8")

            slug = filenames.next_publication_slug(
                "Second readable article",
                moment=datetime(2026, 8, 13, 16, 30),
                published_dir=published,
            )

        self.assertEqual(slug, "2026-08-13-02-second-readable-article")
        self.assertTrue(filenames.is_managed_slug(slug))

    def test_slug_respects_zenn_fifty_character_limit(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            slug = filenames.next_publication_slug(
                "this-is-a-deliberately-very-long-readable-article-title-for-testing",
                moment=datetime(2026, 8, 13, 16, 30),
                published_dir=Path(tmp),
            )

        self.assertLessEqual(len(slug), 50)
        self.assertTrue(slug.startswith("2026-08-13-01-"))
        self.assertTrue(filenames.is_managed_slug(slug))


if __name__ == "__main__":
    unittest.main()
