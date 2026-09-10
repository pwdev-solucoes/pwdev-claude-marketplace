---
type: REFERENCE
okf_version: "0.2"
title: Consolidated status
status: DRAFT
source: sdd-composy
verified: 2026-09-09
---

# Consolidated status

`scripts/sdd_status.py ROOT [--feature SLUG] [--tasks] [--fleet] [--json]` is a
read-only projection of configuration, global state, task contracts, trace integrity, loop
records, and fleet records. Read-only means it creates, modifies, or deletes no project file.
It does not invoke a provider; any provider-native logs produced by a separate runtime
operation are outside this command and must be measured separately.

The result has schema `sdd-composy.status`, `read_only: true`, `status`, `next_action`,
`reasons`, and source-by-source `confidence`, `state`, and `value`. `--tasks` adds
`task_summary`, `--fleet` adds `fleet_summary`, `--feature` filters the operational task
bundle, and `--json` emits compact JSON. Operational task authority is the validated
`.planning/sdd-composy/tasks/<prd-slug>.json` object with its nested `tasks` array. Markdown
task files are a legacy/read-only fallback only when that operational directory is absent;
their existence never overrides live JSON or proves approval.

The action is intentionally conservative: malformed sources require manual repair; blocked,
divergent, looping, and fleet states identify the gate that must be handled before normal
execution resumes. Top-level `status` may be `uninitialized`, `active`, `blocked`,
`divergent`, `looping`, `fleet`, or `malformed`. When valid global state exists and no task,
loop, fleet, blocker, or divergence overrides it, the value is the lowercase lifecycle stage,
for example `init`, `map`, `prd`, `stories`, `techspec`, `tasks`, `execute`, `qa`, `evidence`,
`review`, `verify`, or `complete`. Missing optional loop/fleet/trace sources are reported as
low-confidence `missing`, not silently fabricated.

Unsafe symlink sources fail closed. Status never reconciles divergence, migrates fleet members,
repairs trace history, chooses Markdown or JSON authority, or recommends editing `state.json`
to simulate a gate. Use the explicit synchronization or migration operation after reviewing
its diagnostic. The same output contract applies on Claude Code, Codex, and Hermes; it does
not demonstrate real-provider acceptance.
