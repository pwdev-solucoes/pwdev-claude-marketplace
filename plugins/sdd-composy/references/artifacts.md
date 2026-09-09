# SDD Composy artifact contract

SDD Composy separates human-readable product contracts from machine-operational state. Neither root may silently replace the other.

## Human contract root

Human contracts live under `tasks/prd-<slug>/`:

```text
tasks/
├── index.md
└── prd-<slug>/
    ├── prd.md
    ├── stories.md
    ├── techspec.md
    ├── tasks.md
    ├── task_<n>.md
    ├── qa.md
    ├── codereview.md
    ├── evidence-report.html
    ├── evidence-report.pdf
    └── evidences/
        └── manifest.json
```

`tasks/` is an OKF v0.2 bundle. Its reserved `index.md` declares `okf_version: "0.2"`; reserved `index.md` and `log.md` follow their OKF-specific structures. Every generated non-reserved project Markdown document has parseable frontmatter with a non-empty `type`. It records `generated: { by, at }`, lifecycle metadata, upstream `sources`, and human `verified` events when a gate is approved. Timestamps use ISO 8601 with an explicit UTC offset. Unknown OKF extension fields are permitted and preserved by supported updates.

Downstream documents link stable upstream identifiers rather than duplicating full requirements. Human Markdown owns intent, decisions, narrative acceptance contracts, and approval records.

## Operational root

Operational state lives under `.planning/sdd-composy/`:

```text
.planning/sdd-composy/
├── config.json
├── state.json
├── context/{project,stack,domain,pitfalls}.md
├── context/codebase.json
├── tasks/index.json
├── tasks/<prd-slug>.json
├── trace/events.jsonl
├── trace/trace.json
├── loops/<loop-id>.json
├── fleet/<member-id>.json
├── fleet-results/
├── fleet-logs/
└── reports/
```

Validated mutable JSON owns current workflow and task state. `trace/events.jsonl` is append-only semantic history: append an event only after the represented action succeeds. `trace/trace.json` is a deterministic derived projection, records its source event count, and is never edited directly. Loop and fleet records are durable lifecycle truth independent of terminals or presentation tools.

All supported JSON updates preserve unknown fields. Mutations validate their target schema, write through same-directory temporary files, and atomically replace the destination. Invalid history is reported for explicit recovery and is never silently repaired.

## Synchronization and evidence

When Markdown and JSON disagree, synchronization reports the divergence and exact candidate resolutions before writing. It never silently chooses one representation, infers approval, or overwrites a human contract from operational state.

Acceptance evidence belongs below `tasks/prd-<slug>/evidences/`. Each manifest entry links the applicable requirement, story, scenario, criterion, and test to a confined repository-relative regular-file path and SHA-256 digest. Criterion result and evidence type are distinct fields. Generated reports escape or sanitize untrusted text; manifests cannot inject arbitrary HTML. PDF is optional unless requested, and a requested PDF fails if an expected image is not loaded.
