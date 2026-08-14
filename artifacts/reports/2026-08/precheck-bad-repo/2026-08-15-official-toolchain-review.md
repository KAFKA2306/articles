# 2026 quality toolchain review — official sources only

## Scope

This review separates three layers that are often mixed together:

1. **analysis authorities** — formatter, linter, static type checker, runtime schema validator;
2. **developer-side orchestration** — Git hooks / local precheck runners;
3. **workspace orchestration** — project graph, task graph, affected execution, caching, architectural boundaries.

It is intentionally not a vendor benchmark. The selection criteria are derived from production static-analysis practice and current official tool documentation.

## Professional evaluation model

Google's Tricorder work frames static analysis as an ecosystem and workflow-integration problem, not merely an analyzer-accuracy contest. Google's later report on production static analysis describes tooling used daily by most Google engineers and emphasizes issues that engineers actually choose to fix before check-in. Earlier user-centered research also identifies false positives and warning presentation as barriers to adoption.

Therefore this review uses these criteria:

- **semantic authority** — which tool is the final arbiter for a concern;
- **signal density** — how much output is independently actionable rather than duplicated/derived noise;
- **feedback latency** — whether the check can live in editor/save/commit loops without creating context switching;
- **trust boundary coverage** — whether untrusted runtime data is validated before entering application logic;
- **graph awareness** — whether workspace-level dependency/task relationships can reduce work or enforce architecture;
- **migration/maintenance cost** — whether adding the tool reduces or increases long-term policy duplication;
- **stability boundary** — stable vs beta/experimental features must not be treated as equivalent authorities.

Primary references:

- Google Tricorder: https://research.google/pubs/tricorder-building-a-program-analysis-ecosystem/
- Lessons from Building Static Analysis Tools at Google: https://research.google/pubs/lessons-from-building-static-analysis-tools-at-google/
- Why Don't Software Developers Use Static Analysis Tools to Find Bugs?: https://research.google/pubs/why-dont-software-developers-use-static-analysis-tools-to-find-bugs/

## Layer 1 — analysis authorities

### Python formatter/linter: Ruff

Official Ruff docs describe one CLI providing both linter and formatter, with more than 900 first-party lint rules and drop-in parity goals covering major Flake8/isort/Black workflows. The formatter explicitly aims at a unified toolchain and the linter is intended to replace a broad collection of Python lint utilities.

Decision: **Ruff is the default Python format/lint authority for greenfield repositories.**

Sources:
- https://docs.astral.sh/ruff/
- https://docs.astral.sh/ruff/linter/
- https://docs.astral.sh/ruff/formatter/

### Python static type authority: Pyrefly, with ty as challenger

Pyrefly reached stable v1 on 2026-05-12 and its maintainers explicitly state that it is ready for production use.

Astral's ty is still Beta as of the current official documentation/blog. Astral recommends it to motivated production users and its incremental architecture is compelling, but the project explicitly states that Stable remains a future milestone.

Decision: **Pyrefly is the conservative blocking authority today; ty remains a high-priority challenger/shadow evaluation target.** Do not permanently run two blocking type authorities unless a migration experiment requires it.

Sources:
- https://pyrefly.org/blog/v1.0/
- https://docs.astral.sh/ty/
- https://astral.sh/blog/ty

### Python runtime contract: Pydantic

Pydantic validates runtime values using declared schemas/types. This is a different failure domain from static type checking. `validate_call` also makes explicit that runtime validation has a cost and is not a substitute for a strongly typed language.

Decision: **Use Pydantic at untrusted/runtime boundaries, not as a repository-wide linter.**

Source:
- https://docs.pydantic.dev/2.10/concepts/validation_decorator/

### TypeScript formatter: Biome

Biome's formatter is intentionally opinionated and deliberately limits formatting options to avoid team bikeshedding. Biome also has a substantial linter (518 rules in current docs), monorepo support, and a CI-specific command.

Decision: **Use Biome as formatter authority when Oxlint is selected as lint authority.** This is a deliberate authority split, not a claim that Biome's linter is weak.

Sources:
- https://biomejs.dev/formatter/
- https://biomejs.dev/linter/
- https://biomejs.dev/guides/big-projects/
- https://biomejs.dev/recipes/continuous-integration/

### TypeScript linter: Oxlint

Oxlint's type-aware linting became stable in July 2026 and currently supports 59 of 61 type-aware typescript-eslint rules. The type-aware engine uses TypeScript 7 / typescript-go semantics.

However, the current configuration reference still labels `typeCheck` as experimental even though the type-aware guide shows that `--type-check` can report compiler diagnostics alongside lint output and can replace a separate `tsc --noEmit` step.

Decision: **Oxlint is the preferred dedicated JS/TS lint authority for greenfield modern-TypeScript repositories. Keep `tsc --noEmit` as the blocking compiler/type authority until Oxlint `typeCheck` leaves experimental status or a repository-specific parity experiment justifies migration.**

