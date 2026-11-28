import tempfile
import unittest
from pathlib import Path

from pipeline.evidence_gate import check_article, validate_published_paths, validate_unique_slugs


class EvidenceGateTests(unittest.TestCase):
    def check(self, text: str) -> list[str]:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "article.md"
            path.write_text(text, encoding="utf-8")
            return check_article(path)

    def test_accepts_valid_frontmatter_and_rejects_clean_body(self) -> None:
        text = "---\ntitle: Example\nemoji: \"🧪\"\ntype: tech\ntopics: [python]\npublished: false\n---\nBody [source](https://example.com/source).\n"
        self.assertEqual([], self.check(text))

    def test_rejects_proxy_metadata(self) -> None:
        text = "---\ntitle: Example\nemoji: \"🧪\"\ntype: tech\ntopics: [python]\npublished: false\n---\n<!-- pipeline_meta: {} -->\n"
        self.assertIn("contains retired pipeline scoring metadata", self.check(text))

    def test_rejects_missing_fields_and_bad_publication_type(self) -> None:
        errors = self.check("---\ntitle: Example\npublished: yes\n---\n")
        self.assertIn("missing frontmatter emoji", errors)
        self.assertIn("published must be boolean", errors)
        self.assertIn("topics must be a YAML list", errors)

    def test_rejects_invalid_type_and_topic_count(self) -> None:
        errors = self.check('---\ntitle: Example\nemoji: "🧪"\ntype: blog\ntopics: [a, b, c, d, e, f]\npublished: false\n---\n')
        self.assertIn("type must be tech or idea", errors)
        self.assertIn("topics must contain 1..5 non-empty strings", errors)

    def test_rejects_unverified_prose_and_placeholder_code(self) -> None:
        base = '---\ntitle: Example\nemoji: "🧪"\ntype: tech\ntopics: [python]\npublished: false\n---\n'
        self.assertIn("contains an explicit unverified placeholder", self.check(base + "具体的な入力、出力、テスト結果は未確認。\n"))
        self.assertIn("contains an explicit unverified placeholder", self.check(base + "```python\nrows = fetch_rows()\n```\n"))

    def test_rejects_broken_local_reference(self) -> None:
        base = '---\ntitle: Example\nemoji: "🧪"\ntype: tech\ntopics: [python]\npublished: false\n---\n'
        errors = self.check(base + "[broken](missing/file.json)\n")
        self.assertTrue(any(error.startswith("broken local reference:") for error in errors))

    def test_requires_linked_primary_source_or_public_artifact(self) -> None:
        text = '---\ntitle: Example\nemoji: "🧪"\ntype: tech\ntopics: [python]\npublished: false\n---\nNo source.\n'
        self.assertIn("requires at least one linked primary source or public evidence artifact", self.check(text))

    def test_published_path_baseline_rejects_deletion_or_rename(self) -> None:
        self.assertEqual([], validate_published_paths({"articles/a.md"}, {"articles/a.md"}))
        self.assertEqual(["published article path removed or renamed: articles/a.md"], validate_published_paths(set(), {"articles/a.md"}))

    def test_duplicate_slug_check_is_case_insensitive(self) -> None:
        paths = [Path("articles/example-slug.md"), Path("articles/EXAMPLE-SLUG.md")]
        self.assertEqual(1, len(validate_unique_slugs(paths)))

    def test_rejects_empty_title_and_emoji(self) -> None:
        errors = self.check('---\ntitle: ""\nemoji: ""\ntype: tech\ntopics: [python]\npublished: false\n---\n')
        self.assertIn("title must be a non-empty string", errors)
        self.assertIn("emoji must be a non-empty string", errors)


if __name__ == "__main__":
    unittest.main()
