# Catálogo de regras de LINT — pwdev-brain

Regras que o subagente `brain-linter` valida. Escopo: arquivos `.md` de
`wiki/` fora de `wiki/output/`, mais as checagens estruturais de `raw/` e
`wiki/output/`. Formato de finding no relatório:

```
[BR-nnn] {{erro|aviso|info}} · {{arquivo:linha}} · {{descrição}} · auto-fixável: {{sim|não}} · fix: {{proposta ou —}}
```

Ranqueamento no relatório: erro → aviso → info; dentro do nível, por regra.

## Conformidade dura (erro — bundle inválido segundo OKF v0.2)

| Regra | Verifica | Auto-fixável |
|---|---|---|
| BR-001 | Documento de conceito sem frontmatter YAML parseável | não — exige interpretação do conteúdo |
| BR-002 | Frontmatter sem `type` ou com `type` vazio | sim, quando o tipo é inferível com alta confiança; senão não |
| BR-003 | `wiki/index.md` com frontmatter além de `okf_version: "0.2"` | sim — mover metadados excedentes para fora ou remover |
| BR-004 | `index.md` de subdiretório com frontmatter | sim — remover frontmatter |
| BR-005 | `log.md` fora da estrutura reservada (sem grupos de data, datas fora de ordem desc, histórico reescrito) | não — histórico é imutável; reportar apenas |
| BR-006 | Artefato gerado (HTML, CSS, JS, imagem, PDF, planilha, export) fora de `wiki/output/` — em `wiki/`, subdiretórios de conceito ou raiz do brain | sim — mover para pasta datada nova em `wiki/output/` |
| BR-007 | Arquivo direto na raiz de `wiki/output/` além do eventual `index.md`, ou pasta que não segue `YYYY-MM-DD-<slug>/` | sim — mover/renomear para pasta datada |

## Convenções de metadados (aviso)

| Regra | Verifica | Auto-fixável |
|---|---|---|
| BR-101 | `generated.at` ou `verified[].at` fora de ISO 8601 | sim, quando a data é inequívoca |
| BR-102 | Ator (`generated.by`, `verified[].by`, `sources[].author`) sem prefixo `human:`, `process:` nem forma `<producer>/<version>` | sim, quando o ator é conhecido do contexto |
| BR-103 | `status` com valor fora de `draft` \| `stable` \| `deprecated` | sim, quando o mapeamento é óbvio |
| BR-104 | `stale_after` fora do formato `YYYY-MM-DD` | sim, quando inequívoco |
| BR-105 | Entrada de `sources` sem `resource` | não — exige localizar a fonte |
| BR-106 | `description` ausente ou com mais de uma frase | sim — sintetizar em uma frase |
| BR-107 | `tags` que não é lista YAML de strings curtas | sim |
| BR-108 | Lista genérica `# Citations` usada como convenção primária (legado v0.1) | sim — converter para `sources` + footnotes |

## Integridade de links e citações (aviso)

| Regra | Verifica | Auto-fixável |
|---|---|---|
| BR-201 | Nota de rodapé de atribuição que não resolve para um `sources[].id` | não — exige decidir a fonte correta |
| BR-202 | Link interno quebrado (alvo inexistente no bundle) | sim, quando o alvo foi renomeado e é rastreável; senão não |
| BR-203 | Conceito órfão — sem nenhum link de entrada e fora do `wiki/index.md` | sim — adicionar entrada no índice |
| BR-204 | Conceito ausente do `wiki/index.md` (ou do `index.md` do seu subdiretório) | sim — adicionar entrada com a `description` |
| BR-205 | Entrada de índice apontando para arquivo inexistente | sim — remover ou corrigir o caminho |
| BR-206 | `wiki/output/index.md` apontando para caminhos antigos ou arquivos soltos, ou links entre artefato e auxiliares da mesma pasta que não resolvem | sim — atualizar caminhos |
| BR-207 | Arquivo de `wiki/output/` tratado como conceito (com frontmatter exigido ou listado no `wiki/index.md`) | sim — remover do índice OKF |

## Ciclo de vida e saúde do conhecimento (info)

| Regra | Verifica | Auto-fixável |
|---|---|---|
| BR-301 | `stale_after` vencido (data atual ≥ valor) | não — vira recomendação de re-ingestão/revisão |
| BR-302 | Contradição entre páginas (heurística: afirmações incompatíveis sobre a mesma entidade) | não — vira recomendação; contradição nunca se auto-resolve |
| BR-303 | Afirmação antiga superada por fonte mais recente já ingerida | não — recomendação de atualização |
| BR-304 | Conceito importante mencionado repetidamente sem página própria | não — recomendação de criação |
| BR-305 | Relação por link sem contexto no texto ao redor | sim — pedir uma frase de contexto na correção |
| BR-306 | Lacuna que poderia ser preenchida por nova fonte ou pesquisa | não — sugestão de ingest |

## Regras de aplicação de fix

- MODE `fix` toca **exclusivamente** arquivos citados em findings aprovados.
- `--fix` direto (sem revisão) aplica só findings `sim` de nível **aviso**
  ou os BR-2xx/BR-00x marcados como triviais — nunca BR-3xx.
- Toda correção aplicada gera entrada `**Lint**:` no grupo da data em
  `wiki/log.md`.
- `raw/` jamais é tocado, nem por fix aprovado.
