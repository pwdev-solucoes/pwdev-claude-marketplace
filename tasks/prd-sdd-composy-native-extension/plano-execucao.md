---
type: EXECUTION_PLAN
okf_version: "0.2"
generated:
  by: agent:codex
  at: "2026-09-11T00:00:00-03:00"
lifecycle:
  status: APPROVED
human_approval: APPROVED
updated_at: "2026-09-12T09:41:18Z"
plan_approval:
  status: APPROVED
  scope: "Plano consolidado da v1 nativa, com 12 módulos e 35 tarefas"
  source: "user: aprovado"
worktree_environment_approval:
  status: APPROVED
  scope: "Worktree nativo opcional por Feature, com Docker Compose isolado, portas próprias e limpeza controlada"
  source: "user: aprovado, após proposta de worktree com Docker Compose"
network_participation_approval:
  status: APPROVED
  scope: "Live opcional; Local como padrão; ativação explícita por execução"
  source: "user: live opcional"
optional_capabilities_approval:
  status: APPROVED
  scope: "INIT detecta recursos opcionais, recomenda instalação/configuração e permite continuar sem eles; sem instalação automática nem aprovação de testes não executados"
  source: "user: aprovado"
scope_change:
  source: "user: quero que entre provisionamento Docker, Compozy Network Live, exportação HTML/PDF de evidência"
  design_status: APPROVED
direction_approval:
  scope: "sdd-composy principal; pwdev-flow auxiliar; refazer o plano"
  source: "user: Aprovado, refazer o plano"
language: pt-BR
sources:
  - resource: plugins/sdd-composy/README.md
  - resource: plugins/sdd-composy/references/quick.md
  - resource: plugins/sdd-composy/references/evidence.md
  - resource: plugins/sdd-composy/skills/
  - resource: plugins/sdd-composy/templates/
  - resource: plugins/sdd-composy/schemas/evidence-manifest.schema.json
  - resource: plugins/sdd-composy/references/language.md
  - resource: plugins/sdd-composy/references/states.md
  - resource: plugins/pwdev-flow/references/collaboration.md
  - resource: plugins/pwdev-flow/references/execution.md
  - resource: plugins/pwdev-code/agents/roadmap.md
  - resource: https://www.compozy.com/docs/extensions/develop/
  - resource: https://www.compozy.com/docs/loops/dsl-reference/
  - resource: https://www.compozy.com/docs/network/
  - resource: https://www.compozy.com/docs/network/protocol/implementation-status/
  - resource: https://www.compozy.com/docs/worktrees/loop-environments/
  - resource: https://docs.docker.com/compose/how-tos/project-name/
verified:
  - event: human_approval
    by: human:user
    at: "2026-09-12T09:41:18Z"
    scope: consolidated_v1_native_execution_plan
    source: "user: aprovado"
  - event: human_approval
    by: human:user
    at: "2026-09-12T09:09:46Z"
    scope: optional_worktree_docker_environment
    source: "user: aprovado, após proposta de worktree com Docker Compose"
  - event: human_approval
    by: human:user
    at: "2026-09-12T09:02:31Z"
    scope: optional_live_participation
    source: "user: live opcional"
  - event: human_approval
    by: human:user
    at: "2026-09-12T08:59:30Z"
    scope: optional_capabilities_policy
    source: "user: aprovado"
  - event: source_review
    by: agent:codex
    at: "2026-09-11T00:00:00-03:00"
---


# pwdev-composyOs — plano consolidado da v1 nativa

Status: APPROVED pelo usuário em 2026-09-12. A aprovação abrange o plano consolidado e sua decomposição; não aprova antecipadamente os futuros PRD, Stories, TechSpec, contratos TASK-*, operações de provisionamento ou conclusão. Este documento substitui o desenho anterior e seus adendos. A extensão ainda não foi implementada.

## Objetivo e decisões preservadas

Distribuir uma extensão CompozyOS somente de recursos, fiel ao método, às skills e aos templates de `plugins/sdd-composy/`. Adaptar a integração com o runtime, não simplificar os gates ou inventar evidência.

