# Codebase context

The context map is what this plugin knows about the repository before anyone asks it to change
anything. It exists so that a design does not re-derive the architecture every time, a plan names
real paths, and an implementer that sees only its own task still writes code that matches the
code around it.

It is **observation, not decision.** Nothing here chooses an approach, proposes a refactor, or
states what the project should do. Those belong to a spec, behind a gate.

## The four documents

Written under `.planning/power/context/`. Four files rather than one so that a reader can load
what it needs — an implementer wants conventions and stack, a debugger wants pitfalls.

### `project.md`

What this repository is and how it is put together.

```markdown
# Project context
Updated: <ISO date>
Commit: <short sha the map was taken at>

## Purpose
## Architecture          entry points, layers, how a request flows end to end
## Structure             the directories that matter and what lives in each
## Conventions           naming, error handling, logging, imports, formatting
## Commands              install, run, test, lint, build — the real ones, from manifests
## Boundaries            what this repository owns and what it delegates
```

**Commands are read from manifests and config, never guessed.** `npm test` when `package.json`
says so; `pytest -q` when `pyproject.toml` says so. A wrong test command here becomes a plan step
that cannot run.

### `stack.md`

Languages, frameworks, databases, infrastructure and their **observed versions**. Versions come
from lockfiles and manifests, not from what is current upstream — the point is to record what this
repository actually pins.

### `domain.md`

The vocabulary the code uses and the invariants it assumes. If the code says `Beneficiary` and the
team says "patient", record both and note which one the code uses; a plan that invents a third
name produces code nobody can find later. Invariants are the rules the code relies on without
restating: an appointment always belongs to a clinic, a ticket cannot leave a closed state.

Keep it short. Domain vocabulary is worth recording; a data dictionary is not.

### `pitfalls.md`

Risks and failure modes, **each with evidence**: a file and line, a commit, an issue, or a
reproducible command. A pitfall without evidence is a rumour, and a rumour in a context file
outlives the person who guessed it.

Good entries name a trap that has already caught someone: a test suite that must run serially, a
migration that is not reversible, a cache that is not invalidated on write, a rate limit
discovered in production.

## Producing the map

Read-only. Inspect manifests, source layout, tests, configuration and recent Git history. Never
read secrets — see [safety](safety.md).

Prefer dispatching the packaged `mapper` subagent: reading a repository closely consumes far more
context than the map itself is worth carrying in the main conversation. Where no subagent is
available, do it inline and keep it to what the four files need.

Record the commit the map was taken at. That is what makes staleness measurable rather than a
feeling.

## Staleness

The map is a snapshot, and it starts drifting the moment it is written. It is not authoritative
over the code — when the two disagree, **the code is right and the map is stale.** Say so, and
offer to remap rather than reasoning from a document you have just seen contradicted.

Remap when the stack changes, when a new subsystem appears, or after a refactor that moves
boundaries. Do not remap on every command: a map rewritten constantly is a map nobody reads.

## Who reads what

| Consumer | Reads | For |
|---|---|---|
| `power-brainstorm` | `project.md`, `domain.md` | to explore from what is known, and to use the project's own words |
| `power-plan` | `project.md`, `stack.md` | real paths in File Structure, real commands in steps |
| `power-execute` | passes the paths to each implementer | conventions, without pasting them into every brief |
| `power-quick` | `project.md` | to match conventions on a change too small to explore |
| `power-debug` | `pitfalls.md` first | the failure may already be documented |
| `power-verify` | `project.md` | the real test and lint commands to run |

The map informs; it never overrides. Repository governance files and direct user instructions
outrank it, and an approved spec outranks it for the feature it covers.

## Prohibitions

- Never put a secret, credential, token, or connection string in a context file.
- Never record a pitfall you cannot evidence.
- Never let the map state an intention ("we should migrate to X"). Observation only.
- Never treat a stale map as an excuse: verify against the code before acting on it.
