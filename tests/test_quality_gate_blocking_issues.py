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

    def test_missing_reviewer_blocker_verdict_fails_closed(self):
        # A reviewer response without this field is not a clean review.
        self.assertFalse(passes_quality(self.review, sources_ok=True))

    def test_aggregated_review_missing_one_verdict_fails_closed(self):
        from unittest.mock import patch
        from pipeline.core import aggregate_evaluations
        complete = {**self.review, "blocking_issues": [], "revision_actions": []}
        missing = {**self.review, "revision_actions": []}
        with patch("pipeline.core.evaluate", side_effect=[complete, missing, complete]):
            aggregated = aggregate_evaluations("example")
        self.assertFalse(passes_quality(aggregated, sources_ok=True))

    def test_malformed_blocker_entry_cannot_be_discarded_by_aggregation(self):
        from unittest.mock import patch
        from pipeline.core import aggregate_evaluations
        clean = {**self.review, "blocking_issues": [], "revision_actions": []}
        malformed = {**self.review, "blocking_issues": [None], "revision_actions": []}
        with patch("pipeline.core.evaluate", side_effect=[clean, malformed, clean]):
            aggregated = aggregate_evaluations("example")
        self.assertFalse(passes_quality(aggregated, sources_ok=True))

    def test_incomplete_numeric_review_cannot_be_outvoted(self):
        from unittest.mock import patch
        from pipeline.core import aggregate_evaluations
        clean = {**self.review, "blocking_issues": [], "revision_actions": []}
        incomplete = {**clean}
        del incomplete["logic"]
        with patch("pipeline.core.evaluate", side_effect=[clean, incomplete, clean]):
            aggregated = aggregate_evaluations("example")
        self.assertFalse(passes_quality(aggregated, sources_ok=True))

    def test_nonfinite_numeric_review_cannot_pass(self):
        from unittest.mock import patch
        from pipeline.core import aggregate_evaluations
        clean = {**self.review, "blocking_issues": [], "revision_actions": []}
        invalid = {**clean, "overall": float("nan")}
        with patch("pipeline.core.evaluate", side_effect=[clean, invalid, clean]):
            aggregated = aggregate_evaluations("example")
        self.assertFalse(passes_quality(aggregated, sources_ok=True))

    def test_model_review_missing_score_is_not_silently_zero(self):
        import json
        from unittest.mock import patch
        from pipeline.core import evaluate
        payload = {"logic": 5, "utility": 5, "readability": 5, "originality": 5}
        with patch("pipeline.core.model_call", return_value=json.dumps(payload)):
            with self.assertRaisesRegex(ValueError, "clarity"):
                evaluate("example")

    def test_model_review_nonfinite_score_is_rejected(self):
        import json
        from unittest.mock import patch
        from pipeline.core import evaluate
        payload = {"logic": 5, "utility": 5, "readability": 5, "originality": 5, "clarity": float("nan")}
        with patch("pipeline.core.model_call", return_value=json.dumps(payload)):
            with self.assertRaisesRegex(ValueError, "clarity"):
                evaluate("example")

    def test_complete_model_review_retains_mean(self):
        import json
        from unittest.mock import patch
        from pipeline.core import evaluate
        payload = {"logic": 5, "utility": 4, "readability": 3, "originality": 4, "clarity": 4, "blocking_issues": []}
        with patch("pipeline.core.model_call", return_value=json.dumps(payload)):
            self.assertEqual(4.0, evaluate("example")["overall"])

    def test_clean_review_with_sources_still_passes(self):
        self.assertTrue(passes_quality({**self.review, "blocking_issues": []}, sources_ok=True))

    def test_missing_sources_still_fails(self):
        self.assertFalse(passes_quality(self.review, sources_ok=False))


if __name__ == "__main__":
    unittest.main()
