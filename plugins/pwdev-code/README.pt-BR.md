# PWDEV-CODE v1.1.1

*Leia em [English](./README.md)*

> **Framework de Desenvolvimento Orientado a Especificações para o Claude Code**

```
Never execute without a plan. Never ship without verification.
```

O PWDEV-CODE orquestra **11 agentes especializados** em **5 fases** usando **3 camadas** para garantir que cada linha de código seja planejada, rastreável e verificada.

---

## Metodologia

### O Problema

Sem um framework estruturado, o Claude gera código ad-hoc sem um plano, os critérios de aceitação ficam subjetivos, a degradação de contexto compromete a qualidade em sessões longas, as decisões se tornam não rastreáveis e a verificação está ausente.

### Arquitetura de 3 Camadas

O framework separa **o que** fazer, **quem** faz e **com qual** conhecimento:

```
┌─────────────────────────────────────────────────────────────┐
│  LAYER 1 — COMMANDS (commands/)                             │
│  "WHAT to do" — orchestration, gates, flow, persistence     │
├─────────────────────────────────────────────────────────────┤
│  LAYER 2 — AGENTS (agents/)                                 │
│  "WHO does it" — persona, rules, prohibitions, stop conds   │
├─────────────────────────────────────────────────────────────┤
│  LAYER 3 — SKILLS (skills/)                                 │
│  "WITH WHAT knowledge" — guidelines, patterns, anti-patterns│
└─────────────────────────────────────────────────────────────┘
```

Cada camada é independente: o **agent-executor** é chamado por 3 comandos diferentes (execute, quick, fix-plans) — a persona existe uma vez e é reutilizada. Skills são pacotes de conhecimento intercambiáveis. Os comandos definem o fluxo sem conhecer as regras de implementação.

### 5 Fases

Cada funcionalidade passa por um pipeline estruturado com portões de aprovação humana:

```
DISCOVER  ─▶  DESIGN  ─▶  PLAN  ─▶  EXECUTE  ─▶  REVIEW  ─▶  VERIFY
   │            │           │          │           │           │
Interview    spec.md     Atomic     Code        Code review  Goal-backward
+ Research   + Decisions tasks      + Commits   + QA audit   + AC/DoD
```

| Fase | O que acontece | Saída |
|------|---------------|-------|
| **DISCOVER** | Entrevista o usuário (máx. 3 rodadas), mapeia o código-base silenciosamente, sintetiza os requisitos | project.md, requirements.md |
| **DESIGN** | Toma e documenta decisões arquiteturais, gera o contrato de execução | spec.md (8 seções), decisions.md |
| **PLAN** | Decompõe o spec.md em tarefas atômicas organizadas em ondas (paralelas/sequenciais) | plan.md com tarefas (máx. 3 por plano, máx. 5 arquivos cada) |
| **EXECUTE** | Implementa cada tarefa em contexto limpo, executa lint, testes e commit atômico | Código + commits + summary.md por tarefa |
| **REVIEW** | Revisão de código (bugs, segurança, performance) + auditoria de testes QA (cobertura, lacunas) em paralelo | code-review.md + qa-report.md |
| **VERIFY** | Validação retroativa a partir do objetivo: "o que precisa ser VERDADEIRO?" em vez de "o que fizemos?" | verify.md com veredicto, fix-plan.md se rejeitado |

**Regras de transição:** cada portão requer aprovação humana. REVIEW deve ser aprovado (zero achados críticos) antes do VERIFY. O VERIFY aprova (concluído) ou gera planos de correção que voltam para o EXECUTE.

### Níveis de Intensidade

Nem tudo precisa das 6 fases:

| Nível | Quando usar | Fluxo |
|-------|------------|-------|
| **Quick** | Correção de bug, configuração, 1 a 3 arquivos | mini-plan → execute → mini-review → mini-verify |
| **Standard** | Feature média, 2 a 5 arquivos | DISCOVER → PLAN → EXECUTE → REVIEW → VERIFY |
| **Full** | Feature complexa, novo projeto | PRD → ROADMAP → todas as 6 fases por feature |

**Escalonamento automático:** mais de 5 arquivos → Standard. Decisão arquitetural → Standard. Migração/schema → Full.

