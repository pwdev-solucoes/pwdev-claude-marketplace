# Task 24 — implementation report

## Status

DONE

The documentary integration, scenario oracle, real fixture export and executable probes are
complete. Under explicit authorization, Claude Code, Codex and Hermes each completed discovery,
invocation/missing-tool handling and report generation/inspection in one session. CA-003 is PASS
with 3 of 3 runtimes VERIFIED; preliminary partial attempts remain historical diagnostics only.

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
| Claude Code | `2.1.270 (Claude Code)` | VERIFIED | session `b522acbc-c139-4dec-af75-abb245a7f905` invoked `pwdev-qa:qa-tooling`, preserved the negative probe as missing/NOT_RUN/BLOCKED, exported complete/FAIL, inspected HTML and parsed 171 PDF pages with CA-000..099 and the defect |
| Codex | `codex-cli 0.153.4` | VERIFIED | thread `01a09a22-f2ce-7a70-84ae-97f2b14b126e` used installed-plugin discovery to invoke `pwdev-qa:qa-tooling`; bundled Python 3.11.16 completed the same negative probe and complete/FAIL 171-page fixture validation |
| Hermes Agent | `Hermes Agent v0.21.1 (2026.9.7) · upstream 564aef29` | VERIFIED | session `20260913_064516_ed1c02` preloaded the skill from authorized commit `a80b97b`, then completed the probe and fixture inspection after doctor passed |

Structured affirmative observations, exact commands, session/transcript locators and hashes,
artifact paths/digests, output summaries and limitations are in
`plugins/pwdev-qa/references/runtime-smoke.md`.

## Verification evidence

- All QA tests: Python 3.12 `unittest discover -s tests -p 'test_qa_*.py' -q` — 209 tests ran,
  all passed in 14.654s.
- Focused/root validator: `tests.test_qa_scenarios`, `tests.test_readme_marketplace` and
  `scripts/validate_readme_plugins.py` — 12 tests passed in 4.041s; 17 plugins validated in both
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
- CA-003: PASS — 3/3 runtimes completed the strict real smoke in one session each.
- CA-004: PASS — the unavailable-tool scenario preserves exit 1, `NOT_RUN`/`BLOCKED`, an
  alternative and no automatic installation/fabricated execution.
- CA-018: PASS — English and Portuguese root/plugin documentation is integrated.
- CA-022: PASS — the recommendation carries tool, purpose, availability, evidence,
  prerequisites, alternative and reason.
- CA-023: PASS — global and checkout-local Playwright paths and isolated session behavior were
  exercised. Limitation: an initial non-authoritative `npx` probe could have populated the npm
  cache, and the CLI required loopback serving because it refused the report's `file:` URL.

## Limitations and incident disclosure

- A preliminary Claude attempt stopped on expired OAuth; the later authorized complete session is
  authoritative and the failed attempt remains diagnostic history.
- A preliminary ephemeral Codex attempt lacked plugin discovery; installed-plugin discovery and the
  later complete one-session smoke supersede it for verification.
- A preliminary Hermes attempt proved doctor/registration only; the authorized install of exact
  commit `a80b97b` and complete preloaded-skill session are authoritative.
- The authoritative raw transcripts remain restricted temporary local sources and were not
  versioned. The plugin scanner reported `known_credential_pattern=true` for Claude and Codex, so
  those two logs are not publishable; Hermes reported `false`. The runtime ledger contains only the
  sanitized IDs, commands/results, line locators, paths, hashes and sizes needed for review.
- The first exploratory local-entry probe was mistakenly run from `/tmp` as
  `npx playwright cli --version`; npx warned that it would install Playwright 1.63.0 and may have
  populated the npm cache. This probe is excluded from evidence. It was not repeated or silently
  cleaned up. The compliant checkout-local sequence subsequently used
  `npx --no-install playwright --version` (1.61.1) before `npx playwright cli --help`.
- A `file:` URL was refused by playwright-cli. The report was instead served on loopback, opened,
  snapshotted and screenshotted in the task-owned session, then that session was closed. Generated
  repository-local Playwright artifacts and Python cache were moved to Trash after inspection.

## Fix round 1

### Root cause

The first scenario oracle searched for names and evidence vocabulary across the whole Markdown
document. It did not bind a runtime status to that runtime's three smoke steps and detailed
section, nor bind a workflow/specialist result to semantic fields in that item's table row.
Consequently, unrelated occurrences satisfied the assertions after evidence was removed or a row
was reduced to labels. The acceptance table also combined a normative result with limitation prose,
creating values outside the approved enum.

### RED and mutation reproduction

- Before correction, in-memory mutations promoting only Codex to `VERIFIED`, removing the complete
  Claude detail section, and replacing either the `qa-init` or `qa-specialist-security` semantic
  row with placeholders were all accepted by the old predicates.
