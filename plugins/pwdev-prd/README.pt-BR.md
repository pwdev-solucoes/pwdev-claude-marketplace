# PWDEV-PRD v1.1.1

*Leia em [English](./README.md)*

> **Criação de PRD Guiada por Entrevista para o Claude Code**

```
Entrevista estruturada → PRD consistente → Exportação em Markdown + JSON
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

## Novidades da v1.1.1

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
| 5 | **Requisitos Funcionais** | Nome, descrição, fluxo principal, alternativas, erros, prioridade |
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
- Os RNFs incluem pelo menos performance e disponibilidade
- O que está fora do escopo não contradiz o que está dentro
- A arquitetura suporta os RNFs declarados
- Toda decisão possui justificativa e trade-off
- Todo risco possui probabilidade, impacto, mitigação e contingência
- Os critérios de aceite são objetivos e verificáveis

---

## Agente

| Agente | Papel | O que faz |
|--------|-------|-----------|
| **agent-interviewer** | Especialista em Entrevista de PRD | Conduz a entrevista de 12 etapas, valida consistência, gera PRD.md + prd.json |

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
| `/pwdev-prd:init` | Cria o workspace `.planning/prds/`, configura idioma e perfil de modelo |

### Criação de PRD

| Comando | O que faz |
|---------|-----------|
| `/pwdev-prd:create "desc"` | Inicia a entrevista estruturada → gera PRD.md + prd.json opcional |
| `/pwdev-prd:refine {slug}` | Atualiza seções específicas de um PRD existente |

### Gerenciamento

| Comando | O que faz |
|---------|-----------|
| `/pwdev-prd:list` | Lista todos os PRDs com status |
| `/pwdev-prd:export {slug}` | Exporta como JSON ou issue do GitHub |
| `/pwdev-prd:export {slug} --json` | Regenera o prd.json |
| `/pwdev-prd:export {slug} --github` | Cria uma issue no GitHub a partir do PRD |
| `/pwdev-prd:audit` | Consultar a trilha de auditoria — resumo, eventos, decisões, artefatos, estatísticas, exportar PDF |

---

## Configuração de Idioma e Modelo

### Idioma

Todos os comandos suportam **Português (PT-BR)** e **Inglês (EN)**. Configurado durante o `/pwdev-prd:init` e armazenado em `.planning/config.json`.

- `/pwdev-prd:init` — sempre pergunta a preferência de idioma
- Outros comandos — usam a preferência salva silenciosamente
- Override — mude de idioma durante a conversa e confirme quando solicitado

### Perfil de Modelo

O modelo do agente é configurável via perfis definidos durante o `/pwdev-prd:init`:

| Perfil | agent-interviewer |
|--------|:-----------------:|
| **performance** | Opus |
| **balanced** | Sonnet |
| **economy** | Sonnet |

Override com `model_overrides` em `.planning/config.json`:

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
│   ├── PRD.md              # Documento PRD estruturado
│   └── prd.json            # Exportação JSON opcional
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

*PWDEV-PRD v1.1.1 — Requisitos claros, documentos consistentes, melhores funcionalidades.*
*Mantido por [Paulo Soares](https://github.com/soarescbm)*
