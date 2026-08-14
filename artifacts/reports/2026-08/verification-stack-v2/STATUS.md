# Verification Stack v2 — Status

Date: 2026-08-15

## Goal

**The benchmark is not the deliverable. The deliverable is the strongest evidence-backed article this investigation can support.**

The article must change a professional reader's engineering decision, not merely enumerate tools or report timing differences. `benchmarks/verification-stack-v2/EDITORIAL_GOAL.md` is the terminal editorial contract.

## Canonical workline

- Branch: `experiment/verification-stack-v2-ground-truth`
- Draft PR: #116
- Superseded experiment: #115 (closed, not merged)
- Autonomous ChatGPT task: active hourly, scoped to the same canonical workline
- Repository controller: `.github/workflows/verification-stack-v2-autonomous.yml`

## Current machine state

```text
phase: fixtures_frozen
comparison_started: false
publication_authorized: false
blocked_on: neutral harness / pinned candidate versions
```

The repository controller successfully advanced `design_frozen -> fixtures_frozen` after validating the frozen mutant manifest and required fixture files.

No v2 candidate tool has been compared yet.

## Why v1 was discarded

The v1 experiment started with one unhealthy real repository and interpreted tool output afterward. That can demonstrate operational behavior, but it cannot estimate recall or blocking false-positive rate because the complete defect set is unknown.

It also exposed the study to fixture-selection bias, post-hoc metric selection, diagnostic-count inflation from cascading failures, single-run timing overinterpretation, and premature article framing.

The v1 DeepCode measurements remain historical observations only. They are not canonical evidence for v2.

## Evidence architecture

```text
preregister protocol
        ↓
freeze controlled fixtures                 DONE
        ↓
freeze one-root-fault mutant manifest      DONE
        ↓
pin candidate versions + neutral harness   NEXT
        ↓
run controlled correctness benchmark
        ↓
freeze real-repository sample
        ↓
run external-validity benchmark
        ↓
classify raw evidence
        ↓
generate >= 3 competing story propositions
        ↓
try to falsify each proposition
        ↓
select one decision-changing proposition
        ↓
write one unpublished article candidate
```

## Frozen evidence contracts

- `benchmarks/verification-stack-v2/PROTOCOL.md`
- `benchmarks/verification-stack-v2/FIXTURE_DESIGN.md`
- `benchmarks/verification-stack-v2/RESULTS_SCHEMA.md`
- `benchmarks/verification-stack-v2/EDITORIAL_GOAL.md`
- `benchmarks/verification-stack-v2/AUTONOMY.md`
- `benchmarks/verification-stack-v2/mutants.json`
- `benchmarks/verification-stack-v2/workspace/ground-truth.json`

## Implemented fixtures

### Python

Neutral Python 3.12 fixture with typed service code, async behavior, an external-payload boundary, deterministic unit tests, and a frozen payload mutant.

### TypeScript

Neutral strict TypeScript fixture with typed service code and an `unknown` boundary. Candidate-specific formatter/linter/schema code is intentionally kept outside the fixture.

### Workspace

A five-node workspace implementing the preregistered graph:

```text
web -> ui -> core
api ------> core
docs         independent
```

The expected affected sets and forbidden edges are frozen separately from Nx/Turborepo configuration.

## Candidate families under study

Candidate names are hypotheses, not recommendations.

- Python source hygiene: Ruff vs incumbent formatter/lint stack
- Python typing: Pyrefly / ty / Pyright / mypy
- Python runtime boundary: Pydantic vs unvalidated control
- TypeScript formatting: Biome vs Prettier
- TypeScript lint: Oxlint vs ESLint + typescript-eslint
- TypeScript compiler/type baseline: `tsc --noEmit`
- TypeScript runtime boundary: Zod vs unvalidated control
- Local orchestration: prek vs pre-commit
- Workspace orchestration: Nx vs Turborepo

## Article gate

After evidence classification, the autonomous workflow must generate at least three competing story propositions and try to falsify each using the same evidence.

A proposition survives only if it is:

- falsifiable;
- measured;
- externally plausible;
- decision-changing;
- non-obvious;
- bounded in generality.

If no proposition survives, `no_article` is a valid terminal state. The system must not manufacture a weak tool-comparison article.

Publication remains a separate explicit side effect.