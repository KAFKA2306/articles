# Verification Stack v2 — Editorial Goal

The benchmark is not the product. **The product is the best evidence-backed article this investigation can support.**

The experiment exists only to create trustworthy evidence that can change a professional engineering decision.

## Reader outcome

The target reader is an experienced engineer or technical lead deciding how to structure verification for a modern Python/TypeScript codebase or monorepo.

After reading, the reader should be able to change at least one concrete decision such as:

- which tool owns formatting, lint, type checking, runtime validation, hooks, or workspace orchestration;
- which tools should not be stacked because their authority overlaps;
- which fast tool is not yet trustworthy enough to replace an incumbent;
- where a runtime contract adds information static analysis cannot provide;
- when Nx/Turborepo is justified and when it is unnecessary infrastructure;
- which checks belong in the first feedback loop versus later CI gates.

A reader who merely learns product names is a failure.

## Story gate

Do not draft an article until the evidence supports at least one **decision-changing, non-obvious proposition**.

A proposition qualifies only when all are true:

1. **Falsifiable** — the opposite could have been supported by the experiment.
2. **Measured** — at least one controlled result directly bears on it.
3. **Externally plausible** — real-repository evidence does not immediately invalidate it.
4. **Decision-changing** — adopting the proposition changes a tool, ordering, boundary, or operational policy.
5. **Non-obvious** — it is not merely the vendor's positioning or a generic best practice.
6. **Bounded** — the article can state where the result does not generalize.

If no proposition passes this gate, expand or amend the experiment rather than manufacture a narrative.

## Candidate story generation

After evidence classification, generate multiple competing story propositions before choosing a title. Examples of proposition shapes, not predetermined conclusions:

- `The fastest checker was not the fastest path to a trustworthy fix.`
- `Two popular tools were measuring the same failure, so stacking them reduced signal rather than increasing coverage.`
- `The compiler remained the authority even after the linter became type-aware.`
- `Monorepo orchestration paid for itself only after the dependency graph crossed a measurable complexity boundary.`
- `Runtime schemas found an entire class of defects that a perfect static pass could not see.`

Do not select a proposition until evidence exists.

## Article quality tests

The selected article must pass all of these:

### 1. Premise test

Can the article be reduced to one sentence that challenges or sharpens a professional reader's current mental model?

If not, the scope is too broad.

### 2. Evidence spine test

Can every major section attach to one of:

- controlled ground-truth result;
- exact official primary-source capability/limitation;
- frozen real-repository external-validity observation;
- explicit inference from those facts?

If not, remove the section.

### 3. Counterfactual test

Does the article explain what result would have caused the opposite recommendation?

If not, it reads like advocacy rather than engineering analysis.

### 4. Decision table test

Can the conclusion say not only `what won`, but:

- what responsibility it owns;
- what it replaces;
- what it does not replace;
- what disqualifies it;
- when a different choice is rational?

If not, the comparison is too shallow.

### 5. Compression test

Remove product-history, glossary, and feature-list prose unless required to understand the measured result. Tool names are evidence subjects, not the narrative structure.

### 6. Title test

The title should state the discovery or overturned assumption, not enumerate products. Tool names may appear when they materially improve discoverability, but they must not substitute for a thesis.

## Editorial fixed point

The investigation is complete only when one of these is true:

### A. Publishable discovery

- controlled evidence is complete for the relevant claim;
- external-validity evidence is frozen;
- one story proposition passes the story gate;
- a candidate article is written around that single proposition;
- unsupported comparisons are omitted;
- publication remains a separate explicit side effect.

### B. No article

- the preregistered study completes but no decision-changing non-obvious proposition survives;
- the result remains a benchmark/report;
- no filler article is created.

The benchmark must never become the article simply because it required substantial work.