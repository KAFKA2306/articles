"""A reachable allowlisted URL is not evidence if it redirects elsewhere."""
import unittest
from unittest.mock import patch
from pipeline import core

class RedirectEvidenceTests(unittest.TestCase):
    def check_redirect(self, final_url: str) -> bool:
        class Response:
            status = 200
            def __enter__(self):
                return self
            def __exit__(self, *_args):
                return False
            def geturl(self):
                return final_url
            def read(self, _size):
                return b"ok"
        with patch.object(core.urllib.request, "urlopen", return_value=Response()):
            return core.verify_url("https://docs.python.org/3/")

    def test_external_redirect_is_not_primary_evidence(self):
        self.assertFalse(self.check_redirect("https://example.com/claim"))

    def test_http_downgrade_is_not_primary_evidence(self):
        self.assertFalse(self.check_redirect("http://docs.python.org/3/"))

    def test_allowed_official_redirect_remains_valid(self):
        self.assertTrue(self.check_redirect("https://docs.python.org/3/library/"))

    def test_zenn_profile_redirect_is_not_article_evidence(self):
        self.assertFalse(self.check_redirect("https://zenn.dev/someone"))

if __name__ == "__main__":
    unittest.main()
