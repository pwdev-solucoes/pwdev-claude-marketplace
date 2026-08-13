# PWDEV Brain — Segundo Cérebro em LLM Wiki (OKF)

> [English version](./README.md)

Plugin de Claude Code que mantém um **segundo cérebro persistente**: uma LLM
Wiki em Markdown no [padrão do Karpathy](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f)
mantida como bundle [Open Knowledge Format v0.2](https://github.com/GoogleCloudPlatform/knowledge-catalog/blob/main/okf/SPEC.md).
Em vez de reconstruir o conhecimento a partir dos documentos brutos a cada
pergunta, as fontes são lidas uma vez, discutidas e integradas a uma wiki
que acumula valor — toda afirmação citada, toda mudança registrada.

```
raw/  ──INGEST──▶  wiki/ (OKF v0.2)  ──QUERY──▶  respostas citadas
(fontes            │ index.md · log.md            + sínteses duráveis
 imutáveis)        │ documentos de conceito       ──▶ wiki/output/
                   └──LINT──▶ relatório de conformidade  YYYY-MM-DD-<slug>/
```

## O que tem aqui

| Peça | Propósito |
|---|---|
| `/pwdev-brain:init` | Setup guiado: caminho do brain (global ou por projeto), scaffold OKF (`raw/`, `wiki/index.md`, `wiki/log.md`, `wiki/output/`, `AGENTS.md`), identidade para `human:<id>`, preferências |
| `/pwdev-brain:status` | Saúde só-leitura: validade do índice, contagem de conceitos por `status`, últimas entradas do log |
| `/pwdev-brain:ingest` | INGEST: fonte para `raw/` (arquivo ou URL), o subagente `brain-ingestor` extrai uma proposta, os pontos são **discutidos com você** antes de qualquer escrita, e só então aplicados com citações, links, índice e log |
| `/pwdev-brain:query` | QUERY: navegação dirigida pelo índice, síntese com citação por afirmação, respostas duráveis viram conceitos draft, entregáveis vão para `wiki/output/YYYY-MM-DD-<slug>/` |
| `/pwdev-brain:lint` | LINT: o subagente `brain-linter` valida o catálogo de regras BR-001…BR-306; sempre reporta, corrige só o que você aprovar |
| Skill `brain` | Roteia intenções em linguagem natural ("adiciona isso ao meu brain", "o que minha wiki diz sobre X") para a operação certa |
| Servidor MCP `brain` | Embutido, **somente-leitura**, Node stdio zero dependências — 6 tools: `brain_info`, `brain_index`, `brain_list`, `brain_search` (ranqueada, insensível a acentos, com snippets), `brain_get`, `brain_log`. Funciona no Claude Code e em qualquer cliente MCP |
| `references/okf-spec.md` | Fonte única de verdade do formato, carregada por todo escritor |
| 2 subagentes | `brain-ingestor` (extract/apply) e `brain-linter` (report/fix) — a leitura pesada fica fora do contexto principal |

## Requisitos

- Node.js 18+ **apenas para o servidor MCP** — sem ele tudo degrada
  graciosamente para o fluxo filesystem. Sem API keys, sem npm install.
- Um diretório para o brain (o `init` cria se não existir).

## Setup

Rode `/pwdev-brain:init` e siga os passos. Resulta em:

- um diretório do brain (ex.: `~/brain`) com `raw/`, `wiki/` e `AGENTS.md`;
- `.claude/pwdev-brain-context.md` no projeto, registrando idioma, caminho
  do brain, seu ator OKF (`human:<id>`) e preferências de ingestão.

Depois alimente: `/pwdev-brain:ingest <arquivo-ou-URL>` e pergunte:
`/pwdev-brain:query <pergunta>`.

No Claude Code o servidor MCP encontra o brain pelo arquivo de contexto do
projeto — nenhuma configuração necessária. Reinicie a sessão após instalar o
plugin para o servidor conectar; confirme com `/mcp` e `/pwdev-brain:status`.

## Usando com outros clientes MCP

O servidor é um script Node puro — qualquer cliente MCP pode rodá-lo. Para o
Claude Desktop, adicione ao `claude_desktop_config.json` (a env var substitui
o arquivo de contexto do projeto):

```json
{
  "mcpServers": {
    "brain": {
      "command": "node",
      "args": ["/caminho/absoluto/para/plugins/pwdev-brain/server/index.mjs"],
      "env": { "PWDEV_BRAIN_PATH": "/caminho/absoluto/do/seu/brain" }
    }
  }
}
```

Toda tool também aceita um argumento opcional `brain_path`, que sobrepõe a
env var e o arquivo de contexto (útil para múltiplos brains).

## Garantias

- `raw/` nunca é modificado — é a fonte de verdade imutável.
- Nada entra em `wiki/` sem discussão: o ingestor grava uma proposta, você
  aprova/edita/descarta cada ponto, só então ele aplica.
- Toda afirmação carrega nota de rodapé resolvendo para uma entrada de
  `sources[].id`.
- `wiki/log.md` é append-only; o histórico nunca é reescrito.
- O lint nunca auto-resolve contradições ou staleness — viram
  recomendações.
- O servidor MCP é somente-leitura por construção: nenhuma tool grava,
  `wiki/output/` nunca é servido, paths passam por checagem de realpath
  contra a raiz do brain e só arquivos de texto são legíveis.

## Troubleshooting

| Sintoma | Causa / correção |
|---|---|
| Comando aborta apontando `/pwdev-brain:init` | Falta `.claude/pwdev-brain-context.md` ou `wiki/index.md` inválido — rode o init |
| `status` mostra `okf_version ⚠` | Frontmatter do índice raiz divergiu — rode `/pwdev-brain:lint` (BR-003) |
| Ingest não gravou nada após a discussão | Todos os pontos foram descartados, ou a seção `## Decisões` do handoff ficou vazia — refaça o passe apply após registrar as decisões |
| Artefatos soltos em `wiki/` | Arquivos gerados fora de `wiki/output/YYYY-MM-DD-<slug>/` — o `/pwdev-brain:lint` sinaliza (BR-006) e move com aprovação |
| Tools MCP falhando com brain válido | Sessão iniciada antes do plugin/env var, ou Node ausente — reinicie a sessão; o plugin segue funcional via filesystem |
| Tool responde "Brain não configurado" | Sem argumento `brain_path`, sem `PWDEV_BRAIN_PATH` e sem arquivo de contexto do projeto — rode `/pwdev-brain:init` ou defina a env var |
