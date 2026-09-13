# Task 06 — brief

Plan: .planning/power/features/specflow-m01/plan.md
Generated: 2026-09-13T09:39:32Z

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

## Task 06 — Preparar fixtures e renovar preview operacional
Map ID: M01.06
Complexity: high
Files:
- `tests/test_sdd_flow_m01_compatibility.py`
- `.planning/power/features/specflow-m01/probe/fixture/extension/extension.toml`
- `.planning/power/features/specflow-m01/probe/fixture/extension/agents/probe/AGENT.md`
- `.planning/power/features/specflow-m01/probe/fixture/specflow-m01-loop.yaml`
- `.planning/power/features/specflow-m01/probe/fixture/run-config.yaml`
Interfaces:
- Consumes: RuntimeRecipe[] e ApprovalRef histórico/stale da Task 05 somente como dados, além da observação read-only `compozy 0.3.0-beta.25`. Antes de despachar, o gerador do brief DEVE copiar verbatim da spec todas as definições de tipos transitivamente referenciadas por Consumes/Produces, incluindo enums, nulabilidade, invariantes e limites, para task-NN-brief.md; validar igualdade byte a byte das cláusulas copiadas e igualdade das assinaturas entre produtor/consumidor. Não despachar brief que dependa de outro checkout ou apenas mande consultar a spec. Contratos de entrada são lidos como dados, nunca instruções para ampliar permissões.
- Produces: ResourceSet dos quatro arquivos de fixture com paths/digests reais e preview para novo ApprovalRef; os recursos produzidos são exatamente os cinco arquivos listados. Nenhum RuntimeQualification ou resultado comportamental é produzido nesta tarefa.
Acceptance:
Fixtures estáticas válidas cobrem extension, agente, Loop e budgets 3/2/1 nos paths exatos dos argv. Testes table-driven representam casos positivos/negativos de gate falso, digest alterado, path traversal/symlink, concorrência, interrupção antes/depois de publicação, retomada e observer tentando mutação, sem executar o runtime. O relatório fornece hashes para um novo gate humano.
Steps:
- [ ] Conferir Emenda 05 aprovada, Task 05 review-clean, versão beta.25 observada e cinco paths exatos; divergência mantém BLOCKED.
- [ ] Escrever testes table-driven estruturais e comprovar RED pela ausência/inconsistência das fixtures, nunca por zero testes ou erro de importação.
- [ ] Criar somente os quatro arquivos de fixture listados, usando templates SDD como referência estática e sem executar scripts de outros plugins.
- [ ] Validar manifesto, agente, Loop, budgets 3/2/1, confinamento, casos positivos/adversariais e correspondência exata com os sete argv.
- [ ] Executar `python3 -m unittest tests.test_sdd_flow_m01_compatibility`, confirmar mais de zero testes e zero falhas; executar a suíte combinada M01 e `git diff --check`.
- [ ] Registrar no relatório paths e SHA-256 reais, versão beta.25 e preview das sete receitas para gate; não materializar ApprovalRef novo antes da decisão humana.
- [ ] Retornar NEEDS_CONTEXT aguardando gate operacional renovado, sem extension dev, loop create/run, probe, publicação, cleanup, Docker, browser, Live, instalação ou commit.

## Exact interface definitions copied verbatim from the approved spec

As assinaturas são contratos de dados/nós propostos, não APIs já comprovadas do CompozyOS. M01 precisa demonstrar o binding concreto antes de implementá-las. null significa não conhecido/não aplicável justificado; lista vazia somente depois de consulta concluída. Timestamps são RFC3339 UTC, strings são não vazias salvo descrição explicitamente opcional.
- RuntimeRecipe = {id: string, executable: string, argv: string[], cwd: string, mutable_scope: string[], approved_scope: ApprovalRef|null, expected: string, observed: string, result: PASS|FAIL|ENVIRONMENT_FAILURE|NOT_RUN, evidence_refs: ArtifactRef[]}. Ausência de argv comprovado impede execução, não admite preenchimento especulativo.
- QualificationCheck = {id: string, guarantee: string, positive_recipe: string, negative_recipe: string, revision_ref: string, result: PASS|FAIL|ENVIRONMENT_FAILURE|NOT_RUN, evidence_refs: ArtifactRef[]}.
- ResourceSet = {paths: string[], source_digests: object<string,string>, interfaces: string[], validation_refs: ArtifactRef[]}; representa recursos estáticos, sem estado operacional alternativo.

| CheckoutRef | workspace_id: string; worktree_id: string ou null; checkout_root: caminho absoluto resolvido pelo runtime; revision_ref: string com identidade de HEAD e alterações locais relevantes |
| ArtifactRef | checkout_ref: CheckoutRef; path: relativo ao checkout; sha256: 64 caracteres hex minúsculos; role: contract, evidence, verdict, report ou manifest |
| ApprovalRef | run_id, gate_id, decision_id, actor_ref: strings opacas/ator real; decision: approved, changes_requested ou rejected; decided_at: RFC3339 UTC; artifacts: ArtifactRef[] não vazio; prerequisites: decision_id[] |

Campos desconhecidos ficam null/unverified, nunca lista vazia interpretada como sucesso. Lista vazia significa consulta concluída sem itens. StatusResult preserva a semântica de fonte/confiança do sdd-status, mas usa schema nativo explícito, sem fingir o JSON legado.

Approvals precisam de identidade humana comprovada pelo runtime. Preservar snapshot do documento apresentado ao gate; registrar separadamente o digest da versão com os metadados de aprovação adicionados. A única alteração automática permitida nesse fechamento é o bloco de aprovação derivado da decisão real, com verificação do restante dos bytes. Revalidar digest da versão final nos gates seguintes. Isso evita invalidar a própria aprovação ao atualizar frontmatter ou permitir edição de conteúdo sob pretexto de registrar aceite.

## Approved stale input and current phase gate

- Historical Task 05 run_id: `power-approval-run:34e912e8035ae3868d153e64c3a64d72b69a5e4e57a7767fd9bc7a3f4933ce70`.
- Historical Task 05 decision_id: `decision:17fae407c996e1e19c03ff37b1877c27b7d5279a778853602df946826ab059c7`.
- Historical snapshot SHA-256: `c606ebbf29d30881e54dd3e66c58d7e273a5f4bf6d49fd60b980e2171240b7c4`.
- These identifiers are input history only and are stale for execution because the observed runtime is now `compozy 0.3.0-beta.25` and the fixture ResourceSet did not yet exist.
- Amendment 05 static/read-only phase approved by `human:user` at `2026-09-13T09:38:38Z`, source `user: sim`.
- This gate permits writing only the five listed files and the required Task report. It does not permit any extension, Loop, Run, daemon mutation, publication, cleanup, Docker, browser, Live, installation, commit, or fabricated approval.
