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

| workflow | preconditions | actions | oracle | safety/limitation | evidence | result |
|---|---|---|---|---|---|---|
| `qa-init` | explicit objective, target, contract and project root | inspect local contracts, probe each capability and inventory constraints | ordered TARGET, OBJECTIVE, CONTRACT, CAPABILITIES and LIMITATIONS fields preserve observations | no mutation, installation or invented positive probe; missing input is BLOCKED | `tests/test_qa_workflows.py`, `tests/test_qa_core.py` exercise routing, probes and exact output | PASS |
| `qa-strategy` | bounded target, complete contract, risks and authorization | map risks to criteria/cases and consult installed `qa-tooling` | every planned case has priority, oracle, environment and traceable criterion | no execution; missing contract, oracle or authority stays BLOCKED | `tests/test_qa_workflows.py`, `tests/test_qa_tooling.py` exercise coverage and unavailable inputs | PASS |
| `qa-test` | approved cases, target identity, environment and execution authority | run only selected cases and record attempts, expected/observed and evidence | terminal attempts determine criterion results under FAIL-before-BLOCKED precedence | unavailable tool or authority remains NOT_RUN and cannot manufacture PASS | `tests/test_qa_workflows.py`, `tests/test_qa_verdict.py` exercise traceability and precedence | PASS |
| `qa-explore` | explicit charter, target, timebox, environment and authorization | inspect the authorized surface and record notes, findings and follow-up | observations remain findings until a reproducible oracle/evidence supports a result | no scope expansion; an observation alone never manufactures PASS | `tests/test_qa_workflows.py` exercises charter preservation and false-PASS refusal | PASS |
| `qa-bug` | reproducible target/build, current scope and evidence source | record steps, impact, severity, priority, links and terminal retest | current reproduction and retest lineage decide open/resolved without erasing history | no product correction; incomplete or stale proof remains a limitation | `tests/test_qa_workflows.py`, `tests/test_qa_verdict.py` exercise defect and retest semantics | PASS |
| `qa-regression` | identified change set, risks, criteria, defects and exclusions | trace change to risk/criterion/defect and select deterministic cases | every inclusion and exclusion has rationale; terminal same-case retest is authoritative | missing links or current retest block completion and prevent PASS | `tests/test_qa_workflows.py`, `tests/test_qa_specialists.py` exercise impact chains | PASS |
| `qa-review` | immutable recorded run, target, contract and evidence references | inspect requirements coverage, findings, defects and evidence sufficiency | report all contradictions and stale/missing records without rewriting them | strictly read-only; ambiguous state remains BLOCKED or a finding | `tests/test_qa_workflows.py`, `tests/test_qa_core.py` exercise read-only boundaries | PASS |
| `qa-release` | current QA verdict, applicable criteria, defects and separate decision authority | evaluate readiness and record any human risk decision independently | FAIL precedes pending; no failure plus pending is BLOCKED; clean applicable set may PASS | never publishes; risk acceptance cannot rewrite test or criterion results | `tests/test_qa_workflows.py`, `tests/test_qa_verdict.py` exercise readiness precedence | PASS |
| `qa-report` | explicit private manifest, project root and new authorized run ID | invoke the exporter exactly once and preserve diagnostics and publication attestation | HTML/PDF come from one normalized model; exit code never substitutes QA verdict | stored tests/evidence commands stay inert; no retry, overwrite or external publish | `tests/test_qa_workflows.py`, `tests/test_qa_report_cli.py` exercise export-only behavior | PASS |
| `qa-status` | existing immutable run records and explicit target context | summarize criteria, attempts, evidence, defects, limitations and verdict | output matches recorded current state without recalculation or discarded history | strictly read-only; never repairs, mutates or silently completes pending work | `tests/test_qa_workflows.py`, `tests/test_qa_core.py` exercise immutable summaries | PASS |

## SCN-SPECIALISTS — all specialist surfaces

Each positive scenario is accepted only when the skill carries the surface-specific prerequisites,
expected/observed result and evidence contract. Each failure/limitation scenario must stop or
classify the unavailable operation honestly. The specialist suite evaluates both scenarios rather
than treating section presence as behavioral proof.