### spec.md — O Contrato Central

Gerado pelo agent-architect, governa toda a execução downstream. 8 seções obrigatórias:

| # | Seção | Propósito |
|---|-------|----------|
| 1 | **Persona** | Stack, senioridade, skills ativas |
| 2 | **Objective** | O que precisa existir ao final (1 a 3 sentenças mensuráveis) |
| 3 | **Inputs** | Entidades, endpoints, regras de negócio |
| 4 | **Format** | Estrutura de arquivos, convenções de nomenclatura |
| 5 | **Quality** | Testes, lint, performance + critérios específicos de skill |
| 6 | **Stop Conditions** | Quando o executor DEVE parar e perguntar (mín. 5) |
| 7 | **Prohibitions** | O que NUNCA fazer (específico + global) |
| 8 | **Definition of Done** | Checklist verificável com comandos reais |

### Gerenciamento de Contexto

O framework combate a **degradação de contexto** — a deterioração que ocorre quando a janela de contexto do Claude se esgota:

```
Context 0-30%   → Maximum quality
Context 50%+    → Starts cutting corners
Context 70%+    → Hallucinations, forgets requirements
```

**Solução:** cada tarefa executa em **contexto limpo** (subagente) recebendo apenas: tarefa + spec.md (seções 1, 6, 7) + skills ativas + arquivos listados. Nada mais. Zero de histórico.

Salvaguardas adicionais: máximo de 3 tarefas por plano, state.md para persistência entre sessões, `/pwdev-code:context` para atualizar o contexto antes de retomar após longas pausas.

---

### Novidades da v1.1.1

- **Seleção de Idioma** — Todos os comandos suportam PT-BR e EN. Configurado durante o `/pwdev-code:init`.
- **Perfis de Modelo** — Modelos dos agentes configuráveis via perfis `performance`, `balanced` ou `economy`.
- **Trilha de Auditoria (opt-in)** — Registro SQLite opcional de comandos, decisões e artefatos. Desativado por padrão.
- **Gerenciamento de Skills** — Novo comando `/pwdev-code:skill` para criar skills de backend/frontend, listar skills instaladas e auditar uso.
- **Setup Unificado** — `setup-mcp` renomeado para `/pwdev-code:setup` com subcomandos (`setup mcp`, `setup stack`).
- **Health Consolidado** — `/pwdev-code:deps` integrado ao `/pwdev-code:health --deps`.
- **Estrutura de diretórios organizada** — Artefatos reorganizados em `context/`, `product/`, `phases/{slug}/`, `quick/` e `reports/`. Cada fase tem sua própria pasta com spec, planos, execução, revisão e verificação isolados.

### Verificação — Retroativa a Partir do Objetivo

O verificador não pergunta "o que fizemos?" — ele pergunta **"o que precisa ser VERDADEIRO para que isso esteja concluído?"**

Fontes de verdade: objetivo + qualidade + DoD do spec.md, ACs das tarefas, checklists de skills, proibições (não violadas).

| Veredicto | Critério |
|-----------|---------|
| **APPROVED** | 100% dos ACs + 100% do DoD + 0 proibições violadas |
| **WITH CAVEATS** | >=90% dos ACs + apenas falhas de baixa severidade |
| **REJECTED** | <90% dos ACs OU proibição crítica OU item crítico do DoD falhando |

---

## Agentes

### Produto & Estratégia

| Agente | Papel | Chamado por | O que faz |
|--------|-------|------------|----------|
| **agent-prd** | Product Manager | `prd` | Entrevista o usuário (3 rodadas), gera prd.md com 10 seções, prioriza com MoSCoW |
| **agent-roadmap** | Delivery Lead | `roadmap` | Decompõe o PRD em hierarquia Phase → Epic → Feature → Task, gera roadmap multi-arquivo com matriz de rastreabilidade |

### Descoberta & Design

| Agente | Papel | Chamado por | O que faz |
|--------|-------|------------|----------|
| **agent-interviewer** | Requirements Engineer | `discover` | Mapeia o código-base silenciosamente, conduz entrevista estruturada (máx. 3 rodadas), sintetiza project.md + requirements.md |
| **agent-researcher** | Technical Analyst | `discover` | Investiga versões do stack, compatibilidade, problemas conhecidos, gera context/domain.md, stack.md, pitfalls.md |
| **agent-architect** | Software Architect | `design` | Toma decisões de design documentadas (opções/escolha/trade-off), gera spec.md (8 seções) + decisions.md |

