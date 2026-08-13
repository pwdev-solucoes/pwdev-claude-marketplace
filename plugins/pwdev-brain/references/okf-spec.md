# LLM Wiki em Open Knowledge Format — spec operacional

Fonte única de verdade do formato mantido pelo pwdev-brain. Combina o padrão
LLM Wiki descrito por Andrej Karpathy com a especificação Open Knowledge
Format (OKF) v0.2:

- https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f
- https://github.com/GoogleCloudPlatform/knowledge-catalog/blob/main/okf/SPEC.md

Todo agente ou comando que escreve na wiki carrega este arquivo antes.

## Ideia central

Mantenha uma wiki persistente em Markdown entre o usuário e suas fontes. Em
vez de reconstruir o conhecimento a partir dos documentos brutos a cada
pergunta, leia as fontes, extraia o que importa e integre esse conteúdo à
wiki existente.

A wiki deve acumular valor: novas fontes e novas perguntas podem atualizar
páginas, conexões, comparações e sínteses já existentes.

O usuário seleciona fontes, explora o conteúdo e faz perguntas. O agente
mantém a wiki: resume, organiza, cria relações, atualiza páginas e cuida da
consistência.

## Arquitetura do brain

O diretório raiz do brain (caminho registrado em
`.claude/pwdev-brain-context.md`) contém:

### `raw/`

Coleção curada de documentos-fonte, como artigos, papers, imagens e arquivos
de dados.

- É a fonte de verdade.
- O agente pode ler seus arquivos, mas **nunca deve modificá-los**.
- Não faz parte do bundle OKF e, por isso, seus arquivos não precisam seguir
  o formato de documentos de conceito.

### `wiki/`

Bundle de conhecimento OKF v0.2 e diretório de arquivos Markdown gerados e
mantidos pelo agente. Pode conter resumos, páginas de entidades, páginas de
conceitos, comparações, panoramas e sínteses.

- O agente cria e atualiza as páginas.
- O agente mantém referências cruzadas e consistência entre elas.
- O usuário e qualquer consumidor compatível com OKF consultam o resultado.
- A raiz do bundle é `wiki/`; links iniciados por `/` são relativos a ela.

### `wiki/output/`

Área exclusiva para artefatos gerados como resultado de consultas ou
operações da wiki: imagens, landing pages, HTML, CSS, JavaScript, gráficos,
apresentações, canvases, PDFs, planilhas, exports e outros arquivos que não
sejam documentos de conceito indexados pelo OKF.

- Todo artefato fica dentro de uma pasta própria de operação, no formato
  `wiki/output/YYYY-MM-DD-<slug>/` — data ISO 8601 da operação + slug
  descritivo em `kebab-case` (ex.: `wiki/output/2026-08-03-landing-page-x/`).
- Nunca criar artefatos diretamente na raiz de `wiki/output/`; a única
  exceção é o eventual `wiki/output/index.md`. Arquivos auxiliares do mesmo
  resultado (HTML e CSS, por exemplo) permanecem juntos na mesma pasta.
- Não misturar resultados de operações distintas na mesma pasta. Variação
  nova → pasta nova com a data da operação e slug adequado.
- Arquivos em `wiki/output/` não representam conceitos, não precisam de
  frontmatter YAML e não entram no `wiki/index.md` como páginas da wiki.
- `wiki/output/index.md` pode existir apenas como inventário operacional dos
  artefatos, sem frontmatter de conceito, apontando para as pastas datadas.
  Não é um índice OKF.
- Quando um artefato tiver valor durável, registre a operação em
  `wiki/log.md` e, se necessário, crie separadamente um documento de
  conceito que explique o conhecimento. O artefato continua em sua pasta
  datada.
- Não confundir `wiki/output/` com `raw/`: output contém derivados gerados
  pelo agente; raw contém fontes preservadas e nunca modificadas.

### `AGENTS.md`

Schema operacional do brain, legível por qualquer agente que abra o
diretório (Claude Code, Codex ou outro). Define a estrutura, as convenções e
os fluxos. Pode evoluir com o uso, em colaboração com o usuário. Não faz
parte do bundle OKF.

## Documentos de conceito OKF

Todo arquivo `.md` dentro de `wiki/`, exceto os nomes reservados `index.md`
e `log.md` e todo o conteúdo de `wiki/output/`, representa exatamente um
conceito. O caminho sem a extensão `.md` é o identificador estável desse
conceito. Prefira nomes de arquivo descritivos em `kebab-case` e não altere
caminhos sem atualizar os links de entrada.

O LINT considera como conjunto de conceitos os arquivos Markdown fora de
`wiki/output/`. O conteúdo de `wiki/output/`, inclusive seu eventual
`index.md`, fica fora da validação de frontmatter, órfãos, entradas de
índice e conformidade de documentos OKF.

Cada documento de conceito deve ser UTF-8 e começar com frontmatter YAML:

