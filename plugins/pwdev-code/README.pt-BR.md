# PWDEV-CODE v2.2.0

*Leia em [English](./README.md)*

> **Framework de Desenvolvimento Orientado a Especificação (SDD) para Claude Code**

```
Nunca execute sem um plano. Nunca entregue sem verificação.
```

O PWDEV-CODE usa **orquestração híbrida**: fases interativas rodam na conversa
principal (onde o humano aprova os gates), e o trabalho pesado é delegado a
**8 subagentes reais** com contexto fresco — em **6 fases** com loops de
correção e **memória curada do projeto**, para que cada linha de código seja
planejada, rastreável e verificada.

---

## Novidades da v2.2.0

- **Subagente advisor** (`advisor` + status `NEEDS_ADVICE`): quando o executor
  trava numa decisão difícil no meio da task (ambiguidade de spec, fork
  arquitetural, falha repetida de verificação com pergunta concreta), ele para
  e pergunta. O orquestrador consulta o advisor — o modelo forte (Opus mesmo
  em `balanced`), somente leitura, `effort: high` — e re-spawna o executor com
  a decisão anexada. Máx. 1 consulta por task; conselhos de alta confiança
  viram memória `decision`.
- **Roteamento de modelo por task**: os planos declaram
  `Complexity: low|medium|high` no cabeçalho de wave; o `/pwdev-code:execute`
  resolve o modelo do executor por task via a matriz de complexidade em
  `references/model-profiles.md` (ex.: em `balanced`, low/medium → sonnet,
  high → opus; fix plans são implicitamente high). Retrocompatível — sem o
  campo, vale `medium`, exatamente o comportamento anterior.
- **Grafo de memória**: memórias agora se relacionam (`related:` no
  frontmatter, links `[[nome]]`, sufixo `[rel:]` no índice). A seleção no
  spawn expande 1 salto pelas relações (cap total 7) sem abrir arquivo algum.
  Novos subcomandos: `/pwdev-code:memory link <a> <b>` e
  `/pwdev-code:memory graph`.
- **Waves paralelas opt-in** (`"parallel_execution": true`): tasks marcadas
  `Parallel-safe: yes` com conjuntos de arquivos disjuntos rodam em lote de
  executores em worktrees git isolados (`isolation: worktree`), integrados
  por merge sequencial. O padrão continua serial; qualquer dúvida cai para
  serial.
- **Reviewer externo opcional via CLI** (`external_models.reviewer` no
  `.planning/config.json`): o `/pwdev-code:review` pode colher uma segunda
  opinião de uma CLI externa (codex, gemini, opencode, qwen — allowlist +
  confirmação humana). Findings externos são apenas consultivos — nunca
  bloqueiam o gate de review sozinhos.

## Novidades da v2.1.0

- **Memória curada do projeto** (`/pwdev-code:memory` + `.planning/memory/`,
  versionada): decisões duradouras, lições e convenções. Todo spawn de
  subagente recebe um bloco RELEVANT MEMORY; rejeições do verify e reviews
  bloqueados capturam lições automaticamente (teto: 2/fase); o design
  consulta memórias de decisão e sinaliza contradições. Protocolo:
  `references/memory.md`.
- **Passo de simplificação** (`/pwdev-code:simplify` + subagente
  `simplifier`): etapa opcional entre EXECUTE e REVIEW. Dois passes —
  ANALYZE só propõe simplificações com confiança ≥80% (reuso, dead code,
  complexidade, eficiência; nunca bugs, nunca mudança de comportamento), o
  humano aprova por ID, APPLY implementa com commit `refactor` próprio e
  verificação por proposta (falhou → reverte + SKIPPED). Mudanças aplicadas
  marcam `review_gate: STALE` → o review re-roda escopado ao diff do refactor.
- **Histórias de usuário** (`skill-user-stories` + `/pwdev-code:product
  stories`): INVEST, formato canônico Como/Quero/Para, ACs em Gherkin,
  definition of ready, anti-padrões, checklist de 10 itens — persistidas em
  `.planning/product/stories/US-NN-*.md`. O §6 do PRD agora segue a skill.
