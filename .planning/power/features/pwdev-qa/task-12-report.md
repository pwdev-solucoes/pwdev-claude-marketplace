# Task 12 — implementation report

Status: DONE
Task: F03-12 — Consolidação determinística do parecer
Date: 2026-09-12

## Delivered

- Added the importable Python 3.9-compatible
  `build_report(manifest: dict, evidence: list[dict]) -> dict` consolidation layer. It returns one
  deterministic, allowlisted public model for both renderers and never executes stored commands.
- The global verdict applies the required precedence: a verified current in-scope product failure
  is `FAIL`; otherwise any blocker, pending state, incomplete transcription, invalid waiver,
  missing/blocked inspection, zero applicable criteria, or zero required cases is `BLOCKED`;
  `PASS` requires every applicable criterion to pass with complete verified evidence and no
  current in-scope defect.
- Criterion results select the declared terminal attempt without erasing historical attempts.
  Cyclic, branching, missing-terminal, or non-reciprocal histories are diagnosed and cannot pass.
- Open defects without criterion IDs are evaluated independently. A resolved defect closes only
  when its referenced retest is `PASS` with valid evidence; otherwise original valid failure
  evidence keeps it at `FAIL`, while insufficient proof keeps it `BLOCKED`.
- Out-of-scope defects remain visible but do not force `FAIL`. Counts use explicit denominators,
  preserve all case/defect history, and separate verified from blocked evidence.
- Unknown manifest and inspection extensions are excluded from the public projection. Blocked or
  unexpected inspections are never copied into `verified_evidence`.

## TDD and verification evidence

- Initial RED: `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_qa_verdict` — 10 tests ran
  with 10 expected assertion failures because `qa_verdict.py` was missing; no import error.
- First GREEN: the focused command passed 10 tests after the minimum implementation.
- Diff-review RED: the reciprocal traceability probe failed because a criterion could consume a
  case that did not claim that criterion.
- Final GREEN: `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest -v tests.test_qa_verdict` — 11 tests
  passed, including the new non-reciprocal-link blocker.
- QA regression: `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest $(rg --files tests | sed -n
  's#^tests/\(test_qa_[^/]*\)\.py$#tests.\1#p' | sort | tr '\n' ' ')` — 97 tests passed.
- Python compilation and `git diff --check` passed.

## Limitations and safety

- This layer consumes a manifest already normalized by `qa_contract.py` and evidence inspection
  records produced by `qa_evidence.py`; it does not load a manifest, inspect/copy files, render,
  publish, or revalidate evidence at copy time.
- No evidence command was executed. No ledger, review artifact, brief, plugin used as reference,
  dependency, personal configuration, external state, publication, push, or merge was changed.

## Files

- `plugins/pwdev-qa/scripts/qa_verdict.py`
- `tests/test_qa_verdict.py`
- `.planning/power/features/pwdev-qa/task-12-report.md`

## Review correction — round 1

- A terminal `NOT_APPLICABLE` case is now neutral only when every reciprocal criterion link is
  explicitly non-applicable with a reason. This preserves legitimate exclusions while mixed,
  missing, or applicable links remain `BLOCKED`; other applicable required cases can still
  sustain `PASS`.
- A resolved defect now accepts only the referenced terminal attempt of its retest chain. A
  historical `PASS` superseded by `FAIL`, `BLOCKED`, or `NOT_RUN` cannot close the defect; valid
  original defect evidence keeps the current in-scope failure at `FAIL`.
- The independent `in_scope` and `status` markers must agree. `true/out_of_scope`, `false/open`,
  and `false/resolved` are diagnosed as contradictory and produce `BLOCKED`; coherent proven
  in-scope defects retain `FAIL` precedence, and coherent out-of-scope defects remain visible
  without forcing failure.
- RED: four focused correction methods produced 7 failures across the legitimate waiver, three
  superseded-retest terminals, and three contradictory-scope combinations.
- GREEN: the full focused suite passed 15 tests after the minimum correction.
- Regression proof: after reversing only the production correction, the same four methods
  reproduced all 7 failures; restoring it returned the full focused suite to 15 passing tests.
- Combined probes cover valid and invalid waivers, terminal `FAIL`/`BLOCKED`/`NOT_RUN` retests,
  both directions of scope contradiction, resolved/out-of-scope states, and coherent in-scope
  failure precedence.
- Fresh final verification: all 101 `test_qa_*` tests passed; Python compilation and
  `git diff --check` passed.
- No ledger, review artifact, brief, review package, dependency, external state, publication,
  push, or merge was changed.
