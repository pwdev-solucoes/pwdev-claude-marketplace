# Runtime smoke evidence

Observed on 2026-09-13 under explicit user authorization. Each report used a new
isolated temporary directory. Claude Code loaded the repository-local plugin, Codex used its installed plugin, and
Hermes used the explicitly authorized local installation pinned to commit `a80b97b`. A runtime is
VERIFIED only after successful `qa-tooling discovery`, real invocation producing the
`missing-tool response`, and `fixture report` generation/inspection in that same runtime session.

## Result summary

| runtime | exact version | status | discovery | invocation/missing-tool | fixture report | limitations |
|---|---|---|---|---|---|---|
| Claude Code | `2.1.269 (Claude Code)` | VERIFIED | PASS — loaded `pwdev-qa:qa-tooling` in the authorized session | PASS — negative probe produced missing/NOT_RUN/BLOCKED | PASS — export complete/FAIL; HTML and 171-page PDF inspected | no limitation in the authoritative run; preliminary authentication failure retained below |
| Codex | `codex-cli 0.153.4` | VERIFIED | PASS — installed plugin exposed `pwdev-qa:qa-tooling` | PASS — negative probe produced missing/NOT_RUN/BLOCKED | PASS — export complete/FAIL; HTML and 171-page PDF inspected | no limitation in the authoritative run; preliminary ephemeral discovery failure retained below |
| Hermes Agent | `Hermes Agent v0.21.1 (2026.9.7) · upstream 564aef29` | VERIFIED | PASS — commit `a80b97b` installed/enabled and skill preloaded | PASS — negative probe produced missing/NOT_RUN/BLOCKED | PASS — export complete/FAIL; manifest, HTML and 171-page PDF inspected | authorized local install used flattened layout; preliminary doctor-only result retained below |

Aggregate status: PASS — 3 of 3 runtimes VERIFIED. Each row is backed by one session that completed
all three steps; preliminary partial attempts below are non-authoritative diagnostics.

## Claude Code

- Version command/probe: `claude --version` → `2.1.269 (Claude Code)`.

### Structured observations

| step | affirmative observation | command/result | source locator |
|---|---|---|---|
| discovery | OBSERVED — session `b522acbc-c139-4dec-af75-abb245a7f905` invoked `pwdev-qa:qa-tooling` from the repository-local plugin. | Skill load completed and the session applied the returned tooling contract. | restricted transcript lines `16-21` |
| missing-tool | OBSERVED — the invoked skill classified the probe as `missing`, preserved execution as `NOT_RUN` and outcome as `BLOCKED`, and returned a safe alternative. | `command -v pwdev-qa-missing-tool` → empty output, exit `1`; no install ran. | restricted transcript lines `27` and `63-64` |
| fixture-report | OBSERVED — the session inspected `manifest.json`, `report.html` and `report.pdf`, then confirmed `CA-000..CA-099` and `BUG-OPEN-UNMAPPED`. | bundled Python 3.12 `qa_demo.py --output-dir /tmp/pwdev-qa-evidence-claude/report` → exit `0`, `export_status=complete`, `verdict=FAIL`; PDF 171 pages. | restricted transcript lines `52`, `55-56` and `63-64` |

Provenance: session `b522acbc-c139-4dec-af75-abb245a7f905`; restricted local source
`/tmp/pwdev-qa-evidence-claude/transcript.jsonl`, SHA-256
`172ea6119c70e633967e26d4194a19f82c75827b302c051d31e1bb93bf88f2a5`, `153890 bytes`,
scan `known_credential_pattern=true`. The raw transcript is not publishable and was not versioned;
the table above is the sanitized, consultable record. Artifact root:
`/tmp/pwdev-qa-evidence-claude/report/.planning/pwdev-qa/reports/qa-report-demo`.
Artifact SHA-256/size: `manifest.json` `bc02eb690bb82a07d1d94757c5f355b6f5503bc3281511ef336208605270aa98`
(`321416 bytes`); `report.html` `0005e8da8befe1e2115697067fdcc21b685ebec40eae899b3e631d050eac4f02`
(`348246 bytes`); `report.pdf` `7f5b9d18bcb26070dbd3a841da5f5d7a460a0523527d0fa9f27fcbf55666fbfb`
(`328935 bytes`).

- The authoritative one-session smoke loaded `pwdev-qa:qa-tooling`; this was real skill invocation,
  not manifest-only discovery.
