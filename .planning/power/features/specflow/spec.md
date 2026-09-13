---
type: TECHNICAL_PROPOSAL
okf_version: "0.2"
generated:
  by: agent:power-roadmap
  at: "2026-09-12T10:31:30Z"
lifecycle:
  status: APPROVED
sources:
  - resource: ".planning/power/product/prd.md"
  - resource: "/Users/paulosoares/Projetos/skills-ia/pwdev-claude-marketplace/tasks/prd-sdd-composy-native-extension/plano-execucao.md"
verified:
  - event: human_approval
    by: human:user
    at: "2026-09-12T10:35:43Z"
    scope: specflow_v1_power_plan
    source: "user: aprovado"
---

# SpecFlow — Spec

Status: APPROVED
Updated: 2026-09-12
Source: [PRD](../../product/prd.md)
Historical source: /Users/paulosoares/Projetos/skills-ia/pwdev-claude-marketplace/tasks/prd-sdd-composy-native-extension/plano-execucao.md
Historical SHA-256: e68288470ad2efb3dce373e5cd0a1c430c0b2699386c1de8bee4a8059ba5fa9c

## Goal
Entregar a extensão SpecFlow somente de recursos nativos CompozyOS, preservando o método SDD, suas três entradas, gates e evidência, com autoria governada por Power.

## Global Constraints
- Nome público: SpecFlow. Plugin: plugins/sdd-flow. Identificador: sdd-flow. Prefixo de recursos: sdd-flow-*.
- Inventário v1: 9 agentes, 20 skills, 4 Loops e 11 templates SDD individuais; complementos explícitos: roadmap.md, environment.md, approval-receipt.md, export-receipt.md e evidence-report.html.
- Autoria: somente pwdev-power; recursos SDD são referência do produto. Não executar scripts SDD/Flow, alterar fontes de outros plugins, instalar helpers no consumidor ou substituir AGENTS.md.
- PRD Power, spec, rastreabilidade e os 12 planos foram aprovados pelo usuário em 2026-09-12T10:35:43Z. A execução segue os gates internos de PRD, Stories/aplicabilidade, TechSpec e escopo; completion requer verificação independente e aprovação humana.
- Power: até 8 tarefas por plano, 5 arquivos por tarefa incluindo testes, 7 passos por tarefa e 5 ciclos de correção de autoria; rounds 1–3 no mesmo implementador, 4–5 em novo implementador conforme runtime. Isso não amplia limites canônicos nem os limites do produto.
- Produto: até 3 tentativas totais por tarefa incluindo a primeira, janela de ausência de progresso 2, fan-out 1; contador persiste em filhos e retomada. QUICK: até 5 arquivos de implementação; testes/evidência contados separadamente. Sem Fleet, paralelismo ou merge automático.
- M01 qualifica obrigatoriamente gates humanos/digests, schemas, carregamento, atomicidade, histórico/retomada, confinamento, observação sem efeitos e exclusão mútua; falha, NOT_RUN ou garantia não demonstrada bloqueia módulos dependentes. Help/build não comprovam comportamento.
- Checkout atual e Network Local são padrões; worktree por Feature, Docker local de app/testes, Live e playwright-cli são opcionais. INIT detecta/recomenda sem instalar, provisionar, abrir browser ou ativar Live; agentes/daemon permanecem no host.
- contract_root = execution_root = checkout_root validado pelo runtime. Contratos de produto: tasks/prd-<slug>/task-001.md; configuração/contexto do perfil nativo: .planning/sdd-composy/. Compatibilidade legada nunca é presumida.
- Nunca ler segredos, .env, credenciais, tokens, chaves, certificados, cookies, auth storage ou dumps; nunca sobrescrever governança, symlinks ou alterações alheias.
- ArtifactRef usa caminho relativo confinado, arquivo regular sem symlink/traversal e SHA-256 minúsculo com 64 caracteres; preservar campos desconhecidos, publicar atomicamente e registrar sucesso antes do evento.
- Idiomas do produto: pt-BR e en-US, definidos somente em INIT. Manifesto-fonte: schema_version "1", result passed|failed|not_applicable, evidence_type test_output|screenshot|log|report. Verdict claim: PASS|FAIL|STALE|ENVIRONMENT_FAILURE|NOT_RUN.
- QA sem browser adequado para critério obrigatório: NOT_RUN e critério bloqueado; ausência de ferramenta nunca é PASS nem NOT_APPLICABLE. Aprovação stale ou digest divergente bloqueia transição e exige reconciliação.
- Feature só conclui com tarefas completas, integração fresca, QA/review/verify independentes, dossier/exportações contratados íntegros e gate humano final; Run done ou contagem de tarefas não conclui Feature.
- Runtime mutável: comando e versão demonstrados localmente, receita e escopo aprovados antes do probe; comando ainda não qualificado significa BLOCKED. Não inventar sintaxe, versão, provider ou garantia.
- Testes focados test_sdd_flow_mXX_*.py devem executar mais de zero testes e terminar sem falhas. Baseline integral fb14629: 7 falhas preexistentes aceitas, reproduzidas com mesmos IDs e causas; nenhuma falha nova, omitida ou trocada pode ser ocultada por contagem <=7.

