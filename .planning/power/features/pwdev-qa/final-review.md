# PWDEV QA — definitive targeted re-check

Date: 2026-09-13
Reviewed HEAD: e048b29aa0ccab4dfebbc02d7f8b020914bf5c6e
Previous review HEAD: b58456945ed730971faa6cf98dde20feb5f3c2a0
Original whole-branch review HEAD: f5188df00eaed33a294d72b77ae120e9cfe96d57

Scope: remaining FR-03 Major, reviewed against the preceding final-review.md, updated
final-fix-report.md and review-b584569..e048b29.diff. Code remained read-only; only this
review was updated. No runtime, dependency, personal configuration, HEAD or source changes.

## SPEC

PASS for the reviewed implementation. FR-03's criterion-level behavior now agrees with the
approved acceptance semantics. The prior FR-01, FR-02 and FR-04 corrections remain addressed
and unchanged by this patch. Runtime CA-003 remains an independent acceptance blocker.

## QUALITY

Fresh verification:

- Bundled Python 3.12:
  `-m unittest discover -s tests -p 'test_qa_*.py'`:
  **208 tests, OK**, 14.253 seconds.
- Default Python 3.9:
  `python3 -m unittest tests.test_qa_verdict tests.test_qa_contract tests.test_qa_evidence`:
  **42 tests, OK**, 3.430 seconds.
- `git diff --check`: OK.
- Five fresh real-export probes with matching UTF-8 acceptance contracts, safely reviewed
  synthetic evidence, the real ReportLab renderer, and inspection of the public manifest:
  every expected result and count matched.

The bundled executable was
/Users/paulosoares/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3.
No stored evidence command was executed. All probe files were temporary synthetic fixtures.

| Real-export probe | Export | Criterion result | Global verdict | Relevant count |
|---|---|---|---|---|
| Required PASS case with empty expected | complete | BLOCKED | BLOCKED | pass=0, blocked=1 |
| Required PASS case with whitespace observed | complete | BLOCKED | BLOCKED | pass=0, blocked=1 |
| Verified required FAIL with blank criterion assessment | complete | FAIL | FAIL | fail=1, blocked=0 |
| Legitimate NOT_RUN with empty expected/observed | complete | NOT_RUN | BLOCKED | not_run=1 |
| One PASS criterion plus justified NOT_APPLICABLE with empty observations | complete | PASS, NOT_APPLICABLE | PASS | pass=1, not_applicable=1 |

## FINDINGS

### ADDRESSED — FR-03: missing-observation and failure precedence in the acceptance matrix

`plugins/pwdev-qa/scripts/qa_verdict.py:251-254,343-361` now shares one substantive-observation
predicate across case and criterion assessment handling. Incomplete executed required cases
block the associated criterion before the PASS branch. Verified required-case failure is
evaluated before absent assessment and remains FAIL. Stored historical case values are not
rewritten, and global precedence remains consistent.

The real-export probes above reproduce both formerly incorrect combinations and confirm the
correct criterion results and counters. NOT_RUN and valid NOT_APPLICABLE keep their legitimate
empty-observation behavior. `tests/test_qa_verdict.py:190-229` now asserts criterion results
and relevant counts as well as the global verdict. No blocking regression was found in this
targeted correction.

### Prior Major findings — all ADDRESSED

- **FR-01:** contract is read with bounded no-follow traversal and verified for digest and
  declared ID/text pairs before consolidation. The preceding independent re-review verified
  absent/changed contracts, correct-digest unpaired criteria, parent symlinks and oversize.
- **FR-02:** the shared public model is scanned using the bounded credential policy before
  JSON/HTML/PDF publication. The preceding real probe verified neutral refusal, zero public
  artifacts and unchanged private input; those regressions remain green.
- **FR-04:** runtime requirements contain only ReportLab; PDF extraction dependencies remain
  development-only. The Python 3.9 compatible group and dependency-contract test remain green.

## DEFERRED

Two non-blocking Minors remain:

1. **Exact-pair fixture: STILL OPEN.**
   `tests/test_qa_report_cli.py:155-178` rewrites the unpaired contract without recomputing
   the manifest digest, so the fixture blocks at hash mismatch. The preceding in-memory
   mutation making the pair checker always return True survived this test. Recompute the
   digest for that fixture and assert the pair-specific diagnostic. The production pair
   checker passed the stronger independent correct-digest probe; this is a test gap.
2. **Flaky quarantine example: STILL OPEN.**
   `plugins/pwdev-qa/skills/qa-specialist-automation/SKILL.md:74` still lacks explicit
   rationale and bounded expiry in the example. Normative procedure lines 39-41 and failure
   mode lines 88-89 already require them; its outcome remains BLOCKED.

**Long-text final fragment: EFFECTIVELY COVERED**, not an open Minor.
`tests/test_qa_reports_e2e.py:82-94,123-144` checks exact cardinality, full 2,000-character
HTML content, and all partial final sentinels through both PDF extractors. The fresh full QA
suite includes this integrated coverage.

## RUNTIME_ACCEPTANCE

**BLOCKED — CA-003, 0/3 VERIFIED.**
The documented Claude authentication, Codex discovery/invocation and Hermes session-local
skill-loading limitations in `plugins/pwdev-qa/references/runtime-smoke.md:12-18` remain
unchanged. Code review and deterministic tests do not substitute for the approved real
discovery/invocation/report smoke. This re-check performed no new runtime smoke, installation
or configuration changes and does not declare the complete v1 accepted.

## REVIEW

**APPROVED** for code quality and the reviewed implementation, with the two recorded
non-blocking Minors. No unresolved Major remains from FR-01 through FR-04.
Overall runtime acceptance remains independently BLOCKED; this verdict neither grants
release approval nor authorizes merge, publication or runtime configuration changes.
