---
description: Configure MCP servers in .mcp.json for the detected stack
---

# /setup-mcp — Configure MCP Servers

## Role
Utility agent that configures the `.mcp.json` file in the project root with recommended MCP servers for the detected stack.

## Input
$ARGUMENTS: Optional — comma-separated list of servers to install (e.g., "primevue,context7,github"). If empty, runs interactive mode.

## Procedure

### STEP 1 — Detect Current State
```bash
# Check if .mcp.json already exists
if [ -f ".mcp.json" ]; then
  echo "EXISTING"
else
  echo "NEW"
fi
```

If `.mcp.json` exists → show current servers, ask: "Add servers to existing config or replace?"

### STEP 2 — Detect Stack (silent, ~10s)
```bash
cat package.json 2>/dev/null | head -30
cat composer.json 2>/dev/null | head -30
ls src/ app/ resources/ 2>/dev/null
cat CLAUDE.md .planning/SPEC.md 2>/dev/null | head -50
```

Identify: Vue/React/Angular, Laravel/Express/Django, DB type, etc.

### STEP 3 — Present Server Catalog

Show available servers organized by category. Mark recommended ones based on detected stack.

```
## MCP Server Catalog

### UI Frameworks
| Server | Package | Requires API Key | Recommended |
|--------|---------|:-:|:-:|
| primevue | @primevue/mcp | No | [if Vue detected] |
| shadcn | @anthropic/mcp-server-shadcn-ui | No | [if React detected] |
| chakra-ui | @anthropic/mcp-server-chakra-ui | No | [if React detected] |

### Documentation
| Server | Package | Requires API Key | Recommended |
|--------|---------|:-:|:-:|
| context7 | @upstash/context7-mcp | Yes | Always |

### DevOps & Integrations
| Server | Package | Requires API Key | Recommended |
|--------|---------|:-:|:-:|
| github | @modelcontextprotocol/server-github | Yes (PAT) | Always |
| supabase | @supabase/mcp-server-supabase@latest | Yes | [if Supabase detected] |

### Databases
| Server | Package | Requires API Key | Recommended |
|--------|---------|:-:|:-:|
| postgres | @modelcontextprotocol/server-postgres | Yes (conn string) | [if PG detected] |
| redis | @modelcontextprotocol/server-redis | No | [if Redis detected] |

### Design
| Server | Package | Requires API Key | Recommended |
|--------|---------|:-:|:-:|
| figma | @anthropic/mcp-server-figma | Yes | [if frontend project] |

### AI Providers
| Server | Package | Requires API Key | Recommended |
|--------|---------|:-:|:-:|
| openrouter | @openrouter/mcp-server | Yes | Optional |
| openai | @modelcontextprotocol/server-openai | Yes | Optional |
| google-ai | @anthropic/mcp-server-google-ai | Yes | Optional |
| ollama | @modelcontextprotocol/server-ollama | No (local) | Optional |

### Utilities
| Server | Package | Requires API Key | Recommended |
|--------|---------|:-:|:-:|
| sequential-thinking | @modelcontextprotocol/server-sequential-thinking | No | Always |
| memory | @modelcontextprotocol/server-memory | No | Always |
| fetch | @modelcontextprotocol/server-fetch | No | Always |
| filesystem | @modelcontextprotocol/server-filesystem | No | Optional |
| brave-search | @modelcontextprotocol/server-brave-search | Yes | Optional |
```

### STEP 4 — Selection

**If $ARGUMENTS provided:** use the listed servers directly.
**If interactive:** ask the human to select which servers to configure.

Suggest a sensible default based on detected stack:
- **Always:** context7, github, sequential-thinking, memory, fetch
- **Vue project:** + primevue
- **React project:** + shadcn or chakra-ui
- **Laravel project:** + postgres
- **Frontend project:** + figma

Present selection and await approval.

### STEP 5 — Collect API Keys

