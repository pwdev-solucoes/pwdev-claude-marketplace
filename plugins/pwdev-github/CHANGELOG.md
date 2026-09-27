# Changelog — pwdev-github

## 0.1.0 — 2026-09-27

First release.

- `/pwdev-github:init`, `/pwdev-github:status` — gh, scopes, default repo and Project.
- `/pwdev-github:project` — GitHub Project from a preset (`roadmap-produto`, `kanban`, `scrum`)
  customized before creation, or copied from a template Project (keeps views).
- `/pwdev-github:publish` — publishes a `pwdev-roadmap/1` roadmap: issues, sub-issues,
  milestones, native blocked-by and Project fields; dry-run first, idempotent and resumable
  through `.planning/github/<slug>.map.json`.
- User stories (US) with acceptance criteria (CA) and business rules (RN) from the roadmap:
  in the feature body (`--stories body`, default) or as sub-issues (`--stories issues`);
  presets gain Tipo=História.
- Skill `github-issues` — create, update, comment, close and reopen issues; sub-issues,
  dependencies and Project fields, including batches, with a preview before every write.
- `scripts/ghp.py` — standard-library wrapper over `gh` for everything above.
- Portable from the start: skills `github-init`, `github-project`, `github-publish`,
  `github-status`, `github-issues`; Claude commands are wrappers; Codex manifest and
  `openai.yaml` per skill; Hermes adapter with a first-turn bootstrap; OpenCode installer that
  links the skills and writes one `/github-<name>` command each.
