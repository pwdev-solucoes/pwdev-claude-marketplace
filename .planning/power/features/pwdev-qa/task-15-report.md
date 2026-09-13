# Task 15 — implementation report

Status: COMPLETE
Task: F03-15 — CLI e publicação do pacote
Date: 2026-09-13

## Delivered

- Added `generate_report(manifest_path, project_root)` and `main(argv=None)` with the exact
  `report --manifest PATH --project-root PATH` CLI.
- Added descriptor-relative, no-follow output traversal, exclusive sibling staging, source
  evidence reopen/revalidation, exclusive same-descriptor copies, safe staging paths, complete
  package validation, and an atomic no-overwrite rename.
- Added allowlisted `manifest.json`, static HTML, PDF, approved attachments, and exclusive
  diagnostic-only partial directories for incomplete exports.
- Kept stored command strings inert and private extension fields only in the original manifest.
- Documented the package, exit codes, public/private boundary, evidence behavior, and partial
  export semantics in `references/reports.md`.

## TDD evidence

RED:

```text
python3 -m unittest tests.test_qa_report_cli
Ran 5 tests in 0.004s
FAILED (failures=5: qa_report.py is missing)
```

GREEN after implementation and race/symlink probes:

```text
python3 -m unittest tests.test_qa_report_cli
Ran 8 tests in 0.044s
OK
```

The probes cover an output-component symlink, a source replaced by a symlink after inspection,
a source changed after inspection, a final-directory collision won immediately before rename,
an unavailable PDF renderer, and a renderer returning without a PDF artifact.

## Verification

```text
python3 -m unittest tests.test_qa_contract tests.test_qa_evidence tests.test_qa_verdict tests.test_qa_html tests.test_qa_report_cli
Ran 51 tests in 3.436s — OK

<bundled-python-3.12> -m unittest tests.test_qa_report_cli tests.test_qa_pdf
Ran 18 tests in 3.839s — OK

python3 -m unittest tests.test_qa_core tests.test_qa_runtime_contracts tests.test_qa_specialists tests.test_qa_tooling
Ran 63 tests in 0.069s — OK

<bundled-python-3.12> -m unittest discover -s tests -p 'test_qa*.py'
Ran 124 tests in 6.170s — OK

python3 -m py_compile plugins/pwdev-qa/scripts/qa_report.py tests/test_qa_report_cli.py
OK

git diff --check
OK
```

A real ReportLab integration probe with the bundled Python 3.12 published a complete two-page
PDF package, reopened it with pypdf, and verified the copied attachment bytes. The system
`python3` is Python 3.9.6 and does not include ReportLab; the CLI correctly records a diagnostic
partial and returns exit code 3 in that environment. No dependency was installed.

## Scope

Only the three implementation files authorized by the brief and this task report are included
in the task commit. Pre-existing ledger, review-package, and earlier-task changes remain
untouched and uncommitted.
