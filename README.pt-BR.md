# PWDEV Marketplace

*Read in [English](./README.md).*

Marketplace de plugins para Claude Code, Codex e runtimes PWDEV compatíveis.

## Instalação

```bash
claude plugin marketplace add /caminho/para/pwdev-claude-marketplace
claude plugin install <plugin>@pwdev-claude-marketplace
```

Reinicie o runtime após a instalação. Consulte o README de cada plugin para setup e permissões.

## Escolha por objetivo

| Objetivo | Plugins |
|---|---|
| Desenvolvimento orientado a especificações | [pwdev-power](./plugins/pwdev-power/), [pwdev-flow](./plugins/pwdev-flow/), [sdd-composy](./plugins/sdd-composy/) |
| Código e delegação | [pwdev-code](./plugins/pwdev-code/), [pwdev-feat](./plugins/pwdev-feat/), [pwdev-hermes-orca](./plugins/pwdev-hermes-orca/) |
| Requisitos e UI/UX | [pwdev-prd](./plugins/pwdev-prd/), [pwdev-uiux](./plugins/pwdev-uiux/) |
| Garantia de qualidade | [pwdev-qa](./plugins/pwdev-qa/) |
| Engenharia de skills | [pwdev-skills](./plugins/pwdev-skills/) |
| Copy e conteúdo social | [pwdev-copy](./plugins/pwdev-copy/), [pwdev-social-media](./plugins/pwdev-social-media/) |
| Mídia: modelos, provedores, custo e edição de vídeo | [pwdev-media](./plugins/pwdev-media/), [pwdev-video-hyperframes](./plugins/pwdev-video-hyperframes/), [pwdev-video-remotion](./plugins/pwdev-video-remotion/) |
| Planejamento visual | [pwdev-excalidraw](./plugins/pwdev-excalidraw/) |
| Sites de documentação | [pwdev-fumadocs](./plugins/pwdev-fumadocs/) |
| DevOps e operações | [pwdev-devops](./plugins/pwdev-devops/) |
| Conhecimento e integrações | [pwdev-brain](./plugins/pwdev-brain/), [pwdev-github](./plugins/pwdev-github/), [pwdev-glpi](./plugins/pwdev-glpi/), [pwdev-obsidian](./plugins/pwdev-obsidian/), [pwdev-postgres](./plugins/pwdev-postgres/), [pwdev-youtrack](./plugins/pwdev-youtrack/) |
| Suporte ao terminal | [pwdev-statusline](./plugins/pwdev-statusline/), [pwdev-mods](./plugins/pwdev-mods/) |

### PWDEV Flow — runtime duplo

O `pwdev-flow` é o fluxo PWDEV portátil para Claude Code e Codex. As mesmas
skills com aprovação e artefatos `.planning/flow` funcionam nos dois runtimes;
as frotas isoladas selecionam um engine nativo explícito (`claude` ou `codex`) e
mantêm separados os vetores de execução privilegiada.

Membros Claude executam por `claude -p`; membros Codex executam por
`codex exec`, sem fallback entre runtimes.

Comandos: `/pwdev-flow:init`, `/pwdev-flow:discover`, `/pwdev-flow:design`,
`/pwdev-flow:plan`, `/pwdev-flow:execute`, `/pwdev-flow:review`,
`/pwdev-flow:verify`, `/pwdev-flow:simplify`, `/pwdev-flow:quick`,
`/pwdev-flow:product`, `/pwdev-flow:memory`, `/pwdev-flow:health`,
`/pwdev-flow:audit`, `/pwdev-flow:maintenance`, `/pwdev-flow:compat`,
`/pwdev-flow:delegate`, `/pwdev-flow:fleet`.

---

## Plugins