- **`verify --strict`**: dois verifiers independentes em paralelo (lente
  FUNCTIONAL vs lente COMPLIANCE); veredito final = o pior dos dois. Custo
  ≈2× — indicado para o gate final da fase, não para toda iteração de fix.
- **Re-review automático escopado** após `execute --fix` e `simplify` — só
  os commits de correção/refactor, nunca a fase inteira de novo.
- **Frontmatter moderno**: `effort: high` (verifier) / `effort: low`
  (researcher); `paths` com auto-load de skills (frontend-design ativa em
  arquivos de frontend, user-stories em PRD/stories); roteamento posicional
  `$1`/`$2` nos comandos com subcomandos. Progressive enhancement — campos
  não suportados viram no-op em versões antigas do Claude Code.
- **Rejeitados deliberadamente** (registrado para não re-discutir): campo
  `memory` por agente (bifurcaria o conhecimento fora da memória curada e
  quebraria o Fresh Context Model) e hook SessionStart de memória (taxaria
  toda sessão e ficaria stale — os STEPs releem na hora do uso).

## Novidades da v2.0.0

**Release com breaking changes** — o framework foi reconstruído sobre o
sistema moderno de plugins do Claude Code. Nenhum slash command foi renomeado
ou removido; o que mudou é como eles funcionam por dentro.

- **Subagentes reais (orquestração híbrida).** `execute`, `review`, `verify`,
  `discover` (pesquisa) e `product roadmap` agora spawnam subagentes de
  verdade via Task tool — o "Fresh Context Model" é literal, e o `review`
  roda code-reviewer + qa **genuinamente em paralelo**.
- **Auditoria determinística via hooks.** A trilha SQLite agora é gravada por
  hooks do plugin (`SessionStart`, `SubagentStart/Stop`, `PostToolUse`,
  `Stop`) — sem INSERTs inline dependentes do LLM lembrar, e com
  `duration_ms` real.
- **Hook de guarda de segredos.** A regra "nunca ler .env / *.pem / *.key"
  agora é garantida deterministicamente por um hook `PreToolUse`, não só por prosa.
- **Loops de correção com parada dura.** `verify` → fix plans →
  `execute --fix` → re-verify, com **máximo de 2 iterações de correção**
  antes de escalar ao humano. Gate de review: findings críticos bloqueiam o `verify`.
- **Verificador adversarial.** O verifier tenta REFUTAR a conclusão — ele
  re-executa as evidências e desconfia dos summaries de execução.
- **Protocolos empacotados.** Idioma, perfis de modelo, contratos de spawn e
  o schema de auditoria vivem em `references/` dentro do plugin (resolvidos
  via `${CLAUDE_PLUGIN_ROOT}`) — uma fonte de verdade, sem blocos duplicados.
- **Removidos:** `settings.example.json` (fluxo de instalação manual legado)
  e o `executor-context.md` auto-gerado (obsoleto — todo spawn é fresco e
  auto-contido).

### Instalação

```
/plugin marketplace add pwdev-solucoes/pwdev-claude-marketplace
/plugin install pwdev-code
```

Depois, dentro do seu projeto: `/pwdev-code:init`.

---

## Metodologia

### O Problema

Sem um framework estruturado, o Claude gera código ad-hoc sem plano, critérios
de aceite são subjetivos, o context rot degrada a qualidade em sessões longas,
decisões não são rastreáveis e a verificação é ausente.

### Orquestração Híbrida

O framework separa **o que** fazer, **quem** faz e **com que** conhecimento:

