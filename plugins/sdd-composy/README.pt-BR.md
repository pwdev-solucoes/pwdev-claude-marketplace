# SDD Composy — Desenvolvimento Portátil Orientado a Especificação

> [English version](./README.md)

## Origem e adaptação

Este plugin é um fork da metodologia de Desenvolvimento Orientado a Especificações
implementada por [Rodrigo Branas](https://github.com/rodrigobranas) e
[Pedro Nauck](https://github.com/pedronauck). Ele foi adaptado ao fluxo de trabalho
PWDEV e é destinado ao uso com o [Compozy](https://github.com/compozy/compozy).

## Hermes Agent

O SDD Composy também possui um adaptador explícito para o Hermes Agent. O Hermes registra as
mesmas skills por `.hermes-plugin`, carrega o mapeamento de ferramentas no primeiro turno e usa
`hermes run` para membros da fleet. Não há fallback silencioso para Claude Code ou Codex. A
integração real com Hermes, Kanban e cmux deve ser validada em um ambiente que possua essas ferramentas.

SDD Composy é um fluxo com portões de aprovação que roda no Claude Code e no Codex a partir de um único pacote portátil. Os dois runtimes usam o mesmo ciclo de vida, schemas, skills, referências, scripts e templates; um fluxo pode mudar de host sem mudar de significado.

Contratos legíveis por pessoas ficam em `tasks/prd-<slug>/`. O estado operacional fica em `.planning/sdd-composy/`. O Markdown gerado para o projeto segue OKF v0.2, exige `type` não vazio e permite campos de extensão desconhecidos. Atualizações suportadas de JSON e Markdown preservam campos desconhecidos.

## Idioma dos artefatos

Execute `/sdd-composy:init` com `pt-BR` ou `en-US` para escolher o idioma dos artefatos
legíveis por pessoas. Se o idioma não for informado, o init pergunta qual opção usar e não
cria artefatos até a escolha ser feita. A escolha é persistida em
`.planning/sdd-composy/config.json`; todas as skills seguintes a utilizam sem perguntar
novamente. Antes do init, elas retornam `{"status":"not_initialized","next_action":"run_init"}`.

PRDs, histórias, TechSpecs, descrições de tarefas, relatórios de QA/evidências e textos de
status seguem o idioma escolhido. Chaves de máquina, IDs, schemas, nomes de arquivos,
valores de ciclo de vida e nomes de comandos permanecem em inglês, preservando a
compatibilidade entre Claude Code e Codex. Valores de idioma inválidos falham sem alterar a
configuração existente. Consulte o [contrato completo de idioma e fluxo](./references/workflow.md).

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
