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


if __name__ == "__main__":
    unittest.main()
