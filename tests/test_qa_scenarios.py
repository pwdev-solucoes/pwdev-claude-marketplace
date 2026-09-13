import importlib.util
import json
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).parents[1]
PLUGIN = ROOT / "plugins" / "pwdev-qa"
ACCEPTANCE = PLUGIN / "references" / "acceptance-scenarios.md"
RUNTIME_SMOKE = PLUGIN / "references" / "runtime-smoke.md"
TASK_REPORT = ROOT / ".planning" / "power" / "features" / "pwdev-qa" / "task-24-report.md"

WORKFLOWS = {
    "qa-init",
    "qa-strategy",
    "qa-test",
    "qa-explore",
    "qa-bug",
    "qa-regression",
    "qa-review",
    "qa-release",
    "qa-report",
    "qa-status",
}
SPECIALISTS = {
    "qa-specialist-accessibility",
    "qa-specialist-api",
    "qa-specialist-automation",
    "qa-specialist-cicd",
    "qa-specialist-data",
    "qa-specialist-defects",
    "qa-specialist-functional",
    "qa-specialist-metrics",
    "qa-specialist-mobile",
    "qa-specialist-performance",
    "qa-specialist-production",
    "qa-specialist-readiness",
    "qa-specialist-regression",
    "qa-specialist-requirements",
    "qa-specialist-security",
    "qa-specialist-strategy",
    "qa-specialist-web",
}

