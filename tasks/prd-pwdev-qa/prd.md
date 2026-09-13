---
type: PRD
okf_version: "0.2"
sources:
  - resource: "conversation:pwdev-qa"
  - resource: "tasks/prd-pwdev-qa/design.md"
  - resource: ".planning/sdd-composy/context/project.md"
generated:
  by: agent:codex
  at: "2026-09-12"
lifecycle:
  status: DRAFT
human_approval: PENDING
verified: []
---

# PWDEV QA — requisitos da v1

Status: DRAFT
Atualizado: 2026-09-12
Processo: pwdev-power:power-product, subordinado ao AGENTS.md do repositório.

## 1. Visão geral

O PWDEV QA apoia prevenção, descoberta e comunicação de defeitos durante todo o
ciclo de software. Usuários primários são profissionais de QA e desenvolvedores;
responsáveis por entregas consomem seus relatórios e recomendações.

O problema é reunir estratégia, especialidades e evidências em um processo utilizável
em Claude Code, Codex e Hermes, com critérios de aceite rastreáveis e resultados
que possam ser revisados em HTML e PDF. O pedido do usuário estabelece a necessidade;
não há dados quantitativos disponíveis sobre custo ou frequência atual do problema.

## 2. Objetivos e métricas

Todas as metas abaixo são medidas na validação da v1, não prometem desempenho
de projetos consumidores. Baseline: plugin ainda sem implementação nesta tarefa.

| Objetivo | Meta de aceite da v1 | Medição |
|---|---|---|
| O-01: cobrir o ciclo de QA aprovado | 10 workflows e 17 especialidades | Inventário e cenários de uso |
| O-02: operar nos runtimes solicitados | 3 de 3 com descoberta e invocação reais verificadas | Smoke registrado por runtime |
| O-03: tornar o aceite auditável | 100% dos critérios do contrato na matriz | Comparação contrato/relatório |
| O-04: fornecer relatórios consistentes | 0 divergências de critérios, resultados e parecer entre HTML e PDF | Extração e comparação |
| O-05: evitar falso sucesso | 0 aprovações nas fixtures de evidência inválida ou execução pendente | Testes negativos |

## 3. Requisitos funcionais — MoSCoW

### RF-001 — MUST — Entradas de trabalho

Oferecer `init`, `strategy`, `test`, `explore`, `regression`, `bug`, `review`,
`release`, `report` e `status`, com objetivo, entradas, procedimento, resultados
e tratamento de indisponibilidade. Selecionar especialidades segundo escopo e risco.

### RF-002 — MUST — QA geral e especializado

Cobrir as 17 especialidades enumeradas em `design.md`, seção Superfície aprovada.
Cada especialidade deve orientar seleção de cenários, execução ou inspeção,
interpretação de resultados e evidência esperada. Nenhuma exige ferramenta ausente
como se estivesse instalada. Testes funcionais incluem caminhos positivos, negativos
e fronteiras. Defeitos incluem reprodução, impacto, severidade, prioridade e reteste.

### RF-003 — MUST — Portabilidade

Permitir descoberta e uso em Claude Code, Codex e Hermes. Manter semântica comum
de contratos e resultados. Capacidades equivalentes devem produzir classificações
equivalentes nos cenários de referência; ferramentas ausentes geram limitação
explícita. O suporte de um runtime permanece não verificado se seu smoke real
não puder ocorrer; teste simulado não satisfaz a meta O-02.

### RF-004 — MUST — Validação dos critérios de aceite

Preservar todos os IDs e textos do contrato de aceite fornecido. Relacionar cada
critério a testes, resultado esperado, observado, avaliação e evidências referentes
ao alvo identificado. Classificar em PASS, FAIL, BLOCKED, NOT_RUN ou NOT_APPLICABLE.
Não aplicabilidade requer justificativa sustentada pelo escopo aprovado.
Não criar ou enfraquecer critérios para obter aprovação.

