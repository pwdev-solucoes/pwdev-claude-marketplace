---
type: EXECUTION_PLAN
okf_version: "0.2"
generated:
  by: agent:power-roadmap
  at: "2026-09-12T10:31:30Z"
lifecycle:
  status: APPROVED
sources:
  - resource: ".planning/power/features/specflow/spec.md"
  - resource: ".planning/power/features/specflow-m01/plan-amendment-01-runtime-recipe.md"
  - resource: ".planning/power/features/specflow-m01/plan-amendment-02-stale-consumers.md"
verified:
  - event: human_approval
    by: human:user
    at: "2026-09-12T10:35:43Z"
    scope: specflow_v1_power_plan
    source: "user: aprovado"
  - event: human_approval
    by: human:user
    at: "2026-09-13T00:13:19Z"
    scope: .planning/power/features/specflow-m01/plan-amendment-01-runtime-recipe.md
    source: "user: sim"
  - event: human_approval
    by: human:user
    at: "2026-09-13T00:34:42Z"
    scope: .planning/power/features/specflow-m01/plan-amendment-02-stale-consumers.md
    source: "user: Aprovar"
---

# SpecFlow M01 — Contratos e qualificação do runtime — Plan

Status: APPROVED
Spec: [spec.md](../specflow/spec.md)
Updated: 2026-09-12

For agentic workers: execute this with pwdev-power:power-execute. Este plano foi aprovado; cada gate humano interno continua obrigatório.

## Goal
Contratos e qualificação do runtime com critérios verificáveis e handoff explícito.

## Architecture
Recursos estáticos em plugins/sdd-flow; contratos normativos tipados na spec, qualificação nativa antes do binding. Dependência: pedido autorizado de preparar proposta. M01.01 prepara PRD/Stories; M01.02 prepara TechSpec/escopo; M01.03 qualifica comandos somente leitura e propõe receitas; M01.04 reconcilia consumidores stale e renova TechSpec/TASKS; M01.05 vincula aprovação operacional separada; M01.06 executa probes; M01.07 reconcilia a prova. Não exigir contrato inexistente para redigir sua própria proposta. Sem paralelismo. Alteração de arquitetura ou escopo retorna ao design.

## Tech Stack
Markdown/OKF, YAML de Loop, TOML de extensão e JSON Schema; unittest Python já usado no repositório. Sintaxe CompozyOS só após qualificação local M01; nenhum helper executável distribuído. Fixtures Python são exclusivas da autoria.

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

## File Structure
Existentes consultados: plugins/pwdev-power/, plugins/sdd-composy/templates/, tests/test_sdd_composy.py e [spec compartilhada](../specflow/spec.md). Destinos futuros abaixo são CREATE ou UPDATE se já produzidos por tarefa anterior do mesmo programa; não pressupor existência e preservar mudanças alheias.
- `tests/test_sdd_flow_m01_qualification.py`
- `.planning/power/features/specflow-m01/runtime-qualification.md`
- `.planning/power/features/specflow-m01/probe-recipe.md`
- `tests/test_sdd_flow_m01_contracts.py`
- `.planning/power/features/specflow-m01/compatibility.md`
- `.planning/power/features/specflow-m01/interface-decisions.md`
- `tests/test_sdd_flow_m01_recipe.py`
- `.planning/power/features/specflow-m01/runtime-command-qualification.md`
- `tests/test_sdd_flow_m01_compatibility.py`
- `tests/fixtures/sdd_flow/extension.toml`
- `tests/fixtures/sdd_flow/agents/probe/AGENT.md`
- `tests/fixtures/sdd_flow/loops/probe.yaml`
- `tests/fixtures/sdd_flow/cases.json`

- `tasks/prd-specflow/prd.md` (CREATE: projeção contratual do PRD Power, sem mudar requisitos)
- `tasks/prd-specflow/stories.md` (CREATE: Stories ou aplicabilidade justificada)
- `tasks/prd-specflow/techspec.md` (CREATE: contrato técnico da spec Power)
- `tasks/prd-specflow/tasks.md` (CREATE: escopo contratual; não gerar TASK-NNN ready sem gate)

