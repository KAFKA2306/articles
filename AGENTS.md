# Articles Agent Operating Contract

This repository is the canonical system for discovering, testing, drafting, reviewing, selecting, revalidating, and retiring KAFKA2306 technical articles.

`README.md` describes the portfolio to humans. `pipeline/contracts/article.md` defines the editorial contract. This file defines what an autonomous agent may do and what it must never decide on its own.

## 1. Mission

Produce and maintain a small portfolio of evidence-backed articles that improve a reader's decision.

The target article does not merely explain a technology. It identifies a boundary that changes what the reader may reasonably trust, delegate, ship, infer, or reject.

Canonical article shape:

```text
observed scene / failure / number
  -> tempting initial interpretation
  -> current primary evidence
  -> falsification / boundary
  -> updated mental model
  -> portable decision rule
  -> explicit non-goal
```

Do not optimize for article count, publication frequency, word count, citation count, diagrams, or tool coverage.

A month with zero publishable articles is valid. Deleting or retiring a weak article is valid progress.

## 2. Source-of-truth precedence

When information conflicts, use this order:

1. the active user instruction for the current task;
2. current official/public primary sources fetched now;
3. current GitHub/production state fetched now;
4. current repository code, config, schemas, and executable audit logic;
5. `pipeline/contracts/article.md`;
6. deterministic tests, exact-head CI, reports, and immutable artifacts;
7. `README.md` and current design docs;
8. Issue/PR prose and historical audit reports;
9. memory, previous conversation context, or inference.

Historical prose is a hypothesis, not ground truth. Revalidate claims whose truth can change.

A generated sentence, model score, branch name, old screenshot, or unverified URL is not evidence.

## 3. Claim provenance

Classify every material claim as one of:

- **VERIFIED** — directly supported by currently fetched primary evidence, current repository state, deterministic execution, or exact-head CI.
- **OBSERVED** — an observation explicitly supplied by the user/task or recorded in a public artifact.
- **INFERRED** — a conclusion derived from verified evidence; the inference boundary must be visible.
- **UNVERIFIED** — not checked; remove or label it, never silently upgrade it.
- **FABRICATED** — forbidden.

For numbers preserve target, period, unit, population/scope, comparison basis, and what the number does not prove.

For causal language distinguish correlation, mechanism evidence, implementation dependency, and speculation.

For quotations verify the original page and keep attribution adjacent.

## 4. What counts as article value

The unit of value is not knowledge transfer alone. It is **decision leverage**.

Before drafting, define:

- `reader_job` — the concrete decision or action the reader needs to make;
- `reader_before` — what uncertainty, friction, risk, or false confidence exists before reading;
- `observed_anomaly` — the specific failure, contradiction, number, or unexpected result;
- `initial_hypothesis` — the tempting interpretation before investigation;
- `proof_of_value` — the public evidence unique to this article;
- `boundary` — what the evidence authorizes and what it does not authorize;
- `hypothesis_update` — what changed after verification;
- `decision_rule` — a portable rule the reader can apply elsewhere;
- `reader_after` — the action/decision newly enabled;
- `non_goal` — what remains unresolved;
- `half_life` — which claims are volatile and when revalidation is needed;
- `portfolio_overlap` — whether an existing article already does this job better.

If these cannot be stated without vague language, return to topic selection.

## 5. Topic rejection rules

Reject or keep private when the candidate is only:

- an official-documentation summary;
- an installation/setup guide;
- a link collection or service directory;
- a product roundup or "best stack" list without a controlled comparison;
- a tool/library explanation;
- a repository changelog;
- a generic best-practice summary;
- a configuration mistake with no transferable boundary;
- a secondary-source collage;
- an invented framework without implementation/measurement/falsification;
- an article whose central numbers cannot be reproduced or sourced;
- an "Aを使ってBを作った" story with no hypothesis update;
- a result where the conclusion was obvious before reading;
- a weak question padded with prose, citations, diagrams, or rhetoric.

Do not promote technical novelty to reader value automatically.

## 6. Preferred article families

The portfolio may span different technologies, but strong articles usually belong to one of these families:

1. **Authority boundary** — who/what is allowed to declare success or truth.
2. **Verification boundary** — what a test, detector, CI result, screenshot, or tool success actually proves.
3. **Delegation boundary** — what an AI/agent/process may safely do and what must remain externally constrained.
4. **Release/runtime boundary** — build, validation, release, production, visual, or real-client completion are separated.
5. **Provenance/decision history** — why a number or decision can be reconstructed later without hindsight rewriting.
6. **Observation boundary** — internal state is separated from user-visible/real-world outcome.

These are not mandatory section templates. They are portfolio-level patterns.

## 7. Evidence gate

Before an article can be publishable:

