# Task synchronization

`sdd_sync.py inspect` compares OKF task Markdown contracts with the JSON task
projection. `plan` is a deterministic, read-only presentation of that report.
Neither command chooses an authority or mutates files. Classifications are the
`CLASSIFICATIONS` tuple of `scripts/sdd_sync.py`: `no_change`, `markdown_only`, `json_only`,
`identity_changed`, `status_divergence`, `malformed_markdown`, and `malformed_json`. A human must
resolve conflicts explicitly using the displayed confirmation token
`CONFIRM-SDD-SYNC`. Unknown JSON fields are never discarded by inspection.

Both paths must be repository-bound; symlinks and external paths are rejected.
