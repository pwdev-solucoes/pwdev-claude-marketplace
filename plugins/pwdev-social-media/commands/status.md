---
description: Mostra o estado — contexto, chaves de API, Figma, e gasto acumulado
---

# /pwdev-social-media:status

## STEP 0 — Idioma
`${CLAUDE_PLUGIN_ROOT}/references/language.md`

## Verificações
1. `.claude/pwdev-social-context.md` — seções com `{{PLACEHOLDER}}`
2. `${CLAUDE_PLUGIN_ROOT}/scripts/check-keys.sh` — quais chaves existem
3. MCP do Figma responde? (opcional) Notion?
4. Vault do Obsidian acessível (seção 7)
5. `.pwdev-social/gerados/manifest.jsonl` — gasto acumulado

## Saída
```
pwdev-social-media — {{organização}}

Contexto     {{n}}/9 seções
  3 Brand kit    pendente → brand-kit

Chaves de API (caminho principal)
  Ideogram       configurada | ausente → modo prompt
  Leonardo       ...
  Flux           ...
  Runway         ...
  Freepik        ...

Camadas opcionais
  Figma          conectado | ausente → composição vira especificação
  Notion         conectado | ausente
  Obsidian       {{caminho}} — acessível | não encontrado

Gasto acumulado
  Chamadas: {{n}} · Aproveitamento: {{%}}

Modo atual: completo | prompt | degradado
Próximo passo: {{comando}}
```

Deixe claro o **modo atual** — define o que o plugin consegue entregar.
