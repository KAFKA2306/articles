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

    def test_maximum_length_is_50(self) -> None:
        self.assertEqual([], validate_slug("a" * 50))
        self.assertTrue(validate_slug("a" * 51))

    def test_allowed_characters(self) -> None:
        self.assertEqual([], validate_slug("valid-slug_123"))
        for slug in ("Invalid-Slug-123", "invalid.slug.123", "invalid slug 123"):
            with self.subTest(slug=slug):
                self.assertTrue(validate_slug(slug))

    def test_regression_rejects_original_54_character_filename(self) -> None:
        path = "articles/2026-08-15-static-types-do-not-validate-external-input.md"
        errors = validate_article_paths([path])
        self.assertTrue(any("invalid Zenn slug" in error for error in errors))

    def test_replacement_filename_is_valid(self) -> None:
        path = "articles/2026-08-15-runtime-validation-boundary.md"
        self.assertEqual([], validate_article_paths([path]))

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

    def test_pipeline_materializes_final_slug_without_rename(self) -> None:
        selection = Path("pipeline/selection.py").read_text(encoding="utf-8")
        core = Path("pipeline/core.py").read_text(encoding="utf-8")
        self.assertNotIn("finalize_publication_filename", selection)
        self.assertNotIn("old_path.rename", selection)
        self.assertIn("slug = publication_slug(article)", selection)
        self.assertIn("create_article_file(", core)
        self.assertIn("slug=slug", selection)

    def test_ci_runs_repository_wide_slug_gate(self) -> None:
        workflow = Path(".github/workflows/article-pipeline-ci.yml").read_text(
            encoding="utf-8"
        )
        self.assertIn("python -m pipeline.zenn_slug", workflow)

    def test_manual_release_is_generic_and_content_clean(self) -> None:
        workflow = Path(".github/workflows/zenn-manual-release.yml").read_text(
            encoding="utf-8"
        )
        self.assertIn("python -m pipeline.zenn_slug", workflow)
        self.assertIn("type: string", workflow)
        self.assertNotIn("type: choice", workflow)
        self.assertNotIn("zenn-deploy-sync", workflow)
        self.assertIn("git push origin HEAD:zenn-release", workflow)
        self.assertIn("git worktree add _zenn_release origin/zenn-release", workflow)
        self.assertNotIn("git push origin HEAD:main", workflow)


if __name__ == "__main__":
    unittest.main()