- Invocation/missing-tool result/evidence: `command -v pwdev-qa-missing-tool` returned exit `1`.
  The loaded skill classified the tool `missing`, kept execution `NOT_RUN`, returned outcome
  `BLOCKED`, supplied a safe alternative, and did not install or fabricate execution.
- Fixture report command/evidence: repository-local `qa_demo.py` ran in that same session and
  returned exit `0`, `export_status=complete`, and `verdict=FAIL`.
- Report inspection/evidence: `report.html` was inspected; `report.pdf` parsed as 171 pages; the
  complete range `CA-000..CA-099` and `BUG-OPEN-UNMAPPED` were confirmed. Status: VERIFIED.

## Codex

- Version command/probe: `codex --version` → `codex-cli 0.153.4`.

### Structured observations

| step | affirmative observation | command/result | source locator |
|---|---|---|---|
| discovery | OBSERVED — thread `01a09a22-f2ce-7a70-84ae-97f2b14b126e` invoked `pwdev-qa:qa-tooling` through installed-plugin discovery. | Installed source `/Users/paulosoares/.codex/plugins/cache/pwdev-flow/pwdev-qa/0.1.0` exposed the skill and tooling reference. | restricted transcript lines `35` and `62-66` |
| missing-tool | OBSERVED — the invoked skill classified the probe as `missing`, preserved execution as `NOT_RUN` and outcome as `BLOCKED`, and returned a safe alternative. | `command -v pwdev-qa-missing-tool` → empty output, exit `1`; no install ran. | restricted transcript lines `67-69` and `101` |
| fixture-report | OBSERVED — the session inspected `manifest.json`, `report.html` and `report.pdf`, then confirmed `CA-000..CA-099` and `BUG-OPEN-UNMAPPED`. | bundled Python 3.12 `qa_demo.py --output-dir /tmp/pwdev-qa-evidence-codex/report` → exit `0`, `export_status=complete`, `verdict=FAIL`; PDF 171 pages. | restricted transcript lines `95-101` |

Provenance: thread `01a09a22-f2ce-7a70-84ae-97f2b14b126e`; restricted local source
`/tmp/pwdev-qa-evidence-codex/transcript.jsonl`, SHA-256
`eed80c343749042ac6591dd1231069e594a42e17a70fe8fb3f9fc6d0b8ef2624`, `80963 bytes`, scan
`known_credential_pattern=true`. The raw transcript is not publishable and was not versioned; the
table above is the sanitized, consultable record. Artifact root:
`/tmp/pwdev-qa-evidence-codex/report/.planning/pwdev-qa/reports/qa-report-demo`.
Artifact SHA-256/size: `manifest.json` `bc02eb690bb82a07d1d94757c5f355b6f5503bc3281511ef336208605270aa98`
(`321416 bytes`); `report.html` `0005e8da8befe1e2115697067fdcc21b685ebec40eae899b3e631d050eac4f02`
(`348246 bytes`); `report.pdf` `28edb6ffb046e2db788bc0889ad8c30fc6e7a0cef382eae8901a2e456024d2b5`
(`328935 bytes`).

- The authoritative one-session smoke completed installed plugin discovery by invoking
  `pwdev-qa:qa-tooling`; reading a skill file was not substituted for discovery.
- Invocation/missing-tool result/evidence: `command -v pwdev-qa-missing-tool` returned exit `1`.
  The skill classified the tool `missing`, preserved `NOT_RUN`/`BLOCKED`, provided a safe
  alternative, and performed no installation or fictitious execution.
- Fixture report command/evidence: repository-local `qa_demo.py` ran in the same session and
  returned exit `0`, `export_status=complete`, and `verdict=FAIL`.
- Report inspection/evidence: `manifest.json` and `report.html` were inspected, `report.pdf` parsed as 171 pages,
  and `CA-000..CA-099` plus `BUG-OPEN-UNMAPPED` were confirmed. Status: VERIFIED.

## Hermes Agent

- Version command/probe: `hermes --version` →
  `Hermes Agent v0.21.1 (2026.9.7) · upstream 564aef29`.

### Structured observations