## Autoria Power e autoridade
Este documento foi aprovado pelo usuário em 2026-09-12T10:35:43Z e libera o handoff controlado para `power-execute`. O PRD local é a fonte de requisito; a fonte histórica é preservada abaixo apenas nas cláusulas necessárias ao contrato, com nomes atualizados. A autoria usa power-product, power-plan, power-execute, power-review, power-verify e power-finish. As obrigações canônicas de contratos e gates humanos continuam vinculantes; a aprovação desta spec não cria TASK-NNN ready nem substitui os gates internos.
As regras referenciadas por AGENTS.md e os contextos Power project.md/stack.md não existem neste checkout. As regras foram consultadas no checkout principal; o plano não supõe que links ausentes sejam resolvidos. Observação local: tests/test_pwdev_power.py e tests/test_sdd_composy.py usam unittest; plugins/sdd-composy/templates/ e plugins/pwdev-power/ existem. Cada novo caminho é marcado CREATE; não é alegado como existente.
Power separa seus até cinco ciclos de correção de autoria das três tentativas totais do produto. Rejeição humana volta ao artefato dono; não é autorização para retry cosmético. Não tocar state.md alheio, branch, commits ou código na elaboração desta proposta.

## Preparação de contratos sem circularidade
M01.01 redige por Power o PRD canônico derivado do PRD Power, apresenta seu gate e depois Stories/aplicabilidade com gate separado. M01.02 redige TechSpec derivado desta spec, apresenta gate e só então TASKS/escopo para aprovação. Paths propostos: tasks/prd-specflow/{prd,stories,techspec,tasks}.md; nenhuma dessas propostas ou TASK-NNN foi criada nesta rodada. M01.03 somente executa probes depois dos quatro gates, qualificação de comando e autorização da receita mutável. Redigir proposta não exige sua própria aprovação prévia; executar código exige todos os gates.

## Interfaces normativas adicionais
As assinaturas são contratos de dados/nós propostos, não APIs já comprovadas do CompozyOS. M01 precisa demonstrar o binding concreto antes de implementá-las. null significa não conhecido/não aplicável justificado; lista vazia somente depois de consulta concluída. Timestamps são RFC3339 UTC, strings são não vazias salvo descrição explicitamente opcional.
- RuntimeQualification = {version: string, command_recipes: RuntimeRecipe[], core_checks: QualificationCheck[], optional_checks: QualificationCheck[], verdict: PASS|FAIL|BLOCKED, evidence_refs: ArtifactRef[]}.
- RuntimeRecipe = {id: string, executable: string, argv: string[], cwd: string, mutable_scope: string[], approved_scope: ApprovalRef|null, expected: string, observed: string, result: PASS|FAIL|ENVIRONMENT_FAILURE|NOT_RUN, evidence_refs: ArtifactRef[]}. Ausência de argv comprovado impede execução, não admite preenchimento especulativo.
- QualificationCheck = {id: string, guarantee: string, positive_recipe: string, negative_recipe: string, revision_ref: string, result: PASS|FAIL|ENVIRONMENT_FAILURE|NOT_RUN, evidence_refs: ArtifactRef[]}.
- ResourceSet = {paths: string[], source_digests: object<string,string>, interfaces: string[], validation_refs: ArtifactRef[]}; representa recursos estáticos, sem estado operacional alternativo.
- BaselineFailure = {test_id: string, exception_type: string, normalized_cause: string, baseline_commit: string, evidence_ref: ArtifactRef}; BaselineComparison = {baseline: BaselineFailure[], current: BaselineFailure[], new_failures: BaselineFailure[], missing_tests: string[], accepted_by: ApprovalRef|null}.
- FeatureClosure = {checkout_ref: CheckoutRef, task_results: DeliveryResult[], integration_results: CommandResult[], qa_ref: ArtifactRef, review_ref: ArtifactRef, verdict_ref: ArtifactRef, dossier_refs: ArtifactRef[], exports: ExportResult[], final_approval: ApprovalRef|null, complete: boolean}.
- sdd-flow-init(input: StageInput) -> StageResult; sdd-flow-map(input: StageInput) -> StageResult; capacidades são CapabilityResult[] ligados ao resultado.
- sdd-flow-prd(input: StageInput) -> StageResult; sdd-flow-stories(input: StageInput) -> StageResult; sdd-flow-roadmap(input: StageInput) -> StageResult; sdd-flow-promote(input: StageInput) -> Handoff.
- sdd-flow-feature(input: StageInput) -> Handoff.
- sdd-flow-techspec(input: StageInput) -> StageResult; sdd-flow-tasks(input: StageInput) -> StageResult.
- sdd-flow-environment(plan: EnvironmentPlan) -> EnvironmentRef; sdd-flow-network(participation: ParticipationRef) -> ParticipationRef.
- sdd-flow-execute(input: Handoff) -> StageResult; sdd-flow-qa(input: Handoff) -> StageResult; sdd-flow-evidence(input: Handoff) -> StageResult; sdd-flow-review(input: Handoff) -> StageResult; sdd-flow-verify(input: Handoff) -> StageResult.
- sdd-flow-delivery(input: Handoff) -> DeliveryResult; mode feature exige FeatureClosure.complete antes de feature_verified=true.
- sdd-flow-evidence-export(input: Handoff) -> ExportResult[]; sdd-flow-quick(input: StageInput) -> DeliveryResult; sdd-flow-status(input: StageInput) -> StatusResult.
- Revalidação ApprovalRef: comparar snapshot apresentado, decisão humana e digest publicado; somente metadados derivados da decisão podem mudar no fechamento e demais bytes permanecem iguais. prerequisites são revalidados recursivamente, sem autoaprovação por estado.
- Retomada: publicar estágio atomicamente; interrupção antes da publicação não emite sucesso; após publicação não repete estágio/gate válido. Código/contexto material/evidência alterados tornam dependentes STALE e exigem testes reais frescos; contador não reinicia.
- StatusResult.schema = "sdd-flow.status/v1". CommandResult.result nunca é convertido diretamente ao enum de evidence-manifest.
- Parâmetros finitos de ParticipationRef.bounds, timeout/health e cleanup são definidos no plano aprovado da execução após capacidade qualificada. Nenhum default de timeout novo é presumido.

