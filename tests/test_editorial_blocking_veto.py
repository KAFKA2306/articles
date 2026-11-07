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

    def test_nonfinite_scores_never_pass_quality_gate(self):
        # A malformed numeric model output previously made NaN look like 5.0.
        for bad in (float("nan"), float("inf"), -float("inf"), "NaN", "Infinity"):
            with self.subTest(score=repr(bad)):
                for axis in ("logic", "interest", "overall", "story_overall"):
                    with self.subTest(axis=axis):
                        self.assertFalse(editorial.passes_quality(
                            {**self.good, axis: bad}, True))

    def test_out_of_rubric_scores_cannot_be_promoted_to_perfect(self):
        # A model returning 500 previously passed as 5.0 after clamping.
        for bad in (500, 5.1, -1, True, "500"):
            with self.subTest(score=repr(bad)):
                for axis in ("logic", "interest", "overall", "story_overall"):
                    with self.subTest(axis=axis):
                        self.assertFalse(editorial.passes_quality(
                            {**self.good, axis: bad}, True))

    def test_out_of_rubric_minority_review_is_not_hidden_by_median(self):
        from unittest.mock import patch

        good = dict(self.good)
        corrupted = {**good, "logic": 500}
        with patch.object(editorial, "evaluate", side_effect=[good, corrupted, good]):
            combined = editorial.aggregate_evaluations("fixture", rounds=3)
        self.assertIn("reviewer_score_below_quality_floor", combined["blocking_issues"])
        self.assertFalse(editorial.passes_quality(combined, True))

    def test_nonfinite_minority_review_cannot_be_hidden_by_median(self):
        from unittest.mock import patch

        good = dict(self.good)
        corrupted = {**good, "logic": float("nan")}
        with patch.object(editorial, "evaluate", side_effect=[good, corrupted, good]):
            combined = editorial.aggregate_evaluations("fixture", rounds=3)
        self.assertIn("reviewer_score_below_quality_floor", combined["blocking_issues"])
        self.assertFalse(editorial.passes_quality(combined, True))

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

    def test_single_dissenting_low_score_cannot_be_hidden_by_median(self):
        from unittest.mock import patch

        good = dict(self.good)
        low = {**good, "logic": 1.0, "blocking_issues": []}
        # Previously the median of [1, 5, 5] passed every score floor.
        with patch.object(editorial, "evaluate", side_effect=[good, low, good]):
            combined = editorial.aggregate_evaluations("unsupported claim", rounds=3)
        self.assertEqual(5.0, combined["logic"])
        self.assertIn("reviewer_score_below_quality_floor", combined["blocking_issues"])
        self.assertFalse(editorial.passes_quality(combined, True))

    def test_single_dissenting_interest_score_cannot_be_hidden(self):
        from unittest.mock import patch

        good = dict(self.good)
        low = {**good, "interest": 2.0, "blocking_issues": []}
        with patch.object(editorial, "evaluate", side_effect=[good, low, good]):
            combined = editorial.aggregate_evaluations("weak opening", rounds=3)
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
