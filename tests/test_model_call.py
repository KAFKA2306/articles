from __future__ import annotations

import subprocess
import unittest
from unittest.mock import patch

from pipeline import core


class ModelCallTests(unittest.TestCase):
    @patch.object(core.shutil, "which", return_value="/usr/local/bin/copilot")
    @patch.object(core.subprocess, "run")
    def test_uses_prompt_argument_and_closed_stdin(self, run, _which):
        run.return_value = subprocess.CompletedProcess([], 0, "answer", "")
        self.assertEqual(core.model_call("system", "task"), "answer")
        args, kwargs = run.call_args
        self.assertEqual(args[0][1:3], ["-p", "SYSTEM INSTRUCTIONS:\nsystem\n\nUSER TASK:\ntask\n"])
        self.assertIs(kwargs["stdin"], subprocess.DEVNULL)
        self.assertNotIn("input", kwargs)
        self.assertEqual(kwargs["timeout"], 420)

    @patch.object(core.shutil, "which", return_value="copilot")
    @patch.object(core.subprocess, "run")
    def test_rejects_prompt_over_safe_argv_size(self, run, _which):
        with self.assertRaisesRegex(ValueError, "too large"):
            core.model_call("", "x" * (core.COPILOT_PROMPT_ARG_LIMIT + 1))
        run.assert_not_called()

    @patch.object(core.shutil, "which", return_value="copilot")
    @patch.object(core.subprocess, "run", side_effect=subprocess.TimeoutExpired("copilot", 420))
    def test_propagates_timeout(self, _run, _which):
        with self.assertRaises(subprocess.TimeoutExpired):
            core.model_call("system", "task")

    @patch.object(core.shutil, "which", return_value="copilot")
    @patch.object(core.subprocess, "run")
    def test_nonzero_exit_includes_stderr(self, run, _which):
        run.return_value = subprocess.CompletedProcess([], 1, "", "specific failure")
        with self.assertRaisesRegex(RuntimeError, "specific failure"):
            core.model_call("system", "task")

    def test_extracts_json_from_markdown_prose(self):
        self.assertEqual(core._extract_json_payload('Here is the result:\n```json\n{"ok": true}\n```'), '{"ok":true}')

    def test_extracts_nested_topic_json_without_false_ambiguity(self):
        source = 'Here is the topic:\n```json\n{"selected": {"title": "foo", "alternatives": [{"kind": "incumbent"}]}, "alternatives": [{"a": 1}]}\n```\nDone.'
        self.assertEqual(
            core._extract_json_payload(source),
            '{"alternatives":[{"a":1}],"selected":{"alternatives":[{"kind":"incumbent"}],"title":"foo"}}',
        )

    def test_rejects_conflicting_json_payloads(self):
        with self.assertRaises(ValueError):
            core._extract_json_payload('{"a":1} then {"b":2}')

    @patch.object(core.shutil, "which", return_value="copilot")
    @patch.object(core.subprocess, "run")
    def test_json_mode_retries_once_for_non_json(self, run, _which):
        run.side_effect = [
            subprocess.CompletedProcess([], 0, "thinking...", ""),
            subprocess.CompletedProcess([], 0, '{"ok":true}', ""),
        ]
        self.assertEqual(core.model_call("system", "task", json_mode=True), '{"ok":true}')
        self.assertEqual(run.call_count, 2)

    @patch.object(core.shutil, "which", return_value="copilot")
    @patch.object(core.subprocess, "run")
    def test_json_failure_has_sanitized_diagnostic(self, run, _which):
        run.return_value = subprocess.CompletedProcess([], 0, "no json github_pat_abcdefghijklmnop gho_abcde12345", "stderr ghs_secret123")
        with self.assertRaisesRegex(RuntimeError, "response_bytes=.*REDACTED"):
            core.model_call("system", "task", json_mode=True)


if __name__ == "__main__":
    unittest.main()