- Nome: `pwdev-composyOs`. Raiz proposta: `plugins/pwdev-composyOs/`.
- `sdd-composy` é a referência principal. Flow auxilia somente no brief autocontido e relato de bloqueios; pwdev-code auxilia somente no roadmap.
- Roadmap opcional; Feature independente e QUICK funcionam sem ele.
- Docker opcional, apenas para aplicação e dependências de teste; agentes e daemon ficam no host.
- Ambiente padrão: checkout atual. Opções: checkout atual, worktree nativo ou worktree nativo com Docker Compose.
- Um worktree por Feature, reutilizado nas tarefas e correções, sem Fleet ou merge automático.
- Network Local por padrão; Live opcional por consentimento explícito.
- INIT detecta capacidades e recomenda instalação/configuração, mas não instala, baixa, ativa Live ou provisiona automaticamente.
- playwright-cli opcional; testes e exportações exigidos não viram PASS quando a ferramenta está ausente.
- HTML e PDF fazem parte das capacidades da v1; uso em cada entrega é declarado no contrato.
- Status mínimo faz parte do produto e é exclusivamente leitura.

A consolidação usa `power-plan` apenas para dimensionar trabalho. Não importa o estado Power nem seu limite de correções. A governança deste repositório prevalece.

## 1. Política de fidelidade ao SDD

### Regras de portabilidade

Cada skill nativa deriva da skill SDD correspondente, conservando inputs, procedimento, outputs, condições de parada e referências. Manter nomes de arquivos de templates, tipos OKF, seções e tabelas; não substituir os onze templates por dois documentos genéricos.

A adaptação remove chamadas a helpers não empacotados, variáveis como CLAUDE_PLUGIN_ROOT e descoberta de providers de outros runtimes. Uma chamada removida precisa de uma capacidade nativa comprovada que cumpra sua garantia; texto em prompt não substitui validação, confinamento, exclusão mútua ou atomicidade.

`provenance.md` registra por recurso: fonte exata, revisão/digest, cláusulas preservadas, diferenças, motivo e testes. Ajustes técnicos novos desta consolidação permanecem sujeitos ao gate de TechSpec. Não modificar `plugins/sdd-composy/` nesta entrega.

### Mapeamento das 17 skills-fonte

| Fonte SDD | Destino | Fidelidade e ajuste delimitado |
|---|---|---|
| sdd-init | sdd-native-init | Idioma/actor, preview, criação apenas de ausências, diagnóstico e verificação; perfil nativo e descoberta opcional |
| sdd-map | sdd-native-map | Observação, exclusão de segredos, commit e staleness; mecanismo de publicação nativo qualificado |
| sdd-prd | sdd-native-prd | Problema, objetivos, RF/CA e aprovação; não decide arquitetura |
| sdd-stories | sdd-native-stories | Actors/Journeys/US/SC, dependências, edge cases e gate de aplicabilidade |
| sdd-techspec | sdd-native-techspec | Inventário, interfaces, decisões/riscos, testes e gate |
| sdd-tasks | sdd-native-tasks | TASK-NNN, dependências, allowlist e comandos; projeção operacional adaptada explicitamente |
| sdd-execute | sdd-native-execute | Uma tarefa ready, TDD real, escopo, ownership/cleanup, resultado e próxima transição |
| sdd-qa | sdd-native-qa | Cobertura CA/SC, testes, browser quando aplicável, acessibilidade, regressão e gate humano |
| sdd-evidence | sdd-native-evidence | Inventário, manifesto criterion-linked, tipos/resultados reais e hashes; exportação em procedimento separado |
| sdd-review | sdd-native-review | Diff explícito, achados/rule citations, comandos, conformidade e gate humano; sem silent fix |
| sdd-verify | sdd-native-verify | Truth table, comandos frescos, ator independente e parecer; aprovação humana de conclusão |
| sdd-quick | sdd-native-quick | Q-* mais tarefa normal, cinco arquivos, TDD e cadeia de qualidade completa |
| sdd-status | sdd-native-status | Consulta conservadora, confiança por fonte, divergências e próxima ação; extensões de ambiente/capacidades |
| sdd-loop | sdd-native-delivery.yaml | Motor nativo coordena as etapas SDD; sem skill com motor concorrente |
| sdd-trace | evidence/status e histórico nativo qualificado | Preservar rastreabilidade e sucesso antes do evento; record/build/projeção legada não são portados |
| sdd-sync | Não distribuída na v1 | Diagnóstico permanece; sem apply ou migração automática |
| sdd-fleet | Não distribuída na v1 | Sem runner Fleet; worktree nativo opcional continua incluído |

### Templates individuais e diferenças permitidas

