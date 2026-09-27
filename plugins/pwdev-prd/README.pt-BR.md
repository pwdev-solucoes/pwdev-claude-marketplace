# PWDEV-PRD v3.0.0

*Leia em [English](./README.md)*

> **Criação de PRD Guiada por Entrevista para Claude Code, Codex, Hermes Agent e OpenCode**

```
Entrevista estruturada → PRD aprovado → Roadmap com dependências → GitHub Project
```

O PWDEV-PRD guia você por uma **entrevista estruturada de 12 etapas** para criar Documentos de Requisitos de Produto completos, consistentes e agnósticos de tecnologia — para funcionalidades ou sistemas inteiros.

---

## Metodologia

### O Problema

PRDs costumam ser incompletos, inconsistentes ou enviesados para uma tecnologia específica. As equipes começam a construir sem objetivos claros, métricas, critérios de aceite ou avaliação de riscos. O resultado: escopo descontrolado, requisitos perdidos e funcionalidades que não resolvem o problema real.

### A Solução

Um agente entrevistador especializado que:
- Faz **uma pergunta por vez** e aguarda sua resposta
- Oferece **2 a 3 opções** quando você não sabe a resposta
- Resume e confirma ao final de cada etapa
- Marca incógnitas como **hipóteses** (nunca inventa)
- Executa **verificações de consistência** antes de gerar o PRD final
- Produz um **documento estruturado** pronto para execução

### Agnóstico de Tecnologia

Os PRDs criados por este plugin descrevem **o que** precisa ser construído e **por quê**, não **como**. As seções de arquitetura capturam decisões em nível de sistema (monólito vs. microsserviços, síncrono vs. assíncrono) sem especificar frameworks, bibliotecas ou linguagens.

Isso torna os PRDs compatíveis com qualquer fluxo de trabalho posterior:
- `/pwdev-feat:feat` para desenvolvimento simplificado de funcionalidades
- `/pwdev-code:discover` para desenvolvimento rigoroso orientado a especificações
- Handoff manual para equipes de engenharia

---

## Instalação

| Runtime | Instalação | Uso |
|---|---|---|
| Claude Code | `claude plugin install pwdev-prd@pwdev-claude-marketplace` | `/pwdev-prd:create "…"` |
| Codex | adicione este repositório como marketplace e habilite o **pwdev-prd** (`.agents/plugins/marketplace.json`) | `$prd-create …` |
| Hermes Agent | `hermes plugins install pwdev-solucoes/pwdev-claude-marketplace --enable` (entrada `.hermes-plugin/`) | `skill_view("pwdev-prd:prd-create")` ou só peça |
| OpenCode | `python3 plugins/pwdev-prd/.opencode-plugin/install.py [--project <dir>]` | `/prd-create …` ou a ferramenta `skill` |

O fluxo mora em nove skills portáveis (`skills/prd-*`); cada comando do Claude é um wrapper fino
de uma delas (`create → prd-create`, `roadmap → prd-roadmap`, ...). O escritor do roadmap é
subagente em todo runtime que tem um (Claude `Agent`, Codex `spawn_agent`, Hermes
`delegate_task`, OpenCode `task`) e roda inline nos demais; subagentes no Codex exigem
`[features] multi_agent = true` em `~/.codex/config.toml`. Hooks (auditoria, guarda de segredos)
são só do Claude; nos outros runtimes a trilha tem apenas os eventos de marco. Detalhes:
[`references/runtime.md`](./references/runtime.md).

---

## Novidades da v3.0.0

- **Portável para Codex, Hermes Agent e OpenCode** — nove skills `prd-*` são a fonte única; os
  comandos do Claude viraram wrappers; manifesto Codex e `openai.yaml` por skill; adaptador
  Hermes com bootstrap no primeiro turno; instalador OpenCode que cria os links das skills e um
  comando `/prd-<nome>` para cada.
- O contrato do escritor do roadmap foi para `references/roadmap-agent.md`, compartilhado por
  todos os runtimes e pelo fallback inline.
- **Histórias de usuário, CA e RN por feature** — o PRD ganha a seção `### Business Rules`
  (`RN-xx`, coletadas na etapa 5 da entrevista); o escritor do roadmap rascunha de 1 a 3
  histórias por feature ("Como…, quero…, para…", CA em Gherkin com caminho feliz e de erro, as RN
  que aplicam); o novo **`/pwdev-prd:stories {slug} [feature|next]`** evolui uma feature por vez
  com você até a Definition of Ready (INVEST, 3–8 CA, toda RN verificada por um CA). O checker
  aplica o padrão (adaptado da `skill-user-stories` do pwdev-code, ver
  `references/user-stories.md`) e gera `STORIES.md` e `stories/US-NN-*.md`. A publicação coloca
  as histórias na issue da feature ou as transforma em sub-issues.

