# Verification Stack v2.3 — Deterministic real-repository sampling

Status: **FROZEN AFTER CONTROLLED COLLECTION, BEFORE CONTROLLED CANDIDATE OUTPUT IS INSPECTED**

Date: 2026-08-15

At amendment time `state.json` was `controlled_results_ready`; the controlled evidence files existed, but candidate-level result content had not been inspected for story selection or repository selection.

## Why this amendment exists

The original protocol requires an active, public, non-archived repository but did not define `active` numerically. A subjective interpretation after seeing controlled results would create a selection degree of freedom.

## Frozen repository universe

The sampling universe is repositories owned by `KAFKA2306` returned by the GitHub REST repositories API at sampling time.

A repository is eligible for either language only if all are true:

- visibility is public;
- `archived == false`;
- `fork == false` (the repository must be an independent codebase rather than an upstream mirror);
- `pushed_at >= 2025-08-15T00:00:00Z` (fixed one-year activity window relative to the experiment date);
- its default-branch head SHA can be frozen;
- it has `.github/workflows/` or a conventional test directory/file signal;
- static inspection does not reveal a required private package index/token solely to install or invoke static checks.

## Python eligibility

In addition to the universe rules:

- root contains one of `pyproject.toml`, `requirements.txt`, `Pipfile`, or `uv.lock`;
- repository tree contains at least 10 non-vendored `.py` files;
- generated/vendor/virtual-environment paths are excluded from the source count.

## TypeScript eligibility

In addition to the universe rules:

- root contains `package.json`;
- root contains at least one lockfile among `package-lock.json`, `pnpm-lock.yaml`, `yarn.lock`, `bun.lock`, `bun.lockb`;
- repository tree contains at least one `tsconfig*.json`;
- repository tree contains at least 10 non-vendored `.ts`/`.tsx` files;
- generated/vendor paths including `node_modules`, `dist`, `build`, `.next`, coverage and vendored copies are excluded from the source count.

## Deterministic choice

For Python and TypeScript independently:

1. freeze the full eligible inventory with exact default-branch head SHA and qualification evidence;
2. compute `sha256(repository_full_name.encode('utf-8')).hexdigest()`;
3. choose the lexicographically smallest digest;
4. if one repository qualifies for both languages, it may be selected for both because the rule is applied independently; do not manually substitute a more convenient repository.

## Installation qualification

The sample is frozen before candidate output is inspected. If the selected repository later proves to require a private credential or cannot be installed under its own public documented/lockfile path, record that as a preregistered **external-validity setup incompatibility**. Do not replace it post hoc with a friendlier repository unless a versioned protocol amendment is made and all affected external-validity results are rerun.

## What the sample can prove

The real repositories can test:

- invocation compatibility;
- configuration/migration friction;
- diagnostic/actionability characteristics;
- cold/warm operational latency;
- whether controlled conclusions survive ordinary repository structure.

They cannot estimate total defect recall because their complete defect ground truth is unknown.