Os onze arquivos abaixo permanecem em `skills/sdd-native-contracts/templates/`, com os mesmos nomes da fonte.

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

| Agente sdd-native-* | Skills sdd-native-* | Limite |
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

A 20ª skill é `sdd-native-contracts`, biblioteca compartilhada de referências, schemas e templates, sem operação mutável própria. Cada agente tem AGENT.md; cada skill tem SKILL.md. Loops publicados: product, feature, quick e delivery, todos com prefixo sdd-native- e extensão .yaml.

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

Os schemas propostos em S/schemas/native-contracts.schema.json concretizam os tipos abaixo. S = skills/sdd-native-contracts. Inputs e outputs dos nós são comparados aos schemas; enums de domínio não são convertidos em terminais nativos.

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
| StatusResult | schema: pwdev-composyos.status/v1; read_only: true; checkout_ref; bundle_path; status; next_action; reasons; sources; confidence por fonte; task_summary; last_verified_gate; pending_approvals; divergences; capabilities: CapabilityResult[]; environment_ref; participation_ref; export_results |

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

## 7. Estrutura de implementação e módulos

A ampliação substitui a decomposição antiga: são **12 módulos**, cada um com até oito tarefas e cada tarefa com até cinco arquivos, incluindo testes. IDs Mxx.yy são identificadores deste mapa de implementação; os contratos TASK-NNN reais serão gerados e aprovados em cada pacote, sem renumerar contratos já aprovados.

Abreviações: E = plugins/pwdev-composyOs; S = E/skills/sdd-native-contracts; C = tasks/prd-sdd-composy-native-extension; T = tests. Todos os arquivos E são futuros. Não alterar fontes SDD, Flow ou pwdev-code.

Cada linha abaixo é uma tarefa e declara seus arquivos exatos; os caminhos também constituem o inventário completo de implementação. Templates/referências espelhados conservam um arquivo por fonte. Testes novos usam o unittest existente. Fixtures não são distribuídas.

Protocolo por tarefa (cinco passos):
1. Ler inputs aprovados e critérios vinculados; parar em conflito ou escopo desconhecido.
2. Para recurso/teste, escrever e executar teste de comportamento ausente antes de implementá-lo; para contrato humano, validar estrutura e pedir seu gate antes de gerar downstream.
3. Produzir apenas os arquivos declarados, preservando fonte e registrando diferenças.
4. Executar comando focado do módulo, conferir resultados e realizar os ensaios reais autorizados quando aplicáveis.
5. Revisar diff/links/outputs e apresentar evidência; não commit, merge, install ou publish automaticamente.

Os comandos da futura extensão só serão executados após criação dos recursos; unittest com zero testes não é aprovação. Exemplos em templates são dados de autoria, nunca comandos a executar sem contrato. A ordem dos módulos é sequencial; independência de arquivos não autoriza paralelismo.


### M01 — Contratos e qualificação do runtime

Complexidade: alta. Dependência: direção aprovada; ensaio mutável depende de seu escopo específico.
Consome: Decisões do usuário, templates e referências SDD.
Produz: PRD/Stories/TechSpec e escopo de ensaio aprovados; matriz de capacidades com comandos reais.

| Tarefa | Entrega | Arquivos exatos |
|---|---|---|
| M01.1 | Produto e Stories | `C/prd.md`; `C/stories.md` |
| M01.2 | Arquitetura e ensaio | `C/techspec.md`; `C/tasks.md`; `C/compatibilidade.md` |
| M01.3 | Probe isolado | `T/test_sdd_composy_native_m01_compatibility.py`; `T/fixtures/sdd_composy_native/extension.toml`; `T/fixtures/sdd_composy_native/agents/probe/AGENT.md`; `T/fixtures/sdd_composy_native/loops/probe.yaml`; `T/fixtures/sdd_composy_native/cases.json` |
| M01.4 | Reconciliar observações | `C/compatibilidade.md`; `C/techspec.md`; `C/tasks.md` |

Verificação focada: `python3 -m unittest discover -s tests -p 'test_sdd_composy_native_m01_*.py'`.

Aceite: Identificar versão real e sintaxe suportada sem instalar. Provar gates humanos vinculados a bytes, schemas, carregamento de skills, atomicidade, histórico/retomada, confinamento, read-only e exclusão mútua. Qualificar capacidades de worktree, Docker, Live e exportação em ambiente autorizado. Matriz inclui teste positivo, negativo, esperado/observado, comando, resultado e referências reais. Help/build não comprovam comportamento. Falha central impede módulo dependente; opcional ausente no consumidor não bloqueia INIT. A adaptação de Stories N/A/QUICK e o perfil nativo precisam de aceite técnico explícito.

