# Protocolo de Idioma (STEP 0)

Todo comando do pwdev-social-media roda isto como **STEP 0**, antes de qualquer outra etapa.

## Ordem de resolução (silenciosa — todos os comandos exceto `treinar`)

1. Ler `.claude/pwdev-social-context.md` → seção 1, campo **Idioma das peças**.
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

5. Persistir a escolha em `.claude/pwdev-social-context.md` **e** mesclar
   `"lang": "<valor>"` em `.planning/config.json` (nunca sobrescrever outros campos).

## Distinção crítica deste plugin

O pwdev-social-media tem **dois idiomas independentes**:

| Eixo | Governado por | Padrão |
|---|---|---|
| **Idioma da conversa** — perguntas, resumos, findings | `{{LANG}}` | pt-BR |
| **Idioma das peças** — o texto dentro do criativo | Seção 1 do contexto | pt-BR |

Eles podem divergir: uma agência brasileira produzindo peça em inglês
conversa em pt-BR e entrega a peça em `en`. Sempre confirmar antes de assumir que são
iguais.

## Regras de aplicação

- **Termos técnicos** permanecem em inglês: CTA, headline, alt text, brand kit,
  design system, token, Auto Layout, frame, feed, story, reels, thumbnail.
- **Nomes de arquivo** permanecem em inglês: `SKILL.md`, `pwdev-social-context.md`.
- **Chaves de dados estruturados** permanecem em inglês.
- **Spawn de subagente**: sempre passar `LANGUAGE: {{LANG}}` e
  `ASSET_LANGUAGE: {{ASSET_LANG}}` no prompt.
