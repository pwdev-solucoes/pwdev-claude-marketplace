# SDD Composy — Desenvolvimento Portátil Orientado a Especificação

> [English version](./README.md)

SDD Composy é um fluxo com portões de aprovação que roda no Claude Code e no Codex a partir de um único pacote portátil. Os dois runtimes usam o mesmo ciclo de vida, schemas, skills, referências, scripts e templates; um fluxo pode mudar de host sem mudar de significado.

Contratos legíveis por pessoas ficam em `tasks/prd-<slug>/`. O estado operacional fica em `.planning/sdd-composy/`. O Markdown gerado para o projeto segue OKF v0.2, exige `type` não vazio e permite campos de extensão desconhecidos. Atualizações suportadas de JSON e Markdown preservam campos desconhecidos.

## Pontos de entrada por runtime

O Claude Code descobre `.claude-plugin/plugin.json` e expõe adaptadores finos de comando como `/sdd-composy:<name>`. O Codex descobre `.codex-plugin/plugin.json` e sua raiz de `skills`, expondo então as skills compartilhadas como `$sdd-composy-<name>`.

Os comandos Claude não contêm política própria de workflow. Eles selecionam a skill portátil correspondente, repassam argumentos e contexto e mapeiam os nomes das ferramentas do host. O núcleo compartilhado continua sendo a autoridade para ciclo de vida, portões, artefatos, transições de estado, segurança e orquestração. Consulte o [contrato de runtime](./references/runtime.md) exato.

## Fluxo

```text
INIT -> MAP -> PRD -> STORIES -> TECHSPEC -> TASKS
                                            |
                              EXECUTE -> QA -> EVIDENCE -> REVIEW -> VERIFY -> COMPLETE
```

Os portões de produto e execução exigem aprovação humana explícita. A verificação reproduz evidência nova. Os caminhos reduzido `QUICK`, delimitado `LOOP` e isolado `FLEET` mantêm os mesmos contratos duráveis e regras de segurança. O lançamento da fleet aceita apenas tarefas prontas, preserva branches recuperáveis, usa cmux para apresentação quando disponível e nunca faz merge automaticamente.

## Independência e segurança

SDD Composy não tem dependência de runtime em `pwdev-flow` nem `pwdev-feat`. Ele nunca presume aprovação, lê segredos ou arquivos de ambiente de frota, nem mescla branches de frota automaticamente. Os contratos completos estão em [`references/`](./references/).

## Licença

Apache-2.0. Consulte [LICENSE](../../LICENSE).
