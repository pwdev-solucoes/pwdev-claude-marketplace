---
description: Mostra o estado do treino — o que está preenchido no contexto, quais ativos existem e o que falta
---

# /pwdev-copy:status — Estado do treino

## STEP 0 — Idioma
`${CLAUDE_PLUGIN_ROOT}/references/language.md`

## Verificações
1. `.claude/pwdev-copy-context.md` existe? Quais seções ainda têm `{{PLACEHOLDER}}`?
2. `.claude/research/` — quais dossiês de VOC, de quando?
3. Idioma da conversa e idioma da copy configurados?
4. MCPs úteis instalados? (Playwright, Notion, Perplexity)

## Saída
```
Treino do pwdev-copy — {{organização}}

Contexto        {{n}}/9 seções preenchidas
  3 Posicionamento   pendente → /pwdev-copy:brief
  6 VOC              pendente → /pwdev-copy:voc

Dossiês VOC     {{n}} ({{mais recente}})
Idioma          conversa pt-BR · copy pt-BR
MCPs            Playwright ausente (voc-research fica degradado)

Próximo passo recomendado: {{comando}}
```

Sinalize dossiê de VOC com mais de 6 meses como possivelmente desatualizado.