RUNTIME_VERSIONS = {
    "Claude Code": "`2.1.270 (Claude Code)`",
    "Codex": "`codex-cli 0.153.4`",
    "Hermes Agent": "`Hermes Agent v0.21.1 (2026.9.7) · upstream 564aef29`",
}
RUNTIME_PROVENANCE = {
    "Claude Code": {
        "session": "b522acbc-c139-4dec-af75-abb245a7f905",
        "transcript": "/tmp/pwdev-qa-evidence-claude/transcript.jsonl",
        "sha256": "172ea6119c70e633967e26d4194a19f82c75827b302c051d31e1bb93bf88f2a5",
        "size": "153890 bytes",
        "scan": "known_credential_pattern=true",
    },
    "Codex": {
        "session": "01a09a22-f2ce-7a70-84ae-97f2b14b126e",
        "transcript": "/tmp/pwdev-qa-evidence-codex/transcript.jsonl",
        "sha256": "eed80c343749042ac6591dd1231069e594a42e17a70fe8fb3f9fc6d0b8ef2624",
        "size": "80963 bytes",
        "scan": "known_credential_pattern=true",
    },
    "Hermes Agent": {
        "session": "20260913_064516_ed1c02",
        "transcript": "/tmp/pwdev-qa-evidence-hermes-2/transcript.log",
        "sha256": "836e6b0d3c563ec047c78cfd6c68203e48833ee410cf34a500898b89c1ac3d38",
        "size": "92903 bytes",
        "scan": "known_credential_pattern=false",
    },
}
RUNTIME_ARTIFACTS = {
    "Claude Code": (
        "/tmp/pwdev-qa-evidence-claude/report/.planning/pwdev-qa/reports/qa-report-demo",
        "7f5b9d18bcb26070dbd3a841da5f5d7a460a0523527d0fa9f27fcbf55666fbfb",
    ),
    "Codex": (
        "/tmp/pwdev-qa-evidence-codex/report/.planning/pwdev-qa/reports/qa-report-demo",
        "28edb6ffb046e2db788bc0889ad8c30fc6e7a0cef382eae8901a2e456024d2b5",
    ),
    "Hermes Agent": (
        "/tmp/pwdev-qa-evidence-hermes-2/report/.planning/pwdev-qa/reports/qa-report-demo",
        "e95e48bc2f1195d5e0449db228a25219f1f2330dbe0dddfb1b50b66a487b09fe",
    ),
}
COMMON_ARTIFACT_HASHES = (
    "bc02eb690bb82a07d1d94757c5f355b6f5503bc3281511ef336208605270aa98",
    "0005e8da8befe1e2115697067fdcc21b685ebec40eae899b3e631d050eac4f02",
)
FORBIDDEN_PLACEHOLDERS = {"nonsense", "fabricated", "no evidence", "none", "n/a"}
SEMANTIC_TOKENS = {
    "qa-init": {"preconditions": ("objective", "target", "contract", "project root"), "actions": ("inspect", "probe", "inventory"), "oracle": ("TARGET", "CONTRACT", "CAPABILITIES", "LIMITATIONS"), "safety/limitation": ("no mutation", "BLOCKED")},
    "qa-strategy": {"preconditions": ("target", "contract", "risks", "authorization"), "actions": ("criteria/cases", "qa-tooling"), "oracle": ("priority", "oracle", "environment"), "safety/limitation": ("no execution", "BLOCKED")},
    "qa-test": {"preconditions": ("cases", "target", "authority"), "actions": ("attempts", "expected/observed", "evidence"), "oracle": ("terminal", "precedence"), "safety/limitation": ("NOT_RUN", "PASS")},
    "qa-explore": {"preconditions": ("charter", "target", "timebox"), "actions": ("notes", "findings", "follow-up"), "oracle": ("reproducible", "evidence"), "safety/limitation": ("no scope expansion", "PASS")},
    "qa-bug": {"preconditions": ("target/build", "scope", "evidence"), "actions": ("severity", "priority", "retest"), "oracle": ("reproduction", "lineage"), "safety/limitation": ("no product correction", "limitation")},
    "qa-regression": {"preconditions": ("change set", "risks", "exclusions"), "actions": ("risk/criterion/defect", "cases"), "oracle": ("rationale", "retest"), "safety/limitation": ("missing links", "PASS")},
    "qa-review": {"preconditions": ("immutable", "contract", "evidence"), "actions": ("coverage", "defects", "sufficiency"), "oracle": ("contradictions", "stale/missing"), "safety/limitation": ("read-only", "BLOCKED")},
    "qa-release": {"preconditions": ("QA verdict", "criteria", "decision authority"), "actions": ("readiness", "risk decision"), "oracle": ("FAIL", "BLOCKED", "PASS"), "safety/limitation": ("never publishes", "cannot rewrite")},
    "qa-report": {"preconditions": ("manifest", "project root", "run ID"), "actions": ("exporter exactly once", "attestation"), "oracle": ("HTML/PDF", "exit code", "verdict"), "safety/limitation": ("inert", "no retry")},
    "qa-status": {"preconditions": ("immutable", "target"), "actions": ("criteria", "evidence", "limitations"), "oracle": ("current state", "history"), "safety/limitation": ("read-only", "never repairs")},
    "qa-specialist-accessibility": {"preconditions": ("standard", "browser", "assistive"), "actions": ("keyboard", "focus", "contrast"), "oracle": ("rule", "element", "evidence"), "safety/limitation": ("unverified", "never PASS")},
    "qa-specialist-api": {"preconditions": ("schema", "endpoint", "credentials"), "actions": ("authentication/authorization", "idempotency"), "oracle": ("status/body", "side effects"), "safety/limitation": ("NOT_RUN", "unsafe target")},
    "qa-specialist-automation": {"preconditions": ("suite", "runner", "CI"), "actions": ("repeatable", "flaky"), "oracle": ("repeatability", "artifact"), "safety/limitation": ("missing runner", "never replaces")},
    "qa-specialist-cicd": {"preconditions": ("CI provider", "build", "gate policy"), "actions": ("pipeline", "artifacts"), "oracle": ("QA verdict", "exit code"), "safety/limitation": ("NOT_RUN", "not mutated")},
    "qa-specialist-data": {"preconditions": ("schema", "dataset", "write limit"), "actions": ("integrity", "transactions", "reconciliation"), "oracle": ("before/after", "invariant"), "safety/limitation": ("blocks mutation",)},
    "qa-specialist-defects": {"preconditions": ("scope", "reproduction", "lineage"), "actions": ("severity", "priority", "retest"), "oracle": ("current in-scope", "valid linked retest"), "safety/limitation": ("blocks disposition", "cannot hide")},
    "qa-specialist-functional": {"preconditions": ("contract", "boundaries", "expected"), "actions": ("positive", "negative", "boundary"), "oracle": ("expected", "observed", "evidence"), "safety/limitation": ("BLOCKED",)},
    "qa-specialist-metrics": {"preconditions": ("numerator", "denominator", "included/excluded"), "actions": ("calculate", "auditable"), "oracle": ("percentage", "population"), "safety/limitation": ("zero", "no invented")},
    "qa-specialist-mobile": {"preconditions": ("platform", "SDK/toolchain", "build/signing", "device"), "actions": ("Android", "iOS"), "oracle": ("prerequisite probe", "readiness"), "safety/limitation": ("BLOCKED/unverified",)},
    "qa-specialist-performance": {"preconditions": ("workload", "window", "percentiles", "authorization"), "actions": ("bounded workload", "measurements"), "oracle": ("percentiles", "limits", "evidence"), "safety/limitation": ("NOT_RUN", "prevents load")},
    "qa-specialist-production": {"preconditions": ("owner", "read-only", "window", "redaction"), "actions": ("logs/metrics/incidents", "preventive"), "oracle": ("timestamps", "queries", "sanitized"), "safety/limitation": ("stops production access",)},
    "qa-specialist-readiness": {"preconditions": ("criteria", "evidence", "defects"), "actions": ("failure-before-pending", "risk decision"), "oracle": ("every applicable", "no current"), "safety/limitation": ("zero applicable", "prevents PASS")},
    "qa-specialist-regression": {"preconditions": ("change", "risks", "exclusions"), "actions": ("impact cases", "retest lineage"), "oracle": ("change-to-case", "exclusion"), "safety/limitation": ("BLOCKED", "missing risk")},
    "qa-specialist-requirements": {"preconditions": ("contract/hash", "criterion catalog", "actor/time"), "actions": ("ID/text", "expected/observed"), "oracle": ("semantic assessment", "file integrity"), "safety/limitation": ("blocks PASS", "waiver")},
    "qa-specialist-security": {"preconditions": ("owner", "target", "methods", "window", "rate", "stop", "cleanup"), "actions": ("authorized", "exact scope"), "oracle": ("reproducible evidence", "impact"), "safety/limitation": ("NOT_RUN", "BLOCKED")},
    "qa-specialist-strategy": {"preconditions": ("scope", "risks", "constraints", "contract"), "actions": ("prioritize", "criteria", "evidence"), "oracle": ("risk", "criterion/case", "oracle"), "safety/limitation": ("blocking limitation",)},
    "qa-specialist-web": {"preconditions": ("target URL", "browser", "session ownership"), "actions": ("refs/snapshot/actions", "fallback"), "oracle": ("observable UI state", "expected"), "safety/limitation": ("personal profile", "cookies")},
}


