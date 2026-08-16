# AIDev vocabulary study

This study uses only the public AIDev dataset as research data. KAFKA2306 repositories, prior chat examples, and hand-picked repository samples are excluded from the study corpus.

## Question

Do agent-authored pull requests exhibit different cross-document reuse of multiword expressions than human-authored pull requests from the same repositories when the number of documents is balanced within each repository?

This is an observational question. It does not by itself establish that an agent invented a term, that a repeated phrase is jargon, or that repeated language increases maintenance cost.

## Upstream data

Primary sources:

- AIDev paper: https://arxiv.org/abs/2602.09185
- AIDev replication package: https://github.com/SAILResearch/AI_Teammates_in_SE3
- AIDev dataset: https://huggingface.co/datasets/hao-li/AIDev

The study pins AIDev revision `6200a09fc80606189a50056eb10a50da157bde13` and verifies SHA-256 before reading either file:

- `pull_request.parquet` — SHA-256 `08f520b5ef36b6281f82090db09ac14aefc3534ee113886e7bc85131fd8d214c`
- `human_pull_request.parquet` — SHA-256 `910238f8fe5deb544ae82be343232ff6838f271f3de4b4e4787a515336a91248`

AIDev states that Human-PRs were sampled from the same repositories as Agentic-PRs and restricted to repositories with more than 500 GitHub stars. Repository identity is therefore derived from published GitHub repository/PR URLs and only repositories present in both classes are compared.

## Analysis

Two text scopes are reported separately:

- `title`: PR title only, to reduce PR-template contamination;
- `title_body`: cleaned title plus body, to measure the broader collaboration text.

For each scope:

1. Remove URLs, fenced code, and inline code.
2. Tokenize ASCII word-like tokens and lowercase them.
3. Extract contiguous 2-, 3-, and 4-token expressions.
4. Intersect repository identities between Agentic-PR and Human-PR data.
5. Within every repository, set `n = min(agent documents, human documents)` and select exactly `n` documents from each class using deterministic SHA-256 ordering with a fixed seed.
6. Measure, per repository and class:
   - median token count per PR;
   - fraction of unique 2–4-grams appearing in at least two PRs;
   - fraction of document–phrase events attributable to expressions appearing in at least two PRs.
7. Repeat the paired comparison for repositories with at least 2, 5, 10, and 20 documents in each class. Reporting all four thresholds exposes instability caused by small repositories rather than selecting a favorable cutoff after seeing results.
8. Report mean and median paired differences, positive/negative/zero difference counts, a 10,000-resample bootstrap 95% confidence interval for the mean paired difference, a two-sided Wilcoxon signed-rank test, and a two-sided sign test.

No phrase is manually labeled as "AI jargon". Repeated expressions are descriptive lexical observations only. Raw phrases are not published by this analysis because AIDev states that source-repository content remains governed by each source repository's original license.

## Run

```bash
python -m pip install pandas pyarrow scipy numpy
python research/aidev-vocabulary-study/analyze.py
```

Outputs:

- `results/summary.json`
- `results/repository_metrics.csv`

The raw downloaded Parquet files are stored under `.data/` and are not intended for version control.

## Threats to validity

- AIDev's human comparison set is sampled and restricted to popular repositories; it is not a census of all human PRs.
- PR language is not the same thing as persistent repository instructions such as `AGENTS.md`.
- Multiword-expression reuse can reflect legitimate project/domain terminology, contribution conventions, or duplicated text.
- PR bodies can contain templates; the title-only scope is included specifically to expose this confound rather than assuming it away.
- Balancing document counts controls opportunity for reuse but changes the analyzed sample when class sizes differ.
- Statistical differences in reuse do not establish higher comprehension or maintenance cost.
- This observational stage cannot identify whether an AI agent caused a phrase to enter a repository.

A causal follow-up must hold task semantics constant and randomize wording in controlled agent and human experiments.
