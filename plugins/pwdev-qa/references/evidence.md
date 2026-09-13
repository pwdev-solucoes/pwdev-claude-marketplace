# PWDEV QA evidence inspection

`inspect_evidence(root: Path, manifest: dict) -> list[dict]` consumes a manifest already
normalized by `validate_manifest`. It never executes a stored command and never treats file
content as instructions.

## Admission sequence

For every manifest evidence record, the inspector:

1. checks the project root and opens it without following a symlink, then traverses every
   repository-relative component from that root descriptor with no-follow `stat`, relative
   `open`, and `O_NOFOLLOW`;
2. refuses traversal, external paths, sensitive secret-bearing paths, symlinks in files or
   directories, and anything other than a regular local file;
3. safely opens the file without following a final symlink and confirms file identity;
4. rechecks actual individual and aggregate byte limits, declared size, and SHA-256;
5. verifies the declared media type from inert bytes: UTF-8 text, parsed inert JSON, a complete
   CRC-checked PNG chunk stream, palette constraints, and compressed image payload, or a complete
   JPEG marker/scan stream ending in `EOI`;
6. refuses images over 20 megapixels and requires a recorded visual review for every image;
7. checks text for bounded known credential patterns and recursively checks every decoded JSON
   object pair, key, and string value—including duplicate and Unicode-escaped keys before any
   overwrite—without claiming universal detection.

Unsafe paths, formats, file kinds, or exceeded limits raise `EvidenceError` and the caller must
refuse export. Missing, changed, target-incompatible, credential-bearing, or pending-review
attachments produce a neutral `BLOCKED` diagnostic and `copy_allowed=false`.

## Public projection

Every result preserves the evidence ID, target ID, and contract path/hash. A `VERIFIED` result
also exposes only the approved relative path, SHA-256, media type, and actual byte size, with
`copy_allowed=true` and `requires_copy_revalidation=true`. Here, `copy_allowed` records only the
eligibility of the inspected snapshot. It is never durable authorization to resolve that pathname
later. A `BLOCKED` result never exposes the rejected path, digest, media metadata, matched
credential fragment, or file content.

## Atomic copy revalidation contract

Immediately before copying, an exporter must repeat descriptor-relative traversal from a newly
opened project-root descriptor, with no-follow checks on every component. It must reopen the
source regular file, revalidate identity, actual individual/aggregate size, SHA-256, MIME/image
structure, target, contract, credential policy, and sanitization state, and copy bytes from that
same open descriptor into an exclusive temporary destination. A post-read `fstat` must confirm
the source snapshot did not change. Only that temporary copy may proceed to the report's atomic
publication step. Any mismatch discards the temporary attachment, produces a sanitized blocker,
and prevents `PASS`; the exporter must never fall back to copying from the projected pathname.

Any `BLOCKED` result prevents a later global `PASS` until corrected and re-inspected. Evidence
inspection does not itself calculate the QA verdict.

## Safety boundary

Do not point evidence records at `.env`, credential stores, private-key files, certificates,
personal browser data, or real secrets. Use only synthetic fixtures or evidence sanitized under
the shared [safety policy](safety.md) and [artifact contract](artifacts.md). JSON remains inert;
the inspector parses it only to establish its media type and scans its textual representation
for the bounded credential patterns.
