# Verification Stack v2 — Autonomous Execution Contract

The autonomous controller exists to produce the strongest evidence-backed article this investigation can support. **Benchmark completion is an intermediate state, not the objective.**

The controller may execute and extend the investigation, but it may not change a preregistered metric or defect after seeing results merely to make a preferred tool look better.

## State machine

```text
design_frozen
  -> fixtures_frozen
  -> harness_ready
  -> controlled_results_ready
  -> real_repo_sample_frozen
  -> external_validity_ready
  -> evidence_classified
  -> story_candidates_ready
  -> article_candidate_ready OR no_article
```

The current phase is stored in `state.json`. The controller advances only through explicit gates.

## Terminal objective

Use `EDITORIAL_GOAL.md` as the terminal contract.

A successful run is not `all tools executed`. A successful investigation ends in one of two states:

1. **article_candidate_ready** — one decision-changing, non-obvious proposition survives the evidence gates and a candidate article can be written around it; or
2. **no_article** — the evidence is useful but does not justify a strong article.

Never manufacture a story to avoid `no_article`.

## Evidence autonomy

The controller may autonomously:

- implement already-frozen fixtures and mutant generators;
- build neutral result collectors;
- pin current tool versions with provenance;
- run clean baselines and controlled mutants;
- rerun contaminated/flaky measurements according to the protocol;
- freeze the real-repository sample using the preregistered deterministic selection rule;
- execute external-validity checks;
- classify evidence against `RESULTS_SCHEMA.md`;
- generate multiple competing story propositions after evidence classification;
- add a versioned protocol amendment when the existing experiment cannot answer an important newly exposed question.

A protocol amendment must state the reason before collecting the new data. Old results remain visible and are not rewritten.

## Non-negotiable constraints

- Never change `PROTOCOL.md`, `FIXTURE_DESIGN.md`, or `RESULTS_SCHEMA.md` because a candidate performs poorly.
- Never treat raw diagnostic counts as defect counts.
- Never choose a real repository after reading candidate output.
- Never convert timing wins into correctness wins.
- Never use vendor positioning as the article's discovery.
- Never choose a title before the evidence-classification phase.
- Never create a product-list article when no single proposition passes `EDITORIAL_GOAL.md`.
- Never publish an article. Publication remains a separate explicit authorization.
- Never create a second canonical branch or PR for the same investigation.
- Never silently suppress a required mutant.

## Editorial search loop

After controlled and external-validity evidence exists:

```text
classify evidence
  -> generate >= 3 competing propositions
  -> try to falsify each proposition with the same evidence
  -> reject generic/vendor-obvious propositions
  -> test decision impact
  -> select one surviving proposition
  -> draft one article around that proposition
```

If all propositions fail, the controller may propose a versioned follow-up experiment only when a precise unresolved question would materially change the reader's decision. Otherwise terminate as `no_article`.

## Autonomous trigger

The repository workflow may run the deterministic controller on the canonical experiment branch and on manual dispatch. It should execute the next eligible phase and stop at a missing prerequisite rather than bypassing it.

A green GitHub Actions run means the controller obeyed its contract. It does not mean a candidate tool won or an article is publishable.

## Fixed point

Stop when either `article_candidate_ready` or `no_article` is reached.

Even at `article_candidate_ready`, keep the candidate unpublished until explicit publication authorization exists.