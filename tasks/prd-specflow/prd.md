---
type: PRD
okf_version: "0.2"
generated:
  by: agent:pwdev-power
  at: "2026-09-12T10:38:47Z"
lifecycle:
  status: APPROVED
human_approval: APPROVED
sources:
  - resource: .planning/power/product/prd.md
  - resource: .planning/power/features/specflow-m01/task-01-brief.md
  - resource: plugins/sdd-composy/templates/prd.md
verified:
  - event: human_approval
    by: human:user
    at: "2026-09-12T11:28:23Z"
    scope: tasks/prd-specflow/prd.md
    source: "user: aprovado"
---

# SpecFlow — Product Requirements Document

Contrato aprovado pelo usuário em 2026-09-12T11:28:23Z. A aprovação histórica do PRD Power é proveniência;
somente o evento acima aprova estes bytes. Autoria conduzida por pwdev-power; o template SDD foi
consultado como dado, sem executar skills ou scripts SDD/Flow.

Fontes: [PRD Power](../../.planning/power/product/prd.md),
[brief M01.01](../../.planning/power/features/specflow-m01/task-01-brief.md) e
[template de referência](../../plugins/sdd-composy/templates/prd.md).
Os IDs RF/CA abaixo conservam o sufixo dos FR/AC de origem; não renumerar nem reutilizar.
Metadados da fonte não concedem aprovação local; a decisão registrada neste documento concede.

## Problem

Equipes e operadores do CompozyOS precisam desenvolver a partir de especificações,
sem perder decisões humanas, rastreabilidade e provas de qualidade entre sessões.
O método SDD existente depende de convenções de outros runtimes. Copiá-lo sem
qualificar as garantias pode produzir aprovações sem vínculo ao conteúdo, relatórios
sem prova e automação não autorizada. A evidência da necessidade é o pedido e o PRD
Power de origem; não foram presumidos dados de mercado ou pesquisa com usuários.

## Objectives

- O-001 (G-001) — Preservar os gates e o método SDD no CompozyOS.
- O-002 (G-002) — Atender roadmap, Feature independente e QUICK.
- O-003 (G-003) — Manter o fluxo básico utilizável sem capacidades opcionais.
- O-004 (G-004) — Oferecer evidências rastreáveis a cada critério aceito.
- O-005 (G-005) — Consultar status sem efeitos colaterais.
- O-006 (G-006) — Distribuir o inventário contratado de recursos nativos.

## Success Metrics

| Objetivo | Métrica | Baseline | Meta | Janela |
|---|---|---|---|---|
| O-001 | Gates obrigatórios representados e testados | Não medido | 100% | Aceite v1 |
| O-002 | Jornadas obrigatórias aceitas | Não medido | 3 de 3 | Aceite v1 |
| O-003 | Jornadas básicas sem opcionais | Não medido | 3 de 3 | Aceite v1 |
| O-004 | Critérios aceitos ligados a teste, resultado, arquivo e hash válidos | Não medido | 100% | Cada conclusão |
| O-005 | Consultas que criam execução, alteram estado ou enviam mensagens | Não medido | 0 | Ensaios de status |
| O-006 | Inventário validado | Não medido | 9 agentes, 20 skills, 4 Loops e 11 templates SDD | Aceite v1 |

## Scope

### In Scope

Nome público SpecFlow; identificador `sdd-flow`, distribuição `plugins/sdd-flow/`
e prefixo de recursos `sdd-flow-*`. O inventário exige 9 agentes, 20 skills, 4 Loops
e 11 templates SDD individuais, com complementos explícitos: `roadmap.md`,
`environment.md`, `approval-receipt.md`, `export-receipt.md` e `evidence-report.html`.
São restrições aprovadas de produto, não seleção de componentes neste PRD.

Ciclo INIT → MAP → PRD → STORIES → TECHSPEC → TASKS → EXECUTE → QA → EVIDENCE →
REVIEW → VERIFY → COMPLETE; roadmap e QUICK como entradas apropriadas. Incluem-se
status mínimo, evidência/exportação, qualificação central e opcionais autorizados:
worktree por Feature, Docker local, Live e playwright-cli. A distribuição é somente
de recursos, sem dependência operacional dos plugins de referência.

### Out of Scope

Fleet, paralelismo automático, merge automático, publicação externa automática,
agentes ou daemon em containers, Docker remoto, Network multi-daemon, MCP próprio,
hooks, automações agendadas e migração/sincronização automática de estado legado.
Não instalar ferramentas automaticamente, descartar dados/volumes automaticamente,
substituir governança, distribuir helpers executáveis no consumidor ou alterar os
plugins de referência. Este PRD não escolhe APIs, schemas, providers ou componentes.

