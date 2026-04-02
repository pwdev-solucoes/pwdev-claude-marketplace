# PWDEV-FEAT v1.1.1

*Leia em [English](./README.md)*

> **Desenvolvimento de Features com IA Simplificado para o Claude Code**

```
Descreva o que você quer → receba um plano estruturado → execute-o.
```

PWDEV-FEAT utiliza a **metodologia PWDEVIA de 7 perguntas** para gerar planos de ação estruturados que um agente executor segue com precisão. Sem cerimônias complexas — basta descrever, planejar e executar.

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

## Novidades da v1.1.1

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

| Agente | Papel | O que faz |
|--------|-------|-----------|
| **agent-planner** (PWDEVIA) | Engenheiro de Prompt | Aplica as 7 perguntas para criar planos de ação estruturados. Nunca escreve código. |
| **agent-executor** | Engenheiro de Implementação | Segue os planos passo a passo. Implementa, testa e faz commits. Reporta desvios. |

### Limites dos Agentes

- **PWDEVIA** cria planos — nunca escreve código de produção
- **Executor** segue planos — nunca desvia sem perguntar antes
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

Os modelos dos agentes são configuráveis via perfis definidos durante o `/pwdev-feat:init`:

| Perfil | agent-planner | agent-executor |
|--------|:------------:|:--------------:|
| **performance** | Opus | Opus |
| **balanced** | Sonnet | Sonnet |
| **economy** | Sonnet | Sonnet |

Override de agentes específicos com `model_overrides` em `.planning/config.json`:

```json
{
  "lang": "pt-BR",
  "model_profile": "balanced",
  "model_overrides": {}
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
│   ├── auth-tests/
│   │   ├── plan.md
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
| **Agentes** | 2 (planner + executor) | 11 agentes especializados |
| **Comandos** | 10 | 21 |
| **Ideal para** | Features individuais, iterações rápidas, equipes pequenas | Projetos complexos, conformidade, equipes grandes |
| **Cerimônia** | Mínima | Estruturada com gates |
| **Estilo de plano** | Plano de ação com 7 perguntas | SPEC.md (8 seções) + tarefas atômicas |

**Use pwdev-feat quando** quiser entregar rápido com suporte de IA.
**Use pwdev-code quando** precisar de rastreabilidade e verificação completas.

---

## Licença

Apache-2.0 — Veja [LICENSE](./LICENSE)

*PWDEV-FEAT v1.1.1 — Descreva, planeje, execute. Entregue.*
*Mantido por [Paulo Soares](https://github.com/soarescbm)*
