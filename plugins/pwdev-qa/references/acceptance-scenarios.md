# PWDEV QA acceptance scenarios

This ledger evaluates the complete v1 inventory against the approved contracts. A structural
scenario is evidence about the checked skill document, not a claim that an unavailable external
tool ran. Runtime discovery and invocation are evaluated separately in
[`runtime-smoke.md`](./runtime-smoke.md).

## SCN-WORKFLOWS — all workflow routes

The positive scenario checks that each installed workflow preserves explicit intent, target,
contract, authorization, results, evidence, limitations and its documented output order. The
failure/limitation scenario checks that missing authority, input, evidence or capability stays
`NOT_RUN`/`BLOCKED` and does not become an invented result. The behavior suites exercise the
actual Markdown contracts and wrappers.

| workflow | positive scenario expected | failure/limitation scenario expected | observed | evidence | result |
|---|---|---|---|---|---|
| `qa-init` | inventories the bounded target and observed capabilities | missing objective/target/capability is explicit | contract and routing assertions pass | `tests/test_qa_workflows.py`, `tests/test_qa_router.py` | PASS |
| `qa-strategy` | creates traceable coverage and consults `qa-tooling` | missing contract/authority remains a limitation | contract and routing assertions pass | `tests/test_qa_workflows.py`, `tests/test_qa_router.py` | PASS |
| `qa-test` | records execution against criteria and evidence | absent authorization/tool never becomes execution | contract and routing assertions pass | `tests/test_qa_workflows.py`, `tests/test_qa_router.py` | PASS |
| `qa-explore` | explores only an authorized surface | observation alone never manufactures PASS | contract and routing assertions pass | `tests/test_qa_workflows.py`, `tests/test_qa_router.py` | PASS |
| `qa-bug` | preserves reproduction, impact, severity, priority and evidence | an incomplete defect remains explicit | contract and routing assertions pass | `tests/test_qa_workflows.py`, `tests/test_qa_router.py` | PASS |
| `qa-regression` | traces change → risk/criterion/defect → case | missing links or current retest block completion | contract and routing assertions pass | `tests/test_qa_workflows.py`, `tests/test_qa_router.py` | PASS |
| `qa-review` | inspects recorded state without mutation | ambiguous/stale inputs remain findings | contract and routing assertions pass | `tests/test_qa_workflows.py`, `tests/test_qa_router.py` | PASS |
| `qa-release` | evaluates readiness separately from human risk acceptance | failure precedes pending; pending prevents PASS | contract and routing assertions pass | `tests/test_qa_workflows.py`, `tests/test_qa_router.py` | PASS |
| `qa-report` | exports once from one validated manifest | never runs stored tests/evidence commands or retries | contract and routing assertions pass | `tests/test_qa_workflows.py`, `tests/test_qa_report_cli.py` | PASS |
| `qa-status` | summarizes current immutable state | never repairs, discards or mutates records | contract and routing assertions pass | `tests/test_qa_workflows.py`, `tests/test_qa_router.py` | PASS |

## SCN-SPECIALISTS — all specialist surfaces

Each positive scenario is accepted only when the skill carries the surface-specific prerequisites,
expected/observed result and evidence contract. Each failure/limitation scenario must stop or
classify the unavailable operation honestly. The specialist suite evaluates both scenarios rather
than treating section presence as behavioral proof.

