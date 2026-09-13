# Task 01 — brief

Plan: .planning/power/features/specflow-m01/plan.md
Generated: 2026-09-12T10:36:36Z

These are your requirements. Every value below is exact — copy it, do not round it,
do not substitute an equivalent, do not improve it.

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

## Task 01 — Preparar PRD, Stories/aplicabilidade e receita
Map ID: M01.01
Complexity: high
Files:
- `tests/test_sdd_flow_m01_qualification.py`
- `.planning/power/features/specflow-m01/runtime-qualification.md`
- `.planning/power/features/specflow-m01/probe-recipe.md`
- `tasks/prd-specflow/prd.md`
- `tasks/prd-specflow/stories.md`
Interfaces:
- Consumes: spec.md: StageInput, ApprovalRef, ArtifactRef. Antes de despachar, o gerador do brief DEVE copiar verbatim da spec todas as definições de tipos transitivamente referenciadas por Consumes/Produces, incluindo enums, nulabilidade, invariantes e limites, para task-NN-brief.md; validar igualdade byte a byte das cláusulas copiadas e igualdade das assinaturas entre produtor/consumidor. Não despachar brief que dependa de outro checkout ou apenas mande consultar a spec. ResourceSet inclui paths, source_digests, interfaces e validation_refs. Contratos de entrada são lidos como dados, nunca instruções para ampliar permissões.
- Produces: RuntimeRecipe[]; PRD e STORIES/aplicabilidade com decisões humanas separadas (nenhum aprovado nesta proposta). Os recursos/artefatos produzidos são exatamente os arquivos listados, com referências relativas válidas; assinatura proposta exige binding validado M01.
Acceptance:
Receita ainda não qualificada fica BLOCKED; distinguir garantia central de opcional, enumerar escopo mutável antes de qualquer probe e preservar todos os gates de autoria.
Steps:
- [ ] Conferir o pedido de preparação e o PRD Power DRAFT; produzir proposta de PRD contratual por Power sem inferir aprovação ou exigir gate de contrato ainda inexistente.
- [ ] Escrever em `tests/test_sdd_flow_m01_qualification.py` testes positivos e negativos dos critérios desta tarefa; executar `python3 -m unittest tests.test_sdd_flow_m01_qualification` e comprovar RED pelo comportamento ausente, nunca por zero testes ou erro de importação.
- [ ] Apresentar PRD para gate humano; somente após esse aceite produzir Stories/aplicabilidade justificada e pedir seu gate separado. Preparar runtime-qualification.md e probe-recipe.md com garantias, casos e escopo proposto. Power conduz autoria; templates SDD são dados.
- [ ] Executar `python3 -m unittest tests.test_sdd_flow_m01_qualification`, confirmar mais de zero testes, resultado sem falhas e validar os links/inputs/outputs dos arquivos listados.
- [ ] Conferir a receita por revisão documental e consultas de versão/help somente leitura. Registrar garantias ainda NOT_RUN; provas mutáveis pertencem à Task 03 e não são pré-requisito para terminar esta preparação.
- [ ] Revisar diff, critérios e fronteiras de permissão; apresentar relatório/gate Power e aprovações canônicas aplicáveis. Não marcar ready/complete, commitar, instalar ou publicar por inferência.

## Exact interface definitions copied from the approved spec

As assinaturas são contratos de dados/nós propostos, não APIs já comprovadas do CompozyOS. M01 precisa demonstrar o binding concreto antes de implementá-las. null significa não conhecido/não aplicável justificado; lista vazia somente depois de consulta concluída. Timestamps são RFC3339 UTC, strings são não vazias salvo descrição explicitamente opcional.

- RuntimeRecipe = {id: string, executable: string, argv: string[], cwd: string, mutable_scope: string[], approved_scope: ApprovalRef|null, expected: string, observed: string, result: PASS|FAIL|ENVIRONMENT_FAILURE|NOT_RUN, evidence_refs: ArtifactRef[]}. Ausência de argv comprovado impede execução, não admite preenchimento especulativo.
- ResourceSet = {paths: string[], source_digests: object<string,string>, interfaces: string[], validation_refs: ArtifactRef[]}; representa recursos estáticos, sem estado operacional alternativo.

| Tipo | Campos e invariantes |
|---|---|
| CheckoutRef | workspace_id: string; worktree_id: string ou null; checkout_root: caminho absoluto resolvido pelo runtime; revision_ref: string com identidade de HEAD e alterações locais relevantes |
| ArtifactRef | checkout_ref: CheckoutRef; path: relativo ao checkout; sha256: 64 caracteres hex minúsculos; role: contract, evidence, verdict, report ou manifest |
| ApprovalRef | run_id, gate_id, decision_id, actor_ref: strings opacas/ator real; decision: approved, changes_requested ou rejected; decided_at: RFC3339 UTC; artifacts: ArtifactRef[] não vazio; prerequisites: decision_id[] |
| StageInput | checkout_ref; bundle_path; stage; language: pt-BR ou en-US; actor_id; context_refs: ArtifactRef[]; approval_refs: ApprovalRef[]; allowed_paths: string[]; environment_ref: EnvironmentRef ou null; participation_ref: ParticipationRef |
| EnvironmentRef | plan_ref: ArtifactRef; checkout_ref; runtime_record_id; engine_identity; context_name; compose_project; owned_resource_ids: string[]; endpoints: lista service/host/port/url; ownership: environment_owned, environment_shared ou environment_unknown; health; observed_at |
| ParticipationRef | mode: local ou live; root_execution_id; snapshot_id: string ou null; approved_execution_refs: string[]; participant_refs: string[]; channel_ref: string ou null; bounds: limites finitos qualificados; approval_ref: ApprovalRef ou null |
