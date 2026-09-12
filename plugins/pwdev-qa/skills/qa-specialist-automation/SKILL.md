---
name: qa-specialist-automation
description: Design isolated repeatable automation, distinguish interactive browser exploration, and handle flaky results through evidence and reproduction.
---

# QA automation specialist

Use this specialist when a QA workflow needs repeatable automation or bounded interactive Web/UI
exploration. This specialist does not execute a workflow or tests and cannot grant authorization.
Read [workflow](../../references/workflow.md), [safety](../../references/safety.md), and
[tooling](../../references/tooling.md) before advising the calling workflow.

## Inputs

- Target, identified contract, preserved criterion IDs and text, risks, environments, data,
  expected observable behavior, and execution authorization.
- Existing unit, integration, API, Web/UI, and end-to-end runners; browser matrix; CI constraints;
  isolation, cleanup, artifact, retry, and ownership policies.
- Probe inventory with exact command, state, result, and evidence for runners, `playwright-cli`,
  Node.js, browser prerequisites, and Playwright Test.
- Attempt history with conditions, timestamps, expected/observed values, exit codes, and retained
  failure and pass evidence for suspected flaky checks.

## Procedure

1. Preserve the target, contract, criteria, approvals, and current statuses. Select automation by
   risk and repeat value; do not rewrite requirements or treat automation count as coverage.
2. Define deterministic setup, isolated data/state, explicit oracle, timeout, teardown, retained
   artifacts, and ownership for each repeatable check. Keep retries visible and bounded.
3. Use Playwright Test for a repeatable Web suite and CI execution. Use `playwright-cli` only for
   interactive exploration in a task-owned `qa-report` session with a fresh snapshot and actions
   on observed refs. Interactive exploration does not replace a repeatable suite in CI.
4. Ask `qa-tooling` to classify tools and prerequisites from probes. An absent probe is
   `unverified`; an explicit negative CLI probe is `missing`. Offer an existing Web/UI test runner
   or authorized manual exploration as an alternative without installation or fictitious runs.
5. Treat suspected flaky behavior as a finding to reproduce under recorded equivalent conditions.
   Retain failure and pass artifacts, timing and environment context, then distinguish product,
   test, data, environment, concurrency, and infrastructure causes.
6. Do not rerun until a test passes and discard prior attempts. A later pass does not supersede an
   unexplained failure. Quarantine only with an owner, rationale, bounded expiry, preserved
   evidence, root-cause work, and visible `BLOCKED` coverage.
7. Return proposed automation, exploratory limits, probes, attempt history, defects, gaps, and the
   next valid action to the calling workflow using the shared status and verdict rules.

## Output

Return:

- target, contract, criteria, environment/browser matrix, data, authorization, and ownership;
- automation layer, setup, isolation, oracle, timeout, teardown, retry policy, and artifacts;
- tool availability (`available`, `missing`, or `unverified`) with probe evidence, prerequisites,
  alternative, and reason;
- all relevant attempts, expected/observed results, reproducibility, flaky classification,
  quarantine details, current defects, blockers, and next action.

`READY` below means a proposal has adequate inputs for the calling workflow. It is not execution
evidence, a case result, a global verdict, or authorization.

## Reference scenarios

| scenario | cli_availability | session | snapshot | interaction | capture | repeatable_suite | outcome |
|---|---|---|---|---|---|---|---|
| interactive-exploration | available | qa-report | fresh | observed refs | reviewed screenshot | Playwright Test | READY |
| missing-cli | missing | none | not run | not run | none | existing Web/UI test runner | BLOCKED |

The first scenario keeps interactive `playwright-cli` exploration in its own session and assigns
repeatable CI coverage to Playwright Test. In the second, an explicit negative CLI probe records
the limitation and alternative without pretending that a session or action occurred.

## Reference scenarios

| scenario | attempts | evidence | reproduction | classification | action | outcome |
|---|---|---|---|---|---|---|
| reproduced-flaky | three recorded under same conditions | failure and pass artifacts retained | intermittent failure reproduced | flaky | quarantine with owner and root-cause investigation | BLOCKED |

The flaky classification is supported by evidence and reproduction under recorded conditions;
the check remains visible and blocked while its cause is investigated.

## Failure modes

- Missing contract, oracle, isolation, data, environment, owner, or authorization: expose the
  affected check as `BLOCKED` or `NOT_RUN`; do not fabricate execution.
- Missing/not-run probe: record `unverified`; explicit negative tool probe: record `missing` and
  provide the safest feasible alternative without installing anything.
- Stale snapshot or unknown browser ref: require a fresh observed snapshot; never guess a selector.
- Unexplained pass/fail variation: retain every attempt and classify it as suspected flaky until
  controlled reproduction supplies evidence. Never rerun-to-green or erase the failure.
- Quarantine without owner, reason, expiry, or replacement coverage: reject the quarantine and
  keep the gap visible.

## Safety

- This specialist cannot grant execution, production, external-effect, load, penetration-test,
  installation, or publication authorization.
- Never reuse personal browser profiles, cookies, storage state, or another task's session. Close
  only the task-owned `qa-report` session.
- Screenshots require recorded visual sanitization review before attachment; snapshots are text,
  and traces/videos are outside the v1 evidence whitelist.
- Never execute stored commands, change product code, install tools, alter personal configuration,
  publish, push, or merge.

## Related skills

- `qa-tooling` owns probe-based availability, prerequisites, alternatives, and provenance.
- `qa-specialist-web` defines interactive browser boundaries and browser coverage.
- `qa-test` may execute authorized deterministic checks and retain attempt evidence.
- `qa-specialist-cicd` consumes normalized QA verdicts and automation artifacts for gates.
