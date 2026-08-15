# Evidence report: false success is the real failure

Date: 2026-08-15
Candidate: `artifacts/candidates/2026-08/2026-08-15-false-success-is-the-real-failure.md`
Publication state: `published: false`

## Contract

Create a 2026 successor to the author's January 2026 Crash-Driven Development article, but do not merely restate “fail fast”. Use current public repository outcomes to test what actually lets a user delegate work to an AI agent with less manual babysitting.

Original article:
https://zenn.dev/kafka2306/articles/11cd731eebded1

## Surviving proposition

**In an autonomous AI workflow, a visible crash is only the first half of reliability. The more dangerous state is false success: exit 0, green CI, or a completed side effect whose identity/meaning was never verified. User value appears when success itself must close an evidence loop before the system may advance.**

This is bounded to the public KAFKA2306 workflows cited below. It is not a universal proof that all systems should remove exception handling.

## Reader value

- `reader_before`: AI can implement and run CI, but the user still has to inspect logs, outputs, deployment targets, and whether “success” refers to the intended commit or remote object.
- `reader_after`: the reader can design an explicit progression from execution to verified outcome, so human attention is reserved for real blockers and product decisions rather than routine confirmation.
- `design_philosophy`: fail closed on ambiguity; preserve semantics at boundaries; separate execution, validation, side effect, read-back, identity, and authorization-to-advance; remove false-green/fallback paths before adding more automation.
- `why_this_article`: the January article argued for visible failure. The public 2026 repository evidence shows where that model breaks: green tests can be fake, a real crash can point at the wrong abstraction, migration debt can make strict gates unusable, and CI success can still be different from what a user sees in production.
- `proof_of_value`: merged PRs and exact-head workflow runs in yt3, investor2, books, and semiconductor-earnings-model.
- `desired_reader_action`: add one `VERIFIED` state to an existing workflow and require explicit evidence before advancing from CI success to irreversible side effects or completion.
- `non_goal`: no measured claim about percentage reduction in human work; no claim that try/catch or retries are generally bad; no claim that CI/provenance eliminates the need for human review in high-stakes decisions.

## Public evidence

### yt3 — false green removed

Merged PR:
https://github.com/KAFKA2306/yt3/pull/10

Observed changes in the merged PR:
- removed `bun test || echo "No tests found"` from CI and local task
- added publish-routing and no-fallback audits
- removed implicit latest-run selection
- preserved explicit RUN_ID, private-first publication, and remote proof boundaries

Exact PR-head workflow run (`9ae96846a83c4de74be71ec947288e121e343bad`):
https://github.com/KAFKA2306/yt3/actions/runs/31811558191
Conclusion: success.

### investor2 — strictness introduced as a ratchet, not mass rewrite

Merged PR:
https://github.com/KAFKA2306/investor2/pull/96

Pre-existing debt measured by the PR:
- 40 Python files would be reformatted
- Ruff: 96 errors
- Pyrefly strict: 73 errors
- Oxlint: 11 warnings

Decision:
- changed/maintained files fail on new format/lint debt
- full TypeScript strict check stays blocking
- Pyrefly existing debt is baselined; new errors fail
- duplicate `package-lock.json` and unused `vllm` dependency removed
- no Nx/Turborepo layer added

Exact PR-head workflows (`28105353d873eb99fb90cae5fedcaa256308dc6b`):
- Repository Ratchet: https://github.com/KAFKA2306/investor2/actions/runs/31823096854
- Hypothesis Lab Integrity: https://github.com/KAFKA2306/investor2/actions/runs/31823096820
- Quality Gates: https://github.com/KAFKA2306/investor2/actions/runs/31823096871
All completed successfully. The PR records the new Quality Gates run at 18 seconds; no like-for-like pre-migration combined baseline existed.

### books — a crash is not yet a useful failure model

Merged PR:
https://github.com/KAFKA2306/books/pull/73

The scheduled category enrichment completed its NDL/NDC work but failed later because a generic test encoded Markdown heading depth (`### Work`, `### Edition`, `### Holding`) instead of the semantic contract. The fix changed one test file to validate the Work/Edition/Holding concepts directly, preserving the enrichment logic.

Exact PR-head workflow (`4bc0f7c0b3b862b6309cd721dd9deccd69a9a66f`):
https://github.com/KAFKA2306/books/actions/runs/31849343391
Conclusion: success.

Interpretation: failure visibility was useful, but the next operational improvement is failure classification (`failed_step`, `failure_class`, SHA) so an agent does not mistake “data enrichment failed” for “post-enrichment repository contract failed”.

### semiconductor-earnings-model — CI success is not the user-visible artifact

Merged PR:
https://github.com/KAFKA2306/semiconductor-earnings-model/pull/116

Change:
- align Pages workflow with the current GitHub artifact deployment path (`configure-pages@v5`, `upload-pages-artifact@v4`, `deploy-pages@v4`)
- preserve post-deploy identity/provenance checks

Merge SHA:
`4d2ab0e9fc3e489c380c3c5706c3b43a336f3516`

A scheduled production workflow on that exact main SHA completed successfully:
https://github.com/KAFKA2306/semiconductor-earnings-model/actions/runs/31832401572

Official GitHub Pages custom-workflow documentation:
https://docs.github.com/en/pages/getting-started-with-github-pages/using-custom-workflows-with-github-pages

## External primary sources

GitHub documents that for `pull_request` workflows `GITHUB_SHA` can represent the synthetic merge commit, while the PR head commit is available as `github.event.pull_request.head.sha`. This supports treating “green run” and “which exact source revision was verified” as separate questions:
https://docs.github.com/en/actions/reference/workflows-and-actions/events-that-trigger-workflows

GitHub supports rerunning only failed jobs, which supports narrowing recovery to the failed evidence boundary rather than blindly rerunning everything:
https://docs.github.com/en/actions/how-tos/manage-workflow-runs/re-run-workflows-and-jobs

GitHub Pages documents a build-artifact-deploy chain and explicit deployment environment/permissions, supporting a separate deployment stage rather than equating source CI with public delivery:
https://docs.github.com/en/pages/getting-started-with-github-pages/using-custom-workflows-with-github-pages

## Competing propositions considered

1. “Fail fast is still the best AI coding discipline.”
   - Rejected as too close to the 2026-01 article and unable to explain false-green or remote-identity failures.

2. “Modern lint/type tools make AI agents reliable.”
   - Rejected. investor2 evidence shows tool choice is secondary to authority boundaries and migration policy; books and yt3 failures are not solved by adding more linters.

3. “The real unit of autonomous reliability is verified success, not visible failure.”
   - Survives. It explains all four cases without claiming more than the evidence supports.

## Counterfactual / reversal condition

This recommendation would weaken if the workflow has no external side effects, no ambiguous success state, deterministic single-process execution, and a human already reviews every result before it matters. In that bounded case, stack traces plus ordinary tests may be enough and additional state/evidence machinery can be needless overhead.

## Publication boundary

This change creates an unpublished candidate and evidence report only. It does not authorize publication to Zenn or move the candidate into `articles/`.