# Task 16 — implementation report

Status: DONE_WITH_CONCERNS

## Delivered

- Added a reproducible 100-criterion fixture whose criterion texts are exactly 2,000 characters.
- Added end-to-end assertions against the source manifest and public normalized model for IDs, full-text tokens, expected/observed values, defects, approved evidence references, and verdict in HTML plus PDF extracted independently by pypdf and pdfplumber.
- Added credential-bearing log and pending-review PNG scenarios; neither attachment is published, both prevent PASS, and a proven current in-scope defect without criterion IDs produces FAIL.
- Added an explicit-output demo CLI that refuses an existing directory and pins the PDF verification dependencies in `requirements-dev.txt`.

## TDD and verification evidence

- RED: bundled Python 3.12, `python3 -m unittest tests.test_qa_reports_e2e` — 3 tests failed because `qa_demo.py` and `requirements-dev.txt` were absent.
- GREEN: bundled Python 3.12, same focused command — 3 tests passed.
- Regression: bundled Python 3.12, `python3 -m unittest discover -s tests -p 'test_qa*.py'` — 142 tests passed.
- Compatibility syntax: system Python 3.9.6, `py_compile` for both new Python files — passed.
- Diff hygiene: `git diff --check` — passed.

## Visual and browser inspection

- Generated the demo in a fresh temporary directory: complete export, expected global verdict FAIL, 171-page A4 PDF.
- Rendered pages 1, 100, and 171 with Poppler and visually inspected them: pagination, complete wrapped criterion text, diagnostics, evidence, and textual verdict were legible with no observed clipping or overlap.
- Global `playwright-cli` 0.1.14 was available. Opened HTML through a loopback-only server in isolated session `qa-report`, captured a fresh snapshot and screenshot, reviewed both, and closed only that session. The sole console entry was the expected absent `favicon.ico` (404).
- Temporary outputs and generated caches were moved to the macOS Trash and remain recoverable.

## Concern

- The literal focused command with system Python 3.9.6 cannot import `pdfplumber`; this is an environment/dependency failure, not an approval. The specified bundled Python 3.12 environment contains the exact pinned verification dependencies and passed focused plus full QA regression.
