# PWDEV QA — adversarial Power verification verdict

Date: 2026-09-13T06:05:53Z
Status: REJECTED
Spec: `.planning/power/features/pwdev-qa/spec.md`
Plan: `.planning/power/features/pwdev-qa/plan.md`
Branch range: `fb146297d681a1a6a77d71b5c30772655802590a..e048b29aa0ccab4dfebbc02d7f8b020914bf5c6e`

## Verdict

**REJECTED.** The implementation and deterministic QA suite survived the fresh checks, but the
whole feature did not satisfy every approved truth. CA-003 requires successful real discovery,
skill invocation with the missing-tool response, and fixture-report generation/inspection in each
of Claude Code, Codex and Hermes. Fresh non-mutating probes corroborate the recorded result:
**0/3 runtimes are VERIFIED**. The approved plan states that unavailable runtime access may allow
independent work to finish but prevents closing v1. A blocking acceptance condition cannot be
downgraded to a Power `CAVEATS` verdict.

The consolidated product acceptance result is **BLOCKED**, not FAIL: no current product failure
was proved by the runtime attempts, but mandatory execution evidence is absent. Power's verdict
vocabulary has no `BLOCKED`; under `power-verify`, a mandatory stated truth that did not survive is
`REJECTED`.

## Acceptance

| Criteria | Result | Fresh basis |
|---|---|---|
| CA-001, CA-002 | PASS | Exactly 10 workflow wrappers, 29 skills total, 17 specialist skills, scenario contracts, and the fresh 208-test QA suite. |
| CA-003 | **BLOCKED** | Claude discovery only; Codex has no effective ephemeral local skill discovery; Hermes doctor proves packaging/registration only. None completed discovery + invocation + report in one runtime session. |
| CA-004 through CA-023, except CA-003 | PASS | Fresh QA suite, Python 3.9 critical group, direct synthetic export, catalog validation, source/diff inspection, and the accepted traceability mapping. |

Consolidated acceptance: **BLOCKED solely on CA-003**. Structural/unit checks were not promoted to
runtime acceptance.

## Objective and constraint refutation

- The objective to deliver the complete v1 for all three runtimes was refuted at its mandatory
  runtime-validation boundary: 0/3 complete runtime smokes.
- The code-shape objectives survived: 29 regular skill files, 10 Claude command files, 17
  specialists, no plugin symlinks, no required MCP server, and no hooks or agents in Claude's
  inventory.
- The report objective survived a fresh real export: 100 applicable criteria, 171 PDF pages,
  `export_status=complete`, expected global `FAIL` from the proven open unlinked defect, one copied
  reviewed attachment, and two withheld unsafe/pending attachments.
- The portability constraint did not survive as an accepted runtime claim. Packaging/discovery
  evidence is useful but is not a substitute for real invocation.
- No tracked changes exist under the reference plugins `plugins/pwdev-flow`,
  `plugins/pwdev-devops`, or `plugins/pwdev-power`; the global Power state is also unchanged in the
  branch range.
- No merge commit or committed review package exists in the feature range. `git diff --check`
  passed.
- A process prohibition did not survive cleanly: `task-24-report.md` records an exploratory
  `npx playwright cli --version` run before the required `--no-install` preflight. The command
  allowed an automatic fallback and may have populated the npm cache. The effect is unverified;
  this verification did not inspect or alter personal cache/configuration. This is a historical
  execution nonconformance, not a newly observed source defect.

## Fresh commands and results

### Complete and focused tests

```text
/Users/paulosoares/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3 \
  -m unittest discover -s tests
=> exit 1; Ran 878 tests in 450.035s; FAILED (failures=7)
=> exactly the known baseline signatures:
   2 test_flow_claude_compat README failures for missing `claude -p`
   4 legacy test_marketplace_readmes format/inventory failures
   1 test_pwdev_power missing power-roadmap-status symlink failure
=> no additional failure signature

/Users/paulosoares/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3 \
  -m unittest discover -s tests -p 'test_qa_*.py' -q
=> exit 0; Ran 208 tests in 14.623s; OK

python3 -m unittest tests.test_qa_verdict tests.test_qa_contract tests.test_qa_evidence -q
=> exit 0; Ran 42 tests in 3.531s; OK on Python 3.9.6

python3 -m py_compile plugins/pwdev-qa/scripts/*.py
=> exit 0

python3 -m unittest tests.test_readme_marketplace -q
=> exit 0; Ran 1 test; OK

python3 scripts/validate_readme_plugins.py
=> exit 0; validated 17 plugins in both READMEs
```

The three baseline test files are unchanged in `fb146297..HEAD`. The root README diff is limited
to the two bilingual `pwdev-qa` catalog/grouping additions. Therefore the complete-suite red state
is recorded as baseline debt, not as evidence that the QA feature suite passed globally.

### Inventory, dependency, diff, and prohibition probes

