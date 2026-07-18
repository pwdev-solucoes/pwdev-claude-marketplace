# PWDEV-UIUX v2.0.0

> **Framework de Engenharia UI/UX Agnóstico de Stack para Claude Code**

*Leia em [English](./README.md)*

```
Configure sua stack → Analise → Implemente → Revise → Entregue
```

PWDEV-UIUX orquestra **6 subagentes reais + 2 personas inline** em um **fluxo de 5 fases** para produzir componentes de UI orientados por especificação, acessíveis (WCAG 2.1 AA) e consistentes com o seu projeto. Funciona com qualquer stack frontend moderno.

---

## Primeiros Passos

### Passo 1 — Instalar

```bash
claude plugin install pwdev-uiux@pwdev-claude-marketplace
```

### Passo 2 — Inicializar

```
/pwdev-uiux:init
```

Este comando faz tudo de uma vez:
- Cria o workspace `.planning/ui/`
- Pergunta idioma (PT-BR / EN) e perfil de modelo
- Detecta o framework frontend do projeto
- Solicita a escolha da stack de UI (shadcn-vue, shadcn-react, primevue, untitled-ui, tailwind-plus ou custom)
- Verifica a conexão com o Figma MCP

### Passo 3 — Comece a construir

Escolha o caminho conforme o contexto do projeto:

**Brownfield** (projeto existente com componentes de UI):
```
/pwdev-uiux:scan                                  # analisa padrões + verificação de conformidade
/pwdev-uiux:start "descrição da sua tarefa"       # inicia o fluxo de 5 fases
```

**Greenfield** (projeto novo, sem UI existente):
```
/pwdev-uiux:theme create                          # gera tema semântico de cores
/pwdev-uiux:start "descrição da sua tarefa"       # inicia o fluxo de 5 fases
```

**Com designs do Figma disponíveis**:
```
/pwdev-uiux:setup-figma                           # conecta o Figma MCP (uma vez)
/pwdev-uiux:theme from-figma                      # extrai tema das variáveis do Figma
/pwdev-uiux:start "descrição da sua tarefa"       # specs do Figma extraídas na Fase 2
```

Pronto. O orquestrador guia você pelas 5 fases automaticamente.

### Comandos opcionais de configuração

| Comando | Quando usar |
|---------|------------|
| `/pwdev-uiux:stack` | Alterar a stack de UI após o init |
| `/pwdev-uiux:setup-figma` | Conectar a integração com o Figma |
| `/pwdev-uiux:scan` | Re-analisar após mudanças significativas no projeto |
| `/pwdev-uiux:theme create` | Gerar um novo tema antes de construir |

---

## Novidades da v2.0.0

Reconstruído sobre o sistema moderno de plugins do Claude Code. Nenhum slash
command renomeado ou removido.

- **Orquestração híbrida**: orchestrator e theme-builder agora são personas
  INLINE (`references/workflow.md`, `references/theme-method.md`) — eles
  interagem com o humano nos gates e entrevistas, o que subagentes não
  fazem. Os outros 6 agents viraram **subagentes reais** spawnados via Task
  tool com frontmatter oficial (description, tools restritas, `maxTurns`) e
  paralelismo real (a11y-reviewer + ux-critic na mesma mensagem;
  design-bridge + ux-analyst com Figma).
