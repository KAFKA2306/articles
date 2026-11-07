"""Regression: a high score cannot override a reviewer's explicit veto."""

import unittest

from pipeline import editorial


class BlockingIssueGateTests(unittest.TestCase):
    def setUp(self):
        self.good = {
            **{axis: 5.0 for axis in editorial.TECHNICAL_AXES},
            **{axis: 5.0 for axis in editorial.EDITORIAL_AXES},
            "overall": 5.0,
            "story_overall": 5.0,
            "blocking_issues": [],
        }

    def test_high_scoring_supported_article_is_not_rejected(self):
        self.assertTrue(editorial.passes_quality(self.good, True))

    def test_source_failure_still_rejects(self):
        self.assertFalse(editorial.passes_quality(self.good, False))

    def test_unrecognized_veto_cannot_be_ignored(self):
        for issue in ("unsupported_numeric_claim", "causal_overreach",
                      "missing_first_hand_evidence", "unverified_source"):
            with self.subTest(issue=issue):
                self.assertFalse(editorial.passes_quality(
                    {**self.good, "blocking_issues": [issue]}, True))

    def test_missing_veto_data_fails_closed(self):
        incomplete = dict(self.good)
        del incomplete["blocking_issues"]
        self.assertFalse(editorial.passes_quality(incomplete, True))

    def test_aggregation_does_not_erase_incomplete_review(self):
        from unittest.mock import patch

        good = dict(self.good)
        incomplete = dict(good)
        del incomplete["blocking_issues"]
        malformed = {**good, "blocking_issues": [None]}
        with patch.object(editorial, "evaluate", side_effect=[good, incomplete, malformed]):
            combined = editorial.aggregate_evaluations("fixture", rounds=3)
        self.assertIn("invalid_reviewer_blocking_issues", combined["blocking_issues"])
        self.assertFalse(editorial.passes_quality(combined, True))

    def test_complete_clean_reviews_remain_eligible(self):
        from unittest.mock import patch

        with patch.object(editorial, "evaluate", return_value=dict(self.good)):
            combined = editorial.aggregate_evaluations("fixture", rounds=3)
        self.assertEqual([], combined["blocking_issues"])
        self.assertTrue(editorial.passes_quality(combined, True))

    def test_malformed_veto_data_fails_closed(self):
        for value in (None, "unsupported_numeric_claim", [""], [None]):
            with self.subTest(value=value):
                self.assertFalse(editorial.passes_quality(
                    {**self.good, "blocking_issues": value}, True))


if __name__ == "__main__":
    unittest.main()
