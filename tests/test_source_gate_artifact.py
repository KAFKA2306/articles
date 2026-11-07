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


if __name__ == "__main__":
    unittest.main()
