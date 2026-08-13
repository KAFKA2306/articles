# Articles Agent Operating Contract

This repository is the canonical system for discovering, drafting, reviewing, selecting, and publishing KAFKA2306 technical articles.

`README.md` explains the system to humans. `pipeline/contracts/article.md` defines the editorial contract. `AGENTS.md` defines how an autonomous agent may operate the repository safely and decide when work is complete.

## 1. Mission

Produce evidence-backed articles that contain one verifiable, non-obvious discovery.

Do not optimize for article count. Do not publish because a schedule exists. A month with zero publishable articles is valid.

The canonical loop is:

```text
public/private-safe idea seed
  -> public evidence
  -> one question
  -> one hypothesis
  -> one surprising finding
  -> candidate draft
  -> source gate
  -> technical review
  -> editorial review
  -> bounded revision
  -> selection
  -> publication only when explicitly eligible
  -> post-publication verification
```

## 2. Source-of-Truth Precedence

When sources disagree, use this order:

1. current public primary-source evidence and directly fetched GitHub evidence;
2. current repository code, config, schemas, and audit logic;
3. `pipeline/contracts/article.md`;
4. deterministic tests, reports, source-gate results, CI, and exact-head artifacts;
5. `README.md`, architecture/editorial docs, and current ADR-like documents;
6. Issue/PR prose and historical reports;
7. memory or inference.

Never let stale article prose override current evidence.

A generated sentence is not evidence. A model score is not evidence. A branch name is not evidence. An unverified URL is not evidence.

## 3. Claim Provenance

Every material claim must be treated as one of:

- **VERIFIED** — directly supported by fetched public evidence, repository state, a deterministic command, or CI result.
- **OBSERVED** — explicitly provided by the user or task contract.
- **INFERRED** — a conclusion derived from evidence; identify the inference boundary.
- **UNVERIFIED** — not checked; never present as fact.
- **FABRICATED** — forbidden.

For numerical claims, preserve target, period, unit, comparison basis, and what the number does not prove.

For causal claims, distinguish correlation, mechanism evidence, implementation dependency, and speculation.

## 4. Privacy Boundary

Graphiti and other private context are idea sources only.

Never commit or publish:

- private diary text;
- personal identifiers that are not already intentionally public;
- tax, asset, health, travel, private relationship, or employer-internal information;
- unpublished project details;
- credentials, tokens, private URLs, local absolute paths, or hidden metadata.

A private seed may suggest a topic, but every public article claim must be re-grounded in public evidence.

`python -m pipeline.audit` is a mandatory privacy/repository gate when its scope is affected.

## 5. Canonical State Boundaries

Repository state is intentionally separated:

- `artifacts/candidates/YYYY-MM/` — unpublished, public-safe article candidates;
- `artifacts/reports/YYYY-MM/` — review/source evidence;
- `pipeline/` — generation, review, selection, and audit implementation;
- `pipeline/contracts/article.md` — editorial contract;
- `articles/` — published article files only;
- `images/` / `demos/` — supporting assets only when they improve the article and remain independently verifiable.

Do not treat a candidate as published because it was merged to `main`.

`published: false` is a hard state boundary. Merging a candidate with `published: false` does not authorize publication.

Do not copy candidate files into `articles/` unless the publication contract is explicitly satisfied.

## 6. Canonical Workline Rule

Before creating a branch or PR:

1. inspect open PRs and relevant branches;
2. continue an existing canonical workline for the same article/change if one exists;
3. do not create a competing implementation or duplicate article candidate;
4. use one short-lived branch and one PR for pipeline/CI/contract changes;
5. use direct-to-main only when the repository's current branch policy explicitly permits it and independent review is not required.

Different article candidates may have separate PRs. The duplicate prohibition applies to the same outcome, not unrelated articles.

When an older workline is superseded, close or consolidate it rather than leaving two canonical paths.

## 7. Contract Before Change

For non-trivial work, define:

- **Contract** — what must change and what must remain unchanged;
- **Outcome** — observable final state;
- **Acceptance Criteria** — deterministic checks that prove the outcome;
- **Evidence** — files, fetched URLs, reports, tests, CI runs, or publication receipts;
- **Stopping Condition** — the fixed point after which additional edits are scope expansion.

Do not broaden an article because adjacent facts are interesting.

## 8. Article Selection Rule

One article should contain one discovery.

Reject or return to topic selection when the candidate is only:

- a tool/library explanation;
- a best-practice summary;
- a configuration mistake with no broader finding;
- a URL/error cleanup story;
- a repository inventory with no falsified hypothesis;
- a collection of unrelated impressive results;
- a generic AI-generated tutorial.

A weak question must not be rescued by more prose, more citations, more diagrams, or stronger rhetoric.

## 9. Evidence and Source Gate

Before an article can be considered publishable:

- verify source URLs by actual HTTP retrieval when the pipeline contract requires it;
- prefer primary/official sources for external claims;
- preserve at least the source minimums defined by the current article contract;
- use concrete KAFKA2306 GitHub evidence for repository-specific claims;
- do not quote or paraphrase beyond what the source supports;
- do not turn an implementation example into a universal claim without a separate justification;
- distinguish direct measurement from inferred interpretation.

If a required source is inaccessible, stale, contradictory, or ambiguous, fail closed or weaken/remove the claim.

## 10. Editorial Contract

Follow `pipeline/contracts/article.md` for the current editorial thresholds and title/story rules.

