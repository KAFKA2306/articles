# Articles Agent Operating Contract

This repository is the canonical system for discovering, testing, drafting, reviewing, selecting, revalidating, and retiring KAFKA2306 technical articles.

`README.md` describes the portfolio to humans. `pipeline/contracts/article.md` defines the editorial contract. This file defines what an autonomous agent may do and what it must never decide on its own.

## 1. Mission

Produce and maintain a small portfolio of **people-first, first-hand, useful technical articles**.

The target is not an article that merely proves a claim correctly. The target is an article that gives an intended reader a meaningful benefit:

```text
recognizable problem / desire
  -> first-hand observation, failure, number, or comparison
  -> non-obvious insight
  -> concrete proof
  -> useful next action / better decision
```

Use this shorthand:

> **Broad door -> Original insight -> Concrete proof -> Useful exit**

Evidence, claim calibration, and audit are mandatory quality infrastructure. They are not the portfolio's primary subject.

Do not optimize for article count, publication frequency, word count, citation count, diagrams, tool coverage, or SEO traffic.

A month with zero publishable articles is valid. Rewriting, merging, or retiring a weak article is valid progress.

## 2. People-first precedence

Before asking whether an article is technically correct, ask whether it deserves a reader's time.

Google Search Central's current people-first self-assessment emphasizes intended audience usefulness, first-hand expertise, satisfying goal completion, original information/research/analysis, and substantial value beyond other search results.

Primary references:

- https://developers.google.com/search/docs/fundamentals/creating-helpful-content
- https://developers.google.com/search/docs/fundamentals/creating-helpful-content?hl=ja

Zenn's current guidelines emphasize concrete trial-and-error, author-specific perspective, real experience, accurate titles, reader-oriented structure, and avoiding unverified AI-generated mass posting.

Primary references:

- https://zenn.dev/guideline
- https://info.zenn.dev/2026-02-03-community-guidelines-update
- https://info.zenn.dev/2026-03-10-ai-contents-guideline

Use these as editorial principles, not as SEO hacks.

## 3. Article value model

Before drafting, define all of the following.

### Reach

- `intended_audience` — who should care;
- `broad_entry` — the problem/desire in language that audience understands without knowing the implementation technology;
- `stakes` — why this matters in time, money, risk, effort, quality, capability, or confidence.

A niche article is allowed. A niche title whose reader cannot tell why the topic matters is not.

### Customer value

- `reader_job` — what the reader wants to accomplish or decide;
- `reader_before` — current friction, loss, risk, uncertainty, or false confidence;
- `customer_value` — what becomes cheaper, safer, faster, clearer, or newly possible;
- `reader_after` — the action/decision state enabled after reading;
- `useful_exit` — checklist, decision rule, design pattern, stop condition, adoption rule, or reproducible next step.

`understand`, `learn`, or `know about X` alone is insufficient.

### Originality and experience

- `original_observation` — first-hand measurement, operation, failure, comparison, implementation, or artifact;
- `surprising_finding` — what a competent reader would not get cheaply from official docs or a generic AI summary;
- `hypothesis_update` — what changed after actual observation;
- `why_this_article` — why this deserves a separate article rather than a paragraph in another article.

### Proof and trust

- `proof_of_value` — current public evidence unique to the article;
- `claim_boundary` — what the evidence supports and what it does not;
- `non_goal` — unresolved/unproven area;
- `half_life` — volatile claims and revalidation trigger.

### Portfolio value

- `portfolio_overlap` — whether another article already performs the same reader job better;
- `durable_value` — why the article should still be useful after the immediate news/product moment passes.

If these cannot be stated concretely, return to topic selection.

## 4. Preferred article shape

The default discovery shape is:

```text
broadly recognizable friction / desire
  -> concrete scene, failure, number, or comparison
  -> natural expectation
  -> first-hand evidence / experiment
  -> unexpected insight or reframing
  -> practical consequence
  -> useful exit
  -> proof limits
```

The article may discuss authority/verification boundaries when they create reader value, but **finding a boundary is not itself a publication reason**.

## 5. Topic rejection rules

Reject, merge, or keep private when a candidate is only:

- official-documentation summary;
- installation/setup guide;
- link collection or service directory;
- product/tool roundup without a meaningful reader decision;
- repository changelog;
- generic best-practice summary;
- secondary-source collage;
- invented framework without first-hand implementation/measurement;
- technology-first article whose intended audience cannot identify the problem;
- an "Aを使ってBを作った" story with no reader benefit beyond the author's success;
- unsupported rankings, magic numbers, thresholds, or success rates;
- obvious conclusion padded with prose/citations/diagrams;
- a duplicate reader job with weaker proof than an existing article;
- an article that is accurate but does not save effort, reduce risk, unlock action, or change a useful mental model.