| Plugin | Descrição | Versão | Licença |
|--------|-----------|:------:|:------:|
| [**pwdev-flow**](./plugins/pwdev-flow/) | Desenvolvimento orientado a especificação portátil para Claude Code **e** Codex — um único contrato `.planning/flow`, 17 comandos, auditoria semântica opt-in, delegação guardada a CLIs externas, frotas nativas isoladas (`claude -p` / `codex exec`) | 0.6.0 | Apache-2.0 |
| [**sdd-composy**](./plugins/sdd-composy/) | Desenvolvimento orientado a especificação portátil para Claude Code, Codex, Hermes e OpenCode — contratos compartilhados, estado durável, artefatos OKF v0.2, rastreabilidade, loops delimitados e frotas isoladas | 0.1.0 | Apache-2.0 |
| [**pwdev-power**](./plugins/pwdev-power/) | Desenvolvimento orientado a especificação com disciplina, para Claude Code, Codex **e** Hermes Agent — portão de brainstorm, planos com restrições literais, execução dirigida por subagentes com registro e ciclo de correção limitado, verificação adversarial, mapa do codebase, frotas isoladas no cmux como painel visual ou sozinhas | 0.2.0 | Apache-2.0 |
| [**pwdev-code**](./plugins/pwdev-code/) | Desenvolvimento orientado a especificação — 8 subagentes reais (incl. advisor), roteamento por task, grafo de memória, waves paralelas opt-in, delegação a CLIs externas (Codex/OpenCode/Kimi/Gemini/Kiro), 23 comandos | 2.4.0 | Apache-2.0 |
| [**pwdev-uiux**](./plugins/pwdev-uiux/) | Engenharia UI/UX — 6 subagentes reais, fluxo de 5 fases com gates, Figma, WCAG 2.1 AA | 2.0.1 | Apache-2.0 |
| [**pwdev-feat**](./plugins/pwdev-feat/) | Desenvolvimento rápido de features para Claude Code, Codex, Hermes e OpenCode — mapa do código com evidência, planos PWDEVIA com critérios rastreáveis, executor com retomada, reviews com regra citada, cenários E2E para Playwright, loop de issue do GitHub até o PR | 3.2.1 | Apache-2.0 |
| [**pwdev-hermes-orca**](./plugins/pwdev-hermes-orca/) | Hermes Agent como coordenador do Orca — issues do GitHub num DAG aprovado pelo usuário, um worker supervisionado do Orca por issue rodando o `feat-loop` do pwdev-feat (plan → exec → review → PR), gates dos workers respondidos via `orca ask`, relatório por issue; nunca faz merge | 0.1.1 | Apache-2.0 |
| [**pwdev-prd**](./plugins/pwdev-prd/) | PRDs guiados por entrevista para Claude Code, Codex, Hermes Agent e OpenCode — 12 etapas inline, gate de aprovação, roadmap com cadeia de dependências (ondas, caminho crítico), publicação no GitHub | 3.0.0 | Apache-2.0 |
| [**pwdev-qa**](./plugins/pwdev-qa/) | Garantia de qualidade portátil para Claude Code, Codex e Hermes Agent — 10 fluxos, 17 guias especialistas, recomendação de ferramentas, evidência auditável, relatórios offline em HTML e PDF | 0.1.0 | Apache-2.0 |
| [**pwdev-skills**](./plugins/pwdev-skills/) | Engenharia de skills para Claude Code, Codex e Hermes Agent — revisão e refatoração de skills, perfis lean/guided por medição, descoberta de runtimes e modelos, benchmark A/B headless objetivo em Claude Code, Codex, Hermes e OpenCode | 0.1.0 | Apache-2.0 |
| [**pwdev-copy**](./plugins/pwdev-copy/) | Framework de copywriting treinável — 20 skills no ciclo completo (VOC → copy → revisão → análise), 5 subagentes reais | 1.1.0 | Apache-2.0 |
| [**pwdev-social-media**](./plugins/pwdev-social-media/) | Geração de criativos por IA — orquestração de APIs (Ideogram, Leonardo, Flux, Runway, Freepik) com trava de gasto, 19 skills, 4 subagentes | 2.0.1 | Apache-2.0 |
| [**pwdev-devops**](./plugins/pwdev-devops/) | Plataforma, operação e incidente — postura de execução segura com guard script, 24 skills, 4 subagentes | 1.0.0 | Apache-2.0 |
| [**pwdev-youtrack**](./plugins/pwdev-youtrack/) | Gestão do YouTrack — MCP oficial embutido (2025.3+) para issues, artigos e log de trabalho; fallback REST para boards, sprints e relatórios de tempo | 1.0.0 | Apache-2.0 |
| [**pwdev-github**](./plugins/pwdev-github/) | GitHub Projects para Claude Code, Codex, Hermes Agent e OpenCode — templates personalizáveis, publicação idempotente de roadmaps (issues, sub-issues, milestones, blocked-by nativo) e skill para criar, atualizar e fechar issues e tarefas de Project, via gh CLI | 0.1.0 | Apache-2.0 |
| [**pwdev-glpi**](./plugins/pwdev-glpi/) | GLPI 10/11 ITSM multi-runtime para Claude Code, Codex e Hermes — servidor MCP próprio via npx (@soarescbm/mcp-glpi): CRUD de tickets, triagem com prompts MCP, relatórios de fila, ativos e KB | 1.2.0 | Apache-2.0 |
| [**pwdev-postgres**](./plugins/pwdev-postgres/) | PostgreSQL — servidor MCP próprio via npx (@soarescbm/postgres-mcp): SELECT somente-leitura validado por AST, inspeção de schema, DML/DDL com dry-run obrigatório | 1.0.0 | Apache-2.0 |
| [**pwdev-obsidian**](./plugins/pwdev-obsidian/) | Vault do Obsidian — servidor MCP embutido no plugin comunitário Local REST API: leitura, escrita e edição estrutural de notas (heading/bloco/frontmatter), busca JsonLogic e texto livre, tags, arquivo ativo, paleta de comandos | 1.0.0 | Apache-2.0 |
| [**pwdev-brain**](./plugins/pwdev-brain/) | Segundo cérebro em LLM Wiki (padrão Karpathy) no Open Knowledge Format v0.2 — ingest discutido com citação por afirmação, query citada, lint de conformidade; 2 subagentes, MCP embutido somente-leitura (6 tools) | 1.1.0 | Apache-2.0 |
| [**pwdev-excalidraw**](./plugins/pwdev-excalidraw/) | Planejamento visual com diagramas Excalidraw via servidor MCP oficial — arquitetura, fluxos, dependências, decisões e roadmaps editáveis | 0.2.0 | Apache-2.0 |
| [**pwdev-fumadocs**](./plugins/pwdev-fumadocs/) | Sites de documentação Fumadocs para Claude Code, Codex, Hermes Agent e OpenCode — documentação oficial ao vivo pelo servidor MCP do Fumadocs, instalação, conteúdo MDX e navegação, features via @fumadocs/cli, scanner determinístico do projeto, verificação por type-check e build | 0.1.0 | Apache-2.0 |
| [**pwdev-media**](./plugins/pwdev-media/) | Núcleo da suíte de mídia para Claude Code, Codex e Hermes Agent — catálogo de modelos e apps de IA em 14 categorias com rotina de atualização, geração por OpenRouter, fal e ElevenLabs com estimativa e confirmação, chaves no Keychain, orçamento mensal, ledger, formatos de criativos com zonas seguras | 0.3.0 | Apache-2.0 |
| [**pwdev-video-hyperframes**](./plugins/pwdev-video-hyperframes/) | Edição de vídeo falado por conversa com HyperFrames para Claude Code, Codex e Hermes Agent — corte pela onda (sem respiros, última tomada certa), legendas por palavra, zooms, textos na zona segura, cenas sob medida com as skills oficiais do HyperFrames, trilha e efeitos, amostra no estúdio e render com portão de qualidade | 0.1.0 | Apache-2.0 |
| [**pwdev-video-remotion**](./plugins/pwdev-video-remotion/) | Edição de vídeo falado por conversa com Remotion (React) para Claude Code, Codex e Hermes Agent — mesmo fluxo e mesmo projeto.json do pwdev-video-hyperframes: corte pela onda, legendas por palavra, zooms, cenas em React, trilha, Remotion Studio, render com portão de qualidade e checagem da licença do Remotion | 0.1.0 | Apache-2.0 |
| [**pwdev-statusline**](./plugins/pwdev-statusline/) | Barra de status rica — cores dinâmicas, tokens formatados, totalmente configurável | 1.1.0 | Apache-2.0 |
| [**pwdev-mods**](./plugins/pwdev-mods/) | Mod do Claude Code — painel de gestão de subagentes (monitorar, parar, disparar), tokens, custo e histórico diário | 0.1.0 | Apache-2.0 |

### pwdev-power

Desenvolvimento com disciplina rodando em **três runtimes** — Claude Code, Codex
e Hermes Agent — a partir de um só conjunto de skills, com frotas autônomas
isoladas no **cmux**.

```
[MAPA] ─▶ PRD ─▶ ROADMAP ─▶ BRAINSTORM ─▶ PLANO ─▶ EXECUÇÃO ─▶ VERIFICAÇÃO ─▶ FECHO
```

