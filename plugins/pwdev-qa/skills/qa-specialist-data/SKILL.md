---
name: qa-specialist-data
description: Design traceable data checks for reconciliation, integrity, transactions, and atomicity with separate observable oracles.
---

# QA data specialist

Use this specialist when a QA workflow needs data coverage derived from an identified contract.
This specialist does not execute a workflow or tests and cannot grant authorization. Read
[workflow](../../references/workflow.md), [safety](../../references/safety.md), and
[tooling](../../references/tooling.md) before advising the calling workflow.

## Inputs

- Target, environment, data engine, identified contract, and preserved criterion IDs and text.
- Source and target schemas, mappings, keys, constraints, relationships, totals, tolerances, and
  expected transformation rules.
- Transaction boundaries, isolation and concurrency rules, commit/rollback behavior, retry or
  recovery semantics, and the observable durable state.
- Safe synthetic or reviewed dataset, read/write boundary, backups where applicable, and explicit
  authorization for every mutation or production observation.
- Tool and prerequisite probes, each with `state`, `result`, and `evidence`, plus access limits.

## Procedure

1. Preserve the supplied target, contract, criteria, approvals, and access boundary. Do not infer
   write or production permission from the presence of a database client or credential.
2. Design reconciliation checks that compare declared source and target populations, keys,
   counts, sums, transformations, duplicates, omissions, and tolerances. Record the comparison
   scope and denominator.
3. Design integrity checks for type/domain rules, uniqueness, nullability, referential links,
   invariants, and lineage. Reconciliation does not prove atomicity, and integrity does not prove
   transaction behavior; keep their observations separate.
4. Design transaction checks around declared boundaries and isolation: observe successful commit,
   forced failure and rollback, concurrency where applicable, retry, and recovery. Atomicity needs
   an oracle showing that a failed unit leaves no partial durable write.
5. Ask `qa-tooling` to classify clients and prerequisites as `available`, `missing`, or
   `unverified` from supplied probes. An absent probe remains unverified; never install a client
   or fabricate access.
6. Keep expected and observed values distinct and trace each result to case, attempt, criterion,
   target, dataset, and evidence. A matching aggregate alone does not establish row integrity,
   transactional isolation, or atomicity.
7. Return coverage or assessment to the calling workflow. Use only `PASS`, `FAIL`, `BLOCKED`,
   `NOT_RUN`, or `NOT_APPLICABLE` for case/criterion results and only `PASS`, `FAIL`, or `BLOCKED`
   for a global verdict when the calling workflow has execution evidence.

## Output

Return:

- target, contract, criteria, environment, schema/data identities, authorization, and dataset;
- distinct reconciliation, integrity, transaction, and atomicity checks with expected observable
  result, scope, denominator, preconditions, and evidence need;
- tool/access availability with exact probe evidence and a safe alternative;
- supplied observations kept distinct from planned checks, plus defects, blockers, limitations,
  and the next valid action.

`READY` below means the proposed coverage has usable oracles. It is not a case result, proof of
execution, authorization, or global verdict.

## Reference scenarios

| scenario | authorization | target | dataset | write_limit | evidence | reconciliation | integrity | transaction | atomicity | outcome |
|---|---|---|---|---|---|---|---|---|---|---|
| complete-data-check | explicit mutation grant | qa-db.orders | synthetic orders v1 | 20 rows in one transaction | EV-DATA-001 | source and target totals match | constraints and relationships verified | commit and rollback observed | failure leaves no partial write | READY |
| missing-data-authorization | missing | qa-db.orders | synthetic orders v1 | 20 rows in one transaction | EV-DATA-001 | NOT_RUN | NOT_RUN | NOT_RUN | unverified | BLOCKED |
| missing-data-target | explicit mutation grant | missing | synthetic orders v1 | 20 rows in one transaction | EV-DATA-001 | NOT_RUN | NOT_RUN | NOT_RUN | unverified | BLOCKED |
| missing-data-dataset | explicit mutation grant | qa-db.orders | missing | 20 rows in one transaction | EV-DATA-001 | NOT_RUN | NOT_RUN | NOT_RUN | unverified | BLOCKED |
| missing-write-limit | explicit mutation grant | qa-db.orders | synthetic orders v1 | missing | EV-DATA-001 | NOT_RUN | NOT_RUN | NOT_RUN | unverified | BLOCKED |
| missing-data-evidence | explicit mutation grant | qa-db.orders | synthetic orders v1 | 20 rows in one transaction | missing | NOT_RUN | NOT_RUN | NOT_RUN | unverified | BLOCKED |

The complete scenario carries the mutation grant and its target, synthetic dataset, write limit,
and target-bound evidence before presenting the four separate observations as `READY`. Every
limitation row omits one required component and therefore keeps reconciliation, integrity, and
transaction `NOT_RUN`, atomicity unverified, and the outcome `BLOCKED`.

## Failure modes

- Missing mapping, schema, key, tolerance, invariant, transaction boundary, or observable oracle:
  return the affected check as `BLOCKED` and ask the contract owner for the missing rule.
- Aggregate totals match but row-level integrity is unverified: preserve the reconciliation
  observation and block the unsupported integrity conclusion.
- Commit succeeds but rollback or partial-write state is unobserved: do not claim transaction or
  atomicity coverage.
- Missing, not-run, or ambiguous probe: report `unverified`; explicit negative tool probe:
  report `missing`. Neither state is simulated execution.
- Unsafe data, unavailable isolation, unclear access, production target, or destructive operation
  outside authorization: stop before access and record the exact blocked operation.

## Safety

- This specialist cannot grant database access, mutation, production observation, destructive
  operation, load testing, penetration testing, or external-effect authorization.
- Never expose credentials, secrets, or personal data; use synthetic or reviewed data and least
  privilege within the supplied boundary.
- Never execute stored queries or commands, install tools, alter personal configuration, publish,
  push, merge, or correct product code.
- Bind evidence to the exact target, contract, schema/build, dataset, and attempt, then apply local
  confinement and sanitization before attachment.

## Related skills

- `qa-tooling` owns probe-based data-tool availability and safe alternatives.
- `qa-test` may execute explicitly authorized data checks and bind evidence.
- `qa-specialist-functional` supplies state, boundary, and error partitions.
- `qa-specialist-performance` handles separately authorized data workload performance.