## Assumptions

- A-001 — A equivalência entre recursos nativos e garantias centrais ainda não está
  demonstrada; M01 deve comprová-la antes da liberação de módulos dependentes.
- A-002 — Não há contexto project.md/stack.md disponível para esta parcela. Não
  inferir stack ou arquitetura de testes observados.
- A-003 — Integrações opcionais podem estar ausentes no consumidor. Isso permite
  trabalho independente, não dispensa testes/exportações contratados nem sua
  qualificação para distribuir a v1.

## Dependencies

- D-001 — Responsável humano: aprovar separadamente PRD, Stories/aplicabilidade,
  design, escopo e conclusão; criação de arquivo não é decisão.
- D-002 — Responsável pela qualificação: demonstrar comandos/versão e comportamento
  do runtime em escopo aprovado. Help/build não são prova comportamental.
- D-003 — Operador: autorizar capacidades e ambientes opcionais exatos antes do uso.
  Indisponibilidade deve gerar recomendação e alternativas qualificadas consentidas.
- D-004 — Avaliadores independentes: fornecer QA, review e verify com evidência fresca.

## Open Questions

- Q-001 — Nenhuma questão de produto adicional foi identificada na fonte aprovada.
  O próximo gate é a decisão humana sobre este PRD. Sintaxes, permissões e garantias
  nativas continuam questões de qualificação, não capacidades presumidas.

## Functional Requirements

### RF-001 — Ciclo com gates separados (FR-001, Must)

Conduzir todas as etapas do ciclo com aprovações humanas aplicáveis separadas.
Stories só podem ser NOT_APPLICABLE para trabalho puramente interno, com justificativa
e decisão explícitas. QA/review/verify permanecem independentes da implementação.

### RF-002 — Entradas sem roadmap obrigatório (FR-002, Must)

Permitir Feature independente e QUICK diretamente, além da promoção controlada de
uma Feature de roadmap aprovado. Aprovação de origem não aprova o contrato derivado.

### RF-003 — Aprovações vinculadas ao conteúdo (FR-003, Must)

Recusar avanço com aprovação pendente, rejeitada, stale ou digest divergente.
Solicitar reconciliação do contrato dono da decisão e de dependências afetadas,
preservando histórico. Metadados, existência e confiança não autorizam execução.

### RF-004 — Status mínimo somente leitura (FR-004, Must)

Informar Feature, tarefa, gates, próxima ação permitida, ambiente e opcionais com
fonte, horário e confiança. Distinguir desconhecido, ausência, bloqueio e divergência.
Não iniciar execução, enviar mensagens ou alterar estado durante consulta.

### RF-005 — Descoberta opcional sem instalação (FR-005, Must)

INIT detecta/recomenda sem instalar, baixar, provisionar, criar worktree, abrir browser
ou ativar Live. Permite continuar trabalho independente sem essas capacidades;
alternativa não pode substituir silenciosamente requisito contratual.

### RF-006 — Padrões locais e consentimento (FR-006, Must)

Usar checkout atual e Network Local como padrões. Worktree por Feature, Docker Compose
e Live são opcionais, escolhidos/autorizados explicitamente por execução. Live não
substitui gates e seu consentimento não pode ampliar-se silenciosamente.

### RF-007 — Ambiente local de teste isolado (FR-007, Must)

Docker inclui apenas aplicação e dependências de teste; agentes e daemon permanecem no host.
Features autorizadas podem ter worktrees/Compose distintos, sem colisões de portas,
processos, contratos ou dados. Preservar recursos alheios e dados por padrão; limpeza
e reaproveitamento exigem propriedade comprovada e autorização correspondente.

### RF-008 — Browser opcional, aceite obrigatório (FR-008, Must)

playwright-cli auxilia QA, sem substituir a suíte adotada. Se um critério obrigatório
não puder ser executado com browser adequado ou alternativa qualificada, registrar
NOT_RUN e bloquear seu aceite. Ausência nunca significa PASS ou NOT_APPLICABLE.

### RF-009 — Evidência e exportações contratadas (FR-009, Must)

Vincular evidência real a requisitos e testes. Suportar HTML, PDF ou ambos conforme
contrato; formato solicitado ausente/falho impede concluir a entrega. Preservar
resultados negativos, fontes e integridade; não publicar automaticamente.

### RF-010 — Retomada consistente (FR-010, Must)

