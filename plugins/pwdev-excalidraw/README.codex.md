# PWDEV Excalidraw — Codex

The plugin is compatible with Codex through the portable Agent Skill at
`skills/excalidraw/SKILL.md` and the Codex manifest at `.codex-plugin/plugin.json`.

## MCP setup

Configure the Excalidraw MCP server in the Codex MCP configuration using the
server's documented transport. For the official remote server, use:

```json
{
  "mcpServers": {
    "excalidraw": {
      "url": "https://mcp.excalidraw.com/mcp"
    }
  }
}
```

Do not put OAuth tokens or credentials in this repository. If the server is not
available, Codex may still use the skill to produce a planning contract, an
ASCII/Mermaid fallback, or a local `.excalidraw` artifact when requested; it must
not pretend that an MCP diagram was created.

## Example

```text
Use the pwdev-excalidraw skill to map this approved implementation plan. Use the
Excalidraw MCP if connected; otherwise explain the fallback and do not change code.
```