```text
find plugins/pwdev-qa/skills -mindepth 2 -maxdepth 2 -name SKILL.md -type f | wc -l
=> 29

find plugins/pwdev-qa/skills -mindepth 2 -maxdepth 2 -name SKILL.md -type l | wc -l
=> 0

find plugins/pwdev-qa/commands -maxdepth 1 -name '*.md' -type f | wc -l
=> 10

find plugins/pwdev-qa -iname '*mcp*' -print
=> no matches

python3 -m json.tool <each QA runtime manifest and both marketplace JSON files>
=> exit 0 for all four files

bundled Python importlib.metadata versions
=> reportlab 4.4.9; pypdf 6.10.0; pdfplumber 0.11.9

requirements.txt / requirements-dev.txt
=> runtime: reportlab==4.4.9
=> development: pypdf==6.10.0, pdfplumber==0.11.9

git diff --check fb146297..HEAD
=> exit 0

git diff --quiet fb146297..HEAD -- plugins/pwdev-flow plugins/pwdev-devops plugins/pwdev-power
=> exit 0; reference plugins unchanged

git diff --quiet fb146297..HEAD -- .planning/power/state.md
=> exit 0; global state unchanged

git rev-list --merges --count fb146297..HEAD
=> 0

git ls-files '.planning/power/features/pwdev-qa/review-packages/*' | wc -l
=> 0; generated review packages remain uncommitted working material

credential-pattern scan over plugin, feature artifacts and QA tests
=> no matching literal credential/private-key pattern
```

### Real report export probe

A fresh temporary synthetic output root was used; no stored evidence command was executed.

```text
bundled-python plugins/pwdev-qa/scripts/qa_demo.py --output-dir <new temporary path>
=> exit 0
=> run_id=qa-report-demo
=> export_status=complete
=> verdict=FAIL
=> criteria_total=100; criteria_pass=100
=> defects_current_in_scope=1
=> evidence_verified=1; evidence_blocked=2
=> package files: attachments/, manifest.json, report.html, report.pdf
=> pypdf pages: 171
=> credential-log.txt and pending-image.png absent from public manifest and HTML
```

The initial verifier invocation intentionally supplied an already-existing temporary directory and
was rejected with `--output-dir must identify a directory that does not exist`; retrying with a new
child path succeeded. This confirms collision/refusal behavior rather than weakening it.

### Fresh non-mutating runtime probes

```text
claude --version
=> 2.1.269 (Claude Code)

claude --plugin-dir plugins/pwdev-qa plugin details pwdev-qa
=> plugin 0.1.0 discovered; qa-tooling listed; 39 UI components are 29 skills + 10 wrappers;
   0 agents, 0 hooks, 0 MCP servers

codex --version
=> codex-cli 0.153.4

codex exec --help | search local plugin/skill discovery options
=> --add-dir, --ephemeral and --ignore-user-config are present; no session-local plugin/skill
   discovery option is documented

hermes --version
=> Hermes Agent v0.21.1 (2026.9.7), upstream 564aef29

hermes plugins doctor plugins/pwdev-qa --ci
=> runtime discovery, manifest parsing, import and registration passed; 0 tools, 0 hooks
=> packaging evidence only, not qa-tooling invocation evidence

playwright-cli --version
=> 0.1.14

npx --no-install playwright --version
=> Version 1.61.1
```

No authenticated/model invocation was attempted during this verification: doing so would require
using credentials or crossing the explicitly recorded configuration/isolation boundaries. The
fresh probes corroborate, but do not upgrade, the task-24 runtime evidence.

## Findings

1. **BLOCKER — CA-003 remains BLOCKED at 0/3 VERIFIED.** This falsifies completion of the whole
   v1 and requires the Power verdict `REJECTED`.
2. **IMPORTANT — installation prohibition has a disclosed historical nonconformance.** The task-24
   record admits a preflight-free `npx` fallback that may have populated cache. No further personal
   state inspection or mutation is authorized here.
3. **MINOR — exact-pair mutation fixture remains incomplete.** The `unpaired` case in
   `tests/test_qa_report_cli.py` changes the contract without recomputing its declared digest, so it
   reaches hash mismatch before isolating the exact ID/text-pair diagnostic. Production behavior
   survived the stronger prior correct-digest real probe.
4. **MINOR — flaky quarantine example remains incomplete.** The example at
   `qa-specialist-automation/SKILL.md:74` names owner/root-cause investigation but omits explicit
   rationale and bounded expiry, although the normative procedure and failure mode require both.
5. **MINOR — final review is not yet in HEAD.** `final-review.md` exists and records independent
   approval, but was untracked during verification. It must be intentionally included with the
   durable feature artifacts before integration; generated review packages must remain untracked.

## Global state conflict and ledger recommendation

`.planning/power/state.md` currently and legitimately tracks active unrelated work:
`sdd-composy`, status `EXECUTING`. Updating it to record this gate would clobber another feature's
operational truth, so this verification deliberately did not modify it.

Ledger recommendation: after the owner resolves or explicitly hands off the active global state,
append a `pwdev-qa` verification entry that records `Power verdict: REJECTED`, `Acceptance:
BLOCKED`, `CA-003: 0/3 VERIFIED`, this verdict path, the disclosed no-install incident, and the next
valid action: obtain authorized isolated runtime invocation evidence for Claude, Codex and Hermes,
then rerun `power-verify`. Do not overwrite or reinterpret the existing `sdd-composy` entry.

## Next valid action

Do not run `power-finish`, merge, publish, install, or promote runtime support. Resolve CA-003 using
authorized isolated runtime sessions without mutating personal configuration; separately decide how
to acknowledge the historical `npx` process nonconformance. Then repeat full adversarial
verification with fresh evidence.
