from __future__ import annotations

import unittest

from pipeline.publication_diff import PublicationState, validate_transition


class PublicationDiffTests(unittest.TestCase):
    def test_single_promotion_is_allowed(self) -> None:
        errors = validate_transition(
            [
                (
                    "articles/a-valid-slug-123.md",
                    PublicationState(False, "2026-08-15 10:00"),
                    PublicationState(True, "2026-08-15 10:00"),
                )
            ]
        )
        self.assertEqual([], errors)

    def test_multiple_promotions_fail_closed(self) -> None:
        errors = validate_transition(
            [
                (
                    "articles/a-valid-slug-123.md",
                    PublicationState(False, None),
                    PublicationState(True, None),
                ),
                (
                    "articles/b-valid-slug-123.md",
                    PublicationState(False, None),
                    PublicationState(True, None),
                ),
            ]
        )
        self.assertTrue(any("at most one article" in error for error in errors))

    def test_existing_published_at_is_immutable(self) -> None:
        errors = validate_transition(
            [
                (
                    "articles/a-valid-slug-123.md",
                    PublicationState(False, "2026-08-13 10:00"),
                    PublicationState(True, "2026-08-15 10:00"),
                )
            ],
            original_published_at={
                "articles/a-valid-slug-123.md": "2026-08-13 10:00"
            },
        )
        self.assertTrue(any("published_at is immutable" in error for error in errors))

    def test_restoring_first_repository_published_at_is_allowed(self) -> None:
        path = "articles/a-valid-slug-123.md"
        errors = validate_transition(
            [
                (
                    path,
                    PublicationState(True, "2026-08-15 10:00"),
                    PublicationState(True, "2026-08-13 10:00"),
                )
            ],
            original_published_at={path: "2026-08-13 10:00"},
        )
        self.assertEqual([], errors)

    def test_new_article_may_choose_initial_published_at(self) -> None:
        errors = validate_transition(
            [
                (
                    "articles/new-valid-slug-123.md",
                    None,
                    PublicationState(True, "2026-08-15 10:00"),
                )
            ]
        )
        self.assertEqual([], errors)


if __name__ == "__main__":
    unittest.main()