Sources:
- https://oxc.rs/docs/guide/usage/linter/
- https://oxc.rs/docs/guide/usage/linter/type-aware.html
- https://oxc.rs/docs/guide/usage/linter/config-file-reference
- https://oxc.rs/blog/2026-07-22-type-aware-linting-stable.html

### TypeScript type authority: tsc --noEmit

TypeScript's official `noEmit` option explicitly supports using the TypeScript compiler as a source-code type checker while another tool handles code generation.

Decision: **Retain `tsc --noEmit` as the conservative compiler authority in 2026-08.**

Source:
- https://www.typescriptlang.org/tsconfig/noEmit.html

### TypeScript runtime contract: Zod

Zod's `parse`/`safeParse` validate unknown runtime inputs and produce inferred static types from the same schema.

Decision: **Use Zod at untrusted boundaries; do not count Zod validation failures as the same category as lint/type diagnostics.**

Source:
- https://zod.dev/basics

## Layer 2 — developer-side orchestration

### prek

Current prek documentation states that existing `.pre-commit-config.yaml` files work unchanged for common workflows and that 0.4.5 completed language coverage parity with pre-commit. The compatibility page also documents prek-only extensions and explicitly recommends staying with YAML and avoiding those extensions when strict upstream portability matters.

In the DeepCode frozen-fixture discovery run, pre-commit 4.6.2 and prek 0.4.11 produced byte-identical working-tree patches. Their single-run timing differed substantially, but separate runner VMs mean the timing cannot be generalized as a universal speed ratio.

Decision: **prek is a strong local hook-runner replacement candidate, but quality policy must live in repository commands/configs/CI rather than in a prek-specific architecture.**

Sources:
- https://prek.j178.dev/compatibility/
- https://prek.j178.dev/changelog/
- https://prek.j178.dev/diff/
- discovery run: https://github.com/KAFKA2306/articles/actions/runs/31812751114

## Layer 3 — workspace orchestration

### Nx

Nx models both a Project Graph and a Task Graph. Official docs use the graph to determine execution order, affected projects, cache behavior, and workspace analysis. `nx affected` computes the minimum set of projects affected by a change. Nx also provides local/remote caching and architectural dependency constraints via project tags.

Important boundary detail: for JavaScript/TypeScript, the open-source module-boundary mechanism is an ESLint rule (`@nx/enforce-module-boundaries`). Language-agnostic graph-level Conformance is an Nx Powerpack/Enterprise capability. Therefore a stack that removes ESLint entirely must account for this integration boundary rather than assuming Nx architecture enforcement automatically comes with Oxlint.

Decision: **Nx is the stronger choice when the primary problem is large-workspace governance: project graph, affected execution, architectural policy, multi-project CI, and heterogeneous workspace orchestration.**

Sources:
- https://nx.dev/docs/features/explore-graph
- https://nx.dev/docs/features/ci-features/affected
- https://nx.dev/docs/features/cache-task-results
- https://nx.dev/docs/features/enforce-module-boundaries

### Turborepo

Turborepo builds package and task DAGs from workspace/package configuration, caches deterministic task outputs/logs, and supports remote caching. It is explicitly positioned by Vercel as a high-performance build system for JavaScript/TypeScript codebases.

Turborepo also has `turbo boundaries`, including package breakout, undeclared dependency and tag rules, but the official reference currently marks Boundaries as experimental.

Decision: **Turborepo is the stronger default when the primary problem is low-friction JS/TS monorepo task execution, caching and deployment integration. Do not treat its current experimental boundaries as equivalent to mature architecture governance.**

Sources:
- https://turborepo.dev/docs/core-concepts/package-and-task-graph
- https://turborepo.dev/docs/crafting-your-repository/caching
- https://turborepo.dev/docs/reference/boundaries
- https://vercel.com/docs/monorepos/turborepo

## Resulting 2026-08 reference architecture

```text
Repository / workspace policy
        │
        ├─ monorepo? ── no ─────────────── direct CI tasks
        │
        └─ yes
            ├─ governance/heterogeneous ── Nx
            └─ lean JS/TS execution ────── Turborepo
                    │
                    ▼
Language authorities
  Python:     Ruff → Pyrefly → Pydantic at runtime boundaries
  TypeScript: Biome(format) → Oxlint → tsc --noEmit → Zod at runtime boundaries
                    │
                    ▼
Developer commit trigger
  prek (replaceable; not the policy authority)
```

The architecture deliberately does **not** select both Nx and Turborepo for the same workspace task graph. It also does not require Nx/Turborepo for a small single-project repository.

## Evidence boundary

Directly measured in the current broken-repository experiment:
- Ruff 0.16.3
- Pyrefly 1.2.0
- ty 0.0.71
- prek 0.4.11
- pre-commit 4.6.2

Official-source architecture review only, not yet measured on the frozen fixture:
- Pydantic
- Biome
- Oxlint
- `tsc --noEmit`
- Zod
- Nx
- Turborepo

A future article revision must not turn official capability claims into local empirical claims without a separate fixture/run.