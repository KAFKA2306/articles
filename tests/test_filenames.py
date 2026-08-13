from __future__ import annotations

import tempfile
import unittest
from datetime import datetime
from pathlib import Path

from pipeline import core
from pipeline import filenames


class ArticleFilenameTests(unittest.TestCase):
    def test_filename_policy_is_explicit_and_non_destructive(self) -> None:
        policy = core.CONFIG["filename_policy"]
        self.assertEqual(policy["format"], "YYYY-MM-DD-NN-title")
        self.assertEqual(policy["sequence_width"], 2)
        self.assertEqual(policy["max_slug_length"], 50)
        self.assertEqual(policy["title_max_length"], 36)
        self.assertTrue(policy["new_articles_only"])
        self.assertFalse(policy["rename_existing_articles"])
        self.assertEqual(
            policy["zenn_slug_reference"],
            "https://zenn.dev/zenn/articles/what-is-slug",
        )

    def test_normalize_file_title_keeps_readable_ascii_kebab_case(self) -> None:
        self.assertEqual(
            filenames.normalize_file_title("Codex + ChatGPT GitHub Issue Bridge"),
            "codex-chatgpt-github-issue-bridge",
        )

    def test_next_slug_uses_date_and_daily_sequence(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            published = Path(tmp)
            (published / "2026-08-13-01-first-article.md").write_text("x", encoding="utf-8")
            (published / "legacy-article.md").write_text("x", encoding="utf-8")

            slug = filenames.next_publication_slug(
                "second-readable-article",
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

    def test_existing_legacy_filename_does_not_need_to_match_new_schema(self) -> None:
        self.assertFalse(filenames.is_managed_slug("codex-chatgpt-github-issue-bridge"))
        self.assertFalse(filenames.is_managed_slug("engineering-evidence-2026-08-deadbeef00"))


if __name__ == "__main__":
    unittest.main()