### M02 — Referências, schemas e manifesto

Complexidade: alta. Dependência: M01 aceito.
Consome: M01 aprovado e fontes SDD fixadas por revisão/digest.
Produz: Contratos da seção 5, biblioteca de referências e manifesto resource-only.

| Tarefa | Entrega | Arquivos exatos |
|---|---|---|
| M02.1 | Referências 1 | `T/test_sdd_composy_native_m02_references.py`; `S/references/artifacts.md`; `S/references/evidence.md`; `S/references/execution.md`; `S/references/language.md` |
| M02.2 | Referências 2 | `T/test_sdd_composy_native_m02_references.py`; `S/references/loop.md`; `S/references/mapping.md`; `S/references/okf.md`; `S/references/product.md` |
| M02.3 | Referências 3 | `T/test_sdd_composy_native_m02_references.py`; `S/references/quality.md`; `S/references/quick.md`; `S/references/safety.md`; `S/references/specification.md` |
| M02.4 | Referências 4 | `T/test_sdd_composy_native_m02_references.py`; `S/references/states.md`; `S/references/status.md`; `S/references/stories.md`; `S/references/tasks.md` |
| M02.5 | Referências 5 | `T/test_sdd_composy_native_m02_references.py`; `S/references/trace.md`; `S/references/verification.md`; `S/references/workflow.md`; `S/references/runtime-native.md` |
| M02.6 | Referências 6 | `T/test_sdd_composy_native_m02_references.py`; `S/references/environment.md`; `S/references/network.md`; `S/references/exports.md`; `S/references/provenance.md` |
| M02.7 | Schemas e biblioteca | `T/test_sdd_composy_native_m02_contracts.py`; `S/SKILL.md`; `S/schemas/evidence-manifest.schema.json`; `S/schemas/evidence-native.schema.json`; `S/schemas/native-contracts.schema.json` |
| M02.8 | Manifesto | `T/test_sdd_composy_native_m02_extension.py`; `E/extension.toml` |

Verificação focada: `python3 -m unittest discover -s tests -p 'test_sdd_composy_native_m02_*.py'`.

Aceite: Comparar referências cláusula a cláusula, preservar regras SDD e isolar diferenças em runtime-native/provenance. Schema base de evidência idêntico à fonte; schema nativo separado para exceções aprovadas. Testar enums, links RF/CA/US/SC/TEST, campos desconhecidos, limites de caminho e decisão ligada a digest. Manifesto lista árvores estáticas; cardinalidade final é conferida em M12.

### M03 — Templates fiéis e complementos mínimos

Complexidade: média. Dependência: M02 aceito.
Consome: M02 e os onze templates SDD lidos individualmente.
Produz: Templates individuais preservados e modelos auxiliares isolados.

| Tarefa | Entrega | Arquivos exatos |
|---|---|---|
| M03.1 | Templates SDD 1 | `T/test_sdd_composy_native_m03_templates.py`; `S/templates/prd.md`; `S/templates/stories.md`; `S/templates/techspec.md`; `S/templates/tasks.md` |
| M03.2 | Templates SDD 2 | `T/test_sdd_composy_native_m03_templates.py`; `S/templates/task.md`; `S/templates/quick-contract.md`; `S/templates/quick-report.md`; `S/templates/qa.md` |
| M03.3 | Templates SDD 3 | `T/test_sdd_composy_native_m03_templates.py`; `S/templates/codereview.md`; `S/templates/evidence-report.md`; `S/templates/verdict.md` |
| M03.4 | Complementos nativos | `T/test_sdd_composy_native_m03_native_templates.py`; `S/templates/roadmap.md`; `S/templates/environment.md`; `S/templates/approval-receipt.md`; `S/templates/export-receipt.md` |

Verificação focada: `python3 -m unittest discover -s tests -p 'test_sdd_composy_native_m03_*.py'`.

Aceite: Testar tipo OKF, campos, headings/tabelas e cláusulas de gates de cada template contra fonte. Diferença exige entrada em provenance. Exemplos são renderizados com links reais; PRD CA não aponta para Stories por erro de exemplo. Evidência/report ganha metadados ausentes. Não misturar placeholders de template com documentos finais incompletos.

