# Task 11 — implementation report

Status: DONE
Task: F03-11 — Integridade e sanitização de evidências
Date: 2026-09-12

## Delivered

- Added `inspect_evidence(root: Path, manifest: dict) -> list[dict]` and `EvidenceError` in the
  importable, standard-library-only Python 3.9 evidence layer.
- Evidence paths are independently normalized and checked component by component with `lstat`;
  external paths, sensitive secret-bearing paths, file/directory symlinks, and non-regular files
  stop export before content inspection.
- Safe opening does not follow the final symlink and rechecks file identity. Actual individual
  and aggregate sizes, SHA-256, target ID, declared size, media signature, and image dimensions
  are verified from the local file. PNG and JPEG images are limited to 20 megapixels.
- UTF-8 logs and inert JSON are checked for bounded known credential patterns. Credential-bearing
  attachments and pending/unreviewed visual evidence are withheld and return sanitized `BLOCKED`
  diagnostics; the projection never includes a matched fragment or rejected file content/path.
- Verified projections preserve evidence ID, target ID, contract path/hash, and only the approved
  path/hash/media type/actual size metadata needed by a later exporter.
- Added the shared evidence reference defining admission order, public projection, blocking
  semantics, and the no-`.env`/no-real-secret safety boundary.

## TDD evidence

- RED: `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_qa_evidence` — 7 tests ran with
  11 expected assertion failures because `qa_evidence.py` did not exist; this was a behavioral
  failure rather than an import error.
- GREEN: `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_qa_evidence` — 8 tests passed
  after the minimum implementation and race-safe file-size recheck.
- Diff-review RED: the isolated real-MIME scenario failed once because valid JSON declared as
  `text/plain` was accepted. After the minimum signature distinction, all 8 focused tests passed.
- QA regression: `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest $(rg --files tests | sed -n
  's#^tests/\(test_qa_[^/]*\)\.py$#tests.\1#p' | sort | tr '\n' ' ')` — 84 tests passed.
- Contract checks: `python3 -m py_compile plugins/pwdev-qa/scripts/qa_evidence.py` and
  `git diff --check` passed.

## Scenario coverage

Synthetic temporary fixtures cover accepted text; missing, size-changed, hash-changed, and
target-incompatible evidence; traversal; symlink files and directories; `.env` refusal before
inspection; actual 10 MiB/100 MiB limits; MIME mismatch; a PNG over 20 megapixels; credential
patterns in log and JSON; and a pending visual review. Fixtures contain no real credentials.

## Limitations

- Credential detection is intentionally bounded and does not promise universal secret detection.
- The inspector produces safe admission records but does not copy attachments or calculate the
  global verdict; later layers must copy only `VERIFIED`/`copy_allowed=true` records and treat any
  `BLOCKED` record as incompatible with global `PASS`.
- No evidence command, `.env`, real secret, plugin used as reference, ledger/review artifact,
  dependency, personal configuration, publication, push, or merge was read or changed.

## Files

- `plugins/pwdev-qa/scripts/qa_evidence.py`
- `plugins/pwdev-qa/references/evidence.md`
- `tests/test_qa_evidence.py`
- `.planning/power/features/pwdev-qa/task-11-report.md`
