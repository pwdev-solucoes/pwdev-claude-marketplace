---
type: ROADMAP_INDEX
okf_version: "0.2"
generated:
  by: agent:power-roadmap
  at: "2026-09-12T10:31:30Z"
lifecycle:
  status: APPROVED
sources:
  - resource: ".planning/power/product/prd.md"
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

# SpecFlow — Plan

Status: APPROVED
Spec: [spec.md](spec.md)
Updated: 2026-09-12

## Goal
Implementar a v1 SpecFlow em 12 módulos sequenciais e 35 tarefas Power revisáveis. Este é índice mestre de propostas, não plano executável monolítico. Nunca entregar os 35 itens juntos a power-execute. Cada plano tem no máximo 8 tarefas e aguarda os próprios gates.

## Architecture
Autoria por pwdev-power; SDD fornece exclusivamente os contratos e comportamento do produto; CompozyOS executa recursos nativos quando qualificados. Os planos não substituem gates canônicos nem criam contratos TASK-NNN. O PRD, a especificação, a rastreabilidade e os 12 planos foram aprovados em 2026-09-12T10:35:43Z; o próximo passo é executar M01 Task 01 e parar no gate do PRD contratual.

## Tech Stack
Markdown/OKF, YAML, TOML, JSON Schema e unittest Python. As raízes existentes plugins/pwdev-power/, plugins/sdd-composy/ e tests/ fundamentam os caminhos; plugins/sdd-flow/ é destino futuro CREATE. Contextos Power ausentes não são usados como prova.

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
- [Spec autocontida](spec.md)
- [PRD](../../product/prd.md)
- [TRACEABILITY](TRACEABILITY.md)
- [Plano M01](../specflow-m01/plan.md)
- [Plano M02](../specflow-m02/plan.md)
- [Plano M03](../specflow-m03/plan.md)
- [Plano M04](../specflow-m04/plan.md)
- [Plano M05](../specflow-m05/plan.md)
- [Plano M06](../specflow-m06/plan.md)
- [Plano M07](../specflow-m07/plan.md)
- [Plano M08](../specflow-m08/plan.md)
- [Plano M09](../specflow-m09/plan.md)
- [Plano M10](../specflow-m10/plan.md)
- [Plano M11](../specflow-m11/plan.md)
- [Plano M12](../specflow-m12/plan.md)
O inventário de arquivos de implementação exatos está no File Structure de cada módulo. Nenhuma implementação, contrato aprovado, state.md ou branch foi modificado por esta proposta.

## Roadmap
A hierarquia Power agrupa seis fases, um épico por fase e duas Features por épico. São agrupamentos propostos; release público somente após M12. F01 entrega contrato/compatibilidade verificável; F02 templates e preparação; F03 planejamento do consumidor; F04 ambiente e entrega; F05 colaboração e dossier; F06 operação e aceite final.

| Phase | Epic | Feature | Módulo/plano | Tasks | Dependência |
|---|---|---|---|---:|---|
| F01 | F01-E01 | F01-E01-FT01 | [M01 — Contratos e qualificação do runtime](../specflow-m01/plan.md) | 7 | gates de proposta e receita |
| F01 | F01-E01 | F01-E01-FT02 | [M02 — Referências, schemas e manifesto](../specflow-m02/plan.md) | 8 | M01 aceito |
| F02 | F02-E01 | F02-E01-FT01 | [M03 — Templates fiéis e complementos mínimos](../specflow-m03/plan.md) | 4 | M02 aceito |
| F02 | F02-E01 | F02-E01-FT02 | [M04 — INIT, intake e MAP](../specflow-m04/plan.md) | 2 | M03 aceito |
| F03 | F03-E01 | F03-E01-FT01 | [M05 — Produto, Stories, roadmap e promoção](../specflow-m05/plan.md) | 2 | M04 aceito |
| F03 | F03-E01 | F03-E01-FT02 | [M06 — TechSpec e contratos TASK](../specflow-m06/plan.md) | 2 | M05 aceito |
| F04 | F04-E01 | F04-E01-FT01 | [M07 — Worktree nativo e Docker por Feature](../specflow-m07/plan.md) | 2 | M06 aceito |
| F04 | F04-E01 | F04-E01-FT02 | [M08 — Entrega SDD e gates independentes](../specflow-m08/plan.md) | 5 | M07 aceito |
| F05 | F05-E01 | F05-E01-FT01 | [M09 — Network Live opcional e consentimento](../specflow-m09/plan.md) | 1 | M08 aceito |
| F05 | F05-E01 | F05-E01-FT02 | [M10 — HTML/PDF e fechamento do dossier](../specflow-m10/plan.md) | 1 | M09 aceito |
| F06 | F06-E01 | F06-E01-FT01 | [M11 — QUICK e status consolidado somente leitura](../specflow-m11/plan.md) | 2 | M10 aceito |
| F06 | F06-E01 | F06-E01-FT02 | [M12 — Aceitação, documentação e conformidade com a fonte](../specflow-m12/plan.md) | 2 | M11 aceito |

