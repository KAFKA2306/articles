"""Acceptance tests: reviewer blockers must override otherwise passing scores."""
import unittest
from pipeline.core import passes_quality


class BlockingIssueGateTests(unittest.TestCase):
    def setUp(self):
        self.review = {
            "overall": 5.0,
            "logic": 5.0,
            "utility": 5.0,
            "readability": 5.0,
            "originality": 5.0,
            "clarity": 5.0,
        }

    def test_high_scores_do_not_override_unverified_claim_blocker(self):
        review = {**self.review, "blocking_issues": ["Numerical claim has no reproducible primary evidence"]}
        self.assertFalse(passes_quality(review, sources_ok=True))

    def test_clean_review_with_sources_still_passes(self):
        self.assertTrue(passes_quality({**self.review, "blocking_issues": []}, sources_ok=True))

    def test_missing_sources_still_fails(self):
        self.assertFalse(passes_quality(self.review, sources_ok=False))


if __name__ == "__main__":
    unittest.main()