| step | affirmative observation | command/result | source locator |
|---|---|---|---|
| discovery | OBSERVED — preloaded session `20260913_064516_ed1c02` invoked `pwdev-qa:qa-tooling` from the enabled flattened plugin at commit `a80b97b`. | Authorized local install and doctor succeeded before the single-query session accepted the bound skill contract. | restricted transcript lines `75` and structured conclusion lines `490-556` |
| missing-tool | OBSERVED — the invoked skill classified the probe as `missing`, preserved execution as `NOT_RUN` and outcome as `BLOCKED`, and returned a safe alternative. | `command -v pwdev-qa-missing-tool` → empty output, `REAL_EXIT=1`; no install ran. | restricted transcript lines `114-139` and `499-510` |
| fixture-report | OBSERVED — the session inspected `manifest.json`, `report.html` and `report.pdf`, then confirmed `CA-000..CA-099` and `BUG-OPEN-UNMAPPED`. | bundled Python 3.12 `qa_demo.py --output-dir /tmp/pwdev-qa-evidence-hermes-2/report` → `QA_DEMO_EXIT=0`, `export_status=complete`, `verdict=FAIL`; PDF 171 pages. | restricted transcript lines `153`, `177`, `364` and `512-556` |

Provenance: session `20260913_064516_ed1c02`; restricted local source
`/tmp/pwdev-qa-evidence-hermes-2/transcript.log`, SHA-256
`836e6b0d3c563ec047c78cfd6c68203e48833ee410cf34a500898b89c1ac3d38`, `92903 bytes`, scan
`known_credential_pattern=false`. The raw transcript remains temporary and was not versioned; the
table above is the sanitized, consultable record. Artifact root:
`/tmp/pwdev-qa-evidence-hermes-2/report/.planning/pwdev-qa/reports/qa-report-demo`.
Artifact SHA-256/size: `manifest.json` `bc02eb690bb82a07d1d94757c5f355b6f5503bc3281511ef336208605270aa98`
(`321416 bytes`); `report.html` `0005e8da8befe1e2115697067fdcc21b685ebec40eae899b3e631d050eac4f02`
(`348246 bytes`); `report.pdf` `e95e48bc2f1195d5e0449db228a25219f1f2330dbe0dddfb1b50b66a487b09fe`
(`328935 bytes`).

- Under explicit authorization, exact commit `a80b97b` was locally installed and enabled in the
  flattened layout; plugin doctor passed before the session.
- The authoritative one-session smoke preloaded `pwdev-qa:qa-tooling`, proving skill discovery and
  invocation beyond the successful doctor result.
- Invocation/missing-tool result/evidence: `command -v pwdev-qa-missing-tool` returned exit `1`.
  The preloaded skill classified it `missing`, recorded `NOT_RUN`/`BLOCKED`, returned an alternative,
  and did not install or fabricate a tool execution.
- Fixture report command/evidence: repository-local `qa_demo.py` ran in the same session and
  returned exit `0`, `export_status=complete`, and `verdict=FAIL`.
- Report inspection/evidence: `manifest.json`, `report.html`, and the 171 pages of `report.pdf`
  were inspected; `CA-000..CA-099` and `BUG-OPEN-UNMAPPED` were confirmed. Status: VERIFIED.

## Historical preliminary diagnostics

These failed or partial attempts are retained for traceability and are non-authoritative after the
successful one-session smokes above:

- Claude Code initially discovered the session-only plugin but stopped with `OAuth session expired`
  before invoking a skill or producing a report.
- Codex initially ran ephemerally without installed-plugin discovery. It correctly refused to count
  reading `SKILL.md` as invocation; its standalone successful report did not verify that runtime.
- Hermes initially passed doctor only. Registration without a preloaded/invoked skill and report did
  not satisfy verification.

## playwright-cli probes

The official/local contract requires both paths to be distinguished; `npx` presence alone is not
Playwright evidence.

| command/probe | observed result | evidence and limitations |
|---|---|---|
| `playwright-cli --version` | `0.1.14` | installed global CLI is available |
| `npx --no-install playwright --version` | `Version 1.61.1` | positive local package probe in this checkout; `--no-install` prevented fallback download |
| `npx playwright cli --help` | successful `playwright-cli` help | documented local `npx playwright cli` entry was resolved only after the positive no-install probe |
| `playwright-cli -s=qa-f05-24-report open http://127.0.0.1:18765/report.html` followed by `snapshot`, `screenshot --filename=/tmp/pwdev-qa-f05-24-report.png`, and `close` | successful task-owned session | localhost served the generated static report because the CLI blocks `file:` URLs; screenshot was visually reviewed and not attached as fixture evidence |

An exploratory probe from `/tmp` invoked `npx playwright cli --version` before a local-package
preflight and emitted `The following package was not found and will be installed: playwright@1.63.0`.
That probe is non-compliant with the no-install contract, is excluded from availability evidence,
and may have populated the npm cache. No deletion or further modification of that personal cache
was attempted. The authoritative results are the later checkout-local no-install probe and entry
help above.