## Critérios de aceitação técnica
| ID | Critério | Módulos |
|---|---|---|
| AT-01 | Qualificação central positiva/negativa com execução real, identidade humana, digest alterado, confinamento, transação interrompida, concorrência, recuperação e zero efeito do observer | M01, M12 |
| AT-02 | 17 skills-fonte mapeadas cláusula a cláusula, schemas fiel/nativo separados, 11 templates individuais preservados, links resolvíveis e bindings verificados | M02, M03, M12 |
| AT-03 | INIT sem opcionais, idioma único, legado recusado sem mutação e MAP apenas observacional | M04, M12 |
| AT-04 | Três entradas: roadmap opcional/promovido, standalone e QUICK, gates de contrato distintos sem herança de aprovação | M05, M06, M11 |
| AT-05 | Checkout inequívoco; transferência de bundle não commitado por digest e decisão; dois ambientes isolados, engine/bind/mounts/health e cleanup próprios | M07, M12 |
| AT-06 | RED real, comandos aprovados, QA/review/verifier separados, NOT_RUN bloqueante, nenhuma evidência inventada | M08, M12 |
| AT-07 | Máximo 3 tentativas, stalled em janela 2, cancelamento, digest stale e retomada preservando contador/publicação comprovados com testes reais | M01, M08, M12 |
| AT-08 | Local explícito; Live por execução e filho autorizado, sem ampliação, gate por mensagem ou default global | M09, M12 |
| AT-09 | HTML sanitizado, PDF inspecionado/hash, fetch/script bloqueados, dossier após review/verify, export solicitado indisponível bloqueia entrega | M10, M12 |
| AT-10 | Status completo com fonte/tempo/confiança e sem Run, escrita, mensagens ou browser; entrada maliciosa não amplia ferramentas | M11, M12 |
| AT-11 | Fechamento obrigatório de Feature integra tarefas, testes frescos, QA/review/verdict e recibo humano final separado | M08, M10, M12 |
| AT-12 | Build/validação em geração real e jornadas nativas aceitas; suíte focada verde não vazia; baseline por IDs/causas, zero nova falha | M12 |

## Qualificação e liberação
M01 bloqueia M02–M12 até PASS de cada garantia central e aceite técnico/humano aplicável. Ferramenta opcional ausente num consumidor permite INIT/fluxo básico, mas uma capacidade prometida da distribuição exige prova em ambiente autorizado antes de release. Se qualquer garantia não puder ser fornecida sem helper distribuído, registrar incompatibilidade e retornar ao design; não contornar com prompt ou remover escopo silenciosamente.
Cada ensaio guarda workspace isolado, inputs sanitizados, versão, argv real, escopo/receita aprovados, esperado/observado, IDs Run/gate/decision, inventário antes/depois, cleanup e classificação. Os comandos de runtime são qualificados antes de constarem como executáveis. Os testes unittest especificados nos planos serão criados; hoje zero testes encontrados é NOT_RUN. Não executar probes durante esta proposta.
A suíte integral de referência é `rg --files tests -g 'test_*.py' | sort | sed 's#/#.#g; s#\.py$##' | xargs python3 -m unittest`, com 670 testes/7 falhas históricos em fb14629. Antes de liberar, reproduzir baseline isolado autorizado, registrar exatamente IDs/tipos/causas e comparar ao checkout entregue, incluindo testes removidos. Contagem não é identidade; baseline não reproduzido bloqueia conclusão.
Release requer AT-01–AT-12, todos AC do PRD, inventário/bindings/link validation e ausência de dependência operacional de outros plugins. Jornada real em runtime qualificado para QUICK, standalone e promoção roadmap deve incluir modo sem opcionais, duas Features com worktree/Compose em portas/dados distintos, Live fora de escopo recusado, PDF solicitado incompleto bloqueado, stale/cancel/resume e status sem efeito. Só build, help, schema ou mocks não bastam. QA/review/verdict independentes e gate final humano obrigatórios.

## 1. Política de fidelidade ao SDD

### Regras de portabilidade

Cada skill nativa deriva da skill SDD correspondente, conservando inputs, procedimento, outputs, condições de parada e referências. Manter nomes de arquivos de templates, tipos OKF, seções e tabelas; não substituir os onze templates por dois documentos genéricos.

A adaptação remove chamadas a helpers não empacotados, variáveis como CLAUDE_PLUGIN_ROOT e descoberta de providers de outros runtimes. Uma chamada removida precisa de uma capacidade nativa comprovada que cumpra sua garantia; texto em prompt não substitui validação, confinamento, exclusão mútua ou atomicidade.

`provenance.md` registra por recurso: fonte exata, revisão/digest, cláusulas preservadas, diferenças, motivo e testes. Ajustes técnicos novos desta consolidação permanecem sujeitos ao gate de TechSpec. Não modificar `plugins/sdd-composy/` nesta entrega.

