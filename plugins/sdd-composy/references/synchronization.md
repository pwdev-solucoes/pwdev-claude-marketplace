# Task synchronization

`sdd_sync.py inspect` compares OKF task Markdown contracts with the JSON task
projection. `plan` is a deterministic, read-only presentation of that report.
Neither command chooses an authority or mutates files. Classifications are the
`CLASSIFICATIONS` tuple of `scripts/sdd_sync.py`: `no_change`, `markdown_only`, `json_only`,
`identity_changed`, `status_divergence`, `malformed_markdown`, and `malformed_json`. A human must
resolve conflicts explicitly using the plan's confirmation token `CONFIRM-SDD-SYNC-<digest>`,
which is bound to the input fingerprints the plan was built from. With Markdown authority the
merged projection is validated before it is written and lifecycle state is never taken from
Markdown; state moves only through `sdd_tasks.py transition`. The default repository root is
the grandparent of `tasks/prd-<slug>/`. Unknown JSON fields are never discarded by inspection.

Both paths must be repository-bound; symlinks and external paths are rejected.
