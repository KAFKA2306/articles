# Verification Stack v2 — Autonomous Execution Contract

The autonomous controller may advance this benchmark only through preregistered gates. It is an executor, not an editor of the hypothesis.

## State machine

```text
design_frozen
  -> fixtures_frozen
  -> harness_ready
  -> controlled_results_ready
  -> real_repo_sample_frozen
  -> external_validity_ready
  -> evidence_classified
  -> article_gate_ready
```

The controller must stop at the first unmet gate. A blocked gate is a valid outcome.

## Non-negotiable constraints

- Never change `PROTOCOL.md`, `FIXTURE_DESIGN.md`, or `RESULTS_SCHEMA.md` because a candidate performs poorly.
- Never treat raw diagnostic counts as defect counts.
- Never choose a real repository after reading candidate output.
- Never convert timing wins into correctness wins.
- Never publish an article. `publication_authorized` remains `false` unless an explicit human task changes it.
- Never create a second canonical branch or PR for the same benchmark.
- Never silently suppress a required mutant.

## Autonomous trigger

`.github/workflows/verification-stack-v2-autonomous.yml` runs the deterministic controller on pushes to the canonical experiment branch and on manual dispatch. The controller advances through all currently satisfied gates, writes the machine-readable state, and stops when the next prerequisite is absent.

A GitHub Actions run succeeding means the controller itself behaved correctly. It does not mean any candidate tool won.

## Fixed point

Autonomous execution stops when either:

1. the next preregistered gate is not satisfied; or
2. `article_gate_ready` is reached.

At `article_gate_ready`, evidence may support drafting a candidate article, but publication still requires a separate explicit authorization.