| specialist | preconditions | actions | oracle | safety/limitation | evidence | result |
|---|---|---|---|---|---|---|
| `qa-specialist-accessibility` | scoped standard, browser, assistive technology and user path | inspect semantics, keyboard flow, focus, names and contrast | each finding names rule, element, observed behavior and reproducible evidence | missing browser or assistive technology remains unverified, never PASS | `tests/test_qa_specialists.py` exercises positive and unavailable accessibility scenarios | PASS |
| `qa-specialist-api` | explicit schema, endpoint, safe target, credentials and authorization | test contracts, authentication/authorization, errors and idempotency | response status/body/side effects match the declared contract and evidence | unsafe target or credential gap blocks calls as NOT_RUN | `tests/test_qa_specialists.py` exercises API success and authorization failure | PASS |
| `qa-specialist-automation` | owned suite, deterministic environment, runner and CI constraints | execute repeatable cases, isolate artifacts and classify flaky behavior | repeatability, oracle and artifact identity support each recorded outcome | missing runner is explicit; interactive CLI never replaces the CI suite | `tests/test_qa_specialists.py` exercises isolation, flaky handling and Playwright roles | PASS |
| `qa-specialist-cicd` | CI provider, immutable change/build, commands, secrets and gate policy | inspect or run the authorized pipeline and collect isolated artifacts | gate reads the QA verdict and traceable results, not exporter exit code | absent CI access remains NOT_RUN; secrets and configuration are not mutated | `tests/test_qa_specialists.py` exercises artifacts and verdict-aware gates | PASS |
| `qa-specialist-data` | engine, schema, bounded dataset, write limit and authorization | check integrity, transactions and reconciliation within the declared target | before/after values and transaction evidence prove the expected invariant | incomplete target, dataset or write limit blocks mutation | `tests/test_qa_specialists.py` exercises authorized and incomplete data scenarios | PASS |
| `qa-specialist-defects` | current target/scope, reproduction evidence and attempt lineage | classify reproduction, impact, severity, priority and terminal retest | current in-scope proven failure remains open until a valid linked retest passes | ambiguous scope or status blocks disposition and cannot hide a defect | `tests/test_qa_specialists.py`, `tests/test_qa_verdict.py` exercise defect precedence | PASS |
| `qa-specialist-functional` | explicit behavior contract, inputs, boundaries and expected results | execute positive, negative and boundary paths against one target | expected and observed behavior plus evidence decide each case result | incomplete oracle or missing evidence remains BLOCKED | `tests/test_qa_specialists.py` exercises full functional path selection | PASS |
| `qa-specialist-metrics` | target/contract, collection source, numerator, denominator, included/excluded IDs and evidence | calculate named numerator and denominator only from auditable records | published percentage reproduces exactly from the stated population | zero or unknown denominator produces no invented percentage | `tests/test_qa_specialists.py` exercises valid and zero-denominator metrics | PASS |
| `qa-specialist-mobile` | platform, host, SDK/toolchain, driver, build/signing, device and service probes | run only compatible Android or iOS cases on the identified build | every prerequisite probe and device result independently supports readiness | any missing platform prerequisite keeps execution BLOCKED/unverified | `tests/test_qa_specialists.py` exercises Android/iOS readiness and absence | PASS |
| `qa-specialist-performance` | target, environment, workload, window, percentiles, limits and authorization | execute the bounded workload and collect timing/resource measurements | observed percentiles compare against agreed limits with repeatable evidence | absent environment, window or limit prevents load and remains NOT_RUN | `tests/test_qa_specialists.py` exercises authorized and blocked performance runs | PASS |
| `qa-specialist-production` | owner, read-only scope, target, environment, window and redaction policy | observe only authorized logs/metrics/incidents and record preventive links | timestamps, queries and sanitized evidence support each production finding | missing owner, scope or window stops production access | `tests/test_qa_specialists.py` exercises the complete production boundary | PASS |
| `qa-specialist-readiness` | complete applicable criteria, terminal cases, evidence and current defects | apply failure-before-pending precedence and keep risk decision separate | PASS requires every applicable criterion PASS and no current in-scope defect | failure, pending or zero applicable criteria prevents PASS | `tests/test_qa_specialists.py`, `tests/test_qa_verdict.py` exercise readiness | PASS |
| `qa-specialist-regression` | identified change, risks, criteria, defects, cases and exclusions | select deterministic impact cases and retain terminal retest lineage | every change-to-case link and justified exclusion is reproducible | missing risk, criterion or defect linkage remains explicit and BLOCKED | `tests/test_qa_specialists.py` exercises positive and incomplete impact maps | PASS |
| `qa-specialist-requirements` | identified contract/hash, complete criterion catalog and review actor/time | compare every ID/text/applicability/expected/observed/case mapping | completeness and semantic assessment are recorded separately from file integrity | incomplete semantic review or unjustified waiver blocks PASS | `tests/test_qa_specialists.py` exercises complete and incomplete catalogs | PASS |
| `qa-specialist-security` | written owner, target, methods, environment, window, rate limit, stop conditions and cleanup | run only authorized security checks within the exact scope | every finding has reproducible evidence, impact and bounded reproduction | incomplete pentest authority keeps execution NOT_RUN and outcome BLOCKED | `tests/test_qa_specialists.py` exercises authorized scope and refusal | PASS |
| `qa-specialist-strategy` | explicit scope, risks, constraints, environments, contract and resources | prioritize surfaces and map criteria to cases, tools and evidence needs | planned coverage traces risk to criterion/case with an executable oracle | missing scope, constraint or oracle remains a blocking limitation | `tests/test_qa_specialists.py` exercises complete and incomplete strategy | PASS |
| `qa-specialist-web` | target URL, browser, session ownership, authorization and observed tool probes | use isolated browser refs/snapshot/actions or select the documented fallback | navigation and observable UI state match the declared expected behavior | absent CLI/browser remains unavailable; no personal profile or cookies | `tests/test_qa_specialists.py`, `tests/test_qa_tooling.py` exercise Web paths | PASS |

