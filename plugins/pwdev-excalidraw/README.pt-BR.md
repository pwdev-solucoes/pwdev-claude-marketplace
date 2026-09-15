# PWDEV Excalidraw — Planejamento Visual

> [English version](./README.md)

Plugin para Claude Code que apoia planejamento com diagramas Excalidraw editáveis por meio do servidor MCP oficial do Excalidraw.

## O que tem aqui

| Peça | Propósito |
|---|---|
| MCP `excalidraw` | Servidor remoto oficial em `https://mcp.excalidraw.com` para renderizar e iterar diagramas editáveis |
| Skill `excalidraw` | Fluxo de planejamento para arquitetura, fluxos, dependências, decisões, roadmaps e mapas de risco |

## Requisitos

- Claude Code com suporte a MCP;
- autorização OAuth na primeira utilização, se solicitada pelo servidor Excalidraw;
- contexto do repositório e artefatos de planejamento quando o diagrama representar um projeto existente.

O plugin não armazena credenciais. Reinicie a sessão do Claude Code depois da instalação se o servidor MCP não aparecer em `/mcp`.

## Segurança

A autorização OAuth é tratada pelo cliente MCP. Não faça commit de tokens, credenciais, dados privados ou diagramas gerados que contenham informação sensível.

## Exemplos

```text
Mapeie a arquitetura desta feature no Excalidraw. Leia as instruções do repositório, mostre as premissas e não altere o código.
```

```text
Transforme o plano de implementação aprovado em um fluxo de usuário e um diagrama de dependências no Excalidraw.
```

```text
Revise visualmente esta proposta e destaque riscos, dependências externas, decisões e desconhecidos.
```

## Escopo

O plugin apoia planejamento visual. Ele não aprova requisitos, implementa código nem substitui validação técnica.