Technical novelty does not automatically equal reader value.

## 6. Broad-entry rule

The title and opening must make the problem legible before requiring niche vocabulary.

Prefer:

```text
human problem / desire
  -> concrete anomaly/result
  -> technical term when useful
```

Avoid titles that only make sense to someone already searching for an implementation detail.

Broad entry does **not** mean shallow content. Keep the proof and technical depth as narrow and rigorous as necessary.

Before accepting a title, create at least:

1. `broad_problem`
2. `concrete_result`
3. `searchable`

Do not use exaggerated clickbait. The selected title must accurately match the body.

## 7. Source-of-truth precedence

When information conflicts, use this order:

1. active user instruction for the current task;
2. current official/public primary sources fetched now;
3. current GitHub/production state fetched now;
4. current repository code/config/schema/executable audit logic;
5. `pipeline/contracts/article.md`;
6. deterministic tests, exact-head CI, reports, immutable artifacts;
7. `README.md` and current design docs;
8. Issue/PR prose and historical audit reports;
9. memory, previous conversation context, or inference.

Historical prose is a hypothesis, not ground truth. Revalidate changeable claims.

## 8. Claim provenance and calibration

Classify material claims as:

- **VERIFIED** — supported by currently fetched primary evidence, current repository state, deterministic execution, or exact-head CI;
- **OBSERVED** — explicitly supplied or recorded observation;
- **INFERRED** — conclusion derived from evidence with visible inference boundary;
- **UNVERIFIED** — not checked; remove or label;
- **FABRICATED** — forbidden.

For numbers preserve target, period, unit, population/scope, comparison basis, and what the number does not prove.

For each important proof, ask:

```text
What does this prove?
What stronger conclusion would exceed it?
Why does the reader need this proof?
```

The third question is essential. Proof without a reader job is not an article.

## 9. Evidence gate

Before publication:

- retrieve current primary/official sources for changeable external claims;
- use current public KAFKA2306 GitHub evidence for repository-specific claims;
- follow source minimums in current config/contract;
- verify URLs by real retrieval when required;
- preserve fixed commit/run/artifact references for historical state;
- distinguish measurement from interpretation;
- remove claims when sources are inaccessible, contradictory, stale, or narrower than prose;
- never infer vendor internals from another vendor's implementation;
- never convert NOT_RUN / unknown / pending into PASS / complete.

Source count is a floor, never the objective.

## 10. Reader satisfaction gate

Before calling an article publishable, an independent reviewer should be able to answer:

- Who is this for?
- Why should they care before knowing the tool name?
- What can they do better after reading?
- What did the author actually observe or do?
- What is genuinely non-obvious here?
- What proof supports it?
- What does the proof not establish?
- Would a reader still need to search again for the core answer?
- Is this worth bookmarking, sharing, or referring to later?

If the core answer still requires another search, the article is incomplete unless it explicitly scopes itself as a narrow reference.

## 11. Privacy boundary

Private context is idea seed only.

Never commit or publish private diary text, non-public personal identifiers, tax/asset/health/private relationship information, private travel details, employer-internal information, credentials, tokens, private URLs, local absolute paths, or unpublished confidential project details.

If a private seed suggests a topic, re-ground every public claim in public evidence.

Run `python -m pipeline.audit` whenever its scope is affected.

## 12. Repository state boundaries

- `artifacts/candidates/YYYY-MM/` — unpublished public-safe candidates;
- `artifacts/reports/YYYY-MM/` — source/review/selection evidence;
- `pipeline/` — generation/review/selection/audit implementation;
- `pipeline/contracts/article.md` — canonical editorial contract;
- `articles/` — Zenn-compatible source for published articles and deliberately human-selected `published:false` drafts;
- `images/` / `demos/` — support only when they materially improve understanding or proof.

`published: false` is a hard boundary.

Merging, CI green, article selection, or placement under `articles/` does not authorize public publication.

## 13. Human-controlled publication

Scheduled automation may discover, research, draft, audit, compare, and report.

Scheduled automation must never change `published: false` to `published: true`.

The internal `publish` command may only materialize a selected candidate as `published: false`.

Public publication requires an explicit current human instruction or equivalent explicit approval state. A calendar event, score threshold, merge, or "best candidate" result is never publication authorization.

If instructions are ambiguous, fail closed at `published: false`.

## 14. Portfolio lifecycle

Publication is not terminal.

