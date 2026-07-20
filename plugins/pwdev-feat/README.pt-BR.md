# PWDEV-FEAT v2.1.0

*Leia em [English](./README.md)*

> **Desenvolvimento de Features com IA Simplificado para o Claude Code**

```
Descreva o que você quer → receba um plano estruturado → execute-o.
```

PWDEV-FEAT utiliza a **metodologia PWDEVIA de 7 perguntas** para gerar planos
de ação estruturados — criados inline, entrevistando você (máx. 2 rodadas) —
que um **subagente executor real** implementa com contexto fresco. Sem
cerimônias complexas — basta descrever, planejar e executar.

---

## Novidades da v2.1.0

> **Atualizando da 2.0.x?** Plugins instalados são cópias em cache — fazer
> merge ou pull deste repo NÃO os atualiza. Rode
> `claude plugin marketplace update pwdev-claude-marketplace` e depois
> `claude plugin update pwdev-feat@pwdev-claude-marketplace`, e **reinicie o
> Claude Code** para o novo subagente `advisor` registrar na sessão.

- **Subagente advisor** (`pwdev-feat:advisor` + status `NEEDS_ADVICE`):
  quando o executor trava numa decisão difícil no meio do plano (ambiguidade,
  fork arquitetural, falha repetida de verificação com pergunta concreta),
  ele para e pergunta. O `/pwdev-feat:exec` consulta o advisor — o modelo
  forte (Opus mesmo em `balanced`), somente leitura, `effort: high` — e
  re-spawna o executor com a decisão anexada. Máx. 1 consulta por plano;
  chave de override `feat-advisor` no config compartilhado.
- **Memória compartilhada do projeto (somente leitura)**: quando o projeto
  mantém memória curada (`.planning/memory/`, gerida pelo pwdev-code), o
  planner PWDEVIA incorpora ≤3 memórias relevantes nas
  Assumptions/Quality Criteria do plano e o `/pwdev-feat:exec` injeta um
  bloco RELEVANT MEMORY no spawn do executor. O pwdev-feat nunca escreve na
  memória — a curadoria fica com o pwdev-code.
- A segunda opinião via CLI externa é recurso do `/pwdev-code:review` — não
  existe aqui (planos de review do feat rodam dentro de um subagente, sem
  canal para confirmar um comando externo com o humano).

## Novidades da v2.0.0

Reconstruído sobre o sistema moderno de plugins do Claude Code. Nenhum slash
command foi renomeado ou removido; os internos foram reestruturados.

- **Subagente executor real** (`pwdev-feat:executor`): o `/pwdev-feat:exec`
  agora spawna um subagente de verdade via Task tool com prompt auto-contido
  — contexto fresco por plano, frontmatter oficial, tools restritas.
- **Planner PWDEVIA inline por design** (`references/pwdevia-method.md`): ele
  entrevista você, e subagentes não conversam com o usuário. Os antigos
  arquivos de persona em prosa foram removidos.
- **Modos IMPLEMENT / REPORT**: planos de review (e planos só-relatório)
  rodam em modo REPORT — findings vão para `report.md`, sem alterar código,
  sem commit. Corrige o conflito antigo em que executar um plano de review
  tentava commitar.
- **Auditoria determinística via hooks**: início/fim de sessão, execuções do
  executor com `duration_ms`/`session_id` reais e escritas em `.planning/`
  são registradas por hooks do plugin — sem INSERTs inline. `config_changes`
  agora é populada de verdade (via `audit-log.sh config`). Hook de guarda de
  segredos bloqueia leitura de `.env`/`*.pem`/`*.key`/`id_rsa*`.
- **References empacotadas** (`${CLAUDE_PLUGIN_ROOT}/references/`): método
  PWDEVIA, protocolo de idioma, perfis de modelo (fonte única), contrato de
  spawn, schema de auditoria — substitui 11 blocos de idioma duplicados e 6
  blocos divergentes de Model Resolution.