```
┌─────────────────────────────────────────────────────────────┐
│  COMMANDS (commands/) — "O QUE fazer"                       │
│  orquestração, gates, fluxo, persistência; fases            │
│  interativas (entrevista, decisões de design) ficam aqui    │
├─────────────────────────────────────────────────────────────┤
│  SUBAGENTES (agents/) — "QUEM faz o trabalho pesado"        │
│  8 subagentes reais spawnados com contexto fresco e         │
│  prompt auto-contido (spawn contract)                       │
├─────────────────────────────────────────────────────────────┤
│  SKILLS (skills/) — "COM QUE conhecimento"                  │
│  guidelines, padrões, anti-padrões                          │
└─────────────────────────────────────────────────────────────┘
```

**Regra de bolso:** o que precisa conversar com o humano (entrevistas, gates
de aprovação) roda no contexto principal; o que é pesado, repetitivo ou se
beneficia de contexto limpo roda como subagente.

### 6 Fases

```
DISCOVER  ─▶  DESIGN  ─▶  PLAN  ─▶  EXECUTE  ─▶  REVIEW  ─▶  VERIFY
   │            │           │          │           │           │
Entrevista   spec.md     Tasks      Subagente   Reviewer+QA  Verificador
+ subagente  + Decisões  atômicas   executor    subagentes   adversarial
  researcher             em waves   por task    em paralelo  + fix plans
```

| Fase | Quem faz o trabalho | Saída |
|------|--------------------|-------|
| **DISCOVER** | Entrevista (contexto principal) + subagente **researcher** em paralelo | project.md, requirements.md, domain/stack/pitfalls |
| **DESIGN** | Persona de arquiteto (contexto principal, decisões exigem aprovação) | spec.md (8 seções), decisions.md |
| **PLAN** | Persona de planner (contexto principal, mapa de waves exige aprovação) | planos com `Wave:`/`Depends on:` (máx 3 tasks, máx 5 arquivos/task) |
| **EXECUTE** | Subagente **executor**, contexto fresco por task | Código + commits atômicos + summaries |
| **REVIEW** | Subagentes **code-reviewer** + **qa** em paralelo | code-review.md + qa-report.md |
| **VERIFY** | Subagente **verifier** (adversarial, goal-backward) | verify.md + fix plans se rejeitado |

**Regras de transição:** cada gate exige aprovação humana. Findings críticos
no review setam `review_gate: BLOCKED` e o `verify` se recusa a rodar. O
VERIFY aprova ou gera fix plans → `execute --fix` → re-verify, no máximo 2
iterações de correção antes de escalar.

### Níveis de Intensidade

| Nível | Quando usar | Fluxo |
|-------|-------------|-------|
| **Quick** | Bugfix, config, 1-3 arquivos | `/pwdev-code:quick` — mini-plano → implementar → mini-review → mini-verify |
| **Standard** | Feature média, 2-5 arquivos | DISCOVER → PLAN → EXECUTE → REVIEW → VERIFY |
| **Full** | Feature complexa, projeto novo | PRD → ROADMAP → todas as 6 fases por feature |

**Escalação automática:** >5 arquivos → Standard. Decisão arquitetural → Standard. Migração/schema → Full.

### spec.md — O Contrato Central

Gerado na fase DESIGN, governa toda a execução. 8 seções obrigatórias:

| # | Seção | Propósito |
|---|-------|-----------|
| 1 | **Persona** | Stack, senioridade, skills ativas |
| 2 | **Objective** | O que deve existir ao terminar (1-3 frases mensuráveis) |
| 3 | **Inputs** | Entidades, endpoints, regras de negócio |
| 4 | **Format** | Estrutura de arquivos, convenções |
| 5 | **Quality** | Testes, lint, performance + critérios das skills |
| 6 | **Stop Conditions** | Quando o executor DEVE parar e perguntar (mín 5) |
| 7 | **Prohibitions** | O que NUNCA fazer (específicas + globais) |
| 8 | **Definition of Done** | Checklist verificável com comandos reais |

### Gestão de Contexto (harness engineering)

O framework combate o **context rot**: cada task roda num subagente real com
contexto fresco, recebendo APENAS: a task + trechos da spec (§1, 6, 7) +
skills ativas + arquivos explicitamente listados. Zero histórico.