- `KEEP` — Reach, customer value, originality, experience, utility, trust, and portfolio value remain strong;
- `REVALIDATE` — insight is durable but material facts are volatile;
- `REWRITE` — core experience/insight is valuable but broad entry, customer value, or structure is weak;
- `MERGE` — another article can perform the same reader job with stronger proof;
- `RETIRE` — no longer worth a reader's time or the maintenance cost.

Retire or rewrite when one or more hold:

1. intended audience / reader job is unclear;
2. title is implementation-first and hides the actual human problem;
3. article is accurate but commodity information;
4. first-hand experience or original observation is weak;
5. useful exit is missing;
6. central claim is stale or unverifiable;
7. evidence encourages a stronger conclusion than it supports;
8. a newer article supersedes the same reader job;
9. unsupported numeric guidance is central;
10. title/body promise is mismatched;
11. maintenance cost exceeds durable value;
12. keeping it dilutes the portfolio's recognizable expertise and usefulness.

Do not keep a weak article merely because it was published.

## 15. Zenn retirement procedure

For repo-managed articles, complete deletion may require both Zenn dashboard deletion and repository deletion according to Zenn's GitHub integration behavior.

Reference:

- https://zenn.dev/zenn/articles/connect-to-github

When an agent cannot access the Zenn dashboard:

1. mark exact public URL and lifecycle decision;
2. remove repository source only when authorized;
3. maintain one exact human-action checklist;
4. never claim public deletion until the URL is fetched and confirmed absent;
5. close only after public absence is verified.

## 16. Post-publication review

Revisit published articles for:

- Reach: does the title still expose the real problem?
- Customer value: is the benefit still meaningful?
- Originality: is the page now commodity information?
- Experience: does first-hand evidence remain visible?
- Utility: is the useful exit still actionable?
- Trust: do current sources still support material claims?
- Portfolio value: is a newer article now better?
- Half-life: are volatile facts current?

Deleting low-value work is portfolio maintenance, not failure.

## 17. Builder / auditor separation

### Builder may

- research public evidence;
- draft/revise candidates;
- create tests, images, demos, reports, and pipeline code;
- run deterministic validation;
- open/update the canonical PR;
- propose lifecycle transitions.

### Auditor must independently verify

- intended audience and broad entry;
- customer value / reader after;
- original observation and first-hand experience;
- useful exit;
- current source support and claim calibration;
- privacy boundaries;
- portfolio overlap;
- candidate/published state;
- exact-head CI where applicable;
- no helper/staging residue;
- publication state did not change without explicit authorization.

Implementation intent is never acceptance evidence.

## 18. Images and demos

Use images only when they materially improve comprehension, comparison, or proof.

Rules:

- article remains understandable if image fails;
- generated illustrations are not screenshots, measurements, or historical evidence;
- captions do not exceed the source artifact;
- keep only final required assets;
- remove staging/base64/helper residue before merge;
- interactive demos are optional progressive enhancement.

## 19. Contract before change

For non-trivial work define:

- **Contract** — what changes and what must remain unchanged;
- **Outcome** — observable final state;
- **Acceptance Criteria** — deterministic checks;
- **Evidence** — source URLs, files, CI runs, artifacts, or public receipts;
- **Stopping Condition** — fixed point after which further edits are scope expansion.

## 20. Canonical workline / Git protocol

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
10. verify merged `main` and affected publication state.

## 21. Validation ladder

Use the cheapest deterministic verifier that can falsify the change, then escalate.

```bash
python -m compileall pipeline demos/python-syntax-gate/syntax_gate.py
python -m unittest discover -s tests -v
node --check demos/_shared/pyodide-worker.mjs
node --check demos/python-syntax-gate/app.mjs
python -m pipeline.audit
```

For PRs, verify GitHub Actions on the exact head SHA. A green run on another SHA is not evidence.

A verifier that did not run is not PASS.

## 22. Fixed point

Stop when all are true:

- requested editorial/repository outcome exists;
- intended audience, broad entry, customer value, original observation, and useful exit are explicit;
- material claims are grounded and calibrated;
- portfolio lifecycle state is correct;
- relevant tests/audits pass;
- exact-head CI is verified when applicable;
- publication state matches explicit human authorization;
- task-created residue is gone;
- no known blocker remains except an external action unavailable to the tools.

## 23. Final report

Report only verified state relevant to the task:

- target repo / PR / article URLs;
- what changed, rewrote, merged, or retired;
- reader-value / source / portfolio gates checked;
- tests/audits/CI exact result;
- commit/PR/merge SHA;
- public publication/deletion result only if directly verified;
- external blocker and exact human action if one remains.

Do not report Zenn deletion when only a repository file or retirement checklist changed. Do not report evidence that was not fetched.