### Planejamento & Execução

| Agente | Papel | Chamado por | O que faz |
|--------|-------|------------|----------|
| **agent-planner** | Planning Engineer | `plan` | Decompõe o spec.md em tarefas atômicas organizadas em ondas, valida 100% de cobertura contra a spec |
| **agent-executor** | Implementation Engineer | `execute`, `quick`, fix-plans | Implementa uma tarefa por vez em contexto limpo, segue SPEC + skills, commita atomicamente, gera summary.md |
| **agent-quick** | Generalist Engineer | `quick` | Tudo-em-um para tarefas simples: mini-discovery → mini-plan → implementa → mini-review → mini-verify → commit |

### Qualidade & Revisão

| Agente | Papel | Chamado por | O que faz |
|--------|-------|------------|----------|
| **agent-code-reviewer** | Senior Code Reviewer | `review` | Revisa código quanto a bugs, segurança, performance, arquitetura e convenções — gera code-review.md |
| **agent-qa** | QA Test Specialist | `review`, `qa` | Audita cobertura de testes, rastreia requisitos até os testes, identifica lacunas, sugere esboços de testes — gera qa-report.md |
| **agent-verifier** | Spec Verifier | `verify` | Validação retroativa a partir do objetivo contra spec.md + ACs das tarefas + checklists de skills, gera verify.md ou fix-plan.md |

---

## Comandos

### Configuração & Setup

| Comando | O que faz |
|---------|----------|
| `/pwdev-code:init` | Inicializa o framework no repositório — cria `.planning/`, CLAUDE.md, configurações, configura idioma e perfil de modelo |
| `/pwdev-code:setup` | Setup do projeto — servidores MCP, detecção de stack (`setup mcp`, `setup stack`) |

### Planejamento de Produto

| Comando | O que faz | Saída |
|---------|----------|-------|
| `/pwdev-code:prd` | Entrevista de descoberta de produto → PRD estruturado | prd.md (10 seções) |
| `/pwdev-code:roadmap` | Decompõe o PRD em roadmap executável | .planning/roadmap/ (multi-arquivo com rastreabilidade) |

### Fluxo de Desenvolvimento

| Comando | Fase | Portão de Entrada | Saída |
|---------|------|------------------|-------|
| `/pwdev-code:discover` | DISCOVER | `.planning/` existe | project.md, requirements.md |
| `/pwdev-code:design` | DESIGN | project.md + requirements.md | spec.md, decisions.md |
| `/pwdev-code:plan` | PLAN | spec.md aprovado | plan.md (tarefas atômicas em ondas) |
| `/pwdev-code:execute` | EXECUTE | PLANs aprovados | Código + commits + summary.md |
| `/pwdev-code:review` | REVIEW | Alterações de código existem | code-review.md + qa-report.md |
| `/pwdev-code:verify` | VERIFY | SUMMARYs existem | verify.md, fix-plan.md |
| `/pwdev-code:quick` | Tudo-em-um | Descrição da tarefa | Código + commit (para tarefas simples) |

### Sessão & Progresso

| Comando | Quando usar |
|---------|------------|
| `/pwdev-code:status` | Verificar fase atual, plano, tarefa e progresso |
| `/pwdev-code:resume` | Retomar de onde parou (lê state.md) |
| `/pwdev-code:context` | Atualizar contexto antes de executar após uma longa pausa |

### Análise & Diagnóstico

| Comando | Quando usar |
|---------|------------|
| `/pwdev-code:map-codebase` | Primeiro contato com repositório existente — analisa stack, padrões, convenções, riscos |
| `/pwdev-code:health` | Scorecard de saúde do projeto — testes, lint, dependências, segurança |
| `/pwdev-code:health --deps` | Auditoria focada de dependências — versões, vulnerabilidades, pacotes depreciados |
| `/pwdev-code:audit` | Consultar a trilha de auditoria — resumo, eventos, decisões, artefatos, estatísticas, exportar PDF |
| `/pwdev-code:skill` | Criar, listar ou auditar skills (`skill create backend`, `skill create frontend`, `skill list`, `skill audit`) |

