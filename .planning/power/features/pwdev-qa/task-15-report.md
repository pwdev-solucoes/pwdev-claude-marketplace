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

## Correction round 1

The two Important findings in `task-15-review.md` were reproduced before correction:

```text
python3 -m unittest <malformed-pdf> <reports-root-exchange> <published-pdf-exchange>
Ran 3 tests — FAILED (failures=3)
```

The correction now snapshots the complete staging tree and, after the atomic rename, twice
reopens the reports root and run directory through the nominal no-follow path. Directory
identities plus the recursive inventory, file identities, sizes, and SHA-256 hashes must match.
On mismatch, cleanup removes only unchanged owned artifacts; replacement files, directories, and
sentinels remain untouched. A run-directory exchange probe was added as a separate boundary case.

PDF validation no longer accepts header/EOF markers alone. A standard-library parser validates
the numeric `startxref`, classic xref subsections and entries, trailer `/Size` and `/Root`, live
root object reference, and terminal EOF. No verification library became an export dependency.

GREEN, explicit regression reversal, and restoration:

```text
python3 -m unittest <three reviewer probes>
Ran 3 tests — OK

# protections temporarily reverted
python3 -m unittest <three reviewer probes>
Ran 3 tests — FAILED (failures=3)

# protections restored
python3 -m unittest <three reviewer probes>
Ran 3 tests — OK

python3 -m unittest tests.test_qa_report_cli
Ran 12 tests in 0.055s — OK

<bundled-python-3.12> -m unittest discover -s tests -p 'test_qa*.py'
Ran 128 tests in 6.278s — OK

python3 -m py_compile plugins/pwdev-qa/scripts/qa_report.py tests/test_qa_report_cli.py
OK

git diff --check
OK
```

The ReportLab 4.4.9 integration was repeated with bundled Python 3.12: publication returned
`complete`, pypdf strict mode reopened all 7 pages, and the copied attachment remained identical.

## Correction round 2

The controller ruling defines the atomic no-overwrite rename as the publication commit. The
finite post-rename snapshots from round 1 were removed: they could not prove future immutability
and incorrectly classified external post-commit mutation as exporter failure. Root and staging
identity/content are revalidated immediately before the commit; collisions remain non-overwrite.

Every complete result now returns a deterministic, inode-independent `publication_snapshot` of
the staged directory/file inventory, sizes, and SHA-256 values, plus `publication_digest`, the
SHA-256 of canonical JSON. Independent tests mutate the PDF or replace the run directory after
commit, classify those changes as external, and prove the recomputed consumer digest diverges.

The standard-library PDF parser now dereferences `/Root` into a `/Type /Catalog` dictionary,
dereferences its live `/Pages` dictionary, validates non-negative integer `/Count`, parses the
`/Kids` reference array, checks count consistency, and dereferences each child. A coherent xref
whose root body is garbage is refused as an incomplete export.

TDD and regression reversal:

```text
python3 -m unittest <catalog-pages> <digest> <post-commit> <pre-commit-staging>
RED: semantic garbage accepted; digest absent; post-commit misclassified; staging swap accepted

python3 -m unittest <six correction probes>
GREEN: Ran 6 tests — OK

# semantic parser, digest calculation, and staging comparison temporarily reverted
python3 -m unittest <three regression probes>
Ran 3 tests — FAILED (failures=3)

# protections restored
python3 -m unittest <three regression probes>
Ran 3 tests — OK

python3 -m unittest tests.test_qa_report_cli
Ran 15 tests in 0.076s — OK

<bundled-python-3.12> -m unittest discover -s tests -p 'test_qa*.py'
Ran 131 tests in 6.174s — OK

python3 -m py_compile plugins/pwdev-qa/scripts/qa_report.py tests/test_qa_report_cli.py
OK

git diff --check
OK
```

The ReportLab 4.4.9 integration was repeated with bundled Python 3.12: strict pypdf reopened all
7 pages, the attachment was identical, and an independently rebuilt snapshot produced the exact
returned publication digest. No parser dependency was added to export.

