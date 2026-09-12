# PWDEV Excalidraw — Visual Planning

> [Versão em Português](./README.pt-BR.md)

Claude Code plugin for planning with editable Excalidraw diagrams through the official Excalidraw MCP server.

## What's inside

| Piece | Purpose |
|---|---|
| MCP `excalidraw` | Official remote server at `https://mcp.excalidraw.com` for rendering and iterating editable diagrams |
| Skill `excalidraw` | Planning workflow for architecture, flows, dependencies, decisions, roadmaps, and risk maps |

## Requirements

- Claude Code with MCP support;
- first-use OAuth authorization, if requested by the Excalidraw server;
- repository context and planning artifacts when the diagram represents an existing project.

The plugin does not store credentials. Restart the Claude Code session after installation if the MCP server does not appear in `/mcp`.

## Security

OAuth authorization is handled by the MCP client. Do not commit tokens, credentials, private data, or generated diagrams containing sensitive information.

## Example prompts

```text
Map the architecture of this feature in Excalidraw. Read the repository instructions first, show assumptions, and do not change code.
```

```text
Turn the approved implementation plan into a user flow and a dependency diagram in Excalidraw.
```

```text
Review this proposal visually and highlight risks, external dependencies, decisions, and unknowns.
```

## Scope

The plugin supports visual planning. It does not approve requirements, implement code, or replace technical verification.