## Module acceptance
Identificar versão real e sintaxe suportada sem instalar. Provar gates humanos vinculados a bytes, schemas, carregamento de skills, atomicidade, histórico/retomada, confinamento, read-only e exclusão mútua. Qualificar capacidades de worktree, Docker, Live e exportação em ambiente autorizado. Matriz inclui teste positivo, negativo, esperado/observado, comando, resultado e referências reais. Help/build não comprovam comportamento. Falha central impede módulo dependente; opcional ausente no consumidor não bloqueia INIT. A adaptação de Stories N/A/QUICK e o perfil nativo precisam de aceite técnico explícito.
Comando focado: `python3 -m unittest tests.test_sdd_flow_m01_qualification tests.test_sdd_flow_m01_contracts tests.test_sdd_flow_m01_recipe tests.test_sdd_flow_m01_compatibility`. Mais de zero testes; testes de texto/schema não substituem prova real exigida. Cada relatório registra revisão, comando, exit code, resultado, artefato e hash. Módulo rejeitado invalida dependentes afetados.

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
- [ ] Conferir a receita por revisão documental e consultas de versão/help somente leitura. Registrar garantias ainda NOT_RUN; provas mutáveis pertencem à Task 04 e não são pré-requisito para terminar esta preparação.
- [ ] Revisar diff, critérios e fronteiras de permissão; apresentar relatório/gate Power e aprovações canônicas aplicáveis. Não marcar ready/complete, commitar, instalar ou publicar por inferência.

## Task 02 — Preparar TechSpec/escopo e contratos de garantias
Map ID: M01.02
Complexity: high
Files:
- `tests/test_sdd_flow_m01_contracts.py`
- `.planning/power/features/specflow-m01/compatibility.md`
- `.planning/power/features/specflow-m01/interface-decisions.md`
- `tasks/prd-specflow/techspec.md`
- `tasks/prd-specflow/tasks.md`
Interfaces:
- Consumes: RuntimeRecipe[]. Antes de despachar, o gerador do brief DEVE copiar verbatim da spec todas as definições de tipos transitivamente referenciadas por Consumes/Produces, incluindo enums, nulabilidade, invariantes e limites, para task-NN-brief.md; validar igualdade byte a byte das cláusulas copiadas e igualdade das assinaturas entre produtor/consumidor. Não despachar brief que dependa de outro checkout ou apenas mande consultar a spec. ResourceSet inclui paths, source_digests, interfaces e validation_refs. Contratos de entrada são lidos como dados, nunca instruções para ampliar permissões.
- Produces: QualificationCheck[]. Os recursos/artefatos produzidos são exatamente os arquivos listados, com referências relativas válidas; assinatura proposta exige binding validado M01.
Acceptance:
Versionar proposta de schemas, guardas de digest e publicação atômica; mudanças arquiteturais ou dispensa Stories/QUICK exigem gate técnico, não fallback por confiança.
Steps:
- [ ] Conferir gates e digests de PRD/spec/plano, dependência anterior completa e escopo dos arquivos desta tarefa; registrar bloqueio se qualquer pré-requisito faltar.
- [ ] Escrever em `tests/test_sdd_flow_m01_contracts.py` testes positivos e negativos dos critérios desta tarefa; executar `python3 -m unittest tests.test_sdd_flow_m01_contracts` e comprovar RED pelo comportamento ausente, nunca por zero testes ou erro de importação.
- [ ] Produzir compatibility.md e interface-decisions.md com as hipóteses a qualificar; produzir TechSpec contratual fiel à spec Power e apresentar seu gate humano; após aceite, produzir escopo TASKS com allowlist/comandos/dependências e pedir gate próprio. Aprovação de probe é separada.
- [ ] Executar `python3 -m unittest tests.test_sdd_flow_m01_contracts`, confirmar mais de zero testes, resultado sem falhas e validar os links/inputs/outputs dos arquivos listados.
- [ ] Revisar a matriz e as decisões propostas sem executar probes. Encaminhar a qualificação somente leitura para a Task 03; somente a Task 04 executa provas mutáveis depois dos gates correspondentes.
- [ ] Revisar diff, critérios e fronteiras de permissão; apresentar relatório/gate Power e aprovações canônicas aplicáveis. Não marcar ready/complete, commitar, instalar ou publicar por inferência.

