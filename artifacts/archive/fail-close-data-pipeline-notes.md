# Archived note: fail-close data pipeline

Status: **not an article / not a publish candidate**

The former `articles/fail-close-data-pipeline.md` did not have a repository-specific, public-evidence-backed incident strong enough to justify publication. The generic principles are preserved here only as reusable editorial/engineering notes.

## Minimal state contract

```text
ACQUIRED
  ↓
VALIDATED
  ↓
CANONICAL
  ↓
PUBLISHABLE
```

Do not silently promote states:

- acquisition failure ≠ zero records
- partial fetch ≠ complete dataset
- parsed ≠ validated
- validated ≠ canonical
- canonical ≠ publishable
- `null` ≠ `0`
- unknown ≠ pass

## Re-entry condition for a future article

Create a new article candidate only when at least one concrete public-evidence-backed incident can be reconstructed end to end, for example:

1. an HTTP-success response that was correctly rejected from canonical data;
2. a partial fetch that would otherwise have been mislabeled complete;
3. a concrete field where `null → 0` would materially change meaning;
4. a publish gate that demonstrably prevented an incorrect external release.

The future article must preserve:

```text
incident
→ mistaken-success condition
→ before
→ failing fixture / evidence
→ after
→ measured verification
```

Do not invent an incident merely to make the generic principle publishable.
