---
name: qa-specialist-production
description: Plan explicitly authorized read-only production observations and trace evidence-backed causes into preventive regression coverage without external effects.
---

# QA production specialist

Use this specialist when a QA workflow needs production observations, incident QA analysis, or
preventive regression advice. This specialist does not execute a workflow or production observation
and cannot grant authorization. Read [workflow](../../references/workflow.md),
[safety](../../references/safety.md), [artifacts](../../references/artifacts.md), and
[tooling](../../references/tooling.md) before advising the calling workflow.

## Inputs

- Target, service/environment identity, identified contract, preserved criterion IDs/text,
  incident/change identity, and requested question.
- Explicit production-observation authorization naming the target, approved telemetry sources,
  identities/roles, read-only boundary, fields, time window, owner, data-handling rules, stop
  conditions, and evidence-retention boundary.
- Existing logs, metrics, alerts, traces or incident timeline supplied through authorized access,
  with query/probe evidence, target binding, and sanitization review.
- Candidate cause, uncertainty, supporting and contradicting evidence, defect links, prior
  attempts, and proposed preventive regression oracle.

## Procedure

1. Preserve the target, contract, criteria, incident state, approvals, and requested operation.
   Separate production observation from test execution, remediation, deployment, messaging, and
   any other external effect.
2. Before any calling workflow observes production, verify explicit authorization for the exact
   target, existing telemetry sources, identity/role, read-only boundary, permitted fields, time
   window, owner, data handling, stop conditions, and retention. Missing, unclear, stale, or
   wrong-target authorization leaves observation `NOT_RUN` and the proposal `BLOCKED`.
3. Restrict the plan to reading approved existing telemetry inside that boundary. Do not create
   traffic, synthetic transactions, probes that change state, messages, tickets, configuration,
   deployments, acknowledgements, or remediation. External effects remain absent even when
   read-only production observation is authorized.
4. Record timestamps, query/probe identity, expected and observed signals, gaps, uncertainty, and
   reviewed evidence. Classify observability tools as `available`, `missing`, or `unverified`
   only from supplied probes; never request secrets or use personal sessions.
5. Distinguish correlation, contributing condition, and root cause. Claim a cause only when named,
   target-bound evidence supports it and contrary evidence is addressed; otherwise retain it as
   a hypothesis and mark the causal conclusion `BLOCKED`.
6. Link prevention of recurrence to the supported cause, evidence IDs, affected criterion/risk or
   explicit unlinked defect, and a deterministic regression check with expected observable
   behavior. A generic test unrelated to the cause is not preventive regression coverage.
7. Apply shared verdict precedence. A proven current in-scope production defect is `FAIL`, even
   without a criterion association. Missing authorization or evidence is `BLOCKED` when no proven
   failure exists. Return findings and the next authorized action without executing external effects.

## Output

Return:

- target, contract, criteria, incident/change identity, owner, and exact authorization boundary;
- telemetry sources, identity/role, fields, time window, queries/probes, expected/observed signals,
  evidence references, gaps, and uncertainty;
- incident timeline, defect links, correlation/contributing-condition/cause classification, and
  supporting or contradicting evidence;
- preventive regression proposal linked to cause, evidence, criterion/risk or explicit unlinked
  reason, stable case ID, oracle, environment, and prerequisites;
- external-effects statement, current defects, blockers, limitations, global verdict input, and
  next valid action.

`READY` below means the bounded observation record and preventive proposal are traceable. It is not
permission to access production, proof that an observation was executed by this specialist, or a
deployment decision.

## Reference scenarios

