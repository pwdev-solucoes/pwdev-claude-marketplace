---
description: QUERY — responde a partir da wiki com síntese citada; respostas duráveis viram conceitos, artefatos vão para output/
argument-hint: "<pergunta>"
---

# /pwdev-brain:query

Roda **inline** — a leitura é dirigida pelo índice e a conversa é o valor.
Antes de escrever qualquer coisa na wiki, carregue
`${CLAUDE_PLUGIN_ROOT}/references/okf-spec.md`. O MCP `brain` é
**somente-leitura**: toda escrita (STEPs 3 e 4) é feita via filesystem.

## STEP 0 — Idioma
`${CLAUDE_PLUGIN_ROOT}/references/language.md`

## Gate
Sem `.claude/pwdev-brain-context.md` ou sem `<brain>/wiki/index.md` válido →
**aborte** e aponte `/pwdev-brain:init`.

## STEP 1 — Navegação dirigida

**Path A — MCP `brain` conectado** (preferido): `brain_index` →
`brain_search` com os termos da pergunta → `brain_get` dos candidatos
(siga links internos **1 nível** quando citados na resposta). Os snippets e
o score da busca economizam contexto frente à leitura de arquivos inteiros.

**Path B — MCP ausente ou falhando** (fallback, sem simular resultado):
1. Leia `wiki/index.md` e identifique os conceitos candidatos.
2. Leia os candidatos; siga links internos **1 nível** quando citados na
   resposta.
3. Só se o índice não cobrir a pergunta, complemente com Grep na `wiki/`.
   **Nunca leia a wiki inteira por Glob.**

## STEP 2 — Síntese citada
- Afirmações vindas da wiki levam citação: conceito de origem e, quando a
  atribuição for por afirmação, a fonte (`sources[].id`) daquele conceito.
- Conhecimento do modelo que não está na wiki é **sinalizado como externo** —
  nunca apresentado como se fosse conteúdo do brain.
- Sem cobertura → diga explicitamente que a wiki não cobre e sugira
  `/pwdev-brain:ingest` com fontes candidatas.

## STEP 3 — Incorporação durável (condicional)
Se a preferência do contexto for `propor` e a resposta cruzou ≥2 conceitos
com síntese nova, ou resolveu algo que será reperguntado:

1. Proponha gravar como conceito (`type: Synthesis` ou `Comparison`,
   `status: draft`, `generated.by: pwdev-brain/1.0.0`, `sources` apontando
   para os conceitos usados).
2. **Só grave com aprovação.** Ao gravar: conceito + entrada no
   `wiki/index.md` + entrada `**Consulta**:` no `wiki/log.md`.

Com preferência `só-quando-pedido`, incorpore apenas se o usuário pedir.

## STEP 4 — Artefatos
Se a resposta for um entregável (relatório, comparativo, HTML, gráfico,
planilha): grave em `<brain>/wiki/output/{{YYYY-MM-DD}}-{{slug}}/` com todos
os auxiliares juntos — **nunca** solto em `wiki/` nem na raiz de `output/`.
Registre o caminho no `wiki/log.md` se o artefato tiver valor durável.

## Saída
Resposta citada, seguida de:

```
Conceitos consultados: {{lista}}
Incorporado à wiki: {{sim → caminho | não}}
Artefato: {{wiki/output/YYYY-MM-DD-slug/ | —}}
```
