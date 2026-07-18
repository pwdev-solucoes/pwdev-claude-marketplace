---
description: Exporta peças aprovadas e monta o pacote de entrega com legendas e alt text
argument-hint: "[campanha]"
---

# /pwdev-social:exportar

## STEP 0 — Idioma
`${CLAUDE_PLUGIN_ROOT}/references/language.md`

## STEP 1 — Portão
- [ ] `creative-review` com veredito APROVADO
- [ ] alt text de cada peça (carrossel: por slide)
- [ ] nenhum `[PREENCHER]`
- [ ] peça em `04 — Aprovado`
- [ ] aprovador humano confirmou, se a seção 9 exigir

Falhou algum: **não exporte**. Diga o que falta.

## STEP 2 — Exportar
`export-handoff`. Nomenclatura
`{{campanha}}_{{plataforma}}_{{formato}}_{{n}}_{{versão}}.{{ext}}`

## STEP 3 — Pacote
peças · legendas.md · alt-text.md · publicacao.md · origem.md

## STEP 4 — Arquivar
Ofereça `vault-sync`.

**Este plugin não publica.**