### M04 — INIT, intake e MAP

Complexidade: média. Dependência: M03 aceito.
Consome: M02/M03 e escolha de checkout.
Produz: CapabilityResult[] e StageResult de preparação/contexto.

| Tarefa | Entrega | Arquivos exatos |
|---|---|---|
| M04.1 | Entrada e capacidades | `T/test_sdd_composy_native_m04_init.py`; `E/agents/sdd-native-coordinator/AGENT.md`; `E/skills/sdd-native-intake/SKILL.md`; `E/skills/sdd-native-init/SKILL.md` |
| M04.2 | Observação MAP | `T/test_sdd_composy_native_m04_map.py`; `E/skills/sdd-native-map/SKILL.md` |

Verificação focada: `python3 -m unittest discover -s tests -p 'test_sdd_composy_native_m04_*.py'`.

Aceite: Idioma só em INIT; not_initialized/run_init em downstream. INIT sem opcionais termina com recomendações, não instalações. Testar configuração inválida, legado, conflito, actor, publicação só de ausências e preservação de governança. MAP observa revisão, não arquitetura; não executa comandos descobertos. Saídas capabilities podem ser resultados do turno, sem criar cache operacional paralelo.

### M05 — Produto, Stories, roadmap e promoção

Complexidade: média. Dependência: M04 aceito.
Consome: StageInput, contexto e problema do usuário.
Produz: StageResult de PRD/Stories/roadmap e origem da Feature promovida.

| Tarefa | Entrega | Arquivos exatos |
|---|---|---|
| M05.1 | PRD e Stories | `T/test_sdd_composy_native_m05_product.py`; `E/agents/sdd-native-product/AGENT.md`; `E/skills/sdd-native-prd/SKILL.md`; `E/skills/sdd-native-stories/SKILL.md` |
| M05.2 | Roadmap e promoção | `T/test_sdd_composy_native_m05_roadmap.py`; `E/skills/sdd-native-roadmap/SKILL.md`; `E/skills/sdd-native-promote/SKILL.md`; `E/loops/sdd-native-product.yaml` |

Verificação focada: `python3 -m unittest discover -s tests -p 'test_sdd_composy_native_m05_*.py'`.

Aceite: Gates separados de PRD/Stories. Roadmap termina em Feature, com ROADMAP, TRACEABILITY, RISKS, METRICS, ROLLOUT e VALIDATION; até oito Features por Épico, acima de 50 recomendar módulos. Não gera TASKs. Promoção idempotente para destino exato, sem herdar aprovações do PRD de produto; usa raiz escolhida para a Feature. Feature simples não requer roadmap.

### M06 — TechSpec e contratos TASK

Complexidade: alta. Dependência: M05 aceito.
Consome: PRD e Stories/aplicabilidade aprovados, contexto fresco e StageInput.
Produz: StageResult de TechSpec e TASKS; tarefas elegíveis, sem execução.

| Tarefa | Entrega | Arquivos exatos |
|---|---|---|
| M06.1 | Especificação e tarefas | `T/test_sdd_composy_native_m06_specification.py`; `E/agents/sdd-native-architect/AGENT.md`; `E/skills/sdd-native-techspec/SKILL.md`; `E/skills/sdd-native-tasks/SKILL.md` |
| M06.2 | Loop Feature | `T/test_sdd_composy_native_m06_feature.py`; `E/loops/sdd-native-feature.yaml` |

Verificação focada: `python3 -m unittest discover -s tests -p 'test_sdd_composy_native_m06_*.py'`.

Aceite: Usar templates reais, task-001.md, RF/CA/US/SC/DEC/RISK e links de testes. States snapshots não concedem aprovação. Testar dependências desconhecidas/cíclicas, allowlist e comandos vazios, staleness e gates diretos. Stories N/A exige decisão humana, nunca preenchimento artificial. Quatro gates de produto/especificação não são um único aceite.

### M07 — Worktree nativo e Docker por Feature

Complexidade: alta. Dependência: M06 aceito.
Consome: EnvironmentPlan, CheckoutRef e decisão humana de ambiente.
Produz: EnvironmentRef validado e vinculação única ao checkout; endpoints efetivos.

