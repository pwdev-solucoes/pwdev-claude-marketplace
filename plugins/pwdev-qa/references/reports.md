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
and final EOF produced by ReportLab; marker-only or malformed files are incomplete exports.

After rename, the exporter reopens the reports root and run directory through the nominal project
path without following symlinks. It compares their identities and the recursive inventory,
identities, sizes, and SHA-256 hashes of every artifact with the staging snapshot, then repeats the
whole nominal check. Any root, run-directory, file, or attachment exchange fails explicitly.
Cleanup removes only entries still matching the owned snapshot; attacker replacements and
sentinels are never deleted. An existing run directory is never replaced, and `complete` is
returned only while the nominal `output_dir` contains the exact validated package.

## Results and failures

The result object contains `run_id`, `verdict`, `export_status`, `output_dir`, and `diagnostics`.
Exit code `0` means both formats were published, independently of a QA verdict of `PASS`, `FAIL`,
or `BLOCKED`. Exit code `2` means invalid or unsafe input/output. Exit code `3` means export was
incomplete, including an unavailable `reportlab==4.4.9` or a write/render failure.

An incomplete export never occupies the complete run path. The exporter removes staging content
and preserves only `diagnostic.json` in an exclusive `<run-id>.partial-<token>/` directory. That
partial directory is diagnostic state, not a report package and must not be treated as complete.
