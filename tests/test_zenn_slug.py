from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from pipeline.zenn_slug import (
    InvalidZennSlug,
    create_article_file,
    validate_article_paths,
    validate_slug,
)


class ZennSlugTests(unittest.TestCase):
    def test_minimum_length_is_12(self) -> None:
        self.assertEqual([], validate_slug("a" * 12))
        self.assertTrue(validate_slug("a" * 11))

    def test_allowed_characters(self) -> None:
        self.assertEqual([], validate_slug("valid-slug_123"))
        for slug in ("Invalid-Slug-123", "invalid.slug.123", "invalid slug 123"):
            with self.subTest(slug=slug):
                self.assertTrue(validate_slug(slug))

    def test_nested_article_path_is_rejected(self) -> None:
        errors = validate_article_paths(["articles/nested/valid-slug-123.md"])
        self.assertTrue(any("invalid Zenn slug" in error for error in errors))

    def test_creation_rejects_invalid_slug_before_any_filesystem_mutation(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            articles_dir = Path(tmp) / "articles"
            with self.assertRaises(InvalidZennSlug):
                create_article_file(
                    articles_dir,
                    "2026-08-15-static-types-do-not-validate-external-input",
                    "content\n",
                )
            self.assertFalse(articles_dir.exists())

    def test_creation_uses_final_valid_slug_and_never_overwrites(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            articles_dir = Path(tmp) / "articles"
            slug = "2026-08-15-runtime-validation-boundary"
            path = create_article_file(articles_dir, slug, "first\n")
            self.assertEqual(path.name, f"{slug}.md")
            self.assertEqual(path.read_text(encoding="utf-8"), "first\n")
            with self.assertRaises(FileExistsError):
                create_article_file(articles_dir, slug, "second\n")
            self.assertEqual(path.read_text(encoding="utf-8"), "first\n")


if __name__ == "__main__":
    unittest.main()
