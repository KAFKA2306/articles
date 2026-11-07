import unittest
from pipeline.alternatives import alternatives_ready

def topic():
    return {
        "alternatives": [
            {"kind": kind, "name": kind, "reader_job": "choose a reliable approach",
             "primary_urls": ["https://example.org/source"], "tradeoff": "measurable cost"}
            for kind in ("incumbent", "direct", "adjacent")
        ],
        "unsearched_scope": "non-English implementations",
        "alternative_decision": {"verdict": "unresolved"},
    }

class AlternativesTests(unittest.TestCase):
    def test_unresolved_comparison_is_not_a_winner(self):
        self.assertTrue(alternatives_ready(topic()))

    def test_single_familiar_tool_cannot_pass(self):
        t = topic()
        t["alternatives"] = t["alternatives"][:1]
        self.assertFalse(alternatives_ready(t))

    def test_false_winner_without_measurement_is_rejected(self):
        t = topic()
        t["alternative_decision"] = {"verdict": "choose", "selected": "direct"}
        self.assertFalse(alternatives_ready(t))

    def test_winner_with_reproducible_comparison_record(self):
        t = topic()
        t["alternative_decision"] = {"verdict": "choose", "selected": "direct",
            "comparison": {"same_reader_job": "same task", "same_conditions": "same inputs",
                           "measured_result": "10 seconds versus 20",
                           "artifact_url": "https://example.org/run"}}
        self.assertTrue(alternatives_ready(t))

    def test_missing_primary_source_fails(self):
        t = topic()
        t["alternatives"][1]["primary_urls"] = []
        self.assertFalse(alternatives_ready(t))