### Release & Manutenção

| Comando | Quando usar |
|---------|------------|
| `/pwdev-code:changelog` | Gerar changelog a partir do histórico de commits |
| `/pwdev-code:cleanup` | Arquivar artefatos de fases concluídas em `.planning/archive/` |

---

## Configuração de Idioma e Modelo

### Idioma

Todos os comandos suportam **Português (PT-BR)** e **Inglês (EN)**. Configurado durante o `/pwdev-code:init` e armazenado em `.planning/config.json`.

- `/pwdev-code:init` — sempre pergunta a preferência de idioma
- Outros comandos — usam a preferência salva silenciosamente
- Override — mude de idioma durante a conversa e confirme quando solicitado

### Perfil de Modelo

Os modelos dos agentes são configuráveis via perfis definidos durante o `/pwdev-code:init`:

| Perfil | architect / planner / roadmap | interviewer / prd | executor / quick | code-reviewer / qa | researcher | verifier |
|--------|:---------------------------:|:-----------------:|:----------------:|:------------------:|:----------:|:--------:|
| **performance** | Opus | Opus | Opus | Sonnet | Sonnet | Sonnet |
| **balanced** | Sonnet | Sonnet | Sonnet | Sonnet | Sonnet | Haiku |
| **economy** | Sonnet | Sonnet | Sonnet | Haiku | Haiku | Haiku |

Override de agentes específicos com `model_overrides` em `.planning/config.json`:

```json
{
  "lang": "pt-BR",
  "model_profile": "balanced",
  "model_overrides": {
    "agent-architect": "opus"
  }
}
```

---

## Trilha de Auditoria

Todos os plugins compartilham um banco de dados SQLite opcional em `.planning/pwdev-audit.db`. Ele é **desativado por padrão** e configurado durante o `/init`. O arquivo do banco nunca é versionado (adicionado automaticamente ao `.gitignore`).

A trilha de auditoria registra:
- **Eventos** — cada execução de comando (início, conclusão, falha) com timestamp, agente, modelo e fase
- **Decisões** — decisões arquiteturais e de produto com justificativa e alternativas consideradas
- **Artefatos** — arquivos criados ou modificados pelo framework, com rastreamento de status
- **Alterações de config** — histórico de alterações de idioma, perfil de modelo e outras configurações

O banco de auditoria funciona **em paralelo** com os arquivos Markdown — os agentes continuam lendo e escrevendo Markdown como antes. O SQLite é uma camada adicional para histórico e análise.

### Consultando a Trilha de Auditoria

Use `/pwdev-code:audit` para consultar o banco interativamente:

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

Adicione `.planning/pwdev-audit.db` ao `.gitignore` (recomendado).

---

## Skills

Skills são pacotes de conhecimento de domínio versionados que os agentes consultam. Eles transformam saídas genéricas em resultados com qualidade de domínio.

Sem skill: `"Create users table"` → tabela funcional que exibe dados.
Com skill-uiux: → tabela com estado vazio, skeleton de carregamento, cabeçalho fixo, destaque ao passar o mouse, visualização em card para mobile, navegação por teclado, contraste AA.

### Skills Incluídas

| Skill | Domínio |
|-------|---------|
| skill-frontend-design | Design de UI corporativo — dashboards, painéis administrativos, interfaces SaaS, aplicações com grande volume de dados |

### Anatomia de uma Skill

```
skills/skill-name/
├── SKILL.md              # Main file (<500 lines)
│   ├── Frontmatter       # name, description (activation triggers)
│   ├── Principles        # 3-5 fundamental principles
│   ├── Guidelines        # Practical rules with examples
│   ├── Anti-Patterns     # never do / why / alternative
│   └── Integration       # How it affects SPEC, PLAN, VERIFY
└── references/           # On-demand lookup (unlimited size)
```

### Catálogo de Skills Instaláveis

skill-laravel, skill-vue3-primevue, skill-react-chakra, skill-api-design, skill-security,
skill-testing, skill-performance, skill-devops, skill-data-modeling, skill-docs

