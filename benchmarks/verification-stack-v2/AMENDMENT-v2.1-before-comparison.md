# Verification Stack v2.1 — Pre-comparison amendment

Status: **PREREGISTERED BEFORE ANY CANDIDATE COMPARISON**

Date: 2026-08-15

At amendment time `state.json` had `comparison_started: false` and phase `fixtures_frozen`.

## Why this amendment exists

A design audit found two omissions before candidate output was observed:

1. the candidate set includes Ruff/Black and Biome/Prettier as formatting authorities, but the frozen corpus had no formatting-specific ground truth;
2. the candidate set includes prek/pre-commit, but the frozen corpus had no runner-neutral hook fixture for patch-parity measurement.

Leaving those omissions in place would permit conclusions about responsibilities the experiment never directly exercised. This amendment narrows that validity gap before comparison starts.

## Added controlled scenarios

- `PY-FORMAT-001` — valid Python with deliberately non-canonical spacing. A formatting authority detects it when check mode fails or produces the expected normalized patch. The source must remain semantically equivalent.
- `TS-FORMAT-001` — valid TypeScript with deliberately non-canonical spacing. Same criterion.
- `HOOK-PATCH-PARITY-001` — the same local hook configuration and dirty text fixture are executed by pinned pre-commit and pinned prek. The primary correctness outcome is byte-identical resulting patch and identical selected-file set.

These scenarios are evaluated independently from the original mutants.

## Additional formatter metrics

Formatter correctness is not diagnostic recall. For formatter scenarios record:

- changed/not-changed against the seeded formatting mutant;
- idempotence on the second formatting pass;
- parse/compile validity after formatting;
- semantic smoke-test result after formatting;
- normalized patch hash.

A faster formatter cannot be preferred if it changes semantics, fails idempotence, or cannot format the valid seeded input.

## Hook-runner metrics

For `HOOK-PATCH-PARITY-001` record:

- selected files;
- exit status;
- resulting repository diff SHA-256;
- second-run cleanliness/idempotence;
- cold and warm elapsed time separately.

The hook implementation is local and runner-neutral so this comparison measures orchestration semantics rather than differences between third-party hook repositories.

## State handling

Because the fixture corpus changes, the machine state is reset to `design_frozen` and the fixture gate must pass again before `harness_ready` can be reached.

This amendment does not select or favor any candidate and does not change the correctness-before-speed policy.