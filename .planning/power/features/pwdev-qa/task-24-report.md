# Task 24 — implementation report

## Status

DONE_WITH_CONCERNS

The documentary integration, scenario oracle, real fixture export and executable probes are
complete. CA-003 remains BLOCKED because none of the three runtimes completed successful
discovery plus invocation plus report generation in one real runtime session. No partial result is
reported as runtime verification.

## Scope delivered

- Added `pwdev-qa` to the existing goal grouping and catalog layout in both root READMEs.
- Added complete acceptance evaluation for all 10 workflows and 17 specialists, the required
  `qa-tooling` unavailable-tool response, and a real HTML/PDF fixture validation.
- Added reproducible runtime smoke evidence with exact versions, help/probes, results, evidence and
  limitations for Claude Code, Codex and Hermes Agent.
- Tested both documented Playwright resolutions and exercised the generated HTML with a task-owned
  global `playwright-cli` session.
- Preserved the detailed installation and inventory guidance in the plugin READMEs; no personal
  runtime configuration or repository plugin implementation was changed.

## TDD evidence

- RED: `python3 -m unittest tests.test_qa_scenarios tests.test_readme_marketplace && python3
  scripts/validate_readme_plugins.py` failed for the missing root README entries and missing
  `acceptance-scenarios.md`/`runtime-smoke.md`. After making missing files assertion failures rather
  than fixture errors, 8 tests ran with 7 expected behavioral failures and 1 PDF-environment skip;
  the validator separately reported both root READMEs missing `pwdev-qa`.
- GREEN (required default Python command): 8 tests passed with the 1 declared PDF-environment skip;
  the validator reported `validated 17 plugins in both READMEs`.
- GREEN (declared Python 3.12 PDF environment): the same 8 tests all passed. The fixture created a
  new report, parsed HTML and the 171-page PDF with pypdf and pdfplumber, compared IDs/status/defect
  content, and confirmed rejected attachments were absent.

## Runtime results

| runtime | exact version | result | decisive evidence |
|---|---|---|---|
| Claude Code | `2.1.269 (Claude Code)` | UNVERIFIED | session-only plugin details found `qa-tooling`; the model invocation stopped with expired OAuth before missing-tool handling/report |
| Codex | `codex-cli 0.153.4` | UNVERIFIED | ephemeral session did not expose `qa-tooling`; negative probe and fixture report ran, with `export_status=complete` and `verdict=FAIL` |
| Hermes Agent | `Hermes Agent v0.21.1 (2026.9.7) · upstream 564aef29` | UNVERIFIED | doctor passed discovery/manifest/import/registration; no safe documented session-local invocation route satisfied the `.env` and no-config constraints |

Full commands, output summaries and limitations are in
`plugins/pwdev-qa/references/runtime-smoke.md`.

## Verification evidence

- All QA tests: Python 3.12 `unittest discover -s tests -p 'test_qa_*.py' -v` — 198 tests ran,
  all passed in 14.345s.
- Focused/root validator: `tests.test_qa_scenarios`, `tests.test_readme_marketplace` and
  `scripts/validate_readme_plugins.py` — all applicable tests passed; 17 plugins validated in both
  READMEs.
- Legacy root README suite: 5 checks passed and 4 failed. These are the four pre-existing
  `test_marketplace_readmes` failures recorded in the baseline: it requires the superseded
  per-plugin sections/install commands/inventory format for every plugin. The current catalog
  validator and task-specific bilingual catalog tests pass; this task did not rewrite the approved
  root layout to satisfy the stale format.
- Claude and Codex manifests plus both marketplace JSON files passed `python3 -m json.tool`.
- `git diff --check` passed.

## Acceptance review

- CA-001: PASS — all 10 workflow contracts and wrappers are covered.
- CA-002: PASS — all 17 specialties have positive and failure/limitation evaluations.
- CA-003: BLOCKED — 0/3 runtimes completed the strict real smoke.
- CA-004: PASS — the unavailable-tool scenario preserves exit 1, `NOT_RUN`/`BLOCKED`, an
  alternative and no automatic installation/fabricated execution.
- CA-018: PASS — English and Portuguese root/plugin documentation is integrated.
- CA-022: PASS — the recommendation carries tool, purpose, availability, evidence,
  prerequisites, alternative and reason.
- CA-023: PASS_WITH_LIMITATION — global and checkout-local Playwright paths and isolated session
  behavior were exercised; runtime skill invocation remains blocked as described above.

## Limitations and incident disclosure

- Claude authentication was expired; refreshing credentials is outside this task.
- Codex's installed help exposes marketplace installation but not a session-only local plugin flag;
  changing plugin configuration to force discovery was intentionally refused.
- Hermes's safe mode disables plugins, while its documented ignore-user-config mode may still load
  `.env`; installation/trust/config changes and existing `.env` reads were intentionally refused.
- The first exploratory local-entry probe was mistakenly run from `/tmp` as
  `npx playwright cli --version`; npx warned that it would install Playwright 1.63.0 and may have
  populated the npm cache. This probe is excluded from evidence. It was not repeated or silently
  cleaned up. The compliant checkout-local sequence subsequently used
  `npx --no-install playwright --version` (1.61.1) before `npx playwright cli --help`.
- A `file:` URL was refused by playwright-cli. The report was instead served on loopback, opened,
  snapshotted and screenshotted in the task-owned session, then that session was closed. Generated
  repository-local Playwright artifacts and Python cache were moved to Trash after inspection.
