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

The analysis downloads these two published files and verifies their SHA-256 hashes before use:

- `pull_request.parquet` — SHA-256 `08f520b5ef36b6281f82090db09ac14aefc3534ee113886e7bc85131fd8d214c`
- `human_pull_request.parquet` — SHA-256 `910238f8fe5deb544ae82be343232ff6838f271f3de4b4e4787a515336a91248`

AIDev states that Human-PRs were sampled from the same repositories as Agentic-PRs, restricted to repositories with more than 500 GitHub stars. The analysis therefore uses only repository IDs present in both files.

## Predefined analysis

1. Concatenate PR title and body.
2. Remove URLs, fenced code, and inline code.
3. Tokenize ASCII word-like tokens and lowercase them.
4. Extract contiguous 2-, 3-, and 4-token expressions.
5. Intersect repository IDs between Agentic-PR and Human-PR data.
6. Require at least two usable PR documents in each class for a repository because cross-document reuse is undefined with one document.
7. Within every eligible repository, set `n = min(agent documents, human documents)` and select exactly `n` documents from each class using a deterministic SHA-256 ordering with a fixed seed.
8. For each repository and class, measure:
   - median token count per PR;
   - fraction of unique 2–4-grams appearing in at least two PRs;
   - fraction of document–phrase events attributable to expressions appearing in at least two PRs.
9. Compare Agentic-PR and Human-PR values within the same repository.
10. Report the mean and median paired difference, a 10,000-resample bootstrap 95% confidence interval for the mean paired difference, and a two-sided Wilcoxon signed-rank test.

No phrase is manually labeled as "AI jargon". Repeated expressions are descriptive lexical observations only.

## Run

```bash
python -m pip install pandas pyarrow scipy numpy
python research/aidev-vocabulary-study/analyze.py
```

Outputs:

- `results/summary.json`
- `results/repository_metrics.csv`
- `results/top_reused_phrases.csv`

The raw downloaded Parquet files are stored under `.data/` and are not intended for version control.

## Threats to validity

- AIDev's human comparison set is sampled and restricted to popular repositories; it is not a census of all human PRs.
- PR title/body language is not the same thing as persistent repository instructions such as `AGENTS.md`.
- Multiword-expression reuse can reflect legitimate project/domain terminology, templates, contribution conventions, or duplicated text.
- Balancing document counts controls exposure opportunity but changes the analyzed sample when class sizes differ.
- A statistical difference in reuse does not establish higher comprehension or maintenance cost.

A causal follow-up must hold task semantics constant and randomize wording in controlled agent and human experiments.
