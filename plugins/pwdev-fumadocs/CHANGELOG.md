# Changelog — pwdev-fumadocs

## 0.1.0 — 2026-09-28

First release.

- `/pwdev-fumadocs:setup` — new site (`create-fumadocs-app`), existing app (`@fumadocs/cli init`)
  or manual install from the official page; verified by scanner, type-check and build.
- `/pwdev-fumadocs:content` — pages, frontmatter, `meta.json`, groups, root folders, versions,
  i18n files, MDX components and migration from other docs tools.
- `/pwdev-fumadocs:feature` — search, llms.txt, MCP, Ask AI, OG, OpenAPI, i18n, static export,
  theme, layout and components, `@fumadocs/cli feature` first.
- `/pwdev-fumadocs:doctor` — read-only diagnosis, fix after approval, health and upgrades.
- `scripts/fdscan.py` — deterministic read-only project scan with findings `FD001`–`FD013`.
- Official Fumadocs MCP server (`https://www.fumadocs.dev/api/mcp`) in `.mcp.json`; HTTP
  fallback through `/docs/<path>.mdx` and `/llms.txt`.
- Portable from the start: skills `fumadocs-setup`, `fumadocs-content`, `fumadocs-feature`,
  `fumadocs-doctor`; Claude commands are wrappers; Codex manifest and `openai.yaml` per skill;
  Hermes adapter with a first-turn bootstrap; OpenCode installer that links the skills and
  writes one `/fumadocs-<name>` command each.
