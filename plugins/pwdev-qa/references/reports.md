# PWDEV QA report publication

Run the local exporter without installing the plugin:

```text
python3 plugins/pwdev-qa/scripts/qa_report.py report \
  --manifest path/to/private-manifest.json \
  --project-root path/to/project
```

`generate_report(manifest_path: Path, project_root: Path) -> dict` and the CLI perform the
same sequence: validate the private manifest, inspect evidence, consolidate the verdict, copy
only revalidated attachments, render both formats, validate the package, and publish it with one
atomic no-overwrite rename. Stored `command` values remain inert text throughout.

## Package and public boundary

A complete package is published only at
`.planning/pwdev-qa/reports/<run-id>/` and contains `report.html`, `report.pdf`,
`manifest.json`, plus `attachments/` when approved evidence exists. The public manifest is the
allowlisted report model used by both renderers. Unknown extension fields remain only in the
caller-owned private input; rejected evidence paths, metadata, and content are not projected.

The exporter reopens each initially `VERIFIED` source through a new project-root descriptor. It
refuses symlinks, rechecks regular-file identity, byte limits, size, SHA-256, MIME structure,
credential patterns, target, contract, and sanitization state, and writes an exclusive staging
attachment from that same descriptor. Missing or changed evidence becomes a sanitized diagnostic,
is withheld, and prevents `PASS`. Unsafe evidence or invalid schema refuses export.

Staging is an exclusive sibling directory. Every component of the project/output path is opened
without following symlinks. HTML, PDF, the public manifest, and every attachment are reopened and
validated before the exclusive atomic rename. PDF validation uses the standard library to verify
the numeric `startxref`, classic xref entries, trailer `/Size` and `/Root`, referenced root object,
and final EOF produced by ReportLab. It also dereferences `/Root` as a `/Type /Catalog`
dictionary, dereferences its `/Pages` dictionary, and checks non-negative `/Count`, `/Kids`, and
live child references. Marker-only, xref-only, garbage-root, or malformed files are incomplete.

Immediately before commit, the exporter reopens the nominal reports root without following
symlinks and confirms its identity, then re-snapshots staging and compares it with the validated
snapshot. A root/staging exchange or destination collision observed before the syscall fails and
does not overwrite sentinels. The no-overwrite directory rename is the publication commit point.

No finite sequence of reads can make files immutable after that commit. Mutation by another actor
after the rename is external to exporter success, even when it occurs before the caller consumes
the return value. For consumer revalidation, every complete result includes
`publication_snapshot`—a path-keyed inventory of directory kinds and file byte sizes/SHA-256—and
`publication_digest`, the lowercase SHA-256 of its canonical UTF-8 JSON (`ensure_ascii=false`,
keys sorted, separators `,` and `:`). A consumer that needs current integrity must rebuild the
snapshot from `output_dir`, recompute the digest, and compare it with the returned digest.

## Results and failures

The result object contains `run_id`, `verdict`, `export_status`, `output_dir`, `diagnostics`,
`publication_snapshot`, and `publication_digest`. Incomplete results use an empty snapshot and a
null digest.
Exit code `0` means both formats were published, independently of a QA verdict of `PASS`, `FAIL`,
or `BLOCKED`. Exit code `2` means invalid or unsafe input/output. Exit code `3` means export was
incomplete, including an unavailable `reportlab==4.4.9` or a write/render failure.

An incomplete export never occupies the complete run path. The exporter removes staging content
and preserves only `diagnostic.json` in an exclusive `<run-id>.partial-<token>/` directory. That
partial directory is diagnostic state, not a report package and must not be treated as complete.