O **spawn contract** (`references/spawn-contracts.md`) formaliza isso: os
subagentes gravam relatórios completos em arquivos de `.planning/` e
respondem ao orquestrador com ≤10 linhas de status — os artefatos são o
contrato, `state.md` é a fonte de verdade, e o orquestrador nunca cola
relatórios de volta no próprio contexto.

### Verificação — Goal-Backward Adversarial

O verifier não pergunta "o que fizemos?" — pergunta **"o que precisa ser
VERDADE, e consigo provar que NÃO é?"** Ele re-executa as evidências dos
summaries e tenta ao menos uma refutação por verdade.

| Veredito | Critério |
|----------|----------|
| **APPROVED** | 100% ACs + 100% DoD + 0 proibições violadas |
| **WITH CAVEATS** | >=90% ACs + só falhas de baixa severidade |
| **REJECTED** | <90% ACs OU proibição crítica OU DoD crítico falhando |

---

## Subagentes

Subagentes reais (spawnados via Task tool, contexto fresco, tools restritas):

| Subagente | Modelo (balanced) | Tools | O que faz |
|-----------|:----------------:|-------|-----------|
| **executor** | sonnet | Read, Write, Edit, Grep, Glob, Bash | Implementa UMA task atômica: código, verificação, commit atômico, summary |
| **advisor** | opus | somente leitura + Write (sem Edit) | Resolve UMA decisão difícil levantada por um executor travado (NEEDS_ADVICE) — escolhe uma direção, nunca implementa |
| **code-reviewer** | sonnet | leitura + Write (sem Edit) | Revisa o diff em 6 dimensões (correção, segurança, perf, arquitetura, convenções, testes) |
| **qa** | sonnet | leitura + Write (sem Edit) | Roda a suíte real de testes, rastreia requisito→teste, propõe skeletons |
| **verifier** | sonnet | leitura + Write (sem Edit) | Verificação adversarial; gera fix plans quando rejeita |
| **researcher** | haiku | leitura + Write + web | Investiga stack/domínio/pitfalls em paralelo à entrevista |
| **roadmap** | sonnet | Read, Write, Grep, Glob, Bash | Decompõe o PRD no roadmap multi-arquivo com rastreabilidade |
| **simplifier** | sonnet | Read, Grep, Glob, Bash, Edit, Write | Refactor de qualidade em 2 passes: propõe simplificações com confiança ≥80%, aplica só as aprovadas pelo humano |

Personas interativas absorvidas nos commands (contexto principal):
interviewer (`discover`), architect (`design`), planner (`plan`), product
manager (`product prd`), quick engineer (`quick`).

---

## Comandos

### Setup & Configuração

| Comando | O que faz |
|---------|-----------|
| `/pwdev-code:init` | Inicializa o framework — cria `.planning/`, CLAUDE.md, settings, configura idioma, perfil de modelo e auditoria |
| `/pwdev-code:init mcp` | Configura servidores MCP (.mcp.json) |
| `/pwdev-code:init stack` | Detecta e configura a stack do projeto |
| `/pwdev-code:init claude` | Gera o CLAUDE.md (memória operacional) |

### Planejamento de Produto

| Comando | O que faz | Saída |
|---------|-----------|-------|
| `/pwdev-code:product prd` | Entrevista de produto → PRD estruturado | prd.md (10 seções) |
| `/pwdev-code:product roadmap` | Decompõe o PRD via subagente roadmap | .planning/product/roadmap/ (multi-arquivo com rastreabilidade) |
| `/pwdev-code:product stories` | Gera/refina histórias de usuário (padrão skill-user-stories) | .planning/product/stories/US-NN-*.md + índice |

### Fluxo de Desenvolvimento