- retrieve primary/official external sources now when the claim can change;
- use current public KAFKA2306 GitHub evidence for repository-specific claims;
- follow the source minimums in `pipeline/config.json` and `pipeline/contracts/article.md`;
- verify URLs by real retrieval when required by the pipeline;
- preserve immutable commit/run/artifact references when the exact historical state matters;
- distinguish direct measurement from interpretation;
- remove a claim if a source is inaccessible, contradictory, stale, or narrower than the prose;
- never infer vendor internals from another vendor's implementation;
- never convert NOT_RUN / unknown / pending into PASS / complete.

A source count can satisfy a floor; it cannot rescue a weak claim.

## 8. Claim calibration / authority rule

For each important piece of evidence, explicitly ask:

```text
What conclusion does this evidence permit?
What stronger conclusion would exceed the evidence?
```

Examples:

```text
unit test PASS
  permits: tested assertions passed
  does not permit: product is correct in every user-visible state

MCP tool returned success
  permits: the tool invocation completed as reported
  does not permit: visual/runtime result is complete

watermark detector score
  permits: detector observed its defined signal under its assumptions
  does not permit: universal proof of AI authorship
```

This calibration is a blocking editorial requirement.

## 9. Privacy boundary

Private context is idea seed only.

Never commit or publish private diary text, non-public personal identifiers, tax/asset/health/private relationship information, private travel details, employer-internal information, credentials, tokens, private URLs, local absolute paths, or unpublished confidential project details.

If a private seed suggests a topic, re-ground every public claim in public evidence.

Run `python -m pipeline.audit` whenever its scope is affected.

## 10. Repository state boundaries

State is intentionally separated:

- `artifacts/candidates/YYYY-MM/` — unpublished public-safe candidates;
- `artifacts/reports/YYYY-MM/` — source/review/selection evidence;
- `pipeline/` — generation/review/selection/audit implementation;
- `pipeline/contracts/article.md` — canonical editorial contract;
- `articles/` — Zenn-compatible source for published articles and deliberately human-selected `published:false` drafts;
- `images/` / `demos/` — supporting assets only when they materially improve understanding or verification.

`published: false` is a hard state boundary.

Merging, CI green, article selection, or placement under `articles/` does not authorize public publication.

## 11. Human-controlled publication

Zenn's official AI-content policy requires the author to verify accuracy and contribute their own experience/insight, and warns against posting faster than human verification can keep up.

Primary references:

- https://info.zenn.dev/2026-03-10-ai-contents-guideline
- https://zenn.dev/guideline

Therefore:

- scheduled automation may discover, research, draft, audit, compare, and report;
- scheduled automation must not change an article from `published: false` to `published: true`;
- the internal `publish` command may only materialize a selected candidate as `published: false`;
- public publication requires an explicit current human instruction or equivalent explicit approval state;
- a calendar event, score threshold, merge, or "best candidate" result is never publication authorization.

If instructions are ambiguous, fail closed at `published: false`.

## 12. Portfolio lifecycle

Publication is not the terminal state.

Audit published articles as:

- `KEEP` — current evidence, reader job, and decision rule remain strong;
- `REVALIDATE` — core insight is durable but material facts are volatile;
- `REWRITE` — evidence/kernel is worth preserving but presentation or calibration is below current standard;
- `MERGE` — another article provides the same reader job with stronger proof;
- `RETIRE` — stale, misleading, redundant, weakly evidenced, or no longer worth maintaining.

Retirement is appropriate when one or more hold:

1. the article encourages a stronger conclusion than its evidence supports;
2. its central claim is no longer verifiable/current;
3. a newer article strictly supersedes its reader job;
4. it is mostly links/setup/docs summary and has no unique proof;
5. it relies on arbitrary thresholds or unsupported numeric claims;
6. title/body or promise/evidence are materially mismatched;
7. maintenance/revalidation cost exceeds the durable reader value;
8. keeping it dilutes the portfolio's decision/audit signature.

Do not keep a weak article merely because it has already been published.

## 13. Zenn retirement procedure

Zenn's GitHub integration and article deletion are different operations.

Official documentation states that complete deletion of a GitHub-managed article requires deleting it from the Zenn dashboard and from the connected repository; deleting only one side is insufficient and a repository copy can reappear.

- https://zenn.dev/zenn/articles/connect-to-github

When an agent cannot access the Zenn dashboard:

1. mark the article `RETIRE` in the portfolio audit with exact public URL;
2. remove the repository source only if it is repo-managed and the user authorized retirement;
3. create/maintain one exact human-action checklist for dashboard deletion;
4. never claim the public Zenn article was deleted until the public URL is fetched and confirmed absent;
5. after the human dashboard deletion, re-fetch the URL and close the retirement item only when absence is verified.

Do not create replacement slugs solely to simulate deletion.

