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

## Review correction — round 1

- Replaced pathname reopening with descriptor-relative traversal rooted in a verified project
  directory descriptor. Every component uses no-follow metadata inspection plus relative
  `open`/`O_NOFOLLOW`; file reads remain bound to the opened parent descriptor.
- Added a deterministic parent-swap probe. It renames the already opened parent and replaces its
  pathname with a symlink to attacker-controlled bytes before the file open; inspection still
  reads the original descriptor-held snapshot and never follows the replacement pathname.
- `VERIFIED` now includes `requires_copy_revalidation=true`. The reference explicitly defines
  `copy_allowed` as snapshot eligibility, never durable authorization, and requires the exporter
  to reopen, revalidate, and copy from one descriptor into an exclusive temporary destination.
- PNG admission now verifies the complete chunk stream, CRCs, critical structure, palette rules,
  consecutive IDAT data, bounded decompression, row size/filter consistency, and terminal IEND.
  JPEG admission validates segment lengths, frame/scan structure, entropy presence, and terminal
  EOI. Tests use complete synthetic PNG/JPEG fixtures and reject truncated/malformed variants.
- JSON credential checks now recursively inspect decoded keys and string values, so Unicode
  escapes such as `api\\u005fkey` cannot evade the known-pattern policy; diagnostics continue to
  expose no matched fragment, rejected path, or content.

### Correction TDD and verification evidence

- RED: focused correction probes failed on all confirmed gaps: parent swap was not descriptor
  bound; truncated/malformed images were admitted; Unicode-escaped JSON credentials were
  `VERIFIED`; and verified output omitted mandatory copy revalidation.
- GREEN: `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest -v tests.test_qa_evidence` — 9 tests
  passed after the fixes.
- Regression proof: with the corrected tests retained and only `qa_evidence.py` temporarily
  reversed to its prior version, the four targeted correction tests produced 4 failures. Restoring
  the staged implementation returned the same four probes to 4 passing tests.
- Adversarial probes cover deterministic parent swap, complete/truncated/malformed PNG, complete
  and truncated JPEG, escaped semantic JSON keys, sanitized projections, and copy revalidation.
- Independent fixture probe: macOS `sips` decoded the embedded JPEG with `pixelWidth: 1` and
  `pixelHeight: 1`; the focused suite itself requires no imaging dependency.
- QA regression: all 85 `test_qa_*` tests passed; Python compilation and staged `git diff --check`
  passed after restoration.
- No ledger, review artifact, brief, plugin used as reference, dependency, personal configuration,
  publication, push, or merge was changed.

## Review correction — round 2

- PNG `PLTE` validation now permits only one palette, preserves the existing placement/length and
  color-type rules, and limits indexed-color entries to `2^bit_depth`. Synthetic probes reject a
  1-bit image with three entries and an image with duplicate palettes while admitting a complete
  1-bit image with exactly two entries.
- JSON parsing now retains every decoded object pair instead of materializing a last-write-wins
  dictionary. Credential inspection visits all keys and string values, so an escaped first
  `api_key` occurrence cannot be erased by a later duplicate. The result remains a neutral
  `BLOCKED` projection without path, content, credential name, or matched fragment.
- RED: the two targeted correction tests produced 3 failures: both malformed indexed PNG variants
  were admitted and the overwritten Unicode-escaped credential returned `VERIFIED`.
- GREEN: the same two targeted tests passed after the minimal parser changes.
- Regression proof: with corrected tests retained and only the round-2 production patch reversed,
  the two targeted methods reproduced all 3 failures. Restoring the staged implementation returned
  both methods to green, including the valid indexed-PNG boundary case.
- Final verification: `tests.test_qa_evidence` passed 10 tests; the complete `test_qa_*` regression
  passed 86 tests; Python compilation and staged `git diff --check` passed.