- **Correções**: `/pwdev-feat:status` agora detecta ❌ FAILED e ⚠️ WITH
  CAVEATS; guard de query do audit endurecido (só SELECT de statement único);
  verificação lê os comandos do CLAUDE.md primeiro (sem correntes
  `npm || composer`); `echo -e` e o `$SUB_COMMAND` morto removidos.
- **Config compartilhada, com namespace**: `.planning/config.json` e o DB de
  auditoria são compartilhados com o pwdev-code de propósito; a chave de
  override de modelo do pwdev-feat é `"feat-executor"`.

---

## Metodologia

### As 7 Perguntas do PWDEVIA

Cada plano é construído respondendo a 7 perguntas fundamentais:

| # | Pergunta | Propósito |
|---|----------|-----------|
| 1 | **Persona & Escopo** | Quem deve ser o executor? Quais são os limites exatos? |
| 2 | **Objetivo Direto** | O que deve existir ao término? (1 frase clara) |
| 3 | **Entradas Mínimas** | Quais dados, regras e arquivos o executor precisa? |
| 4 | **Formato de Saída** | Quais arquivos criar/modificar? Estrutura esperada? |
| 5 | **Critérios de Qualidade** | Quais padrões devem ser atendidos? Quais testes? |
| 6 | **Tratamento de Ambiguidades** | O que fazer quando algo não estiver claro? |
| 7 | **Proibições** | O que NUNCA deve ser feito? |

### Como Funciona

```
Você descreve               PWDEVIA cria                   Executor implementa
─────────────               ────────────                   ────────────────────
"CRUD de usuário    →       user-crud/plan.md        →     Código + Testes + Commit
 com listagem               (7 seções + passos)            user-crud/plan.done.md
 paginada"
```

### Tipos de Plano

| Tipo | Comando | Escopo |
|------|---------|--------|
| **Feature** | `/pwdev-feat:feat` | Feature completa — backend + frontend + testes |
| **Backend** | `/pwdev-feat:backend` | API, serviços, models, migrations, testes de backend |
| **Frontend** | `/pwdev-feat:frontend` | Componentes, páginas, composables, E2E com Playwright |
| **Test** | `/pwdev-feat:test` | Testes unitários, integração e E2E para código existente |
| **Review** | `/pwdev-feat:review` | Revisão de código — segurança, performance, convenções |
| **Quick** | `/pwdev-feat:quick` | Execução direta, sem arquivo de plano (máx. 1-3 arquivos) |

---

## Novidades da v1.1.2

- **Pastas por feature** — Planos agora ficam em `.planning/feat/features/{slug}/plan.md` em vez do diretório flat `plans/`. Cada feature tem sua própria pasta isolada.
- **Seleção de Idioma** — Todos os comandos suportam PT-BR e EN. Configurado durante o `/pwdev-feat:init`.
- **Perfis de Modelo** — Modelos dos agentes configuráveis via perfis `performance`, `balanced` ou `economy`.
- **Trilha de Auditoria (opt-in)** — Registro SQLite opcional de comandos, decisões e artefatos. Desativado por padrão.

---

## Início Rápido

```bash
# 1. Inicializar
/pwdev-feat:init

# 2. (Opcional) Analisar a base de código existente
/pwdev-feat:map-codebase

# 3. (Opcional) Gerar CLAUDE.md
/pwdev-feat:setup

# 4. Criar um plano
/pwdev-feat:feat "CRUD de usuário com listagem paginada e busca"

# 5. Executar o plano
/pwdev-feat:exec user-crud

# Ou pular o planejamento para tarefas simples
/pwdev-feat:quick "Corrigir validação de e-mail no UserController"
```

---

## Agentes

