# PWDEV Marketplace

*Leia em [English](./README.md)*

Marketplace de plugins para o [Claude Code](https://docs.anthropic.com/en/docs/claude-code).

---

## O que é a PWDEV

[Paulo Soares](https://github.com/soarescbm), CTO da PWDEV, empresa focada no desenvolvimento de soluções GovTech, acredita que a inteligência artificial está remodelando fundamentalmente o desenvolvimento de software. Mais do que uma tendência passageira, essa transformação representa uma nova forma de apoiar profissionais, ampliar capacidades e trazer maior consistência ao longo de todo o ciclo de desenvolvimento. Guiada por essa visão, a PWDEV disponibiliza essas soluções para ajudar equipes a trabalhar com mais estrutura, qualidade e previsibilidade.

Nossos plugins transformam o Claude Code de um assistente de codificação de uso geral em um parceiro de engenharia disciplinado, por meio de agentes especializados, fluxos de trabalho estruturados e pacotes de conhecimento específicos por domínio.

Filosofia central em todos os plugins:

> **Nunca execute sem um plano. Nunca entregue sem verificação.**

---

## Plugins

| Plugin | Descrição | Versão | Licença |
|--------|-----------|:------:|:------:|
| [**pwdev-code**](./plugins/pwdev-code/) | Framework de desenvolvimento orientado a especificação — 11 agentes, 6 fases, 21 comandos | 1.0.0 | Apache-2.0 |
| [**pwdev-uiux**](./plugins/pwdev-uiux/) | Framework de engenharia UI/UX — 7 agentes, fluxo de 5 fases, integração com Figma, WCAG 2.1 AA | 1.0.0 | Apache-2.0 |
| [**pwdev-feat**](./plugins/pwdev-feat/) | Desenvolvimento simplificado de features — planos PWDEVIA com 7 perguntas + executor, rápido e prático | 1.0.0 | Apache-2.0 |
| [**pwdev-prd**](./plugins/pwdev-prd/) | Criação de PRD guiada por entrevista — entrevista estruturada em 12 etapas, Markdown + JSON, agnóstico de tecnologia | 1.0.0 | Apache-2.0 |

### pwdev-code

Framework que orquestra **11 agentes especializados** em **6 fases** para garantir que cada linha de código seja planejada, rastreável e verificada.

```
PRD ─▶ ROADMAP ─▶ DISCOVER ─▶ DESIGN ─▶ PLAN ─▶ EXECUTE ─▶ REVIEW ─▶ VERIFY
```

**Agentes:** Product Manager, Delivery Lead, Requirements Engineer, Technical Analyst, Software Architect, Planning Engineer, Implementation Engineer, Code Reviewer, QA Engineer, Spec Verifier, Generalist Engineer

Veja a [documentação completa do plugin](./plugins/pwdev-code/README.md).

### pwdev-uiux

Framework de engenharia UI/UX para **Vue 3 + shadcn-vue (Reka UI v2)** que orquestra **7 agentes especializados** em um fluxo de trabalho de 5 fases.

```
UNDERSTAND ─▶ STRUCTURE ─▶ IMPLEMENT ─▶ REVIEW ─▶ HANDOFF
```

**Agentes:** Orchestrator, UX Analyst, Design Bridge, UI Scanner, UI Builder, A11y Reviewer, UX Critic

**Principais funcionalidades:** integração com Figma MCP, auditoria WCAG 2.1 AA, revisão UX em 7 eixos, habilidades contextuais específicas por projeto

Veja a [documentação completa do plugin](./plugins/pwdev-uiux/README.md).

### pwdev-feat

Desenvolvimento de features assistido por IA simplificado, utilizando a **metodologia PWDEVIA com 7 perguntas**. Descreva o que você quer, obtenha um plano estruturado e execute.

```
Describe ─▶ Plan ─▶ Execute
```

**Agentes:** PWDEVIA (Prompt Engineer) + Executor

**Tipos de plano:** Feature, Backend, Frontend, Test, Review, Quick

Veja a [documentação completa do plugin](./plugins/pwdev-feat/README.md).

### pwdev-prd

**Criação de PRD** guiada por entrevista com um processo estruturado em 12 etapas. Agnóstico de tecnologia, gera saída em Markdown + JSON opcional.

```
Interview (12 steps) ─▶ PRD.md ─▶ Export (JSON / GitHub Issue)
```

**Agente:** PRD Interview Specialist

**Saídas:** PRD estruturado com objetivos, métricas, requisitos funcionais/não-funcionais, arquitetura, riscos e critérios de aceitação

Veja a [documentação completa do plugin](./plugins/pwdev-prd/README.md).

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
# Desenvolvimento orientado a especificação (11 agentes, 6 fases)
claude plugin install pwdev-code@pwdev-claude-marketplace

# Engenharia UI/UX (8 agentes, Figma, WCAG, theming)
claude plugin install pwdev-uiux@pwdev-claude-marketplace

# Desenvolvimento simplificado de features (planos com 7 perguntas)
claude plugin install pwdev-feat@pwdev-claude-marketplace

# Criação de PRD guiada por entrevista (processo em 12 etapas)
claude plugin install pwdev-prd@pwdev-claude-marketplace
```

Instale apenas os plugins de que você precisa. Cada um funciona de forma independente.

---

## Licença

Apache-2.0

*Mantido por [Paulo Soares](https://github.com/pwdev-solucoes)*
