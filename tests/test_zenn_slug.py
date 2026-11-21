from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from pipeline.zenn_slug import (
    InvalidZennSlug,
    create_article_file,
    validate_article_paths,
    validate_article_metadata,
    validate_new_article,
    validate_repository,
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
            slug = "2026-08-15-01-runtime-validation-boundary"
            first = (
                '---\ntitle: "Example"\n'
                'emoji: "🧪"\ntype: "tech"\ntopics: []\n'
                'published: false\n'
                'created_at: "2026-08-15"\nupdated_at: "2026-08-15"\n'
                '---\n\nfirst\n'
            )
            path = create_article_file(articles_dir, slug, first)
            self.assertEqual(path.name, f"{slug}.md")
            self.assertEqual(path.read_text(encoding="utf-8"), first)
            with self.assertRaises(FileExistsError):
                create_article_file(articles_dir, slug, first)
            self.assertEqual(path.read_text(encoding="utf-8"), first)

    def test_new_article_dates_must_match_filename(self) -> None:
        body = (
            '---\ncreated_at: "2026-11-21"\n'
            'updated_at: "2026-11-21"\npublished: false\n---\n\nExample\n'
        )
        self.assertEqual(
            [],
            validate_new_article("articles/2026-11-21-01-example.md", body),
        )
        self.assertTrue(validate_new_article("articles/example-article.md", body))
        self.assertTrue(validate_new_article("articles/2026-11-20-01-example.md", body))
        self.assertTrue(validate_new_article("articles/2026-11-21-example.md", body))

    def test_invalid_dates_are_rejected_without_guessing(self) -> None:
        bad = (
            '---\ncreated_at: "2026-02-30"\n'
            'updated_at: "2026-02-28"\n---\n\nExample\n'
        )
        self.assertTrue(validate_article_metadata("articles/sample.md", bad))
        reverse = (
            '---\ncreated_at: "2026-11-21"\n'
            'updated_at: "2026-11-20"\n---\n\nExample\n'
        )
        self.assertTrue(validate_article_metadata("articles/sample.md", reverse))

    def test_full_scan_checks_existing_metadata_without_renaming(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            directory = Path(tmp) / "articles"
            directory.mkdir()
            legacy = directory / "existing-zenn-article.md"
            legacy.write_text(
                '---\ncreated_at: "2026-08-15"\n'
                'updated_at: "2026-11-21"\npublished: true\n---\n\nText\n',
                encoding="utf-8",
            )
            self.assertEqual([], validate_repository(Path(tmp)))
            legacy.write_text('---\npublished: true\n---\n\nText\n', encoding="utf-8")
            self.assertTrue(validate_repository(Path(tmp)))

if __name__ == "__main__":
    unittest.main()
