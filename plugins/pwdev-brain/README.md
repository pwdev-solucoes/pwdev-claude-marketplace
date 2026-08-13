# PWDEV Brain — Second Brain as an LLM Wiki (OKF)

> [Versão em português](./README.pt-BR.md)

Claude Code plugin that maintains a **persistent second brain**: an LLM Wiki
in Markdown following [Karpathy's pattern](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f)
kept as an [Open Knowledge Format v0.2](https://github.com/GoogleCloudPlatform/knowledge-catalog/blob/main/okf/SPEC.md)
bundle. Instead of rebuilding knowledge from raw documents on every
question, sources are read once, discussed, and integrated into a wiki that
accumulates value — every claim cited, every change logged.

```
raw/  ──INGEST──▶  wiki/ (OKF v0.2)  ──QUERY──▶  cited answers
(immutable         │ index.md · log.md            + durable syntheses
 sources)          │ concept docs                 ──▶ wiki/output/
                   └──LINT──▶ compliance report        YYYY-MM-DD-<slug>/
```

## What's inside

| Piece | Purpose |
|---|---|
| `/pwdev-brain:init` | Guided setup: brain path (global or per-project), OKF scaffold (`raw/`, `wiki/index.md`, `wiki/log.md`, `wiki/output/`, `AGENTS.md`), user identity for `human:<id>`, preferences |
| `/pwdev-brain:status` | Read-only health: index validity, concept counts by `status`, latest log entries |
| `/pwdev-brain:ingest` | INGEST: source into `raw/` (file or URL), `brain-ingestor` subagent extracts a proposal, points are **discussed with you** before anything is written, then applied with citations, links, index and log |
| `/pwdev-brain:query` | QUERY: index-driven navigation, synthesis with per-claim citations, durable answers become draft concepts, deliverables go to `wiki/output/YYYY-MM-DD-<slug>/` |
| `/pwdev-brain:lint` | LINT: `brain-linter` subagent validates the BR-001…BR-306 rule catalog; always reports, fixes only what you approve |
| Skill `brain` | Routes natural-language intents ("add this to my brain", "what does my wiki say about X") to the right operation |
| MCP server `brain` | Embedded, **read-only**, zero-dependency Node stdio server — 6 tools: `brain_info`, `brain_index`, `brain_list`, `brain_search` (ranked, accent-insensitive, with snippets), `brain_get`, `brain_log`. Works in Claude Code and any MCP client |
| `references/okf-spec.md` | Single source of truth for the format, loaded by every writer |
| 2 subagents | `brain-ingestor` (extract/apply) and `brain-linter` (report/fix) — heavy reading stays out of the main context |

## Requirements

- Node.js 18+ **only for the MCP server** — without it everything degrades
  gracefully to the filesystem flow. No API keys, no npm install.
- A directory for the brain (created by `init` if missing).

## Setup

Run `/pwdev-brain:init` and follow the steps. It results in:

- a brain directory (e.g. `~/brain`) with `raw/`, `wiki/` and `AGENTS.md`;
- `.claude/pwdev-brain-context.md` in the project recording language, brain
  path, your OKF actor id (`human:<id>`) and ingestion preferences.

Then feed it: `/pwdev-brain:ingest <file-or-URL>` and ask:
`/pwdev-brain:query <question>`.

In Claude Code the MCP server finds the brain through the project's context
file — no configuration needed. Restart the session after installing the
plugin so the server connects; confirm with `/mcp` and `/pwdev-brain:status`.

## Using with other MCP clients

The server is a plain Node script — any MCP client can run it. For Claude
Desktop, add to `claude_desktop_config.json` (the env var replaces the
project context file):

```json
{
  "mcpServers": {
    "brain": {
      "command": "node",
      "args": ["/absolute/path/to/plugins/pwdev-brain/server/index.mjs"],
      "env": { "PWDEV_BRAIN_PATH": "/absolute/path/to/your/brain" }
    }
  }
}
```

Every tool also accepts an optional `brain_path` argument, which overrides
both the env var and the context file (useful for multiple brains).

## Guarantees

- `raw/` is never modified — it is the immutable source of truth.
- Nothing enters `wiki/` without discussion: the ingestor writes a proposal,
  you approve/edit/discard each point, only then it applies.
- Every claim carries a footnote resolving to a `sources[].id` entry.
- `wiki/log.md` is append-only; history is never rewritten.
- Lint never auto-resolves contradictions or staleness — those become
  recommendations.
- The MCP server is read-only by construction: no tool writes, `wiki/output/`
  is never served, paths are realpath-checked against the brain root, and
  only text files are readable.

## Troubleshooting

| Symptom | Cause / fix |
|---|---|
| Command aborts pointing to `/pwdev-brain:init` | Missing `.claude/pwdev-brain-context.md` or invalid `wiki/index.md` — run init |
| `status` shows `okf_version ⚠` | Root index frontmatter drifted — run `/pwdev-brain:lint` (BR-003) |
| Ingest wrote nothing after discussion | All points were discarded, or the handoff `## Decisões` section was left empty — re-run the apply step after recording decisions |
| Artifacts loose in `wiki/` | Generated files outside `wiki/output/YYYY-MM-DD-<slug>/` — `/pwdev-brain:lint` flags (BR-006) and moves them on approval |
| MCP tools failing with a valid brain | Session started before the plugin/env var, or Node missing — restart the session; the plugin keeps working via filesystem meanwhile |
| Tool answers "Brain não configurado" | No `brain_path` argument, no `PWDEV_BRAIN_PATH`, and no project context file — run `/pwdev-brain:init` or set the env var |
