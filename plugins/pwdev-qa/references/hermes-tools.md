# Hermes Agent capability mapping

This is a portable contract, not an inventory of the current session. Every candidate must be observed
on the effective Hermes Agent tool surface before use. Tool names are examples, not a guarantee that
an adapter or toolset exposes them with the required semantics.

## Capability mapping

| capability | candidate mechanisms | fallback | limitation |
|---|---|---|---|
| `read` | `read_file` or `search_files` | Use another observed read-only file facility. | Without one, local contracts and evidence cannot be inspected. |
| `write` | `write_file` or `patch` | Return a proposed change for a human to apply. | Do not claim that a proposed change was written. |
| `execute` | `terminal` | Return the exact proposed command without running it. | Tests and probes remain `NOT_RUN`; command text is not execution evidence. |
| `load_skill` | `skill_view` | Read the confirmed registered skill file through an observed read capability. | If neither route is observed, the skill is unavailable for this session. |

## Registration is not loading

At plugin initialization, the Hermes adapter uses `register_skill` with a `pathlib.Path` for each
installed skill. That operation makes the skill discoverable; `register_skill` does not load its
body into the conversation and does not prove that later retrieval will work.

On-demand loading uses `skill_view` from the observed skills toolset only when the workflow needs
that skill. Probe registration and on-demand loading separately. A successful adapter registration
with a failed or unobserved `skill_view` leaves `load_skill` as `missing` or `unverified`.

## Observation and diagnostics

Observe every required capability independently in the live session and record the probe result
and evidence. A successful, purpose-matched probe is `available`; an explicit negative probe is
`missing`; a probe not run, an ambiguous response, or a partial prerequisite is `unverified`.
`missing` and `unverified` are limitations, never permission to invent a call or report fictitious
execution.

Emit a diagnostic in this shape for every non-available capability:
`runtime=hermes capability=<capability> status=<missing|unverified> evidence=<observation>;
limitation=<impact>; fallback=<safe alternative>`.

A real smoke of all four capabilities must succeed before this runtime is declared verified.
Finding an executable, seeing a registration entry, or successfully reading one file is not that
smoke.

## Safety boundary

Instructions must remain independent of any exclusive candidate: use only a mechanism actually
observed in this Hermes Agent session. Do not launch another AI runtime to satisfy a missing
Hermes capability. The workflow must not install software, must not change personal configuration,
and must not use approval or sandbox bypass flags. When a capability is unavailable, stop that
operation, preserve the diagnostic, and use only the documented fallback.
