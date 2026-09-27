# Changelog — pwdev-prd

## 3.0.0 — 2026-09-27

### Added
- User stories, acceptance criteria (CA) and business rules (RN) per feature:
  `references/user-stories.md` (adapted from pwdev-code `skill-user-stories`: canonical format,
  INVEST, Gherkin CA with happy/error paths, Definition of Ready, anti-patterns, review
  checklist, plus RN); PRD `### Business Rules` section (`RN-xx`, interview step 5, `prd.json`
  `business_rules`); `roadmap.json` optional `rules[]` and `stories[]`; the roadmap writer drafts
  1–3 stories per feature; new `prd-stories` skill and `/pwdev-prd:stories` command evolve one
  feature at a time up to `ready`; `roadmap-check.py` enforces the standard and generates
  `STORIES.md` and `stories/US-NN-*.md`; `prd-list` shows stories ready/total; `prd-publish`
  asks before publishing drafts.
- Portable skills `skills/prd-*` (init, create, refine, list, export, roadmap, stories, publish, audit) —
  the single source of truth for every runtime.
- Codex: `.codex-plugin/plugin.json` and `skills/*/agents/openai.yaml`.
- Hermes Agent: `.hermes-plugin/` registering the skills as `Path` objects with a short
  first-turn bootstrap.
- OpenCode: `.opencode-plugin/install.py` links the skills and writes one `/prd-<name>` command
  per Claude command (`--project`, `--force`, `--uninstall`, `--dry-run`).
- `references/runtime.md` and one tool map per runtime; `references/roadmap-agent.md` is the
  roadmap writer's contract for every runtime and for the inline fallback.

### Changed
- Claude commands are thin wrappers over the skills; `agents/roadmap.md` reads the shared
  contract.
- Skills use `<plugin-root>/...` paths and `sh .../audit-log.sh`, never `${CLAUDE_PLUGIN_ROOT}`.

## 2.1.0 — 2026-09-27

### Added
- `/pwdev-prd:roadmap {slug}` — approved PRD → Phase/Epic/Feature/Task roadmap with an
  explicit dependency chain, written by the new `roadmap` subagent (`model: inherit`).
- `scripts/roadmap-check.py` — deterministic validator (IDs, hierarchy, traceability,
  cycles, dangling edges, split limits) that generates `DEPENDENCIES.md` (Mermaid graph,
  waves, critical path).
- `references/roadmap-format.md` — the `pwdev-roadmap/1` contract shared with pwdev-github.
- `/pwdev-prd:publish {slug}` — hands an approved roadmap to `/pwdev-github:publish`.

### Changed
- PRD header has `Status: DRAFT | APPROVED`; `create` ends with an approval gate.
- Requirement IDs `FR-xx` / `NFR-xx` / `AC-xx` are mandatory and stable across refinements.
- Priority is MoSCoW (`must|should|could|wont`) in both the template and `prd.json`.
- `refine` bumps `Version`, appends to `### Change Log`, and re-opens approval.
- `export --github`: preflight (gh, auth, repo, labels, body size) and a preview before
  creating the issue; uses `--body-file`.
- `list` shows status, version, roadmap state and the GitHub Project URL.
- Audit docs name the real subagent (`pwdev-prd:roadmap`) instead of a non-existent executor.
