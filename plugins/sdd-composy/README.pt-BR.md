# SDD Composy — Desenvolvimento Portátil Orientado a Especificação

> [English version](./README.md)

## Origem e adaptação

Este plugin é um fork da metodologia de Desenvolvimento Orientado a Especificações
implementada por [Rodrigo Branas](https://github.com/rodrigobranas) e
[Pedro Nauck](https://github.com/pedronauck). Ele foi adaptado ao fluxo de trabalho
PWDEV e é destinado ao uso com o [Compozy](https://github.com/compozy/compozy).

SDD Composy é um fluxo com portões de aprovação empacotado para Claude Code, Codex e Hermes
Agent. Os três runtimes usam o mesmo ciclo de vida, schemas, skills, referências, scripts e
templates; um fluxo pode mudar de host sem mudar de significado. Suporte empacotado e testes
offline dos adaptadores não equivalem à aceitação com providers reais. A aceitação real dos
três runtimes depende do harness de aceitação; execuções indisponíveis, não autorizadas ou sem
orçamento devem ser registradas como `BLOCKED` ou `NOT_RUN`, nunca como `PASS`.

Contratos legíveis por pessoas ficam em `tasks/prd-<slug>/`. O estado operacional fica em
`.planning/sdd-composy/`. O Markdown gerado segue OKF v0.2, exige `type` não vazio e permite
campos de extensão desconhecidos. Atualizações suportadas de JSON e Markdown preservam campos
desconhecidos.

## Idioma dos artefatos

Execute `/sdd-composy:init` com `pt-BR` ou `en-US` para escolher o idioma dos artefatos
legíveis por pessoas. Se o idioma não for informado, o init pergunta qual opção usar e não
cria artefatos até a escolha. Ela é persistida em `.planning/sdd-composy/config.json`; todas as
skills seguintes a utilizam sem perguntar novamente. Antes do init, elas retornam
`{"status":"not_initialized","next_action":"run_init"}`.

PRDs, histórias, TechSpecs, descrições de tarefas, relatórios de QA/evidências e textos de
status seguem o idioma escolhido. Chaves de máquina, IDs, schemas, nomes de arquivos, valores
de ciclo de vida, nomes de comandos e evidências do usuário permanecem inalterados. Valores de
idioma inválidos falham sem alterar a configuração. Consulte o
[contrato completo de idioma e fluxo](./references/workflow.md).

## Pontos de entrada por runtime

O Claude Code descobre `.claude-plugin/plugin.json` e expõe adaptadores finos como
`/sdd-composy:<name>`. O Codex descobre `.codex-plugin/plugin.json` e sua raiz de `skills`,
expondo as skills compartilhadas como `$sdd-composy-<name>`. O Hermes descobre
`.hermes-plugin/plugin.yaml`; o bootstrap registra as mesmas skills e carrega o mapeamento de
ferramentas documentado no primeiro turno.

A automação Hermes de LOOP/fleet usa `hermes -z <prompt> --in <worktree>` somente após
comprovar isolamento independente ou obter consentimento específico do usuário. Não existe
fallback para Claude Code ou Codex. A integração Kanban do Hermes não está implementada e está
indisponível nesta versão. O núcleo compartilhado permanece como autoridade para ciclo de vida,
portões, artefatos, transições de estado, segurança e orquestração. Consulte o
[contrato de runtime](./references/runtime.md).

## Fluxo

```text
INIT -> MAP -> PRD -> STORIES -> TECHSPEC -> TASKS
                                            |
                              EXECUTE -> QA -> EVIDENCE -> REVIEW -> VERIFY -> COMPLETE
```

Os portões de produto e execução exigem aprovação humana explícita; editar o JSON operacional
não simula aprovação. A verificação reproduz evidência nova. Os caminhos reduzido `QUICK`,
delimitado `LOOP` e isolado `FLEET` mantêm os mesmos contratos duráveis e regras de segurança.
O lançamento da fleet aceita apenas tarefas prontas, cria uma branch própria e uma Git worktree
independente por membro, pode iniciar o provider selecionado via cmux, tmux ou modo headless e
nunca faz merge automaticamente. Com `--compose`, o arquivo central
`.planning/sdd-composy/fleet/<fleet-id>/docker-compose.yml` é iniciado uma vez para a fleet.
Cada membro registra esse caminho relativo ao repositório, seu digest SHA-256, o projeto exato
`sdd_fleet_<fleet-id>` e `compose_allocated: true` em `resources`. Sem `--compose`,
`compose_allocated` é `false` e o teardown não executa ação Compose. O teardown aceita somente
essa identidade central validada; falha de limpeza preserva o estado de recuperação.

## Estado, compatibilidade e recuperação

A intenção humana e os registros de aprovação ficam no Markdown em `tasks/prd-<slug>/`; o JSON
validado em `.planning/sdd-composy/` é a autoridade do estado operacional atual. Bundles
operacionais de tarefas são objetos com um array `tasks`, não objetos de tarefa planos. A
sincronização relata divergência Markdown/JSON e exige escolha explícita de autoridade. O
schema v1 legado de membro de fleet é diagnosticado e recusado durante a execução normal;
registros elegíveis são migrados explicitamente com
`scripts/fleet/run.sh --migrate-member MEMBER.json --root ROOT`.

O init nunca substitui uma `.claude` existente. Um link compatível `.claude -> .agents` é
reportado como `claude_compatibility: "symlink"`; um diretório real existente é preservado e
recebe o arquivo regular de ponte `.claude/AGENTS.md`, sendo reportado como
`"existing_directory"`. Outros links ou colisões são conflitos. A inspeção de status é
read-only: ela não cria nem modifica arquivos do projeto. Logs nativos do provider, quando um
provider é invocado fora dessa inspeção, são contabilizados separadamente dessa garantia.
Consulte [status](./references/status.md), [fleet](./references/fleet.md) e o
[contrato de runtime](./references/runtime.md).

## Independência e segurança

SDD Composy não tem dependência de runtime em `pwdev-flow` nem `pwdev-feat`. Ele nunca presume
aprovação, lê segredos ou arquivos de ambiente de frota, nem mescla branches de frota
automaticamente. Os contratos completos estão em [`references/`](./references/).

## Licença

Apache-2.0. Consulte [LICENSE](../../LICENSE).
