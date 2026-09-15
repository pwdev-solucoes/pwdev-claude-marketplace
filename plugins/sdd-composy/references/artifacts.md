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
    ├── task-<id>.md
    ├── qa.md
    ├── codereview.md
    ├── evidence-report.html
    ├── evidence-report.pdf   (optional, on request)
    └── evidences/
        └── manifest.json
```

`tasks/` is an OKF v0.2 bundle: reserved `index.md` and `log.md` follow their OKF-specific structures, and every generated non-reserved document carries the frontmatter defined in [okf.md](okf.md). Unknown OKF extension fields are permitted and preserved by supported updates.

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
└── fleet/<fleet-id>/
    ├── members/<task-id>.json
    └── docker-compose.yml   (only with --compose)
```

Validated mutable JSON owns current workflow and task state; the trace files follow [trace.md](trace.md). Loop and fleet records are durable lifecycle truth independent of terminals or presentation tools. All supported JSON updates preserve unknown fields, validate their target schema, and write atomically ([safety.md](safety.md), "Mutation integrity"). Invalid history is reported for explicit recovery and is never silently repaired.

## Synchronization and evidence

When Markdown and JSON disagree, synchronization follows [synchronization.md](synchronization.md): it reports the divergence before writing and never silently chooses one representation.

Acceptance evidence belongs below `tasks/prd-<slug>/evidences/`. Each manifest entry links the applicable requirement, story, scenario, criterion, and test to a confined repository-relative regular-file path and SHA-256 digest. Criterion result and evidence type are distinct fields. Generated reports escape or sanitize untrusted text; manifests cannot inject arbitrary HTML. PDF is optional unless requested, and a requested PDF fails if an expected image is not loaded.