### RF-005 — MUST — Relatórios HTML e PDF

Entregar os dois formatos a partir da mesma execução, com identificação do projeto,
contrato e alvo, matriz completa, resultados, evidências, defeitos, resumo e parecer.
HTML deve funcionar offline. PDF deve ser legível, paginado e autossuficiente para
ler matriz e parecer; anexos de evidência podem acompanhar o pacote separadamente.
Exportação incompleta deve ser comunicada como tal.

### RF-006 — MUST — Integridade e histórico

Vincular evidências ao alvo e contrato, detectar arquivo ausente ou alterado,
preservar execuções anteriores e identificar o reteste que sustenta cada resultado.
Separar avaliação semântica registrada de verificações automáticas de integridade;
um arquivo existente ou comando com saída zero não prova sozinho um critério.

### RF-007 — MUST — Parecer de prontidão

Emitir FAIL diante de falha comprovada; na ausência de falha, emitir BLOCKED diante
de pendências, evidências inválidas ou ausência de critérios aplicáveis. Emitir PASS
somente se todos os critérios aplicáveis passarem. Decisão humana de aceitar risco
é registrada separadamente e não muda o resultado dos testes. Não publicar releases.

### RF-008 — MUST — Integrações e execução autorizada

Consumir contratos de Flow e Power sem modificar seus critérios ou aprovações.
Funcionar sem plugins complementares. Exigir autorização explícita para carga,
pentest, produção e efeitos externos pertinentes. Corrigir produto apenas mediante
pedido de implementação. Não enviar defeitos a sistemas externos sem solicitação.

## 4. Requisitos não funcionais

- RNF-001: 0 recursos remotos ou scripts executáveis no HTML entregue.
- RNF-002: 0 leituras de evidências fora dos caminhos autorizados; rejeitar symlinks
  e travessia de diretórios nas fixtures de segurança.
- RNF-003: 100% dos resultados têm rótulo textual além de indicação visual por cor.
- RNF-004: cenário de referência com 100 critérios, acentos e descrições de 2.000
  caracteres preserva todo o texto no HTML e no PDF, sem cortes ou sobreposição
  na inspeção das páginas renderizadas. É fixture de aceite, não limite de uso.
- RNF-005: 0 sobrescritas silenciosas de execuções anteriores nos testes de colisão.
- RNF-006: documentação de instalação e uso disponível em português e inglês.

## 5. Escopo e exclusões

Incluídos: RF-001 a RF-008 e RNF-001 a RNF-006. A v1 abrange todos os workflows e
especialidades aprovados, mesmo que a entrega seja decomposta em features menores.

Excluídos: hospedagem do relatório, publicação automática, certificação regulatória,
infraestrutura própria de execução, correção automática de produto, serviço MCP
obrigatório e mudança nos plugins usados como referência.

## 6. Histórias e critérios de aceite

Estas histórias compõem o PRD do Power. O artefato STORIES exigido pelo AGENTS.md
será derivado mantendo estes IDs e deverá passar por seu gate próprio.