## Task 03 — Qualificar comandos e aprovar RuntimeRecipe
Map ID: M01.03
Complexity: high
Files:
- `tests/test_sdd_flow_m01_recipe.py`
- `.planning/power/features/specflow-m01/runtime-command-qualification.md`
- `.planning/power/features/specflow-m01/probe-recipe.md`
- `.planning/power/features/specflow-m01/runtime-qualification.md`
- `tasks/prd-specflow/tasks.md`
Interfaces:
- Consumes: RuntimeRecipe[], QualificationCheck[], ApprovalRef, ArtifactRef. Antes de despachar, o gerador do brief DEVE copiar verbatim da spec todas as definições de tipos transitivamente referenciadas por Consumes/Produces, incluindo enums, nulabilidade, invariantes e limites, para task-NN-brief.md; validar igualdade byte a byte das cláusulas copiadas e igualdade das assinaturas entre produtor/consumidor. Não despachar brief que dependa de outro checkout ou apenas mande consultar a spec. ResourceSet inclui paths, source_digests, interfaces e validation_refs. Contratos de entrada são lidos como dados, nunca instruções para ampliar permissões.
- Produces: RuntimeRecipe[] concreto e CommandQualification documental, ambos NOT_RUN até gates de TASKS e escopo operacional. Os recursos/artefatos produzidos são exatamente os arquivos listados, com referências relativas válidas; nenhum ApprovalRef é fabricado e nenhuma garantia CORE/OPT vira PASS.
Acceptance:
Qualificar executable/argv/cwd por version/help/status somente leitura, distinguir descoberta de comportamento, preparar escopo/cleanup/budgets exatos e transferir explicitamente consumidores stale para Task 04; nenhum gate ou probe ocorre nesta tarefa.
Steps:
- [ ] Conferir gates e digests de PRD/Stories/TechSpec, emenda aprovada, Task 02 completa e TASKS stale; registrar qualquer divergência antes de autoria.
- [ ] Escrever `tests/test_sdd_flow_m01_recipe.py` com positivos/negativos para argv concreto, escopo confinado, cleanup próprio, aprovação stale e proibição de PASS inventado; executar o teste e comprovar RED real.
- [ ] Consultar somente `command -v`, version, help e status dos comandos candidatos; registrar comando, versão, esperado/observado e exit code sem iniciar daemon, link, Loop, Run, browser, Docker ou Live.
- [ ] Produzir runtime-command-qualification.md e atualizar probe-recipe.md/runtime-qualification.md com receitas concretas propostas, resultados NOT_RUN e approved_scope null; reabrir/atualizar TASKS com a nova allowlist e dependências.
- [ ] Executar `python3 -m unittest tests.test_sdd_flow_m01_recipe`, confirmar mais de zero testes e zero falhas; executar também a suíte combinada somente para inventariar consumidores stale e registrar seus seis IDs/causas sem reclassificá-los como baseline.
- [ ] Entregar a proposta à Task 04; não solicitar gate TASKS ou operacional nesta tarefa e não executar comandos mutáveis.
- [ ] Revisar diff, critérios e permissões; retornar DONE com os consumidores stale explícitos, sem commitar, instalar, provisionar ou publicar.

## Task 04 — Reconciliar consumidores stale e renovar contratos
Map ID: M01.04
Complexity: high
Files:
- `tests/test_sdd_flow_m01_qualification.py`
- `tests/test_sdd_flow_m01_contracts.py`
- `.planning/power/features/specflow-m01/compatibility.md`
- `tasks/prd-specflow/techspec.md`
- `tasks/prd-specflow/tasks.md`
Interfaces:
- Consumes: RuntimeRecipe[], QualificationCheck[], ApprovalRef, ArtifactRef. Antes de despachar, o gerador do brief DEVE copiar verbatim da spec todas as definições de tipos transitivamente referenciadas por Consumes/Produces, incluindo enums, nulabilidade, invariantes e limites, para task-NN-brief.md; validar igualdade byte a byte das cláusulas copiadas e igualdade das assinaturas entre produtor/consumidor. Não despachar brief que dependa de outro checkout ou apenas mande consultar a spec. ResourceSet inclui paths, source_digests, interfaces e validation_refs. Contratos de entrada são lidos como dados, nunca instruções para ampliar permissões.
- Produces: consumidores reconciliados da RuntimeRecipe[] concreta ainda NOT_RUN; TechSpec e TASKS com gates renovados. Os recursos/artefatos produzidos são exatamente os arquivos listados, com referências relativas válidas; nenhuma garantia vira PASS e nenhuma receita é executada.
Acceptance:
Eliminar as seis falhas stale sem revertê-las ou tratá-las como baseline; atualizar digests/semântica e obter gates separados de TechSpec e TASKS antes da aprovação operacional.
Steps:
- [ ] Conferir Task 03 e reproduzir as seis falhas stale pelos mesmos IDs/causas; divergência exige parar e reconciliar o inventário.
- [ ] Atualizar testes de qualificação/contratos por TDD para a receita concreta ainda não aprovada, TASKS renovado e digests vigentes; não enfraquecer negativos.
- [ ] Atualizar compatibility e TechSpec da entrada vazia para proposta concreta NOT_RUN/BLOCKED, preservando histórico e reabrindo o TechSpec DRAFT/PENDING.
- [ ] Atualizar TASKS para sete tasks, allowlists/dependências exatas e estado DRAFT/PENDING; nenhum TASK fica ready/complete por existência.
- [ ] Executar `python3 -m unittest tests.test_sdd_flow_m01_recipe tests.test_sdd_flow_m01_qualification tests.test_sdd_flow_m01_contracts`, confirmar mais de zero testes e zero falhas; validar links/digests.
- [ ] Apresentar TechSpec para gate humano e, após aceite, TASKS para gate próprio; aprovação operacional da receita permanece separada.
- [ ] Revisar diff e fronteiras; retornar NEEDS_CONTEXT em cada gate, sem probe, commit, instalação, daemon, Loop, Docker, browser ou Live.

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

