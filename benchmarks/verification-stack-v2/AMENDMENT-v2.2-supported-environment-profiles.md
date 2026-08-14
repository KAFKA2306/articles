# Verification Stack v2.2 — Supported environment profiles

Status: **PREREGISTERED BEFORE ANY CANDIDATE COMPARISON RESULT**

Date: 2026-08-15

At amendment time the machine state remained `harness_ready` with `comparison_started: false`. The first controlled workflow attempt failed during dependency installation before any candidate command executed.

## Observed setup incompatibility

Installing all TypeScript candidates into one `node_modules` failed dependency resolution:

- the frozen compiler baseline is TypeScript 7.0.2;
- typescript-eslint 8.65.0 officially supports TypeScript `>=4.8.4 <6.1.0`;
- Oxlint type-aware officially requires TypeScript 7.0+ and its tsgolint release tracks TypeScript 7.0.2.

Forcing the dependency tree with `--force` or `--legacy-peer-deps` would test an unsupported typescript-eslint environment and bias the comparison.

## Amendment

Candidate execution is split into official-support profiles:

### TS7 profile

Used for:

- TypeScript compiler baseline (`tsc --noEmit`);
- Oxlint type-aware;
- Oxlint experimental `--type-check` challenger;
- Biome / Prettier / Zod where their responsibility does not require downgrading TypeScript;
- workspace tools.

Pinned TypeScript: 7.0.2.

### typescript-eslint profile

Used for ESLint + typescript-eslint type-aware linting.

Pinned TypeScript: 6.0.3, the latest stable TypeScript release inside the current official `<6.1.0` support envelope at the time of this amendment.

The source fixture and lint mutant remain identical. Only the compiler-generation dependency required by each supported toolchain differs.

## Interpretation rule

This is not treated as a benchmark win or loss by itself. It is recorded as an **ecosystem compatibility constraint**.

Latency measured across these profiles is operational latency for a supported deployment path, not a pure engine microbenchmark under an identical compiler implementation.

A future typescript-eslint release that officially supports TypeScript 7 would require a versioned rerun; historical results must not be silently reinterpreted.

## Invalidated attempt

Controlled workflow attempt #1 is setup-invalid and contributes no candidate result. No source/type/lint/formatter/runtime/workspace candidate executed in that attempt.
