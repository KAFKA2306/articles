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


if __name__ == "__main__":
    unittest.main()
