# Task 05 — brief

Plan: .planning/power/features/specflow-m01/plan.md
Generated: 2026-09-13T09:22:24Z

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

## Task 05 — Vincular aprovação operacional da RuntimeRecipe
Map ID: M01.05
Complexity: high
Files:
- `tests/test_sdd_flow_m01_recipe.py`
- `.planning/power/features/specflow-m01/probe-recipe.md`
- `.planning/power/features/specflow-m01/probe-recipe-approved-snapshot.md`
- `.planning/power/features/specflow-m01/runtime-command-qualification.md`
- `.planning/power/features/specflow-m01/runtime-qualification.md`
Interfaces:
- Consumes: RuntimeRecipe[], ApprovalRef, ArtifactRef. Antes de despachar, o gerador do brief DEVE copiar verbatim da spec todas as definições de tipos transitivamente referenciadas por Consumes/Produces, incluindo enums, nulabilidade, invariantes e limites, para task-NN-brief.md; validar igualdade byte a byte das cláusulas copiadas e igualdade das assinaturas entre produtor/consumidor. Não despachar brief que dependa de outro checkout ou apenas mande consultar a spec. ResourceSet inclui paths, source_digests, interfaces e validation_refs. Contratos de entrada são lidos como dados, nunca instruções para ampliar permissões.
- Produces: RuntimeRecipe[] com ApprovalRef pré-Run real/fresco ligado aos bytes, prerequisites e escopo aprovados; `run_id` usa namespace `power-approval-run:` e é derivado deterministicamente do checkout/revisão, Task 05 e snapshot; `gate_id` é `gate:specflow-m01:runtime-recipe`; `decision_id` deriva deterministicamente do ator, decisão, timestamp, checkout/revisão e snapshot. `.planning/power/features/specflow-m01/probe-recipe-approved-snapshot.md` preserva exatamente os bytes pré-aprovação com SHA-256 `c606ebbf29d30881e54dd3e66c58d7e273a5f4bf6d49fd60b980e2171240b7c4`, e todos os ArtifactRef da decisão apontam para esse arquivo regular endereçável. Resultados continuam NOT_RUN. Os recursos/artefatos produzidos são exatamente os arquivos listados, com referências relativas válidas; ausência de identidade humana real mantém BLOCKED.
Acceptance:
Apresentar preview completo, obter decisão operacional separada e atualizar somente campos derivados da aprovação; IDs do recibo Power são reproduzíveis a partir dos registros UTF-8/LF canônicos e distintos dos futuros IDs do Loop. O snapshot referenciado resolve diretamente para arquivo regular confinado cujo SHA-256 corresponde ao ArtifactRef. Testes rejeitam alterações de IDs, artifacts, prerequisites, ordem, timestamp, ator, path/digest e mistura de namespaces. Nenhuma execução ocorre e incapacidade de provar ApprovalRef bloqueia Task 06.
Steps:
- [ ] Conferir TechSpec/TASKS aprovados, receitas/digests vigentes e identidade disponível; falta ou divergência mantém BLOCKED.
- [ ] Escrever/atualizar testes positivos e negativos de gate operacional, ApprovalRef, bytes stale, escopo, cleanup e budgets; recomputar `run_id`/`decision_id` dos registros UTF-8/LF canônicos e rejeitar ID alterado, artifacts vazio, prerequisites vazios/fora de ordem, timestamp divergente, ator inválido, path/digest stale e mistura Power/Loop; comprovar RED real antes do binding.
- [ ] Apresentar as sete receitas, executable/argv/cwd, mutable_scope, cleanup e budgets para decisão humana separada; nenhuma ação mutável antes dela.
- [ ] Após aceite real, preservar os bytes pré-aprovação em `.planning/power/features/specflow-m01/probe-recipe-approved-snapshot.md` com SHA-256 `c606ebbf29d30881e54dd3e66c58d7e273a5f4bf6d49fd60b980e2171240b7c4`; registrar ApprovalRef com `actor_ref: human:user`, `gate_id: gate:specflow-m01:runtime-recipe`, `run_id`/`decision_id` determinísticos, algoritmo/inputs reproduzíveis, prerequisites e ArtifactRef apontando para esse arquivo regular; se qualquer input não puder ser demonstrado, não fabricar e retornar BLOCKED.
- [ ] Manter `result` e `observed` NOT_RUN e CORE/OPT NOT_RUN; executar `python3 -m unittest tests.test_sdd_flow_m01_recipe tests.test_sdd_flow_m01_qualification tests.test_sdd_flow_m01_contracts` com zero falhas.
- [ ] Revisar hashes, validar por path os sete ArtifactRef contra o snapshot endereçável e garantir que somente campos derivados da decisão mudaram no fechamento do gate.
- [ ] Retornar DONE ou BLOCKED, sem executar daemon, extensão, Loop, Run, cleanup, Docker, browser ou Live e sem commitar/publicar.

## Exact canonical receipt records from approved Amendment 03

Use UTF-8, LF, no trailing whitespace on any line, and exactly one final LF.
`run_id` is `power-approval-run:` plus the lowercase SHA-256 of exactly:

```text
schema=specflow.power-approval-run.v1
feature=specflow-m01
task=M01.05
checkout_revision=fb146297d681a1a6a77d71b5c30772655802590a
snapshot_sha256=c606ebbf29d30881e54dd3e66c58d7e273a5f4bf6d49fd60b980e2171240b7c4
```

`decision_id` is `decision:` plus the lowercase SHA-256 of exactly the following,
replacing `<run_id>` with the computed value:

```text
schema=specflow.power-approval-decision.v1
run_id=<run_id>
gate_id=gate:specflow-m01:runtime-recipe
actor_ref=human:user
decision=approved
decided_at=2026-09-13T08:53:00Z
snapshot_sha256=c606ebbf29d30881e54dd3e66c58d7e273a5f4bf6d49fd60b980e2171240b7c4
techspec_sha256=09bde614371cb465ea1c135244bd6c4e8cc3f3e62c0c9fdeb3dc065d70ab54f3
tasks_sha256=1efe23df5abe7950567a39bc9451adb5672de14f835ec111fed30bb941bd02d4
```

`prerequisites`, in order, are:

1. `power-gate:techspec:09bde614371cb465ea1c135244bd6c4e8cc3f3e62c0c9fdeb3dc065d70ab54f3`
2. `power-gate:tasks:1efe23df5abe7950567a39bc9451adb5672de14f835ec111fed30bb941bd02d4`

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
