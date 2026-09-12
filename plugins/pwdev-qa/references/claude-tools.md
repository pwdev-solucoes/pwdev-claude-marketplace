# Claude Code capability mapping

This is a portable contract, not an inventory of the current session. Every candidate must be observed
on the effective Claude Code tool surface before use. Tool names are examples, not a guarantee that a
host exposes them or that a similarly named tool has the required semantics.

## Capability mapping

| capability | candidate mechanisms | fallback | limitation |
|---|---|---|---|
| `read` | `Read`, `Grep`, or `Glob` | Use another observed read-only file facility. | Without one, local contracts and evidence cannot be inspected. |
| `write` | `Write` or `Edit` | Return a proposed change for a human to apply. | Do not claim that a proposed change was written. |
| `execute` | `Bash` | Return the exact proposed command without running it. | Tests and probes remain `NOT_RUN`; command text is not execution evidence. |
| `load_skill` | `Skill` with the installed namespaced skill name | Read the confirmed local skill file through an observed read capability. | If neither route is observed, the skill is unavailable for this session. |

## Observation and diagnostics

Observe every required capability independently in the live session and record the probe result
and evidence. A successful, purpose-matched probe is `available`; an explicit negative probe is
`missing`; a probe not run, an ambiguous response, or a partial prerequisite is `unverified`.
`missing` and `unverified` are limitations, never permission to invent a call or report fictitious
execution.

Emit a diagnostic in this shape for every non-available capability:
`runtime=claude capability=<capability> status=<missing|unverified> evidence=<observation>;
limitation=<impact>; fallback=<safe alternative>`.

A real smoke of all four capabilities must succeed before this runtime is declared verified.
Finding an executable, seeing a tool name, or successfully reading one file is not that smoke.

## Safety boundary

Instructions must remain independent of any exclusive candidate: use only a mechanism actually
observed in this Claude Code session. Do not launch another AI runtime to satisfy a missing Claude
Code capability. The workflow must not install software, must not change personal configuration,
and must not use approval or sandbox bypass flags. When a capability is unavailable, stop that
operation, preserve the diagnostic, and use only the documented fallback.
