# Task synchronization

`sdd_sync.py inspect` compares OKF task Markdown contracts with the JSON task
projection. `plan` is a deterministic, read-only presentation of that report.
Neither command chooses an authority or mutates files. Classifications are
`no_change`, `markdown_only`, `json_only`, `identity_changed`, and
`status_divergence`; malformed inputs are reported as errors. A human must
resolve conflicts explicitly using the displayed confirmation token
`CONFIRM-SDD-SYNC`. Unknown JSON fields are never discarded by inspection.

Both paths must be repository-bound; symlinks and external paths are rejected.
