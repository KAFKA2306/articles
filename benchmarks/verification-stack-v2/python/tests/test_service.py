import asyncio
import importlib.util
from pathlib import Path
import unittest


SERVICE_PATH = Path(__file__).parents[1] / "src" / "verification_fixture" / "service.py"
SPEC = importlib.util.spec_from_file_location("verification_fixture.service", SERVICE_PATH)
assert SPEC and SPEC.loader
service = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(service)


class ServiceTests(unittest.TestCase):
    def test_calculate_total(self) -> None:
        self.assertAlmostEqual(service.calculate_total(100.0, 0.2), 120.0)

    def test_render_total(self) -> None:
        self.assertEqual(service.render_total(120.0), "120.00")

    def test_next_count(self) -> None:
        self.assertEqual(asyncio.run(service.next_count()), 2)


if __name__ == "__main__":
    unittest.main()