| História | Critérios verificáveis |
|---|---|
| US-001: como QA, quero selecionar o trabalho e suas especialidades para avaliar o escopo correto | CA-001: os 10 workflows encaminham ao procedimento documentado; CA-002: as 17 especialidades têm cenário positivo e cenário de falha/limitação |
| US-002: como desenvolvedor, quero usar QA no meu runtime para manter o processo de trabalho | CA-003: descoberta/invocação real em cada runtime; CA-004: ferramenta ausente resulta em limitação explícita, nunca execução inventada |
| US-003: como QA, quero avaliar cada critério para demonstrar atendimento aos requisitos | CA-005: todos os critérios constam da matriz com teste, resultado e avaliação; CA-006: casos ausentes, contrato vazio ou dispensa sem justificativa não produzem PASS |
| US-004: como responsável por entrega, quero HTML e PDF para revisar e compartilhar os resultados | CA-007: ambos têm os mesmos IDs, resultados e parecer; CA-008: HTML funciona offline e PDF passa RNF-003/004; CA-009: falha da exportação PDF é explicitamente informada |
| US-005: como QA, quero evidências vinculadas à versão para evitar conclusões obsoletas | CA-010: evidência ausente, alterada ou de alvo incompatível impede PASS; CA-011: reteste preserva a execução anterior e identifica a vigente |
| US-006: como responsável por entrega, quero conhecer falhas e pendências para decidir sobre a liberação | CA-012: FAIL prevalece sobre pendência; sem falha, pendência implica BLOCKED; todos aplicáveis aprovados permitem PASS; CA-013: aceite humano de risco não altera resultados |
| US-007: como mantenedor, quero QA integrado ao projeto sem alterar sua governança | CA-014: integração preserva critérios, estados e aprovações externos; CA-015: operações fora da autorização são interrompidas antes da execução |

CA-016: fixtures de segurança verificam RNF-001/002; CA-017: colisão de execução
preserva relatórios conforme RNF-005; CA-018: documentação atende RNF-006.
Os IDs CA-001 a CA-018 deste PRD são distintos dos IDs CA-01 a CA-15 da proposta
de desenho. A rastreabilidade posterior usará sempre o documento junto ao ID.

## 7. Restrições técnicas

A arquitetura de núcleo, especialistas e workflows e os três runtimes foram aprovados
na conversa. A especificação técnica definirá interfaces, dependências e exportação.
Contratos de implementação vivem em `tasks/prd-pwdev-qa/` por exigência do AGENTS.md;
artefatos no projeto consumidor usam `.planning/pwdev-qa/` conforme a proposta.

Não alterar configurações pessoais nem instalar runtimes ou dependências implicitamente.
A disponibilidade dos três runtimes e de um exportador PDF deve ser verificada na
etapa técnica. Sua indisponibilidade não equivale a teste aprovado.

## 8. Riscos

| Risco | Mitigação e sinal |
|---|---|
| Skills amplas, mas superficiais | Avaliar cenários completos por especialidade; só checklist genérico não satisfaz CA-002 |
| Alegação de portabilidade baseada apenas em mocks | Exigir CA-003 separado dos testes unitários |
| Relatório apresenta falso aceite | Fixtures negativas de CA-006/010/012 e revisão da avaliação semântica |
| Vazamento em anexos | Evidências sanitizadas, confinamento e fixture CA-016 |
| PDF ilegível ou diferente do HTML | Comparação de conteúdo e inspeção visual CA-007/008 |

## 9. Cronograma e sequência

Não há prazo informado; não estimar datas sem decomposição técnica.
Sequência: aprovação do PRD, roadmap de features, STORIES e desenho técnico,
planos de execução aprovados, implementação com TDD, revisão e verificação.
O relatório HTML/PDF é entrega obrigatória da v1. Nenhuma etapa de planejamento
constitui evidência de execução de testes ou implementação do plugin.

## 10. Apêndices e gate

Fontes: pedido do usuário, decisões explicitamente aprovadas na conversa e
`design.md`. Referências de implementação observadas: pwdev-flow, pwdev-devops e
adaptador Hermes do pwdev-power.

Checklist de preparação do PRD:

- [x] Recuperar visão e escopo da conversa sem repetir perguntas respondidas.
- [x] Relacionar cada MUST a critérios de aceite.
- [x] Definir requisitos não funcionais verificáveis.
- [x] Separar requisito de produto de detalhe de implementação.
- [x] Incorporar relatório HTML/PDF e validação do aceite.
- [ ] Obter aprovação explícita deste PRD.

O power-product exige apresentar o requisito e aguardar aprovação. Este arquivo
permanece DRAFT; usar o Power não dispensa os gates explícitos do AGENTS.md.
Após aprovação, seguir para roadmap e detalhamento sem repetir o levantamento.