| Agente | Onde roda | O que faz |
|--------|-----------|-----------|
| **PWDEVIA** (planner) | Inline, contexto principal (`references/pwdevia-method.md`) | Aplica as 7 perguntas, entrevistando você (máx. 2 rodadas). Nunca escreve código. |
| **executor** (subagente) | Subagente real via Task tool, contexto fresco | Segue o plano passo a passo. IMPLEMENT: código + testes + commit + relatório. REPORT: só findings, sem commit. |

### Limites dos Agentes

- **PWDEVIA** cria planos — nunca escreve código de produção
- **Executor** segue planos — nunca desvia sem perguntar antes (status STOPPED)
- Ambos leem CLAUDE.md e codebase.md para obter contexto do projeto

---

## Comandos

### Configuração

| Comando | O que faz |
|---------|-----------|
| `/pwdev-feat:init` | Cria o workspace `.planning/feat/`, configura idioma e perfil de modelo |
| `/pwdev-feat:map-codebase` | Analisa a base de código → gera o contexto `codebase.md` |
| `/pwdev-feat:setup` | Gera `CLAUDE.md` com as convenções do projeto |

### Planejamento (gerado pelo PWDEVIA)

| Comando | O que faz |
|---------|-----------|
| `/pwdev-feat:feat "desc"` | Cria plano de feature completa (backend + frontend + testes) |
| `/pwdev-feat:backend "desc"` | Cria plano focado em backend (API, serviços, models) |
| `/pwdev-feat:frontend "desc"` | Cria plano focado em frontend (componentes, E2E) |
| `/pwdev-feat:test "desc"` | Cria plano de testes para código existente |
| `/pwdev-feat:review "scope"` | Cria plano de revisão de código |

### Execução

| Comando | O que faz |
|---------|-----------|
| `/pwdev-feat:exec {slug}` | Executa o plano de uma feature específica (ou `latest`) |
| `/pwdev-feat:quick "desc"` | Execução direta — sem arquivo de plano, para tarefas simples |
| `/pwdev-feat:status` | Exibe planos pendentes, executados e com falha |
| `/pwdev-feat:audit` | Consultar a trilha de auditoria — resumo, eventos, decisões, artefatos, estatísticas, exportar PDF |

---

## Configuração de Idioma e Modelo

### Idioma

Todos os comandos suportam **Português (PT-BR)** e **Inglês (EN)**. Configurado durante o `/pwdev-feat:init` e armazenado em `.planning/config.json`.

- `/pwdev-feat:init` — sempre pergunta a preferência de idioma
- Outros comandos — usam a preferência salva silenciosamente
- Override — mude de idioma durante a conversa e confirme quando solicitado

### Perfil de Modelo

Só o subagente **executor** resolve modelo (o planner PWDEVIA roda inline no
modelo da sessão). Fonte única de verdade: `references/model-profiles.md`.

| Perfil | executor |
|--------|:--------:|
| **performance** | Opus |
| **balanced** (padrão) | Sonnet |
| **economy** | Sonnet |

Override com a **chave namespaced `"feat-executor"`** em
`.planning/config.json` (o arquivo é compartilhado com o pwdev-code — a chave
simples `"executor"` pertence a ele):

```json
{
  "lang": "pt-BR",
  "model_profile": "balanced",
  "model_overrides": { "feat-executor": "opus" }
}
```

---

## Trilha de Auditoria

Todos os plugins compartilham um banco de dados SQLite opcional em `.planning/pwdev-audit.db`. Ele é **desativado por padrão** e configurado durante o `/init`. O arquivo do banco nunca é versionado (adicionado automaticamente ao `.gitignore`).

**Como os dados chegam aqui (v2.0 — determinístico, via hooks):**
- `scripts/audit-hook.sh` (SessionStart, SubagentStart/Stop, PostToolUse,
  Stop) → eventos de sessão, execuções do executor com `session_id` e
  `duration_ms` reais, escritas de artefatos em `.planning/`