Retomar do último estágio publicado com sucesso sem repetir decisões válidas ou
etapas concluídas. Conservar histórico/contadores; invalidar resultados dependentes
de conteúdo alterado. Nunca registrar sucesso antes de ocorrer a ação representada.

### RF-011 — Correção limitada (FR-011, Must)

Limitar a 3 tentativas totais por tarefa, incluindo a primeira; janela de ausência de progresso 2,
fan-out 1. Preservar contador em filhos e retomada. Parar por ausência de progresso,
ampliação, ambiguidade arquitetural, operação destrutiva, autorização externa faltante,
falha irrecuperável ou cancelamento; nunca mudar escopo durante correção autônoma.

### RF-012 — Distribuição nativa autocontida (FR-012, Must)

Entregar somente recursos nativos, sem SDK, subprocesso, hook, MCP próprio ou helper
executável no consumidor. Não depender operacionalmente de sdd-composy, pwdev-flow,
pwdev-code ou pwdev-power; SDD permanece referência funcional/de templates.

### RF-013 — Qualificação verificável (FR-013, Must)

Apresentar comando, versão, esperado, observado, resultado e prova de gates/digests,
schemas, carregamento, atomicidade, histórico/retomada, confinamento, observação sem
efeitos, isolamento de papéis e exclusão mútua. Garantia central falha, NOT_RUN ou não
demonstrada bloqueia dependentes. Receita sem comando qualificado permanece BLOCKED;
nenhum probe mutável ocorre sem receita e escopo aprovados.

### RF-014 — Recibos preservando decisões e fontes (FR-014, Must)

Produzir registros separados de aprovação, Live, ambiente e exportações. Relacionar
decisões reais ao conteúdo/hashes sem reescrever evidência aprovada, transferir
aprovação histórica ou criar uma segunda autoridade operacional.

### RF-015 — Resumo agregado opcional (FR-015, Could)

Disponibilizar resumo da Feature concluída sem substituir seus relatórios independentes.
Não constitui requisito Must nem dispensa a verificação agregada obrigatória.

### RF-016 — Exclusões explícitas da v1 (FR-016, Won't)

Respeitar integralmente Out of Scope; não oferecer Fleet, paralelismo/merge/publicação
automáticos, containers de agentes, Docker remoto, Network multi-daemon, MCP, hooks
ou migração legada como capacidades implicitamente suportadas.

### RF-017 — Conclusão real da Feature (FR-017, Must)

Exigir tarefas aplicáveis completas, integração fresca, QA/review/verify independentes,
dossier/exportações contratados íntegros e gate humano final. Run done ou contagem de
tarefas nunca conclui Feature; pendências mantêm o bundle incompleto.

## Non-functional Requirements

- NFR-001 — QUICK: até 5 arquivos de implementação; testes/evidência contados separadamente.
  Arquitetura, migração, destruição, ampliação ou verificação desconhecida escalonam antes da edição.
- NFR-002 — Máximo de 3 tentativas totais por tarefa, incluindo a primeira.
- NFR-003 — 100% dos Must devem ter critério verificável e prova antes da conclusão.
- NFR-004 — Zero leitura/publicação de segredos, .env, credenciais, tokens, chaves,
  certificados, cookies, auth storage ou dumps. Não sobrescrever governança/symlinks
  nem alterações alheias.
- NFR-005 — 100% das evidências aceitas: arquivo regular relativo ao checkout, sem
  symlink/traversal, com SHA-256 minúsculo de 64 caracteres dos bytes reais. Preservar
  campos desconhecidos, publicar atomicamente e só registrar evento após sucesso.
- NFR-006 — Zero instalação, ativação Live, provisionamento, criação de worktree,
  merge ou publicação sem ação e consentimento correspondentes.
- NFR-007 — HTML escapa conteúdo hostil; PDF solicitado deriva do HTML validado,
  sem scripts ativos/fetch externo não autorizado, com imagens, inspeção visual e hash.
- NFR-008 — Todas as jornadas obrigatórias exigem provas reais e zero falhas de aceite.
- NFR-009 — Pacote com exatamente o inventário e complementos descritos em Scope.

Restrições herdadas do brief: idiomas pt-BR e en-US, definidos somente em INIT;
contract_root = execution_root = checkout_root validado pelo runtime. Contrato de
tarefa em `tasks/prd-<slug>/task-001.md`; perfil nativo em `.planning/sdd-composy/`,
sem presumir compatibilidade legada. Manifesto-fonte: schema_version "1",
result passed|failed|not_applicable e evidence_type test_output|screenshot|log|report.
Verdict claim: PASS|FAIL|STALE|ENVIRONMENT_FAILURE|NOT_RUN. Estes valores são restrições
de compatibilidade; schemas e interfaces detalhados pertencem ao design posterior.