Ele junta uma camada de produto — um requisito e, depois, um roadmap
`Fase → Épico → Feature → Task` com rastreabilidade obrigatória — com execução
dirigida por subagentes: registro durável, um brief por task, um revisor novo
entre tasks, e ciclo de correção limitado a cinco rodadas, com cada decisão de
arbitragem gravada como ruling.

Três regras valem o tempo todo, cada uma escrita contra a racionalização que a
derruba: **nenhum código de produção sem um teste visto falhando**, **nenhuma
correção sem causa raiz antes** e **nenhuma afirmação de sucesso sem rodar o
comando e ler a saída**. A verificação é adversarial — o verificador é instruído
a *refutar* a conclusão, não a confirmá-la.

O `init` mapeia o codebase em quatro documentos de contexto, para que um design
não redescubra a arquitetura a cada fase. O comando privilegiado do provider
existe em exatamente um adaptador por runtime; o runtime é fixado pelo launcher
escolhido antes de qualquer mutação, e um runner cujo adaptador discorda recusa
iniciar. Com o Hermes disponível, fases aprovadas também podem ser despachadas
pelo Kanban dele.

As frotas são como várias fases aprovadas rodam ao mesmo tempo, e como você
acompanha é a escolha. O `/pwdev-power:fleet` abre por padrão um **painel visual
no cmux** — um pane por fase, cada um uma sessão interativa no próprio worktree
já lendo o spec e o plano daquela fase, de um a quatro membros, um painel por
vez. Com `--auto` roda a frota não supervisionada, que conduz sozinha
`plano → execução → revisão → verificação` e reporta pela sidebar. Assistir não
é aprovar: os dois vetores rodam com permissões contornadas, então os dois
exigem que você reconheça a flag perigosa antes de qualquer lançamento. Um
membro que parou no meio retoma com `--resume`, reexecutando a etapa que o
status do runner registra em vez de recomeçar — e essa flag é também a única
coisa que pode reiniciar um membro parado em `NEEDS_HUMAN`.

**Subagentes:** mapper, roadmap, implementer, task-reviewer, verifier

**Inclui:** 7 comandos · 5 subagentes · 16 skills · hooks

Veja a [documentação completa do plugin](./plugins/pwdev-power/README.pt-BR.md).

### pwdev-flow

Desenvolvimento portátil com aprovação em portões, rodando nativamente **tanto
no Claude Code quanto no Codex** a partir de um único pacote. Os contratos do
fluxo ficam em skills e references neutras de runtime; cada host recebe um
adaptador fino.

```
DISCOVER ─▶ DESIGN ─▶ PLAN ─▶ EXECUTE ─▶ [SIMPLIFY] ─▶ REVIEW ─▶ VERIFY
```

Um fluxo iniciado em um runtime pode continuar no outro: os dois leem e escrevem
os mesmos artefatos `.planning/flow`. As frotas autônomas rodam fases aprovadas
em worktrees Git isolados, com stack Docker e painel tmux próprios, conduzidas
pela CLI headless do próprio runtime — `claude -p` ou `codex exec`. Os dois
vetores privilegiados são construídos em adaptadores separados e nunca podem se
transformar um no outro.

**Sem subagentes, sem hooks, sem servidores MCP**, por decisão de projeto: a
trilha de auditoria é um log JSONL semântico e opt-in, gravado só depois que a
ação realmente aconteceu, para continuar significativo nos dois hosts em vez de
virar telemetria específica de um deles.

**Inclui:** 17 comandos · 17 skills · sem subagentes, sem hooks, sem MCP

Veja a [documentação completa do plugin](./plugins/pwdev-flow/README.pt-BR.md).

### sdd-composy

Desenvolvimento orientado a especificação portátil para Claude Code e Codex a partir
de um conjunto compartilhado de contratos. Mantém contratos humanos em
`tasks/prd-<slug>/`, estado operacional em `.planning/sdd-composy/` e Markdown
gerado alinhado ao OKF v0.2.

```
INIT ─▶ MAPA ─▶ PRD ─▶ HISTÓRIAS ─▶ TECHSPEC ─▶ TASKS ─▶ EXECUÇÃO ─▶ QA ─▶ EVIDÊNCIA ─▶ REVISÃO ─▶ VERIFICAÇÃO
```

**Inclui:** 17 comandos · 17 skills · sem subagentes · sem MCP

Veja a [documentação completa do plugin](./plugins/sdd-composy/README.pt-BR.md).

### pwdev-code

Desenvolvimento orientado a especificação com **orquestração híbrida**: fases
interativas rodam na conversa principal; o trabalho pesado é delegado a
**8 subagentes reais** em **6 fases** com loops de correção e um **grafo de
memória curada do projeto**.

```
PRD ─▶ ROADMAP ─▶ DISCOVER ─▶ DESIGN ─▶ PLAN ─▶ EXECUTE ─▶ [SIMPLIFY] ─▶ REVIEW ─▶ VERIFY
```

**Subagentes:** executor, advisor, simplifier, code-reviewer, qa, verifier adversarial, researcher, roadmap
**Personas inline:** interviewer, architect, planner, product manager, quick engineer

**Inclui:** 23 comandos · 8 subagentes · 2 skills · hooks

Veja a [documentação completa do plugin](./plugins/pwdev-code/README.md).

### pwdev-uiux

Engenharia UI/UX agnóstica de stack: **6 subagentes reais + 2 personas
inline** em um fluxo de 5 fases com gates humanos.

```
UNDERSTAND ─▶ STRUCTURE ─▶ IMPLEMENT ─▶ REVIEW ─▶ HANDOFF
```

**Subagentes:** UX Analyst, Design Bridge, UI Scanner, UI Builder, A11y Reviewer, UX Critic
**Personas inline:** Orchestrator (gates), Theme Builder (entrevista de marca)

**Principais funcionalidades:** integração com Figma MCP, auditoria WCAG 2.1 AA, revisão UX em 7 eixos, habilidades contextuais específicas por projeto

**Inclui:** 13 comandos · 6 subagentes · 10 skills · hooks

Veja a [documentação completa do plugin](./plugins/pwdev-uiux/README.md).

### pwdev-feat

Desenvolvimento de features assistido por IA com a **metodologia PWDEVIA de 7 perguntas**, portável para **Claude Code, Codex, Hermes Agent e OpenCode**. Mapeie o código com evidência, obtenha um plano estruturado com critérios de aceite rastreáveis, execute e revise.