- `scripts/audit-log.sh` → marcos de comandos (`event`) e alterações de
  configuração (`config` → tabela `config_changes`, populada pelo `/init`)
- `scripts/guard-secrets.sh` (PreToolUse) → bloqueia leitura de `.env`,
  `*.pem`, `*.key`, `id_rsa*` (`.env.example` permitido)

O banco é **compartilhado com o pwdev-code** — as linhas se distinguem pela
coluna `plugin` (`WHERE plugin='pwdev-feat'`).

### Consultando a Trilha de Auditoria

Use `/pwdev-feat:audit` para consultar o banco interativamente:

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
/pwdev-feat:audit              # dashboard resumido
/pwdev-feat:audit stats        # estatísticas detalhadas
/pwdev-feat:audit export       # gerar relatório PDF em .planning/audit-report.pdf
/pwdev-feat:audit query "SELECT * FROM events WHERE action='failed'"
```

Adicione `.planning/pwdev-audit.db` ao `.gitignore` (recomendado).

---

## Estrutura do Plano

Todo plano gerado pelo PWDEVIA segue esta estrutura:

```markdown
# Plano de Ação — {title}

## 1. Persona & Scope        ← quem e o quê
## 2. Direct Objective        ← o que deve existir ao término
## 3. Minimum Inputs          ← dados, regras, arquivos a ler
## 4. Output Format           ← arquivos a criar/modificar
## 5. Quality Criteria        ← testes, lint, padrões
## 6. Ambiguity Handling      ← o que fazer quando houver dúvida
## 7. Prohibitions            ← o que NUNCA fazer

## Execution Steps            ← passos concretos e numerados
## Done                       ← uma frase = concluído
## Commit                     ← mensagem de commit convencional
```

Os planos são armazenados em `.planning/feat/features/{slug}/plan.md` e executados com `/pwdev-feat:exec {slug}`.

---

## Workspace

```
.planning/feat/
├── features/
│   ├── user-crud/
│   │   ├── plan.md                # Plano de ação
│   │   └── plan.done.md           # Relatório de execução
│   ├── api-review/
│   │   ├── plan.md                # Plano de review (Type: review)
│   │   ├── report.md              # Findings (modo REPORT — sem commit)
│   │   └── plan.done.md
│   └── ...
└── codebase.md                    # Gerado por /pwdev-feat:map-codebase
```

Cada feature tem sua própria pasta em `features/`. Todos os artefatos da feature (plano, relatório de execução, review) ficam dentro dessa pasta.

Arquivos de contexto opcionais:
- `.planning/feat/codebase.md` — gerado por `/pwdev-feat:map-codebase`
- `CLAUDE.md` — gerado por `/pwdev-feat:setup`

---

## pwdev-feat vs pwdev-code

| Aspecto | pwdev-feat | pwdev-code |
|---------|-----------|------------|
| **Filosofia** | Rápido e prático | Rigoroso e rastreável |
| **Fases** | Plan → Execute | DISCOVER → DESIGN → PLAN → EXECUTE → REVIEW → VERIFY |
| **Agentes** | PWDEVIA inline + subagentes executor e advisor | 8 subagentes reais + personas inline |
| **Comandos** | 12 | 16 |
| **Ideal para** | Features individuais, iterações rápidas, equipes pequenas | Projetos complexos, conformidade, equipes grandes |
| **Cerimônia** | Mínima | Estruturada com gates |
| **Estilo de plano** | Plano de ação com 7 perguntas | SPEC.md (8 seções) + tarefas atômicas |

**Use pwdev-feat quando** quiser entregar rápido com suporte de IA.
**Use pwdev-code quando** precisar de rastreabilidade e verificação completas.

---

## Licença

Apache-2.0 — Veja [LICENSE](./LICENSE)

*PWDEV-FEAT v2.1.0 — Descreva, planeje, execute. Entregue.*
*Mantido por [Paulo Soares](https://github.com/soarescbm)*