## 14. Post-publication revalidation

Assign an approximate half-life to volatile claims.

Examples:

- pricing / quota / product availability — short half-life;
- current API/tool behavior — medium, version-sensitive;
- immutable experiment result at fixed commit — long;
- standards/history at fixed version — long, but citation links still need availability checks.

Revalidation checks:

- central source still exists and supports the same claim;
- product/version/pricing facts are still current where material;
- linked GitHub artifact still resolves;
- a newer article has not superseded the reader job;
- title still matches the actual evidence;
- no retrospective overclaiming has appeared after later results.

## 15. Builder / auditor separation

### Builder may

- research public evidence;
- draft/revise candidates;
- create tests, images, demos, reports, and pipeline code;
- run deterministic validation;
- open/update the canonical PR;
- propose lifecycle transitions.

### Auditor must independently verify

- one central reader job and one discovery;
- current source support for material claims;
- claim calibration and non-goal;
- privacy boundaries;
- portfolio overlap;
- candidate/published state;
- image/demo evidence integrity;
- exact-head CI where applicable;
- no helper/staging residue;
- publication state did not change without explicit authorization.

Implementation intent is never acceptance evidence.

## 16. Images and demos

Use an image only when it compresses a causal/data flow, exposes a state/boundary, makes a measured comparison easier to understand, or shows a concrete artifact that prose obscures.

Rules:

- article remains understandable if the image fails;
- generated illustrations are never presented as screenshots, measurements, or historical evidence;
- captions do not claim more than the source artifact;
- keep only final required assets;
- remove staging/base64/helper generation residue before merge;
- interactive demos are optional progressive enhancement, never a substitute for the written proof.

## 17. Contract before change

For non-trivial work define:

- **Contract** — what changes and what must remain unchanged;
- **Outcome** — observable final state;
- **Acceptance Criteria** — deterministic checks;
- **Evidence** — source URLs, files, CI runs, artifacts, or public receipts;
- **Stopping Condition** — the fixed point after which further edits are scope expansion.

Do not broaden an article because adjacent facts are interesting.

## 18. Canonical workline / Git protocol

Before creating a branch or PR:

1. inspect current `main`, open PRs, and relevant branches;
2. continue an existing canonical workline if it targets the same outcome;
3. otherwise create one short-lived branch for one logical change;
4. do not create competing implementations for the same outcome;
5. keep one logical change in one commit where practical;
6. prefer Git data API batching (`create_blob` -> `create_tree` -> `create_commit` -> `update_ref(force=false)`) for multi-file atomic changes;
7. verify changed filenames and exact-head CI;
8. inspect failed jobs/steps rather than blindly rerunning everything;
9. merge only after acceptance criteria pass;
10. verify merged `main` and any affected publication state.

If a host-side safety system rejects a write, re-fetch current state and retry the exact canonical action once. Do not create duplicate branches/PRs as a workaround.

## 19. Validation ladder

Use the cheapest deterministic verifier that can falsify the change, then escalate.

Baseline:

```bash
python -m compileall pipeline demos/python-syntax-gate/syntax_gate.py
python -m unittest discover -s tests -v
node --check demos/_shared/pyodide-worker.mjs
node --check demos/python-syntax-gate/app.mjs
python -m pipeline.audit
```

For PRs, verify GitHub Actions on the exact head SHA. A green run on another SHA is not evidence.

A verifier that did not run is not PASS.

## 20. Cleanup is completion

Inspect for stale candidates, duplicate articles, orphaned images, superseded reports, temporary generation scripts, debug/noop files, accidental private data, obsolete branches, and stale lifecycle metadata.

Delete only when the lifecycle decision and user authorization support deletion. Historical audit/evidence may remain when it is useful for explaining why an article was retired.

If unfinished work remains, leave exactly one canonical workline and record the blocker plus exact next action.

## 21. Fixed point

Stop when all are true:

- requested editorial/repository outcome exists;
- material claims were re-grounded in current evidence;
- reader job, boundary, decision rule, and non-goal are explicit;
- portfolio lifecycle state is correct;
- relevant tests/audits pass;
- exact-head CI is verified when applicable;
- publication state matches explicit human authorization;
- supporting assets resolve correctly;
- task-created residue is gone;
- no known blocker remains except an external action the available tools cannot perform.

Further polishing after this point is a new task.

## 22. Final report

Report only verified state relevant to the task:

- target repo / PR / article URLs;
- what was changed or retired;
- source/portfolio gates checked;
- tests/audits/CI exact result;
- commit/PR/merge SHA;
- public publication/deletion result only if directly verified;
- external blocker and exact human action if one remains.

Do not report Zenn deletion when only a repository file or retirement checklist changed. Do not report evidence that was not fetched. Do not use completion theater.
