---
description: Configure project infrastructure — MCP servers, stack detection, and general setup tasks
argument-hint: "[mcp | stack] (default: interactive)"
---

# /pwdev-code:setup — Project Setup

## Role
Multi-purpose setup utility. Routes to the appropriate setup flow based on $ARGUMENTS.

## Input
$ARGUMENTS: subcommand — `mcp`, `stack`, or empty (interactive menu).

## Procedure

### STEP 0 — Language Selection
Read `.planning/config.json` for the `lang` field (`pt-BR` or `en`).
If set → use it silently. If not set → detect from $ARGUMENTS or ask:
"Em qual idioma deseja seguir? / Which language would you like to use? 1. Portugues (PT-BR) 2. English (EN)"
Save choice to `.planning/config.json` (merge, do not overwrite other fields).
All subsequent output follows the resolved language. Technical terms stay in English.

### STEP 1 — Route Subcommand

Parse the first word of $ARGUMENTS:

- **`mcp`** → go to STEP 2 (MCP Server Configuration)
- **`stack`** → go to STEP 3 (Stack Detection & Config)
- **empty or other** → present interactive menu:

  **PT-BR:**
  ```
  O que deseja configurar?

  1. mcp    — Configurar servidores MCP (.mcp.json)
  2. stack  — Detectar e configurar a stack do projeto

  Escolha (1-2):
  ```

  **EN:**
  ```
  What would you like to set up?

  1. mcp    — Configure MCP servers (.mcp.json)
  2. stack  — Detect and configure project stack

  Choose (1-2):
  ```

---

## STEP 2 — MCP Server Configuration

> Previously `/pwdev-code:setup-mcp`. Full MCP setup flow.

### STEP 2.1 — Detect Current State
```bash
if [ -f ".mcp.json" ]; then
  echo "EXISTING"
else
  echo "NEW"
fi
```

If `.mcp.json` exists → show current servers, ask: "Add servers to existing config or replace?"

### STEP 2.2 — Detect Stack (silent, ~10s)
```bash
cat package.json 2>/dev/null | head -30
cat composer.json 2>/dev/null | head -30
ls src/ app/ resources/ 2>/dev/null
cat CLAUDE.md .planning/phases/{active-phase-slug}/spec.md 2>/dev/null | head -50
```

### STEP 2.3 — Present Server Catalog

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

### STEP 2.4 — Selection

**If $ARGUMENTS has server names (e.g., `mcp primevue,context7`):** use them directly.
**If interactive:** ask the human to select which servers to configure.

Suggest a sensible default based on detected stack:
- **Always:** context7, github, sequential-thinking, memory, fetch
- **Vue project:** + primevue
- **React project:** + shadcn or chakra-ui
- **Laravel project:** + postgres
- **Frontend project:** + figma

Present selection and await approval.

### STEP 2.5 — Collect API Keys

For each selected server that requires an API key:
1. Ask the human for the key
2. If human says "skip" or "later" → use placeholder `"<your-KEY_NAME-here>"`
3. NEVER store real keys in files that will be committed

**Important:** Inform the human:
> "API keys will be written to `.mcp.json`. Make sure `.mcp.json` is in your `.gitignore` to avoid committing secrets."

### STEP 2.6 — Generate .mcp.json

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

### STEP 2.7 — Ensure .gitignore

Check if `.mcp.json` is in `.gitignore`. If not, ask the human:
> ".mcp.json contains API keys. Add it to .gitignore? (recommended)"

If approved, append `.mcp.json` to `.gitignore`.

### STEP 2.8 — Summary

```markdown
## MCP Servers Configured

**File:** .mcp.json
**Servers:** [N] configured

| Server | Status |
|--------|--------|
| context7 | Configured |
| github | Placeholder key (update later) |
| primevue | Ready (no key needed) |

### Next steps:
1. Update placeholder API keys in `.mcp.json`
2. Restart Claude Code to load the new MCP servers
3. Verify with `/pwdev-code:health`
```

---

## STEP 3 — Stack Detection & Config

### STEP 3.1 — Detect Stack
```bash
cat package.json 2>/dev/null | head -40
cat composer.json 2>/dev/null | head -40
cat requirements.txt 2>/dev/null | head -20
cat go.mod 2>/dev/null | head -10
ls artisan nuxt.config.* next.config.* vite.config.* 2>/dev/null
```

### STEP 3.2 — Present Findings

Show detected stack and ask the human to confirm or adjust.

### STEP 3.3 — Save to config

Update `.planning/config.json` with detected stack info (merge, do not overwrite).

---

## Prohibitions
- NEVER commit `.mcp.json` with real API keys
- NEVER overwrite existing `.mcp.json` without confirmation
- NEVER log or display API key values after writing
- NEVER read `.env` files
- NEVER write to the plugin directory — only to the project root
