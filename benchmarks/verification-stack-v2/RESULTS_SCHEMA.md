# Verification Stack v2 — Results Schema and Publication Gate

Status: **PREREGISTERED BEFORE COMPARISON RESULTS**

This file defines what evidence must exist before a recommendation or article may be written.

## 1. Per-candidate result record

Every candidate run must record at least:

```yaml
candidate: <tool>
version: <exact version>
responsibility: <declared layer>
runner:
  os: <image>
  cpu: <reported runner CPU where available>
  runtime: <Python/Node/etc exact version>
configuration:
  files: []
  non_default_settings: []
clean_baseline:
  exit_code: 0
  blocking_false_positives: 0
mutants:
  - id: <mutant id>
    detected: true|false
    first_actionable_root_cause: true|false
    root_cause_location: <file:line or graph edge>
    raw_diagnostic_count: <integer>
    grouped_root_fault_count: <integer>
latency_ms:
  install: <value>
  cold_full: []
  warm_full: []
  incremental: []
operational:
  config_files_added: <integer>
  config_lines_added: <integer>
  migration_notes: []
  incompatible_features: []
```

Raw logs and machine-readable outputs must be retained as artifacts. Markdown summaries are secondary evidence.

## 2. Correctness first

No speed comparison is allowed to promote a candidate that fails a critical in-scope mutant detected by another candidate in the same responsibility, unless the missed case is explicitly outside that candidate's documented scope.

A candidate is not a default authority if the clean baseline is blocked by a false positive under the tested standard configuration.

## 3. Root-cause grouping

Results are counted by preregistered root fault, not by emitted message count.

For one mutant:

```text
1 root fault
→ 1 diagnostic   = 1 detected fault
→ 20 diagnostics = still 1 detected fault
```

Downstream parse/type/lint cascades do not create additional ground-truth defects.

`raw_diagnostic_count` is retained only as a noise/UX variable.

## 4. Latency methodology

For fast checks:

- use at least 10 measured repetitions after setup;
- report median;
- report dispersion (p25/p75 or equivalent);
- separate install, cold full-project, warm full-project, and incremental/change-local latency;
- paired competitors must run on the same runner image and equivalent checkout state whenever technically possible.

A single GitHub Actions job duration is not accepted as a performance conclusion.

## 5. Workspace correctness

Nx and Turborepo must be scored on:

- exact affected-set match against the known graph;
- no omitted required downstream task;
- no stale output after declared input changes;
- deterministic cache hit on an unchanged repeat where cacheability is expected;
- task ordering correctness;
- boundary-policy behavior only for capabilities documented by the product.

A faster but incorrect affected set or invalid cache result is a correctness failure, not a performance win.

## 6. Hook runner parity

For prek vs pre-commit, the benchmark records:

- hook coverage;
- exit semantics;
- file mutation patch SHA-256;
- staged-file behavior;
- cold setup time;
- repeated execution latency.

A migration recommendation requires semantic parity for the tested hook corpus. Speed alone is insufficient.

## 7. Runtime validator evaluation

Pydantic and Zod are not compared against Ruff/Oxlint/type checkers.

They are evaluated on external payload mutants that static checking cannot prove safe because the value originates outside the typed program.

Required observations:

- invalid payload rejected;
- valid payload accepted;
- error location/actionability;
- validation runtime;
- schema duplication/maintenance cost.

An unvalidated control path is retained to demonstrate what static verification cannot establish at the trust boundary.

## 8. Decision format

The final comparison must be Pareto-oriented rather than collapsed into a made-up weighted score.

For each responsibility, report candidates along these axes:

```text
correctness / recall
blocking false positives
root-cause quality
incremental latency
cold latency
configuration burden
migration burden
maturity / experimental status
```

A recommendation may state different winners for different operating conditions.

Examples of valid conclusions:

- best default for greenfield;
- best drop-in replacement for an incumbent stack;
- fastest candidate that preserves the required correctness envelope;
- promising challenger, but not yet default authority;
- workspace tool appropriate only once graph/caching complexity exists.

## 9. Article publication gate

No article candidate is created until all of the following are true:

1. controlled fixture baseline passes;
2. mutant manifest is committed and immutable for the run;
3. exact candidate versions are pinned;
4. raw controlled results exist;
5. real-repository sample is frozen before its candidate outputs are reviewed;
6. external-validity results exist;
7. claims are separated into observed fact, inference, and recommendation;
8. at least one non-obvious finding changes a professional engineering decision.

If the result is merely "tool A is a little faster than tool B," the experiment may be published as data but **must not be promoted into a standalone article**.

## 10. Prohibited claims

The eventual article must not claim:

- universal `x times faster` from one CI run;
- total defects by adding diagnostics from overlapping analyzers;
- runtime validator superiority based on static-checker tests;
- Nx/Turborepo superiority from a single-package repository;
- production readiness solely from vendor claims;
- a default winner that failed a preregistered critical correctness condition.

The objective is not to crown the newest tool. The objective is to identify the smallest set of authorities that gives trustworthy feedback under a measured latency and maintenance budget.