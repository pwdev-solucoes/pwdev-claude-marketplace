---
description: Pesquisa de Voz do Cliente — coleta linguagem literal do público em reviews, fóruns e concorrentes
argument-hint: "[alvo: produto próprio, concorrente ou categoria]"
---

# /pwdev-copy:voc — Pesquisa de voz do cliente

## STEP 0 — Idioma
`${CLAUDE_PLUGIN_ROOT}/references/language.md`

## STEP 1 — Escopo
Defina com o usuário: alvo, segmento, profundidade (rápida ~30min | completa).
Liste as fontes que pretende consultar **antes** de começar.

## STEP 2 — Despachar
Spawn do subagente `voc` (contexto isolado — a coleta é pesada).
Passe: `LANGUAGE`, `COPY_LANGUAGE`, `ALVO`, `PUBLICO`, `PROFUNDIDADE`, `CONTEXT_FILE`.

## STEP 3 — Consolidar
Receba o dossiê, apresente os padrões ranqueados e **pergunte antes de gravar**
a seção 6 do contexto.

Destaque sempre, em separado:
- fontes que **não** foram acessadas e por quê
- padrões com apenas uma fonte (anedota, não ângulo)
