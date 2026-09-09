---
name: sdd-evidence
description: Build, verify, and optionally export portable SDD evidence manifests.
metadata:
  version: 0.1.0
---

# SDD Evidence

The discovery step uses `sdd_evidence.py discover <root>` to return a deterministic,
read-only inventory of existing task evidence under the confined evidence root before
creating anything. Rebuild a manifest with `sdd_evidence.py build <input.json> <root>
<manifest>`, preserving source files and
recording relative paths, SHA-256 digests, known enums, and sanitized content. Verify it
with `sdd_evidence.py verify <manifest> <root>` before routing a task from `evidence_required` to
`review_required`; the task engine remains the authority and rejects missing, stale, or
unapproved evidence. Use `sdd_evidence.py export <manifest> <root> <output>` for HTML. PDF export is optional: when explicitly
requested it must fail if expected screenshot images cannot load, and may report that no
PDF backend is available.

Never mutate existing evidence while rebuilding. Never infer approval, bypass lifecycle
guards, expose secrets, or use paths outside the task root. Return the shared manifest and
verification result unchanged to the caller.

Do not commit.