## Task map
Mxx.yy identifica o mapa; Task NN identifica a tarefa local no plano Power. Nenhum TASK-NNN do produto é criado ou renumerado. A etapa executiva só poderá vincular contratos individuais existentes/aprovados explicitamente; este índice não converte IDs de mapa em contratos SDD.

| ID do mapa | Task Power | Nome | Complexidade | Arquivos |
|---|---|---|---|---|
| M01.01 | M01 Task 01 | Preparar PRD, Stories/aplicabilidade e receita | high | `tests/test_sdd_flow_m01_qualification.py`; `.planning/power/features/specflow-m01/runtime-qualification.md`; `.planning/power/features/specflow-m01/probe-recipe.md`; `tasks/prd-specflow/prd.md`; `tasks/prd-specflow/stories.md` |
| M01.02 | M01 Task 02 | Preparar TechSpec/escopo e contratos de garantias | high | `tests/test_sdd_flow_m01_contracts.py`; `.planning/power/features/specflow-m01/compatibility.md`; `.planning/power/features/specflow-m01/interface-decisions.md`; `tasks/prd-specflow/techspec.md`; `tasks/prd-specflow/tasks.md` |
| M01.03 | M01 Task 03 | Qualificar comandos e aprovar RuntimeRecipe | high | `tests/test_sdd_flow_m01_recipe.py`; `.planning/power/features/specflow-m01/runtime-command-qualification.md`; `.planning/power/features/specflow-m01/probe-recipe.md`; `.planning/power/features/specflow-m01/runtime-qualification.md`; `tasks/prd-specflow/tasks.md` |
| M01.04 | M01 Task 04 | Reconciliar consumidores stale e renovar contratos | high | `tests/test_sdd_flow_m01_qualification.py`; `tests/test_sdd_flow_m01_contracts.py`; `.planning/power/features/specflow-m01/compatibility.md`; `tasks/prd-specflow/techspec.md`; `tasks/prd-specflow/tasks.md` |
| M01.05 | M01 Task 05 | Vincular aprovação operacional da RuntimeRecipe | high | `tests/test_sdd_flow_m01_recipe.py`; `.planning/power/features/specflow-m01/probe-recipe.md`; `.planning/power/features/specflow-m01/runtime-command-qualification.md`; `.planning/power/features/specflow-m01/runtime-qualification.md` |
| M01.06 | M01 Task 06 | Probe isolado positivo e adversarial | high | `tests/test_sdd_flow_m01_compatibility.py`; `tests/fixtures/sdd_flow/extension.toml`; `tests/fixtures/sdd_flow/agents/probe/AGENT.md`; `tests/fixtures/sdd_flow/loops/probe.yaml`; `tests/fixtures/sdd_flow/cases.json` |
| M01.07 | M01 Task 07 | Reconciliar prova e gate técnico | high | `tests/test_sdd_flow_m01_qualification.py`; `.planning/power/features/specflow-m01/runtime-qualification.md`; `.planning/power/features/specflow-m01/compatibility.md`; `.planning/power/features/specflow-m01/interface-decisions.md` |
| M02.01 | M02 Task 01 | Referências 1 | high | `tests/test_sdd_flow_m02_references.py`; `plugins/sdd-flow/skills/sdd-flow-contracts/references/artifacts.md`; `plugins/sdd-flow/skills/sdd-flow-contracts/references/evidence.md`; `plugins/sdd-flow/skills/sdd-flow-contracts/references/execution.md`; `plugins/sdd-flow/skills/sdd-flow-contracts/references/language.md` |
| M02.02 | M02 Task 02 | Referências 2 | high | `tests/test_sdd_flow_m02_references.py`; `plugins/sdd-flow/skills/sdd-flow-contracts/references/loop.md`; `plugins/sdd-flow/skills/sdd-flow-contracts/references/mapping.md`; `plugins/sdd-flow/skills/sdd-flow-contracts/references/okf.md`; `plugins/sdd-flow/skills/sdd-flow-contracts/references/product.md` |
| M02.03 | M02 Task 03 | Referências 3 | high | `tests/test_sdd_flow_m02_references.py`; `plugins/sdd-flow/skills/sdd-flow-contracts/references/quality.md`; `plugins/sdd-flow/skills/sdd-flow-contracts/references/quick.md`; `plugins/sdd-flow/skills/sdd-flow-contracts/references/safety.md`; `plugins/sdd-flow/skills/sdd-flow-contracts/references/specification.md` |
| M02.04 | M02 Task 04 | Referências 4 | high | `tests/test_sdd_flow_m02_references.py`; `plugins/sdd-flow/skills/sdd-flow-contracts/references/states.md`; `plugins/sdd-flow/skills/sdd-flow-contracts/references/status.md`; `plugins/sdd-flow/skills/sdd-flow-contracts/references/stories.md`; `plugins/sdd-flow/skills/sdd-flow-contracts/references/tasks.md` |
| M02.05 | M02 Task 05 | Referências 5 | high | `tests/test_sdd_flow_m02_references.py`; `plugins/sdd-flow/skills/sdd-flow-contracts/references/trace.md`; `plugins/sdd-flow/skills/sdd-flow-contracts/references/verification.md`; `plugins/sdd-flow/skills/sdd-flow-contracts/references/workflow.md`; `plugins/sdd-flow/skills/sdd-flow-contracts/references/runtime-native.md` |
| M02.06 | M02 Task 06 | Referências 6 | high | `tests/test_sdd_flow_m02_references.py`; `plugins/sdd-flow/skills/sdd-flow-contracts/references/environment.md`; `plugins/sdd-flow/skills/sdd-flow-contracts/references/network.md`; `plugins/sdd-flow/skills/sdd-flow-contracts/references/exports.md`; `plugins/sdd-flow/skills/sdd-flow-contracts/references/provenance.md` |
| M02.07 | M02 Task 07 | Schemas e biblioteca | high | `tests/test_sdd_flow_m02_contracts.py`; `plugins/sdd-flow/skills/sdd-flow-contracts/SKILL.md`; `plugins/sdd-flow/skills/sdd-flow-contracts/schemas/evidence-manifest.schema.json`; `plugins/sdd-flow/skills/sdd-flow-contracts/schemas/evidence-native.schema.json`; `plugins/sdd-flow/skills/sdd-flow-contracts/schemas/native-contracts.schema.json` |
| M02.08 | M02 Task 08 | Manifesto | high | `tests/test_sdd_flow_m02_extension.py`; `plugins/sdd-flow/extension.toml` |
| M03.01 | M03 Task 01 | Templates SDD 1 | medium | `tests/test_sdd_flow_m03_templates.py`; `plugins/sdd-flow/skills/sdd-flow-contracts/templates/prd.md`; `plugins/sdd-flow/skills/sdd-flow-contracts/templates/stories.md`; `plugins/sdd-flow/skills/sdd-flow-contracts/templates/techspec.md`; `plugins/sdd-flow/skills/sdd-flow-contracts/templates/tasks.md` |
| M03.02 | M03 Task 02 | Templates SDD 2 | medium | `tests/test_sdd_flow_m03_templates.py`; `plugins/sdd-flow/skills/sdd-flow-contracts/templates/task.md`; `plugins/sdd-flow/skills/sdd-flow-contracts/templates/quick-contract.md`; `plugins/sdd-flow/skills/sdd-flow-contracts/templates/quick-report.md`; `plugins/sdd-flow/skills/sdd-flow-contracts/templates/qa.md` |
| M03.03 | M03 Task 03 | Templates SDD 3 | medium | `tests/test_sdd_flow_m03_templates.py`; `plugins/sdd-flow/skills/sdd-flow-contracts/templates/codereview.md`; `plugins/sdd-flow/skills/sdd-flow-contracts/templates/evidence-report.md`; `plugins/sdd-flow/skills/sdd-flow-contracts/templates/verdict.md` |
| M03.04 | M03 Task 04 | Complementos nativos | medium | `tests/test_sdd_flow_m03_native_templates.py`; `plugins/sdd-flow/skills/sdd-flow-contracts/templates/roadmap.md`; `plugins/sdd-flow/skills/sdd-flow-contracts/templates/environment.md`; `plugins/sdd-flow/skills/sdd-flow-contracts/templates/approval-receipt.md`; `plugins/sdd-flow/skills/sdd-flow-contracts/templates/export-receipt.md` |
| M04.01 | M04 Task 01 | Entrada e capacidades | medium | `tests/test_sdd_flow_m04_init.py`; `plugins/sdd-flow/agents/sdd-flow-coordinator/AGENT.md`; `plugins/sdd-flow/skills/sdd-flow-intake/SKILL.md`; `plugins/sdd-flow/skills/sdd-flow-init/SKILL.md` |
| M04.02 | M04 Task 02 | Observação MAP | medium | `tests/test_sdd_flow_m04_map.py`; `plugins/sdd-flow/skills/sdd-flow-map/SKILL.md` |
| M05.01 | M05 Task 01 | PRD e Stories | medium | `tests/test_sdd_flow_m05_product.py`; `plugins/sdd-flow/agents/sdd-flow-product/AGENT.md`; `plugins/sdd-flow/skills/sdd-flow-prd/SKILL.md`; `plugins/sdd-flow/skills/sdd-flow-stories/SKILL.md` |
| M05.02 | M05 Task 02 | Roadmap e promoção | medium | `tests/test_sdd_flow_m05_roadmap.py`; `plugins/sdd-flow/skills/sdd-flow-roadmap/SKILL.md`; `plugins/sdd-flow/skills/sdd-flow-promote/SKILL.md`; `plugins/sdd-flow/loops/sdd-flow-product.yaml` |
| M06.01 | M06 Task 01 | Especificação e tarefas | high | `tests/test_sdd_flow_m06_specification.py`; `plugins/sdd-flow/agents/sdd-flow-architect/AGENT.md`; `plugins/sdd-flow/skills/sdd-flow-techspec/SKILL.md`; `plugins/sdd-flow/skills/sdd-flow-tasks/SKILL.md` |
| M06.02 | M06 Task 02 | Loop Feature | high | `tests/test_sdd_flow_m06_feature.py`; `plugins/sdd-flow/loops/sdd-flow-feature.yaml` |
| M07.01 | M07 Task 01 | Procedimento de ambiente | high | `tests/test_sdd_flow_m07_environment.py`; `plugins/sdd-flow/agents/sdd-flow-environment/AGENT.md`; `plugins/sdd-flow/skills/sdd-flow-environment/SKILL.md` |
| M07.02 | M07 Task 02 | Retomada e isolamento | high | `tests/test_sdd_flow_m07_worktree.py`; `plugins/sdd-flow/skills/sdd-flow-environment/SKILL.md`; `plugins/sdd-flow/skills/sdd-flow-promote/SKILL.md` |
| M08.01 | M08 Task 01 | Execute | high | `tests/test_sdd_flow_m08_execute.py`; `plugins/sdd-flow/agents/sdd-flow-implementer/AGENT.md`; `plugins/sdd-flow/skills/sdd-flow-execute/SKILL.md` |
| M08.02 | M08 Task 02 | QA e manifesto | high | `tests/test_sdd_flow_m08_quality.py`; `plugins/sdd-flow/agents/sdd-flow-qa/AGENT.md`; `plugins/sdd-flow/skills/sdd-flow-qa/SKILL.md`; `plugins/sdd-flow/skills/sdd-flow-evidence/SKILL.md` |
| M08.03 | M08 Task 03 | Review | high | `tests/test_sdd_flow_m08_review.py`; `plugins/sdd-flow/agents/sdd-flow-reviewer/AGENT.md`; `plugins/sdd-flow/skills/sdd-flow-review/SKILL.md` |
| M08.04 | M08 Task 04 | Verify | high | `tests/test_sdd_flow_m08_verify.py`; `plugins/sdd-flow/agents/sdd-flow-verifier/AGENT.md`; `plugins/sdd-flow/skills/sdd-flow-verify/SKILL.md` |
| M08.05 | M08 Task 05 | Loop Delivery | high | `tests/test_sdd_flow_m08_delivery.py`; `plugins/sdd-flow/loops/sdd-flow-delivery.yaml` |
| M09.01 | M09 Task 01 | Participação e herança | high | `tests/test_sdd_flow_m09_network.py`; `plugins/sdd-flow/skills/sdd-flow-network/SKILL.md`; `plugins/sdd-flow/agents/sdd-flow-coordinator/AGENT.md`; `plugins/sdd-flow/loops/sdd-flow-delivery.yaml`; `plugins/sdd-flow/skills/sdd-flow-contracts/references/network.md` |
| M10.01 | M10 Task 01 | Exportação e integração final | high | `tests/test_sdd_flow_m10_exports.py`; `plugins/sdd-flow/skills/sdd-flow-evidence-export/SKILL.md`; `plugins/sdd-flow/skills/sdd-flow-contracts/templates/evidence-report.html`; `plugins/sdd-flow/agents/sdd-flow-qa/AGENT.md`; `plugins/sdd-flow/loops/sdd-flow-delivery.yaml` |
| M11.01 | M11 Task 01 | QUICK | high | `tests/test_sdd_flow_m11_quick.py`; `plugins/sdd-flow/skills/sdd-flow-quick/SKILL.md`; `plugins/sdd-flow/loops/sdd-flow-quick.yaml` |
| M11.02 | M11 Task 02 | Status | high | `tests/test_sdd_flow_m11_status.py`; `plugins/sdd-flow/agents/sdd-flow-observer/AGENT.md`; `plugins/sdd-flow/skills/sdd-flow-status/SKILL.md` |
| M12.01 | M12 Task 01 | Matriz final e documentação | high | `tests/test_sdd_flow_m12_acceptance.py`; `plugins/sdd-flow/README.md`; `.planning/power/features/specflow-m12/evidence.md`; `.planning/power/features/specflow-m12/baseline-comparison.json` |
| M12.02 | M12 Task 02 | Pareceres finais | high | `.planning/power/features/specflow-m12/qa.md`; `.planning/power/features/specflow-m12/codereview.md`; `.planning/power/features/specflow-m12/verdict.md`; `.planning/power/features/specflow-m12/feature-closure.md` |