| Tarefa | Entrega | Arquivos exatos |
|---|---|---|
| M07.1 | Procedimento de ambiente | `T/test_sdd_composy_native_m07_environment.py`; `E/agents/sdd-native-environment/AGENT.md`; `E/skills/sdd-native-environment/SKILL.md` |
| M07.2 | Retomada e isolamento | `T/test_sdd_composy_native_m07_worktree.py`; `E/skills/sdd-native-environment/SKILL.md`; `E/skills/sdd-native-promote/SKILL.md` |

Verificação focada: `python3 -m unittest discover -s tests -p 'test_sdd_composy_native_m07_*.py'`.

Aceite: Testar worktree criado antes de contratos e transferência explícita de bundle não commitado, comparação de bytes e uma raiz ativa. Dois ambientes não compartilham dados/portas involuntariamente. Troca de engine/contexto entre preview/apply bloqueia. Bind efetivo loopback, mounts aprovados, Compose hash correto, health e limpeza de um sem atingir o outro. Não copiar .env, montar socket, apagar volumes ou fazer merge automaticamente. Sem Docker, trabalho independente continua; escolha explícita indisponível não é substituída silenciosamente.

### M08 — Entrega SDD e gates independentes

Complexidade: alta. Dependência: M07 aceito.
Consome: Handoff com uma tarefa ready ou modo Feature e EnvironmentRef.
Produz: StageResult por etapa e DeliveryResult com artefatos/decisões frescos.

| Tarefa | Entrega | Arquivos exatos |
|---|---|---|
| M08.1 | Execute | `T/test_sdd_composy_native_m08_execute.py`; `E/agents/sdd-native-implementer/AGENT.md`; `E/skills/sdd-native-execute/SKILL.md` |
| M08.2 | QA e manifesto | `T/test_sdd_composy_native_m08_quality.py`; `E/agents/sdd-native-qa/AGENT.md`; `E/skills/sdd-native-qa/SKILL.md`; `E/skills/sdd-native-evidence/SKILL.md` |
| M08.3 | Review | `T/test_sdd_composy_native_m08_review.py`; `E/agents/sdd-native-reviewer/AGENT.md`; `E/skills/sdd-native-review/SKILL.md` |
| M08.4 | Verify | `T/test_sdd_composy_native_m08_verify.py`; `E/agents/sdd-native-verifier/AGENT.md`; `E/skills/sdd-native-verify/SKILL.md` |
| M08.5 | Loop Delivery | `T/test_sdd_composy_native_m08_delivery.py`; `E/loops/sdd-native-delivery.yaml` |

Verificação focada: `python3 -m unittest discover -s tests -p 'test_sdd_composy_native_m08_*.py'`.

Aceite: RED real antes do código; todos comandos aprovados executados; QA/review humanos separados; truth table e ambiente fresco. EvidenceRequired false somente conforme exceção full aprovada. Manter serviços da Feature até consumidores terminarem, limpar serviços task-owned. No máximo três iterações agregadas e ausência de progresso dois; rejeição não autoriza scope change. Mode Feature exige integração e gate final, não terminal done. playwright-cli é opção, sem alterar runner existente ou omitir E2E obrigatório.

### M09 — Network Live opcional e consentimento

Complexidade: alta. Dependência: M08 aceito.
Consome: ParticipationRef e escopo explícito de execução/filhos.
Produz: Snapshot nativo qualificado e handoff preservando modo/limites.

| Tarefa | Entrega | Arquivos exatos |
|---|---|---|
| M09.1 | Participação e herança | `T/test_sdd_composy_native_m09_network.py`; `E/skills/sdd-native-network/SKILL.md`; `E/agents/sdd-native-coordinator/AGENT.md`; `E/loops/sdd-native-delivery.yaml`; `S/references/network.md` |

Verificação focada: `python3 -m unittest discover -s tests -p 'test_sdd_composy_native_m09_*.py'`.

Aceite: Local explícito não herda Live de workspace. Testar Live ausente, opt-in, limites, participação de child autorizada e não autorizada, retomada sem novo consentimento fora do escopo, nova Run exigindo escolha própria. Nenhuma mensagem concede gate ou escrita. Não ativar defaults globais. Template de skill só controla participação pelos mecanismos do runtime demonstrados em M01.

### M10 — HTML/PDF e fechamento do dossier

Complexidade: alta. Dependência: M09 aceito.
Consome: Manifestos validados, QA/review/verdict e formatos contratados.
Produz: ExportResult[] e snapshot final para aprovação de entrega.

