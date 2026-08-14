# Broken-repo precheck discovery run — 2026-08-15

## Status

- Evidence class: observed from GitHub Actions and downloaded run artifacts
- Article state: discovery only; not publication authorization
- Target repository: `KAFKA2306/DeepCode`
- Frozen target SHA: `088059855d2c9187c51d674db02a06f70c37f087`
- Harness PR: https://github.com/KAFKA2306/articles/pull/115
- Workflow run: https://github.com/KAFKA2306/articles/actions/runs/31812751114
- Runner image: Ubuntu 24.04.4 / `ubuntu-24.04` image `20260810.271.1`
- Python: 3.12.13
- uv: 0.12.4

## Question

When a repository is already unhealthy, does adding more current lint/type tools immediately produce more independent actionable defects, or does the order of checks matter more than raw diagnostic count?

## Initial hypothesis

A modern stack such as Ruff + Pyrefly, orchestrated by prek, should expose a broad and mostly complementary failure surface quickly. More diagnostics were expected to mean more independently useful information.

## Discovery result

The raw counts were large, but they were not additive.

| tool | observed version | install_ms | scan_ms | exit | raw diagnostics / output |
|---|---:|---:|---:|---:|---:|
| Ruff | 0.16.3 | 356 | 99 | 1 | 1,076 lint findings |
| Pyrefly | 1.2.0 | 326 | 361 | 1 | 723 findings |
| ty | 0.0.71 | 683 | 264 | 1 | 952 concise output lines |
| prek | 0.4.11 | 293 | 2,326 | 1 | existing pre-commit config |
| pre-commit | 4.6.2 | 1,534 | 8,765 | 1 | same existing config |

Timing is a single cold GitHub Actions observation, not a general performance benchmark. Jobs ran on separate GitHub-hosted runner VMs and the pre-commit/prek scan interval includes hook environment preparation. The useful reproducible facts are the exact commands, target SHA, versions, exit status, diagnostics, and resulting patch.

### Ruff classification

Ruff returned 1,076 findings across 47 files. The largest categories were:

| code | count |
|---|---:|
| `invalid-syntax` | 508 |
| `UP006` | 147 |
| `BLE001` | 143 |
| `I001` | 44 |
| `RUF010` | 42 |
| `UP045` | 33 |
| `UP035` | 29 |
| `S110` | 28 |
| `ASYNC230` | 21 |

The 508 syntax findings were concentrated in 14 files. Examples include missing closing string quotes in `deepcode.py` and `tools/code_implementation_server.py`.

Ruff formatter returned exit code 2 in this discovery run. Per Ruff's official formatter documentation, code 2 means abnormal termination such as invalid configuration, invalid CLI options, or an internal error. Because this repository contains extensive invalid syntax, the formatter result must not be interpreted as a normal "needs formatting" result without separate diagnosis.

Official Ruff docs:
- https://docs.astral.sh/ruff/linter/
- https://docs.astral.sh/ruff/formatter/

### Pyrefly classification

Pyrefly returned exactly 723 errors:

| name | count |
|---|---:|
| `parse-error` | 508 |
| `unknown-name` | 108 |
| `missing-import` | 86 |
| `invalid-syntax` | 12 |
| `unexpected-keyword` | 9 |
| **total** | **723** |

This falsified the naive additive interpretation. In particular, the 508 Pyrefly parse errors numerically match the 508 Ruff `invalid-syntax` findings. The remaining Pyrefly output is also affected by project/import resolution: for example, diagnostics report modules that cannot be found under the zero-dependency discovery environment.

Therefore `1,076 + 723` must not be reported as 1,799 independent defects.

Pyrefly's official documentation also confirms built-in Pydantic v2 support, but Pydantic runtime validation itself was not executed in this run:
- https://pyrefly.org/en/docs/pydantic/

## pre-commit vs prek compatibility observation

Both tools executed the same repository `.pre-commit-config.yaml` against the same frozen target SHA.

Observed timing:

| runner | install_ms | scan_ms | total measured ms |
|---|---:|---:|---:|
| pre-commit 4.6.2 | 1,534 | 8,765 | 10,299 |
| prek 0.4.11 | 293 | 2,326 | 2,619 |

The single-run total ratio is `10,299 / 2,619 ≈ 3.93`. This is an observation from this run only, not a universal speed claim.

More importantly, the generated working-tree patches were byte-identical:

```text
SHA-256(pre-commit.diff.patch)
30275602cf6b35644199d3a7fe949c038a10eaa9e6685074de4f7c8d62b36bf1

SHA-256(prek.diff.patch)
30275602cf6b35644199d3a7fe949c038a10eaa9e6685074de4f7c8d62b36bf1
```

This supports compatibility for this concrete repository/configuration only. prek's current official compatibility documentation states that existing `.pre-commit-config.yaml` files are intended to work unchanged:
- https://prek.j178.dev/compatibility/

## Hypothesis update

For a badly broken repository, diagnostic count is a poor first optimization target.

The more useful precheck order is:

```text
1. parse / syntax
2. formatter + lint after syntax is parseable
3. static type checking after import/dependency context is valid
4. runtime schema / fixture validation at data boundaries
5. tests and heavier CI
```

A type checker can run quickly on broken code, but its output is less actionable while hundreds of parse errors and unresolved imports remain. The precheck system should therefore stage failures and suppress or defer downstream noise rather than presenting every tool's raw count as additive evidence.

## Proposed stack and evidence boundary

### Python

```text
Ruff -> Pyrefly -> Pydantic contract tests
```

- Ruff: **measured here**
- Pyrefly: **measured here**
- Pydantic runtime contract tests: **not measured here**

Pydantic is a runtime validation layer, not another source linter. Official validation reference:
- https://docs.pydantic.dev/2.10/concepts/validation_decorator/

### TypeScript

```text
Biome formatter -> Oxlint -> tsc --noEmit -> Zod contract tests
```

This TypeScript path was **not measured in this run** and must not be presented as an experimental result yet.

Current official references checked on 2026-08-15:
- Biome formatter: https://biomejs.dev/formatter/
- Oxlint type-aware linting: https://oxc.rs/docs/guide/usage/linter/type-aware.html
- Oxlint config reference (`typeCheck` remains experimental): https://oxc.rs/docs/guide/usage/linter/config-file-reference
- TypeScript `noEmit`: https://www.typescriptlang.org/tsconfig/noEmit.html
- Zod parse/safeParse: https://zod.dev/basics
- Zod JSON Schema: https://zod.dev/json-schema

Because Oxlint's `typeCheck` option is still documented as experimental, the proposed production gate keeps `tsc --noEmit` until a separate experiment demonstrates replacement is safe for the target repository.

## Next experiment

1. Repair only the syntax failures in a controlled copy of the frozen target.
2. Re-run Ruff and Pyrefly with exact versions pinned.
3. Install the target's declared dependencies and re-run Pyrefly.
4. Measure how many `unknown-name` / `missing-import` findings survive after environment repair.
5. Add actual Pydantic models/fixtures only where the repository has runtime data boundaries.
6. Select a genuinely unhealthy TypeScript repository and repeat with Biome / Oxlint / `tsc --noEmit` / Zod.
7. Use repeated runs before making general performance claims.

## Publication-safe takeaway

The discovery is not "Ruff finds more errors than Pyrefly" and not "prek is always 4x faster".

The defensible finding is:

> On this broken repository, hundreds of syntax failures propagated into the type-checking surface. A useful precheck system should order gates so that syntax and environment failures are resolved before downstream diagnostic counts are treated as independent defects.
