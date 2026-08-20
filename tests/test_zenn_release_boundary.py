from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
WORKFLOWS = ROOT / ".github" / "workflows"
MANUAL_RELEASE = WORKFLOWS / "zenn-manual-release.yml"
PRODUCTION_VERIFY = WORKFLOWS / "zenn-production-verify.yml"


class ZennReleaseBoundaryTests(unittest.TestCase):
    def test_release_is_manual_only(self) -> None:
        text = MANUAL_RELEASE.read_text(encoding="utf-8")
        self.assertIn("workflow_dispatch:", text)
        self.assertNotIn("\n  schedule:", text)
        self.assertNotIn("\n  push:", text)
        self.assertNotIn("\n  pull_request:", text)

    def test_release_requires_explicit_confirmation(self) -> None:
        text = MANUAL_RELEASE.read_text(encoding="utf-8")
        self.assertIn("confirm:", text)
        self.assertIn('test "$CONFIRM" = "true"', text)

    def test_release_is_single_slug_and_idempotent(self) -> None:
        text = MANUAL_RELEASE.read_text(encoding="utf-8")
        self.assertIn('"articles/${SLUG}.md"|"images/${SLUG}/"*', text)
        self.assertIn("refusing unrelated zenn-release change", text)
        self.assertIn("refusing multi-article release diff", text)
        self.assertIn("NO_DEPLOY: zenn-release already contains the requested snapshot", text)
        self.assertNotIn("--force", text)

    def test_release_stages_pr_instead_of_touching_production_branch(self) -> None:
        text = MANUAL_RELEASE.read_text(encoding="utf-8")
        self.assertIn('branch="zenn-sync/${GITHUB_RUN_ID}-${GITHUB_RUN_ATTEMPT}"', text)
        self.assertIn("gh pr create", text)
        self.assertIn("--base zenn-release", text)
        self.assertNotIn("git push origin HEAD:zenn-release", text)
        self.assertNotIn("gh pr merge", text)

    def test_only_one_pending_release_pr_is_allowed(self) -> None:
        text = MANUAL_RELEASE.read_text(encoding="utf-8")
        self.assertIn("Refuse a second pending production change", text)
        self.assertIn("--base zenn-release", text)
        self.assertIn("A zenn-release pull request is already pending", text)

    def test_publish_and_unpublish_share_one_staging_path(self) -> None:
        text = MANUAL_RELEASE.read_text(encoding="utf-8")
        self.assertIn("- publish", text)
        self.assertIn("- unpublish", text)
        self.assertIn("stage: ${ACTION} ${SLUG}", text)

    def test_no_workflow_directly_pushes_zenn_release(self) -> None:
        offenders: list[str] = []
        for path in WORKFLOWS.glob("*.yml"):
            text = path.read_text(encoding="utf-8")
            if "git push origin HEAD:zenn-release" in text:
                offenders.append(path.name)
        self.assertEqual([], offenders)

    def test_production_verifier_is_triggered_by_release_branch_update(self) -> None:
        text = PRODUCTION_VERIFY.read_text(encoding="utf-8")
        self.assertIn("push:", text)
        self.assertIn("branches: [zenn-release]", text)
        self.assertIn("permissions:\n  contents: read", text)


if __name__ == "__main__":
    unittest.main()