Core invariant:

```text
scene / number / failure
  -> unresolved question
  -> initial hypothesis
  -> evidence / experiment
  -> hypothesis update
  -> one takeaway
```

Do not begin with a glossary or technology definition unless the article cannot be understood otherwise.

Do not imitate an identifiable writer's style. Extract structural/editorial principles only.

Do not manufacture suspense by hiding evidence or exaggerating certainty.

## 11. Images and Illustrations

Images are supporting evidence/explanation, not decoration quotas.

Add an image only when it does at least one of:

- compress a complex causal/data flow;
- make a measured comparison easier to understand;
- expose a state transition or architecture boundary;
- show a concrete artifact/result that prose alone obscures.

Rules:

- the article must remain understandable if the image fails to load;
- image captions/nearby prose must not claim more than the underlying evidence;
- generated illustrations must not be presented as screenshots, measurements, or historical evidence;
- keep only final assets required by the article;
- remove staging chunks, base64 helpers, temporary generation scripts, noop files, and intermediate artifacts before merge;
- verify final image references resolve to repository files.

## 12. Interactive Demos

Interactive demos are optional progressive enhancement.

Use them only when changing an input and recalculating materially improves understanding.

The article must still stand alone if the demo is unavailable.

Do not claim a demo is executable until the actual public/static route has been fetched and tested when publication requires that route.

Prefer one shared runtime over duplicate per-article runtimes.

## 13. Builder / Auditor Separation

Treat implementation and acceptance as separate phases.

### Builder

May:

- research public evidence;
- draft/revise candidates;
- add tests, images, demos, pipeline code, contracts, and reports;
- run deterministic validation;
- open/update the canonical PR.

### Auditor

Must independently verify:

- the article has one central question and one discovery;
- material claims are supported by fetched evidence;
- privacy boundaries hold;
- candidate/published state is correct;
- generated images/demos are not misrepresented as evidence;
- current source/technical/editorial gates pass where applicable;
- CI evidence belongs to the exact head SHA;
- no helper/staging residue remains;
- publication state was not changed without authorization.

Implementation intent is never audit evidence.

## 14. Validation Ladder

Use the cheapest deterministic verifier that can falsify the change, then escalate.

Current baseline:

```bash
python -m compileall pipeline demos/python-syntax-gate/syntax_gate.py
python -m unittest discover -s tests -v
node --check demos/_shared/pyodide-worker.mjs
node --check demos/python-syntax-gate/app.mjs
python -m pipeline.audit
```

When a demo/static route is affected, run the repository's static route smoke equivalent.

For PRs, verify GitHub Actions on the exact head SHA. A green run on another SHA is not evidence for the current head.

A verifier that did not run is not PASS.

## 15. Publication Is a Separate Side Effect

Drafting, merging, or passing CI does not imply publication authorization.

Publication requires the active task or canonical pipeline state to explicitly authorize it.

Before publication:

1. confirm `published` state and publication contract;
2. rerun required source/technical/editorial gates;
3. verify the selected candidate is still the intended article;
4. verify filename/slug policy;
5. move/materialize only the intended article into `articles/` through the canonical path;
6. verify generated publication diff;
7. after deployment/sync, fetch the public result when possible;
8. retain evidence of the published revision/URL.

Do not publish a candidate merely because it is "finished".

## 16. Git / PR / CI Protocol

For repository changes:

1. start from the latest intended base;
2. continue the canonical branch if one exists;
3. otherwise create one short-lived descriptive branch when review is warranted;
4. keep the diff limited to the Contract;
5. remove generation intermediates before PR acceptance;
6. open/update one canonical PR;
7. verify changed filenames and exact-head CI;
8. inspect failed checks instead of retrying blindly;
9. merge only when acceptance criteria are satisfied;
10. verify merged `main` SHA and required main/deploy workflow;
11. verify candidate/publication state after merge;
12. rely on branch-hygiene automation or delete the merged branch when possible.

If a host-side safety system rejects a GitHub write, re-fetch current state and retry the exact canonical action once. Do not create a duplicate branch/PR as a workaround.

## 17. Cleanup Is Part of Completion

Before final reporting, inspect for:

- staging chunks;
- `.b64` intermediates;
- noop/debug files;
- temporary image-generation scripts;
- unused `.gitkeep` files introduced by the task;
- generated caches;
- duplicate images;
- superseded PRs;
- merged/redundant branches;
- stale article-state metadata;
- accidental private material.

Do not delete unrelated valid article candidates or evidence.

If unfinished work must remain, keep exactly one canonical workline and record the blocker and next action.

## 18. Fixed Point

Stop when all are true:

- requested outcome exists;
- article/pipeline state is correct;
- evidence and privacy gates are satisfied;
- relevant tests/audits pass;
- exact-head CI is verified when applicable;
- publication state matches the explicit contract;
- supporting assets resolve correctly;
- task-created residue is gone;
- linked PR/Issue state is correct;
- no known blocker remains.

Further polishing after this point is a new editorial task, not completion.

## 19. Final Report Contract

Report only verified state relevant to the task:

- target article / Issue / PR URL;
- what changed;
- evidence/source gates checked;
- tests/audits/CI and exact result;
- PR/commit/merge SHA;
- publication URL/receipt if publication occurred;
- cleanup performed;
- blocker and exact next action if unfinished.

Do not report publication when only a candidate was merged. Do not report evidence that was not fetched. Do not use completion theater.
