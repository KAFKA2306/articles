# Amendment v2.5 — post-merge evidence integrity re-audit

Date: 2026-08-15

Status: **article conclusion suspended until repaired controlled evidence is regenerated**

## Trigger

PR #116 merged an unpublished article candidate while `results/controlled/summary.json` still contained the pre-v2.4 collection: clean-baseline blockers for several formatter/linter candidates and failed workspace discovery/affected/cache results.

The repository also contained the v2.4 harness repair code, but the canonical summary had not been regenerated from that repaired harness before the article conclusion was accepted.

Therefore the existing article candidate is not publication-eligible evidence until this re-audit completes.

## Integrity rule added by v2.5

A mutant run is credited as a detection only when the corresponding calibrated clean baseline passes. A tool that rejects both clean and mutated input provides no controlled detection evidence for that mutant.

`raw_mutant_blocking_outputs` is retained for debugging. `detected` and the mutant detection matrix use only baseline-qualified observations.

## Re-audit procedure

1. Keep all candidate versions, mutants, frozen repository samples, and environment profiles unchanged.
2. Run the v2.4 repaired source and workspace harnesses from an exact trigger SHA.
3. Recompute `baseline-calibration.json` and `summary.json` using the v2.5 baseline-qualified detection rule.
4. Require `summary.status == complete` before any controlled result can contribute to a recommendation or story proposition.
5. Preserve the frozen real-repository sample unchanged.
6. Re-run evidence classification and story falsification after the repaired controlled evidence is fixed in Git.
7. Keep the article unpublished. If its surviving proposition no longer follows, replace or withdraw it rather than rationalizing the previous title.

## What this does not change

- candidate versions or stability labels;
- mutant definitions or expected affected sets;
- frozen real-repository names or SHAs;
- external-validity principle that unknown real-repo defect ground truth cannot be treated as recall;
- publication remains a separate explicit action.
