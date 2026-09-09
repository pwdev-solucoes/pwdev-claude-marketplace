# Evidence manifest and report

Evidence is criterion-linked and fail-closed. `path` is a repository-relative path beneath the evidence root; parent traversal, absolute paths, backslashes, symlinks, missing files, unknown `result`/`evidence_type` values, and hash mismatches are rejected. Results and evidence types are separate fields. SHA-256 is computed from the exact bytes. HTML report values are escaped before rendering. PDF export is optional; a requested export fails if expected screenshot files cannot be loaded or no verified PDF backend is available.
