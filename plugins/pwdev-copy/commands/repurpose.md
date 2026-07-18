---
description: Transforma uma peça de conteúdo em vários derivados nativos, com ranking de alavancagem e cronograma
argument-hint: "[arquivo ou material de origem]"
---

# /pwdev-copy:repurpose — Reaproveitar conteúdo

## STEP 0 — Idioma
`${CLAUDE_PLUGIN_ROOT}/references/language.md`

## STEP 1 — Origem
`$ARGUMENTS` pode ser caminho de arquivo, URL ou texto colado. Se vazio, peça.

## STEP 2 — Canais
Leia a seção 8 do contexto. Gere derivados **apenas** para canais que a
organização mantém — derivado para canal inativo é desperdício puro.

Se a seção 8 estiver vazia, pergunte antes de gerar para tudo.

## STEP 3 — Executar
Invoque a skill `copy-repurpose`. Para conteúdo de política pública, encadeie
`copy-setor-publico`.

## STEP 4 — Revisar
Rode `copy-review` em cada derivado. Reaproveitamento é justamente onde a
deriva de tom mais aparece.

## STEP 5 — Entregar
Derivados + ranking de alavancagem + cronograma + ativos visuais necessários.

**Nunca publique nem agende** sem confirmação explícita do usuário.
