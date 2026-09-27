# PWDEV-GITHUB v0.1.0

*Read this in [Português Brasileiro](./README.pt-BR.md)*

> **GitHub Projects from templates, roadmaps published with their dependency chain, and a skill to run issues day to day — on Claude Code, Codex, Hermes Agent and OpenCode.**

```
roadmap.json (pwdev-roadmap/1) → Project from template → issues + sub-issues + blocked-by → daily issue work
```

## What it does

| Piece | What it does |
|---|---|
| `/pwdev-github:init` | Checks `gh`, auth and the `project` scope; saves the default repo and Project in `.planning/github.json` |
| `/pwdev-github:project [name]` | Creates a Project from a preset (`roadmap-produto`, `kanban`, `scrum`) — shown as a table and customizable (name, owner, visibility, linked repo, fields, options, iterations) before anything is created — or copies a template Project |
| `/pwdev-github:publish <roadmap.json>` | Publishes a roadmap: phases → milestones, epics/features (and optionally tasks) → issues and sub-issues, dependencies → native **blocked by**, Project fields (Type, Priority, Estimate, Phase, Wave). Dry-run first; idempotent and resumable |
| `/pwdev-github:status` | gh, scopes, repo, Project and published roadmaps |
| Skill `github-issues` | "create an issue", "close #12", "move #14 to In progress", "#15 is blocked by #14", "close all done tasks of FT01" — issues, sub-issues, dependencies and Project fields, single or batch |

Works on its own, and as the publishing backend of **pwdev-prd** (`/pwdev-prd:publish <slug>`).

## Setup

1. Install the GitHub CLI: https://cli.github.com/ (tested with gh 2.93).
2. `gh auth login`, then `gh auth refresh -s project` — Projects need the `project` scope,
   issues need `repo`.
3. Python 3 (standard library only) for `scripts/ghp.py`.
4. Install the plugin in your runtime, then run the init skill:

| Runtime | Install | Invoke |
|---|---|---|
| Claude Code | `claude plugin install pwdev-github@pwdev-claude-marketplace` | `/pwdev-github:init`, `/pwdev-github:project`… |
| Codex | add this repository as a marketplace and enable **pwdev-github** (`.agents/plugins/marketplace.json`) | `$github-init`, `$github-project`… |
| Hermes Agent | `hermes plugins install pwdev-solucoes/pwdev-claude-marketplace --enable` (entry point `.hermes-plugin/`) | `skill_view("pwdev-github:github-init")` or just ask |
| OpenCode | `python3 plugins/pwdev-github/.opencode-plugin/install.py [--project <dir>]` | `/github-init`, `/github-project`… or the `skill` tool |

Five portable skills (`skills/github-*`) are the single source of truth: `github-init`,
`github-project`, `github-publish`, `github-status` (each wrapped by a Claude command) and
`github-issues` (triggered by the request). No subagents, no hooks. On Codex, the sandbox must
allow network access for `gh`. Details: [references/runtime.md](./references/runtime.md).

## Mapping a roadmap

| Roadmap | default | task-issues | flat |
|---|---|---|---|
| Phase | milestone | milestone | milestone |
| Epic | issue | issue | — |
| Feature | sub-issue of the epic | sub-issue of the epic | issue |
| Task | checklist in the feature | sub-issue of the feature | checklist |
| Dependency | blocked-by | blocked-by | blocked-by |
| User story | in the feature body (`--stories body`, default) or sub-issue of the feature (`--stories issues`) | same | same |

Details: [references/roadmap-contract.md](./references/roadmap-contract.md) ·
presets and spec format: [references/project-templates.md](./references/project-templates.md) ·
gh recipes: [references/gh-recipes.md](./references/gh-recipes.md).

## Limits

- The GitHub API cannot create Project **views**; `project` prints the suggested views as a
  checklist. Copying a template Project is the way to reuse views.
- Where native dependencies are unavailable (404/422, e.g. GitHub Enterprise Server without the
  feature), publish falls back to a "Blocked by #N" comment and reports it.
- Publish never closes or deletes issues that left the roadmap; it lists them as orphans.

## Security

- Every write (Project, labels, milestones, issues, links, fields) is preceded by a preview or
  dry-run and needs an explicit yes.
- Nothing is deleted: no `issue delete`, `project delete` or `item-delete` unless you ask for a
  deletion by name.
- Authentication is the `gh` token only; the plugin stores no credentials.
  `.planning/github/*.map.json` holds issue numbers and ids, not secrets.
- Issue bodies embed the roadmap's feature files — keep secrets out of the roadmap.

## License

Apache-2.0 — see [LICENSE](./LICENSE)
