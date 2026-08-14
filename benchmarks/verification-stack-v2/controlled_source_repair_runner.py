from __future__ import annotations

import controlled_source_runner as base


# v2.4 repair: preserve the frozen mutants and scoring scopes, but prevent
# unrelated test/config/package-manager files from becoming clean-baseline
# failures for source-oriented formatter/linter checks.
base.COMMANDS.update(
    {
        "ruff_lint": ["ruff", "check", "--no-cache", "--output-format=json", "src"],
        "ruff_format": ["ruff", "format", "--check", "src"],
        "black": ["black", "--check", "src"],
        "flake8": ["flake8", "src"],
        "ty": ["ty", "check", "--output-format", "concise", "--no-progress", "src"],
        "pyright": ["pyright", "--outputjson", "src"],
        "mypy": ["mypy", "--show-error-codes", "--no-error-summary", "src"],
        "biome": ["biome", "format", "src"],
        "prettier": ["prettier", "--check", "src"],
        "oxlint": ["oxlint", "--type-aware", "src"],
        "eslint": ["eslint", "src"],
        "oxlint_type_check": ["oxlint", "--type-aware", "--type-check", "src"],
    }
)
base.FORMAT_WRITE.update(
    {
        "ruff_format": ["ruff", "format", "src"],
        "black": ["black", "src"],
        "biome": ["biome", "format", "--write", "src"],
        "prettier": ["prettier", "--write", "src"],
    }
)


if __name__ == "__main__":
    base.main()