| Comando | Fase | Gate de entrada | Saída |
|---------|------|----------------|-------|
| `/pwdev-code:discover` | DISCOVER | `.planning/` existe | project.md, requirements.md |
| `/pwdev-code:design` | DESIGN | project.md + requirements.md | spec.md, decisions.md |
| `/pwdev-code:plan` | PLAN | spec.md aprovado | planos com waves |
| `/pwdev-code:execute` | EXECUTE | Planos aprovados | Código + commits + summaries |
| `/pwdev-code:execute --fix` | EXECUTE | Fix plans do verify | Correções (máx 2 iterações) |
| `/pwdev-code:simplify` | EXECUTE→REVIEW (opcional) | Summaries ou escopo explícito | Simplificações aprovadas + commit refactor |
| `/pwdev-code:review` | REVIEW | Mudanças de código existem | code-review.md + qa-report.md (paralelo) |
| `/pwdev-code:verify` | VERIFY | Summaries existem, review gate OK | verify.md, fix plans |
| `/pwdev-code:verify --strict` | VERIFY | Gate final / pré-release | 2 verifiers em paralelo (FUNCTIONAL + COMPLIANCE), vale o pior veredito (≈2× custo) |
| `/pwdev-code:quick` | All-in-one | Descrição da task | Código + commit (tasks simples) |

`review` também aceita `--code-only`, `--tests-only`, `--diff HEAD~N`.

### Sessão, Diagnóstico & Manutenção

| Comando | Quando usar |
|---------|------------|
| `/pwdev-code:memory` | Curar a memória durável do projeto — `capture`, `list`, `show`, `forget`, `link`, `graph` |
| `/pwdev-code:session` / `session resume` | Ver progresso / retomar do state.md |
| `/pwdev-code:init map` | Primeiro contato com repositório existente |
| `/pwdev-code:health` / `health --deps` | Scorecard de saúde / auditoria de dependências |
| `/pwdev-code:audit` | Consultar a trilha de auditoria (summary, events, decisions, stats, export PDF, SQL) |
| `/pwdev-code:manager-skills` | Criar, listar ou auditar skills |
| `/pwdev-code:maintenance cleanup` / `changelog` | Arquivar artefatos / gerar changelog |

---

## Idioma & Modelos

### Idioma

Todos os comandos suportam **Português (PT-BR)** e **Inglês (EN)**.
Configurado no `/pwdev-code:init`, salvo em `.planning/config.json`,
protocolo em `references/language.md`.

### Perfil de Modelo

Só os subagentes resolvem modelo (fases interativas usam o modelo da sessão).
Fonte única de verdade: `references/model-profiles.md`.

| Subagente | performance | balanced (padrão) | economy |
|-----------|:-----------:|:-----------------:|:-------:|
| executor / roadmap | opus | sonnet | sonnet |
| advisor | opus | opus | sonnet |
| code-reviewer / qa / verifier | sonnet | sonnet | haiku |
| researcher | sonnet | haiku | haiku |

O executor ainda roteia **por task**: os planos declaram
`Complexity: low|medium|high`, e em `balanced`, por exemplo, tasks `high`
vão para opus enquanto `low`/`medium` ficam no sonnet (matriz em
`references/model-profiles.md`; o executor nunca roda em haiku).

Override por subagente com `model_overrides` no `.planning/config.json`:

```json
{
  "lang": "pt-BR",
  "model_profile": "balanced",
  "model_overrides": { "executor": "opus" },
  "parallel_execution": false,
  "external_models": { "reviewer": { "cmd": "codex exec", "enabled": false, "timeout_s": 300 } }
}
```

`parallel_execution` (padrão false) ativa os lotes paralelos opt-in com
isolamento por worktree. `external_models.reviewer` (opcional, manual)
permite ao `/pwdev-code:review` colher uma segunda opinião consultiva de uma
CLI externa — o comando é mostrado antes da primeira execução, e findings
externos nunca bloqueiam o gate sozinhos.

---

## Trilha de Auditoria (determinística, via hooks)

Banco SQLite opcional em `.planning/pwdev-audit.db` — **desabilitado por
padrão**, configurado no `/init`, nunca versionado.

