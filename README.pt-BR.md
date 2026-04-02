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

## Novidades da v1.1.0

- **Seleção de Idioma** — Todos os comandos agora suportam Português (PT-BR) e Inglês (EN). Configurado uma vez durante o `/init`, usado silenciosamente em todos os comandos.
- **Perfis de Modelo** — Escolha entre os perfis `performance`, `balanced` ou `economy` para controlar qual modelo Claude (Opus/Sonnet/Haiku) cada agente utiliza.
- **Trilha de Auditoria (opt-in)** — Banco de dados SQLite opcional em `.planning/pwdev-audit.db` registra todos os comandos, decisões e artefatos. Desativado por padrão, nunca versionado.
- **Configuração Unificada** — Idioma, perfil de modelo e configuração de auditoria armazenados em `.planning/config.json`, compartilhados entre todos os plugins.

---

## Plugins

| Plugin | Descrição | Versão | Licença |
|--------|-----------|:------:|:------:|
| [**pwdev-code**](./plugins/pwdev-code/) | Framework de desenvolvimento orientado a especificação — 11 agentes, 6 fases, 21 comandos | 1.1.0 | Apache-2.0 |
| [**pwdev-uiux**](./plugins/pwdev-uiux/) | Framework de engenharia UI/UX — 7 agentes, fluxo de 5 fases, integração com Figma, WCAG 2.1 AA | 1.1.0 | Apache-2.0 |
| [**pwdev-feat**](./plugins/pwdev-feat/) | Desenvolvimento simplificado de features — planos PWDEVIA com 7 perguntas + executor, rápido e prático | 1.1.0 | Apache-2.0 |
| [**pwdev-prd**](./plugins/pwdev-prd/) | Criação de PRD guiada por entrevista — entrevista estruturada em 12 etapas, Markdown + JSON, agnóstico de tecnologia | 1.1.0 | Apache-2.0 |

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

Cada plugin usa agentes especializados que podem rodar em diferentes modelos Claude. Os perfis de modelo permitem equilibrar qualidade vs. custo:

| Perfil | Orquestrador | Planner / Executor | Reviewer | Scanner |
|--------|:----------:|:-----------------:|:--------:|:-------:|
| **performance** | Opus | Opus | Sonnet | Sonnet |
| **balanced** | Opus | Sonnet | Sonnet | Haiku |
| **economy** | Sonnet | Sonnet | Haiku | Haiku |

- Durante o `/init`: você escolhe um perfil (padrão: balanced)
- Override de agentes específicos: `model_overrides` no config.json

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
claude plugin install pwdev-code@pwdev-claude-marketplace
claude plugin install pwdev-uiux@pwdev-claude-marketplace
claude plugin install pwdev-feat@pwdev-claude-marketplace
claude plugin install pwdev-prd@pwdev-claude-marketplace
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