### Mapeamento das 17 skills-fonte

| Fonte SDD | Destino | Fidelidade e ajuste delimitado |
|---|---|---|
| sdd-init | sdd-flow-init | Idioma/actor, preview, criação apenas de ausências, diagnóstico e verificação; perfil nativo e descoberta opcional |
| sdd-map | sdd-flow-map | Observação, exclusão de segredos, commit e staleness; mecanismo de publicação nativo qualificado |
| sdd-prd | sdd-flow-prd | Problema, objetivos, RF/CA e aprovação; não decide arquitetura |
| sdd-stories | sdd-flow-stories | Actors/Journeys/US/SC, dependências, edge cases e gate de aplicabilidade |
| sdd-techspec | sdd-flow-techspec | Inventário, interfaces, decisões/riscos, testes e gate |
| sdd-tasks | sdd-flow-tasks | TASK-NNN, dependências, allowlist e comandos; projeção operacional adaptada explicitamente |
| sdd-execute | sdd-flow-execute | Uma tarefa ready, TDD real, escopo, ownership/cleanup, resultado e próxima transição |
| sdd-qa | sdd-flow-qa | Cobertura CA/SC, testes, browser quando aplicável, acessibilidade, regressão e gate humano |
| sdd-evidence | sdd-flow-evidence | Inventário, manifesto criterion-linked, tipos/resultados reais e hashes; exportação em procedimento separado |
| sdd-review | sdd-flow-review | Diff explícito, achados/rule citations, comandos, conformidade e gate humano; sem silent fix |
| sdd-verify | sdd-flow-verify | Truth table, comandos frescos, ator independente e parecer; aprovação humana de conclusão |
| sdd-quick | sdd-flow-quick | Q-* mais tarefa normal, cinco arquivos, TDD e cadeia de qualidade completa |
| sdd-status | sdd-flow-status | Consulta conservadora, confiança por fonte, divergências e próxima ação; extensões de ambiente/capacidades |
| sdd-loop | sdd-flow-delivery.yaml | Motor nativo coordena as etapas SDD; sem skill com motor concorrente |
| sdd-trace | evidence/status e histórico nativo qualificado | Preservar rastreabilidade e sucesso antes do evento; record/build/projeção legada não são portados |
| sdd-sync | Não distribuída na v1 | Diagnóstico permanece; sem apply ou migração automática |
| sdd-fleet | Não distribuída na v1 | Sem runner Fleet; worktree nativo opcional continua incluído |

### Templates individuais e diferenças permitidas

Os onze arquivos abaixo permanecem em `skills/sdd-flow-contracts/templates/`, com os mesmos nomes da fonte.

| Template | Elementos obrigatórios preservados |
|---|---|
| prd.md | PRD; Problem, Objectives, Success Metrics, Scope, Assumptions, Dependencies, Open Questions, RF, CA, Gate |
| stories.md | STORIES; Actors, User Journeys, User Stories, Dependencies, Edge Cases, Gate e applicability |
| techspec.md | TECHSPEC; contexto, componentes, interfaces, condicionais Data Model/API, DEC/RISK, TU/TI/E2E, Gate |
| tasks.md | TASKS; Task index, Traceability, Human gate; links task-001.md |
| task.md | TASK; task.id/state/dependencies/allowed_paths/acceptance_criteria/verification_commands/evidence_required; Intent, Dependencies, Allowed files, Subtasks, Acceptance and verification, Human gate |
| quick-contract.md | QUICK_CONTRACT; Objective, Acceptance criteria, Scope gate, TDD and evidence, Escalation |
| quick-report.md | QUICK_REPORT; Contract, Evidence, Verdict; Q-ID e TASK-ID |
| qa.md | QA_REPORT; Scope and traceability, Test results, Accessibility and responsiveness, Environment and regression evidence, Gate |
| codereview.md | CODE_REVIEW; Scope, Approved contracts and rules, Findings, Verification commands, Skill conformity and no-silent-fix policy, Gate and next action |
| evidence-report.md | EVIDENCE_REPORT; origem em manifesto validado, escaping, atores separados |
| verdict.md | VERIFICATION_VERDICT; truth table, comandos/exit codes/hashes, Gate |

Ajustes necessários, sempre documentados:
- Substituir exemplos de links/comandos por destinos reais; não copiar links quebrados do exemplo `task.md` nem um CA apontando para Stories quando pertence ao PRD.
- Usar `task-001.md`, conforme template/tasks reference, substituindo a convenção genérica anterior.
- QA usa os IDs de teste reais do TechSpec. Preservar TU/TI/E2E e relacioná-los a TEST-NNN do manifesto, sem renumerar silenciosamente.
- Completar provenance, fontes e timestamp do template mínimo evidence-report.md; não inventar aprovação.
- Rebasear links dos relatórios quando armazenados por tentativa, preservando nome e conteúdo do template.
- Estado em TASK/TASKS é snapshot observado, não nova autoridade: identificar origem e instante do runtime; divergência impede transição.
- O gate do verdict distingue evento do verificador de aprovação humana; o agente não preenche a decisão humana.
- Seções não aplicáveis recebem justificativa conforme contrato SDD; não fabricar US/SC para trabalho interno ou QUICK.

