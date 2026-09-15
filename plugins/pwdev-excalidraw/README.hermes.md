# PWDEV Excalidraw — Hermes Agent

The plugin is compatible with Hermes through the Hermes manifest at
`.hermes-plugin/plugin.yaml`, the bootstrap at `.hermes-plugin/__init__.py`, and
the portable skill at `skills/excalidraw/SKILL.md`.

## MCP setup

Hermes discovers MCP servers from `~/.hermes/config.yaml`. Add the official
remote server under `mcp_servers`:

```yaml
mcp_servers:
  excalidraw:
    url: "https://mcp.excalidraw.com/mcp"
    connect_timeout: 60
    timeout: 120
```

Restart Hermes after changing this configuration. Tools are exposed with names
such as `mcp_excalidraw_read_me` and `mcp_excalidraw_create_view`, depending on
the tools currently published by the server. The skill must inspect the actual
available tools and must not invent tool names.

If the MCP server is not connected, Hermes may provide a planning contract,
ASCII/Mermaid fallback, or a local `.excalidraw` artifact when requested. It must
report the fallback honestly and never claim that a remote diagram was created.