| Tarefa | Entrega | Arquivos exatos |
|---|---|---|
| M10.1 | Exportação e integração final | `T/test_sdd_composy_native_m10_exports.py`; `E/skills/sdd-native-evidence-export/SKILL.md`; `S/templates/evidence-report.html`; `E/agents/sdd-native-qa/AGENT.md`; `E/loops/sdd-native-delivery.yaml` |

Verificação focada: `python3 -m unittest discover -s tests -p 'test_sdd_composy_native_m10_*.py'`.

Aceite: Templates e escaping determinístico comprovados; renderer externo qualificado sem helper empacotado. Testar enum/path/hash inválido, fonte ausente, HTML hostil, bloqueio de fetch externo, imagens/paginação PDF e backend ausente. Snapshot inclui evidências novas de review/verify; pacote não se referencia; decisão final separada. PDF solicitado faltante impede conclusão contratada, não apaga testes válidos. Não reexecutar teste só porque o relatório foi renderizado; código/evidência alterados invalidam gates afetados.

### M11 — QUICK e status consolidado somente leitura

Complexidade: alta. Dependência: M10 aceito.
Consome: Contratos compartilhados, DeliveryResult e consultas restritas do runtime.
Produz: QUICK_CONTRACT/QUICK_REPORT e StatusResult completo.

| Tarefa | Entrega | Arquivos exatos |
|---|---|---|
| M11.1 | QUICK | `T/test_sdd_composy_native_m11_quick.py`; `E/skills/sdd-native-quick/SKILL.md`; `E/loops/sdd-native-quick.yaml` |
| M11.2 | Status | `T/test_sdd_composy_native_m11_status.py`; `E/agents/sdd-native-observer/AGENT.md`; `E/skills/sdd-native-status/SKILL.md` |

Verificação focada: `python3 -m unittest discover -s tests -p 'test_sdd_composy_native_m11_*.py'`.

Aceite: QUICK preserva Q/TASK, templates e cinco arquivos; sexto, migração ou comando desconhecido escala antes de editar. Testar raiz atual/worktree, endpoints, capacidades opcionais, modo Local/Live, exports pendentes e múltiplos bundles sem escolher silenciosamente. Observer sem Docker shell/browser/Network messages, sem Run nova. Comparar hashes e inventários antes/depois, com documentos maliciosos tentando induzir escrita; fonte não consultável fica unverified.

### M12 — Aceitação, documentação e conformidade com a fonte

Complexidade: alta. Dependência: M11 aceito.
Consome: M01–M11 aceitos e geração completa.
Produz: Evidência integrada, QA/review/verdict independentes e proposta de aceite humano final.

| Tarefa | Entrega | Arquivos exatos |
|---|---|---|
| M12.1 | Matriz final e documentação | `T/test_sdd_composy_native_m12_acceptance.py`; `E/README.md`; `C/evidence.md` |
| M12.2 | Pareceres finais | `C/qa.md`; `C/codereview.md`; `C/verdict.md` |

Verificação focada: `python3 -m unittest discover -s tests -p 'test_sdd_composy_native_m12_*.py'`.

Aceite: Conferir 9 agentes, 20 skills, 4 Loops e onze templates SDD individuais. Nenhuma referência externa ao pacote em runtime. Executar jornadas QUICK/standalone/roadmap com modo básico sem opcionais e com capacidades habilitadas. Provar gates, stale/cancel/resume, dois ambientes isolados, Live sem consentimento bloqueado, PDF incompleto e status sem efeitos. QA/review/verify e aprovação final separados. Build, unit tests e ajuda de CLI não substituem jornadas reais.

## 8. Verificação integrada e critérios de liberação

Comandos do repositório de autoria:

```sh
python3 -m unittest discover -s tests -p 'test_sdd_composy_native_*.py'
python3 -m unittest discover -s tests -p 'test_sdd_composy*.py'
compozy extension build plugins/pwdev-composyOs -o json
```

Após build, usar exatamente generation_dir retornado em `compozy extension validate`. Nunca inventar hash. M01 registra versão e comandos completos de Loop, worktree, decisões, consultas e sessões suportados pelo help da instalação efetiva; nenhum ensaio de provider será chamado com sintaxe presumida. Os comandos de teste acima seguem o unittest existente, mas os arquivos nativos ainda serão criados.

