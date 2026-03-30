# PWDEV-CODE v1.0.0

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
Interview    SPEC.md     Atomic     Code        Code review  Goal-backward
+ Research   + Decisions tasks      + Commits   + QA audit   + AC/DoD
```

| Fase | O que acontece | Saída |
|------|---------------|-------|
| **DISCOVER** | Entrevista o usuário (máx. 3 rodadas), mapeia o código-base silenciosamente, sintetiza os requisitos | PROJECT.md, REQUIREMENTS.md |
| **DESIGN** | Toma e documenta decisões arquiteturais, gera o contrato de execução | SPEC.md (8 seções), CONTEXT.md |
| **PLAN** | Decompõe o SPEC.md em tarefas atômicas organizadas em ondas (paralelas/sequenciais) | PLAN.md com tarefas (máx. 3 por plano, máx. 5 arquivos cada) |
| **EXECUTE** | Implementa cada tarefa em contexto limpo, executa lint, testes e commit atômico | Código + commits + SUMMARY.md por tarefa |
| **REVIEW** | Revisão de código (bugs, segurança, performance) + auditoria de testes QA (cobertura, lacunas) em paralelo | CODE-REVIEW.md + QA-REPORT.md |
| **VERIFY** | Validação retroativa a partir do objetivo: "o que precisa ser VERDADEIRO?" em vez de "o que fizemos?" | VERIFY.md com veredicto, FIX-PLAN.md se rejeitado |

**Regras de transição:** cada portão requer aprovação humana. REVIEW deve ser aprovado (zero achados críticos) antes do VERIFY. O VERIFY aprova (concluído) ou gera planos de correção que voltam para o EXECUTE.

### Níveis de Intensidade

Nem tudo precisa das 6 fases:

| Nível | Quando usar | Fluxo |
|-------|------------|-------|
| **Quick** | Correção de bug, configuração, 1 a 3 arquivos | mini-plan → execute → mini-review → mini-verify |
| **Standard** | Feature média, 2 a 5 arquivos | DISCOVER → PLAN → EXECUTE → REVIEW → VERIFY |
| **Full** | Feature complexa, novo projeto | PRD → ROADMAP → todas as 6 fases por feature |

**Escalonamento automático:** mais de 5 arquivos → Standard. Decisão arquitetural → Standard. Migração/schema → Full.

### SPEC.md — O Contrato Central

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

**Solução:** cada tarefa executa em **contexto limpo** (subagente) recebendo apenas: tarefa + SPEC.md (seções 1, 6, 7) + skills ativas + arquivos listados. Nada mais. Zero de histórico.

Salvaguardas adicionais: máximo de 3 tarefas por plano, STATE.md para persistência entre sessões, `/pwdev-code:context` para atualizar o contexto antes de retomar após longas pausas.

### Verificação — Retroativa a Partir do Objetivo

O verificador não pergunta "o que fizemos?" — ele pergunta **"o que precisa ser VERDADEIRO para que isso esteja concluído?"**

Fontes de verdade: objetivo + qualidade + DoD do SPEC.md, ACs das tarefas, checklists de skills, proibições (não violadas).

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
| **agent-prd** | Product Manager | `prd` | Entrevista o usuário (3 rodadas), gera PRD.md com 10 seções, prioriza com MoSCoW |
| **agent-roadmap** | Delivery Lead | `roadmap` | Decompõe o PRD em hierarquia Phase → Epic → Feature → Task, gera roadmap multi-arquivo com matriz de rastreabilidade |

### Descoberta & Design

| Agente | Papel | Chamado por | O que faz |
|--------|-------|------------|----------|
| **agent-interviewer** | Requirements Engineer | `discover` | Mapeia o código-base silenciosamente, conduz entrevista estruturada (máx. 3 rodadas), sintetiza PROJECT.md + REQUIREMENTS.md |
| **agent-researcher** | Technical Analyst | `discover` | Investiga versões do stack, compatibilidade, problemas conhecidos, gera research/domain.md, stack.md, pitfalls.md |
| **agent-architect** | Software Architect | `design` | Toma decisões de design documentadas (opções/escolha/trade-off), gera SPEC.md (8 seções) + CONTEXT.md |

### Planejamento & Execução

| Agente | Papel | Chamado por | O que faz |
|--------|-------|------------|----------|
| **agent-planner** | Planning Engineer | `plan` | Decompõe o SPEC.md em tarefas atômicas organizadas em ondas, valida 100% de cobertura contra a spec |
| **agent-executor** | Implementation Engineer | `execute`, `quick`, fix-plans | Implementa uma tarefa por vez em contexto limpo, segue SPEC + skills, commita atomicamente, gera SUMMARY.md |
| **agent-quick** | Generalist Engineer | `quick` | Tudo-em-um para tarefas simples: mini-discovery → mini-plan → implementa → mini-review → mini-verify → commit |

### Qualidade & Revisão

| Agente | Papel | Chamado por | O que faz |
|--------|-------|------------|----------|
| **agent-code-reviewer** | Senior Code Reviewer | `review` | Revisa código quanto a bugs, segurança, performance, arquitetura e convenções — gera CODE-REVIEW.md |
| **agent-qa** | QA Test Specialist | `review`, `qa` | Audita cobertura de testes, rastreia requisitos até os testes, identifica lacunas, sugere esboços de testes — gera QA-REPORT.md |
| **agent-verifier** | Spec Verifier | `verify` | Validação retroativa a partir do objetivo contra SPEC.md + ACs das tarefas + checklists de skills, gera VERIFY.md ou FIX-PLAN.md |

---

## Comandos

### Configuração & Setup

| Comando | O que faz |
|---------|----------|
| `/pwdev-code:init` | Inicializa o framework no repositório — cria `.planning/`, CLAUDE.md, configurações |
| `/pwdev-code:setup-mcp` | Configura servidores MCP interativamente — detecta o stack, sugere servidores relevantes, gera `.mcp.json` |

### Planejamento de Produto

| Comando | O que faz | Saída |
|---------|----------|-------|
| `/pwdev-code:prd` | Entrevista de descoberta de produto → PRD estruturado | PRD.md (10 seções) |
| `/pwdev-code:roadmap` | Decompõe o PRD em roadmap executável | .planning/roadmap/ (multi-arquivo com rastreabilidade) |

### Fluxo de Desenvolvimento

| Comando | Fase | Portão de Entrada | Saída |
|---------|------|------------------|-------|
| `/pwdev-code:discover` | DISCOVER | `.planning/` existe | PROJECT.md, REQUIREMENTS.md |
| `/pwdev-code:design` | DESIGN | PROJECT.md + REQUIREMENTS.md | SPEC.md, CONTEXT.md |
| `/pwdev-code:plan` | PLAN | SPEC.md aprovado | PLAN.md (tarefas atômicas em ondas) |
| `/pwdev-code:execute` | EXECUTE | PLANs aprovados | Código + commits + SUMMARY.md |
| `/pwdev-code:review` | REVIEW | Alterações de código existem | CODE-REVIEW.md + QA-REPORT.md |
| `/pwdev-code:verify` | VERIFY | SUMMARYs existem | VERIFY.md, FIX-PLAN.md |
| `/pwdev-code:quick` | Tudo-em-um | Descrição da tarefa | Código + commit (para tarefas simples) |

### Sessão & Progresso

| Comando | Quando usar |
|---------|------------|
| `/pwdev-code:status` | Verificar fase atual, plano, tarefa e progresso |
| `/pwdev-code:resume` | Retomar de onde parou (lê STATE.md) |
| `/pwdev-code:context` | Atualizar contexto antes de executar após uma longa pausa |

### Análise & Diagnóstico

| Comando | Quando usar |
|---------|------------|
| `/pwdev-code:map-codebase` | Primeiro contato com repositório existente — analisa stack, padrões, convenções, riscos |
| `/pwdev-code:health` | Scorecard de saúde do projeto — testes, lint, dependências, segurança |
| `/pwdev-code:deps` | Auditoria de dependências — versões, vulnerabilidades, pacotes depreciados |

### Release & Manutenção

| Comando | Quando usar |
|---------|------------|
| `/pwdev-code:checklist` | Gerar checklists antes de release, revisão, deploy ou auditoria de segurança |
| `/pwdev-code:changelog` | Gerar changelog a partir do histórico de commits |
| `/pwdev-code:cleanup` | Arquivar artefatos de fases concluídas em `.planning/archive/` |

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

## Artefatos

| Artefato | Gerado por | Consumido por | Localização |
|----------|-----------|--------------|-------------|
| CLAUDE.md | init | Todos os agentes | Raiz do projeto |
| PRD.md | agent-prd | agent-roadmap | Raiz do projeto |
| PROJECT.md | agent-interviewer | Todos | .planning/ |
| REQUIREMENTS.md | agent-interviewer | agent-architect | .planning/ |
| **SPEC.md** | **agent-architect** | **Todos os executores** | **.planning/** |
| PLAN.md | agent-planner | agent-executor | .planning/phases/ |
| SUMMARY.md | agent-executor | agent-code-reviewer, agent-qa | .planning/phases/ |
| CODE-REVIEW.md | agent-code-reviewer | agent-verifier | .planning/phases/ |
| QA-REPORT.md | agent-qa | agent-verifier | .planning/phases/ |
| VERIFY.md | agent-verifier | Humano | .planning/phases/ |
| FIX-PLAN.md | agent-verifier | agent-executor | .planning/phases/ |
| STATE.md | Todos (atualizam) | Todos (leem) | .planning/ |

**Numeração de tarefas:** `{phase}-{plan}-{task}` — ex.: `01-02-03` = fase 1, plano 2, tarefa 3.

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

*PWDEV-CODE v1.0.0 — A complexidade vive no sistema, não no seu fluxo de trabalho.*
*Mantido por [Paulo Soares](https://github.com/pwdev-solucoes)*
