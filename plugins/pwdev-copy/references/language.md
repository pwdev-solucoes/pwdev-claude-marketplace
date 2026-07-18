# Protocolo de Idioma (STEP 0)

Todo comando do pwdev-copy roda isto como **STEP 0**, antes de qualquer outra etapa.

## Ordem de resolução (silenciosa — todos os comandos exceto `treinar`)

1. Ler `.claude/pwdev-copy-context.md` → seção 1, campo **Idioma padrão da copy**.
   Se válido (`pt-BR` ou `en`) → usar silenciosamente.
2. Se ausente, ler `.planning/config.json` → campo `lang` (compartilhado com
   pwdev-code e pwdev-feat).
3. Se ainda ausente, detectar o idioma de `$ARGUMENTS`.
4. Se ambíguo ou vazio, perguntar:

   ```
   Em qual idioma deseja seguir? / Which language would you like to use?

   1. Portugues (PT-BR)
   2. English (EN)
   ```

5. Persistir a escolha em `.claude/pwdev-copy-context.md` **e** mesclar
   `"lang": "<valor>"` em `.planning/config.json` (nunca sobrescrever outros campos).

## Distinção crítica deste plugin

O pwdev-copy tem **dois idiomas independentes**:

| Eixo | Governado por | Padrão |
|---|---|---|
| **Idioma da conversa** — perguntas, resumos, findings | `{{LANG}}` | pt-BR |
| **Idioma da copy entregue** — o texto final do cliente | Seção 1 do contexto | pt-BR |

Eles podem divergir: uma agência brasileira escrevendo uma landing em inglês
conversa em pt-BR e entrega em `en`. Sempre confirmar antes de assumir que são
iguais.

## Regras de aplicação

- **Termos técnicos** permanecem em inglês: CTA, headline, landing page, copy,
  lead, funil, CRO, SEO, hero, above the fold.
- **Nomes de arquivo** permanecem em inglês: `SKILL.md`, `pwdev-copy-context.md`.
- **Chaves de dados estruturados** permanecem em inglês.
- **Spawn de subagente**: sempre passar `LANGUAGE: {{LANG}}` e
  `COPY_LANGUAGE: {{COPY_LANG}}` no prompt.