- New structural tests were written first. The focused Python 3.12 run executed 10 tests and failed
  3 times because the old runtime, scenario and acceptance table schemas lacked the required
  per-identity fields. The existing report fixture continued to pass.
- The new mutation tests explicitly require rejection of the false Codex promotion, missing Claude
  detail, destroyed `qa-init` row and destroyed security row. The pre-fix documents were also
  replayed from Git in memory and rejected by the new parser.

### Correction

- Runtime rows now contain exact version, status, discovery evidence, invocation/missing-tool
  evidence, fixture-report evidence and limitations for each unique runtime. Detailed sections are
  mandatory per runtime, and the aggregate remains `BLOCKED — 0 of 3 runtimes VERIFIED`.
- Workflow and specialist tables now have exactly one row per expected item and explicit
  preconditions, actions, oracle, safety/limitation, executable evidence paths and normative result.
  Tests reject duplicates, extras, missing rows, placeholders, weak fields and nonexistent evidence
  paths; `qa-init` and security carry additional behavior-specific assertions.
- Acceptance results are now parsed separately from limitations. CA-023 is `PASS` with its
  limitation in a distinct field; CA-003 remains `BLOCKED` with `0 of 3` in its limitation field.
  No composite result value remains.

### GREEN evidence

- Focused Python 3.12 suite plus README test: 11 tests ran, all passed in 3.697s; the validator
  reported 17 plugins in both READMEs.
- Complete Python 3.12 `test_qa_*` suite: 201 tests ran, all passed in 14.597s.
- The focused mutation tests pass only by observing rejection of all four adversarial variants.
- JSON validation and final diff checks remained green; the known four legacy root README baseline
  failures are unchanged and outside this correction.

## Fix round 2

### Root cause

The round-one ledger correctly prevented unsupported promotion, but it represented an earlier
evidence state. Explicit authorization subsequently produced complete, same-session discovery,
invocation/missing-tool handling and report inspection on all three runtimes. The defect was stale
acceptance evidence and an oracle that still expected the obsolete `BLOCKED — 0 of 3` aggregate,
not a plugin behavior regression.

### RED

- The expectations were changed first to require `CA-003` as `PASS`, all three runtime rows as
  `VERIFIED`, `PASS` evidence for every three-step smoke, and the exact aggregate `PASS — 3 of 3
  runtimes VERIFIED`.
- Against the stale ledger, the focused `tests.test_qa_scenarios` run executed 10 tests and failed
  twice as intended: CA-003 was still `BLOCKED`, and the first runtime row was still `UNVERIFIED`.

### Correction

- Recorded the authorized 2026-09-13 Claude Code 2.1.269, Codex 0.153.4 and Hermes Agent 0.21.1
  results with exact discovery, negative-probe, fixture-export and report-inspection evidence.
- Preserved failed preliminary Claude, Codex and Hermes attempts as explicitly non-authoritative
  diagnostics, together with the historical npx cache incident.
- Kept result values within `PASS`/`FAIL`/`BLOCKED`; CA-023 remains `PASS` and carries its caveats
  only in limitation prose.

### GREEN

- Focused scenario/README suite: 11 tests passed in 4.031s; the catalog validator validated 17
  plugins in both root READMEs.
- Complete `test_qa_*` suite: 208 tests passed in 14.979s.
- Runtime-promotion and semantic-destruction mutation tests remain green by rejecting their
  adversarial variants.

## Post-authorization review correction (PA-01/PA-02)

### Root cause

The runtime ledger used narrative summaries without durable session/transcript/artifact locators,
and its oracle checked vocabulary rather than the affirmative relationship between each runtime
and the three required smoke steps. Explicit denials could therefore retain all required tokens
and still satisfy the contract.

### RED

- A regression test introduced the three review mutations verbatim. Before the fix, its Claude,
  Codex and Hermes subcases all failed because `assert_runtime_contract` raised no assertion for
  the contradictory denial.
- Replaying the prior committed ledger against the strengthened contract is rejected for its
  missing structured observations, confirming the regression test does not merely fit the new
  prose.

### Correction

- Each authoritative runtime now has exactly three structured observations: discovery/invocation,
  missing-tool classification, and fixture report inspection. Every row states an affirmative
  observation, exact command/result, and transcript line locator.
- Each section binds the observation rows to the authoritative session/thread ID, temporary
  transcript path/hash/size and artifact root/hash/size. Raw logs are not versioned; scanner status
  and the Claude/Codex publication block are explicit.
- The oracle validates affirmative semantics per runtime and rejects the three targeted denials
  only inside authoritative sections, leaving legitimate historical failure diagnostics intact.

### GREEN

- Focused runtime/scenario validation and the complete QA suite passed; final command counts and
  timings are recorded in `Verification evidence` above.
