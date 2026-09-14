---
okf_version: "0.2"
type: evaluation-protocol
title: "Evaluating a refactoring across models"
generated:
  by: "agent:codex"
  at: "2026-09-12T23:39:51Z"
lifecycle:
  status: draft
  updated_at: "2026-09-13T20:30:12Z"
sources:
  - resource: "docs/skill-refactoring-guide.md"
    sha256: "b044b3d3246dca295fb93c8e7da094a541b200c262fdc57ad4077fde0c7c60c5"
  - resource: "https://claude.com/plugins/skill-creator"
  - resource: "https://developers.openai.com/api/docs/guides/evaluation-best-practices"
  - resource: "https://www.anthropic.com/claude/fable"
verified:
  - event: static_validation
    by: "agent:claude"
    at: "2026-09-13T20:30:12Z"
    scope: "references/evaluation.md"
    source: "relative links resolved from each referencing file; grep: no model names outside sources:"
---

# Evaluate without mistaking an edit for a gain

## Experiment design

Start from the skill-creator cycle: a few real requests, execution of the candidate
and the reference, judgment of the artifacts, human feedback, and a new iteration. A
pilot of two or three cases finds defects; it does not support a claim of statistical
superiority. Use [this skill's own cases](../evals/evals.json) to test this refactorer;
to evaluate another skill, write cases from its domain.

Freeze before the final comparison: cases, rubric, mandatory requirements, models,
configurations, budget, timeouts, retries, primary metric, and acceptable limits. Do
not run paid batches or launch external providers without authorization and budget.
A request limited to preparation produces the cases and the plan, not executions.
Never widen a pilot to every model on your own.

For a refactoring, A is the complete previous version and B the candidate. For a new
skill, A is the run without that skill. Compare A/B within each model before comparing
models. If a C variant adds guided support, keep B as the same core. Record which
baseline stays fixed across iterations.

Record the real model ID returned by the runtime, the effort level, the tools, and the
profile used. Accept explicit selections; never invent slugs or assume equivalence
between providers' effort levels. Do not change safeguards to obtain a comparison. An
unavailable model is `not_run`, with the reason.

Pair by case, reset context and files, and vary the A/B order. The skill under
evaluation and the baseline never receive each other's answer or the rubric used only
by the grader. Parallelize only with isolation and controlled concurrency. Sequential
isolated runs are valid; subagents are not a statistical requirement.

## Correctness and triggering

Examine real artifacts and observable steps, not only the executor's statement. Use
objective checks for verifiable content and human review for subjective quality. When
the skill-creator plugin is installed, its `grading.json` format records `text`,
`passed`, and `evidence` per expectation; otherwise record the same three fields in a
results table.

A check must measure the observation, not the writer's language or wording. Fold accents
before matching and accept the vocabulary of every language the run may answer in — a
grader looking for `static` scored a compliant Portuguese review ("estático") as a
failure on 2026-09-13, which reads as a model defect and is not one. One expectation
tests one thing: a check that conflates two observations cannot say which failed. When a
run fails, read the evidence string before believing the verdict.

Expectation `pass_rate` and the rate of accepted tasks are different metrics. Failing
a mandatory requirement invalidates the task even with a high average. Treat missing
evidence as an undemonstrated criterion. Show results for human review and, when
useful, compare A/B without revealing the version to the grader.

Examine expectations that pass in both versions, fail in both, or vary widely. Link
observed waste to change hypotheses and test one component at a time: description,
routing, repetition, or guided support. Re-evaluate the final combination and
generalize the fixes beyond the examples seen.

Test discovery separately from forced execution. Use the real catalogue and nearby
positive and negative requests: refactoring a skill is positive; refactoring a Python
function or merely using the skill is negative. Measure one binary decision per run:
precision = TP/(TP+FP); coverage = TP/(TP+FN). Repeated calls are diagnostics, not new
hits. Empty denominators are `N/A`, not zero.

More emphatic descriptions, which skill-creator suggests for triggering omissions on
Claude, must be tested on each model; do not treat them as a universal rule. Separate
development, validation of the description choice, and an untouched final set —
choosing repeatedly by outcome turns a test into validation.

## Measures and decision

- Success rate: accepted runs / started runs. Also report success without recovery
  and failures by category. Repetitions of one case do not replace case diversity.
- Cost per success: the cost of every run, including failures, tools, recovery, and
  fallback, divided by the successes. With no success there is no finite ratio.
  Separate evaluation cost and human work.
- Time: request to verified completion or failure, p50 and p95 when the sample
  allows, timeout rate, and human wait reported separately. Never report successes only.
- Context: accumulated input, peak, output, references loaded, and compactions. A
  file's line count does not replace these data.

Where `scripts/bench.py` records each of these — read
[the runtime contract](runtimes.md) for the per-runtime sources:

| Measure | Field | File |
| --- | --- | --- |
| Accepted run | `pass_rate == 1.0` in `summary` (every objective expectation passed) | `grading.json` |
| Cost of a run | `cost_usd` + `cost_source` (`runtime`, `pricing_table`, `estimated`) | `record.json` |
| Cost per success | `cost_per_success_usd` per (runtime, model, config) | `summary.json → efficiency_by_model` |
| Time | `duration_seconds`; `duration_p50_s` per group | `record.json`, `summary.json` |
| Context | `usage.context_tokens` (fresh input + cache read + cache write — Claude reports `input_tokens` net of cache), `usage.output_tokens`; `skill_static_tokens` | `record.json`, `summary.json`, `tokens.json` |
| Limits fixed beforehand | `budget_usd`, `timeout`, `per_claude_run_budget_usd` | `summary.json` |

Four rules follow from these fields:

- **Triggering is measured apart from execution**: precision and coverage per model on the
  real catalogue (`trigger_evals`); a more emphatic description enters only where it
  improved on each model tested.
- **Context is accumulated input plus peak plus references actually loaded** — never a
  line count. Read the transcript for which references were opened.
- **Limits are fixed before the run**: acceptance rate, cost, p50/p95, timeouts. A result
  outside any limit is not a gain even when the mean improved.
- **Full cost**: failures, retries, tools and fallback are in the numerator; prices carry
  currency and date (`matrix.pricing` in `evals/evals.json`). Claude reports real cost,
  Hermes an estimate, Codex none — computed from usage.

Capture the observations the runtime makes available at the end of each run. If
tokens, cache, or costs are absent, mark `not_available` and explain. Use verified
rates with currency and date; do not count reasoning twice when it is already in the
output. Record observed cache: a new conversation does not guarantee a cold cache.
Compare equivalent conditions and report external failures without hiding their cost
or selectively excluding unfavorable results.

Count a gain only with quality inside the limits defined beforehand. Present results
by model and category with their uncertainty. Mean and standard deviation describe the
sample; they do not prove improvement. If you bootstrap, resample paired cases
preserving repetitions, recompute the total cost/successes ratio in each sample, and
identify samples with no successes. Insufficient data = inconclusive.

## Records and presentation

Create one folder per iteration/case/variant in the authorized artifact area. Record
prompt, inputs, version hashes, configuration, output, transcript, judgment, time, and
observed consumption. Never expose secrets in the records. For this skill the area is
`evals/benchmarks/<date>/`: `summary.json`, `benchmark.md` and `tokens.json` are kept in
version control; workspaces, transcripts and `review.html` are not.

When the skill-creator plugin is installed and compatible, use its aggregator and
viewer instead of rebuilding them, validating the schemas of the installed version.
Otherwise present the artifacts, a results table, and per-case feedback. Keep the same
evaluation contract without assuming specific tools or notifications.

Report what was executed and what is only prepared. A test that receives a model's
label to check routing is not a run on that model. Close with the decision and its
limits: a static reduction in words or a single run is not evidence of efficiency.
