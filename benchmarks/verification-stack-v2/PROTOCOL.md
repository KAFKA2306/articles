# Verification Stack v2 — Preregistered Protocol

Status: **PREREGISTERED / NO COMPARISON RESULTS YET**

This document defines the experiment before candidate tools are run. Results must not change the metrics, defect corpus, disqualifiers, or real-repository selection rules below. Any protocol amendment after data collection starts must be recorded as a new version and the affected results rerun.

## 1. Research question

For modern Python, TypeScript, and monorepo development, which verification architecture returns the most **trustworthy, actionable defect signal within a practical feedback budget**?

The experiment does not ask which product has the most rules or the best vendor microbenchmark. It asks whether a team can trust a tool as an authority for a specific responsibility while preserving fast developer feedback.

## 2. Null hypothesis

After controlling for known ground truth, false-positive noise, setup cost, and repeated timing, newer high-performance tools do **not** materially improve the engineering trade-off over established incumbents.

A candidate must earn its default position; novelty is not evidence.

## 3. Experimental structure

The study has two stages.

### Stage A — controlled ground-truth benchmark

Purpose: measure detection and noise against defects whose intended ground truth is known before any tool is run.

Three independent fixtures are used:

1. `python/` — Python source, static typing, and runtime-boundary faults.
2. `typescript/` — TypeScript source, lint/type semantics, and runtime-boundary faults.
3. `workspace/` — a small monorepo with an explicit dependency graph for affected-set and cache-correctness tests.

Each mutant introduces **one root fault only**. Mutants are evaluated independently from the same clean baseline to prevent cascading defects from inflating diagnostic counts.

### Stage B — real-repository external validity

Purpose: test whether conclusions from Stage A remain operationally plausible on real public codebases.

Real repositories are not used to estimate recall because their complete defect ground truth is unknown. They are used only for:

- execution compatibility;
- actionable/noisy output review;
- cold and warm latency;
- configuration/migration friction;
- changed-file and project-scope behavior;
- patch/behavior parity where applicable.

## 4. Core measurement principle

**Raw diagnostic count is not a quality metric.**

A tool that emits ten messages for one root cause has not found ten independent defects. Results are grouped by the preregistered root fault and responsibility.

The primary correctness quantities are:

- in-scope mutant detected: yes/no;
- clean baseline incorrectly blocked: yes/no;
- first actionable diagnostic points to the root fault: yes/no;
- exclusive actionable information after root-cause grouping.

## 5. Responsibility boundaries

Tools are compared only inside a responsibility they claim to serve.

### Python

- format / source lint authority
- static type authority
- runtime input validation

### TypeScript

- formatting authority
- source / semantic lint authority
- compiler / static type authority
- runtime input validation

### Workspace

- task/project graph construction
- affected-set correctness
- task ordering
- local/remote cache correctness
- architecture-boundary enforcement where supported

### Local orchestration

- hook compatibility
- trigger overhead
- mutation/patch parity

Runtime validators are **not** ranked against linters. Workspace orchestrators are **not** ranked against compilers.

## 6. Candidate sets

Exact versions will be pinned in the first implementation commit after this protocol. Version choice must use current stable releases unless the experiment explicitly tests a Beta/Experimental challenger.

### Python source hygiene

- Ruff
- established incumbent stack sufficient to represent separate formatter/lint authorities (Black + isort + Flake8 family)

### Python static typing

- Pyrefly
- ty
- Pyright
- mypy

### Python runtime boundary

- Pydantic
- unvalidated control path

### TypeScript formatting

- Biome formatter
- Prettier

### TypeScript lint

- Oxlint
- ESLint + typescript-eslint

### TypeScript static type

- `tsc --noEmit`
- Oxlint compiler-diagnostic integration only as an explicitly Experimental challenger if the current official documentation still marks it Experimental at execution time

### TypeScript runtime boundary

- Zod
- unvalidated control path

### Hook orchestration

- prek
- pre-commit

### Workspace orchestration

- Nx
- Turborepo

