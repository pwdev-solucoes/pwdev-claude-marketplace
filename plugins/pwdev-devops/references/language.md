# Protocolo de Idioma (STEP 0)

Todo comando do pwdev-devops roda isto como **STEP 0**, antes de qualquer outra etapa.

## Ordem de resolução (silenciosa — todos os comandos exceto `treinar`)

1. Ler `.claude/pwdev-devops-context.md` → seção 1, campo **Idioma**.
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

5. Persistir a escolha em `.claude/pwdev-devops-context.md` **e** mesclar
   `"lang": "<valor>"` em `.planning/config.json` (nunca sobrescrever outros campos).

## Distinção deste plugin

Conversa, relatório e documentação seguem `{{LANG}}`.

**Comando, saída de ferramenta, log e nome de recurso nunca são traduzidos.**
Traduzir saída de `kubectl` ou de `EXPLAIN` destrói a informação e impede que
alguém pesquise a mensagem de erro.

## Regras de aplicação

- **Termos técnicos** permanecem em inglês: deployment, pod, ingress, rollback,
  quorum, bloat, vacuum, throughput, blast radius, runbook, postmortem.
- **Nomes de arquivo** permanecem em inglês: `SKILL.md`, `pwdev-devops-context.md`.
- **Chaves de dados estruturados** permanecem em inglês.
- **Spawn de subagente**: sempre passar `LANGUAGE: {{LANG}}` e
  `AMBIENTE: {{ENV}}` no prompt.
