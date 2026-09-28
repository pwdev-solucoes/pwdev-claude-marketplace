# PWDEV-FUMADOCS v0.1.0

*Read this in [Português Brasileiro](./README.pt-BR.md)*

> **Build [Fumadocs](https://www.fumadocs.dev) documentation sites from the live official docs — setup, content, features and diagnosis, verified by type-check and build, on Claude Code, Codex, Hermes Agent and OpenCode.**

```
fdscan (project facts) → official page (MCP / .mdx) → @fumadocs/cli or manual edit → scan + type-check + build
```

Fumadocs moves fast (Macro API, Next.js 16 `proxy.ts`, Tailwind 4, Base UI by default). The
plugin never writes Fumadocs API code from memory: every change follows the official page read
in the same session, through the official Fumadocs MCP server or the `.mdx` Markdown of each page.

## What it does

| Piece | What it does |
|---|---|
| `/pwdev-fumadocs:setup` | New site with `create-fumadocs-app`, Fumadocs added to an existing Next.js / React Router / TanStack Start / Waku app with `@fumadocs/cli init`, or a manual install (Astro, other content sources) page by page |
| `/pwdev-fumadocs:content` | Pages, frontmatter, `meta.json`, folder groups, root folders (tabs), versions, i18n files, MDX components; migration from Docusaurus / Nextra / Mintlify |
| `/pwdev-fumadocs:feature` | Search providers, `llms.txt` + Markdown per page, docs MCP server, Ask AI, OG images, OpenAPI / AsyncAPI / GraphQL, i18n, static export, theme, custom layout, components — `@fumadocs/cli feature` first, the official page otherwise |
| `/pwdev-fumadocs:doctor` | Read-only diagnosis (scanner, versions, type-check, build, pitfall catalog, official docs) and a fix applied only after approval; also health/status and upgrades |
| `scripts/fdscan.py` | Deterministic, read-only project scan: framework, package manager, Fumadocs packages, content source (Macro / Config API), `baseUrl`, content dirs, wired features and known pitfalls (`FD001`–`FD013`). JSON or text |
| MCP `fumadocs` | Official server at `https://www.fumadocs.dev/api/mcp` (`search`, `get_page`, `list_pages`, `ask-ai`) — no authentication |

## Setup

1. Node.js 22+ and a package manager (npm, pnpm, yarn or bun) for the Fumadocs project.
2. Python 3 (standard library only) for `scripts/fdscan.py`.
3. Network access to `www.fumadocs.dev` (docs) and the npm registry (`npx`).
4. Install the plugin in your runtime:

| Runtime | Install | Invoke | Fumadocs MCP |
|---|---|---|---|
| Claude Code | `claude plugin install pwdev-fumadocs@pwdev-claude-marketplace` | `/pwdev-fumadocs:setup`, `:content`, `:feature`, `:doctor` | automatic (`.mcp.json`) |
| Codex | add this repository as a marketplace and enable **pwdev-fumadocs** (`.agents/plugins/marketplace.json`) | `$fumadocs-setup`… | `codex mcp add fumadocs --url https://www.fumadocs.dev/api/mcp` |
| Hermes Agent | `hermes plugins install pwdev-solucoes/pwdev-claude-marketplace --enable` (entry point `.hermes-plugin/`) | `skill_view("pwdev-fumadocs:fumadocs-setup")` or just ask | `mcp_servers: { fumadocs: { url: "https://www.fumadocs.dev/api/mcp" } }` in `~/.hermes/config.yaml` |
| OpenCode | `python3 plugins/pwdev-fumadocs/.opencode-plugin/install.py [--project <dir>]` | `/fumadocs-setup`… or the `skill` tool | `"mcp": { "fumadocs": { "type": "remote", "url": "https://www.fumadocs.dev/api/mcp" } }` in `opencode.json` |

Without the MCP server the skills read the same pages over HTTP
(`https://www.fumadocs.dev/docs/<path>.mdx`, index at `/llms.txt`). Four portable skills
(`skills/fumadocs-*`) are the single source of truth, each wrapped by a Claude command. No
subagents, no hooks. Details: [references/runtime.md](./references/runtime.md).

## References

- [docs-access.md](./references/docs-access.md) — how to read the live docs; page map by topic.
- [frameworks.md](./references/frameworks.md) — where each piece lives per framework.
- [features.md](./references/features.md) — feature → CLI command → page.
- [pitfalls.md](./references/pitfalls.md) — scanner findings and runtime symptoms with fixes.

Verified on 2026-09-28 against `create-fumadocs-app` templates (fumadocs-core 16.15,
fumadocs-mdx 15.4, `@fumadocs/cli` 1.7): Next.js template built, `feature mcp` added a working
`/api/mcp`.

## Security

- Installing packages, running a generator (`create-fumadocs-app`, `@fumadocs/cli`) and
  overwriting files need an explicit yes; the command and the affected files are shown first.
  Generators never get `--yes` on an existing project without authorization.
- `fdscan.py` only reads files (it skips `node_modules`, build output and dot-directories) and
  runs `node --version`; it writes nothing.
- API keys for search or AI providers go to untracked env files (`.env.local`), never into
  versioned files.
- The Fumadocs MCP server is a public, read-only documentation service; no credentials are sent.

## License

Apache-2.0 — see [LICENSE](./LICENSE)
