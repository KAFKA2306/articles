# Verification Stack v2.4 — Clean-baseline calibration

Status: **VERSIONED AMENDMENT AFTER INVALID CONTROLLED ATTEMPT; ALL AFFECTED RESULTS MUST BE RERUN**

Date: 2026-08-15

## Why the previous controlled result is invalid for recommendation

The first complete controlled collection satisfied the mechanical state gate but failed the experiment's own clean-baseline precondition for several candidates. Raw stdout/stderr shows the failures were benchmark construction errors rather than evidence that the products cannot perform their declared responsibility:

- Python formatters were invoked on the entire fixture, so an unrelated test file that had not been normalized by either formatter made the clean baseline fail.
- Flake8 and Ruff were not restricted to the same overlapping lint rule; Flake8 therefore blocked on unrelated `E501` line-length findings.
- Biome formatted the whole TypeScript fixture, including JSON/config files and source style where its default indentation differs from Prettier's. A single raw source tree therefore cannot be a preformatted clean baseline for two opinionated formatters with different canonical output.
- Oxlint was invoked on `.`, which caused it to lint the benchmark's shared `node_modules` tree rather than only the controlled `src` corpus.
- ESLint's flat config referenced `@typescript-eslint/*` rules without registering `typescript-eslint`'s parser/plugin, so it exited on configuration before linting the fixture.
- Nx was executed from a fresh workspace copy without a locally resolvable Nx module.
- Turborepo 2 requires/uses the root `packageManager` and lockfile to stabilize its package graph; the fixture omitted `packageManager`, so Turbo treated the copy as a single-package workspace and executed zero package tasks.
- Pyrefly was run with no Pyrefly config. Its documented no-config behavior is the `basic` preset, which intentionally silences broader argument/return type diagnostics. That mode is not a valid test of Pyrefly as the benchmark's full static-type authority.

These are harness/configuration failures. The previous controlled result remains historical debugging evidence only and MUST NOT contribute to recall, false-positive, latency, recommendation, story, or title selection.

## Calibration rules frozen for rerun

### Formatting

Opinionated formatters are not required to produce byte-identical style to each other.

For `PY-FORMAT-001` and `TS-FORMAT-001`:

1. start from the same semantically valid source;
2. create a **candidate-normalized clean baseline** by applying that formatter once to the target source file only;
3. verify the second pass is clean/idempotent;
4. seed the same semantic formatting mutant from the unnormalized fixture;
5. require check mode to detect a change;
6. apply the formatter and require parse/type smoke checks to pass;
7. compare candidate output against that candidate's normalized clean baseline, not against another formatter's style.

A formatter difference in tabs/spaces is not a false positive and not a correctness win.

### Python lint

`PY-LINT-001` compares the overlapping unused-local responsibility only:

- Ruff: `F841` on the controlled service file;
- Flake8: `F841` on the same file.

Unrelated style rules are outside this mutant.

### Pyrefly

Pyrefly is evaluated as a blocking static type authority with its documented `default` preset, not the no-config `basic` preset. The no-config/basic behavior is recorded separately as an onboarding/default-mode observation.

### TypeScript lint

- Oxlint is restricted to `src` and uses the preregistered type-aware rules.
- ESLint is restricted to `src` and explicitly registers `typescript-eslint`'s parser and plugin with `projectService`.
- Both use their previously frozen officially supported TypeScript environment profiles.

### TypeScript compiler

`tsc --noEmit` remains the compiler baseline. Oxlint `--type-check` remains an Experimental challenger and is restricted to the controlled source scope; its experimental status remains a disqualifier for becoming the default compiler authority under the current protocol.

### Workspace

The controlled workspace is repaired into a valid npm workspace before rerun:

- root `package.json` declares `private`, `workspaces`, and `packageManager`;
- lockfile is generated before execution;
- fresh copies receive access to the exact pinned local Nx/Turbo installation rather than falling back to unrelated global binaries;
- package graph discovery must succeed before affected/cache scenarios are scored;
- a candidate that discovers zero projects/tasks when five are expected is a setup failure, not a correctness score.

Nx and Turborepo still receive the same package manifests, dependency edges, deterministic task implementation, changed files, and expected affected sets.

## New hard gate

The rerun must emit `baseline-calibration.json`. Controlled evidence can be marked `complete` only if:

- every non-formatter candidate's declared clean baseline exits successfully;
- every formatter's candidate-normalized baseline is idempotent and passes semantic smoke checks;
- the workspace discovery gate finds exactly the five preregistered projects for both Nx and Turborepo;
- hook runner baselines are valid.

If this gate fails, mutant results are collected only as debugging artifacts and `summary.json.status` must be `invalid_baseline`, never `complete`.

## Sampling independence

The real-repository sample was frozen before the controlled candidate-level outputs were inspected for repository selection. It remains frozen:

- Python: `KAFKA2306/2511youtuber@95a0f6b4f5270d1463c15f301a2bd4f0d709c109`
- TypeScript: `KAFKA2306/investor2@9a45de93437456f215f1a251666f322254aac6b4`

No reselection is permitted because of this amendment.