def markdown_table(text, heading):
    start = text.index(heading)
    lines = text[start:].splitlines()
    table_start = next(index for index, line in enumerate(lines) if line.startswith("|"))
    rows = []
    for line in lines[table_start:]:
        if not line.startswith("|"):
            break
        rows.append([cell.strip() for cell in line.strip().strip("|").split("|")])
    if len(rows) < 3:
        raise AssertionError(f"{heading}: missing table rows")
    return rows[0], rows[2:]


def named_rows(text, heading, expected_header):
    header, rows = markdown_table(text, heading)
    if header != expected_header:
        raise AssertionError(f"{heading}: header {header!r} != {expected_header!r}")
    result = {}
    for row in rows:
        if len(row) != len(expected_header):
            raise AssertionError(f"{heading}: malformed row {row!r}")
        name = row[0].strip("`")
        if name in result:
            raise AssertionError(f"{heading}: duplicate row {name}")
        result[name] = dict(zip(expected_header[1:], row[1:]))
    return result


def backtick_names(text, prefix):
    return {
        name
        for name in re.findall(r"`([^`]+)`", text)
        if name.startswith(prefix)
    }


class TestRootReadmes(unittest.TestCase):
    def test_bilingual_catalogs_add_qa_once_and_group_it_by_goal(self):
        # The root READMEs follow the marketplace contract enforced by
        # tests/test_marketplace_readmes.py: one plain link in the goal table and one
        # bold row (description, version, license) in the plugin table.
        for relative in ("README.md", "README.pt-BR.md"):
            text = (ROOT / relative).read_text(encoding="utf-8")
            goal_link = "[pwdev-qa](./plugins/pwdev-qa/)"
            table_link = "[**pwdev-qa**](./plugins/pwdev-qa/)"
            self.assertEqual(text.count(goal_link), 1, relative)
            self.assertEqual(text.count(table_link), 1, relative)
            self.assertRegex(
                text,
                r"\| (?:Quality assurance|Quality assurance \(QA\)|Garantia de qualidade(?: \(QA\))?) "
                r"\| \[pwdev-qa\]\(\./plugins/pwdev-qa/\) \|",
            )
            self.assertRegex(
                text,
                r"(?m)^\| \[\*\*pwdev-qa\*\*\]\(\./plugins/pwdev-qa/\) \|[^|\n]+\| 0\.1\.0 \| Apache-2\.0 \|$",
                relative,
            )