| specialist | positive scenario expected | failure/limitation scenario expected | observed evidence | result |
|---|---|---|---|---|
| `qa-specialist-accessibility` | scoped WCAG/assistive-tech evidence | missing browser/AT remains unverified | `tests/test_qa_specialists.py` | PASS |
| `qa-specialist-api` | contract, auth, errors and idempotency | unsafe target/credential gap blocks calls | `tests/test_qa_specialists.py` | PASS |
| `qa-specialist-automation` | deterministic suite/CI ownership | flaky or missing runner is explicit | `tests/test_qa_specialists.py` | PASS |
| `qa-specialist-cicd` | isolated artifacts and verdict-aware gate | export exit code never substitutes verdict | `tests/test_qa_specialists.py` | PASS |
| `qa-specialist-data` | authorized integrity/transaction/reconciliation checks | incomplete target/dataset/write limit blocks mutation | `tests/test_qa_specialists.py` | PASS |
| `qa-specialist-defects` | current scope and retest lineage are preserved | ambiguous scope/status blocks disposition | `tests/test_qa_specialists.py` | PASS |
| `qa-specialist-functional` | positive, negative and boundary paths | incomplete oracle remains BLOCKED | `tests/test_qa_specialists.py` | PASS |
| `qa-specialist-metrics` | auditable numerator and denominator | zero/unknown denominator has no invented percentage | `tests/test_qa_specialists.py` | PASS |
| `qa-specialist-mobile` | platform, host, SDK, device and build probes pass | any missing Android/iOS prerequisite blocks readiness | `tests/test_qa_specialists.py` | PASS |
| `qa-specialist-performance` | authorized percentiles and agreed limits | absent environment/window/limits prevents load | `tests/test_qa_specialists.py` | PASS |
| `qa-specialist-production` | read-only authorized observation | missing owner/scope/window stops production access | `tests/test_qa_specialists.py` | PASS |
| `qa-specialist-readiness` | all applicable criteria pass with no current defect | failure/pending/zero applicable criteria prevents PASS | `tests/test_qa_specialists.py` | PASS |
| `qa-specialist-regression` | change and exclusions map to deterministic cases | missing risk/criterion/defect linkage is explicit | `tests/test_qa_specialists.py` | PASS |
| `qa-specialist-requirements` | complete IDs/text/expected/observed mapping | incomplete semantic review blocks PASS | `tests/test_qa_specialists.py` | PASS |
| `qa-specialist-security` | owner, target, methods, rate, stop and cleanup authorized | incomplete pentest authority remains NOT_RUN | `tests/test_qa_specialists.py` | PASS |
| `qa-specialist-strategy` | risk-based surfaces and traceability are explicit | missing scope/constraints remain limitations | `tests/test_qa_specialists.py` | PASS |
| `qa-specialist-web` | isolated browser session uses observed refs | absent CLI/browser uses a safe alternative | `tests/test_qa_specialists.py` | PASS |

## SCN-QA-TOOLING-MISSING — unavailable Web/UI tool

Input is a Web/UI request with the explicit negative probe
`command -v playwright-cli-does-not-exist` (exit `1`, empty output). `qa-tooling` must preserve the
probe rather than infer availability:

| tool | purpose | availability | evidence | prerequisites | alternative | reason |
|---|---|---|---|---|---|---|
| `playwright-cli-does-not-exist` | interactive Web/UI exploration | missing | `command -v playwright-cli-does-not-exist` → exit 1, empty output | executable absent; browser and authorization unverified | existing Playwright Test suite or authorized manual inspection | useful surface, but the named tool is not installed |

Expected and observed: execution is `NOT_RUN`, the scenario outcome is `BLOCKED`, and the response
states no automatic installation. No installation command is executed and no result is fabricated.
The Codex executable smoke reproduced the negative probe; because `qa-tooling` itself was not
discoverable in that isolated session, the runtime stays UNVERIFIED rather than taking credit for
the hand-specified fallback.

## SCN-REPORT-FIXTURE — HTML/PDF acceptance validation

The synthetic `qa_demo.py` fixture creates `demo-manifest.json`, then publishes one package with
`manifest.json`, `report.html`, `report.pdf` and only the reviewed safe attachment. Expected and
observed are `export_status=complete` and `verdict=FAIL`: all 100 applicable criteria pass, but the
current in-scope unlinked defect `BUG-OPEN-UNMAPPED` correctly takes precedence.

Acceptance validation uses Python 3.12 with `reportlab==4.4.9`, `pypdf==6.10.0` and
`pdfplumber==0.11.9`. `tests/test_qa_scenarios.py` creates a new temporary directory, runs the real
exporter, parses the JSON manifest and UTF-8 HTML, parses every PDF page through both libraries,
and checks matching criterion IDs, status text and defect ID in both formats. It also confirms
that `credential-log.txt` and `pending-image.png` do not occur in the public package model, HTML or
PDF. The HTML was additionally opened through the installed global `playwright-cli` in the
task-owned session `qa-f05-24-report`; snapshot and reviewed screenshot showed the title, summary,
100 criteria and textual status without remote resources. A missing favicon request was the sole
browser-console error and does not affect the offline document contract.

## Acceptance mapping

| criterion | scenario/evidence | evaluation |
|---|---|---|
| CA-001 | SCN-WORKFLOWS covers all 10 workflow procedures and wrappers | PASS |
| CA-002 | SCN-SPECIALISTS covers positive and failure/limitation scenarios for all 17 specialties | PASS |
| CA-003 | runtime ledger records actual discovery/invocation/report attempts; no incomplete runtime is claimed verified | BLOCKED: 0 of 3 runtimes completed all three steps |
| CA-004 | SCN-QA-TOOLING-MISSING preserves negative evidence and refuses invented execution | PASS |
| CA-018 | bilingual plugin and root documentation is present and catalogued | PASS |
| CA-022 | missing-tool recommendation includes availability, evidence, prerequisites, alternative and reason | PASS |
| CA-023 | global and local Playwright paths, task-owned isolation and v1 evidence limits are exercised/documented | PASS with the limitations in `runtime-smoke.md` |
