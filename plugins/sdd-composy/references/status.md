---
type: REFERENCE
okf_version: "0.2"
title: Consolidated status
status: DRAFT
source: sdd-composy
verified: 2026-09-09
---

# Consolidated status

`scripts/sdd_status.py` is a read-only projection of configuration, global state,
task contracts, trace integrity, loop records, and fleet records. It never repairs
or writes a source. The result contains `status`, `next_action`, reasons, and a
source-by-source confidence level. The action is intentionally conservative:
malformed sources require manual repair; blocked, divergent, looping, and fleet
states identify the gate that must be handled before normal execution resumes.

Canonical statuses are `uninitialized`, `active`, `blocked`, `divergent`,
`looping`, `fleet`, and `malformed`. Missing optional loop/fleet/trace sources
are reported as low-confidence `missing`, not silently fabricated.