---

## Artefatos & Estrutura de Diretórios

```
.planning/
├── config.json                       # Configuração unificada
├── state.md                          # Estado global do workflow
├── pwdev-audit.db                    # Trilha de auditoria (opt-in, .gitignore)
│
├── context/                          # Conhecimento do projeto (permanente)
│   ├── project.md                    # Visão do produto (discover)
│   ├── requirements.md               # Requisitos (discover)
│   ├── domain.md                     # Conceitos do domínio (researcher)
│   ├── stack.md                      # Stack técnico (researcher)
│   ├── pitfalls.md                   # Riscos conhecidos (researcher)
│   ├── architecture.md               # Arquitetura (map-codebase)
│   ├── conventions.md                # Convenções (map-codebase)
│   ├── dependencies.md               # Dependências (map-codebase)
│   └── concerns.md                   # Preocupações técnicas (map-codebase)
│
├── product/                          # Planejamento de produto
│   ├── prd.md                        # Documento de Requisitos do Produto
│   └── roadmap/                      # Roadmap hierárquico
│       ├── roadmap.md, traceability.md, risks.md, metrics.md
│       └── F01-slug/                 # Fase → Épico → Feature
│
├── phases/                           # Execução (uma pasta por fase)
│   └── F01-user-auth/                # Pasta da fase
│       ├── spec.md                   # Contrato de design desta fase
│       ├── decisions.md              # Decisões arquiteturais
│       ├── plans/                    # Planos de execução (waves)
│       │   ├── 01-models.md
│       │   └── 02-services.md
│       ├── execution/                # Resultados da implementação
│       │   ├── 01-summary.md
│       │   └── executor-context.md
│       ├── review/                   # Verificações de qualidade
│       │   ├── code-review.md
│       │   └── qa-report.md
│       └── verify/                   # Aceitação
│           ├── verify.md
│           └── fix-01.md             # Plano de correção (se rejeitado)
│
├── quick/                            # Tarefas leves (sem fluxo de fases)
│   └── fix-login/
│       ├── plan.md, summary.md, verify.md
│
├── reports/                          # Diagnósticos e checklists
│   ├── health/, deps/, checklists/
│
├── templates/                        # Templates reutilizáveis
└── archive/                          # Fases concluídas (movidas pelo cleanup)
```

| Artefato | Criado por | Localização |
|----------|-----------|-------------|
| config.json | init | `.planning/config.json` |
| state.md | init, todos | `.planning/state.md` |
| project.md | discover | `.planning/context/project.md` |
| requirements.md | discover | `.planning/context/requirements.md` |
| domain/stack/pitfalls | researcher | `.planning/context/` |
| architecture/conventions | map-codebase | `.planning/context/` |
| prd.md | prd | `.planning/product/prd.md` |
| roadmap | roadmap | `.planning/product/roadmap/` |
| spec.md | design | `.planning/phases/{slug}/spec.md` |
| decisions.md | design | `.planning/phases/{slug}/decisions.md` |
| plans | plan | `.planning/phases/{slug}/plans/` |
| summaries | execute | `.planning/phases/{slug}/execution/` |
| code-review.md | review | `.planning/phases/{slug}/review/` |
| qa-report.md | review | `.planning/phases/{slug}/review/` |
| verify.md | verify | `.planning/phases/{slug}/verify/` |
| fix plans | verify | `.planning/phases/{slug}/verify/` |

---

## Regras de Ouro

```
 1. NEVER execute without an approved plan.
 2. NEVER declare "done" without verification against AC.
 3. ALWAYS respect stop conditions — stop and ask.
 4. SPEC.md is the contract — every executor MUST read it.
 5. One task, one commit, one scope.
 6. Fresh subagent > long session with context rot.
 7. Goal-backward: "what must be TRUE?" > "what did we do?"
 8. Security is not optional.
 9. Escalate when needed — Quick → Standard → Full.
10. The human has the final word. Always.
```

---

## Licença

Apache-2.0 — Veja [LICENSE](./LICENSE)

*PWDEV-CODE v1.1.1 — A complexidade vive no sistema, não no seu fluxo de trabalho.*
*Mantido por [Paulo Soares](https://github.com/soarescbm)*
