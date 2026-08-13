# AGENTS.md — schema operacional deste brain

Este diretório é um **segundo cérebro**: uma LLM Wiki persistente em
Markdown (padrão Karpathy) mantida como bundle **Open Knowledge Format
v0.2**. Qualquer agente que trabalhe aqui — Claude Code com o plugin
pwdev-brain, Codex ou outro — segue estas regras. Este arquivo pode evoluir
com o uso, em colaboração com o usuário. Não faz parte do bundle OKF.

## Estrutura

| Caminho | O que é | Regra |
|---|---|---|
| `raw/` | Fontes curadas (artigos, papers, dados) — fonte de verdade | Ler sempre, **nunca modificar**; fora do bundle OKF |
| `wiki/` | Bundle OKF v0.2 — documentos de conceito mantidos pelo agente | Todo `.md` fora de `output/`, exceto `index.md` e `log.md`, é exatamente um conceito |
| `wiki/index.md` | Índice raiz, descoberta progressiva | Único `index.md` com frontmatter — só `okf_version: "0.2"` |
| `wiki/log.md` | Histórico do bundle, agrupado por data desc | Append-only; entradas antigas são imutáveis |
| `wiki/output/` | Artefatos gerados (HTML, imagens, PDFs, exports…) | Sempre em pasta `YYYY-MM-DD-<slug>/`; sem frontmatter; fora do índice OKF |

## Documentos de conceito

- UTF-8, frontmatter YAML no topo, `type` obrigatório e não vazio.
- Recomendados: `title`, `description` (uma frase), `tags`, `generated {by, at}`,
  `sources` (cada entrada com `resource`).
- Opcionais: `resource`, `verified`, `status` (`draft`|`stable`|`deprecated`,
  ausente = `stable`), `stale_after` (`YYYY-MM-DD`).
- Atores: `human:<id>`, `process:<id>` ou `<producer>/<version>`. Datas ISO 8601.
- Afirmação vinda de fonte → nota de rodapé resolvendo para `sources[].id`.
- Preserve campos desconhecidos ao editar; não invente metadados ausentes.
- Nomes de arquivo descritivos em `kebab-case`; não mover sem atualizar links
  de entrada.

## Operações

- **INGEST** — ler fonte de `raw/` sem modificá-la; discutir os pontos com o
  usuário; criar/atualizar conceitos com citações; atualizar links, índices
  e `log.md`.
- **QUERY** — navegar `index.md` → conceitos; sintetizar com citações;
  respostas duráveis viram conceitos; artefatos vão para
  `wiki/output/YYYY-MM-DD-<slug>/`.
- **LINT** — revisar frontmatter, índices, órfãos, links, citações,
  staleness, contradições e artefatos fora do lugar; corrigir só com
  aprovação e registrar no log.

## Preferências do usuário

Ingestão: {{ponto-a-ponto | lote}}
Idioma da prosa: {{pt-BR | en}}
Ator humano: human:{{id}}
