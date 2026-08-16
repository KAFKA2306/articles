# AIDev vocabulary study

This study uses only public external research datasets as study data. KAFKA2306 repositories, prior chat examples, and hand-picked repository samples are excluded from the study corpus.

## Current status

The external AIDev observational analysis has been executed. Its main result is negative with respect to the original lexical-propagation hypothesis: title-only multiword-expression reuse is not consistently higher for Agentic-PRs across the predefined sample-size sensitivity checks after matching by repository and AIDev task type.

The observed numbers and interpretation boundary are recorded in [`FINDINGS.md`](./FINDINGS.md).

Because the observational proxy is insufficient to establish decision or comprehension cost, the causal follow-up is specified separately in [`CONTROLLED_EXPERIMENT.md`](./CONTROLLED_EXPERIMENT.md). It uses ContextBench's existing gold-context and trajectory metrics rather than redefining success around a favorable lexical proxy.

## Observational question

Do agent-authored pull requests exhibit different cross-document reuse of multiword expressions than human-authored pull requests from the same repositories when exposure opportunity is balanced?

This is observational. It does not establish that an agent invented a term, that a repeated phrase is jargon, or that repeated language increases maintenance cost.

## Upstream data

Primary sources:

- AIDev paper: https://arxiv.org/abs/2602.09185
- AIDev replication package: https://github.com/SAILResearch/AI_Teammates_in_SE3
- AIDev dataset: https://huggingface.co/datasets/hao-li/AIDev
- AIDev schema at the pinned revision: https://huggingface.co/datasets/hao-li/AIDev/blob/6200a09fc80606189a50056eb10a50da157bde13/data_table.md

The study pins AIDev revision `6200a09fc80606189a50056eb10a50da157bde13` and verifies SHA-256 before reading inputs:

- `pull_request.parquet` — `08f520b5ef36b6281f82090db09ac14aefc3534ee113886e7bc85131fd8d214c`
- `human_pull_request.parquet` — `910238f8fe5deb544ae82be343232ff6838f271f3de4b4e4787a515336a91248`
- `pr_task_type.parquet` — `f32a97a45ac944f4ea473327e62d8f41361502c2b6b3778e76fb64c2b8896476`
- `human_pr_task_type.parquet` — `5527d52bfd9605a25d1ed1ef03bce0e1cc217f6ffed936e2be1b80a04123e658`

AIDev states that Human-PRs were sampled from the same repositories as Agentic-PRs and restricted to repositories with more than 500 GitHub stars. AIDev also publishes task-purpose classifications using Conventional Commit-style categories, derived by LLM classification of PR titles and commit messages.

## Analyses

Two text scopes are reported separately:

- `title`: PR title only, reducing PR-body template contamination;
- `title_body`: cleaned title plus body.

The repository-matched analysis:

1. removes URLs, fenced code, and inline code;
2. tokenizes word-like tokens and lowercases them;
3. extracts contiguous 2-, 3-, and 4-token expressions;
4. intersects repository identities between Agentic-PR and Human-PR data;
5. within every repository, selects the same number of documents from each class using deterministic SHA-256 ordering with a fixed seed;
6. measures median token count, the share of unique expressions reused in at least two PRs, and the share of document–phrase events attributable to reused expressions;
7. repeats paired comparisons at minimum document counts 2, 5, 10, and 20;
8. reports paired effect estimates, 10,000-resample bootstrap 95% confidence intervals, Wilcoxon signed-rank tests, and sign tests.

The post-specified robustness analysis in `analyze_task_matched.py` additionally balances Agentic-PR and Human-PR documents within the same repository **and the same AIDev task type** before computing repository-level outcomes. This controls the observed task-category mixture but does not make the study causal because the task labels are themselves model classifications and unobserved confounding remains possible.

No phrase is manually labeled as "AI jargon". Repeated expressions are descriptive lexical observations only. Raw phrases are not republished because AIDev states that content originating in source repositories remains governed by each source repository's original license.

## Run

```bash
python -m pip install pandas pyarrow scipy numpy
python research/aidev-vocabulary-study/analyze.py
python research/aidev-vocabulary-study/analyze_task_matched.py
```

Generated outputs:

- `results/summary.json`
- `results/repository_metrics.csv`
- `results/task_matched_summary.json`
- `results/task_matched_repository_metrics.csv`

Verified GitHub Actions run:

- https://github.com/KAFKA2306/articles/actions/runs/31943122727

The run completed both analyses and uploaded artifact `9262565185`; artifact ZIP SHA-256: `2b55ad4cd660cd178cc8766f9f0aa30b9e96d0cd2a70a559c969cdec0145cec6`.

## Threats to validity

- AIDev's human comparison set is sampled and restricted to popular repositories; it is not a census of all human PRs.
- PR language is not the same thing as persistent repository instructions such as `AGENTS.md`.
- Multiword-expression reuse can reflect legitimate project/domain terminology, contribution conventions, templates, or duplicated text.
- PR bodies can contain repeated structures; title-only results are therefore reported separately.
- Balancing document counts controls exposure opportunity but changes the analyzed sample when class sizes differ.
- Task-type matching controls only the published classification, not all differences between human and agent work.
- Statistical differences in wording do not establish comprehension or decision cost.
- This observational stage cannot identify whether an AI agent caused a phrase to enter a repository.

The controlled follow-up holds task semantics constant and randomizes wording instead of selecting another observational proxy after seeing these results.
