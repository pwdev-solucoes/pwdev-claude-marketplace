# SDD Composy — Desenvolvimento Portátil Orientado a Especificação

> [English version](./README.md)

## Origem e adaptação

Este plugin é um fork da metodologia de Desenvolvimento Orientado a Especificações
implementada por [Rodrigo Branas](https://github.com/rodrigobranas) e
[Pedro Nauck](https://github.com/pedronauck). Ele foi adaptado ao fluxo de trabalho
PWDEV e é destinado ao uso com o [Compozy](https://github.com/compozy/compozy).

SDD Composy é um fluxo com portões de aprovação empacotado para Claude Code, Codex, Hermes
Agent e OpenCode. Os quatro runtimes usam o mesmo ciclo de vida, schemas, skills, referências,
scripts e templates; um fluxo pode mudar de host sem mudar de significado. Suporte empacotado e
testes offline dos adaptadores não equivalem à aceitação com providers reais: execuções
indisponíveis, não autorizadas ou sem orçamento devem ser registradas como `BLOCKED` ou
`NOT_RUN`, nunca como `PASS`.

Contratos legíveis por pessoas ficam em `tasks/prd-<slug>/`. O estado operacional fica em
`.planning/sdd-composy/`. O Markdown gerado segue OKF v0.2, exige `type` não vazio e permite
campos de extensão desconhecidos. Atualizações suportadas de JSON e Markdown preservam campos
desconhecidos.

## Configuração e idioma dos artefatos

Execute `/sdd-composy:init` (ou o equivalente abaixo) antes de gerar qualquer artefato,
informando `pt-BR` ou `en-US` para escolher o idioma dos artefatos legíveis por pessoas. Se o
idioma não for informado, o init pergunta qual opção usar e não cria artefatos até a escolha. A
escolha é persistida em `.planning/sdd-composy/config.json`; todas as skills seguintes a usam
sem perguntar novamente e, antes do init, retornam
`{"status":"not_initialized","next_action":"run_init"}`.

PRDs, histórias, TechSpecs, descrições de tarefas, relatórios de QA/evidências e textos de
status seguem o idioma escolhido. Chaves de máquina, IDs, schemas, nomes de arquivos, valores
de ciclo de vida, nomes de comandos e evidências do usuário permanecem inalterados. Valores de
idioma inválidos falham sem alterar a configuração. Consulte o
[contrato de idioma](./references/language.md).

## Pontos de entrada por runtime

| Runtime | Descoberta | Invocação |
| --- | --- | --- |
| Claude Code | `.claude-plugin/plugin.json` | comandos finos `/sdd-composy:<name>` |
| Codex | `.codex-plugin/plugin.json` (raiz `skills`) | `$sdd-<name>` — o `name` da skill |
| Hermes Agent | `.hermes-plugin/plugin.yaml`; o bootstrap registra as 17 skills | `skill_view("sdd-<name>")` |
| OpenCode | pastas de skill linkadas (abaixo) | comandos `/sdd-<name>` ou a ferramenta nativa `skill` |

O **OpenCode** não tem mecanismo de plugin para skills: ele descobre pastas com `SKILL.md`
([opencode.ai/docs/skills](https://opencode.ai/docs/skills)) e comandos customizados ao lado
delas. O instalador incluído linka as 17 skills e gera os 17 comandos `/sdd-<name>`, globalmente
(`~/.config/opencode/{skills,command}`) ou em um projeto:

```bash
python3 plugins/sdd-composy/.opencode-plugin/install.py              # global
python3 plugins/sdd-composy/.opencode-plugin/install.py --project .  # só este projeto
python3 plugins/sdd-composy/.opencode-plugin/install.py --uninstall  # remove o que instalou
```

Ele linka, nunca copia: `scripts/`, `references/` e `templates/` são alcançados pelo link. Uma
instalação como *plugin* do Claude Code fica no cache de plugins do Claude e não torna as skills
visíveis ao OpenCode; o instalador torna. `LOOP` e `FLEET` rodam no OpenCode por adaptadores
dedicados (`scripts/loop-engine-opencode.py`, `scripts/fleet/engine-opencode.sh`) com o vetor
`opencode run --dir <worktree> --format json [--auto]`; veja [opencode-tools.md](./references/opencode-tools.md).
Testes offline de adaptador estabelecem suporte, não aceitação real de provider.

A automação Hermes de LOOP/fleet usa `hermes -z <prompt> --in <worktree>` somente após
comprovar isolamento independente ou obter consentimento específico do usuário. Nenhum adaptador
faz fallback para outro provider, e a integração Kanban do Hermes não está implementada. O
núcleo compartilhado permanece como autoridade para portões do ciclo de vida, artefatos,
transições de estado, segurança e orquestração. Consulte o
[contrato de runtime](./references/runtime.md).

## Comandos

| Claude Code | Codex / OpenCode | Atende |
| --- | --- | --- |
| `/sdd-composy:init` | `$sdd-init` / `/sdd-init` | INIT — workspace, governança, idioma |
| `/sdd-composy:map` | `$sdd-map` / `/sdd-map` | MAP — evidência do código, somente leitura |
| `/sdd-composy:prd` | `$sdd-prd` / `/sdd-prd` | PRD — contrato humano de produto |
| `/sdd-composy:stories` | `$sdd-stories` / `/sdd-stories` | STORIES — a partir de um PRD aprovado |
| `/sdd-composy:techspec` | `$sdd-techspec` / `/sdd-techspec` | TECHSPEC — a partir de contratos aprovados |
| `/sdd-composy:tasks` | `$sdd-tasks` / `/sdd-tasks` | TASKS — importar, inspecionar, avançar |
| `/sdd-composy:execute` | `$sdd-execute` / `/sdd-execute` | EXECUTE — uma tarefa em `ready` |
| `/sdd-composy:qa` | `$sdd-qa` / `/sdd-qa` | QA — tarefa em `qa_required` |
| `/sdd-composy:evidence` | `$sdd-evidence` / `/sdd-evidence` | EVIDENCE — tarefa em `evidence_required` |
| `/sdd-composy:review` | `$sdd-review` / `/sdd-review` | REVIEW — tarefa em `review_required` |
| `/sdd-composy:verify` | `$sdd-verify` / `/sdd-verify` | VERIFY — tarefa em `verify_required` |
| `/sdd-composy:quick` | `$sdd-quick` / `/sdd-quick` | QUICK — mudança delimitada, no máximo cinco arquivos |
| `/sdd-composy:loop` | `$sdd-loop` / `/sdd-loop` | LOOP — correção delimitada de uma tarefa |
| `/sdd-composy:fleet` | `$sdd-fleet` / `/sdd-fleet` | FLEET — worktrees isoladas para tarefas prontas |
| `/sdd-composy:sync` | `$sdd-sync` / `/sdd-sync` | Sincronização Markdown/JSON das tarefas |
| `/sdd-composy:status` | `$sdd-status` / `/sdd-status` | Status consolidado, somente leitura |
| `/sdd-composy:trace` | `$sdd-trace` / `/sdd-trace` | Trace semântico append-only |

## Fluxo

```text
INIT -> MAP -> PRD -> STORIES -> TECHSPEC -> TASKS
                                            |
                              EXECUTE -> QA -> EVIDENCE -> REVIEW -> VERIFY -> COMPLETE
```

Os portões de produto e execução exigem aprovação humana explícita; editar o JSON operacional
não simula aprovação. A verificação reproduz evidência nova. Os caminhos reduzido `QUICK`,
delimitado `LOOP` e isolado `FLEET` mantêm os mesmos contratos duráveis e regras de segurança.
Uma fleet executa apenas tarefas prontas, cada uma em sua própria branch e Git worktree, e nunca
faz merge automaticamente; as regras de alocação Compose, teardown e migração estão no
[contrato de fleet](./references/fleet.md).

## Estado, compatibilidade e recuperação

A intenção humana e os registros de aprovação ficam no Markdown em `tasks/prd-<slug>/`; o JSON
validado em `.planning/sdd-composy/` é a autoridade do estado operacional atual, e a
sincronização exige escolha explícita de autoridade quando eles divergem. A inspeção de status é
somente leitura, e o init nunca substitui uma `.claude` existente. Consulte
[status](./references/status.md) e o [contrato de runtime](./references/runtime.md).

## Independência e segurança

SDD Composy não tem dependência de runtime em `pwdev-flow` nem `pwdev-feat`. Ele nunca presume
aprovação, lê segredos ou arquivos de ambiente de fleet, nem mescla branches de fleet
automaticamente. Não pule os portões de aprovação, QA, evidência ou verificação. Os contratos
completos estão em [`references/`](./references/).

## Licença

Apache-2.0. Consulte [LICENSE](../../LICENSE).