| scenario | authorization | target | telemetry_sources | identity_role | read_only_boundary | fields | window | owner | data_rules | stop_conditions | retention | observation | external_effects | cause | evidence | criterion_risk_or_unlinked | stable_case_id | oracle | environment | prerequisites | outcome |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| authorized-observation | explicit read-only production grant | prod-api/session-service | existing metrics auth_failures and latency | qa-observer read-only | metrics query only | timestamp route status latency_ms | 2026-09-12T10:00Z to 2026-09-12T11:00Z | production-owner | aggregate only no personal data | unexpected sensitive field or access error | reviewed aggregate evidence for 30 days | approved existing telemetry only | none | session cache expiry race with contrary evidence addressed | EV-PROD-001 reviewed and target-bound | AC-SESSION-02 and RISK-AUTH-04 | TC-SESSION-EXPIRY-RACE | one refresh and no authentication failure at expiry | staging with production-equivalent cache timing | synthetic account and controllable clock | READY |
| missing-authorization | missing | prod-api/session-service | existing metrics auth_failures and latency | qa-observer read-only | metrics query only | timestamp route status latency_ms | 2026-09-12T10:00Z to 2026-09-12T11:00Z | production-owner | aggregate only no personal data | unexpected sensitive field or access error | reviewed aggregate evidence for 30 days | NOT_RUN | none | not assessed | none | not assessed | NOT_RUN | NOT_RUN | NOT_RUN | NOT_RUN | BLOCKED |
| missing-target | explicit read-only production grant | missing | existing metrics auth_failures and latency | qa-observer read-only | metrics query only | timestamp route status latency_ms | 2026-09-12T10:00Z to 2026-09-12T11:00Z | production-owner | aggregate only no personal data | unexpected sensitive field or access error | reviewed aggregate evidence for 30 days | NOT_RUN | none | not assessed | none | not assessed | NOT_RUN | NOT_RUN | NOT_RUN | NOT_RUN | BLOCKED |
| missing-telemetry-sources | explicit read-only production grant | prod-api/session-service | missing | qa-observer read-only | metrics query only | timestamp route status latency_ms | 2026-09-12T10:00Z to 2026-09-12T11:00Z | production-owner | aggregate only no personal data | unexpected sensitive field or access error | reviewed aggregate evidence for 30 days | NOT_RUN | none | not assessed | none | not assessed | NOT_RUN | NOT_RUN | NOT_RUN | NOT_RUN | BLOCKED |
| missing-identity-role | explicit read-only production grant | prod-api/session-service | existing metrics auth_failures and latency | missing | metrics query only | timestamp route status latency_ms | 2026-09-12T10:00Z to 2026-09-12T11:00Z | production-owner | aggregate only no personal data | unexpected sensitive field or access error | reviewed aggregate evidence for 30 days | NOT_RUN | none | not assessed | none | not assessed | NOT_RUN | NOT_RUN | NOT_RUN | NOT_RUN | BLOCKED |
| missing-read-only-boundary | explicit read-only production grant | prod-api/session-service | existing metrics auth_failures and latency | qa-observer read-only | missing | timestamp route status latency_ms | 2026-09-12T10:00Z to 2026-09-12T11:00Z | production-owner | aggregate only no personal data | unexpected sensitive field or access error | reviewed aggregate evidence for 30 days | NOT_RUN | none | not assessed | none | not assessed | NOT_RUN | NOT_RUN | NOT_RUN | NOT_RUN | BLOCKED |
| missing-fields | explicit read-only production grant | prod-api/session-service | existing metrics auth_failures and latency | qa-observer read-only | metrics query only | missing | 2026-09-12T10:00Z to 2026-09-12T11:00Z | production-owner | aggregate only no personal data | unexpected sensitive field or access error | reviewed aggregate evidence for 30 days | NOT_RUN | none | not assessed | none | not assessed | NOT_RUN | NOT_RUN | NOT_RUN | NOT_RUN | BLOCKED |
| missing-window | explicit read-only production grant | prod-api/session-service | existing metrics auth_failures and latency | qa-observer read-only | metrics query only | timestamp route status latency_ms | missing | production-owner | aggregate only no personal data | unexpected sensitive field or access error | reviewed aggregate evidence for 30 days | NOT_RUN | none | not assessed | none | not assessed | NOT_RUN | NOT_RUN | NOT_RUN | NOT_RUN | BLOCKED |
| missing-owner | explicit read-only production grant | prod-api/session-service | existing metrics auth_failures and latency | qa-observer read-only | metrics query only | timestamp route status latency_ms | 2026-09-12T10:00Z to 2026-09-12T11:00Z | missing | aggregate only no personal data | unexpected sensitive field or access error | reviewed aggregate evidence for 30 days | NOT_RUN | none | not assessed | none | not assessed | NOT_RUN | NOT_RUN | NOT_RUN | NOT_RUN | BLOCKED |
| missing-data-rules | explicit read-only production grant | prod-api/session-service | existing metrics auth_failures and latency | qa-observer read-only | metrics query only | timestamp route status latency_ms | 2026-09-12T10:00Z to 2026-09-12T11:00Z | production-owner | missing | unexpected sensitive field or access error | reviewed aggregate evidence for 30 days | NOT_RUN | none | not assessed | none | not assessed | NOT_RUN | NOT_RUN | NOT_RUN | NOT_RUN | BLOCKED |
| missing-stop-conditions | explicit read-only production grant | prod-api/session-service | existing metrics auth_failures and latency | qa-observer read-only | metrics query only | timestamp route status latency_ms | 2026-09-12T10:00Z to 2026-09-12T11:00Z | production-owner | aggregate only no personal data | missing | reviewed aggregate evidence for 30 days | NOT_RUN | none | not assessed | none | not assessed | NOT_RUN | NOT_RUN | NOT_RUN | NOT_RUN | BLOCKED |
| missing-retention | explicit read-only production grant | prod-api/session-service | existing metrics auth_failures and latency | qa-observer read-only | metrics query only | timestamp route status latency_ms | 2026-09-12T10:00Z to 2026-09-12T11:00Z | production-owner | aggregate only no personal data | unexpected sensitive field or access error | missing | NOT_RUN | none | not assessed | none | not assessed | NOT_RUN | NOT_RUN | NOT_RUN | NOT_RUN | BLOCKED |
| hypothetical-cause | explicit read-only production grant | prod-api/session-service | existing metrics auth_failures and latency | qa-observer read-only | metrics query only | timestamp route status latency_ms | 2026-09-12T10:00Z to 2026-09-12T11:00Z | production-owner | aggregate only no personal data | unexpected sensitive field or access error | reviewed aggregate evidence for 30 days | approved existing telemetry only | none | hypothesis only | insufficient to support cause | AC-SESSION-02 and RISK-AUTH-04 | TC-SESSION-EXPIRY-RACE | one refresh and no authentication failure at expiry | staging with production-equivalent cache timing | synthetic account and controllable clock | BLOCKED |
| generic-prevention | explicit read-only production grant | prod-api/session-service | existing metrics auth_failures and latency | qa-observer read-only | metrics query only | timestamp route status latency_ms | 2026-09-12T10:00Z to 2026-09-12T11:00Z | production-owner | aggregate only no personal data | unexpected sensitive field or access error | reviewed aggregate evidence for 30 days | approved existing telemetry only | none | session cache expiry race with contrary evidence addressed | EV-PROD-001 reviewed and target-bound | missing | missing | missing | missing | missing | BLOCKED |