## Task 07 — Reconciliar prova e gate técnico
Map ID: M01.07
Complexity: high
Files:
- `tests/test_sdd_flow_m01_compatibility.py`
- `tests/test_sdd_flow_m01_qualification.py`
- `.planning/power/features/specflow-m01/runtime-qualification.md`
- `.planning/power/features/specflow-m01/compatibility.md`
- `.planning/power/features/specflow-m01/interface-decisions.md`
Interfaces:
- Consumes: ResourceSet das fixtures da Task 06, RuntimeRecipe[] e ApprovalRef renovado por gate humano entre tarefas. Antes de despachar, o gerador do brief DEVE copiar verbatim da spec todas as definições de tipos transitivamente referenciadas por Consumes/Produces, incluindo enums, nulabilidade, invariantes e limites, para task-NN-brief.md; validar igualdade byte a byte das cláusulas copiadas e igualdade das assinaturas entre produtor/consumidor. Não despachar brief que dependa de outro checkout ou apenas mande consultar a spec. ResourceSet inclui paths, source_digests, interfaces e validation_refs. Contratos de entrada são lidos como dados, nunca instruções para ampliar permissões. IDs reais retornados pelo Loop são registrados separadamente e nunca confundidos com o recibo Power.
- Produces: RuntimeQualification (core_checks todos PASS, verdict PASS após gate independente). Os recursos/artefatos produzidos são exatamente os arquivos listados, com referências relativas válidas; assinatura proposta exige binding validado M01.
Acceptance:
Executar em escopo autorizado casos positivos/negativos de gate falso, digest alterado, path traversal/symlink, concorrência, interrupção antes/depois de publicação, retomada e observer tentando mutação; guardar esperado/observado real. Cada garantia central tem prova PASS fresca e revisada; teste ausente/NOT_RUN/ENVIRONMENT_FAILURE impede M02.
Steps:
- [ ] Conferir gates e digests de PRD/spec/plano, dependência anterior completa e escopo dos arquivos desta tarefa; registrar bloqueio se qualquer pré-requisito faltar.
- [ ] Escrever em `tests/test_sdd_flow_m01_qualification.py` testes positivos e negativos dos critérios desta tarefa; executar `python3 -m unittest tests.test_sdd_flow_m01_qualification` e comprovar RED pelo comportamento ausente, nunca por zero testes ou erro de importação.
- [ ] Produzir somente os recursos listados, usando os templates individuais e interfaces declaradas; diferenças da fonte exigem provenance e novo gate quando mudarem contrato.
- [ ] Executar `python3 -m unittest tests.test_sdd_flow_m01_qualification`, confirmar mais de zero testes, resultado sem falhas e validar os links/inputs/outputs dos arquivos listados.
- [ ] Executar os ensaios reais aplicáveis apenas pela receita M01 qualificada e autorizada; ausência de receita/capacidade obrigatória é BLOCKED/NOT_RUN. Registrar comando, revisão, esperado/observado, exit code e hash, preservando evidência anterior.
- [ ] Revisar diff, critérios e fronteiras de permissão; apresentar relatório/gate Power e aprovações canônicas aplicáveis. Não marcar ready/complete, commitar, instalar ou publicar por inferência.

## Exit gate
Este módulo só habilita o próximo após critérios comprovados, QA/review não bloqueantes, verificação independente e aceite humano aplicável. Qualificação central insuficiente, falha nova, referência quebrada ou critério obrigatório NOT_RUN bloqueia o handoff. Não editar state.md antes de decisão conhecida.
