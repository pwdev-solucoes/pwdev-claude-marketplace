---
description: Revisa copy existente — passe anti-slop determinístico + os 7 sweeps
argument-hint: "[arquivo ou texto]"
---

# /pwdev-copy:revisar — Revisar copy

## STEP 0 — Idioma
`${CLAUDE_PLUGIN_ROOT}/references/language.md`

## STEP 1 — Entrada
`$ARGUMENTS` pode ser caminho de arquivo ou texto colado. Se vazio, peça.

## STEP 2 — Profundidade
- **rápida** — passe 0 + sweeps 1, 3, 5
- **completa** — passe 0 + todos os 7 sweeps com revalidação

Padrão: completa. Use rápida só se o usuário pedir.

## STEP 3 — Despachar
Spawn do subagente `reviewer`.

## STEP 4 — Entregar
Findings por linha, tabela-resumo, versão revisada completa e a seção
"não alterado".

Se a seção 5 do contexto estiver vazia, avise que o Sweep 2 rodou sem régua
de voz e sugira `/pwdev-copy:treinar`.
