# Observed results from the AIDev matched-corpus study

Date: 2026-08-16

This file records the observed results. The study corpus contains no KAFKA2306 repository data and no repositories selected from prior chat context.

## Data and reproducibility

Upstream data:

- AIDev paper: https://arxiv.org/abs/2602.09185
- AIDev dataset revision: https://huggingface.co/datasets/hao-li/AIDev/tree/6200a09fc80606189a50056eb10a50da157bde13
- AIDev schema: https://huggingface.co/datasets/hao-li/AIDev/blob/6200a09fc80606189a50056eb10a50da157bde13/data_table.md

Pinned inputs:

- `pull_request.parquet`: SHA-256 `08f520b5ef36b6281f82090db09ac14aefc3534ee113886e7bc85131fd8d214c`
- `human_pull_request.parquet`: SHA-256 `910238f8fe5deb544ae82be343232ff6838f271f3de4b4e4787a515336a91248`
- `pr_task_type.parquet`: SHA-256 `f32a97a45ac944f4ea473327e62d8f41361502c2b6b3778e76fb64c2b8896476`
- `human_pr_task_type.parquet`: SHA-256 `5527d52bfd9605a25d1ed1ef03bce0e1cc217f6ffed936e2be1b80a04123e658`

Raw rows read successfully: 33,596 Agentic-PRs and 6,618 Human-PRs.

GitHub Actions run: https://github.com/KAFKA2306/articles/actions/runs/31943122727

The run completed both the repository-matched analysis and the repository + task-type matched robustness analysis successfully. The result artifact ID is `9262565185`; its ZIP SHA-256 is `2b55ad4cd660cd178cc8766f9f0aa30b9e96d0cd2a70a559c969cdec0145cec6`.

## Result 1: agent-authored PR titles are longer

This is the most stable observed difference.

After matching by repository and AIDev task type, the mean paired difference in repository-level median PR-title length was:

| Minimum matched PRs per class | Repositories | Agent − human tokens | Bootstrap 95% CI |
| ---: | ---: | ---: | ---: |
| 2 | 318 | +0.469 | +0.209 to +0.725 |
| 5 | 157 | +0.640 | +0.360 to +0.917 |
| 10 | 93 | +0.726 | +0.376 to +1.075 |
| 20 | 47 | +1.096 | +0.660 to +1.532 |

The direction remains positive at every predefined minimum-document threshold.

This measures text length only. It does not establish comprehension cost.

## Result 2: title-only phrase reuse does not provide robust evidence of stronger agent lexical propagation

The cleanest low-template scope is PR titles only. Multiword reuse was measured using contiguous 2–4-token expressions that appeared in at least two PR titles in the same repository.

After matching by repository and task type, the mean paired difference in the share of unique expressions that were reused was:

| Minimum matched PRs per class | Repositories | Agent − human | Bootstrap 95% CI |
| ---: | ---: | ---: | ---: |
| 2 | 318 | +0.0118 | +0.0026 to +0.0228 |
| 5 | 157 | +0.0083 | −0.0028 to +0.0215 |
| 10 | 93 | +0.0020 | −0.0092 to +0.0127 |
| 20 | 47 | +0.0113 | −0.0022 to +0.0243 |

The corresponding document–phrase event-share differences were:

| Minimum matched PRs per class | Agent − human | Bootstrap 95% CI |
| ---: | ---: | ---: |
| 2 | +0.0152 | +0.0029 to +0.0289 |
| 5 | +0.0121 | −0.0055 to +0.0304 |
| 10 | +0.0042 | −0.0160 to +0.0236 |
| 20 | +0.0227 | −0.0023 to +0.0474 |

Only the most permissive threshold has a bootstrap interval entirely above zero. The effect is not stable across the predefined 5/10/20-document sensitivity checks.

Therefore this observational analysis does **not** support a robust claim that agent-authored PR titles propagate repeated multiword expressions more strongly than human-authored PR titles.

## Result 3: adding PR bodies changes the result substantially

When cleaned PR bodies are included, human-authored PR text has higher mean repeated-expression shares in the larger matched subsets even after matching by repository and task type.

For example:

- minimum 5 PRs/class, 158 repositories: repeated-expression event share difference = −0.0776 (agent − human), bootstrap 95% CI −0.1198 to −0.0373;
- minimum 10 PRs/class, 95 repositories: −0.0941, CI −0.1447 to −0.0452;
- minimum 20 PRs/class, 47 repositories: −0.1476, CI −0.2208 to −0.0748.

For the share of unique expressions reused:

- minimum 5: −0.0360, CI −0.0582 to −0.0152;
- minimum 10: −0.0337, CI −0.0563 to −0.0131;
- minimum 20: −0.0328, CI −0.0605 to −0.0065.

The title-only and title+body analyses therefore answer different questions. PR bodies can contain contribution templates, checklists, boilerplate, copied issue descriptions, standard project language, and other repeated structures. The current analysis does not identify which mechanism produces the body-level difference.

It would be invalid to interpret the body result as evidence that human developers have more or less repository-specific jargon.

## What the observational study falsified

A simple proxy was tested: if coding agents strongly self-propagate repository-local vocabulary, agent-authored PR text might exhibit systematically higher cross-document multiword-expression reuse after matching exposure within repositories.

That prediction is not robustly supported in the cleaner title-only analysis.

This is a useful negative result because it rules out using generic n-gram repetition in PR text as sufficient evidence for the original mechanism.

## Remaining causal question

The original question is narrower and causal:

> Holding task requirements and meaning constant, does replacing ordinary software-engineering language with newly introduced repository-specific terms or abbreviations change how efficiently humans or coding agents find relevant context, make changes, and verify them?

The AIDev analysis cannot answer that question because wording was not randomized. The next study therefore uses controlled wording interventions on a repository-level benchmark rather than searching for another favorable observational proxy.
