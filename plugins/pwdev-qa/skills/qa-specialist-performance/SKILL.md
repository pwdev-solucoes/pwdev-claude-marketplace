---
name: qa-specialist-performance
description: Design bounded performance profiles with explicit load authorization, contextual samples, percentiles, and agreed thresholds.
---

# QA performance specialist

Use this specialist when a QA workflow needs performance coverage derived from an identified
contract and workload profile. This specialist does not execute a workflow or tests and cannot grant authorization.
Read [workflow](../../references/workflow.md),
[safety](../../references/safety.md), and [tooling](../../references/tooling.md) before advising
the calling workflow.

## Inputs

- Target, environment, build/configuration identity, identified contract, and preserved criterion
  IDs and text.
- User or traffic model, operation mix, arrival/concurrency profile, warm-up, duration, dataset,
  cache state, dependencies, expected scale, and recovery expectations.
- Agreed metrics and thresholds, including percentile, unit, measurement boundary, error rate,
  throughput, resource limits, and pass condition.
- Explicit load authorization naming target, limits, environment, and time window, plus stop
  conditions and owner contacts when execution could affect a shared system.
- Runner and prerequisite probes with `state`, `result`, and `evidence`, access constraints, and
  existing baseline evidence.

## Procedure

1. Preserve the target, contract, criteria, thresholds, and authorization supplied by the caller.
   A tool probe, staging label, or prior test never grants current load permission.
2. Define a bounded profile: workload model, operation mix, users/rate, ramp, warm-up, duration,
   dataset, cache state, dependency state, collection interval, stop conditions, and evidence.
3. Before proposing execution to the calling workflow, verify explicit authorization covers the
   exact target, limits, environment, and time window. Without it, the profile may be documented,
   but workload execution is `BLOCKED` and must remain `not run`.
4. Ask `qa-tooling` to classify the runner and prerequisites as `available`, `missing`, or
   `unverified` from probes. Never install a load tool or turn tool presence into proof of target
   readiness or authorization.
5. For each metric, preserve the sample size and measurement context and report applicable p50,
   p95, and p99 latency percentiles alongside throughput, errors, saturation, and variability.
   Compare only like-for-like baselines and state exclusions and uncertainty.
6. Compare the agreed percentile and other limits to observed results. An average alone or an
   isolated average does not support `PASS`, `READY`, or approval because it hides tail latency
   and lacks distribution, sample, and context.
7. Return the plan or supplied assessment. Use exactly `PASS`, `FAIL`, `BLOCKED`, `NOT_RUN`, or
   `NOT_APPLICABLE` for cases/criteria and `PASS`, `FAIL`, or `BLOCKED` globally; a proven current
   failure still takes precedence over pending performance work.

## Output

Return:

- target, contract, criteria, environment/build, authorization scope, workload profile, dataset,
  cache/dependency state, time window, stop conditions, and tools;
- metrics and agreed thresholds with units and measurement boundaries;
- expected and observed values kept distinct, including sample size, context, p50/p95/p99,
  throughput, errors, resource saturation, variability, and baseline comparability;
- exact probe evidence, defects, blockers, limitations, verdict inputs, and next valid action.

`READY` below means an authorized, bounded proposal has sufficient oracles for a calling workflow.
It is not execution evidence, a case result, or a global verdict.

## Reference scenarios

| scenario | authorization | workload | sample | context | percentiles | threshold | outcome |
|---|---|---|---|---|---|---|---|
| authorized-profile | explicit and bounded | 50 VUs for 10 minutes | 12000 requests | staging build abc123 warm cache | p50 80 ms, p95 210 ms, p99 290 ms | p95 at most 250 ms | READY |
| average-only | missing | not run | unspecified | unspecified environment and build | missing | p95 at most 250 ms | BLOCKED |

In `authorized-profile`, the values illustrate a plan/assessment contract with a bounded grant,
sample, environment/build/cache context, distribution, and agreed oracle; they do not claim this
repository executed load. In `average-only`, no load is run: missing authorization plus an
isolated average without a sample or percentiles cannot support approval.

## Failure modes

- Missing, unclear, stale, or wrong-target load authorization: record the exact operation as
  `BLOCKED`/`NOT_RUN`; do not generate traffic.
- Missing workload, environment/build identity, dataset, cache/dependency state, sample, metric,
  percentile, unit, threshold, or measurement boundary: expose the gap and do not approve.
- Average-only result, tiny/unknown sample, omitted tail latency, or incomparable baseline:
  preserve the observation but block the unsupported conclusion.
- Missing/not-run probe: report `unverified`; explicit negative runner probe: report `missing` and
  propose a safe existing alternative without installation.
- Errors, saturation, unstable dependencies, interrupted collection, or breached stop condition:
  stop an authorized calling workflow, retain valid observations, and report limitations; never
  discard a proven failure to manufacture success.

## Safety

- This specialist cannot grant load, production, network, third-party, external-effect,
  penetration-test, or destructive-operation authorization.
- A calling workflow may execute load only inside explicit target, limits, environment, and time
  window boundaries and must obey stop conditions.
- Never execute stored commands, install tools, alter personal configuration, publish, push,
  merge, or correct product code.
- Use synthetic or reviewed data, avoid secrets and personal data, and apply evidence confinement,
  target binding, and sanitization before attachment.

## Related skills

- `qa-tooling` owns probe-based performance-runner availability and alternatives.
- `qa-test` may execute a separately authorized bounded profile and bind evidence.
- `qa-specialist-data` supplies data integrity and transaction concerns for data-heavy profiles.
- `qa-specialist-observability` may supply authorized resource and dependency observations.
