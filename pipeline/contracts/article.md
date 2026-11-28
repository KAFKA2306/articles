# Evidence-first article contract

This file is the concise authoring contract. Repository policy and release
boundaries live in the root `AGENTS.md`; Zenn validation is implemented by
`pipeline/evidence_gate.py`, `pipeline/zenn_slug.py`, and `pipeline/audit.py`.

## Write from a first-hand fixture

Start with an observation the author can identify and defend: a revisioned code
change, failing and passing input, measured output with units and conditions,
operational log, dataset, or direct comparison. Cite the exact public artifact.
Do not infer an experiment from a commit title or invent an observation to fill
an outline.

## Build a useful decision

State the reader's problem, the default expectation, the observed result, the
mechanism the evidence supports, and an action the reader can take. Separate
observation from inference and hypothesis. Include a counterexample, scope
condition, and what would falsify or narrow the rule. Preserve numbers, IDs,
versions, uncertainty, and source history while editing.

## Release boundary

Drafts stay `published: false`. CI validates format and repository invariants;
only the human-triggered Zenn release workflow changes public state. Never
publish from a score, schedule, merge, or candidate-selection result.