## Acceptance Criteria

### CA-001 — RF-005, RF-006; origem AC-001

Dado consumidor sem opcionais, quando INIT roda, então recomenda capacidades ausentes
sem instalação/ativação e permite o fluxo básico sem Docker, Live, browser ou PDF.

### CA-002 — RF-001, RF-002, RF-003; origem AC-002

Dada Feature sem roadmap, quando especificada, então PRD, Stories/aplicabilidade,
TechSpec e tarefas recebem decisões independentes antes de executar.

### CA-003 — RF-002, RF-003, RF-011; origem AC-003

Dado QUICK elegível, quando aprovado, então mantém TDD, QA, evidência, review e verify;
sexta alteração de implementação ou condição de escalonamento impede editar.

### CA-004 — RF-002; origem AC-004

Dado roadmap aprovado, quando promovido um item, então registra origem e novos gates;
sem roadmap, Feature independente e QUICK continuam disponíveis.

### CA-005 — RF-006, RF-007; origem AC-005

Dadas duas Features autorizadas, quando provisionadas, então checkouts, projetos,
portas, processos e dados permanecem distintos, com apenas app/testes em containers;
limpar um ambiente não afeta o outro nem descarta dados sem autorização.

### CA-006 — RF-006, RF-014; origem AC-006

Dado Network Local, quando falta consentimento Live válido, então impede participação;
quando autorizado, registra escopo/recibo sem compartilhar segredos.

### CA-007 — RF-008, RF-009, RF-014; origem AC-007

Dado contrato HTML/PDF, quando exporta evidência real, então vincula artefatos,
preserva pendências/falhas, sanitiza e calcula hashes; formato contratado falho
impede conclusão, e PDF exige inspeção visual, não só existência.

### CA-008 — RF-004, RF-010; origem AC-008

Dada qualquer etapa, quando consultado status, então não cria execução/mensagem/mutação
e distingue ausência, pendência, bloqueio/divergência com fonte, horário e confiança.

### CA-009 — RF-010, RF-011; origem AC-009

Dada correção autorizada, quando retoma, então conserva contadores/escopo e encerra
em sucesso ou parada dentro de três tentativas totais, sem reiniciar limite em filhos.

### CA-010 — RF-012, RF-016; origem AC-010

Dado pacote em ambiente limpo suportado, quando instalado com autorização, então
descobre todos os recursos sdd-flow-* e inventário exato sem plugins-fonte no runtime
ou funções fora da v1. Instalação não ativa opcionais.

### CA-011 — RF-003, RF-014; origem AC-011

Dada aprovação pendente/rejeitada ou conteúdo alterado, quando tenta avançar, então
recusa e identifica contrato para nova decisão; metadados não autorizam outros bytes.

### CA-012 — RF-008; origem AC-012

Dado browser obrigatório indisponível, quando QA avalia, então usa alternativa
qualificada autorizada ou registra NOT_RUN e bloqueia aceite, nunca PASS/N/A.

### CA-013 — RF-010; origem AC-013

Dada interrupção após publicação bem-sucedida, quando retoma, então conserva resultados,
contadores/decisões válidas e segue etapa permitida; alteração invalida dependentes.

### CA-014 — RF-013; origem AC-014

Dado runtime candidato, quando qualificado em escopo aprovado, então cada garantia
central tem cenário positivo/negativo com comando e resultado observados. Falha,
NOT_RUN ou garantia não demonstrada bloqueia dependentes; help/build não comprovam execução.

### CA-015 — RF-001, RF-017; origem AC-015

Dadas tarefas completas, quando fecha Feature, então exige QA/review/verify independentes,
integração/verificação agregada fresca, dossier/exportações íntegros e aceite humano
final; sem isso continua incompleta apesar de Run done.

### CA-016 — RF-009, RF-014; origem AC-016

Dado relatório aguardando aceite, quando aprovado, então recibo separado vincula decisão
aos hashes do snapshot/exportações e os arquivos aprovados permanecem imutáveis.

## Gate

Este PRD foi aprovado pelo usuário em 2026-09-12T11:28:23Z para os bytes apresentados.
A aprovação libera a produção de Stories/aplicabilidade, mas não aprova Stories, design,
execução ou completion.
Após este gate, produzir Stories/aplicabilidade e solicitar seu gate separado;
nenhum desses documentos, receita ou probe é produzido nesta parcela. Verificação
estrutural deste documento não comprova comportamento de runtime nem aceite do produto.
