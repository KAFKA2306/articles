from __future__ import annotations

import unittest

from pipeline.runtime import extract_json_object


class RuntimeJsonTests(unittest.TestCase):
    def test_plain_json(self) -> None:
        self.assertEqual(extract_json_object('{"ok": true}'), {"ok": True})

    def test_markdown_fenced_json(self) -> None:
        self.assertEqual(
            extract_json_object('```json\n{"score": 4.1}\n```'),
            {"score": 4.1},
        )

    def test_prose_prefixed_json(self) -> None:
        self.assertEqual(
            extract_json_object('Result follows:\n{"status": "PASS"}\nDone.'),
            {"status": "PASS"},
        )

    def test_missing_object_fails_closed(self) -> None:
        with self.assertRaises(RuntimeError):
            extract_json_object("not-json")


if __name__ == "__main__":
    unittest.main()
