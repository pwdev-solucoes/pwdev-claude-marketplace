# Task 16 — implementation report

Status: DONE_WITH_CONCERNS

## Delivered

- Added a reproducible 100-criterion fixture whose criterion texts are exactly 2,000 characters.
- Added end-to-end assertions against the source manifest and public normalized model for exact cardinality and 1:1 IDs, complete 2,000-character text sentinels, expected/observed values, defects, approved evidence references, and verdict in HTML plus PDF extracted independently by pypdf and pdfplumber.
- Added credential-bearing log and pending-review PNG scenarios; neither attachment is published, both prevent PASS, and a proven current in-scope defect without criterion IDs produces FAIL.
- Added an explicit-output demo CLI that refuses an existing directory and pins the PDF verification dependencies in `requirements-dev.txt`.

## TDD and verification evidence

- RED: bundled Python 3.12, `python3 -m unittest tests.test_qa_reports_e2e` — 3 tests failed because `qa_demo.py` and `requirements-dev.txt` were absent.
- GREEN: bundled Python 3.12, same focused command — 3 tests passed.
- Regression: bundled Python 3.12, `python3 -m unittest discover -s tests -p 'test_qa*.py'` — 142 tests passed.
- Compatibility syntax: system Python 3.9.6, `py_compile` for both new Python files — passed.
- Diff hygiene: `git diff --check` — passed.

## Correction round 1

- The oracle now requires exactly 100 source criteria, 100 public criteria, and 100 criterion results, then compares both public ID sequences 1:1 with the source before any per-item iteration; silent `zip` truncation is impossible.
- Every HTML criterion row is scoped and checked independently for the full escaped 2,000-character text plus its ID, expected, observed, and result.
- Each pypdf and pdfplumber criterion block is scoped independently. Its complete ordered sentinel sequence includes the final 9-character fragment (for example `c000w0181`) and separately checks ID, expected, observed, and result.
- Mutation RED: truncating the renderer's final 9 characters made the focused suite fail on the missing `c000w0181` sentinel. The renderer was restored byte-for-byte, and the focused suite returned to 3 passing tests.
- Fresh correction verification: Python 3.12 full QA discovery passed 142 tests; Python 3.9.6 compile passed; `git diff --check` passed.
- Fresh visual/browser smoke: the demo remained a complete FAIL export with a 171-page A4 PDF; Poppler pages 1, 100, and 171 and a new isolated-session HTML screenshot/snapshot were inspected successfully. Only the expected missing favicon 404 appeared; the session and loopback server were closed.

## Visual and browser inspection

- Generated the demo in a fresh temporary directory: complete export, expected global verdict FAIL, 171-page A4 PDF.
- Rendered pages 1, 100, and 171 with Poppler and visually inspected them: pagination, complete wrapped criterion text, diagnostics, evidence, and textual verdict were legible with no observed clipping or overlap.
- Global `playwright-cli` 0.1.14 was available. Opened HTML through a loopback-only server in isolated session `qa-report`, captured a fresh snapshot and screenshot, reviewed both, and closed only that session. The sole console entry was the expected absent `favicon.ico` (404).
- Temporary outputs and generated caches were moved to the macOS Trash and remain recoverable.

## Concern

- The literal focused command with system Python 3.9.6 cannot import `pdfplumber`; this is an environment/dependency failure, not an approval. The specified bundled Python 3.12 environment contains the exact pinned verification dependencies and passed focused plus full QA regression.
