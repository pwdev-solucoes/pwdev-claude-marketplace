# PWDEV QA evidence inspection

`inspect_evidence(root: Path, manifest: dict) -> list[dict]` consumes a manifest already
normalized by `validate_manifest`. It never executes a stored command and never treats file
content as instructions.

## Admission sequence

For every manifest evidence record, the inspector:

1. checks the project root and every repository-relative path component with `lstat`;
2. refuses traversal, external paths, sensitive secret-bearing paths, symlinks in files or
   directories, and anything other than a regular local file;
3. safely opens the file without following a final symlink and confirms file identity;
4. rechecks actual individual and aggregate byte limits, declared size, and SHA-256;
5. verifies the declared media type from inert bytes: UTF-8 text, parsed inert JSON, PNG `IHDR`,
   or a JPEG frame carrying dimensions;
6. refuses images over 20 megapixels and requires a recorded visual review for every image;
7. checks text and JSON for bounded known credential patterns without claiming universal secret
   detection.

Unsafe paths, formats, file kinds, or exceeded limits raise `EvidenceError` and the caller must
refuse export. Missing, changed, target-incompatible, credential-bearing, or pending-review
attachments produce a neutral `BLOCKED` diagnostic and `copy_allowed=false`.

## Public projection

Every result preserves the evidence ID, target ID, and contract path/hash. A `VERIFIED` result
also exposes only the approved relative path, SHA-256, media type, and actual byte size, with
`copy_allowed=true`. A `BLOCKED` result never exposes the rejected path, digest, media metadata,
matched credential fragment, or file content. Exporters may copy only records whose status is
`VERIFIED` and whose `copy_allowed` value is true.

Any `BLOCKED` result prevents a later global `PASS` until corrected and re-inspected. Evidence
inspection does not itself calculate the QA verdict.

## Safety boundary

Do not point evidence records at `.env`, credential stores, private-key files, certificates,
personal browser data, or real secrets. Use only synthetic fixtures or evidence sanitized under
the shared [safety policy](safety.md) and [artifact contract](artifacts.md). JSON remains inert;
the inspector parses it only to establish its media type and scans its textual representation
for the bounded credential patterns.
