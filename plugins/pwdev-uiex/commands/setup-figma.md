---
name: setup-figma
description: >
  Verify, install, and configure the Figma MCP server for Claude Code.
  Guides the user through connecting their Figma account step-by-step.
argument-hint: "[check | install | connect]"
---

# /pwdev-uiex:setup-figma — Figma Integration Setup

**Argument**: $ARGUMENTS (optional — `check`, `install`, or `connect`)

## STEP 1 — Check Current Status

Verify if Figma MCP is already configured:

```bash
# Check if Figma MCP is available by looking at settings
cat .claude/settings.json 2>/dev/null | grep -i figma
cat .mcp.json 2>/dev/null | grep -i figma

# Check Claude Code global settings
cat ~/.claude/settings.json 2>/dev/null | grep -i figma
```

Attempt to call the Figma MCP to confirm it's functional:

```
Try: mcp:figma → whoami
```

### Report status:

**If Figma MCP responds:**
```
✅ Figma MCP: Connected
   Account: [user info from whoami]
   Status: Ready to use

Available capabilities:
  READ:  get_design_context, get_screenshot, get_metadata, get_variable_defs
  WRITE: use_figma (create/edit nodes), create_new_file, generate_diagram
  SYNC:  search_design_system, code_connect mappings

→ You're all set! Use /pwdev-uiex:start to begin developing.
```

**If $ARGUMENTS is `check`: stop here.**

---

## STEP 2 — Installation Guide

**If Figma MCP is NOT configured, present the installation guide:**

```
⚠️ Figma MCP: Not configured

The Figma MCP server enables bidirectional design integration:
  • Read designs from Figma → extract tokens, components, specs
  • Write designs to Figma → push components, screens, design systems
  • Sync Code Connect → map Figma components to code components

## How to Install

### Option A: Claude Code Built-in (Recommended)

The Figma MCP server is an official Anthropic integration.
In Claude Code, go to:

  Settings → MCP Servers → Add → Search "Figma"

Or add manually to your MCP config:

### Option B: Manual Configuration

Add to your `.mcp.json` (project-level) or `~/.claude/settings.json` (global):
```

Present the configuration:

```json
{
  "mcpServers": {
    "figma": {
      "command": "npx",
      "args": ["-y", "@anthropic/mcp-server-figma"],
      "env": {
        "FIGMA_ACCESS_TOKEN": "<your-figma-access-token>"
      }
    }
  }
}
```

---

## STEP 3 — Connect to Figma (Step-by-Step)

Present the connection guide:

```
## Connecting to Figma — Step by Step

### 1. Get your Figma Access Token

   a. Open Figma in your browser → https://www.figma.com
   b. Click your profile icon (top-right) → "Settings"
   c. Scroll down to "Personal access tokens"
   d. Click "Generate new token"
   e. Give it a name (e.g., "Claude Code")
   f. Set expiration (recommended: 90 days)
   g. Copy the token — you won't see it again!

   ⚠️ Keep this token secret. Never commit it to git.

### 2. Configure the token

   Choose ONE of these methods:
```

**Method 1 — Project-level `.mcp.json` (recommended):**

Ask the user for their token, then write `.mcp.json`:

```json
{
  "mcpServers": {
    "figma": {
      "command": "npx",
      "args": ["-y", "@anthropic/mcp-server-figma"],
      "env": {
        "FIGMA_ACCESS_TOKEN": "[token provided by user]"
      }
    }
  }
}
```

Ensure `.mcp.json` is in `.gitignore`:
```bash
grep -q ".mcp.json" .gitignore 2>/dev/null || echo ".mcp.json" >> .gitignore
```

**Method 2 — Environment variable:**
```
   Set FIGMA_ACCESS_TOKEN in your shell profile:

   # Add to ~/.bashrc or ~/.zshrc:
   export FIGMA_ACCESS_TOKEN="your-token-here"

   Then restart Claude Code.
```

```
### 3. Restart Claude Code

   After configuring the token, restart Claude Code to load the MCP server.

### 4. Verify the connection

   Run: /pwdev-uiex:setup-figma check

   Expected output:
   ✅ Figma MCP: Connected
   Account: [your-email@example.com]
```

---

## STEP 4 — Verify Write Capabilities

After successful connection, verify write access:

```
## Figma Integration Capabilities

### Reading (Figma → Code)
  ✅ get_design_context  — Extract design structure, code hints
  ✅ get_screenshot      — Capture visual snapshots
  ✅ get_metadata        — File structure and metadata
  ✅ get_variable_defs   — Design tokens and variables
  ✅ search_design_system — Query design system components

### Writing (Code → Figma)
  ✅ use_figma           — Create/edit nodes, components, auto-layout
  ✅ create_new_file     — Create new Figma or FigJam files
  ✅ generate_diagram    — Create diagrams in FigJam

### Skills Available
  /figma:figma-use              — Required before every use_figma call
  /figma:figma-generate-design  — Push screens/pages to Figma
  /figma:figma-generate-library — Build design systems in Figma
  /figma:figma-implement-design — Translate Figma → production code

### pwdev-uiex Commands Using Figma
  /pwdev-uiex:push-to-figma     — Push implemented components to Figma
  /pwdev-uiex:analyze [url]     — Read and analyze Figma designs
  /pwdev-uiex:start             — Full workflow with Figma integration
```

---

## STEP 5 — Summary

```
✅ Figma Setup Complete

Connection: [CONNECTED / NOT CONFIGURED]
Token: [configured in .mcp.json / environment / not set]
.gitignore: [.mcp.json protected / needs update]

Read capabilities: [available / not available]
Write capabilities: [available / not available]

Next steps:
  /pwdev-uiex:start "task"          — Start UI development with Figma
  /pwdev-uiex:push-to-figma         — Push existing components to Figma
  /pwdev-uiex:analyze [figma-url]   — Analyze a Figma design
```

## Prohibitions

- NEVER log or display the Figma access token after writing it
- NEVER commit `.mcp.json` with real tokens
- NEVER skip the `.gitignore` check
- NEVER proceed with write operations if `whoami` fails
