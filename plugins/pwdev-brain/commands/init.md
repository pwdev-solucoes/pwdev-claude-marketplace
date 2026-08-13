---
description: Setup guiado do segundo cérebro — caminho do brain, scaffold OKF v0.2, identidade e preferências
argument-hint: "[caminho-do-brain]"
---

# /pwdev-brain:init

## STEP 0 — Idioma
`${CLAUDE_PLUGIN_ROOT}/references/language.md`. Este comando sempre pergunta.

## STEP 1 — Caminho do brain
Aceite de `$ARGUMENTS`; se vazio, pergunte com opções:

1. **Global** — `~/brain` (um segundo cérebro para tudo, mesmo caminho em
   qualquer projeto)
2. **Neste projeto** — `./brain` na raiz do repositório atual
3. **Caminho custom** — o usuário informa

Expanda `~` e grave sempre o **caminho absoluto**.

## STEP 2 — Detecção de brain existente
Se `<brain>/wiki/index.md` existe e tem frontmatter parseável com
`okf_version` → **brain existente**: não faça scaffold, apenas registre no
contexto (STEP 5) e reporte contagem de conceitos e última entrada do
`log.md`. Senão, siga para o STEP 3.

## STEP 3 — Scaffold
Crie **só o que faltar — nunca sobrescreva** arquivo existente:

| Alvo | Origem |
|---|---|
| `<brain>/raw/` | diretório vazio |
| `<brain>/wiki/index.md` | `${CLAUDE_PLUGIN_ROOT}/templates/index.template.md` |
| `<brain>/wiki/log.md` | `${CLAUDE_PLUGIN_ROOT}/templates/log.template.md` — substituir `{{YYYY-MM-DD}}` pela data de hoje |
| `<brain>/wiki/output/.gitkeep` | arquivo vazio |
| `<brain>/AGENTS.md` | `${CLAUDE_PLUGIN_ROOT}/templates/AGENTS.template.md` — preencher os placeholders da seção "Preferências do usuário" com as respostas dos STEPs 4 e 5 |

## STEP 4 — Identidade
Pergunte o id curto do usuário para o ator `human:<id>` do OKF — sugira a
partir de `git config user.name`/`user.email` (ex.: `human:paulo`). O ator
de processo é fixo: `pwdev-brain/1.0.0`.

## STEP 5 — Preferências
Pergunte (com defaults entre parênteses):

1. **Ingestão** — revisar ponto-a-ponto ou em lote com aprovação única?
   (ponto-a-ponto)
2. **stale_after default** — sugerir data de obsolescência nos conceitos
   novos? (+6 meses | nenhum)
3. **Incorporação em query** — o QUERY pode propor gravar respostas duráveis
   como conceito? (propor | só-quando-pedido)

## STEP 6 — Contexto
Grave `.claude/pwdev-brain-context.md` a partir de
`${CLAUDE_PLUGIN_ROOT}/templates/pwdev-brain-context.template.md`,
preenchendo todos os placeholders. Se o brain era existente, preencha as
preferências perguntando só o que não dá para inferir do `AGENTS.md` dele.

## STEP 7 — MCP (opcional)
O plugin traz um servidor MCP `brain` embutido, somente-leitura (6 tools).
**No Claude Code nada precisa ser configurado**: o servidor encontra o brain
pelo `.claude/pwdev-brain-context.md` do projeto.

Só ofereça a env var se o usuário quiser usar o brain em **outros clientes
MCP** (Claude Desktop etc.) ou fora de projetos com contexto. Mostre o bloco
e pergunte se pode aplicar (append em `~/.zshrc` só com confirmação
explícita; senão, o usuário aplica manualmente):

```sh
export PWDEV_BRAIN_PATH="{{caminho absoluto do brain}}"
```

Avise: MCP recém-instalado e env var nova só valem após **reiniciar a
sessão** do Claude Code. A prova real é `/pwdev-brain:status`.

## Saída
```
pwdev-brain — {{caminho absoluto}}

Brain       {{criado | registrado (existente)}} · okf_version 0.2
Conceitos   {{n}} · raw {{n}} fontes · output {{n}} artefatos
Identidade  human:{{id}} · pwdev-brain/1.0.0
Contexto    .claude/pwdev-brain-context.md gravado
MCP         brain (6 tools, só-leitura) · reinicie a sessão para ativar

Próximos passos: /pwdev-brain:ingest <fonte> · /pwdev-brain:status
```