```markdown
---
type: Concept
title: Nome legível do conceito
description: Resumo do conceito em uma frase.
resource: https://example.com/recurso-canonico
tags: [tema, contexto]
generated:
  by: human:usuario
  at: 2026-07-23T12:00:00-03:00
sources:
  - id: fonte-principal
    resource: https://example.com/fonte
    title: Fonte principal
---

# Visão geral

Conteúdo estruturado e conectado a [outro conceito](/conceitos/outro.md),
conforme a [fonte principal][^fonte-principal].

[^fonte-principal]: Fonte principal
```

### Regras do frontmatter

- `type` é obrigatório: string curta, não vazia e autoexplicativa.
- `title`, `description`, `resource` e `tags` são recomendados quando seus
  valores forem conhecidos.
- `generated` é recomendado para registrar como o conteúdo atual foi
  produzido e quando ocorreu sua última alteração significativa.
- `verified`, `status` e `stale_after` são opcionais: use quando houver
  confirmação, necessidade de ciclo de vida ou política de atualização.
- `sources` é recomendado quando o conceito deriva de fontes identificáveis.
- `description` deve conter uma única frase útil para índices e busca.
- `resource` identifica o recurso canônico descrito pela página; omita em
  conceitos abstratos sem recurso correspondente.
- `tags` deve ser uma lista YAML de strings curtas.
- `generated.by` segue a convenção de atores: `<producer>/<version>` para
  agentes e ferramentas, `human:<id>` para pessoas e `process:<id>` para
  processos automatizados.
- `generated.at` e `verified[].at` usam data e hora ISO 8601.
- `verified` é uma lista de eventos de verificação, cada um com `by` e `at`.
  Um único evento também pode ser escrito como um mapeamento sem lista.
- `status` aceita `draft`, `stable` ou `deprecated`; quando ausente, o
  conceito é considerado `stable`.
- `stale_after` é uma data absoluta `YYYY-MM-DD`; o conceito fica obsoleto
  quando a data atual for igual ou posterior a ela.
- Campos adicionais são permitidos quando o domínio justificar. **Preserve
  campos desconhecidos ao editar uma página.**
- **Não invente metadados ausentes** apenas para preencher o frontmatter.

Não existe taxonomia universal de tipos. Use poucos valores consistentes e
autoexplicativos: `Source Summary`, `Entity`, `Concept`, `Comparison`,
`Synthesis`, `Playbook`, `Attested Computation` ou tipos específicos do
domínio.

### Proveniência e confiança

Quando um conceito for derivado de material externo ou de outro conceito,
use `sources` no frontmatter:

```yaml
sources:
  - id: fonte-principal
    resource: https://example.com/fonte
    title: Fonte principal
    author: human:autor
    usage_count: 42
    last_modified: 2026-07-23
usage_window:
  from: 2026-07-01
  to: 2026-07-31
```

Cada entrada de `sources` deve ter `resource`. `id`, `title`, `author`,
`usage_count` e `last_modified` são opcionais. `usage_window` é irmão de
`sources` e contextualiza os valores de `usage_count`; uma fonte pode
sobrescrevê-lo localmente.

Para atribuir uma afirmação específica a uma fonte, use uma nota de rodapé
com o mesmo identificador de `sources[].id`:

```markdown
O processamento ocorre diariamente.[^fonte-principal]

[^fonte-principal]: Fonte principal
```

Não use uma lista genérica `# Citations` como convenção primária (legado de
OKF v0.1). Novos documentos usam `sources` + notas de rodapé por afirmação.

## Corpo, links e citações

- Use Markdown estrutural: títulos, listas, tabelas e blocos de código.
- Prefira links absolutos relativos ao bundle, como
  `[Conceito](/conceitos/conceito.md)`. Links relativos também são válidos.
- Explique a relação no texto ao redor do link; o link, sozinho, não tipa a
  relação.
- Links quebrados são tolerados pelo OKF, mas devem ser reportados no LINT e
  corrigidos quando não representarem conhecimento ainda pendente.
- Afirmações vindas de material externo apontam para uma entrada em
  `sources`; atribuição por afirmação usa nota de rodapé cujo rótulo
  corresponde a `sources[].id`.
- Ao citar um arquivo local de `raw/`, use um link Markdown relativo ao
  arquivo. Ao citar uma fonte web, prefira a URL canônica.
- `# Schema`, `# Examples` e `# Computation` têm significado convencional no
  OKF — use quando adequados ao conceito.

## Computações atestadas

Quando um conceito precisar declarar uma forma sancionada de calcular um
valor, use `type: Attested Computation`. O frontmatter pode incluir
`runtime`, `parameters`, `computation`, `executor` e `attester`; o corpo usa
a seção `# Computation` para a definição executável. O OKF descreve a
computação e como verificá-la, mas não executa o código nem define seu
pacote ou ambiente de execução.

~~~markdown
---
type: Attested Computation
title: Receita anual
runtime: bigquery
parameters:
  - name: year
    type: integer
    required: true
executor:
  resource: /skills/run-query.md
  receipt: [job_id, executed_sql, result]
attester:
  resource: /attesters/sql-equality.py
generated:
  by: human:usuario
  at: 2026-08-03T12:00:00-03:00