## Novidades da v2.1.0

- **Roadmap com cadeia de dependências** — `/pwdev-prd:roadmap {slug}` decompõe um PRD
  aprovado em Fase → Épico → Feature → Task (mesmos IDs do pwdev-power e do pwdev-code)
  com arestas `depends_on` explícitas. O checker determinístico
  `scripts/roadmap-check.py` rejeita ciclos, arestas soltas e requisitos órfãos e gera o
  `DEPENDENCIES.md`: grafo Mermaid, **ondas** (o que pode rodar em paralelo) e **caminho
  crítico**. O roadmap é escrito pelo primeiro subagente do plugin, `pwdev-prd:roadmap`;
  a entrevista continua inline.
- **Publicação no GitHub** — `/pwdev-prd:publish {slug}` entrega o `roadmap.json`
  aprovado (`pwdev-roadmap/1`) ao plugin **pwdev-github**: GitHub Project a partir de um
  template personalizável, issues, sub-issues, milestones e "blocked by" nativo.
- **Gate de aprovação** — o PRD tem `Status: DRAFT | APPROVED`; só PRD aprovado vira
  roadmap. O `refine` incrementa a `Version`, mantém o `Change Log` e reabre a aprovação.
- **IDs rastreáveis** — `FR-xx`, `NFR-xx`, `AC-xx`; prioridade em MoSCoW em todo lugar
  (template e JSON divergiam).
- **`export --github` mais seguro** — preflight de autenticação, repo, labels ausentes e o
  limite de 65.536 caracteres do corpo, com preview antes de criar a issue.
- **`list`** mostra status, versão, estado do roadmap e a URL do GitHub Project.

## Novidades da v2.0.0

Reconstruído sobre o sistema moderno de plugins do Claude Code. Nenhum slash
command renomeado ou removido.

- **Entrevistador inline por design** (`references/interview-method.md`): ele
  conversa com você, uma pergunta por vez — subagentes não fazem isso, então
  este plugin tem **zero subagentes**. O antigo arquivo de persona em prosa
  foi removido, junto com os blocos mortos de "Model Resolution" (nada aqui
  resolve modelo; a entrevista roda no modelo da sessão).
- **Estrutura canônica do prd.json** finalmente definida (em
  `references/interview-method.md`) — `create` e `export` apontavam para uma
  estrutura JSON que não existia em lugar nenhum.
- **Auditoria determinística via hooks** no banco compartilhado
  `.planning/pwdev-audit.db` (filtre com `WHERE plugin='pwdev-prd'`): eventos
  de sessão com `session_id` real, escritas em `.planning/`, marcos de
  comandos e `config_changes` via `audit-log.sh`. Hook de guarda de segredos
  incluído.
- **Correções**: guard de query do audit endurecido (só SELECT de statement
  único); `echo -e` → `printf`; `$SUB_COMMAND` morto removido; papéis
  fantasmas de model-profile removidos; exemplos de audit herdados errados
  (fases DISCOVER) removidos; paths resolvem via `${CLAUDE_PLUGIN_ROOT}`.

## Novidades da v1.1.2

- **Seleção de Idioma** — Todos os comandos suportam PT-BR e EN. Configurado durante o `/pwdev-prd:init`.
- **Perfis de Modelo** — Modelo do agente configurável via perfis `performance`, `balanced` ou `economy`.
- **Trilha de Auditoria (opt-in)** — Registro SQLite opcional de comandos e decisões. Desativado por padrão.

---

## Processo de Entrevista em 12 Etapas

| Etapa | Tópico | O que é capturado |
|:-----:|--------|-------------------|
| 1 | **Contexto e Visão Geral** | Produto, público-alvo, contexto de implantação, objetivo de negócio |
| 2 | **Problema e Oportunidade** | Dor atual, exemplos reais com números, tentativas anteriores frustradas |
| 3 | **Objetivos e Métricas** | Metas mensuráveis com métrica e meta-alvo |
| 4 | **Escopo** | O que está incluído e o que está explicitamente fora |
| 5 | **Requisitos Funcionais e Regras de Negócio** | Nome, descrição, fluxo principal, alternativas, erros, prioridade; regras de negócio `RN-xx` com enunciado testável e exemplo |
| 6 | **Requisitos Não Funcionais** | Performance, disponibilidade, segurança, observabilidade, conformidade |
| 7 | **Arquitetura e Abordagem** | Componentes, integrações, padrões de comunicação |
| 8 | **Decisões e Trade-offs** | O que foi decidido, por quê e qual o custo |
| 9 | **Dependências** | Técnicas, organizacionais, externas |
| 10 | **Riscos e Mitigação** | Probabilidade, impacto, mitigação (múltiplos itens), contingência |
| 11 | **Critérios de Aceite** | Checklist objetivo e verificável |
| 12 | **Testes e Validação** | Tipos de teste, estratégia de validação |