```
Mapear (evidência) ─▶ Planejar (PWDEVIA, inline, com lint) ─▶ Executar (subagente ou inline, IMPLEMENT/REPORT, retomada) ─▶ Revisar
```

**Agentes:** PWDEVIA (planner inline) + executor e advisor (subagentes em todo runtime que os oferece, inline nos demais); lê a memória curada do pwdev-code quando presente

**Tipos de plano:** Feature, Backend, Frontend, Test, Review, Quick — UI verificada com `playwright-cli` e cenários E2E declarativos exportáveis para o Playwright Test

**Inclui:** 13 comandos · 2 subagentes · 13 skills · hooks

Veja a [documentação completa do plugin](./plugins/pwdev-feat/README.md).

### pwdev-hermes-orca

O Hermes Agent coordena workers supervisionados do **Orca** a partir de **issues do GitHub**. Você aprova o DAG uma vez; o Hermes despacha um worker por issue, cada um na própria worktree do Orca e rodando o `feat-loop` do pwdev-feat em modo orquestrado. Ele responde aos gates dos workers via `orca ask`, leva mudanças de escopo a você e fecha cada issue com PR validado e comentário.

```
Issues ─▶ Hermes (gate do DAG) ─▶ Run do Orca ─▶ worker por issue: plan → exec → review → PR ─▶ relatório
```

**Requer:** Orca (Hermes aberto num terminal do Orca), `gh`, pwdev-feat ≥ 3.2.0 em cada agente roteado

**Inclui:** 1 skill do Hermes · preflight só leitura · adaptador Hermes (bootstrap no primeiro turno só dentro do Orca). Nunca faz merge

Veja a [documentação completa do plugin](./plugins/pwdev-hermes-orca/README.pt-BR.md).

### pwdev-prd

**Criação de PRD** guiada por entrevista com um processo estruturado em 12
etapas — rodando inline (o entrevistador conversa com você). Agnóstico de
tecnologia, gera Markdown + JSON canônico; o PRD aprovado vira um roadmap com
cadeia de dependências explícita, publicado no GitHub pelo pwdev-github.

```
Entrevista (12 etapas) ─▶ PRD.md (APPROVED, RN) ─▶ roadmap + DEPENDENCIES.md ─▶ histórias (US, CA, RN) por feature ─▶ GitHub Project (pwdev-github)
```

**Saídas:** PRD estruturado com objetivos, métricas, requisitos funcionais/não-funcionais, arquitetura, riscos e critérios de aceitação

Portável: nove skills `prd-*` rodam no Claude Code, Codex, Hermes Agent e OpenCode
(`python3 plugins/pwdev-prd/.opencode-plugin/install.py` para o OpenCode).

**Inclui:** 9 comandos · 9 skills · 1 subagente (roadmap) · hooks

Veja a [documentação completa do plugin](./plugins/pwdev-prd/README.md).

### pwdev-github

**GitHub Projects e issues** pelo `gh` CLI: Projects a partir de presets
personalizáveis (ou copiados de um Project-modelo), roadmaps publicados com
sub-issues, milestones e blocked-by nativo, e uma skill para o dia a dia das issues.

```
roadmap.json ─▶ Project a partir de template ─▶ issues + sub-issues + blocked-by ─▶ skill github-issues
```

Portável: cinco skills `github-*` rodam no Claude Code, Codex, Hermes Agent e OpenCode
(`python3 plugins/pwdev-github/.opencode-plugin/install.py` para o OpenCode).

**Inclui:** 4 comandos · 5 skills · sem subagentes

Veja a [documentação completa do plugin](./plugins/pwdev-github/README.md).

### pwdev-qa

**Garantia de qualidade portátil** para Claude Code, Codex e Hermes Agent:
roteamento de intenção entre dez fluxos de QA, orientação especialista para web,
API, mobile, dados, acessibilidade, performance, segurança, automação e
produção, recomendação de ferramentas a partir do contexto observado,
evidência auditável e relatórios offline equivalentes em HTML e PDF.

```
init ─▶ strategy ─▶ test / explore ─▶ bug ─▶ regression ─▶ review ─▶ release ─▶ report
```

**Habilidades:** qa (roteador intenção→fluxo), 17 guias qa-specialist-*, qa-tooling
**Destaques:** evidência com digest SHA-256, aceite nunca inferido de confiança, paridade entre HTML e PDF offline, nenhum servidor MCP obrigatório

**Inclui:** 10 comandos · 29 skills · sem MCP

Veja a [documentação completa do plugin](./plugins/pwdev-qa/README.md).

### pwdev-skills

**Engenharia de skills** para Claude Code, Codex e Hermes Agent: revisa ou refatora uma `SKILL.md`
existente em um núcleo menor com referências condicionais, escolhe perfis lean/guided por medição,
descobre os runtimes e modelos disponíveis, mede skills com tokenizador genérico e compara a
candidata com a versão anterior por benchmark A/B headless em Claude Code, Codex, Hermes e
OpenCode, avaliado objetivamente e com orçamento.

```
descobrir runtimes e modelos ─▶ revisar / refatorar ─▶ tokens ─▶ benchmark A/B ─▶ tabela de eficiência por modelo
```

**Habilidades:** skill-refactor (contrato de revisão, dez regras de otimização, contrato de runtime)
**Destaques:** descoberta de runtimes e modelos com a origem de cada dado, esforço explícito ou registrado em cada run, custo por tarefa aceita, teto de orçamento, registros sanitizados

**Inclui:** 1 skill · sem subagentes · sem MCP

Veja a [documentação completa do plugin](./plugins/pwdev-skills/README.pt-BR.md).

### pwdev-copy

**Framework de copywriting treinável**: um arquivo de contexto define marca,
ICP e voz; **20 skills** produzem copy consistente a partir dele. A mesma
instalação atende qualquer cliente — troca-se o arquivo de treino.

```
treinar ─▶ voc ─▶ brief ─▶ copy ─▶ revisar ─▶ publicar ─▶ analisar ↺
```

**Subagentes:** voc, copywriter, reviewer, adversarial-copy, analyst
**Principais funcionalidades:** revisão em 7 sweeps com anti-slop, revisão adversarial de conversão, portão de brief (Ogilvy), ciclo de análise de desempenho

**Inclui:** 9 comandos · 5 subagentes · 20 skills

Veja a [documentação completa do plugin](./plugins/pwdev-copy/README.md).

### pwdev-social-media

