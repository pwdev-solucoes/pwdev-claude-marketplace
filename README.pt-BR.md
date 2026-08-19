# PWDEV Marketplace

*Leia em [English](./README.md)*

Marketplace de plugins para o [Claude Code](https://docs.anthropic.com/en/docs/claude-code).

---

## O que é a PWDEV

[Paulo Soares](https://github.com/soarescbm), CTO da PWDEV, empresa focada no desenvolvimento de soluções GovTech, acredita que a inteligência artificial está remodelando fundamentalmente o desenvolvimento de software. Mais do que uma tendência passageira, essa transformação representa uma nova forma de apoiar profissionais, ampliar capacidades e trazer maior consistência ao longo de todo o ciclo de desenvolvimento. Guiada por essa visão, a PWDEV disponibiliza essas soluções para ajudar equipes a trabalhar com mais estrutura, qualidade e previsibilidade.

Nossos plugins transformam o Claude Code de um assistente de codificação de uso geral em um parceiro de engenharia disciplinado, por meio de agentes especializados, fluxos de trabalho estruturados e pacotes de conhecimento específicos por domínio.

Filosofia central em todos os plugins:

> **Nunca execute sem um plano. Nunca entregue sem verificação.**

### PWDEV Power — runtime triplo

O `pwdev-power` roda as mesmas skills com aprovação no Claude Code, no Codex **e
no Hermes Agent**, com frotas isoladas no **cmux** em vez de tmux —
acompanhadas lado a lado num painel visual, ou rodando sozinhas.

Ele junta uma camada de produto — requisito e, em seguida, um roadmap
Fase→Épico→Feature→Task com rastreabilidade — com execução dirigida por
subagentes: registro durável, um brief por task, revisão entre tasks e ciclo de
correção limitado. Três disciplinas valem o tempo todo: nenhum código de
produção sem um teste visto falhando, nenhuma correção sem causa raiz antes, e
nenhuma afirmação de sucesso sem rodar o comando e ler a saída.

O comando privilegiado do provider existe em exatamente um adaptador por
runtime. O runtime é fixado pelo launcher escolhido antes de qualquer mutação, e
um runner cujo adaptador discorda recusa iniciar. Com o Hermes disponível, fases
aprovadas também podem ser despachadas pelo Kanban dele.

Comandos: `/pwdev-power:init`, `/pwdev-power:product`, `/pwdev-power:plan`,
`/pwdev-power:exec`, `/pwdev-power:fleet`, `/pwdev-power:verify`,
`/pwdev-power:quick`.

---

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

## Novidades

### Painéis visuais de frota e membros retomáveis — pwdev-power

O `/pwdev-power:fleet` agora abre por padrão um **painel visual no cmux**: um
pane por fase aprovada, cada um uma sessão interativa no próprio worktree já
lendo o spec e o plano daquela fase, até quatro por vez. O `--auto` continua
rodando a frota não supervisionada. O reconhecimento da flag perigosa é exigido
nos dois — assistir a uma sessão não é aprovar o que ela faz entre as suas
olhadas.

Um membro que parou no meio não precisa mais recomeçar. O `--resume` reexecuta a
etapa que o status do runner registra, pula as que já passaram e restaura a
contagem de ciclos de correção, para que o loop de correção continue em vez de
voltar a zero. É também a única coisa que pode reiniciar um membro parado em
`NEEDS_HUMAN`: esse status pede que um humano olhe, e a flag é o humano dizendo
que olhou.

Vieram junto duas correções de contrato, ambas encontradas rodando um membro
real de ponta a ponta. A etapa de plano passa a ser guardada só pelo `spec.md`,
então escrever o `plan.md` não invalida mais o vínculo sob o qual o membro foi
lançado. E o limite de 500 caracteres na mensagem de resultado agora está
declarado no contrato em prosa que os runtimes claude e hermes leem, em vez de
apenas ser cobrado depois — desvios que não carregam informação são reparados,
não derrubam uma etapa que já commitou o trabalho dela.

### Três runtimes e frotas no cmux — pwdev-power v0.1.0

Um plugin de workflow novo, que roda as mesmas skills com aprovação em **Claude
Code, Codex e Hermes Agent**, e troca a camada de frota em tmux pelo **cmux** —
estado, progresso e notificações aparecem na barra lateral em vez de num painel
que alguém precisa ficar olhando.

Ele traz as disciplinas de engenharia que os outros plugins de workflow deixam
implícitas: um portão de brainstorming que classifica o pedido em voz alta antes
da primeira pergunta, planos cujos valores exatos chegam literais a quem
implementa, execução com registro durável e ciclo de correção limitado, e
verificação que tenta refutar a conclusão. O `init` também mapeia o codebase em
quatro documentos de contexto, para que um design parta do que já se sabe.

Onde o Hermes está instalado, fases aprovadas podem ser despachadas pelo Kanban
dele em vez do runner embutido — a ponte reaplica o portão de aprovação por
conta própria, já que o board não tem opinião sobre aprovação.

### Delegação a CLIs externas — pwdev-code v2.3.0

Claude Code como **orquestrador de outros agentes de código**: 6 novos
comandos (`/pwdev-code:codex`, `opencode`, `kimi`, `gemini`, `kiro` e o
inteligente `/pwdev-code:delegate`) roteiam tarefas por um runner único e
endurecido — allowlist de binários, prompt de segurança com 10 regras,
timeout, trava de escrita, verificação read-only (`gemini` é somente leitura
por padrão) — e o Claude então revisa o `git diff` completo, roda os testes
ele mesmo e dá o veredito próprio (nunca commita). Config opcional por
agente via `external_models.<agent>`.

### Padrões de orquestração — pwdev-code v2.2.0 e pwdev-feat v2.1.0

Os plugins de desenvolvimento absorveram três padrões de orquestração —
planejar, especializar, revisar agora também é *consultar o modelo forte no
momento da dúvida*:

- **Subagente advisor** (ambos os plugins) — um executor travado numa decisão
  difícil emite `NEEDS_ADVICE`; o orquestrador consulta o novo `advisor`
  (Opus mesmo em `balanced`, somente leitura, `effort: high`) e re-spawna o
  executor com a decisão anexada. Máx. 1 consulta por task.
- **Roteamento de modelo por task** (pwdev-code) — os planos declaram
  `Complexity: low|medium|high`; o modelo do executor é resolvido por task
  (ex.: `balanced`: high → opus, low/medium → sonnet). Retrocompatível.
- **Grafo de memória** (pwdev-code) — memórias se relacionam via `related:` /
  `[[nome]]` / sufixo `[rel:]` no índice; a seleção no spawn expande 1 salto
  sem abrir arquivos; novos subcomandos `memory link` e `memory graph`. O
  pwdev-feat passa a consumir a memória compartilhada (somente leitura).
- **Waves paralelas opt-in** (pwdev-code) — tasks `Parallel-safe` com
  arquivos disjuntos rodam em lotes de executores em worktrees git isolados,
  integrados por merge sequencial. O padrão continua serial.
- **Reviewer externo opcional via CLI** (pwdev-code) — o `/review` pode
  colher uma segunda opinião consultiva de uma CLI da allowlist (codex,
  gemini, opencode, qwen); findings externos nunca bloqueiam o gate.

> **Atualizando?** Plugins instalados são cópias em cache — rode
> `claude plugin marketplace update pwdev-claude-marketplace` +
> `claude plugin update <plugin>@pwdev-claude-marketplace` e reinicie o
> Claude Code para os novos agentes registrarem.

### Novos plugins — marketing e operações

O marketplace agora vai além do fluxo de desenvolvimento:

- **pwdev-copy v1.1.0** — framework de copywriting treinável, expandido para
  **20 skills / 5 subagentes / 9 comandos**: novas skills de criação (ganchos,
  reaproveitamento), revisão CRO de página e uma **camada de análise**
  (`perf-analyzer` / `perf-patterns` / `perf-optimize` + subagente `analyst`)
  que fecha o ciclo: pesquisa → brief → copy → revisão → publicação → análise.
- **pwdev-social-media v2.0.0** *(novo)* — geração de criativos para redes
  sociais com **orquestração de APIs no centro** (Ideogram, Leonardo, Flux,
  Runway, Freepik/Magnific) via wrappers com trava de gasto: triagem de custo,
  engenharia de prompt, consistência visual e curadoria de variações. Figma é
  camada opcional de composição. 19 skills, 4 subagentes.
- **pwdev-devops v1.0.0** *(novo)* — plataforma, operação e incidente com
  **postura de execução segura**: leitura livre, mutação sob confirmação por
  comando, destrutivo bloqueado por guard script (segunda barreira,
  independente da instrução da skill). 19 skills cobrindo AWS, Kubernetes,
  Docker, Linux, Nginx, PostgreSQL, observabilidade, incidente, segurança,
  Proxmox, FinOps e mais; 4 subagentes.

### A onda v2

Os cinco plugins originais foram reconstruídos sobre o sistema moderno de plugins do
Claude Code. **Nenhum slash command foi renomeado ou removido** — os internos
foram reestruturados.

### Comum aos plugins de workflow (code / feat / prd / uiux)

- **Orquestração híbrida** — personas que interagem com o humano
  (entrevistas, gates de aprovação) rodam INLINE no contexto principal; o
  trabalho pesado roda em **subagentes reais** spawnados via Task tool com
  frontmatter oficial, contexto fresco e paralelismo genuíno. A prosa antiga
  de "assuma a persona" acabou.
- **Auditoria determinística via hooks** — a trilha SQLite compartilhada
  (`.planning/pwdev-audit.db`, coluna `plugin` distingue as linhas) agora é
  gravada por hooks: `duration_ms`/`session_id` reais, `config_changes`
  finalmente populada. Um **hook de guarda de segredos** (PreToolUse)
  bloqueia leitura de `.env`/`*.pem`/`*.key`/`id_rsa*` em todos os plugins.
- **References empacotadas** — protocolo de idioma, perfis de modelo,
  contratos de spawn e schema de auditoria vivem no `references/` de cada
  plugin, resolvidos via `${CLAUDE_PLUGIN_ROOT}` (fim dos blocos duplicados
  e paths relativos quebrados).
- **`/audit` endurecido** — guard de query só-SELECT de statement único;
  shell POSIX portátil em tudo.

### pwdev-code v2.1.0

- **7 subagentes reais** (executor, simplifier, code-reviewer, qa, verifier
  adversarial, researcher, roadmap) + 5 personas inline; 16 comandos.
- **Memória curada do projeto** (`/pwdev-code:memory` + `.planning/memory/`
  versionada) alimentando todo spawn; lições auto-capturadas de verificações
  rejeitadas e reviews bloqueados.
- **Loops de correção com parada dura** — `verify` → fix plans →
  `execute --fix` (máx 2 iterações); review gate bloqueia o verify;
  `verify --strict` roda 2 verifiers em paralelo (vale o pior veredito).
- **`/pwdev-code:simplify`** — refactor de qualidade em 2 passes (propõe
  ≥80% de confiança → humano aprova por ID → aplica + commit refactor).
- **`skill-user-stories`** + `/pwdev-code:product stories` (INVEST, ACs em
  Gherkin, definition of ready).

### pwdev-feat v2.0.0

- **Subagente executor real** com modos IMPLEMENT/REPORT (planos de review
  reportam findings sem commitar); planner PWDEVIA inline
  (`references/pwdevia-method.md`); `/status` agora detecta FAILED/CAVEATS.

### pwdev-prd v2.0.0

- **Entrevistador inline por design** (zero subagentes); estrutura canônica
  do `prd.json` finalmente definida; init não configura mais perfil de
  modelo (nada aqui resolve modelo).

### pwdev-uiux v2.0.0

- **6 subagentes reais + 2 personas inline** (orchestrator e theme-builder
  seguram os gates humanos); campos proibidos removidos dos agents
  (`permissionMode`, `mcpServers`, `skills:` não-oficial); skills passadas
  como paths explícitos de SKILL.md nos spawns; overrides de modelo com
  namespace (`uiux-<agent>`).

### pwdev-statusline v1.1.0

- **Bloco de configuração** (toggles/cores/separador/profundidade como
  variáveis — o `/customize` edita 1 linha, idempotente); **uma chamada de
  jq** por render; cores dinâmicas de contexto/rate; tokens formatados
  (`512k`/`1.2M`); paths truncados; install/uninstall mais seguros.

---

## Plugins

| Plugin | Descrição | Versão | Licença |
|--------|-----------|:------:|:------:|
| [**pwdev-flow**](./plugins/pwdev-flow/) | Desenvolvimento orientado a especificação portátil para Claude Code **e** Codex — um único contrato `.planning/flow`, 17 comandos, auditoria semântica opt-in, delegação guardada a CLIs externas, frotas nativas isoladas (`claude -p` / `codex exec`) | 0.6.0 | Apache-2.0 |
| [**pwdev-power**](./plugins/pwdev-power/) | Desenvolvimento orientado a especificação com disciplina, para Claude Code, Codex **e** Hermes Agent — portão de brainstorm, planos com restrições literais, execução dirigida por subagentes com registro e ciclo de correção limitado, verificação adversarial, mapa do codebase, frotas isoladas no cmux como painel visual ou sozinhas | 0.1.0 | Apache-2.0 |
| [**pwdev-code**](./plugins/pwdev-code/) | Desenvolvimento orientado a especificação — 8 subagentes reais (incl. advisor), roteamento por task, grafo de memória, waves paralelas opt-in, delegação a CLIs externas (Codex/OpenCode/Kimi/Gemini/Kiro), 23 comandos | 2.4.0 | Apache-2.0 |
| [**pwdev-uiux**](./plugins/pwdev-uiux/) | Engenharia UI/UX — 6 subagentes reais, fluxo de 5 fases com gates, Figma, WCAG 2.1 AA | 2.0.1 | Apache-2.0 |
| [**pwdev-feat**](./plugins/pwdev-feat/) | Desenvolvimento simplificado de features — planos PWDEVIA inline + subagentes executor e advisor | 2.1.1 | Apache-2.0 |
| [**pwdev-prd**](./plugins/pwdev-prd/) | Criação de PRD guiada por entrevista — 12 etapas inline, Markdown + JSON canônico | 2.0.1 | Apache-2.0 |
| [**pwdev-copy**](./plugins/pwdev-copy/) | Framework de copywriting treinável — 20 skills no ciclo completo (VOC → copy → revisão → análise), 5 subagentes reais | 1.1.0 | Apache-2.0 |
| [**pwdev-social-media**](./plugins/pwdev-social-media/) | Geração de criativos por IA — orquestração de APIs (Ideogram, Leonardo, Flux, Runway, Freepik) com trava de gasto, 19 skills, 4 subagentes | 2.0.1 | Apache-2.0 |
| [**pwdev-devops**](./plugins/pwdev-devops/) | Plataforma, operação e incidente — postura de execução segura com guard script, 19 skills, 4 subagentes | 1.0.0 | Apache-2.0 |
| [**pwdev-youtrack**](./plugins/pwdev-youtrack/) | Gestão do YouTrack — MCP oficial embutido (2025.3+) para issues, artigos e log de trabalho; fallback REST para boards, sprints e relatórios de tempo | 1.0.0 | Apache-2.0 |
| [**pwdev-glpi**](./plugins/pwdev-glpi/) | GLPI 10.x ITSM — servidor MCP próprio via npx (@soarescbm/mcp-glpi): CRUD de tickets, triagem com prompts MCP, relatórios de fila, ativos e KB | 1.0.5 | Apache-2.0 |
| [**pwdev-postgres**](./plugins/pwdev-postgres/) | PostgreSQL — servidor MCP próprio via npx (@soarescbm/postgres-mcp): SELECT somente-leitura validado por AST, inspeção de schema, DML/DDL com dry-run obrigatório | 1.0.0 | Apache-2.0 |
| [**pwdev-obsidian**](./plugins/pwdev-obsidian/) | Vault do Obsidian — servidor MCP embutido no plugin comunitário Local REST API: leitura, escrita e edição estrutural de notas (heading/bloco/frontmatter), busca JsonLogic e texto livre, tags, arquivo ativo, paleta de comandos | 1.0.0 | Apache-2.0 |
| [**pwdev-brain**](./plugins/pwdev-brain/) | Segundo cérebro em LLM Wiki (padrão Karpathy) no Open Knowledge Format v0.2 — ingest discutido com citação por afirmação, query citada, lint de conformidade; 2 subagentes, MCP embutido somente-leitura (6 tools) | 1.1.0 | Apache-2.0 |
| [**pwdev-statusline**](./plugins/pwdev-statusline/) | Barra de status rica — cores dinâmicas, tokens formatados, totalmente configurável | 1.1.0 | Apache-2.0 |

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

**Inclui:** 7 comandos · 5 subagentes · 14 skills · hooks

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

Desenvolvimento de features assistido por IA simplificado, utilizando a **metodologia PWDEVIA com 7 perguntas**. Descreva o que você quer, obtenha um plano estruturado e execute.

```
Describe ─▶ Plan (PWDEVIA, inline) ─▶ Execute (subagente real, IMPLEMENT/REPORT)
```

**Agentes:** PWDEVIA (planner inline) + executor e advisor (subagentes reais); lê a memória curada do pwdev-code quando presente

**Tipos de plano:** Feature, Backend, Frontend, Test, Review, Quick

**Inclui:** 12 comandos · 2 subagentes · hooks

Veja a [documentação completa do plugin](./plugins/pwdev-feat/README.md).

### pwdev-prd

**Criação de PRD** guiada por entrevista com um processo estruturado em 12
etapas — rodando inline (o entrevistador conversa com você; zero subagentes
por design). Agnóstico de tecnologia, gera Markdown + JSON canônico.

```
Interview (12 steps) ─▶ PRD.md ─▶ Export (JSON / GitHub Issue)
```

**Saídas:** PRD estruturado com objetivos, métricas, requisitos funcionais/não-funcionais, arquitetura, riscos e critérios de aceitação

**Inclui:** 6 comandos · sem subagentes, por design · hooks

Veja a [documentação completa do plugin](./plugins/pwdev-prd/README.md).

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
**Principais funcionalidades:** 19 skills (AWS, Kubernetes, Docker, Linux, Nginx, PostgreSQL, observabilidade, incidente, segurança, Proxmox, FinOps, …), auditoria somente-leitura, relatórios FinOps

**Inclui:** 7 comandos · 4 subagentes · 19 skills · MCP

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

### pwdev-statusline

**Barra de status** rica para o terminal do Claude Code. Exibe modelo, branch git, uso de contexto, rate limits e contagem de tokens em uma linha colorida — cada segmento pode ser ligado/desligado.

```
PWDEV | Paulo Soares | session | …/skills-ia/projeto | Fable 5 | main | ctx:████░░░░░░ 42% | tok:1.5k | 5h:15%
```

**Comandos:** `install`, `uninstall`, `customize`, `preview`

**Seções:** Marca, Usuário, Sessão, Diretório (truncado), Modelo, Branch Git, Barra de Contexto (cor dinâmica), Tokens (formatados), Rate Limit (3 faixas de cor)

**Inclui:** 4 comandos · sem subagentes, sem skills, sem MCP

Veja a [documentação completa do plugin](./plugins/pwdev-statusline/README.pt-BR.md).

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

# Desenvolvimento orientado a especificação (8 subagentes, 6 fases, grafo de memória)
claude plugin install pwdev-code@pwdev-claude-marketplace

# Engenharia UI/UX (6 subagentes, Figma, WCAG, theming)
claude plugin install pwdev-uiux@pwdev-claude-marketplace

# Desenvolvimento simplificado de features (planos com 7 perguntas)
claude plugin install pwdev-feat@pwdev-claude-marketplace

# Criação de PRD guiada por entrevista (processo em 12 etapas)
claude plugin install pwdev-prd@pwdev-claude-marketplace

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
- pwdev-prd: sem subagentes — nada a configurar

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
claude plugin install pwdev-copy@pwdev-claude-marketplace
claude plugin install pwdev-social-media@pwdev-claude-marketplace
claude plugin install pwdev-devops@pwdev-claude-marketplace
claude plugin install pwdev-youtrack@pwdev-claude-marketplace
claude plugin install pwdev-glpi@pwdev-claude-marketplace
claude plugin install pwdev-postgres@pwdev-claude-marketplace
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
