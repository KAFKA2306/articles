# Verification Stack v2 — Status

Date: 2026-08-15

## Canonical workline

- Branch: `experiment/verification-stack-v2-ground-truth`
- Draft PR: #116
- Superseded experiment: #115 (closed, not merged)

## Why v1 was discarded

The v1 experiment started with one unhealthy real repository and then interpreted tool output. That design can demonstrate operational behavior, but it cannot estimate detection recall or false-positive rate because the repository has no complete defect ground truth.

It also exposed the study to:

- fixture-selection bias;
- post-hoc metric selection;
- diagnostic-count inflation from cascading failures;
- single-run timing overinterpretation;
- premature article framing before the evidence architecture was stable.

The v1 DeepCode measurements remain historical observations only. They are not the canonical basis for the v2 recommendation.

## v2 evidence architecture

```text
preregister protocol
        ↓
freeze controlled fixtures
        ↓
freeze one-root-fault mutant manifest
        ↓
implement neutral harness
        ↓
run controlled correctness benchmark
        ↓
freeze real-repository sample
        ↓
run external-validity benchmark
        ↓
classify raw evidence
        ↓
make recommendation
        ↓
write article only if a non-obvious result exists
```

## Files currently frozen

- `benchmarks/verification-stack-v2/PROTOCOL.md`
- `benchmarks/verification-stack-v2/FIXTURE_DESIGN.md`
- `benchmarks/verification-stack-v2/RESULTS_SCHEMA.md`

## Candidate families under study

The protocol currently covers:

### Python

- Ruff vs established formatter/lint incumbents;
- Pyrefly / ty / Pyright / mypy for static typing;
- Pydantic for runtime trust boundaries.

### TypeScript

- Biome formatter vs Prettier;
- Oxlint vs ESLint + typescript-eslint;
- `tsc --noEmit` as compiler/type baseline;
- Zod for runtime trust boundaries.

### Local orchestration

- prek vs pre-commit.

### Workspace orchestration

- Nx vs Turborepo.

These names are candidate sets, not recommendations.

## What is not yet known

No v2 winner exists yet.

In particular, v2 has not yet established:

- whether Pyrefly should replace Pyright/mypy under the benchmark's correctness envelope;
- whether Oxlint can replace ESLint for the required rule surface without unacceptable gaps;
- whether Biome's formatter is preferable to Prettier for the selected compatibility/migration conditions;
- whether prek preserves hook semantics across the preregistered hook corpus;
- whether Nx or Turborepo produces the correct affected set/cache behavior on the controlled graph;
- whether Pydantic/Zod materially improve boundary safety for the chosen external-payload mutants relative to their maintenance/runtime cost.

## Publication state

There is intentionally **no new article candidate** for v2 yet.

The publication gate requires controlled results, frozen real-repo sampling, external-validity evidence, and at least one finding that changes an engineering decision.

If no non-obvious result appears, the work remains a benchmark/report rather than being forced into an article.