**Geração de criativos por IA** para redes sociais: orquestração de APIs no
centro — Ideogram, Leonardo, Flux, Runway, Freepik/Magnific — via wrappers com
trava de gasto. Figma é camada opcional de composição. Complementa o
`pwdev-copy`: lá o texto, aqui a peça.

```
conceito ─▶ [CONFIRMAÇÃO DE CUSTO] ─▶ prompt ─▶ geração via API ─▶ curadoria ─▶ [figma] ─▶ revisão ─▶ export
```

**Subagentes:** art-director, asset-generator, creative-reviewer, figma-builder
**Principais funcionalidades:** trava de gasto com triagem de custo, modo prompt sem chaves de API, revisão de acessibilidade obrigatória

**Inclui:** 9 comandos · 4 subagentes · 19 skills · MCP

Veja a [documentação completa do plugin](./plugins/pwdev-social-media/README.md).

### pwdev-devops

**Plataforma, operação e incidente** com postura de execução segura: leitura
livre, mutação sob confirmação por comando, destrutivo bloqueado pelo
`scripts/guard.sh` — segunda barreira, independente da instrução da skill.

```
init (mapeia ambientes) ─▶ diagnosticar / incidente / auditar / custo / documentar
```

**Subagentes:** incident-commander, infra-auditor, db-analyst, platform-documenter
**Principais funcionalidades:** 24 skills (AWS, Kubernetes, Docker, Linux, Nginx, PostgreSQL, observabilidade, incidente, segurança, Proxmox, FinOps, …), auditoria somente-leitura, relatórios FinOps

**Inclui:** 7 comandos · 4 subagentes · 24 skills · MCP

Veja a [documentação completa do plugin](./plugins/pwdev-devops/README.md).

### pwdev-youtrack

**Gestão do YouTrack** pelo MCP server oficial embutido da JetBrains
(YouTrack 2025.3+): CRUD de issues, busca com a query language, comentários,
tags, artigos da knowledge base e log de trabalho — mais um fallback REST
autenticado para o que o MCP não cobre (agile boards, sprints, relatórios de
tempo, anexos, comandos em lote).

```
init (token → Keychain) ─▶ conversa natural via MCP ─▶ sprint / report via REST
```

**Skills:** youtrack (MCP oficial), youtrack-rest (boards/sprints/relatórios)
**Principais funcionalidades:** setup guiado com token no Keychain do macOS, token nunca em arquivo nem no transcript, mutação só com confirmação

**Inclui:** 4 comandos · 2 skills · MCP

Veja a [documentação completa do plugin](./plugins/pwdev-youtrack/README.pt-BR.md).

### pwdev-glpi