A gravação é feita pelos hooks do plugin, não pelos agentes:

- `scripts/audit-hook.sh` (SessionStart, SubagentStart/Stop, PostToolUse,
  Stop) → eventos com `duration_ms` real, rastreio de artefatos
- `scripts/audit-log.sh` chamado pelos commands nos gates de fase →
  decisões, gate_passed / gate_rejected
- `scripts/guard-secrets.sh` (PreToolUse) → bloqueia leitura de `.env`,
  `*.pem`, `*.key`, `id_rsa*` (`.env.example` permitido)

Consulte com `/pwdev-code:audit`: `summary`, `events`, `decisions`,
`artifacts`, `stats`, `export` (PDF), `query <SELECT>`.

---

## Skills

Skills são packs de conhecimento de domínio que o executor e os revisores
consultam. Transformam saída genérica em resultado com qualidade de domínio.

Sem skill: `"Criar tabela de usuários"` → tabela funcional que renderiza dados.
Com skill de UI: → tabela com empty state, skeleton de loading, header sticky,
hover, visão de card no mobile, navegação por teclado, contraste AA.

### Skills Incluídas

| Skill | Domínio | Arquivos |
|-------|---------|----------|
| skill-frontend-design | UI enterprise — dashboards, painéis admin, SaaS, apps data-heavy | SKILL.md + TEMPLATES.md |
| skill-user-stories | Histórias de usuário — INVEST, ACs em Gherkin, definition of ready, checklist de revisão | SKILL.md |

Crie as suas com `/pwdev-code:manager-skills create <domínio>` — o wizard
detecta sua stack, entrevista você (máx 3 rounds) e gera a skill em
`.claude/skills/` seguindo o schema oficial de SKILL.md.

---

## Artefatos & Estrutura de Diretórios

```
.planning/
├── config.json                       # lang, model_profile, audit, parallel_execution, external_models, version
├── state.md                          # Fonte de verdade: posição, gates, fix_iteration
├── pwdev-audit.db                    # Trilha de auditoria (opt-in, gitignored)
│
├── context/                          # Conhecimento do projeto (permanente)
│   ├── project.md, requirements.md   # discover
│   ├── domain.md, stack.md, pitfalls.md        # subagente researcher
│   └── architecture.md, conventions.md, ...    # init map
│
├── memory/                           # conhecimento durável curado (VERSIONADO)
│   ├── MEMORY.md                     # índice — 1 linha por memória ativa
│   └── {decision|lesson|convention}-*.md
│
├── product/
│   ├── prd.md
│   ├── stories/                      # histórias de usuário (US-NN-*.md + index.md)
│   └── roadmap/                      # subagente roadmap (multi-arquivo)
│
├── phases/F01-slug/
│   ├── spec.md, decisions.md         # design
│   ├── plans/                        # plan (headers Wave/Depends)
│   ├── execution/                    # summaries do executor
│   ├── review/                       # code-review.md, qa-report.md
│   └── verify/                       # verify.md, fix-NN.md
│
├── quick/, reports/, templates/, archive/
```

---

## Regras de Ouro

```
 1. NUNCA execute sem um plano aprovado.
 2. NUNCA declare "pronto" sem verificação contra os ACs.
 3. SEMPRE respeite stop conditions — pare e pergunte.
 4. O SPEC.md é o contrato — todo executor DEVE lê-lo.
 5. Uma task, um commit, um escopo.
 6. Subagente fresco > sessão longa com context rot.
 7. Goal-backward: "o que precisa ser VERDADE?" > "o que fizemos?"
 8. Segurança não é opcional — e é garantida por hooks.
 9. Escale quando necessário — Quick → Standard → Full.
10. O humano tem a palavra final. Sempre.
```

---

## Licença

Apache-2.0 — Veja [LICENSE](./LICENSE)

*PWDEV-CODE v2.2.0 — A complexidade vive no sistema, não no seu fluxo de trabalho.*
*Mantido por [Paulo Soares](https://github.com/soarescbm)*
