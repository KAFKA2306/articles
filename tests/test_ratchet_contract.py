from __future__ import annotations

import copy
import unittest
from unittest import mock

from pipeline import audit, core


class RatchetContractTests(unittest.TestCase):
    def test_canonical_kpis_and_image_policy_pass(self) -> None:
        audit.audit_config()

    def test_fixed_image_count_fails_closed(self) -> None:
        config = copy.deepcopy(core.CONFIG)
        config["image_policy"]["fixed_count"] = 10
        with mock.patch.object(core, "CONFIG", config):
            with self.assertRaises(SystemExit):
                audit.audit_config()

    def test_extra_kpi_fails_closed(self) -> None:
        config = copy.deepcopy(core.CONFIG)
        config["ratchet_kpis"].append("article_count")
        with mock.patch.object(core, "CONFIG", config):
            with self.assertRaises(SystemExit):
                audit.audit_config()


if __name__ == "__main__":
    unittest.main()
