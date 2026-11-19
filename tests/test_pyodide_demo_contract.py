from __future__ import annotations

import json
import runpy
import unittest
from pathlib import Path

ROOT = Path(__file__).parents[1]
DEMO = ROOT / "demos" / "python-syntax-gate"


class PyodideDemoContractTests(unittest.TestCase):
    def test_manifest_fixture_matches_python_core(self) -> None:
        manifest = json.loads((DEMO / "demo.json").read_text(encoding="utf-8"))
        namespace = runpy.run_path(
            str(DEMO / "syntax_gate.py"),
            init_globals={"DEMO_INPUT": manifest["inputs"]["fixed"]},
        )
        check_source = namespace["check_source"]
        self.assertTrue(
            check_source(manifest["inputs"]["broken"]).startswith(
                manifest["expected"]["broken_prefix"]
            )
        )
        self.assertEqual(
            check_source(manifest["inputs"]["fixed"]),
            manifest["expected"]["fixed"],
        )


if __name__ == "__main__":
    unittest.main()
