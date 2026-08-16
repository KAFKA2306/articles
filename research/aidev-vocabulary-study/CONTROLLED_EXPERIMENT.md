# Controlled experiment: wording in repository context and coding-agent retrieval cost

Status: protocol drafted after the observational AIDev analysis and before running this experiment.

The observational study did not robustly show higher multiword-expression reuse in agent-authored PR titles. This experiment therefore tests the causal question directly instead of searching for another observational proxy.

## Research question

Holding the software task and behavioral requirements constant, does introducing repository-specific names or abbreviations into agent instructions change coding-agent context retrieval, task success, or inference cost?

## Benchmark

Use ContextBench because it supplies issue-resolution tasks with human-annotated gold repository context and an evaluator for agent trajectories.

Primary sources:

- Paper: https://arxiv.org/abs/2602.05892
- Code: https://github.com/EuniAI/ContextBench
- Project site: https://contextbench.github.io/

ContextBench reports 1,136 tasks from 66 repositories across eight programming languages and evaluates retrieved context against human-annotated gold context at file, block, and line granularity.

For comparison with existing repository-context research, also retain the published AGENTBench implementation and paper as methodological references:

- Paper: https://arxiv.org/abs/2602.11988
- Code: https://github.com/eth-sri/agentbench

The AGENTS.md study reports that repository context files can increase exploration and inference cost while not consistently improving task success. The present experiment isolates wording while keeping requirements unchanged.

## Intervention

Every benchmark task is run from the same frozen repository snapshot under three instruction variants. The software requirements, required checks, and stopping condition are identical across variants.

### Plain wording

Instructions use ordinary software-engineering language without assigning new names to the rules.

Example semantic content:

- inspect existing work before creating duplicate work;
- make the smallest change required by the issue;
- run the relevant existing checks;
- stop after the requested outcome is verified.

### New multiword labels

The same requirements are expressed with newly introduced multiword names. The name is defined when first used and then used later in place of the ordinary phrase.

The exact label vocabulary must be generated before the confirmatory runs and stored in the experiment manifest. Multiple label sets are used and counterbalanced across tasks so that results cannot depend on one particular coined phrase.

### New abbreviations

The same requirements and multiword names are used, but subsequent references use newly introduced abbreviations. Each abbreviation is defined once before use.

## Two estimands

Two separate comparisons are necessary because real repository terminology can increase both lexical opacity and instruction length.

1. **Realistic package effect**: preserve the natural extra text required to define new labels and abbreviations. This estimates the total effect of introducing the terminology as it would normally appear in a repository context file.
2. **Length-controlled wording effect**: construct semantically equivalent variants with approximately equal tokenizer length and the same number of requirements. This estimates the effect of lexical naming with instruction length held as constant as practicable.

The two estimands must not be collapsed into one result.

## Exposure

The treatment is supplied through the repository-context mechanism used by the evaluated agent. The experiment harness must confirm before inclusion that each agent actually receives the context file or equivalent repository instruction surface.

A manipulation check records whether the introduced labels or abbreviations occur later in the agent trajectory. Failure to repeat a label is not an exclusion criterion; it is evidence that the treatment was ignored.

Each run starts from a clean benchmark snapshot. Treatment vocabulary from one run must never persist into another run.

## Sampling and power

Do not choose a favorable subset after observing treatment outcomes.

1. Draw an initial pilot sample of 30 ContextBench tasks using a fixed pseudorandom seed, stratified by repository and language where possible. Pilot tasks are used only to verify treatment delivery, estimate runtime/variance, and calculate the confirmatory sample size; they are excluded from confirmatory effect estimates.
2. Before confirmatory runs, freeze the task IDs, model versions, agent versions, instruction variants, tokenizer-length checks, time/token limits, and statistical analysis in a machine-readable manifest.
3. Determine the confirmatory task count from the pilot variance using 80% power and two-sided alpha 0.05 for the declared smallest effects of interest. If the computed count exceeds the available benchmark, use the full eligible ContextBench corpus and report the resulting detectable effect rather than reducing the target post hoc.

The initial smallest effects of interest must be set before pilot outcome analysis. Suggested values to justify or revise before running are a 5 percentage-point absolute change in task resolution and a 10% relative change in retrieval-efficiency or token-cost measures.

## Randomization

Use a within-task design: every included task is evaluated under every wording condition for each selected model/agent configuration.

For stochastic agents, repeat each task-condition combination with independent runs. Condition order is randomized independently within each task/model/agent block using a recorded seed.

Repository snapshot, issue text, agent scaffold, model version, tool availability, maximum turns, token budget, and execution timeout remain fixed within each block.

## Outcomes

### Primary process outcome

Use ContextBench's existing retrieval-efficiency metric at the published granularity selected before confirmatory runs. Do not create a new composite score.

### Primary end-to-end outcome

Task resolution using the benchmark's existing pass/fail evaluation.

### Secondary outcomes

Use existing observable quantities where available:

- context recall;
- context precision;
- context F1;
- time or trajectory step at which the first gold-context file is retrieved;
- number of files inspected;
- number of non-gold files inspected;
- input tokens;
- output tokens;
- total model tokens/cost when reported by the runner;
- tool calls;
- elapsed runtime;
- patch size;
- introduced-label or abbreviation occurrences in the trajectory.

Do not infer cognitive state from tokens or tool calls. These are process measurements only.

## Statistical analysis

The primary comparison is paired within task.

- For continuous retrieval/cost outcomes, report the paired mean and median treatment differences with task-clustered bootstrap 95% confidence intervals.
- For binary task resolution, report paired absolute percentage-point differences with a confidence interval and a paired binary test such as McNemar's test.
- Report model/agent-specific estimates in addition to the pooled estimate; do not assume one effect applies to all coding agents.
- Use task as the resampling cluster so repeated runs of one task do not become independent observations.
- Correct confirmatory p-values for the two primary treatment comparisons (`new labels` vs `plain`, `new abbreviations` vs `plain`). Secondary outcomes are exploratory and are reported as effect estimates with intervals rather than used to rescue a null primary result.

The confirmatory analysis script must be written and committed before confirmatory trajectories are generated.

## Exclusions

Exclude a task-run only for a predeclared execution failure unrelated to treatment, such as a corrupted benchmark snapshot or provider outage affecting the whole comparison block. Do not exclude runs because the model ignored the terminology, failed the task, used many tokens, or produced an extreme trajectory.

If one condition in a paired block is lost to infrastructure failure, rerun the entire affected block under the same recorded configuration rather than retaining an unpaired subset.

## Threats to validity

- ContextBench gold context represents expert-annotated sufficient/relevant code context, not human cognitive effort.
- Different agent frameworks may consume repository context files differently; exposure must be verified per agent.
- Coined experimental labels may be more artificial than naturally evolved repository terminology.
- Equalizing tokenizer length can itself require unnatural wording; therefore the realistic and length-controlled estimands are both reported.
- Model/provider updates can invalidate replication unless exact versions are pinned.
- Repeated runs on hosted models may remain nondeterministic even with identical prompts.

## Falsification criterion

The hypothesis that repository-specific naming creates measurable coding-agent decision cost is not supported if the confirmatory experiment shows no practically meaningful degradation in the predefined primary outcomes across the label and abbreviation treatments, with confidence intervals narrow enough to exclude the declared smallest effects of interest.

A null result must be retained. The study must not switch after the fact to a different lexical metric, task subset, or outcome to preserve the original hypothesis.
