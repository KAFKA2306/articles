# Amendment v2.4 — controlled harness repair after invalid collection

Date: 2026-08-15

Status: **canonical repair amendment; all affected controlled evidence must be rerun**

## Why this amendment exists

Controlled run `31820990784` completed collection at trigger SHA `143568b2d8e862a810bcc08edf22c7d75c0c9ad2`. Raw read-back showed that part of that collection violated the experiment's own clean-baseline and executable-workspace preconditions.

The invalid attempt remains auditable but MUST NOT contribute to recall, false-positive, latency, recommendation, story, or title selection for affected scopes.

Observed harness/configuration failures:

- Python formatters were invoked on the entire fixture, so an unrelated test file made the clean baseline fail.
- Flake8 and Ruff were not restricted to the same overlapping lint responsibility; Flake8 blocked on unrelated `E501` findings.
- Biome and Prettier are opinionated formatters with different canonical indentation, so one raw source tree cannot simultaneously be a preformatted clean baseline for both.
- Oxlint was invoked on `.`, so it linted the benchmark's shared `node_modules` tree.
- ESLint referenced `@typescript-eslint/*` rules without registering the `typescript-eslint` parser/plugin, causing configuration failure before source linting.
- Pyrefly was run without Pyrefly configuration. Official no-config behavior is the `basic` preset, which intentionally silences broader argument/return type diagnostics; that is not a valid test of Pyrefly as the experiment's blocking static-type authority.
- Nx was invoked in temporary workspace copies without a locally resolvable Nx module.
- Turborepo did not recognize the copied fixture as a multi-package workspace because the root lacked the package-manager declaration its v2 workspace model expects; it executed zero package tasks.

These are benchmark-construction failures, not candidate losses.

## Frozen repair rules

### Formatting

`PY-FORMAT-001` and `TS-FORMAT-001` use candidate-normalized clean baselines:

1. start from the same semantically valid source;
2. apply each formatter once to the target source file only;
3. require its second pass/check to be clean and semantic smoke checks to pass;
4. independently seed the same formatting mutant;
5. require check mode to observe a required change;
6. apply the formatter and require idempotence plus semantic smoke checks;
7. compare output to that candidate's own normalized baseline, not another formatter's canonical style.

Tabs-vs-spaces preference is not a correctness win or false positive.

### Python lint

`PY-LINT-001` scores the common unused-local responsibility only:

- Ruff `F841` on the controlled service file;
- Flake8 `F841` on the same file.

Unrelated style rules are outside this mutant.

### Python type checking

Pyrefly is run with its documented `default` preset for the blocking type-authority comparison. Its no-config `basic` behavior is retained only as an onboarding/default-mode observation, not as the full type-authority score.

### TypeScript lint/type

- Oxlint is restricted to `src` and uses the preregistered type-aware rules.
- ESLint is restricted to `src`, explicitly registers `typescript-eslint`'s parser/plugin, and retains the already frozen supported TypeScript profile.
- `tsc --noEmit` remains the compiler baseline.
- Oxlint `--type-check` remains an Experimental challenger; experimental status remains a disqualifier for default compiler authority under the current protocol.

### Workspace

The workspace is repaired only enough to satisfy the original execution precondition:

- root declares `private`, npm `workspaces`, and `packageManager`;
- lockfile is generated with the pinned npm used by the workflow;
- every fresh copy exposes the exact already-pinned local Nx/Turbo installation through local `node_modules`;
- project discovery must find exactly `core`, `ui`, `web`, `api`, and `docs` for both tools before affected/cache observations are recommendation-eligible;
- the same package manifests, dependency edges, changed files, deterministic task implementation, and expected affected sets are retained.

## Hard validity gate

The rerun writes `baseline-calibration.json`. `summary.json.status` may be `complete` only if:

- every declared non-formatter clean source baseline exits successfully;
- every formatter candidate-normalized baseline is idempotent and passes semantic smoke checks;
- both Nx and Turborepo discover exactly the five frozen projects;
- the hook runner baseline is valid.

If the gate fails, the run is `invalid_baseline`; mutant output is debugging evidence only.

The validity gate deliberately does **not** require a candidate to detect a mutant, agree on affected sets, hit the cache, or beat another candidate. Those are measured outcomes.

## What may not change

- the root-fault definitions in `mutants.json`;
- expected affected sets;
- frozen candidate versions/stability labels, except previously preregistered supported environment profiles;
- the frozen real-repository sample or its SHAs;
- scoring semantics after the repaired results become visible.

## Sampling independence

The real-repository sample was frozen before candidate-level controlled output was used for repository selection and remains unchanged:

- Python: `KAFKA2306/2511youtuber@95a0f6b4f5270d1463c15f301a2bd4f0d709c109`
- TypeScript: `KAFKA2306/investor2@9a45de93437456f215f1a251666f322254aac6b4`

## Interpretation boundary

A repaired `status: complete` means the calibrated evidence corpus executed under valid clean baselines. It is not a quality verdict and does not authorize an article thesis or publication.