Templates de AGENTS/CLAUDE/rules são referência de governança, não arquivos instalados ou sobrescritos automaticamente. O Compose de Fleet não é reutilizado: sua topologia e autoridade não correspondem ao ambiente por Feature aprovado.

## 2. Distribuição e papéis

Inventário alvo consolidado: **9 agentes, 20 skills e 4 Loops**. O teste de aceitação compara esse inventário com a geração empacotada.

| Agente sdd-flow-* | Skills sdd-flow-* | Limite |
|---|---|---|
| coordinator | intake, init, map, promote, network | Preparação/contexto, promoção e participação aprovada; não implementa código nem aprova gates |
| product | prd, stories, roadmap | Somente contratos de produto |
| architect | techspec, tasks, quick | Arquitetura e contratos de escopo; não executa provisionamento |
| environment | environment | Worktree/Compose apenas sob EnvironmentPlan aprovado; engine e recursos delimitados |
| implementer | execute | Código/testes/evidência dentro da tarefa aprovada |
| qa | qa, evidence, evidence-export | Relatórios, inventário e exportações; sessões/permissões específicas por procedimento |
| reviewer | review | Achados e evidência própria; não corrige código |
| verifier | verify | Reprodução independente e verdict; não altera contratos |
| observer | status | Consulta restrita, sem shell genérico, browser, escrita, spawn ou mensagens |

A 20ª skill é `sdd-flow-contracts`, biblioteca compartilhada de referências, schemas e templates, sem operação mutável própria. Cada agente tem AGENT.md; cada skill tem SKILL.md. Loops publicados: product, feature, quick e delivery, todos com prefixo sdd-flow- e extensão .yaml.

Não há SDK, package.json, subprocesso, hook, MCP próprio ou helper Python/Shell distribuído. Schemas e templates estáticos ficam dentro da skill de contratos para inclusão no build. Docker, browser e renderizador são ferramentas externas opcionais qualificadas do host, não dependências de outros plugins. Não gerar helpers executáveis no consumidor para contornar resource-only.

Bindings agente/skill/input/output são explícitos e testados na geração. Permissões de um nó não são a união das permissões do papel. Não usar a sessão do implementador para QA/review/verify. Modelo/provider são herdados de configuração válida, sem nomes inventados.

## 3. Lifecycle, gates e resultados

Fluxo SDD preservado:

```text
INIT → MAP → PRD → aprovação → STORIES/aplicabilidade → aprovação
     → TECHSPEC → aprovação → TASKS/contratos → aprovação
     → EXECUTE → QA → aprovação → EVIDENCE → REVIEW → aprovação
     → VERIFY → aprovação de conclusão → COMPLETE
```

Todos os quatro Loops executam preflight mesmo quando chamados diretamente: checkout registrado, governança/perfil compatível, INIT/idioma, MAP fresco relevante e gates de entrada. Product/Feature aceitam bundle novo; Delivery exige contratos existentes e aprovados. Preparação de worktree é operação explícita anterior ao Loop da Feature, não efeito automático de INIT. Ações auxiliares chamadas fora de Loop obedecem aos mesmos limites e não simulam transições.

Estados de tarefa preservados: pending, ready, running, qa_required, evidence_required, review_required, verify_required, complete, blocked, rejected e skipped. Skipped requer razão e autoridade humana; não equivale a dependência complete.

EVIDENCE é requerida por padrão, inclusive QUICK. A exceção SDD `evidence_required: false` pode existir somente no contrato full explicitamente aprovado, com registro do desvio de estágio; nunca dispensa evidências de testes/review/verify. HTML/PDF são opcionais por entrega e não definem essa exceção.

- product: PRD de produto aprovado → roadmap aprovado; encerra sem despachar Features.
- feature: PRD → Stories → TechSpec → Tasks, com gates separados; vale para standalone e promoção de roadmap.
- quick: elegibilidade → contrato Q-* e tarefa normal → aprovação → delivery compartilhado. Até cinco arquivos de implementação; testes/evidência contados separadamente. Arquitetura, migração, destruição, ampliação ou verificação desconhecida fazem ESCALATE antes de editar.
- delivery/task: uma tarefa ready, dependências complete e escopo aprovado. Corrige apenas pelo fluxo guardado rejected → ready; correção exige escopo aprovado e evidência anterior invalidada.
- delivery/feature: todas as tarefas do escopo complete; review integrado aprovado, verificação agregada fresca e aprovação final. Uma tarefa ou Run done não conclui a Feature. Não inicia a próxima tarefa automaticamente.

Correção: máximo três iterações por tarefa incluindo a primeira, sem reiniciar contador em filho/retomada; janela de ausência de progresso dois; fan-out um. Parar imediatamente por escopo, arquitetura, destruição, autorização externa, cancelamento ou ambiente irrecuperável. Rejeição humana não autoriza retry cosmético. Implementar repetição com mecanismo nativo qualificado, não grafo cíclico inválido.

Terminais nativos: done, no-op, blocked, failed, exhausted, stalled, canceled. São distintos de estados SDD e verdicts. Cada saída conserva outcome, transition, reason, next_action e evidência quando aplicável, como o contrato de execução SDD.

## 4. Autoridade, raízes e worktrees

### Perfil nativo versus legado

Contratos humanos continuam em `tasks/prd-<slug>/`; configuração/contexto em `.planning/sdd-composy/`. Runtime guarda estado operacional de execução/tarefas, decisões e histórico. Isso é uma adaptação arquitetural explícita ao SDD legado, não equivalência automática com seus helpers/JSON.