## SCN-QA-TOOLING-MISSING — unavailable Web/UI tool

Input is a Web/UI request with the explicit negative probe
`command -v pwdev-qa-missing-tool` (exit `1`, empty output). `qa-tooling` must preserve the
probe rather than infer availability:

| tool | purpose | availability | evidence | prerequisites | alternative | reason |
|---|---|---|---|---|---|---|
| `pwdev-qa-missing-tool` | interactive Web/UI exploration | missing | `command -v pwdev-qa-missing-tool` → exit 1, empty output | executable absent; browser and authorization unverified | existing Playwright Test suite or authorized manual inspection | useful surface, but the named tool is not installed |

Expected and observed: execution is `NOT_RUN`, the scenario outcome is `BLOCKED`, and the response
states no automatic installation. No installation command is executed and no result is fabricated.
All three authoritative runtime sessions invoked `qa-tooling` and reproduced this negative probe.
Each runtime preserved the missing-tool limitation while completing its independent fixture report;
tool absence never became fabricated tool execution.

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

| criterion | scenario/evidence | result | limitations |
|---|---|---|---|
| CA-001 | SCN-WORKFLOWS covers all 10 workflow procedures and wrappers | PASS | Runtime portability is assessed independently by CA-003. |
| CA-002 | SCN-SPECIALISTS covers positive and failure/limitation scenarios for all 17 specialties | PASS | External tools remain subject to each scenario's explicit probes and authorization. |
| CA-003 | Runtime ledger records 3 of 3 real runtime sessions completing discovery, invocation/missing-tool response and fixture report inspection. | PASS | Failed preliminary attempts remain non-authoritative diagnostics and do not replace the successful sessions. |
| CA-004 | SCN-QA-TOOLING-MISSING preserves negative evidence and refuses invented execution. | PASS | The missing tool remains NOT_RUN/BLOCKED even though all runtime skill invocations succeeded. |
| CA-018 | Bilingual plugin and root documentation is present and catalogued. | PASS | The legacy superseded root README-format suite remains a baseline limitation. |
| CA-022 | Missing-tool recommendation includes availability, evidence, prerequisites, alternative and reason. | PASS | The named missing executable remains unavailable; no runtime installed it. |
| CA-023 | Global and local Playwright paths, task-owned isolation and v1 evidence limits are exercised/documented. | PASS | The initial non-authoritative npx probe may have populated the npm cache; loopback serving was required because the CLI refused the report's `file:` URL. |
