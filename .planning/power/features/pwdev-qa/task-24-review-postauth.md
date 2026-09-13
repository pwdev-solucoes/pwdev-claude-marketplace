# Task 24 — independent post-authorization review

Date: 2026-09-13
Reviewed HEAD: `3d944e3e0ca0a3a11e76c98ffbe4b2aa6ab0e1fe`
Range: `a80b97b..3d944e3`
Scope: CA-003 evidence update, runtime/acceptance documentation and its scenario oracle.
Mode: read-only inspection, existing-artifact validation and in-memory mutation probes.
Only this review document was created; no runtime installation, configuration or source change.

## SPEC

PARTIAL. The documents now record the expected exact versions, separate normative statuses,
one-session discovery/invocation/missing-tool/report results and historical failures. However,
the committed evidence does not let an independent reviewer establish the same-session chain,
and the updated oracle still accepts explicit denials of the required runtime behaviors.
The proposed aggregate PASS is therefore not independently verified by this review.

## QUALITY

Fresh verification using the bundled Python 3.12 interpreter:

- `-m unittest tests.test_qa_scenarios tests.test_readme_marketplace`:
  **11 tests, OK**, 4.472 seconds.
- `-m unittest discover -s tests -p 'test_qa_*.py'`:
  **208 tests, OK**, 16.536 seconds.
- `python3 scripts/validate_readme_plugins.py`: **17 plugins validated**.
- `git diff --check`: OK.

The interpreter was
`/Users/paulosoares/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3`.

The controller supplied three existing output directories. This reviewer independently parsed
their manifests and all PDF pages and inspected HTML content:

| Runtime label | Existing report root | Observed artifact result |
|---|---|---|
| Claude | `/tmp/pwdev-qa-claude-ca003/report/.planning/pwdev-qa/reports/qa-report-demo` | FAIL, 100 criteria, 171 PDF pages, all CA-000..099 and BUG-OPEN-UNMAPPED in HTML/PDF |
| Codex | `/tmp/pwdev-qa-codex-ca003-2/report/.planning/pwdev-qa/reports/qa-report-demo` | FAIL, 100 criteria, 171 PDF pages, all CA-000..099 and BUG-OPEN-UNMAPPED in HTML/PDF |
| Hermes | `/tmp/pwdev-qa-hermes-ca003/report/.planning/pwdev-qa/reports/qa-report-demo` | FAIL, 100 criteria, 171 PDF pages, all CA-000..099 and BUG-OPEN-UNMAPPED in HTML/PDF |

All three public manifests have SHA-256
`bc02eb690bb82a07d1d94757c5f355b6f5503bc3281511ef336208605270aa98`.
This is consistent with a deterministic synthetic fixture; it neither proves nor disproves
which runtime generated a package. Report artifacts establish report content, not the preceding
skill discovery/invocation and missing-tool response in that runtime session.

## FINDINGS

### Major — PA-01: the same-session runtime PASS lacks independently inspectable provenance

Locations: `plugins/pwdev-qa/references/runtime-smoke.md:13-18,23-60` and
`.planning/power/features/pwdev-qa/task-24-report.md:7-10`.

The authoritative sections state that each step happened in one session, but omit full runtime
launch commands, output-directory locators, session/event identifiers, or a linked sanitized
transcript tying skill discovery/invocation, the negative probe and the report inspection
together. The task report says full commands are available in the runtime ledger, yet the new
sections provide only executable names for fixture generation and narrative summaries for
skill loading. The reviewer can verify the three packages supplied separately by the controller,
but those packages carry the same synthetic target and do not identify a runtime/session.

The controller additionally supplied Codex session `01a09a10-e8d1-7db1-a198-af1047566cd4`
and Hermes session `20260913_062445_3bd029`; neither is recorded in the changed evidence files.
The Codex app could not retrieve the supplied task ID, and no matching transcripts were located
in the usual Codex/Hermes session directories. Claude used `--no-session-persistence`; the
controller confirmed that stdout was not archived separately. This is an evidence gap, not
an allegation that the runs failed or were fabricated.

Record the actual commands and durable, sanitized observation evidence per authoritative
session, including the installed plugin/source identity, negative result and report paths/digests.
Link those records from the runtime ledger. Existing controller tool-output evidence may be
retained if available; do not invent a transcript or infer session history from the PDF. If a
step cannot be substantiated, preserve it as unverified until an authorized recorded run supplies
the missing evidence. Avoid promoting aggregate acceptance solely from a narrative PASS.

### Major — PA-02: the oracle accepts explicit non-execution as VERIFIED

Location: `tests/test_qa_scenarios.py:333-373`.

The new assertion checks PASS prefixes in summary cells and required substrings in runtime
sections, without checking the assertions those substrings participate in. Fresh in-memory
mutations independently changed the authoritative statements as follows; every mutation was
accepted by `assert_runtime_contract`:

- Claude: `The authoritative one-session smoke never invoked pwdev-qa:qa-tooling; there was
  no real skill invocation`.
- Codex: `The skill never classified the tool missing, never preserved NOT_RUN/BLOCKED,
  never provided a safe alternative`.
- Hermes: report pages `were not inspected` and criteria/defect `were never confirmed`.

Each mutated section keeps the required vocabulary but explicitly removes the affirmative
evidence for a required smoke step. Deleting each entire runtime section is correctly rejected,
so the oracle protects inventory but not these contradictory acceptance claims. This is the
same class of weakness the task's earlier correction intended to eliminate.

Bind per-runtime results to explicit structured observations and linked evidence, then validate
the required steps and aggregate consistently. Add these negative behavioral mutations while
preserving legitimate historical failure disclosures; do not reject the whole document merely
because a historical section contains a negative sentence.

### Confirmed without findings

- The three exact version strings are internally consistent between task report, runtime table
  and tests. Status values in the acceptance mapping remain PASS/FAIL/BLOCKED; runtime values
  use VERIFIED separately.
- Preliminary Claude OAuth, Codex discovery and Hermes doctor-only attempts remain explicitly
  non-authoritative historical diagnostics. The earlier npx cache incident is still disclosed.
- The report fixture's FAIL is correctly independent of export completion and does not imply
  that the runtime-smoke scenario itself failed.
- No change to exporter behavior or dependency installation is part of this documentation diff.

## REVIEW

**CHANGES_REQUESTED** for PA-01 and PA-02. The deterministic suite is green and the existing
report packages are valid, but these facts do not establish the missing session-level evidence
or make the documentation oracle reject contradictory verification claims.

## ACCEPTANCE

**BLOCKED for independent CA-003 acceptance.** Actual runtime failure was not demonstrated;
the missing provenance and weak verification oracle prevent this review from endorsing the
documented aggregate PASS. Preserve valid artifact observations and historical diagnostics
while resolving these two findings. No rerun, installation or configuration change was
performed or authorized by this review.