O perfil nativo só é habilitado por contrato aprovado para consumidor novo/compatível. Encontrar governança legada ou estado JSON legado não autoriza converter, sobrescrever ou escolher outra autoridade. Diagnosticar e interromper mutações incompatíveis. A governança deste repositório não é alterada pela elaboração da extensão.

Atomicidade, preservação de campos desconhecidos, retenção das decisões, recuperação, trilha de eventos e exclusão mútua devem ser demonstradas. Falha em garantia central bloqueia a entrega correspondente. Não prometer compatibilidade com trace.json ou motor de tarefas Python que não foi portado.

### Regra de raiz única por Feature

Identidade operacional: workspace_id + worktree_id (null para raiz) + bundle_path. O runtime fornece a identidade e o caminho confiável do checkout; entradas textuais não autorizam nova raiz.

Escolher/criar o worktree antes de gerar os contratos da nova Feature, quando essa opção for solicitada. Todos os seus contratos, contexto e evidências são relativos ao mesmo checkout ativo. `contract_root = execution_root = checkout_root`. O workspace continua identidade lógica do CompozyOS; não precisa ser ancestral físico do worktree registrado.

Caso já existam contratos no checkout original:
1. Apresentar a mudança de raiz, base Git, arquivos e digests exatos para autorização.
2. Criar/adotar worktree sem copiar segredos ou alterações desconhecidas.
3. Transferir somente o bundle/contexto autorizados, preservando bytes e recibos e verificando digests; não exigir commit automático.
4. Registrar no runtime uma única vinculação ativa da Feature ao destino. Fonte preservada passa a histórica/inativa, não outra Feature executável.
5. Revalidar contexto/revisão e aprovações; mudança de conteúdo ou contexto material exige novo gate. Sem vinculação única segura, bloquear a transferência.

Essa é uma proposta técnica a qualificar, não migração genérica de estado legado. Testar bundle não commitado, divergência de cópias, retomada, worktree ausente e duas tentativas concorrentes. O executor nunca procura silenciosamente contratos na raiz original.

Caminhos relativos passam a resolver no checkout validado. ArtifactRef rejeita caminhos absolutos, traversal, symlinks e arquivos não regulares. Índices e status sempre carregam a identidade de checkout; bundles homônimos não são mesclados.

### Layout do consumidor

```text
<checkout_root>/
├── tasks/index.md
├── tasks/prd-<slug>/
│   ├── index.md
│   ├── prd.md
│   ├── stories.md
│   ├── techspec.md
│   ├── tasks.md
│   ├── task-001.md
│   ├── quick-contract.md
│   ├── quick-report.md
│   ├── environment.md
│   ├── approvals/<decision-id>.md
│   ├── evidences/<TASK-ID>/<attempt-id>/
│   │   ├── qa.md
│   │   ├── codereview.md
│   │   ├── verdict.md
│   │   ├── manifest.json
│   │   └── evidence-report.md
│   ├── evidences/feature/<attempt-id>/
│   ├── exports/<export-id>/evidence-report.html
│   ├── exports/<export-id>/evidence-report.pdf
│   └── roadmap/
└── .planning/sdd-composy/
    ├── config.json
    └── context/{project,stack,domain,pitfalls}.md + codebase.json
```

Gerar somente arquivos aplicáveis. Roadmap fica no bundle de produto; quick-report somente QUICK; environment.md contém plano humano sem segredos. Compose específico fica em `tasks/prd-<slug>/environment/compose.override.yaml`; usar base aprovada da aplicação e não carregar .env implicitamente. Se o projeto depende de segredos, solicitar mecanismo externo/sanitizado compatível com a governança, sem ler valores.

Relatórios por tentativa conservam nomes dos templates e evitam sobrescrita entre tarefas. O manifest.json de cada tentativa mantém paths relativos à raiz `evidences/`, como na fonte. Bundle index referencia tentativas e agregação, sem duplicar estado editável. A agregação de Feature usa índice de manifestos, não task_id falso que viole o schema de tarefa.

## 5. Contratos compartilhados

Os schemas propostos em S/schemas/native-contracts.schema.json concretizam os tipos abaixo. S = skills/sdd-flow-contracts. Inputs e outputs dos nós são comparados aos schemas; enums de domínio não são convertidos em terminais nativos.