---

# Computation

```sql
SELECT SUM(amount) AS revenue
FROM finance.recognized_revenue
WHERE fiscal_year = @year
```
~~~

## Operações

### INGEST — `/pwdev-brain:ingest`

Ao processar uma nova fonte adicionada a `raw/`:

1. Leia a fonte sem modificá-la.
2. Discuta com o usuário os principais pontos extraídos.
3. Crie ou atualize os documentos de conceito afetados, incluindo um resumo
   da fonte quando ele tiver valor próprio.
4. Preencha o frontmatter OKF de todo documento criado e atualize
   `generated.at` apenas nas alterações significativas. Preserve
   `generated.by` quando a origem do conteúdo não mudar.
5. Adicione links entre os conceitos relacionados e citações às fontes.
6. Atualize `wiki/index.md` e os índices de subdiretórios afetados.
7. Atualize outras páginas de entidades, conceitos e sínteses afetadas.
8. Artefatos gerados vão para `wiki/output/YYYY-MM-DD-<slug>/` — nunca
   direto em `wiki/output/`, `wiki/`, subdiretórios de conceito ou na raiz.
9. Registre a operação em `wiki/log.md`.

Uma fonte pode afetar muitas páginas. O fluxo pode processar ponto-a-ponto
ou em lote, conforme a preferência registrada no contexto.

### QUERY — `/pwdev-brain:query`

Ao receber uma pergunta sobre a wiki:

1. Leia `wiki/index.md` para localizar as páginas relevantes.
2. Navegue pelos índices de subdiretórios e links antes de fazer uma busca
   mais ampla.
3. Pesquise e leia os documentos de conceito relevantes.
4. Sintetize uma resposta com citações.
5. Se o resultado for um artefato, salve em
   `wiki/output/YYYY-MM-DD-<slug>/`; não o trate como documento de conceito.
6. Quando uma resposta, comparação, análise ou conexão tiver valor durável,
   incorpore o conhecimento como documento de conceito OKF e atualize índice
   e log. Artefato associado permanece na pasta datada, com o caminho
   registrado no log ou no conceito quando ajudar na descoberta.

Consultas úteis contribuem para o acúmulo de conhecimento, em vez de
permanecer apenas no histórico da conversa.

### LINT — `/pwdev-brain:lint`

Revisão periódica de saúde e conformidade. O catálogo completo de regras
está em `lint-rules.md` (mesmo diretório). Um link quebrado não torna o
bundle inválido segundo o OKF, mas pode indicar problema de manutenção.

## Índices e log

### `wiki/index.md`

Índice raiz do bundle e ponto de entrada para descoberta progressiva. É o
único `index.md` que pode ter frontmatter, exclusivamente para declarar
`okf_version: "0.2"`.

Organize as entradas por categorias que emergirem do conteúdo. Cada entrada
usa link relativo e, quando disponível, a `description` do conceito:

```markdown
# Conceitos

- [Nome](conceitos/nome.md) - Resumo do conceito em uma frase.
```

`index.md` também pode existir em subdiretórios: sem frontmatter, com links
relativos e subdiretórios relevantes listados. Atualize os índices a cada
ingestão que afetar seu escopo. Exceção: `wiki/output/index.md` é apenas
inventário de artefatos e não entra no `wiki/index.md` como conteúdo
conceitual.

### `wiki/log.md`

Histórico de mudanças do bundle, agrupado por data, datas mais recentes
primeiro. Entradas antigas são imutáveis; novas entradas entram no grupo da
data correspondente, sem reescrever o histórico.

```markdown
# Log de atualizações

## 2026-07-23

- **Ingestão**: Adicionado [nome do conceito](/conceitos/nome.md).
- **Consulta**: Incorporada uma comparação durável à wiki.
- **Lint**: Corrigidos links e metadados inconsistentes.
```

Registre consultas apenas quando produzirem alteração durável ou decisão
relevante para a manutenção da wiki.

## Conformidade e evolução

O bundle está conforme com OKF v0.2 quando:

1. cada `.md` não reservado fora de `wiki/output/` tem frontmatter YAML
   parseável;
2. cada frontmatter contém `type` não vazio;
3. cada `index.md` e `log.md` do bundle segue sua estrutura reservada;
4. artefatos gerados estão em pastas `wiki/output/YYYY-MM-DD-<slug>/`, com
   no máximo o inventário `wiki/output/index.md` diretamente na raiz.

Famílias opcionais ausentes, tipos desconhecidos, campos adicionais, links
quebrados e índices ausentes em subdiretórios **não invalidam** o bundle. Um
conceito sem `verified` é consumível, mas tratado como não verificado. Não
acrescente complexidade antes que ela seja necessária: o OKF padroniza o
intercâmbio, não prescreve taxonomia, banco, motor de busca, SDK ou
plataforma.

Se a especificação-alvo mudar, atualize primeiro `okf_version` no índice
raiz e depois o `AGENTS.md` do brain. Em escala moderada, os índices bastam;
se a wiki crescer, uma ferramenta de busca local pode ser adicionada.
