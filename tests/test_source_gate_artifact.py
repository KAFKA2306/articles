from __future__ import annotations

import unittest
from unittest.mock import patch

from pipeline import core


class SourceGateArtifactTests(unittest.TestCase):
    def check(self, urls: list[str]) -> tuple[bool, dict[str, object]]:
        with patch.object(core, "verify_url", return_value=True):
            return core.source_gate(" ".join(urls))

    def test_generic_project_links_cannot_fake_first_hand_evidence(self):
        ok, report = self.check([
            "https://github.com/KAFKA2306/articles",
            "https://github.com/KAFKA2306/graphiti",
            "https://docs.python.org/3/",
        ])
        self.assertFalse(ok)
        self.assertEqual([], report["own_github"])
        self.assertEqual(["https://docs.python.org/3/"], report["external_primary"])

    def test_concrete_artifacts_remain_eligible(self):
        ok, report = self.check([
            "https://github.com/KAFKA2306/articles/pull/185",
            "https://github.com/KAFKA2306/articles/commit/d5b8aedb87500541312d67cd57ed4bd6cf27941c",
            "https://docs.python.org/3/",
        ])
        self.assertTrue(ok)
        self.assertEqual(2, len(report["own_github"]))

    def test_mutable_main_blob_and_project_homepage_do_not_count(self):
        ok, report = self.check([
            "https://github.com/KAFKA2306/articles/blob/main/README.md",
            "https://github.com/KAFKA2306/articles",
            "https://docs.python.org/3/",
        ])
        self.assertFalse(ok)
        self.assertEqual([], report["own_github"])

    def test_one_artifact_cannot_count_twice(self):
        ok, report = self.check([
            "https://github.com/KAFKA2306/articles/pull/185",
            "https://github.com/KAFKA2306/articles/pull/185",
            "https://docs.python.org/3/",
        ])
        self.assertFalse(ok)
        self.assertEqual(1, len(report["own_github"]))


    def test_nonexistent_artifact_shapes_do_not_count(self):
        # URL reachability alone is not a valid artifact identifier.
        for fake in ("pull/not-an-id", "issues/anything", "commit/deadbeef",
                     "blob/feature/README.md", "actions/runs/nope"):
            with self.subTest(fake=fake):
                ok, report = self.check([
                    f"https://github.com/KAFKA2306/articles/{fake}",
                    "https://github.com/KAFKA2306/articles/pull/185",
                    "https://docs.python.org/3/",
                ])
                self.assertFalse(ok)
                self.assertEqual(1, len(report["own_github"]))

    def test_fragments_and_queries_do_not_multiply_artifacts(self):
        ok, report = self.check([
            "https://github.com/KAFKA2306/articles/pull/185",
            "https://github.com/KAFKA2306/articles/pull/185#discussion",
            "https://docs.python.org/3/",
        ])
        self.assertFalse(ok)
        self.assertEqual(1, len(report["own_github"]))

    def test_another_authors_github_artifact_is_not_official_external_source(self):
        ok, report = self.check([
            "https://github.com/KAFKA2306/articles/pull/185",
            "https://github.com/KAFKA2306/articles/commit/d5b8aedb87500541312d67cd57ed4bd6cf27941c",
            "https://github.com/other-owner/other-repo/pull/123",
        ])
        self.assertFalse(ok)
        self.assertEqual([], report["external_primary"])

    def test_stable_commit_blob_and_official_documentation_are_accepted(self):
        ok, report = self.check([
            "https://github.com/KAFKA2306/articles/blob/d5b8aedb87500541312d67cd57ed4bd6cf27941c/README.md",
            "https://github.com/KAFKA2306/articles/pull/185",
            "https://docs.python.org/3/",
        ])
        self.assertTrue(ok)
        self.assertEqual(2, len(report["own_github"]))


    def test_code_examples_and_comments_are_not_evidence(self):
        urls = [
            "https://github.com/KAFKA2306/articles/pull/185",
            "https://github.com/KAFKA2306/articles/commit/d5b8aedb87500541312d67cd57ed4bd6cf27941c",
            "https://docs.python.org/3/",
        ]
        article = "Example only:\n```text\n" + "\n".join(urls) + "\n```\n"
        with patch.object(core, "verify_url", return_value=True):
            ok, report = core.source_gate(article)
        self.assertFalse(ok)
        self.assertEqual([], report["valid_urls"])
        article = "<!-- " + " ".join(urls) + " -->"
        with patch.object(core, "verify_url", return_value=True):
            ok, report = core.source_gate(article)
        self.assertFalse(ok)
        self.assertEqual([], report["valid_urls"])

    def test_unclosed_and_shorter_fences_do_not_count_example_urls(self):
        urls = [
            "https://github.com/KAFKA2306/articles/pull/185",
            "https://github.com/KAFKA2306/articles/commit/d5b8aedb87500541312d67cd57ed4bd6cf27941c",
            "https://docs.python.org/3/",
        ]
        examples = [
            "```text\n" + "\n".join(urls),
            "````text\n```\n" + "\n".join(urls),
            "~~~~text\n```\n" + "\n".join(urls),
        ]
        for article in examples:
            with self.subTest(article=article[:20]), patch.object(core, "verify_url", return_value=True):
                ok, report = core.source_gate(article)
            self.assertFalse(ok)
            self.assertEqual([], report["valid_urls"])

    def test_valid_fence_preserves_following_prose_sources(self):
        urls = [
            "https://github.com/KAFKA2306/articles/pull/185",
            "https://github.com/KAFKA2306/articles/commit/d5b8aedb87500541312d67cd57ed4bd6cf27941c",
            "https://docs.python.org/3/",
        ]
        article = "````text\nhttps://example.invalid/sample\n````\n" + "\n".join(urls)
        with patch.object(core, "verify_url", return_value=True):
            ok, report = core.source_gate(article)
        self.assertTrue(ok)
        self.assertEqual(3, len(report["valid_urls"]))

    def test_comment_fence_does_not_hide_real_citations(self):
        urls = [
            "https://github.com/KAFKA2306/articles/pull/185",
            "https://github.com/KAFKA2306/articles/commit/d5b8aedb87500541312d67cd57ed4bd6cf27941c",
            "https://docs.python.org/3/",
        ]
        article = "<!--\n```\n-->\n" + "\n".join(urls)
        with patch.object(core, "verify_url", return_value=True):
            ok, report = core.source_gate(article)
        self.assertTrue(ok)
        self.assertEqual(3, len(report["valid_urls"]))

    def test_fenced_html_comment_markers_do_not_hide_prose_evidence(self):
        urls = [
            "https://github.com/KAFKA2306/articles/pull/185",
            "https://github.com/KAFKA2306/articles/commit/d5b8aedb87500541312d67cd57ed4bd6cf27941c",
            "https://docs.python.org/3/",
        ]
        article = "```html\n<!--\n```\n" + "\n".join(urls) + "\n<!-- internal note -->"
        with patch.object(core, "verify_url", return_value=True):
            ok, report = core.source_gate(article)
        self.assertTrue(ok)
        self.assertEqual(3, len(report["valid_urls"]))

    def test_inline_code_urls_do_not_satisfy_evidence_gate(self):
        urls = [
            "https://github.com/KAFKA2306/articles/pull/185",
            "https://github.com/KAFKA2306/articles/commit/d5b8aedb87500541312d67cd57ed4bd6cf27941c",
            "https://docs.python.org/3/",
        ]
        for ticks in ("\x60", "\x60\x60"):
            with self.subTest(delimiter=ticks):
                article = "Example: " + " ".join(ticks + url + ticks for url in urls)
                with patch.object(core, "verify_url", return_value=True):
                    ok, report = core.source_gate(article)
                self.assertFalse(ok)
                self.assertEqual([], report["valid_urls"])

    def test_inline_examples_do_not_hide_prose_citations(self):
        urls = [
            "https://github.com/KAFKA2306/articles/pull/185",
            "https://github.com/KAFKA2306/articles/commit/d5b8aedb87500541312d67cd57ed4bd6cf27941c",
            "https://docs.python.org/3/",
        ]
        article = " ".join(urls) + "\nExample: \x60https://example.invalid/not-evidence\x60"
        with patch.object(core, "verify_url", return_value=True):
            ok, report = core.source_gate(article)
        self.assertTrue(ok)
        self.assertEqual(3, len(report["valid_urls"]))

    def test_indented_code_urls_are_not_citations(self):
        urls = [
            "https://github.com/KAFKA2306/articles/pull/185",
            "https://github.com/KAFKA2306/articles/commit/d5b8aedb87500541312d67cd57ed4bd6cf27941c",
            "https://docs.python.org/3/",
        ]
        for indent in ("    ", "\t"):
            with self.subTest(indent=repr(indent)):
                article = "Example:\n\n" + "".join(indent + url + "\n" for url in urls)
                with patch.object(core, "verify_url", return_value=True):
                    ok, report = core.source_gate(article)
                self.assertFalse(ok)
                self.assertEqual([], report["valid_urls"])

    def test_indented_example_does_not_remove_prose_evidence(self):
        urls = [
            "https://github.com/KAFKA2306/articles/pull/185",
            "https://github.com/KAFKA2306/articles/commit/d5b8aedb87500541312d67cd57ed4bd6cf27941c",
            "https://docs.python.org/3/",
        ]
        article = " ".join(urls) + "\n\n    https://example.invalid/code-only\n"
        with patch.object(core, "verify_url", return_value=True):
            ok, report = core.source_gate(article)
        self.assertTrue(ok)
        self.assertEqual(3, len(report["valid_urls"]))

    def test_indented_paragraph_continuation_is_still_evidence(self):
        urls = [
            "https://github.com/KAFKA2306/articles/pull/185",
            "https://github.com/KAFKA2306/articles/commit/d5b8aedb87500541312d67cd57ed4bd6cf27941c",
            "https://docs.python.org/3/",
        ]
        article = "1. Sources:\n\n" + "".join("    - " + url + "\n" for url in urls)
        with patch.object(core, "verify_url", return_value=True):
            ok, report = core.source_gate(article)
        self.assertTrue(ok)
        self.assertEqual(3, len(report["valid_urls"]))

    def test_cited_links_outside_examples_still_count(self):
        article = (
            "Evidence: https://github.com/KAFKA2306/articles/pull/185 "
            "https://github.com/KAFKA2306/articles/commit/d5b8aedb87500541312d67cd57ed4bd6cf27941c "
            "https://docs.python.org/3/\n"
            "```text\nhttps://example.invalid/fake\n```"
        )
        with patch.object(core, "verify_url", return_value=True):
            ok, report = core.source_gate(article)
        self.assertTrue(ok)
        self.assertEqual(3, len(report["valid_urls"]))

if __name__ == "__main__":
    unittest.main()