M01 deve produzir uma receita reproduzível: workspace isolado, preparação sem segredos, inputs do probe, comando real, esperado/observado, IDs de Run/gate/decision, efeitos antes/depois, cleanup e classificação. Teste não executado = NOT_RUN; falha de ambiente não é falha funcional nem PASS. Não iniciar ensaios externos enquanto a receita e o escopo mutável não estiverem aprovados.

| Critério | Módulos responsáveis | Prova |
|---|---|---|
| Fidelidade às 17 skills-fonte e exceções explícitas | M01–M03, M12 | Matriz de proveniência, onze templates separados e schemas comparados |
| Gates e máquina SDD preservados | M05, M06, M08, M11 | Aprovação humana real, rejeição, digest alterado e dependência incompleta |
| Manifesto e verdicts sem enums trocados | M02, M08, M10 | Schemas fonte/nativo, CA/RF/US/SC/TEST reais e exceções aprovadas |
| Perfil nativo sem mutação legada | M01, M04, M07 | Legado recusado; config/contexto confinados; zero sobrescrita de governança |
| Worktree com raiz de contrato inequívoca | M02, M07, M11 | Bundle não commitado transferido por escopo, digests e vínculo único; source histórica |
| Docker somente app/testes, engine correto | M07, M12 | Contexto trocado bloqueia; dois ambientes com portas/dados separados e bind loopback |
| INIT sem opcionais continua | M04, M11, M12 | Capabilities e recomendações sem install, browser, containers ou Live |
| Live opcional com consentimento delimitado | M09, M11 | Local explícito, child fora de escopo recusado e snapshot preservado |
| QA independente e playwright-cli opcional | M08, M11 | Runner do projeto preservado, browser alternativo qualificado ou teste pendente |
| HTML/PDF completos e posteriores às provas | M10, M12 | Manifestos/review/verdict incluídos, escaping, inspeção PDF e recibo final separado |
| Status útil e tecnicamente restrito | M01, M11 | Fonte/confiança e ambiente/exports; zero mutação, Run nova ou mensagens |
| Conclusão de Feature, não só de tarefa | M08, M10, M12 | Integração fresca, exportações contratadas e aceite humano final |

Módulos definem o mapa de execução, não substituem contratos individuais SDD: antes de implementação de cada pacote, gerar TASKS/task-*.md aprovados com critérios, arquivos, dependências e comandos. Sem PRD/Stories/TechSpec aprovados, não gerar uma tarefa ready. O desenho do perfil nativo e a exceção de manifesto ainda dependem de qualificação; a reescrita não declara capacidades de segurança do host como disponíveis.

## 9. Fora da v1

Fleet e seus runners, paralelismo automático, migração/sync apply do estado legado, reconstrução trace.json legada, agentes/daemon em Docker, engine Docker remoto, Network multi-daemon, hooks, MCP próprio, helpers executáveis distribuídos, publicação externa automática, merge automático, descarte automático de volumes e automações agendadas.

Worktree nativo por Feature, Docker local de aplicação/testes, Live opcional, status mínimo e HTML/PDF estão dentro da v1. Não remover uma capacidade do produto porque falta um pré-requisito em um consumidor; reportar indisponibilidade e manter o modo básico. Não confundir essa disponibilidade opcional com dispensa de um critério obrigatório de aceite.

## 10. Registro da consolidação

Esta versão elimina os adendos concorrentes e a cardinalidade antiga. O plano consolidado foi aprovado pelo usuário, preservando gates independentes para cada contrato e operação futura. A extensão-alvo passa a ter nove agentes, vinte skills, quatro Loops e onze templates SDD individuais mais complementos explícitos; os doze módulos totalizam 35 tarefas de implementação.

Correções centrais: contratos/checkout alinhados; engine e bind explícitos; consentimento Live tipado; status expandido; exportação após evidência final; nomes e enums fiéis aos templates/schemas; distinção de helpers determinísticos e recursos nativos.

Fontes principais: skills, templates, schemas e referências locais do SDD Composy. O [formato resource-only](https://www.compozy.com/docs/extensions/develop/) e a [seleção nativa de ambiente dos Loops](https://www.compozy.com/docs/worktrees/loop-environments/) fundamentam a embalagem e a integração; não comprovam por si só enforcement, atomicidade ou execução real. Essas provas pertencem a M01 e à aceitação integrada.

Só este plano foi reescrito. Nenhum recurso da extensão, container, worktree, instalação, conexão Live ou estado operacional foi criado por esta consolidação.