**Gestão ITSM do GLPI 10.x** por um servidor MCP próprio publicado no npm
([@soarescbm/mcp-glpi](https://github.com/soarescbm/mcp-glpi), iniciado via
`npx`): CRUD de tickets, followups, solução/fechamento, mais leitura de
usuários, grupos, ativos, projetos e base de conhecimento. A triagem da fila
é guiada pelos prompts MCP do próprio servidor.

```
init (PAT → Keychain) ─▶ conversa natural via MCP ─▶ triagem / relatorio
```

**Skills:** glpi (mapa intenção→tool, regras ITIL)
**Principais funcionalidades:** setup guiado com PAT no Keychain do macOS, triagem via prompt MCP `triage_ticket`, mutação só com confirmação, versão npm pinada

**Inclui:** 4 comandos · 1 skill · MCP

Veja a [documentação completa do plugin](./plugins/pwdev-glpi/README.pt-BR.md).

### pwdev-postgres

**Operação de PostgreSQL** por um servidor MCP próprio publicado no npm
([@soarescbm/postgres-mcp](https://github.com/soarescbm/postgres-mcp),
iniciado via `npx`): SELECT somente-leitura validado por AST, inspeção de
schema (tabelas, índices, constraints) e DML/DDL onde toda mutação é
dry-run obrigatório — preview primeiro, execução só com `confirm: true`.

```
init (connection string → Keychain) ─▶ conversa natural via MCP ─▶ esquema / mutações seguras
```

**Skills:** postgres (mapa intenção→tool, regras de mutação em duas fases)
**Principais funcionalidades:** setup guiado com connection string no Keychain do macOS, env var dedicada `PG_MCP_DATABASE_URL` (sem colisão com o `DATABASE_URL` de projetos), dry-run obrigatório em toda mutação, versão npm pinada

**Inclui:** 3 comandos · 1 skill · MCP

Veja a [documentação completa do plugin](./plugins/pwdev-postgres/README.pt-BR.md).

### pwdev-obsidian

Gerencia um vault do [Obsidian](https://obsidian.md) pelo **servidor MCP embutido
no plugin comunitário "Local REST API"** — sem servidor separado para instalar.

Lê, escreve e edita notas estruturalmente por heading, bloco ou frontmatter, em
vez de reescrever o arquivo inteiro, e busca no vault com JsonLogic e texto
livre. Também alcança tags, o arquivo ativo e a paleta de comandos.

**Inclui:** 3 comandos · 1 skill · MCP

Veja a [documentação completa do plugin](./plugins/pwdev-obsidian/README.pt-BR.md).

### pwdev-brain

**Segundo cérebro como LLM Wiki persistente** — wiki em Markdown no
[padrão do Karpathy](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f)
mantida como bundle [Open Knowledge Format v0.2](https://github.com/GoogleCloudPlatform/knowledge-catalog/blob/main/okf/SPEC.md).
As fontes são lidas uma vez, discutidas com você e integradas em documentos
de conceito com citação por afirmação; consultas respondem a partir da wiki
e devolvem sínteses duráveis para ela. Traz um **servidor MCP embutido
somente-leitura** (Node stdio zero dependências, 6 tools: info, index, list,
busca ranqueada, get, log) usável no Claude Code e em qualquer cliente MCP —
a escrita continua exclusiva do fluxo de ingest com discussão. Sem API keys.

```
raw/ (imutável) ─▶ ingest (discutido) ─▶ wiki/ OKF v0.2 ─▶ query (citada) ─▶ artefatos em output/
                                         ├─▶ lint (relatório → fixes aprovados)
                                         └─▶ MCP brain (só-leitura, 6 tools)
```

**Skills:** brain (roteamento de intenção: "adiciona isso ao meu brain" / "o que minha wiki diz sobre X", mapa intenção→tool MCP)
**Principais funcionalidades:** setup guiado (brain global ou por projeto), `raw/` imutável, nada é gravado sem discussão, citações em nota de rodapé resolvendo para `sources[].id`, `wiki/log.md` append-only, catálogo de regras de lint BR-nnn com fixes só aprovados, subagentes `brain-ingestor` + `brain-linter`, MCP embutido somente-leitura com guardas de path traversal e degradação graciosa para filesystem

**Inclui:** 5 comandos · 2 subagentes · 1 skill · MCP embutido (6 ferramentas)

Veja a [documentação completa do plugin](./plugins/pwdev-brain/README.pt-BR.md).

### pwdev-excalidraw

**Planejamento visual** com o servidor MCP oficial do Excalidraw: diagramas de arquitetura,
fluxos, mapas de dependência, registros de decisão e roadmaps que continuam editáveis no Excalidraw.

**Inclui:** 1 skill · servidor MCP (Excalidraw oficial)

Veja a [documentação completa do plugin](./plugins/pwdev-excalidraw/README.pt-BR.md).

### pwdev-fumadocs

**Sites de documentação Fumadocs** construídos a partir da documentação oficial ao vivo
(servidor MCP oficial do Fumadocs, páginas `.mdx` como alternativa): instalação em apps React
novos ou existentes, conteúdo MDX e navegação, features via `@fumadocs/cli` e diagnóstico com
scanner determinístico — toda mudança verificada por type-check e build.

```
fdscan (fatos do projeto) ─▶ página oficial ─▶ @fumadocs/cli ou edição manual ─▶ scan + type-check + build
```

Portável: quatro skills `fumadocs-*` rodam no Claude Code, Codex, Hermes Agent e OpenCode
(`python3 plugins/pwdev-fumadocs/.opencode-plugin/install.py` para o OpenCode).

**Inclui:** 4 comandos · 4 skills · servidor MCP (Fumadocs oficial) · sem subagentes

Veja a [documentação completa do plugin](./plugins/pwdev-fumadocs/README.pt-BR.md).

### pwdev-media

**Núcleo da suíte pwdev de mídia**: uma CLI (`pwdev-media`) com catálogo de modelos e apps de IA por
categoria (imagem, vídeo, áudio, transcrição, LLM/visão, motores de render), rotina mensal de
atualização que nunca sobrescreve a curadoria, geração por OpenRouter, fal e ElevenLabs só depois da
estimativa e de um "sim" explícito, chaves no Keychain, orçamento, ledger e formatos de criativos com
zonas seguras. Os plugins de vídeo e de criativos da suíte se apoiam nele.

```
catálogo (curado + descoberto) ─▶ recomendação por objetivo ─▶ estimativa ─▶ sim ─▶ provedor ─▶ ledger
```

Portável: seis skills `media-*` rodam no Claude Code, Codex e Hermes Agent.

**Inclui:** 7 comandos · 6 skills · sem servidor MCP · sem subagentes

Veja a [documentação completa do plugin](./plugins/pwdev-media/README.pt-BR.md).

### pwdev-video-hyperframes

**Edição de vídeo falado por conversa** (anúncio, Reels, TikTok, VSL, aula) com HyperFrames: o corte é
medido na onda do áudio (nenhuma pausa de 0,25 s ou mais, última tomada certa, fim das palavras
preservado); depois um `projeto.json` neutro de motor planeja legendas, zooms, rótulos, cenas sob
medida e som, que o `build.py` transforma na composição oficial do HyperFrames. Primeiro uma amostra
curta no estúdio; o render só é entregue quando o portão de qualidade diz PASSOU.

```
gravações ─▶ transcrição ─▶ frases/tomadas ─▶ corte pela onda ─▶ projeto.json ─▶ estúdio ─▶ render + portão
```

Portável: oito skills `vhf-*` rodam no Claude Code, Codex e Hermes Agent; precisa do `pwdev-media`.

**Inclui:** 9 comandos · 8 skills · sem servidor MCP · sem subagentes

Veja a [documentação completa do plugin](./plugins/pwdev-video-hyperframes/README.pt-BR.md).

### pwdev-video-remotion

**Edição de vídeo falado com Remotion (React)**, com o mesmo fluxo e o mesmo `projeto.json` do
pwdev-video-hyperframes: o núcleo `pwdev-media` resolve um plano de render uma vez, o `build.py` o
transforma em dados para um projeto Remotion com versões fixas, e as cenas sob medida são componentes
React tipados. Para times em React, lotes a partir de dados e render distribuído; a licença do
Remotion é conferida antes do primeiro projeto.

```
projeto.json ─▶ plano-render ─▶ src/dados.json ─▶ Remotion (React) ─▶ render + portão
```

Portável: oito skills `vrm-*` rodam no Claude Code, Codex e Hermes Agent; precisa do `pwdev-media`.

**Inclui:** 9 comandos · 8 skills · sem servidor MCP · sem subagentes

Veja a [documentação completa do plugin](./plugins/pwdev-video-remotion/README.pt-BR.md).

### pwdev-statusline

**Barra de status** rica para o terminal do Claude Code. Exibe modelo, branch git, uso de contexto, rate limits e contagem de tokens em uma linha colorida — cada segmento pode ser ligado/desligado.

```
PWDEV | Paulo Soares | session | …/skills-ia/projeto | Fable 5 | main | ctx:████░░░░░░ 42% | tok:1.5k | 5h:15%
```

**Comandos:** `install`, `uninstall`, `customize`, `preview`

**Seções:** Marca, Usuário, Sessão, Diretório (truncado), Modelo, Branch Git, Barra de Contexto (cor dinâmica), Tokens (formatados), Rate Limit (3 faixas de cor)

**Inclui:** 4 comandos · sem subagentes, sem skills, sem MCP

Veja a [documentação completa do plugin](./plugins/pwdev-statusline/README.pt-BR.md).

### pwdev-mods

Um **mod** do Claude Code (requer Claude Code v2.1.287+): código que roda dentro do Claude Code e desenha um painel de gestão ao lado da transcrição.

**Abas do painel:** Visão geral (barra de contexto, custo da sessão/dia, rate limits) · Subagentes (lista ao vivo, **Parar**, formulário **Disparar**) · Tokens (por turno, modelo e loop de agente, cache hit) · Histórico (sparkline diária mantida entre sessões)

**Também:** faixa de uma linha acima do prompt, toasts de orçamento diário em 80% / 100%, resumo em texto onde não há painel (VS Code, `-p`)

**Inclui:** 1 mod (módulo de hooks) · `/pwdev-mods [overview|agents|tokens|history]` · sem subagentes, sem MCP

Veja a [documentação completa do plugin](./plugins/pwdev-mods/README.pt-BR.md).

---

## Instalação

### Pré-requisitos

- [Claude Code](https://docs.anthropic.com/en/docs/claude-code) instalado
- Node.js 18+ (para servidores MCP via npx)

### Adicionar o marketplace

```bash
claude plugin marketplace add https://github.com/pwdev-solucoes/pwdev-claude-marketplace.git
```

### Instalar plugins

```bash
# Desenvolvimento com disciplina em Claude Code, Codex e Hermes (painéis de frota no cmux)
claude plugin install pwdev-power@pwdev-claude-marketplace

# Desenvolvimento orientado a especificação portátil para Claude Code e Codex (17 comandos, frotas nativas)
claude plugin install pwdev-flow@pwdev-claude-marketplace

# Fluxo SDD portátil com artefatos OKF v0.2 e execução rastreável
claude plugin install sdd-composy@pwdev-claude-marketplace

# Desenvolvimento orientado a especificação (8 subagentes, 6 fases, grafo de memória)
claude plugin install pwdev-code@pwdev-claude-marketplace

# Engenharia UI/UX (6 subagentes, Figma, WCAG, theming)
claude plugin install pwdev-uiux@pwdev-claude-marketplace

# Desenvolvimento simplificado de features (planos com 7 perguntas)
claude plugin install pwdev-feat@pwdev-claude-marketplace

# Hermes coordenando workers do Orca a partir de issues do GitHub (instale no Hermes; veja o README do plugin)
claude plugin install pwdev-hermes-orca@pwdev-claude-marketplace

# Criação de PRD guiada por entrevista (processo em 12 etapas) — também Codex, Hermes e OpenCode
claude plugin install pwdev-prd@pwdev-claude-marketplace
#   OpenCode: python3 plugins/pwdev-prd/.opencode-plugin/install.py     (--project . / --uninstall)

# GitHub Projects a partir de templates, publicação de roadmap, skill de issues — também Codex, Hermes e OpenCode
claude plugin install pwdev-github@pwdev-claude-marketplace
#   OpenCode: python3 plugins/pwdev-github/.opencode-plugin/install.py  (--project . / --uninstall)

# Garantia de qualidade portátil (10 fluxos, evidência, relatórios HTML/PDF)
claude plugin install pwdev-qa@pwdev-claude-marketplace

# Engenharia de skills: revisar, refatorar e fazer benchmark de skills entre runtimes
claude plugin install pwdev-skills@pwdev-claude-marketplace

# Framework de copywriting treinável (20 skills, ciclo de análise)
claude plugin install pwdev-copy@pwdev-claude-marketplace

# Geração de criativos por IA (orquestração de APIs, trava de gasto)
claude plugin install pwdev-social-media@pwdev-claude-marketplace

# Plataforma, operação e incidente (execução segura)
claude plugin install pwdev-devops@pwdev-claude-marketplace

# Gestão do YouTrack (MCP oficial + fallback REST)
claude plugin install pwdev-youtrack@pwdev-claude-marketplace

# Gestão ITSM do GLPI (servidor MCP próprio via npx)
claude plugin install pwdev-glpi@pwdev-claude-marketplace

# Operação de PostgreSQL (servidor MCP próprio via npx, dry-run obrigatório)
claude plugin install pwdev-postgres@pwdev-claude-marketplace

# Vault do Obsidian — notas, edição estrutural e busca (MCP via Local REST API)
claude plugin install pwdev-obsidian@pwdev-claude-marketplace

# Segundo cérebro — LLM Wiki em Open Knowledge Format (MCP embutido somente-leitura)
claude plugin install pwdev-brain@pwdev-claude-marketplace

# Barra de status rica para o terminal
claude plugin install pwdev-statusline@pwdev-claude-marketplace

# Painel de gestão do Claude Code (mod): subagentes, tokens, custo, histórico
claude plugin install pwdev-mods@pwdev-claude-marketplace

# Planejamento visual com Excalidraw (servidor MCP oficial)
claude plugin install pwdev-excalidraw@pwdev-claude-marketplace

# Sites de documentação Fumadocs (MCP oficial do Fumadocs) — também Codex, Hermes e OpenCode
claude plugin install pwdev-fumadocs@pwdev-claude-marketplace
#   OpenCode: python3 plugins/pwdev-fumadocs/.opencode-plugin/install.py  (--project . / --uninstall)

# Núcleo da suíte de mídia: catálogo de modelos, provedores (OpenRouter, fal, ElevenLabs), chaves e custo — também Codex e Hermes
claude plugin install pwdev-media@pwdev-claude-marketplace

# Edição de vídeo falado com HyperFrames (precisa do pwdev-media) — também Codex e Hermes
claude plugin install pwdev-video-hyperframes@pwdev-claude-marketplace

# Edição de vídeo falado com Remotion/React (precisa do pwdev-media; confira a licença do Remotion) — também Codex e Hermes
claude plugin install pwdev-video-remotion@pwdev-claude-marketplace
```

Instale apenas os plugins de que você precisa. Cada um funciona de forma independente.

---

## Configuração

Todos os plugins compartilham uma configuração unificada armazenada em `.planning/config.json`. Ela é definida durante o `/init` de qualquer plugin.

### Seleção de Idioma

Todos os comandos suportam **Português (PT-BR)** e **Inglês (EN)**. O idioma é configurado uma vez e aplicado em todos os plugins.

- Durante o `/init`: você escolhe o idioma
- Durante outros comandos: a preferência salva é usada silenciosamente
- Troca durante a conversa: se você mudar de idioma, o agente detecta e oferece atualizar sua preferência

```json
{
  "lang": "pt-BR"
}
```

Termos tecnicos (API, CRUD, REST, endpoint) permanecem sempre em inglês, independentemente do idioma escolhido. Nomes de arquivos e chaves de dados estruturados também permanecem em inglês.

### Perfis de Modelo

Só os **subagentes** resolvem modelo — personas inline rodam no modelo da
sessão. Cada plugin traz sua própria tabela de perfis em
`references/model-profiles.md` (fonte única por plugin). O `model_profile`
compartilhado (`performance` / `balanced` / `economy`) vale para todos os
plugins; os overrides são por subagente, com chaves namespaced onde
necessário:

- pwdev-code: `"executor"`, `"advisor"`, `"verifier"`, `"simplifier"`, ...
  (o executor também roteia por task via o header `Complexity:` do plano)
- pwdev-feat: `"feat-executor"`, `"feat-advisor"`
- pwdev-uiux: `"uiux-ui-builder"`, `"uiux-ux-critic"`, ...
- pwdev-prd: um subagente (`roadmap`, `model: inherit`) — nada a configurar

```json
{
  "lang": "pt-BR",
  "model_profile": "balanced",
  "model_overrides": {
    "executor": "opus",
    "uiux-ui-builder": "opus"
  }
}
```

---

## Trilha de Auditoria

Todos os plugins compartilham um banco de dados SQLite opcional em `.planning/pwdev-audit.db`. Ele é **desativado por padrão** e configurado durante o `/init`. O arquivo do banco nunca é versionado (adicionado automaticamente ao `.gitignore`).

**Como os dados chegam aqui (v2 — determinístico, via hooks):** cada plugin
traz `hooks/hooks.json` + scripts POSIX que registram automaticamente —
início/fim de sessão, execuções de subagentes com `session_id` e
`duration_ms` reais, escritas em `.planning/`, marcos de comandos e
alterações de configuração (`config_changes`). Nenhum agente roda INSERTs
inline. Um hook de guarda de segredos (PreToolUse, em todos os plugins)
bloqueia leitura de `.env`/`*.pem`/`*.key`/`id_rsa*`.

As linhas se distinguem pela coluna `plugin` — filtre com
`WHERE plugin='pwdev-code'` (ou `pwdev-feat`, `pwdev-prd`, `pwdev-uiux`).

### Consultando a Trilha de Auditoria

Todos os plugins incluem um comando `/audit` para consultar o banco interativamente:

| Sub-comando | O que faz |
|-------------|----------|
| `summary` (padrão) | Dashboard com métricas-chave e atividade recente |
| `events` | Log completo de eventos (últimos 50) |
| `decisions` | Todas as decisões arquiteturais/produto com justificativa |
| `artifacts` | Arquivos rastreados pelo framework |
| `stats` | Frequência de comandos, durações, distribuição por fase, taxa de sucesso |
| `export` | Gerar relatório completo de auditoria em PDF + Markdown |
| `query <SQL>` | Executar uma consulta SQL customizada (somente leitura) |

```bash
/pwdev-code:audit              # dashboard resumido
/pwdev-code:audit stats        # estatísticas detalhadas
/pwdev-code:audit export       # gerar relatório PDF em .planning/audit-report.pdf
/pwdev-code:audit query "SELECT * FROM events WHERE action='failed'"
```

O sub-comando `export` gera um relatório PDF completo com sumário executivo, log de eventos, decisões, artefatos, estatísticas e histórico de configuração. Suporta pandoc, weasyprint e wkhtmltopdf com detecção automática e fallback para Markdown.

Adicione `.planning/pwdev-audit.db` ao `.gitignore` (recomendado).

---

## Atualização

### Atualizar o marketplace

Baixe as últimas alterações do repositório do marketplace:

```bash
claude plugin marketplace update
```

Isso executa `git pull` na cópia local em `~/.claude/plugins/marketplaces/pwdev-claude-marketplace/`.

### Atualizar plugins instalados

Reinstale cada plugin que você usa para obter a versão mais recente:

```bash
claude plugin install pwdev-flow@pwdev-claude-marketplace
claude plugin install pwdev-code@pwdev-claude-marketplace
claude plugin install pwdev-uiux@pwdev-claude-marketplace
claude plugin install pwdev-feat@pwdev-claude-marketplace
claude plugin install pwdev-prd@pwdev-claude-marketplace
claude plugin install pwdev-github@pwdev-claude-marketplace
claude plugin install pwdev-qa@pwdev-claude-marketplace
claude plugin install pwdev-skills@pwdev-claude-marketplace
claude plugin install pwdev-copy@pwdev-claude-marketplace
claude plugin install pwdev-social-media@pwdev-claude-marketplace
claude plugin install pwdev-devops@pwdev-claude-marketplace
claude plugin install pwdev-youtrack@pwdev-claude-marketplace
claude plugin install pwdev-glpi@pwdev-claude-marketplace
claude plugin install pwdev-postgres@pwdev-claude-marketplace
claude plugin install pwdev-fumadocs@pwdev-claude-marketplace
claude plugin install pwdev-media@pwdev-claude-marketplace
claude plugin install pwdev-video-hyperframes@pwdev-claude-marketplace
claude plugin install pwdev-video-remotion@pwdev-claude-marketplace
claude plugin install pwdev-mods@pwdev-claude-marketplace
claude plugin install pwdev-statusline@pwdev-claude-marketplace
```

Isso copia os arquivos atualizados do plugin para o cache local. **Os dados do seu projeto (`.planning/`) nunca são tocados** — apenas os comandos e agentes do plugin são atualizados.

### Migrar seu workspace (se necessário)

Após atualizar, execute `/init` no seu projeto para verificar se há etapas de migração:

```
/pwdev-feat:init
/pwdev-code:init
/pwdev-uiux:init
/pwdev-prd:init
```

O comando `init` detecta workspaces existentes e:
- Preserva todos os seus dados (planos, PRDs, specs, relatórios)
- Oferece migração guiada se a estrutura de pastas mudou
- Pede para confirmar ou atualizar idioma, perfil de modelo e configurações de auditoria
- Nunca sobrescreve sem sua confirmação

### O que é atualizado vs. o que permanece

| Componente | Localização | Na atualização |
|------------|-------------|---------------|
| Comandos e agentes | `~/.claude/plugins/cache/` | **Substituídos** pela nova versão |
| Config do plugin | `~/.claude/plugins/installed_plugins.json` | **Atualizado** (versão, commit SHA) |
| Dados do projeto | `.planning/` (seu projeto) | **Intocados** — nunca modificados por atualizações |
| config.json | `.planning/config.json` | **Preservado** — init usa merge, não sobrescreve |
| Banco de auditoria | `.planning/pwdev-audit.db` | **Preservado** — append-only, nunca resetado |

### Compatibilidade de versão

Cada plugin armazena sua versão em `.claude-plugin/plugin.json`. Após atualizar, você pode verificar:

```bash
# Verificar versão instalada
cat ~/.claude/plugins/cache/pwdev-claude-marketplace/pwdev-feat/*/plugin.json | grep version
```

Mudanças incompatíveis (bumps de versão major) são documentadas no README de cada plugin em "Novidades".

---

## Licença

Apache-2.0

*Mantido por [Paulo Soares](https://github.com/soarescbm)*