class TestAcceptanceScenarios(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.text = ACCEPTANCE.read_text(encoding="utf-8") if ACCEPTANCE.is_file() else ""

    def test_acceptance_scenario_document_exists(self):
        self.assertTrue(ACCEPTANCE.is_file(), f"missing {ACCEPTANCE}")

    def test_every_workflow_and_specialist_has_complete_scenario_evaluation(self):
        workflow_rows = named_rows(
            self.text,
            "## SCN-WORKFLOWS",
            ["workflow", "preconditions", "actions", "oracle", "safety/limitation", "evidence", "result"],
        )
        specialist_rows = named_rows(
            self.text,
            "## SCN-SPECIALISTS",
            ["specialist", "preconditions", "actions", "oracle", "safety/limitation", "evidence", "result"],
        )
        self.assertEqual(set(workflow_rows), WORKFLOWS)
        self.assertEqual(set(specialist_rows), SPECIALISTS)
        for group in (workflow_rows, specialist_rows):
            for name, row in group.items():
                self.assertEqual(row["result"], "PASS", name)
                for field in ("preconditions", "actions", "oracle", "safety/limitation", "evidence"):
                    value = row[field]
                    self.assertGreaterEqual(len(value), 18, f"{name}: weak {field}")
                    self.assertNotIn(value.lower(), FORBIDDEN_PLACEHOLDERS, f"{name}: {field}")
                evidence_paths = re.findall(r"`(tests/[^`]+\.py)`", row["evidence"])
                self.assertTrue(evidence_paths, f"{name}: no executable evidence path")
                for evidence_path in evidence_paths:
                    self.assertTrue((ROOT / evidence_path).is_file(), f"{name}: {evidence_path}")

                for field, tokens in SEMANTIC_TOKENS[name].items():
                    for token in tokens:
                        self.assertIn(token, row[field], f"{name}: {field} missing {token}")

        qa_init = workflow_rows["qa-init"]
        for token in ("objective", "target", "contract", "project root"):
            self.assertIn(token, qa_init["preconditions"])
        for token in ("inspect", "probe", "inventory"):
            self.assertIn(token, qa_init["actions"])
        for token in ("TARGET", "CONTRACT", "CAPABILITIES", "LIMITATIONS"):
            self.assertIn(token, qa_init["oracle"])
        self.assertIn("no mutation", qa_init["safety/limitation"])

        security = specialist_rows["qa-specialist-security"]
        for token in ("owner", "target", "methods", "window", "rate", "stop", "cleanup"):
            self.assertIn(token, security["preconditions"])
        self.assertIn("authorized", security["actions"])
        self.assertIn("reproducible evidence", security["oracle"])
        for token in ("NOT_RUN", "BLOCKED"):
            self.assertIn(token, security["safety/limitation"])

    def test_semantic_destruction_mutations_are_rejected_per_row(self):
        for pattern, replacement in (
            (
                r"^\| `qa-init` \|.*$",
                "| `qa-init` | nonsense | fabricated | no evidence | none | none | PASS |",
            ),
            (
                r"^\| `qa-specialist-security` \|.*$",
                "| `qa-specialist-security` | nonsense | fabricated | no evidence | none | none | PASS |",
            ),
        ):
            mutated = re.sub(pattern, replacement, self.text, count=1, flags=re.MULTILINE)
            with self.assertRaises(AssertionError):
                rows = named_rows(
                    mutated,
                    "## SCN-WORKFLOWS" if "qa-init" in replacement else "## SCN-SPECIALISTS",
                    (["workflow", "preconditions", "actions", "oracle", "safety/limitation", "evidence", "result"]
                     if "qa-init" in replacement else
                     ["specialist", "preconditions", "actions", "oracle", "safety/limitation", "evidence", "result"]),
                )
                target = rows["qa-init" if "qa-init" in replacement else "qa-specialist-security"]
                for field in ("preconditions", "actions", "oracle", "safety/limitation", "evidence"):
                    self.assertGreaterEqual(len(target[field]), 18)
                    self.assertNotIn(target[field].lower(), FORBIDDEN_PLACEHOLDERS)
                self.assertTrue(re.findall(r"`(tests/[^`]+\.py)`", target["evidence"]))

    def test_missing_tool_scenario_is_explicit_and_never_fabricates_execution(self):
        for required in (
            "SCN-QA-TOOLING-MISSING",
            "qa-tooling",
            "missing",
            "pwdev-qa-missing-tool",
            "command -v pwdev-qa-missing-tool",
            "Playwright Test",
            "not installed",
            "NOT_RUN",
            "BLOCKED",
            "no automatic installation",
        ):
            self.assertIn(required, self.text)

    def test_report_fixture_records_cross_format_acceptance_validation(self):
        for required in (
            "SCN-REPORT-FIXTURE",
            "demo-manifest.json",
            "manifest.json",
            "report.html",
            "report.pdf",
            "BUG-OPEN-UNMAPPED",
            "credential-log.txt",
            "pending-image.png",
            "export_status=complete",
            "verdict=FAIL",
            "pypdf==6.10.0",
            "pdfplumber==0.11.9",
        ):
            self.assertIn(required, self.text)

    def test_acceptance_results_use_only_normative_values_and_separate_limitations(self):
        rows = named_rows(
            self.text,
            "## Acceptance mapping",
            ["criterion", "scenario/evidence", "result", "limitations"],
        )
        self.assertEqual(set(rows), {"CA-001", "CA-002", "CA-003", "CA-004", "CA-018", "CA-022", "CA-023"})
        for criterion, row in rows.items():
            self.assertIn(row["result"], {"PASS", "FAIL", "BLOCKED"}, criterion)
            self.assertTrue(row["limitations"], criterion)
        self.assertEqual(rows["CA-003"]["result"], "PASS")
        self.assertIn("3 of 3", rows["CA-003"]["scenario/evidence"])
        self.assertIn("preliminary", rows["CA-003"]["limitations"])
        self.assertEqual(rows["CA-023"]["result"], "PASS")
        report_text = TASK_REPORT.read_text(encoding="utf-8")
        for document in (self.text, report_text):
            self.assertNotRegex(
                document, r"PASS_WITH_LIMITATION|PASS with (?:the )?limitations"
            )

    @unittest.skipUnless(
        importlib.util.find_spec("reportlab")
        and importlib.util.find_spec("pypdf")
        and importlib.util.find_spec("pdfplumber"),
        "requires the declared Python 3.12 PDF verification environment",
    )
    def test_report_fixture_really_exports_and_validates_html_pdf(self):
        from pypdf import PdfReader
        import pdfplumber

        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary) / "fixture"
            completed = subprocess.run(
                [
                    sys.executable,
                    str(PLUGIN / "scripts" / "qa_demo.py"),
                    "--output-dir",
                    str(output),
                ],
                cwd=ROOT,
                text=True,
                capture_output=True,
                check=True,
            )
            result = json.loads(completed.stdout)
            package = Path(result["output_dir"])
            public = json.loads((package / "manifest.json").read_text(encoding="utf-8"))
            html = (package / "report.html").read_text(encoding="utf-8")
            pypdf_text = "\n".join(
                page.extract_text() or "" for page in PdfReader(package / "report.pdf").pages
            )
            with pdfplumber.open(package / "report.pdf") as document:
                plumber_text = "\n".join(page.extract_text() or "" for page in document.pages)

            self.assertEqual(result["export_status"], "complete")
            self.assertEqual(result["verdict"], "FAIL")
            self.assertEqual(
                [item["id"] for item in public["verified_evidence"]], ["ev-safe"]
            )
            for value in ("BUG-OPEN-UNMAPPED", "FAIL", "CA-001", "CA-002", "CA-003"):
                self.assertIn(value, html)
                self.assertIn(value, pypdf_text)
                self.assertIn(value, plumber_text)
            for rejected in ("credential-log.txt", "pending-image.png"):
                self.assertNotIn(rejected, json.dumps(public))
                self.assertNotIn(rejected, html)
                self.assertNotIn(rejected, pypdf_text)
                self.assertNotIn(rejected, plumber_text)