## Correction round 3

The staging descriptor now remains open across the no-replace rename. Snapshot and digest are
computed from that same descriptor only after commit, so a mutation in the last pre-syscall window
is represented by the returned attestation. One immediate nominal no-follow check then binds the
retained reports/run identities to `output_dir`; a root swap spanning the syscall fails and cleanup
removes only the package in the retained reports directory, leaving the nominal sentinel intact.
Mutation injected after this final check remains external under the controller ruling and is
detected by a consumer rebuilding the returned snapshot/digest.

PDF validation now walks nested Pages nodes recursively. Each Kid must dereference to a dictionary
with exactly one `/Type /Page` or `/Type /Pages`; ancestor cycles, duplicate Pages nodes, duplicate
Page leaves, invalid children, and recursive `/Count` mismatches are rejected. A nested two-leaf
tree is accepted, and the real ReportLab tree remains compatible.

TDD and explicit reversal/restoration:

```text
RED: garbage child and self-cycle published; exact pre-syscall staging/root probes diverged
GREEN: recursive tree and retained-descriptor commit probes passed

# recursive walk, post-commit snapshot, and nominal commit check temporarily reverted
python3 -m unittest <three round-3 regression probes>
Ran 3 tests — FAILED (failures=7 across subtests)

# protections restored
python3 -m unittest <three round-3 regression probes>
Ran 3 tests — OK

python3 -m unittest tests.test_qa_report_cli
Ran 19 tests in 0.099s — OK

<bundled-python-3.12> -m unittest discover -s tests -p 'test_qa*.py'
Ran 135 tests in 6.106s — OK

python3 -m py_compile plugins/pwdev-qa/scripts/qa_report.py tests/test_qa_report_cli.py
OK

git diff --check
OK
```

The final ReportLab 4.4.9 integration published 7 pages, reopened them with pypdf strict mode,
verified the attachment, and independently reproduced the committed snapshot and digest.

## Correction round 4

The two remaining round-3 findings were reproduced at their exact boundaries before correction.
The publication probes now mutate `report.pdf` or exchange the nominal reports root immediately
after the real no-overwrite rename syscall but before `_rename_no_replace_syscall` returns. The PDF
fixtures include a false `/Type /Page` in a string, false types in comments/streams, an
unterminated string, and an unbalanced nested dictionary.

The commit helper now performs the last nominal-root probe, flushes all staged files/directories,
and fixes the canonical snapshot/digest immediately before invoking the rename syscall. It returns
that fixed value; no package reread or nominal-path decision occurs after a successful syscall.
Consequently, pre-syscall staging mutation remains represented by the attestation, pre-syscall
root exchange still fails without touching the sentinel, and post-syscall mutation is external and
causes a consumer recomputation to diverge from the returned digest.

PDF Page/Pages validation now uses a standard-library tokenizer/parser. Strings, comments, and
stream bodies are opaque while keys are located; dictionaries, arrays, literal strings, and hex
strings must be balanced; `/Type`, `/Pages`, `/Count`, and `/Kids` are unique direct dictionary
entries with the required parsed value types. Recursive cycle, duplicate-node, live-reference,
and descendant-count checks remain in force. No PDF verification dependency was added at runtime.

Fresh TDD and verification evidence:

```text
# initial RED and explicit reversal
python3 -m unittest <round-4 exact probes>
FAILED (false Page types/unterminated strings published; post-syscall mutation changed success or attestation)

# restored GREEN, including pre-syscall regressions
python3 -m unittest <round-4 exact probes plus pre-syscall probes>
Ran 5 tests — OK

python3 -m unittest tests.test_qa_report_cli
Ran 20 tests — OK

<bundled-python-3.12> -m unittest discover -s tests -p 'test_qa*.py'
Ran 136 tests — OK

# ReportLab 4.4.9 integration
complete/PASS, 7 pages in pypdf 6.10.0 strict mode, pdfplumber text extracted,
and consumer snapshot/digest matched the returned attestation
```