### Verificações de Consistência

Antes de gerar o PRD final, o agente valida:
- Todo objetivo possui uma métrica e uma meta-alvo
- Todo requisito funcional possui nome, fluxo e prioridade
- Toda regra de negócio possui ID `RN-xx`, enunciado testável e exemplo
- Os RNFs incluem pelo menos performance e disponibilidade
- O que está fora do escopo não contradiz o que está dentro
- A arquitetura suporta os RNFs declarados
- Toda decisão possui justificativa e trade-off
- Todo risco possui probabilidade, impacto, mitigação e contingência
- Os critérios de aceite são objetivos e verificáveis

---

## Agente

| Persona | Onde roda | O que faz |
|---------|-----------|-----------|
| **Entrevistador de PRD** | Inline, contexto principal (`references/interview-method.md`) — conversa com você, então nunca é subagente | Conduz a entrevista de 12 etapas, valida consistência, gera PRD.md + prd.json |
| **Roadmap** (`agents/roadmap.md`) | Subagente `pwdev-prd:roadmap`, despachado pelo `/pwdev-prd:roadmap` — nunca conversa com você | Escreve os arquivos do roadmap e o `roadmap.json` com a cadeia de dependências; o comando roda o checker e faz o gate de aprovação |

### Limites do Agente
- Nunca escolhe tecnologias específicas
- Nunca inventa requisitos (marca incógnitas como hipóteses)
- Nunca faz perguntas duplas
- Sempre confirma o entendimento antes de avançar

---

## Comandos

### Configuração

| Comando | O que faz |
|---------|-----------|
| `/pwdev-prd:init` | Cria o workspace `.planning/prds/`, configura idioma e auditoria |

### Criação de PRD

| Comando | O que faz |
|---------|-----------|
| `/pwdev-prd:create "desc"` | Inicia a entrevista estruturada → gera PRD.md + prd.json opcional |
| `/pwdev-prd:refine {slug}` | Atualiza seções específicas de um PRD existente (incrementa versão, reabre aprovação) |

### Roadmap e GitHub

| Comando | O que faz |
|---------|-----------|
| `/pwdev-prd:roadmap {slug}` | PRD aprovado → roadmap com cadeia de dependências, ondas, caminho crítico, rastreabilidade e histórias em rascunho |
| `/pwdev-prd:stories {slug} [feature\|next]` | Evolui uma feature por vez: histórias de usuário, critérios de aceite (CA) e regras de negócio (RN) até a Definition of Ready |
| `/pwdev-prd:publish {slug}` | Roadmap aprovado → GitHub Project, issues, sub-issues e blocked-by (requer pwdev-github) |

### Gerenciamento

| Comando | O que faz |
|---------|-----------|
| `/pwdev-prd:list` | Lista todos os PRDs com status |
| `/pwdev-prd:export {slug}` | Exporta como JSON ou issue do GitHub |
| `/pwdev-prd:export {slug} --json` | Regenera o prd.json |
| `/pwdev-prd:export {slug} --github` | Cria uma única issue no GitHub a partir do PRD (preflight + preview) |
| `/pwdev-prd:audit` | Consultar a trilha de auditoria — resumo, eventos, decisões, artefatos, estatísticas, exportar PDF |

---

## Configuração de Idioma e Modelo

### Idioma

Todos os comandos suportam **Português (PT-BR)** e **Inglês (EN)**. Configurado durante o `/pwdev-prd:init` e armazenado em `.planning/config.json`.

- `/pwdev-prd:init` — sempre pergunta a preferência de idioma
- Outros comandos — usam a preferência salva silenciosamente
- Override — mude de idioma durante a conversa e confirme quando solicitado

### Modelo

A entrevista roda inline no modelo da sessão. O único subagente,
`pwdev-prd:roadmap`, declara `model: inherit` e também segue o modelo da
sessão — não há o que configurar. O `model_profile` do
`.planning/config.json` compartilhado pertence aos plugins com subagentes
(pwdev-code, pwdev-feat) e não é tocado pelo `/pwdev-prd:init`.

A config compartilhada continua com `lang` e `audit`:

```json
{
  "lang": "pt-BR",
  "audit": false
}
```

---

## Trilha de Auditoria