class TestRuntimeSmokeLedger(unittest.TestCase):
    def assert_runtime_contract(self, text):
        rows = named_rows(
            text,
            "## Result summary",
            ["runtime", "exact version", "status", "discovery", "invocation/missing-tool", "fixture report", "limitations"],
        )
        self.assertEqual(set(rows), set(RUNTIME_VERSIONS))
        for runtime, expected_version in RUNTIME_VERSIONS.items():
            row = rows[runtime]
            self.assertEqual(row["exact version"], expected_version)
            self.assertEqual(row["status"], "VERIFIED")
            for field in ("discovery", "invocation/missing-tool", "fixture report"):
                self.assertGreaterEqual(len(row[field]), 12, f"{runtime}: weak {field}")
                self.assertTrue(row[field].startswith("PASS —"), f"{runtime}: {field}")
            self.assertGreaterEqual(len(row["limitations"]), 12, runtime)
        self.assertIn("Aggregate status: PASS — 3 of 3 runtimes VERIFIED", text)

        sections = {}
        for runtime in RUNTIME_VERSIONS:
            match = re.search(
                rf"^## {re.escape(runtime)}\n(?P<body>.*?)(?=^## |\Z)",
                text,
                flags=re.MULTILINE | re.DOTALL,
            )
            self.assertIsNotNone(match, f"missing detailed section for {runtime}")
            sections[runtime] = match.group("body")
        shared = (
            "authoritative one-session smoke",
            "pwdev-qa:qa-tooling",
            "command -v pwdev-qa-missing-tool",
            "exit `1`",
            "missing",
            "NOT_RUN",
            "BLOCKED",
            "qa_demo.py",
            "exit `0`",
            "export_status=complete",
            "verdict=FAIL",
            "report.html",
            "171 pages",
            "CA-000..CA-099",
            "BUG-OPEN-UNMAPPED",
            "VERIFIED",
        )
        required = {
            "Claude Code": ("claude --version", "2.1.270 (Claude Code)", *shared),
            "Codex": ("codex --version", "codex-cli 0.153.4", "installed plugin discovery", *shared),
            "Hermes Agent": ("hermes --version", "a80b97b", "flattened layout", "doctor passed", *shared),
        }
        for runtime, tokens in required.items():
            for token in tokens:
                self.assertIn(token, sections[runtime], f"{runtime}: missing {token}")
            self.assertIn("### Structured observations", sections[runtime], runtime)
            observations = named_rows(
                sections[runtime],
                "### Structured observations",
                ["step", "affirmative observation", "command/result", "source locator"],
            )
            self.assertEqual(set(observations), {"discovery", "missing-tool", "fixture-report"})
            for step, observation in observations.items():
                self.assertTrue(
                    observation["affirmative observation"].startswith("OBSERVED —"),
                    f"{runtime}/{step}: observation is not affirmative",
                )
                self.assertIn("transcript", observation["source locator"])
                self.assertRegex(observation["source locator"], r"lines? `?[0-9]")

            joined = " ".join(
                value for observation in observations.values() for value in observation.values()
            )
            self.assertRegex(joined, r"invoked `pwdev-qa:qa-tooling`")
            self.assertRegex(joined, r"classified .*`missing`.*preserved .*`NOT_RUN`.*`BLOCKED`.*safe alternative")
            self.assertRegex(joined, r"inspected .*`manifest\.json`.*`report\.html`.*`report\.pdf`.*confirmed .*`CA-000\.\.CA-099`.*`BUG-OPEN-UNMAPPED`")

            provenance = RUNTIME_PROVENANCE[runtime]
            for value in provenance.values():
                self.assertIn(value, sections[runtime], f"{runtime}: missing provenance {value}")
            self.assertIn("restricted local source", sections[runtime])
            self.assertIn("not versioned", sections[runtime])
            artifact_root, pdf_hash = RUNTIME_ARTIFACTS[runtime]
            for value in (artifact_root, pdf_hash, *COMMON_ARTIFACT_HASHES):
                self.assertIn(value, sections[runtime], f"{runtime}: missing artifact binding {value}")
            if provenance["scan"] == "known_credential_pattern=true":
                self.assertIn("not publishable", sections[runtime])

        authoritative = "\n".join(sections.values())
        self.assertGreaterEqual(authoritative.count("exit `1`"), 3)
        self.assertNotRegex(authoritative, r"never invoked `pwdev-qa:qa-tooling`|no real skill invocation")
        self.assertNotRegex(authoritative, r"never classified .*`missing`|never preserved .*`NOT_RUN`/`BLOCKED`|never provided a safe alternative")
        self.assertNotRegex(authoritative, r"were not inspected|were never confirmed")
        for diagnostic in (
            "Historical preliminary diagnostics",
            "OAuth session expired",
            "npm cache",
            "non-authoritative",
        ):
            self.assertIn(diagnostic, text)
        return rows

    def test_real_runtime_results_are_versioned_reproducible_and_honest(self):
        self.assertTrue(RUNTIME_SMOKE.is_file(), f"missing {RUNTIME_SMOKE}")
        text = RUNTIME_SMOKE.read_text(encoding="utf-8") if RUNTIME_SMOKE.is_file() else ""
        for runtime in ("Claude Code", "Codex", "Hermes Agent"):
            self.assertIn(runtime, text)
        for required in (
            "qa-tooling discovery",
            "missing-tool response",
            "fixture report",
            "exact version",
            "command/probe",
            "evidence",
            "limitations",
            "VERIFIED",
            "3 of 3",
            "isolated temporary directory",
            "npx --no-install playwright --version",
            "npx playwright cli",
            "playwright-cli --version",
        ):
            self.assertIn(required, text)
        self.assert_runtime_contract(text)

    def test_false_verification_and_removed_runtime_evidence_are_rejected(self):
        text = RUNTIME_SMOKE.read_text(encoding="utf-8")
        incomplete = re.sub(
            r"^(\| Codex \| `codex-cli 0\.153\.4` \| VERIFIED \| [^|]+ \|)[^|]+(\| [^|]+ \| [^|]+ \|)$",
            r"\1 NOT_RUN — invocation evidence removed \2",
            text,
            1,
            flags=re.MULTILINE,
        )
        with self.assertRaises(AssertionError):
            self.assert_runtime_contract(incomplete)

        removed = re.sub(
            r"^## Claude Code\n.*?(?=^## Codex)",
            "## Claude Code\n\nDetailed evidence removed.\n\n",
            text,
            count=1,
            flags=re.MULTILINE | re.DOTALL,
        )
        with self.assertRaises(AssertionError):
            self.assert_runtime_contract(removed)

    def test_explicit_runtime_behavior_denials_are_rejected(self):
        text = RUNTIME_SMOKE.read_text(encoding="utf-8")
        mutations = {
            "Claude Code never invoked the skill": text.replace(
                "The authoritative one-session smoke loaded `pwdev-qa:qa-tooling`; this was real skill invocation,\n"
                "  not manifest-only discovery.",
                "The authoritative one-session smoke never invoked `pwdev-qa:qa-tooling`; there was\n"
                "  no real skill invocation.",
                1,
            ),
            "Codex never handled the missing tool": text.replace(
                "The skill classified the tool `missing`, preserved `NOT_RUN`/`BLOCKED`, provided a safe\n"
                "  alternative, and performed no installation or fictitious execution.",
                "The skill never classified the tool `missing`, never preserved `NOT_RUN`/`BLOCKED`,\n"
                "  and never provided a safe alternative.",
                1,
            ),
            "Hermes never inspected the report": text.replace(
                "were inspected; `CA-000..CA-099` and `BUG-OPEN-UNMAPPED` were confirmed.",
                "were not inspected; `CA-000..CA-099` and `BUG-OPEN-UNMAPPED` were never confirmed.",
                1,
            ),
            "probe exit was not negative": text.replace(
                "exit `1`",
                "exit `0`",
            ),
        }
        for label, mutated in mutations.items():
            with self.subTest(label=label):
                self.assertNotEqual(mutated, text, f"mutation did not apply: {label}")
                with self.assertRaises(AssertionError):
                    self.assert_runtime_contract(mutated)


if __name__ == "__main__":
    unittest.main()