## Verification and release
- Focada: `python3 -m unittest discover -s tests -p 'test_sdd_flow_*.py'`, mais de zero testes e zero falhas.
- Integral: `rg --files tests -g 'test_*.py' | sort | sed 's#/#.#g; s#\.py$##' | xargs python3 -m unittest`; baseline fb14629 precisa ser reproduzido com mesmos sete IDs, tipos e causas. Testes removidos ou falhas trocadas não passam, mesmo com sete ou menos falhas. M12 registra comparação e evidências.
- CLI observado pelo principal: `compozy version` retorna 0.3.0-beta.16; `--version` não é suportado. Help local demonstra apenas sintaxe `compozy extension build [directory] -o json` e `compozy extension validate [directory] -o json`. Depois de recursos existirem e autorização pertinente: `compozy extension build plugins/sdd-flow -o json`; validate recebe exatamente generation_dir retornado pelo build. Nenhum digest/diretório gerado é presumido.
- Nenhum comando mutável de Loop, worktree, decisão ou Network foi qualificado nesta proposta. M01 coleta help/versão e receita, pede gate de escopo e comprova comportamento. Probe BLOCKED até isso ocorrer.
- Release exige todos AT-01–AT-12 e AC-001–AC-016, jornadas reais e gates independentes, especialmente encerramento de Feature, stale/digest, retomada com testes reais, PDF contratado e observer sem efeitos. Contagem de recursos, mocks, build e help isolados não bastam.

## Gate
Revisar PRD, Stories/aplicabilidade, spec e mapa/plano com decisões explícitas separadas. Depois, o primeiro handoff possível é somente M01 aprovado. Os demais módulos ficam bloqueados pela qualificação central e pelas dependências; state.md só muda após decisão conhecida. Rejeição retorna ao artefato que contém a decisão.
