from __future__ import annotations

import tempfile
import unittest
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

from pipeline import zenn_production


class ZennProductionTests(unittest.TestCase):
    def test_collects_only_due_published_articles(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "articles").mkdir()
            (root / "articles" / "public-article-123.md").write_text(
                '---\ntitle: "Public title"\npublished: true\npublished_at: 2026-08-15 10:00\n---\n',
                encoding="utf-8",
            )
            (root / "articles" / "draft-article-123.md").write_text(
                '---\ntitle: "Draft"\npublished: false\n---\n', encoding="utf-8"
            )
            articles, errors = zenn_production.collect_published_articles(
                root,
                now=datetime(2026, 8, 15, 13, 0, tzinfo=ZoneInfo("Asia/Tokyo")),
            )
            self.assertEqual([], errors)
            self.assertEqual(["public-article-123"], [article.slug for article in articles])

    def test_future_published_true_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "articles").mkdir()
            (root / "articles" / "future-article-123.md").write_text(
                '---\ntitle: "Future"\npublished: true\npublished_at: 2026-08-16 10:00\n---\n',
                encoding="utf-8",
            )
            articles, errors = zenn_production.collect_published_articles(
                root,
                now=datetime(2026, 8, 15, 13, 0, tzinfo=ZoneInfo("Asia/Tokyo")),
            )
            self.assertEqual([], articles)
            self.assertTrue(any("invariant violation" in error for error in errors))

    def test_catalog_requires_slug_and_title_match(self) -> None:
        article = zenn_production.Article(
            Path("articles/example-article-123.md"),
            "example-article-123",
            "記事タイトル",
            datetime(2026, 8, 15, 10, 0, tzinfo=ZoneInfo("Asia/Tokyo")),
        )
        passed = zenn_production.compare_catalog(
            [article], {"example-article-123": "記事タイトル"}
        )
        self.assertTrue(passed[0].ok)
        missing = zenn_production.compare_catalog([article], {})
        self.assertFalse(missing[0].ok)
        mismatch = zenn_production.compare_catalog(
            [article], {"example-article-123": "別タイトル"}
        )
        self.assertFalse(mismatch[0].ok)

    def test_cli_exposes_root(self) -> None:
        source = (zenn_production.ROOT / "pipeline" / "zenn_production.py").read_text(
            encoding="utf-8"
        )
        self.assertIn('"--root"', source)
        self.assertIn("collect_published_articles(release_root)", source)

    def test_scheduled_verifier_reads_main(self) -> None:
        workflow = (
            zenn_production.ROOT / ".github" / "workflows" / "zenn-production-verify.yml"
        ).read_text(encoding="utf-8")
        self.assertIn("ref: main", workflow)
        self.assertIn("--root .", workflow)
        self.assertNotIn("zenn-release", workflow)
        self.assertNotIn("_zenn_release", workflow)
        self.assertIn("cron:", workflow)
        self.assertNotIn("push:\n", workflow)
        self.assertNotIn("cancel-in-progress", workflow)

    def test_manual_release_uses_main_as_single_publication_source(self) -> None:
        workflow = (
            zenn_production.ROOT / ".github" / "workflows" / "zenn-manual-release.yml"
        ).read_text(encoding="utf-8")
        self.assertIn("ref: main", workflow)
        self.assertIn('git push origin HEAD:main', workflow)
        self.assertIn('published_at:', workflow)
        self.assertIn("bash scripts/zenn-render-check.sh", workflow)
        self.assertIn("--root .", workflow)
        self.assertIn("DEPLOY_PENDING", workflow)
        self.assertIn("no rollback push is emitted", workflow)
        self.assertNotIn("zenn-release", workflow)
        self.assertNotIn("_zenn_release", workflow)
        self.assertNotIn("git push --force", workflow)
        self.assertNotIn("git push -f", workflow)
        self.assertNotIn("Roll back failed release", workflow)


if __name__ == "__main__":
    unittest.main()