Nx and Turborepo are evaluated as competing workspace authorities. The study will not recommend running both as parallel task-graph authorities in one workspace.

## 7. Ground-truth defect corpus

Every mutant must have an ID, responsibility, expected detecting authority, exact source diff, and expected non-detecting boundaries committed before the comparison workflow is enabled.

### Python mutants

Minimum corpus:

- `PY-SYNTAX-001` — parse/syntax failure.
- `PY-LINT-001` — deterministic source-quality defect in the selected stable lint rule set.
- `PY-TYPE-ARG-001` — incompatible function argument type.
- `PY-TYPE-RETURN-001` — incompatible declared return type.
- `PY-NAME-001` — undefined name with valid syntax.
- `PY-ASYNC-001` — async misuse that is in scope for at least one declared static authority.
- `PY-RUNTIME-001` — syntactically and statically acceptable external payload whose value violates a Pydantic runtime contract.

### TypeScript mutants

Minimum corpus:

- `TS-SYNTAX-001` — parse/syntax failure.
- `TS-LINT-001` — deterministic source lint defect.
- `TS-TYPE-ARG-001` — incompatible function argument type.
- `TS-TYPE-RETURN-001` — incompatible declared return type.
- `TS-PROMISE-001` — promise misuse targeted by a type-aware lint rule.
- `TS-RUNTIME-001` — `unknown` external payload that passes compilation but violates a Zod runtime schema.

### Workspace mutants

Clean graph:

```text
apps/web  -> packages/ui -> packages/core
apps/api  -------------> packages/core
packages/docs   (independent)
```

Minimum mutations / change scenarios:

- `WS-AFFECTED-CORE-001` — change `packages/core`; expected affected tasks include all declared dependents.
- `WS-AFFECTED-UI-001` — change `packages/ui`; `apps/web` is affected, `apps/api` is not.
- `WS-AFFECTED-DOCS-001` — change independent docs package; app tasks must not be marked affected unless configuration explicitly declares such a dependency.
- `WS-CACHE-HIT-001` — identical second execution must be eligible for a cache hit.
- `WS-CACHE-INVALIDATE-001` — dependency input change must invalidate downstream cached work.
- `WS-BOUNDARY-001` — deliberately forbidden package dependency; evaluate boundary enforcement only where the product claims support.

## 8. Clean-baseline requirement

Before mutant measurements, every controlled fixture must pass its intended baseline checks.

Any tool that emits a **blocking false positive on the clean baseline** is disqualified from becoming the default authority under the tested configuration until the cause is corrected without suppressing a required mutant.

Warnings that are explicitly non-blocking are recorded separately.

## 9. Primary metrics

### 9.1 Correctness

For each responsibility:

- `critical_mutant_recall = detected critical in-scope mutants / critical in-scope mutants`
- `all_mutant_recall = detected in-scope mutants / all in-scope mutants`
- `clean_blocking_false_positives`
- `root_cause_first`: whether the first actionable diagnostic identifies the seeded root fault or its exact location/class
- `exclusive_actionable_yield`: root faults uniquely surfaced beyond earlier authorities in the intended verification path

The article must not sum raw diagnostics across tools.

### 9.2 Feedback latency

Measure separately:

- install/setup time;
- cold full-project check;
- warm full-project check;
- incremental check after one relevant file edit;
- time to first actionable diagnostic when observable.

Timing summaries use median and dispersion, not one hosted-run sample.

### 9.3 Operational cost

Record:

- direct configuration lines/files added;
- required runtime/toolchain dependencies;
- migration edits from the clean fixture;
- cache footprint when measurable;
- peak RSS when the harness can capture it reliably;
- unsupported or Experimental features needed for the claimed role.

### 9.4 Workspace correctness

For Nx/Turborepo:

- exact affected-set precision/recall against the known graph;
- cache hit on identical rerun;
- mandatory invalidation after relevant dependency changes;
- absence of invalidation after unrelated changes where expected;
- architecture-boundary detection where officially supported.

A faster wrong affected set or stale cache is a correctness failure, not a performance win.

## 10. Timing protocol

