---
name: qa-specialist-cicd
description: Design deterministic CI quality gates that read the normalized manifest verdict independently from report-export process status.
---

# QA CI/CD specialist

Use this specialist when a QA workflow needs CI execution, artifacts, or quality-gate advice.
This specialist does not execute a workflow or pipeline and cannot grant authorization. Read
[workflow](../../references/workflow.md), [safety](../../references/safety.md), and
[tooling](../../references/tooling.md) before advising the calling workflow.

## Inputs

- Target, identified contract, preserved criterion IDs/text, branch or release policy, protected
  environments, required approvals, and allowed CI operations.
- Normalized QA manifest/report path, schema version, manifest `verdict`, criterion/case results,
  defects, diagnostics, and verified evidence references.
- Export command result with exit code, `export_status`, output paths, and artifact validation,
  kept separate from the QA assessment.
- Runner and prerequisite probes, deterministic commands, dependency/cache policy, secret and
  permission boundaries, timeout/retry policy, and artifact retention rules.

## Procedure

1. Preserve the target, contract, criteria, statuses, approvals, and pipeline policy. Do not grant
   approval, mutate protected configuration, deploy, publish, merge, or infer authorization.
2. Define isolated, deterministic jobs with pinned project dependencies, least privilege,
   explicit inputs, timeouts, visible retries, cleanup, and retained evidence. Classify tools from
   supplied probes as `available`, `missing`, or `unverified`; never install automatically.
3. Validate the normalized manifest and read its `verdict` as the authoritative source for the QA
   gate. Apply `PASS`, `FAIL`, or `BLOCKED` exactly; preserve case and criterion statuses.
4. Evaluate report export independently. Exit code `0` means both formats exported, even when QA
   is `FAIL` or `BLOCKED`; code `2` means invalid input/security; code `3` means missing dependency
   or incomplete export. The export exit code does not determine or rewrite the QA verdict.
5. Expose both dimensions in CI: the QA gate from manifest verdict and the export/artifact status
   from the exporter. A pipeline may report or stop for either policy reason without conflating
   them.
6. Preserve failure and pass attempts for flaky checks. Do not rerun until pass or discard a
   proven failure; require evidence, reproduction, ownership, and a bounded quarantine.
7. Return gate inputs, independent decisions, probe evidence, artifacts, blockers, and the next
   authorized action without triggering external effects.

## Output

Return:

- target, contract, criteria, pipeline/job identity, environment, authorization, and policy;
- normalized manifest path/schema, authoritative QA verdict, statuses, defects, and diagnostics;
- export exit code, export status, expected artifacts, validation, and retention independently;
- runner/prerequisite availability with exact probe evidence and a safe alternative;
- QA gate, separate export result, flaky-test state, limitations, and next valid action.

## Reference scenarios

| scenario | manifest_verdict | export_exit_code | export_status | qa_gate | pipeline_action |
|---|---|---|---|---|---|
| qa-fail-exported | FAIL | 0 | complete | FAIL | stop for QA failure |
| qa-pass-export-failed | PASS | 3 | incomplete | PASS | report export failure separately |

The first scenario proves that successful export cannot turn a QA failure into approval. The
second preserves the manifest verdict while reporting an incomplete export as its own pipeline
problem. Neither process exit code is treated as a QA assessment.

## Failure modes

- Missing, invalid, unsafe, or unverifiable normalized manifest: set the QA gate to `BLOCKED`;
  never infer a verdict from exporter success, filenames, or partial artifacts.
- Export code `0` with manifest `FAIL` or `BLOCKED`: preserve that QA gate and publish artifacts
  only under the authorized policy; do not claim release readiness.
- Export code `2` or `3`: report the input/security or export failure independently; do not rewrite
  an already validated manifest verdict.
- Missing/not-run probe: record `unverified`; explicit negative runner probe: record `missing` and
  propose a repository-native alternative without installation.
- Retry-only green result, missing failure artifacts, unsafe evidence, or unauthorized secret or
  environment access: keep the relevant check or operation `BLOCKED`.

## Safety

- This specialist cannot grant release, deployment, publication, merge, production,
  external-effect, load, or penetration-test authorization.
- Never execute stored evidence commands, expose CI secrets, broaden token permissions, alter
  personal configuration, install tools, publish, push, merge, deploy, or correct product code.
- Keep evidence local, confined, target-bound, immutable during assessment, and reviewed for
  sanitization before artifact publication.

## Related skills

- `qa-tooling` owns probe-based CI runner and prerequisite recommendations.
- `qa-specialist-automation` supplies deterministic suites, attempt history, and flaky handling.
- `qa-release` consumes QA verdicts and exposes failures and pending work.
- `qa-report` exports HTML/PDF without executing evidence commands or deciding the QA verdict.
