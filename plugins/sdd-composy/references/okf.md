# OKF v0.2

## Generated document frontmatter

Every generated human contract (PRD, stories, TechSpec, tasks, QA, review, verdict, quick) is an
OKF v0.2 concept with a non-empty `type`; `sources` listing only the upstream resources actually
consumed (each with `resource`); the generating actor and timestamp under `generated.by` /
`generated.at`; `lifecycle.status`; exactly one `human_approval` field; and `verified` events only
for an actual human gate, with the human actor in `by` and the timestamp in `at`. Timestamps use
ISO 8601 with an explicit UTC offset; actors follow the configured `provider:name` contract.
Unused optional source entries are removed when rendering. The lifecycle vocabulary is defined in
[workflow.md](workflow.md).

## Bundle rules

Project Markdown documents use UTF-8 YAML frontmatter with a non-empty `type`.
`generated.by`, `generated.at`, and `verified[].by`/`verified[].at` are checked
when present (and compare consistently to the configured actor); `sources` entries require a
`resource` when supplied. Unknown extension fields are preserved. The root
`index.md` is reserved for `type: Index` and `okf_version: "0.2"`; `log.md` is
an opaque reserved operational log, exempt from frontmatter and Markdown-link
validation, and is not treated as a concept. Lint reports broken relative Markdown
links as warnings (exit success); malformed metadata and missing required fields
fail. Optional metadata is never invented.

The bundled parser intentionally supports a strict portable YAML subset: UTF-8
frontmatter, scalar values (including quoted values and colons), inline arrays,
and mappings/lists nested by indentation. Unsupported YAML constructs (block
scalars, anchors, tags, and malformed lines) are rejected rather than silently
discarded. JSON is not claimed or accepted as a separate frontmatter format.