1. Pin exact versions and runner image.
2. Separate package/tool installation from analysis execution.
3. Compare competing tools in the **same GitHub Actions job/runner** when environmental parity is required.
4. Randomize or alternate tool order across repetitions where practical to reduce ordering bias.
5. Use at least 10 measured repetitions for fast checker timing, preceded by warmups for warm-mode measurements.
6. Cold-mode runs clear the relevant tool cache intentionally; warm/incremental runs retain it intentionally.
7. Report medians plus a dispersion statistic; do not market a single-run ratio.
8. Do not compare absolute times from different hosted runner VMs as if they were controlled pairs.

## 11. Decision policy

There is **no single weighted total score**. Arbitrary weights would hide engineering trade-offs.

### Default-authority disqualifiers

A candidate cannot be recommended as the default authority for a responsibility if, under the preregistered fixture/configuration, it:

- misses a critical in-scope mutant;
- produces a blocking false positive on the clean baseline that cannot be corrected without suppressing required coverage;
- returns an incorrect affected set or stale cache result for a workspace correctness case;
- requires an Experimental semantic feature for the claimed default-authority role, unless the conclusion is explicitly limited to experimental adoption;
- cannot run reproducibly under the pinned environment.

### Selection among survivors

Survivors are compared as a Pareto set across:

- correctness and actionable signal;
- feedback latency;
- incremental behavior;
- operational/configuration cost;
- compatibility/migration cost;
- stability/maturity boundary.

The recommendation may legitimately be conditional rather than naming one universal winner.

## 12. Real-repository sampling rule

Repository selection occurs **after this protocol commit but before candidate-tool outputs on those repositories are inspected**.

Public, non-archived repositories are eligible. Selection is stratified by workload, not by whether a known tool already succeeds or fails.

### Python stratum

Choose one active public repository that has:

- a Python dependency/config manifest;
- non-trivial Python source;
- automated CI or tests;
- no requirement for private credentials merely to perform static checks.

### TypeScript stratum

Choose one active public repository that has:

- `package.json` and `tsconfig.json`;
- non-trivial TS source;
- automated CI or tests;
- installable public dependencies.

### Workspace stratum

Do not force-fit an existing repository if it does not already present a clean monorepo graph question. The controlled workspace fixture is the primary evidence for Nx/Turborepo correctness. A real monorepo may be added only if one satisfies the same objective eligibility rule without being selected for a known favorable outcome.

If multiple eligible repositories exist, freeze the candidate inventory and use a deterministic selection rule (for example repository name hash order) before tool results are fetched.

## 13. Real-repository interpretation boundary

On real repositories, report:

- whether the tool runs;
- diagnostic classes and representative actionable findings;
- overlap after root-cause grouping;
- latency under the controlled timing harness;
- migration/configuration changes required.

Do **not** claim recall, false-positive rate, or total defect count from an unknown-ground-truth repository.

## 14. Hook-runner parity protocol

For prek vs pre-commit, use one frozen hook configuration and one frozen working tree.

Compare:

- hook set actually executed;
- exit semantics;
- resulting Git diff bytes / SHA-256;
- files changed;
- cold environment setup time;
- warm rerun time.

Patch identity is stronger compatibility evidence than matching output-line counts.

## 15. Evidence and publication gates

The following order is mandatory:

```text
protocol committed
  -> fixture + mutant manifest committed
  -> harness implementation reviewed
  -> controlled benchmark executed
  -> real-repo sample frozen
  -> external-validity run executed
  -> raw artifacts classified
  -> only then decide whether an article-worthy finding exists
```

No article candidate is created merely because the benchmark exists.

A publishable article requires a non-obvious result that survives both evidence classification and the repository's existing article quality contract.

## 16. Protocol change policy

Once the first comparison result is collected, changes to any of the following require a protocol revision and rerun of affected comparisons:

- mutant corpus;
- primary metrics;
- disqualifiers;
- timing repetitions/warmups;
- real-repository eligibility or selection rule;
- responsibility boundaries.

This prevents post-hoc optimization around a preferred tool.
