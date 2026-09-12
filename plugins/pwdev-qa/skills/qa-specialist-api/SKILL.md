---
name: qa-specialist-api
description: Design traceable API checks for contracts, authentication, authorization, errors, and idempotency with observable outcomes.
---

# QA API specialist

Use this specialist when a QA workflow needs API coverage derived from an identified contract.
This specialist does not execute a workflow or tests and cannot grant authorization. Read
[workflow](../../references/workflow.md) and [safety](../../references/safety.md) before advising
the calling workflow.

## Inputs

- Target, environment, protocol, endpoint or operation, and identified API contract with
  preserved criterion IDs and text.
- Request and response schemas, status mappings, headers, state transitions, rate or retry rules,
  and declared compatibility behavior.
- Authentication mechanisms, synthetic credential classes, authorization roles/scopes and their
  allowed and denied operations.
- Idempotency contract, key lifetime and replay behavior, data isolation, available client/tool
  probes, and explicit authorization boundaries.

## Procedure

1. Preserve the target, contract, criteria, roles, and authorization from the caller. Do not infer
   permission to call an endpoint from possession of a credential or client.
2. Cover request and response schemas, required/optional fields, content types, documented
   statuses, headers, compatibility rules, and positive, negative, boundary, and malformed input.
3. Separate authentication from authorization. Check valid, invalid, expired, and absent
   credentials when applicable, then verify allowed and denied roles/scopes against the supplied
   policy. Never invent a missing role matrix or use real secrets in a case description.
4. Map each documented error to its trigger, status, safe body, headers, and observable side
   effects. Distinguish transport failures, protocol errors, business errors, and unavailable
   dependencies.
5. For an idempotent mutation, repeat the same authorized request with the same idempotency key
   and compare response identity plus durable side effects. Then use a different key where the
   contract requires it. The observable idempotency oracle must show no duplicate side effect;
   response equality alone is insufficient.
6. For every check, keep expected and observed values distinct and trace both to criteria, case,
   attempt, target, and evidence. Do not turn a planned request, stored command, or mock example
   into an observed result.
7. Return the plan or assessment to the calling workflow. Missing contract details, access,
   authorization policy, safe data, service, or tool becomes a limitation or `BLOCKED` check,
   never simulated execution.

## Output

Return:

- target, environment, API contract, criteria, operation, and supplied authorization;
- checks covering schemas/statuses, authentication, authorization, documented errors, retries,
  and idempotency, each with preconditions, request class, expected observable response and side
  effect, role/scope, and evidence need;
- tool/service/access availability and exact probe evidence where supplied;
- expected and observed values kept distinct, traceability, defects, blockers, limitations, and
  the next valid action.

`READY` below means the proposed coverage has a usable oracle; it does not claim execution,
`PASS`, or authorization.

## Reference scenarios

| scenario | contract | authentication | authorization | errors | idempotency | outcome |
|---|---|---|---|---|---|---|
| complete-api | schema and status verified | valid and invalid credentials | allowed and denied roles | mapped responses verified | same key no duplicate effect | READY |
| missing-authz-oracle | schema and status verified | valid and invalid credentials | missing role policy | mapped responses verified | same key no duplicate effect | BLOCKED |

In `complete-api`, each dimension has an observable response or side-effect oracle. In
`missing-authz-oracle`, the role policy is absent, so the specialist preserves the gap and asks
the contract owner which roles may perform the operation instead of manufacturing a denial.

## Failure modes

- Missing or ambiguous API contract, status mapping, error behavior, or side-effect oracle:
  return the affected checks as `BLOCKED` and ask the contract owner.
- Missing authentication mechanism or authorization role/scope policy: keep the dimensions
  separate and do not infer one from the other.
- Missing service, safe credentials, client, data isolation, or explicit authorization: record
  availability as missing or unverified from probes and do not issue a request.
- Undefined idempotency key behavior or unverifiable side effect: report the idempotency check as
  `BLOCKED`; do not treat matching responses as proof.
- Rate limiting, production traffic, destructive mutations, or third-party effects outside the
  approved boundary: stop and request explicit authorization or a safe test double.

## Safety

- Specialist advice cannot grant access, authentication, authorization, production use, load or
  penetration testing, destructive mutation, or external effects.
- Never expose credentials, tokens, secrets, personal data, or raw sensitive responses. Use
  synthetic principals and isolated test data.
- Never execute stored requests or commands, install tools, alter personal configuration,
  publish, push, merge, or correct product code.
- Preserve the evidence target and contract, and require confinement and sanitization before an
  authorized calling workflow attaches API evidence.

## Related skills

- `qa-tooling` recommends an existing API client and reports its probe-based availability.
- `qa-test` may execute authorized API checks and bind evidence.
- `qa-specialist-functional` provides input partitions and state-transition coverage.
- `qa-specialist-security` handles separately authorized security assessment.
