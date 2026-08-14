# Amendment v2.4 — controlled harness repair after invalid collection

Date: 2026-08-15

## Why this amendment exists

Controlled run `31820990784` completed collection at trigger SHA `143568b2d8e862a810bcc08edf22c7d75c0c9ad2` and was committed as evidence at `b25a748336e8946f78cc174325a3095aac1ef797`. Read-back of the raw records showed that part of that collection violated the benchmark's clean-baseline and executable-workspace preconditions.

The invalid attempt remains auditable at the fixed commit above. It must not be used as product-performance evidence for the affected scopes.

Observed harness failures in that attempt:

- Python formatter/linter commands scanned the whole fixture, so unrelated test-file formatting/E501 state made clean baselines non-zero.
- TypeScript formatter/linter commands scanned the whole copied fixture, including installed `node_modules`; Oxlint therefore reported third-party package diagnostics instead of only the frozen source fixture.
- Nx was invoked in temporary workspaces without locally resolvable Nx modules.
- Turborepo saw the temporary fixture as `monorepo: false`; the workspace fixture lacked the package-manager declaration needed for deterministic workspace discovery in this harness.

## What may change

Only execution plumbing required to satisfy the original measurement preconditions:

1. source-oriented formatter/linter commands are scoped to the frozen `src` directory;
2. temporary workspace copies expose the exact already-pinned benchmark `node_modules` locally;
3. the workspace root declares and the workflow pins the npm package-manager version used to generate workspace metadata;
4. a repair-validity gate requires clean source baselines and successful workspace command execution before repaired controlled evidence may replace the current working result files.

## What may not change

- `mutants.json` root-fault definitions;
- the 22 preregistered scenarios;
- expected affected sets;
- candidate versions or stability labels;
- scoring semantics;
- candidate outputs already observed in the invalid run;
- the frozen real-repository sample or its selected SHAs.

A repaired run is valid even if a candidate misses a mutant, produces a different affected set, fails patch parity, or fails cache correctness. Those are candidate observations. The repair gate checks only that the clean baseline and harness execution are valid enough to interpret those observations.

## Interpretation boundary

`status: complete` means collection completed; it is not a quality verdict. The repaired collection supersedes run `31820990784` only for controlled comparison, while the old fixed commit remains the audit trail for why this repair was necessary.