The successful scenario exposes each authorization component separately, remains read-only, names
the supported cause, and materializes a deterministic preventive case linked to evidence and the
affected criterion/risk. Every missing-boundary scenario keeps observation `NOT_RUN`. A hypothetical
cause or generic prevention proposal remains `BLOCKED` even when observation was authorized.

## Failure modes

- Missing, ambiguous, stale, or wrong-target authorization, source, identity, fields, window,
  owner, data rule, stop condition, or retention boundary: record observation `NOT_RUN` and
  outcome `BLOCKED`; do not access production.
- Requested write, traffic generation, ticket/message, acknowledgement, configuration,
  deployment, remediation, or other external effect: stop and separate it from this read-only
  specialist; authorization to observe does not authorize that effect.
- Correlation without cause evidence, contradictory evidence not addressed, or incomplete
  timeline: preserve the hypothesis and uncertainty; do not claim root cause or complete prevention.
- Preventive check not linked to cause and evidence: retain it as generic coverage, not prevention
  of recurrence, and block the preventive conclusion.
- Proven current in-scope defect, including one without criteria: return `FAIL`; do not hide it
  behind missing observations or passed checks.
- Unsafe, changed, missing, personal, secret-bearing, or target-incompatible evidence: do not
  attach it and prevent `PASS`.

## Safety

- This specialist cannot grant production, external-effect, test-execution, load,
  penetration-test, deployment, publication, or merge authorization.
- Never execute production queries or stored commands, create traffic, change third-party state,
  expose secrets/personal data, reuse personal sessions, install tools, publish, push, merge,
  deploy, or correct product code.
- Use only supplied synthetic or reviewed evidence. Apply confinement, target binding, hashing,
  least privilege, minimization, retention, and sanitization before attachment.

## Related skills

- `qa-specialist-observability` may define approved telemetry and probe requirements when present.
- `qa-specialist-defects` records the incident defect, severity, priority, history, and retest.
- `qa-specialist-regression` selects the preventive check by impact and traceability.
- `qa-test` may execute that check later in a separately authorized non-production environment.
- `qa-tooling` owns probe-based observability recommendations and safe alternatives.
