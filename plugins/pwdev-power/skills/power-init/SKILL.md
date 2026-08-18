---
name: power-init
description: Use when a repository has no PWDEV Power workspace yet, when resuming work in one, or when the human asks to initialize, configure, or check the Power setup
---

# Initialize a Power Workspace

Read [artifacts](../../references/artifacts.md), [runtime](../../references/runtime.md), and
[safety](../../references/safety.md) before acting.

## Route

- no argument: initialize, or report and resume if already initialized
- `--check`: report the runtime surface only, change nothing

## Step 1 — Detect before you ask

Never ask the human something the repository already answers.

1. Is `.planning/power/config.json` present? If yes, this is a resume: read it, read
   `state.md`, report the active feature and the exact next valid action, and stop. Do not
   re-initialize, and do not overwrite an existing config.
2. Is this a Git repository with a named branch? If not, say so and stop — every later phase
   binds to a branch.
3. Greenfield or brownfield? Brownfield is anything with source files already committed.
4. Detect the stack from manifests, not from folder names: `package.json`, `pyproject.toml`,
   `go.mod`, `Cargo.toml`, `composer.json`, `pom.xml`, `Gemfile`. Read the actual test and
   lint commands out of them.

## Step 2 — Runtime surface

Report what is available, in one line each. Do not install anything, and do not edit any
configuration outside the repository.

| Check | Command | If missing |
|---|---|---|
| Runtime | your own tool surface | — |
| cmux binary and socket | `cmux ping` | fleet is unavailable; everything else works |
| Hermes CLI | `hermes --version` | the Kanban bridge is unavailable |
| cmux↔Hermes hooks | `cmux hooks hermes-agent` | print `cmux hooks hermes-agent install` and let the human run it |
| `jq`, `sqlite3` | `command -v` | audit stays off; note it |

Missing tools are facts to report, not errors to fix. Only the fleet requires cmux.

## Step 3 — Ask what cannot be detected

At most one round, at most three questions, one at a time:

1. Language for conversation and artifacts (default: the repository's existing language).
2. Model profile: `economy`, `balanced`, `performance` (default: `balanced`).
3. Audit trail on? (default: off).

## Step 4 — Write

Create `.planning/power/` with `config.json` and `state.md` exactly as
[artifacts](../../references/artifacts.md) specifies. If audit was enabled, create the
database file — the audit scripts refuse to write into a database that does not exist, so
creating it is the act that turns auditing on.

Add `.planning/power/audit/` and `.planning/power/fleet-logs/` to the repository's
`.gitignore` if one exists. Everything else under `.planning/power/` is a contract and belongs
in version control.

## Step 5 — Governance file, only if asked

Offer to generate `CLAUDE.md` (and `AGENTS.md` for Codex and Hermes) from
`templates/CLAUDE.template.md`, filled with what you detected. If one already exists, show
what you would change and ask before touching it. Never silently overwrite a governance file.

## Report

State the workspace path, the detected stack with its real test and lint commands, the runtime
surface with anything missing, and the next action: `product` for a new product, `plan` for a
feature, `quick` for a small change.