- **Campos proibidos removidos dos agents**: `permissionMode`, `mcpServers`
  e o `skills:` não-oficial. Skills são passadas como paths explícitos de
  SKILL.md em cada spawn (a premissa antiga de "carregamento automático via
  frontmatter" era falsa). As tools MCP do Figma vivem no nível da SESSÃO
  (`/pwdev-uiux:setup-figma`); `push-to-figma` roda inline onde essas tools
  existem.
- **Auditoria determinística via hooks** no banco compartilhado
  `.planning/pwdev-audit.db` (`WHERE plugin='pwdev-uiux'`):
  `duration_ms`/`session_id` reais, `config_changes` populada pelo init,
  hook de guarda de segredos.
- **References empacotadas**: workflow, theme-method, spawn-contracts,
  model-profiles (fonte única — as 3 cópias divergentes com papéis
  fantasmas sumiram), language, audit-schema.
- **Overrides de modelo com namespace**: chaves `uiux-<agent>` na config
  compartilhada (nunca nomes simples).
- **Correções**: guard de query do audit endurecido (só SELECT de statement
  único); `echo -e` → `printf`; `$SUB_COMMAND` morto; strings "v1.0.0"
  velhas em start/handoff; hardcodes "shadcn-vue"/"Vue 3 + Reka" em prompts
  agnósticos agora leem stack.json.

## Novidades da v1.1.2

- **Seleção de Idioma** — Todos os comandos suportam PT-BR e EN. Configurado durante o `/pwdev-uiux:init`.
- **Perfis de Modelo** — Modelos dos agentes configuráveis via perfis `performance`, `balanced` ou `economy`. Orchestrator usa Opus por padrão no modo balanced.
- **Trilha de Auditoria (opt-in)** — Registro SQLite opcional de comandos, decisões e artefatos. Desativado por padrão.

---

## Exemplos de Uso

### Construir uma nova feature do início ao fim

```
/pwdev-uiux:start "User profile page with avatar, settings form, and activity feed"
```

O orquestrador guia você por todas as 5 fases automaticamente.

### Construir um componente a partir de uma spec existente

```
/pwdev-uiux:build UserCard
```

Implementa um componente específico quando a spec UX já está aprovada. Útil para adicionar componentes um a um após a Fase 1.

### Revisar componentes existentes

```
/pwdev-uiux:review
```

Executa revisão de acessibilidade (WCAG 2.1 AA) + UX (7 eixos + boas práticas) em paralelo. Gera um relatório de conformidade com contagens de aprovação/reprovação por prioridade (P0/P1/P2).

### Extrair tema do Figma

```
/pwdev-uiux:theme from-figma
```

Lê variáveis do Figma e gera configuração CSS + Tailwind automaticamente.

### Enviar componentes para o Figma

```
/pwdev-uiux:push-to-figma UserCard
/pwdev-uiux:push-to-figma screen
/pwdev-uiux:push-to-figma tokens
```

Cria representações no Figma a partir do seu código implementado.

---

## Stacks Suportadas

| Stack | Framework | Biblioteca de Componentes | Padrão |
|-------|-----------|--------------------------|:------:|
| `shadcn-vue` | Vue 3 | shadcn-vue (Reka UI v2) | sim |
| `shadcn-react` | React | shadcn/ui (Radix UI) | |
| `primevue` | Vue 3 | PrimeVue (styled mode) | |
| `untitled-ui` | React | Untitled UI (Radix UI) | |
| `tailwind-plus` | Vue / React | Tailwind Plus (Headless UI) | |
| `custom` | Qualquer | Qualquer / Nenhuma | |

As stacks são configuradas via `/pwdev-uiux:stack` e armazenadas em `.planning/ui/stack.json`. O agente `ui-builder` lê essa configuração antes de implementar qualquer componente.

---

## Metodologia

### Fluxo de 5 Fases

```
/pwdev-uiux:scan (projeto existente)
     |
     v gera project-ui-skill.md + relatório de conformidade
     |
/pwdev-uiux:start "descrição"
     |
     v
[FASE 1] ENTENDER        -> ux-spec.md
     | gate: spec aprovada
     v
[FASE 2] ESTRUTURAR      -> figma-spec.md
     | gate: figma-spec preenchida
     v
[FASE 3] IMPLEMENTAR     -> Componentes + component-log.md
     | gate: componentes implementados
     v
[FASE 4] REVISAR         -> review-findings.md + relatório de conformidade
     | gate: zero falhas críticas + todas as regras P0 aprovadas
     v
[FASE 5] ENTREGAR        -> docs/handoff/[feature].md
```

| Fase | O que acontece | Gate |
|------|---------------|------|
| **ENTENDER** | Analista de UX cria spec estruturada | Spec aprovada por humano |
| **ESTRUTURAR** | Design bridge traduz o Figma em spec de implementação | Figma spec preenchida |
| **IMPLEMENTAR** | UI builder cria componentes seguindo config da stack + spec + boas práticas | Todos os componentes registrados |
| **REVISAR** | A11y reviewer + UX critic executam em paralelo com relatório de conformidade | Zero falhas críticas + todas as P0 aprovadas |
| **ENTREGAR** | Gera documentação de entrega | Doc em `docs/handoff/` |

### Conformidade com Boas Práticas

O framework aplica mais de **60 regras de UI/UX** organizadas por prioridade:

| Prioridade | Significado | Aplicação |
|------------|------------|-----------|
| **P0 — Obrigatória** | Violações são bugs | Sempre aplicada. Bloqueia o gate de revisão. |
| **P1 — Padrão forte** | Aplicar salvo justificativa | Aplicada por padrão. Exceção requer documentação. |
| **P2 — Recomendada** | Aplicar quando o contexto permite | Rastreada no relatório de conformidade. |
| **P3 — Contextual** | Caso a caso | Não aplicada, apenas informativa. |

As regras cobrem: fundação visual, tipografia, layout e espaçamento, hierarquia de botões, navegação, abas, interações com dados, ações destrutivas, acesso e onboarding, formulários, relatórios, erros e validação, performance e motion & foco.

### Revisão UX de 7 Eixos + Conformidade com Regras

O UX critic revisa cada componente sob duas perspectivas complementares:

1. **7 Eixos Qualitativos**: Experiência, Gestalt, Confiança, Decisão, Cognição, Atenção, Acessibilidade
2. **Conformidade Baseada em Regras**: mais de 60 regras concretas com prioridade P0–P3 do conjunto de boas práticas

### Contexto do Projeto

O **ui-scanner** analisa seu projeto existente antes do desenvolvimento e gera uma skill contextual específica do projeto que o `ui-builder` utiliza para garantir consistência. Também executa uma verificação de conformidade para identificar violações existentes.

---

## Agentes

**Personas inline** (contexto principal — conversam com o humano):

| Persona | Onde | O que faz |
|---------|------|-----------|
| **orchestrator** | `references/workflow.md` via /start | Coordena as 5 fases e gates, spawna subagentes. Nunca escreve código. |
| **theme-builder** | `references/theme-method.md` via /theme | Temas semânticos (CSS vars + Tailwind), claro/escuro, WCAG AA — entrevista sobre a marca |

**Subagentes reais** (Task tool, contexto fresco):

| Subagente | Modelo (balanced) | O que faz |
|-----------|:-----------------:|-----------|
| **ux-analyst** | Sonnet | Transforma requisitos em specs de UX estruturadas |
| **design-bridge** | Sonnet | Bridge bidirecional com Figma (MCP no nível da sessão) |
| **ui-scanner** | Sonnet | Analisa UI existente, gera skill contextual + conformidade |
| **ui-builder** | Sonnet | Lê stack.json, lê as skills listadas, implementa componentes |
| **a11y-reviewer** | Haiku | Auditoria WCAG 2.1 AA + regras P0 de acessibilidade |
| **ux-critic** | Sonnet | Revisão UX de 7 eixos + conformidade (P0–P3) |

*Modelos por perfil em `references/model-profiles.md`; override com chaves
namespaced (`"uiux-ui-builder"`) na config compartilhada.*

---

## Comandos

### Configuração

| Comando | O que faz |
|---------|-----------|
| `/pwdev-uiux:init` | Inicializa o framework, detecta a stack, cria `.planning/ui/`, configura idioma e perfil de modelo |
| `/pwdev-uiux:stack` | Configura a stack de UI (shadcn-vue, shadcn-react, primevue, untitled-ui, tailwind-plus, custom) |
| `/pwdev-uiux:setup-figma` | Conecta o Figma MCP |
| `/pwdev-uiux:scan` | Analisa a UI do projeto existente + verificação de conformidade com boas práticas |

### Temas

| Comando | O que faz |
|---------|-----------|
| `/pwdev-uiux:theme` | Cria tema semântico (CSS vars + Tailwind, claro/escuro, contraste validado) |
| `/pwdev-uiux:theme update` | Modifica tokens do tema existente |
| `/pwdev-uiux:theme from-figma` | Extrai tema a partir de variáveis do Figma |
| `/pwdev-uiux:theme validate` | Executa validação de contraste WCAG AA no tema atual |

### Desenvolvimento

| Comando | O que faz |
|---------|-----------|
| `/pwdev-uiux:start "task"` | Inicia novo fluxo de UI a partir da Fase 1 |
| `/pwdev-uiux:analyze "desc"` | Exploração rápida de UX |
| `/pwdev-uiux:build [component]` | Implementa componente a partir de spec |

### Revisão e Entrega

| Comando | O que faz |
|---------|-----------|
| `/pwdev-uiux:review` | Revisão de conformidade A11y + UX + boas práticas em paralelo |
| `/pwdev-uiux:handoff` | Gera documentação de entrega |
| `/pwdev-uiux:status` | Exibe o estado atual do fluxo |

### Envio para o Figma

| Comando | O que faz |
|---------|-----------|
| `/pwdev-uiux:push-to-figma [path]` | Envia componente para o Figma |
| `/pwdev-uiux:push-to-figma screen` | Envia layout de tela |
| `/pwdev-uiux:push-to-figma library` | Constrói biblioteca de componentes |
| `/pwdev-uiux:push-to-figma tokens` | Sincroniza design tokens |

### Auditoria

| Comando | O que faz |
|---------|-----------|
| `/pwdev-uiux:audit` | Consultar a trilha de auditoria — resumo, eventos, decisões, artefatos, estatísticas, exportar PDF |

---

## Configuração de Idioma e Modelo

### Idioma

Todos os comandos suportam **Português (PT-BR)** e **Inglês (EN)**. Configurado durante o `/pwdev-uiux:init` e armazenado em `.planning/config.json`.

- `/pwdev-uiux:init` — sempre pergunta a preferência de idioma
- Outros comandos — usam a preferência salva silenciosamente
- Override — mude de idioma durante a conversa e confirme quando solicitado

### Perfil de Modelo

Só os 6 **subagentes** resolvem modelo (orchestrator e theme rodam inline no
modelo da sessão). Fonte única: `references/model-profiles.md`.

| Perfil | ui-builder | ux-analyst / design-bridge | ux-critic / ui-scanner | a11y-reviewer |
|--------|:----------:|:--------------------------:|:----------------------:|:-------------:|
| **performance** | Opus | Sonnet | Sonnet | Sonnet |
| **balanced** (padrão) | Sonnet | Sonnet | Sonnet | Haiku |
| **economy** | Sonnet | Sonnet | Haiku | Haiku |

Override com **chaves namespaced** na config compartilhada:

```json
{
  "lang": "pt-BR",
  "model_profile": "balanced",
  "model_overrides": {
    "uiux-ui-builder": "opus"
  }
}
```

---

## Trilha de Auditoria

Todos os plugins compartilham um banco de dados SQLite opcional em `.planning/pwdev-audit.db`. Ele é **desativado por padrão** e configurado durante o `/init`. O arquivo do banco nunca é versionado (adicionado automaticamente ao `.gitignore`).

**Como os dados chegam aqui (v2.0 — determinístico, via hooks):**
- `scripts/audit-hook.sh` (SessionStart, SubagentStart/Stop, PostToolUse,
  Stop) → eventos de sessão, execuções de subagentes com `session_id` e
  `duration_ms` reais, escritas em `.planning/`
- `scripts/audit-log.sh` → marcos de comandos (`event`) e alterações de
  configuração (`config` → `config_changes`, populada pelo `/init`)
- `scripts/guard-secrets.sh` (PreToolUse) → bloqueia leitura de `.env`,
  `*.pem`, `*.key`, `id_rsa*` (`.env.example` permitido)

O banco é **compartilhado com os demais plugins PWDEV** — filtre as linhas
deste plugin com `WHERE plugin='pwdev-uiux'`.

### Consultando a Trilha de Auditoria

Use `/pwdev-uiux:audit` para consultar o banco interativamente:

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
/pwdev-uiux:audit              # dashboard resumido
/pwdev-uiux:audit stats        # estatísticas detalhadas
/pwdev-uiux:audit export       # gerar relatório PDF em .planning/audit-report.pdf
/pwdev-uiux:audit query "SELECT * FROM events WHERE action='failed'"
```

Adicione `.planning/pwdev-audit.db` ao `.gitignore` (recomendado).

---

## Configuração de Stack

Armazenada em `.planning/ui/stack.json`:

```json
{
  "name": "shadcn-vue",
  "framework": "vue3",
  "component_library": "shadcn-vue",
  "styling": "tailwindcss",
  "forms": "vee-validate + zod",
  "icons": "lucide-vue-next",
  "skills": ["shadcn-vue", "reka-ui", "ux-tokens", "accessibility"]
}
```

---

## Skills

| Skill | Domínio |
|-------|---------|
| **ui-best-practices** | Conjunto canônico de regras de UI/UX (14 seções, 60+ regras, prioridade P0–P3) |
| **ui-theme-reference** | Registro canônico de design tokens (cores, tipografia, espaçamento, sombras, z-index, motion) |
| shadcn-vue | CLI do shadcn-vue, componentes, vee-validate |
| reka-ui | Primitivos headless, asChild, estado controlado |
| figma | Integração bidirecional com Figma |
| ux-tokens | CSS tokens, configuração do Tailwind |
| accessibility | WCAG 2.1 AA |
| component-audit | Auditoria de componentes existentes |
| design-system | Documentação de design system |
| ui-scanner | Protocolo de análise de UI |

---

## Licença

Apache-2.0 — Veja [LICENSE](./LICENSE)

*PWDEV-UIUX v2.0.0 — Qualidade como critério de entrega, não como aspiração.*
*Mantido por [Paulo Soares](https://github.com/soarescbm)*