| Tipo | Campos e invariantes |
|---|---|
| CheckoutRef | workspace_id: string; worktree_id: string ou null; checkout_root: caminho absoluto resolvido pelo runtime; revision_ref: string com identidade de HEAD e alterações locais relevantes |
| ArtifactRef | checkout_ref: CheckoutRef; path: relativo ao checkout; sha256: 64 caracteres hex minúsculos; role: contract, evidence, verdict, report ou manifest |
| ApprovalRef | run_id, gate_id, decision_id, actor_ref: strings opacas/ator real; decision: approved, changes_requested ou rejected; decided_at: RFC3339 UTC; artifacts: ArtifactRef[] não vazio; prerequisites: decision_id[] |
| CapabilityResult | name; status: available, missing, incompatible ou unverified; version: string ou null; checked_at; evidence_ref: ArtifactRef ou null; recommendation; affected_operations: string[] |
| StageInput | checkout_ref; bundle_path; stage; language: pt-BR ou en-US; actor_id; context_refs: ArtifactRef[]; approval_refs: ApprovalRef[]; allowed_paths: string[]; environment_ref: EnvironmentRef ou null; participation_ref: ParticipationRef |
| StageResult | outcome; transition; reason; next_action; artifact_refs: ArtifactRef[]; command_results: CommandResult[]; blockers: string[] |
| CommandResult | command; cwd relativo ao checkout; started_at; ended_at; exit_code: inteiro ou null; result: PASS, FAIL, ENVIRONMENT_FAILURE ou NOT_RUN; evidence_refs: ArtifactRef[]; revision_ref |
| EnvironmentPlan | checkout_ref; bundle_path; mode: current, worktree ou worktree_docker; base_ref; compose_files: ArtifactRef[]; compose_project; engine_identity; context_name; serviços/imagens/mounts/volumes/limites explícitos; port_policy; cleanup_policy; approval_refs |
| EnvironmentRef | plan_ref: ArtifactRef; checkout_ref; runtime_record_id; engine_identity; context_name; compose_project; owned_resource_ids: string[]; endpoints: lista service/host/port/url; ownership: environment_owned, environment_shared ou environment_unknown; health; observed_at |
| ParticipationRef | mode: local ou live; root_execution_id; snapshot_id: string ou null; approved_execution_refs: string[]; participant_refs: string[]; channel_ref: string ou null; bounds: limites finitos qualificados; approval_ref: ApprovalRef ou null |
| Handoff | StageInput mais origin_type: standalone ou roadmap; roadmap_ref: ArtifactRef ou null; mode: task ou feature; task_id: TASK-NNN em task e null em feature; evidence_manifest_refs: ArtifactRef[]; run_id |
| DeliveryResult | checkout_ref; bundle_path; mode; task_id; task_verified: boolean; feature_verified: boolean; artifact_refs; approval_refs; environment_ref; participation_ref; export_results: ExportResult[]; eligible_next_tasks: string[]; blockers; next_action |
| ExportResult | export_id; format: html ou pdf; status: generated, failed, unavailable ou not_requested; source_manifest_refs: ArtifactRef[]; output_ref: ArtifactRef ou null; renderer/version; produced_at; verification_ref: ArtifactRef ou null; reason |
| StatusResult | schema: sdd-flow.status/v1; read_only: true; checkout_ref; bundle_path; status; next_action; reasons; sources; confidence por fonte; task_summary; last_verified_gate; pending_approvals; divergences; capabilities: CapabilityResult[]; environment_ref; participation_ref; export_results |

Campos desconhecidos ficam null/unverified, nunca lista vazia interpretada como sucesso. Lista vazia significa consulta concluída sem itens. StatusResult preserva a semântica de fonte/confiança do sdd-status, mas usa schema nativo explícito, sem fingir o JSON legado.

Approvals precisam de identidade humana comprovada pelo runtime. Preservar snapshot do documento apresentado ao gate; registrar separadamente o digest da versão com os metadados de aprovação adicionados. A única alteração automática permitida nesse fechamento é o bloco de aprovação derivado da decisão real, com verificação do restante dos bytes. Revalidar digest da versão final nos gates seguintes. Isso evita invalidar a própria aprovação ao atualizar frontmatter ou permitir edição de conteúdo sob pretexto de registrar aceite.

IDs usados em filenames são codificados de forma segura e reversível; não usar IDs opacos diretamente como caminhos. Evidências permanecem imutáveis; revisão cria nova tentativa, não reescreve prova anterior.

EnvironmentPlan/EnvironmentRef exigem campos Docker somente em worktree_docker; nos demais modos eles são null/not_applicable. ParticipationRef local não exige canal nem consentimento Live. Nenhum input de checkout substitui a validação de registro e propriedade pelo runtime.

### Manifesto de evidência: conservar o schema real

Empacotar `evidence-manifest.schema.json` fonte sem alterar. Preservar schema_version "1", prd_slug, task_id, generated_at, entries; cada entrada mantém requirement_id, story_id, scenario_id, criterion_id, test_id, result, evidence_type, path, sha256.

Enums reais:
- result: passed, failed, not_applicable.
- evidence_type: test_output, screenshot, log, report.
- Verdict por claim: PASS, FAIL, STALE, ENVIRONMENT_FAILURE, NOT_RUN.
- Estado de tarefa complete e verdict final COMPLETE são distintos.

Não inserir BLOCKED/NOT_RUN no result do manifesto-fonte. Ausência de execução é registrada em CommandResult/QA/verdict e impede aceite; não inventar entrada passed. Corrigir a proposta anterior que confundia esses vocabulários.

O schema-fonte exige US/SC mesmo quando o workflow permite Stories NOT_APPLICABLE e QUICK reduzido. Não inventar IDs para satisfazê-lo: `evidence-native.schema.json` terá identidade própria, conservará a entrada original quando Stories forem REQUIRED e permitirá story_id/scenario_id nulos somente com dispensa de Stories aprovada ou contrato QUICK aprovado, vinculados no envelope. Requirement/criterion/test reais continuam obrigatórios; QUICK atribui RF/CA locais ao objetivo no contrato reduzido. Essa diferença deve passar por gate técnico e testes; sem isso esses casos não avançam.

## 6. Recursos opcionais e limites operacionais

### INIT e ambiente

INIT é o único ponto que pergunta idioma; persiste pt-BR/en-US e actor_id validado. Downstream sem init retorna not_initialized/run_init; não pergunta idioma novamente.

