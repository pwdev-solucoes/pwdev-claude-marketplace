---
description: Estado do segundo cérebro — brain, índice, conceitos, log e contexto
---

# /pwdev-brain:status

## STEP 0 — Idioma
`${CLAUDE_PLUGIN_ROOT}/references/language.md`

## Verificações
Tudo **só leitura** — nenhuma escrita neste comando.

1. `.claude/pwdev-brain-context.md` — existe? Idioma, caminho do brain e
   identidade preenchidos?
2. **Prova viva do MCP nesta sessão**: chamar a tool `brain_info`.
   - Sucesso → use o retorno como fonte das contagens e reporte
     `resolved_via` (`param` | `env` | `context`). Pule as verificações 3–6
     (a tool já as cobre).
   - Erro/tool ausente → `MCP não conectado` (node ausente, plugin recém-
     instalado ou sessão iniciada antes dele — **reiniciar a sessão**; não é
     erro de config do brain). Siga com as verificações 3–6 via filesystem.
3. Estrutura do brain: `raw/`, `wiki/`, `wiki/output/` existem?
4. `wiki/index.md` — frontmatter parseável com `okf_version: "0.2"`?
5. Conceitos: Glob `wiki/**/*.md` excluindo `wiki/index.md`, `wiki/log.md` e
   `wiki/output/**` → contagem total; Grep no frontmatter → contagem por
   `status` (`draft` / `stable` / `deprecated`; sem `status` conta como
   `stable`).
6. `wiki/log.md` — últimas 3 entradas + contagens de `raw/` e pastas datadas
   em `wiki/output/`.

## Gate
Sem contexto → **modo consultivo**: reporte o que for verificável e aponte
`/pwdev-brain:init`. Não crie nada.

## Saída
```
pwdev-brain — {{caminho | "não configurado"}}

Brain      {{ok | AUSENTE | index inválido}} · okf_version {{0.2 | ⚠ divergente}}
MCP        {{ok (brain_info · via {{param|env|context}}) | não conectado — reiniciar sessão? node instalado?}}
Conceitos  {{n}} ({{d}} draft · {{s}} stable · {{x}} deprecated)
Fontes     raw {{n}} · output {{n}} pastas de artefatos
Log        último: {{YYYY-MM-DD — operação e resumo}}
Contexto   {{ok (human:{{id}}) | AUSENTE → /pwdev-brain:init}}

Modo: completo | consultivo
```

MCP não conectado com brain válido no filesystem é quase sempre **sessão
iniciada antes do plugin/env var** ou **node ausente** — o plugin continua
funcional via filesystem (Path B).
