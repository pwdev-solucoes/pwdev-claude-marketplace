# PWDEV QA artifact and evidence contract

QA evidence must remain attributable, confined, size-bounded, and safe to share. A path or hash
alone does not prove that evidence is complete, current, truthful, or sufficient.

## Evidence admission

An evidence attachment must be a regular local file beneath the authorized project root. Its
path is repository-relative, normalized, confined, and free of traversal. Reject absolute paths,
path escapes, symlinks, and any destination chain containing a symlink.

Every evidence record identifies:

- a unique evidence ID and allowed media type;
- its repository-relative path, byte size, and SHA-256 digest;
- the target ID and contract it supports;
- the criterion, case, defect, or assessment that refers to it;
- a sanitization review status, actor, and timestamp.

Accepted media types in v1 are `text/plain`, `application/json`, `image/png`, and `image/jpeg`.
Treat JSON as inert text. Do not attach SVG, HTML, PDF, executable files, traces, or videos.

Sanitization status is `synthetic`, `reviewed`, or `pending`. A pending sanitization review
prevents copying the attachment and prevents `PASS`. Images require a recorded visual review.
Known credential patterns are rejected. Never claim universal secret detection.

## Input limits

- Manifest: 5 MiB.
- Criteria: at most 1000.
- Evidence records: at most 1000.
- Individual evidence file: 10 MiB.
- All evidence files: 100 MiB.
- Image dimensions: at most 20 megapixels.

Exceeding a limit is an explicit error; never silently truncate content.

## Run identity and publication

The caller supplies a run ID matching `^[a-z0-9][a-z0-9-]{0,63}$`. A new run never overwrites
an existing directory. Complete artifacts belong under
`.planning/pwdev-qa/reports/<run-id>/`.

Publish a complete report only after both HTML and PDF validate. Build them in an exclusive
sibling temporary directory and rename only after both formats succeed. A collision or invalid
input publishes nothing as complete. If PDF export fails, preserve only an explicitly named
partial diagnostic directory, never the complete report path.

HTML is static offline UTF-8 with no JavaScript or remote resources. PDF is A4 with 18 mm margins,
pagination, and textual status labels. Both derive from the same normalized manifest and carry
the same IDs, texts, expected and observed values, evidence references, defects, and verdict.

## Evidence verification

Before export, re-check that each admitted file remains regular and confined, is not a symlink,
matches its recorded size and SHA-256, matches the target and contract, uses an accepted media
type, and has completed sanitization review. Missing or changed evidence produces a diagnostic,
is not copied, and prevents `PASS`. Unsafe evidence or an invalid schema refuses export.