Descobrir Git/worktree nativo, Docker/Compose/engine, playwright-cli/browser, Live e renderizador HTML/PDF por consultas não mutáveis. Registrar CapabilityResult e recomendações curtas. Não abrir browser, iniciar Docker, copiar segredos ou instalar algo durante inspeção. Preflight posterior confirma capacidade ao usá-la. Sem opcionais, planejamento e trabalho independente continuam; contrato exigindo teste/exportação ausente permanece pendente, sem PASS fictício.

Resource-only não elimina a necessidade de qualificar ferramentas do host. M01 distingue garantias centrais obrigatórias para distribuir a extensão de dependências opcionais no consumidor. Não bloquear INIT por Docker/Live ausentes.

### Docker/worktree

Usar engine local explicitamente identificado no preview; contexto remoto exige mudança arquitetural aprovada e está fora desta v1. Revalidar identidade antes de cada mutação e retomada, sem ler credenciais. Troca de contexto invalida o apply.

Projeto Compose exclusivo por ambiente; nomes, hashes dos arquivos, containers, redes e volumes registrados. Não usar container_name fixo, volumes externos ou bind mounts compartilhados sem aprovação explícita. Montagens permanecem nos caminhos aprovados; proibir modo privileged, Docker socket no container, host network e mounts amplos do host no perfil padrão.

Publicar apenas serviços necessários ao host em 127.0.0.1; atribuição dinâmica preferida. Descobrir portas reais após bind, testar health e só então fornecer endpoints. Porta fixa requer pedido e diagnóstico de colisão; nunca derrubar outro serviço para liberar porta. Endereço não loopback requer aprovação específica.

Ambiente pertence à Feature e pode ser compartilhado por suas tarefas sequenciais sob contrato explícito; serviços pontuais pertencentes à tarefa são limpos ao fim dela. Estado environment_unknown bloqueia uso. Não encerrar o Compose da Feature entre EXECUTE e QA. Ao final oferecer limpeza de recursos próprios; código/branches/volumes preservados por padrão. Remoção e merge são decisões separadas.

### Network Live

Local é o default explícito dos quatro Loops, inclusive quando o workspace tem outro default. Network não é transportador de estado SDD.

Live é autorizado antes da criação da execução e vinculado a ParticipationRef: execução raiz, participantes, canais e limites. QUICK pode abranger seu Delivery filho somente se o consentimento nomear esse conjunto. Correções/retomada dentro da mesma execução reutilizam o snapshot autorizado; nova Run, tarefa seguinte e agregação de Feature exigem opção própria. Child não amplia limites nem inclui novos peers silenciosamente. Se o runtime não permitir comprovar esse escopo, manter a capacidade indisponível.

Mensagens são dados não confiáveis e não aprovam gates. Live não concede escrita nem paralelismo. Observer permanece Local e sem ferramentas de mensagem. Testar ausência de participação em Local, filho não autorizado, reinício e limites esgotados. A documentação atual limita Live a um daemon; não projetar rede multi-host.

### QA, playwright-cli e exportação

Preservar todo o template QA, inclusive cobertura, testes unitários/integrados/E2E, acessibilidade, responsividade, ambiente e regressão. N/A requer aplicabilidade justificada; ausência de ferramenta para teste exigido não é N/A.

playwright-cli é opção para exploração e captura, não substitui runner de regressão existente. Sessões efêmeras específicas por papel; não adotar perfil pessoal ou encerrar sessões alheias. Snapshots e screenshots não bastam sem assertion esperado/observado. Testar sanitização de traces antes de publicar; não coletar cookies, auth storage, headers ou dumps sensíveis. O help local 0.1.14 observado anteriormente não prova browser/PDF funcional.

EVIDENCE publica manifesto da tentativa para REVIEW. REVIEW e VERIFY acrescentam seus próprios arquivos, sem modificar evidência anterior. Depois de VERIFY, Evidence monta novo snapshot consolidado de manifestos e relatórios e gera os formatos contratados. O verificador confere apenas a integridade/completude dessa embalagem final; não reexecuta toda a cadeia por exportação. Qualquer mudança de código ou resultado reabre os gates afetados.

Aprovação final vincula claims verificados, snapshot e exportações solicitadas. O relatório anterior ao aceite é rotulado como aguardando aprovação; o recibo final fica separado, sem reescrever o PDF aprovado nem criar dependência circular. Não declarar aprovação no próprio relatório antes da decisão real.

Renderizar HTML escapado a partir de manifesto válido; PDF deriva desse HTML e requer backend qualificado, imagens/fontes carregadas, inspeção visual e hash. Bloquear fetch externo e scripts ativos não autorizados. Saídas ficam sob exports/<export-id>/; nenhuma saída se inclui no próprio manifesto de entrada. Falha de PDF solicitado não afeta a veracidade dos testes, mas impede declarar a exportação/entrega contratada completa. Não publicar externamente.

### Status e retomada

Observer lê documentos e consultas restritas do runtime para Feature/tarefa/gates, worktree, ambiente registrado, participação e exportações. Não recebe Docker shell; saúde não consultável por ferramenta restrita fica unverified com timestamp da última observação, não “saudável”.

Status distingue falta de opcional, teste pendente, bloqueio real e divergência. Mostra próximo passo permitido sem instalá-lo/executá-lo. Não cria Run, muda state, participa de Live, abre browser nem persiste cache próprio. Telemetria da consulta é distinta de mutação SDD.