Todos os plugins compartilham um banco de dados SQLite opcional em `.planning/pwdev-audit.db`. Ele é **desativado por padrão** e configurado durante o `/init`. O arquivo do banco nunca é versionado (adicionado automaticamente ao `.gitignore`).

**Como os dados chegam aqui (v2.0 — determinístico, via hooks):**
- `scripts/audit-hook.sh` (SessionStart, PostToolUse, Stop) → eventos de
  sessão com `session_id` real, escritas de artefatos em `.planning/`
- `scripts/audit-log.sh` → marcos de comandos (`event`) e alterações de
  configuração (`config` → tabela `config_changes`, populada pelo `/init`)
- `scripts/guard-secrets.sh` (PreToolUse) → bloqueia leitura de `.env`,
  `*.pem`, `*.key`, `id_rsa*` (`.env.example` permitido)

O banco é **compartilhado com pwdev-code/pwdev-feat** — filtre as linhas
deste plugin com `WHERE plugin='pwdev-prd'`.

### Consultando a Trilha de Auditoria

Use `/pwdev-prd:audit` para consultar o banco interativamente:

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
/pwdev-prd:audit              # dashboard resumido
/pwdev-prd:audit stats        # estatísticas detalhadas
/pwdev-prd:audit export       # gerar relatório PDF em .planning/audit-report.pdf
/pwdev-prd:audit query "SELECT * FROM events WHERE action='failed'"
```

Adicione `.planning/pwdev-audit.db` ao `.gitignore` (recomendado).

---

## Formatos de Saída

### Markdown (PRD.md)

Documento estruturado com seções padronizadas:

```
PRD: [produto] [funcionalidade]
├── Resumo
├── Contexto e Problema
├── Objetivos e Métricas (tabela)
├── Escopo (incluído / excluído)
├── Requisitos Funcionais (por requisito)
├── Requisitos Não Funcionais (por categoria)
├── Arquitetura e Abordagem
├── Decisões e Trade-offs
├── Dependências
├── Riscos e Mitigação
├── Critérios de Aceite (checklist)
└── Testes e Validação
```

### JSON (prd.json) — Opcional

Dados estruturados com chaves em inglês, conteúdo no idioma original:

```json
{
  "meta": { "product", "feature", "version", "date" },
  "context": { "summary", "target_audience", "problems" },
  "goals": [{ "goal", "metric", "target" }],
  "scope": { "in_scope", "out_of_scope" },
  "functional_requirements": [{ "id", "name", "main_flow", "priority" }],
  "non_functional_requirements": [{ "category", "specifications" }],
  "architecture": { "approach", "components", "integrations" },
  "decisions_tradeoffs": [{ "decision", "justification", "trade_off" }],
  "dependencies": [{ "type", "title", "description" }],
  "risks": [{ "risk", "probability", "impact", "mitigation", "contingency_plan" }],
  "acceptance_criteria": [],
  "testing_validation": { "test_types", "strategy" }
}
```

---

## Workspace

```
.planning/prds/
├── user-authentication/
│   ├── PRD.md              # Documento PRD estruturado (Status: DRAFT | APPROVED)
│   ├── prd.json            # Exportação JSON opcional
│   └── roadmap/            # /pwdev-prd:roadmap — ver references/roadmap-format.md
│       ├── roadmap.json    # contrato de máquina pwdev-roadmap/1
│       ├── ROADMAP.md  TRACEABILITY.md  RISKS.md
│       ├── DEPENDENCIES.md # gerado: grafo Mermaid, ondas, caminho crítico
│       ├── STORIES.md      # gerado: histórias por feature, status, CA e RN
│       ├── stories/        # gerado: US-NN-<slug>.md (edite pelo /pwdev-prd:stories)
│       └── F01-<slug>/…    # PHASE.md, EPIC.md, um arquivo por feature
├── inventory-management/
│   ├── PRD.md
│   └── prd.json
└── ...
```

---

## Padrões Inteligentes

Quando o usuário não sabe a resposta, o agente oferece os seguintes valores como **hipóteses** (explicitamente marcadas):

| Aspecto | Padrão |
|---------|--------|
| Latência de API | p95 < 150ms |
| Disponibilidade (externa) | 99,9% |
| Disponibilidade (interna) | 99,5% |
| Observabilidade | Logs estruturados + métricas de erro + rastreamento distribuído |
| Segurança | Auth + RBAC + auditoria de alterações sensíveis |
| Atualizações críticas | Transacional |

---

## Licença

Apache-2.0 — Consulte [LICENSE](./LICENSE)

*PWDEV-PRD v3.0.0 — Requisitos claros, documentos consistentes, melhores funcionalidades.*
*Mantido por [Paulo Soares](https://github.com/soarescbm)*
