# Verification Stack v2 — Controlled Fixture Design

Status: **DESIGN FROZEN BEFORE TOOL EXECUTION**

This file defines the controlled systems under test. It exists to prevent choosing a repository, defect, or dependency graph after seeing which candidate tool performs well.

The benchmark is intentionally split into three fixtures. A tool is evaluated only against responsibilities it claims to own.

## 1. Python fixture

### Clean baseline

The baseline is a small installable Python 3.12 project with:

- `pyproject.toml`;
- typed application code;
- one external-data boundary;
- deterministic unit tests;
- no syntax, lint, type, or contract failure under the benchmark's declared baseline policy.

The application shape is deliberately ordinary:

```text
python/
├─ pyproject.toml
├─ src/verification_fixture/
│  ├─ models.py
│  ├─ service.py
│  └─ boundary.py
└─ tests/
   ├─ test_service.py
   └─ test_boundary.py
```

### Mutants

Each mutant starts from the same clean baseline and introduces one root fault.

| ID | Root fault | Responsibility | Required ground truth |
|---|---|---|---|
| PY-SYNTAX-001 | invalid Python syntax | parser/source hygiene | file + exact fault line |
| PY-LINT-001 | deterministic enabled lint violation | lint | rule fixed before execution |
| PY-TYPE-ARG-001 | incompatible argument type | static typing | call site is the root fault |
| PY-TYPE-RETURN-001 | incompatible declared return type | static typing | return expression is the root fault |
| PY-NAME-001 | undefined identifier with valid syntax | static semantics | identifier location |
| PY-ASYNC-001 | declared async misuse | static semantics | exact misuse chosen before execution |
| PY-RUNTIME-001 | externally sourced value violates runtime contract while remaining syntactically/type acceptable before parsing | runtime validation | fixture payload + rejected field |

A downstream cascade caused by one mutant is grouped into that mutant. Ten diagnostics for `PY-SYNTAX-001` still count as one detected root fault.

## 2. TypeScript fixture

### Clean baseline

The baseline is a TypeScript project with:

- `package.json` and lockfile;
- strict `tsconfig.json`;
- typed application code;
- one `unknown` external-data boundary;
- deterministic tests;
- no formatting, enabled lint, compiler, or contract failure under the benchmark policy.

```text
typescript/
├─ package.json
├─ tsconfig.json
├─ src/
│  ├─ service.ts
│  └─ boundary.ts
└─ test/
   ├─ service.test.ts
   └─ boundary.test.ts
```

### Mutants

| ID | Root fault | Responsibility | Required ground truth |
|---|---|---|---|
| TS-SYNTAX-001 | invalid TS syntax | parser/source hygiene | file + exact fault line |
| TS-LINT-001 | deterministic enabled lint violation | lint | rule fixed before execution |
| TS-TYPE-ARG-001 | incompatible argument type | compiler/static typing | call site |
| TS-TYPE-RETURN-001 | incompatible return type | compiler/static typing | return expression |
| TS-PROMISE-001 | promise misuse targeted by a declared type-aware rule | lint/static semantics | misuse site |
| TS-RUNTIME-001 | `unknown` payload compiles but violates runtime schema | runtime validation | payload + rejected field |

Biome and Prettier are compared as formatting authorities, not as type authorities. Oxlint and ESLint/typescript-eslint are compared only for overlapping declared lint responsibilities. `tsc --noEmit` remains a compiler baseline; any Oxlint compiler-diagnostic integration is evaluated separately if still experimental at execution time.

## 3. Workspace fixture

The workspace fixture tests graph correctness, not source diagnostics.

### Known graph

```text
apps/web  -> packages/ui -> packages/core
apps/api  -------------> packages/core
packages/docs            (independent)
```

Every package exposes a deterministic task whose inputs and output checksum are known.

### Scenarios

| ID | Change | Expected affected set / behavior |
|---|---|---|
| WS-AFFECTED-CORE-001 | `packages/core` input | core, ui, web, api downstream tasks affected |
| WS-AFFECTED-UI-001 | `packages/ui` input | ui + web affected; api not affected |
| WS-AFFECTED-DOCS-001 | `packages/docs` input | docs only unless a dependency is explicitly declared |
| WS-CACHE-HIT-001 | identical second execution | cache hit eligible, output identical |
| WS-CACHE-INVALIDATE-001 | declared dependency input changes | dependent cached work invalidated |
| WS-BOUNDARY-001 | forbidden dependency is introduced | boundary policy must reject it where supported |

Nx and Turborepo are evaluated against this same graph. They are not stacked together.

## 4. Mutation generation rule

Mutants must be represented as reproducible patches or generator operations committed before benchmark execution.

A mutant is invalid if it:

- changes more than one root behavior;
- requires a candidate-specific configuration hack to exist;
- breaks dependency installation rather than the intended responsibility;
- relies on a flaky network service;
- cannot be deterministically restored to the clean baseline.

## 5. Candidate configuration rule

For each candidate, configuration proceeds in this order:

1. documented standard configuration;
2. minimum settings required to express the preregistered responsibility;
3. no rule suppression motivated by observed benchmark output.

If a candidate requires benchmark-specific suppression after results are visible, that run is marked contaminated and rerun only under a versioned protocol amendment.

## 6. Real repositories are not fixtures

KAFKA2306 repositories are used only after controlled results exist.

A real repository may reveal compatibility, migration cost, noisy diagnostics, or operational latency. It cannot establish recall because the complete set of defects is unknown.

The former DeepCode experiment is therefore historical evidence only and is not part of the v2 controlled benchmark.