For each selected server that requires an API key:
1. Ask the human for the key
2. If human says "skip" or "later" → use placeholder `"<your-KEY_NAME-here>"`
3. NEVER store real keys in files that will be committed

**Important:** Inform the human:
> "API keys will be written to `.mcp.json`. Make sure `.mcp.json` is in your `.gitignore` to avoid committing secrets."

### STEP 6 — Generate .mcp.json

Write `.mcp.json` to the **project root** (not the plugin directory).

Format:
```json
{
  "mcpServers": {
    "server-name": {
      "command": "npx",
      "args": ["-y", "@package/name"],
      "env": {
        "API_KEY": "value-or-placeholder"
      }
    }
  }
}
```

**Server configurations:**

| Server | Command | Args | Env |
|--------|---------|------|-----|
| primevue | npx | ["-y", "@primevue/mcp"] | — |
| context7 | npx | ["-y", "@upstash/context7-mcp"] | CONTEXT7_API_KEY |
| github | npx | ["-y", "@modelcontextprotocol/server-github"] | GITHUB_PERSONAL_ACCESS_TOKEN |
| sequential-thinking | npx | ["-y", "@modelcontextprotocol/server-sequential-thinking"] | — |
| filesystem | npx | ["-y", "@modelcontextprotocol/server-filesystem", "[project-path]"] | — |
| memory | npx | ["-y", "@modelcontextprotocol/server-memory"] | — |
| fetch | npx | ["-y", "@modelcontextprotocol/server-fetch"] | — |
| brave-search | npx | ["-y", "@modelcontextprotocol/server-brave-search"] | BRAVE_API_KEY |
| postgres | npx | ["-y", "@modelcontextprotocol/server-postgres"] | POSTGRES_CONNECTION_STRING |
| redis | npx | ["-y", "@modelcontextprotocol/server-redis", "redis://localhost:6379"] | — |
| supabase | npx | ["-y", "@supabase/mcp-server-supabase@latest", "--access-token", "[token]"] | — |
| shadcn | npx | ["-y", "@anthropic/mcp-server-shadcn-ui"] | — |
| chakra-ui | npx | ["-y", "@anthropic/mcp-server-chakra-ui"] | — |
| figma | npx | ["-y", "@anthropic/mcp-server-figma"] | FIGMA_ACCESS_TOKEN |
| openrouter | npx | ["-y", "@openrouter/mcp-server"] | OPENROUTER_API_KEY |
| openai | npx | ["-y", "@modelcontextprotocol/server-openai"] | OPENAI_API_KEY |
| google-ai | npx | ["-y", "@anthropic/mcp-server-google-ai"] | GOOGLE_AI_API_KEY |
| ollama | npx | ["-y", "@modelcontextprotocol/server-ollama"] | OLLAMA_HOST (default: http://localhost:11434) |

### STEP 7 — Ensure .gitignore

Check if `.mcp.json` is in `.gitignore`. If not, ask the human:
> ".mcp.json contains API keys. Add it to .gitignore? (recommended)"

If approved, append `.mcp.json` to `.gitignore`.

### STEP 8 — Summary

```markdown
## ✅ MCP Servers Configured

**File:** .mcp.json
**Servers:** [N] configured

| Server | Status |
|--------|--------|
| context7 | ✅ Configured |
| github | ⚠️ Placeholder key (update later) |
| primevue | ✅ Ready (no key needed) |

### Servers with placeholder keys:
- `github` → set GITHUB_PERSONAL_ACCESS_TOKEN
- Run `/pwdev-code:setup-mcp` again to update keys

### Next steps:
1. Update placeholder API keys in `.mcp.json`
2. Restart Claude Code to load the new MCP servers
3. Verify with `/pwdev-code:health`
```

## Prohibitions
- ❌ NEVER commit `.mcp.json` with real API keys
- ❌ NEVER overwrite existing `.mcp.json` without confirmation
- ❌ NEVER log or display API key values after writing
- ❌ NEVER read `.env` files
- ❌ NEVER write to the plugin directory — only to the project root
