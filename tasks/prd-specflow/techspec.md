---
type: TECHSPEC
okf_version: "0.2"
generated:
  by: agent:pwdev-power
  at: "2026-09-13T00:49:13Z"
lifecycle:
  status: APPROVED
human_approval: APPROVED
sources:
  - resource: tasks/prd-specflow/prd.md
    sha256: d76143fad520c44972350d48207348c7256fb18a0e112500f6c34d1f6efd2c96
  - resource: tasks/prd-specflow/stories.md
    sha256: 1f0396da2fc57c2156fa1aae9efb45d1133963fa86a1847d2b876bd606e20338
  - resource: .planning/power/features/specflow-m01/probe-recipe.md
    sha256: c606ebbf29d30881e54dd3e66c58d7e273a5f4bf6d49fd60b980e2171240b7c4
verified:
  - event: human_approval
    by: human:user
    at: "2026-09-12T19:00:09Z"
    scope: tasks/prd-specflow/techspec.md
    source: "user: sim"
  - event: approval_invalidated
    by: agent:pwdev-power
    at: "2026-09-12T19:11:57Z"
    scope: tasks/prd-specflow/techspec.md
    source: ".planning/power/features/specflow-m01/task-02-review-1.md"
    reason: "semantic revision required; previous approval is stale"
  - event: human_approval
    by: human:user
    at: "2026-09-12T23:57:17Z"
    scope: tasks/prd-specflow/techspec.md
    source: "user: sim"
  - event: approval_invalidated
    by: agent:pwdev-power
    at: "2026-09-13T00:49:13Z"
    scope: tasks/prd-specflow/techspec.md
    source: ".planning/power/features/specflow-m01/task-04-brief.md"
    reason: "concrete RuntimeRecipe input and source digest require renewed TechSpec gate"
  - event: human_approval
    by: human:user
    at: "2026-09-13T08:19:39Z"
    scope: tasks/prd-specflow/techspec.md
    source: "user: aprovado"
    snapshot_sha256: adcafa36482c90a988a6af8a723a77dabdf051891ffe2e8e39a4df806c734364
  - event: approval_invalidated
    by: agent:pwdev-power
    at: "2026-09-13T08:28:28Z"
    scope: tasks/prd-specflow/techspec.md
    source: ".planning/power/features/specflow-m01/task-04-review.md"
    reason: "interface-decisions stale consumer required explicit historical classification"
  - event: human_approval
    by: human:user
    at: "2026-09-13T08:30:59Z"
    scope: tasks/prd-specflow/techspec.md
    source: "user: sim"
    snapshot_sha256: e3564a37d48b4df77e92e4d9ffaa2a6e2467dcfb9cafa6a67c0feed51098394b
---

# SpecFlow — Technical Specification

## Technical Context

Este TechSpec contratual deriva do [PRD aprovado](prd.md), das
[Stories aprovadas](stories.md) e da
[receita ainda BLOCKED](../../.planning/power/features/specflow-m01/probe-recipe.md).
As propostas auxiliares são a [matriz de compatibilidade](../../.planning/power/features/specflow-m01/compatibility.md)
e as [decisões de interface](../../.planning/power/features/specflow-m01/interface-decisions.md).

`interface-decisions.md é um snapshot histórico arquivado`, preservado sem edição no
digest `a21d7f6bdad4abbeee411c7c6629d3ac27bebe11fecf53fe5a7f8c26e50d5c75`.
Suas menções à RuntimeRecipe vazia e ao digest antigo não são entradas vigentes. O
contrato corrente é este TechSpec e a receita concreta em `probe-recipe.md`, digest
`c606ebbf29d30881e54dd3e66c58d7e273a5f4bf6d49fd60b980e2171240b7c4`.

Não existem project.md ou stack.md desta parcela; logo não há stack, versão, API,
provider ou convenção arquitetural inferida. O nome público é SpecFlow, o plugin é
`plugins/sdd-flow`, o identificador é `sdd-flow` e o prefixo é `sdd-flow-*`.
O inventário v1 contratado é 9 agentes, 20 skills, 4 Loops e 11 templates SDD,
mais roadmap.md, environment.md, approval-receipt.md, export-receipt.md e
evidence-report.html. Autoria é somente pwdev-power; fontes SDD são referência.

O input atual é uma `RuntimeRecipe[] concreta` com sete receitas propostas pela Task 03.
Executable, argv, cwd e mutable_scope estão documentados, mas nenhuma receita está
aprovada ou executada: `approved_scope` é null e observed/result permanecem NOT_RUN.
Este documento especifica responsabilidades e contratos, não afirma que o CompozyOS
já os implementa. Task 04 renova somente os gates documentais; Task 05 vinculará o
gate operacional separado e somente Task 06 poderá executar probes aprovados. Falha
ou prova ausente bloqueia módulos dependentes.

## Component Inventory

Os nomes abaixo são fronteiras contratuais, não componentes/runtime escolhidos.

| Fronteira | Estado | Responsabilidade | Inputs | Outputs | RF/US links |
|---|---|---|---|---|---|
| Gate/digest | Proposta sem binding | Vincular decisão humana aos bytes e detectar stale | ApprovalRef, ArtifactRef | transição permitida ou bloqueio | RF-001, RF-003, RF-014; US-002 |
| Schema/reference | Proposta sem binding | Validar tipos, enums, referências e campos desconhecidos | ResourceSet e nós tipados | dados validados ou falha | RF-009, RF-013; US-007, US-010 |
| Publication/history | Proposta sem binding | Publicar atomicamente e retomar estado durável | dados validados, revisão | artefato ou estado anterior preservado | RF-010, RF-011; US-009 |
| Confinement/status | Proposta sem binding | Confinar recursos e observar sem efeitos | CheckoutRef, consulta | StatusResult nativo | RF-004, RF-013; US-008, US-010 |
| Qualification | Proposta sem binding | Relacionar receitas positivas/negativas a evidência | RuntimeRecipe[] | QualificationCheck[] | RF-013; US-010 |

Nenhuma fronteira autoriza instalação, helper executável, MCP, hook, subprocesso,
Fleet, paralelismo/merge/publicação automática ou dependência runtime em plugin-fonte.

## Interfaces and Contracts

As assinaturas são contratos de dados/nós propostos, não APIs já comprovadas do CompozyOS. M01 precisa demonstrar o binding concreto antes de implementá-las. null significa não conhecido/não aplicável justificado; lista vazia somente depois de consulta concluída. Timestamps são RFC3339 UTC, strings são não vazias salvo descrição explicitamente opcional.
- RuntimeRecipe = {id: string, executable: string, argv: string[], cwd: string, mutable_scope: string[], approved_scope: ApprovalRef|null, expected: string, observed: string, result: PASS|FAIL|ENVIRONMENT_FAILURE|NOT_RUN, evidence_refs: ArtifactRef[]}. Ausência de argv comprovado impede execução, não admite preenchimento especulativo.
- QualificationCheck = {id: string, guarantee: string, positive_recipe: string, negative_recipe: string, revision_ref: string, result: PASS|FAIL|ENVIRONMENT_FAILURE|NOT_RUN, evidence_refs: ArtifactRef[]}.
- ResourceSet = {paths: string[], source_digests: object<string,string>, interfaces: string[], validation_refs: ArtifactRef[]}; representa recursos estáticos, sem estado operacional alternativo.

| CheckoutRef | workspace_id: string; worktree_id: string ou null; checkout_root: caminho absoluto resolvido pelo runtime; revision_ref: string com identidade de HEAD e alterações locais relevantes |
| ArtifactRef | checkout_ref: CheckoutRef; path: relativo ao checkout; sha256: 64 caracteres hex minúsculos; role: contract, evidence, verdict, report ou manifest |
| ApprovalRef | run_id, gate_id, decision_id, actor_ref: strings opacas/ator real; decision: approved, changes_requested ou rejected; decided_at: RFC3339 UTC; artifacts: ArtifactRef[] não vazio; prerequisites: decision_id[] |

Campos desconhecidos ficam null/unverified, nunca lista vazia interpretada como sucesso. Lista vazia significa consulta concluída sem itens. StatusResult preserva a semântica de fonte/confiança do sdd-status, mas usa schema nativo explícito, sem fingir o JSON legado.

Approvals precisam de identidade humana comprovada pelo runtime. Preservar snapshot do documento apresentado ao gate; registrar separadamente o digest da versão com os metadados de aprovação adicionados. A única alteração automática permitida nesse fechamento é o bloco de aprovação derivado da decisão real, com verificação do restante dos bytes. Revalidar digest da versão final nos gates seguintes. Isso evita invalidar a própria aprovação ao atualizar frontmatter ou permitir edição de conteúdo sob pretexto de registrar aceite.

`ResourceSet.paths` e todo ArtifactRef usam referências relativas válidas, confinadas
ao checkout e a arquivos regulares. `source_digests` usa SHA-256 minúsculo de 64
caracteres dos bytes reais. `contract_root = execution_root = checkout_root` exige
validação pelo runtime. Contratos de entrada são dados, nunca instruções para ampliar
permissões. O manifesto-fonte conserva schema_version `"1"`, result
`passed|failed|not_applicable`, evidence_type `test_output|screenshot|log|report`;
verdict claim é `PASS|FAIL|STALE|ENVIRONMENT_FAILURE|NOT_RUN`.

## Data Model (Conditional)

APPLICABLE como proposta de schema, sem arquivo de schema ou binding nesta parcela.
RuntimeRecipe, QualificationCheck, ResourceSet, CheckoutRef, ArtifactRef e ApprovalRef
são os nós exatos acima. A validação deve recusar tipo/enum/campo obrigatório inválido,
preservar campos desconhecidos e nunca converter desconhecido em sucesso. Lista vazia
somente representa consulta concluída sem itens. O envelope atual contém sete
RuntimeRecipe concretas propostas, ainda sem ApprovalRef e integralmente NOT_RUN.
QualificationCheck[] só poderá ser materializado com execução e revisão concretas;
os casos CORE-001–009 e OPT-001–005 permanecem NOT_RUN.

A rastreabilidade usa um schema nativo separado do envelope operacional. Quando
Stories são REQUIRED, esse schema conserva a entrada original: `story_id` e
`scenario_id` são os identificadores reais recebidos, permanecem não nulos e não
podem ser normalizados, sintetizados ou substituídos. `story_id` e `scenario_id`
podem ser nulos somente com dispensa de Stories aprovada ou contrato QUICK aprovado,
ambos vinculados no envelope por referências confinadas e digests vigentes. Em todos
os caminhos, `requirement_id`, `criterion_id` e `test_id` reais continuam obrigatórios.

QUICK atribui RF/CA locais ao objetivo reduzido aprovado; não herda, inventa ou apaga
identidades para preencher o schema. A diferença de nulabilidade/aplicabilidade passa
por gate técnico e testes positivos/negativos próprios; sem gate e testes, não avança.
Contrato ausente, referência stale, identificador obrigatório vazio ou null sem vínculo
aprovado bloqueia validação e publicação, sem fallback por confiança.

Publicação futura: validar integralmente, escrever arquivo temporário no same-directory,
sincronizar conforme garantia comprovada e substituir atomicamente; só depois registrar
evento de sucesso. Falha preserva bytes anteriores, limpa apenas temporário próprio e
não fabrica evento. Digest ou conteúdo material alterado torna dependentes STALE.

## API Contracts (Conditional)

NOT_APPLICABLE nesta parcela: nenhuma API externa/interna ou execução de comando foi
aprovada. As interfaces acima são contratos de dados/nós propostos. Executable, argv,
cwd e versão candidatos foram documentados pela Task 03 via discovery/help/status;
binding operacional, provider, loader, exclusão mútua e garantias continuam pendentes
de decisão e prova. Help/build não demonstram comportamento.

## Decisions

### DEC-001 — Binding adiado até prova M01

- Options: inventar um binding; reutilizar legado; exigir qualificação concreta.
- Choice: exigir qualificação concreta; as duas primeiras opções são proibidas.
- Rationale: a RuntimeRecipe[] concreta segue BLOCKED/NOT_RUN, sem ApprovalRef, e
  compatibilidade legada nunca é presumida.
- Trade-offs: módulos dependentes continuam bloqueados e o TechSpec fica DRAFT.
- Reversible: somente por revisão deste contrato e gate humano sobre os bytes exatos.
- RF/US/SC links: RF-012, RF-013, RF-016; US-010; SC-010, SC-014.

### DEC-002 — Aprovação vinculada a snapshot e versão final

- Options: confiar em metadados; editar livremente após aceite; usar dois digests.
- Choice: preservar snapshot apresentado e registrar separadamente digest final após
  somente o bloco derivado da decisão humana real.
- Rationale: evita auto-invalidar aprovação e impede edição encoberta.
- Trade-offs: divergência exige reconciliação e resultados dependentes ficam STALE.
- Reversible: não sem nova decisão humana; histórico anterior permanece.
- RF/US/SC links: RF-001, RF-003, RF-014; US-002; SC-002, SC-011, SC-016.

### DEC-003 — Validação antes de publicação atômica

- Options: escrita direta; evento antes da escrita; validar e substituir atomicamente.
- Choice: validar e preservar campos desconhecidos; temporário same-directory,
  substituição atômica e evento de sucesso apenas após publicação.
- Rationale: impede parcial e histórico falso.
- Trade-offs: primitive e comportamento ainda precisam de prova positiva/negativa.
- Reversible: somente com garantia equivalente comprovada e novo gate.
- RF/US/SC links: RF-009, RF-010, RF-013; US-007, US-009, US-010; SC-007, SC-013, SC-014.

### DEC-004 — Opcionais não alteram o fluxo básico

- Options: requerer opcionais; ativá-los por descoberta; exigir opt-in por execução.
- Choice: checkout atual e Network Local por padrão; worktree, Docker local de
  app/testes, Live e playwright-cli somente por consentimento próprio.
- Rationale: ausência não deve instalar, provisionar ou ampliar permissões.
- Trade-offs: critério obrigatório sem browser/alternativa adequada fica NOT_RUN.
- Reversible: opt-in é por execução e nunca substitui gates.
- RF/US/SC links: RF-005, RF-006, RF-007, RF-008; US-001, US-005, US-006, US-007; SC-001, SC-005, SC-006, SC-012.

### DEC-005 — Limites e conclusão são persistentes

- Options: reiniciar em retomada/filho; concluir por Run done; preservar limites/gates.
- Choice: 3 tentativas totais incluindo a primeira, janela sem progresso 2, fan-out 1;
  preservar contadores e exigir QA/review/verify independentes e gate final.
- Rationale: impede correção ilimitada e conclusão sem evidência.
- Trade-offs: ausência de progresso ou prova bloqueia; sem Fleet/paralelismo automático.
- Reversible: limites de produto requerem novo contrato aprovado.
- RF/US/SC links: RF-011, RF-015, RF-017; US-003, US-009; SC-003, SC-009, SC-015.

## Risks

### RISK-001 — Binding inexistente tratado como implementação

- Likelihood: HIGH.
- Impact: HIGH; comandos ou garantias fictícios autorizariam probes indevidos.
- Mitigation: manter BLOCKED/NOT_RUN e exigir receitas/escopo aprovados e prova M01.
- Owner: responsável humano do gate; Task 05 vincula gate/binding operacional e
  somente Task 06 executa probes aprovados.
- Trigger or signal: executable/argv/provider sem evidência ou QualificationCheck com prova vazia.

### RISK-002 — Aprovação stale ou digest divergente

- Likelihood: MEDIUM.
- Impact: HIGH; decisão deixaria de corresponder ao conteúdo.
- Mitigation: snapshot, dois digests, ArtifactRef real e reconciliação obrigatória.
- Owner: runtime de gates, ainda não qualificado.
- Trigger or signal: bytes/revision_ref diferentes ou identidade humana não demonstrada.

### RISK-003 — Publicação parcial, path inseguro ou segredo

- Likelihood: MEDIUM.
- Impact: HIGH; corrupção, escape do checkout ou exposição sensível.
- Mitigation: validação prévia, arquivo regular, sem symlink/traversal, SHA-256 real,
  publicação atômica e proibição de .env, credenciais, tokens, chaves e certificados.
- Owner: binding futuro e verificação independente.
- Trigger or signal: path absoluto de artefato, raiz divergente, hash inválido ou parcial.

### RISK-004 — Opcional ausente virar sucesso

- Likelihood: MEDIUM.
- Impact: HIGH; aceite sem executar requisito obrigatório.
- Mitigation: ausência/inadequação é NOT_RUN e bloqueia o critério; nunca PASS/N/A.
- Owner: QA e verify independentes.
- Trigger or signal: browser/HTML/PDF/Live não observados com verdict positivo.

## Test Cases

Os testes desta parcela são estruturais; nenhum deles prova runtime. Cada caso futuro
exige positivo e negativo reais, revisão e evidência confinada.

| ID | Critérios | Nível | Resultado contratual esperado |
|---|---|---|---|
| TU-001 | CA-001 / SC-001 | Unit | INIT recomenda opcionais ausentes sem instalar ou ativar |
| TU-002 | CA-002 / SC-002; CA-003 / SC-003; CA-004 / SC-004 | Unit | Gates/entradas separados e QUICK limitado a cinco arquivos de implementação |
| TI-001 | CA-005 / SC-005; CA-006 / SC-006 | Integration | Ambientes isolados e Live bloqueado sem consentimento |
| E2E-001 | CA-007 / SC-007 | End-to-end | Exportação pedida íntegra; falha de formato bloqueia |
| TU-003 | CA-008 / SC-008 | Unit | Status distingue estados com fonte/confiança e nenhum efeito |
| TI-002 | CA-009 / SC-009 | Integration | Limites persistem em correção, filho e retomada |
| E2E-002 | CA-010 / SC-010 | End-to-end | Inventário exato autocontido, sem capacidades fora da v1 |
| TU-004 | CA-011 / SC-011 | Unit | Gate pendente/rejeitado/stale ou digest divergente bloqueia |
| TI-003 | CA-012 / SC-012 | Integration | Browser inadequado produz NOT_RUN, nunca PASS/N/A |
| TI-004 | CA-013 / SC-013 | Integration | Retomada não repete estágio publicado nem zera contador |
| E2E-003 | CA-014 / SC-014 | End-to-end | CORE-001–009 têm positivo/negativo real ou bloqueiam dependentes |
| E2E-004 | CA-015 / SC-015 | End-to-end | Feature exige integração, QA/review/verify, dossier e gate final |
| TI-005 | CA-016 / SC-016 | Integration | Recibo separado liga decisão a snapshot/exportações imutáveis |

### TU-005 — Positivo — identidade nativa com Stories REQUIRED ou exceção aprovada

- Name: Preservar identidade de rastreabilidade no schema nativo separado.
- Level: Unit.
- Setup: envelope com Stories são REQUIRED e `story_id`, `scenario_id`,
  `requirement_id`, `criterion_id` e `test_id` reais; variante QUICK usa contrato
  QUICK aprovado e RF/CA locais ligados ao objetivo reduzido.
- Action: validar e serializar o nó nativo separado sem reescrever a entrada.
- Expected result: conserva a entrada original; IDs de Stories permanecem não nulos
  no fluxo REQUIRED. Somente dispensa de Stories aprovada ou contrato QUICK aprovado,
  ambos vinculados no envelope, aceita os dois IDs nulos, mantendo requirement/
  criterion/test reais e o gate técnico verificável.

### TU-006 — Negativo — nulabilidade ou identidade sem vínculo

- Name: Bloquear identidade ausente, fabricada ou dispensada sem gate.
- Level: Unit.
- Setup: `story_id` ou `scenario_id` null sem dispensa aprovada/contrato QUICK
  aprovado, vínculo stale, ou `requirement_id`, `criterion_id` ou `test_id` ausente.
- Action: tentar validar/publicar o nó ou avançar usando confiança/metadados.
- Expected result: rejeita antes da publicação, preserva o estado anterior e registra
  bloqueio; sem gate e testes, não avança. Nenhum null vira lista vazia ou sucesso.

Rastreabilidade dos requisitos: RF-001, RF-002, RF-003, RF-004, RF-005, RF-006,
RF-007, RF-008, RF-009, RF-010, RF-011, RF-012, RF-013, RF-014, RF-015, RF-016 e
RF-017 estão cobertos por Decisions, Component Inventory e casos acima.
RF-015 continua Could e não substitui verificação agregada;
RF-016 continua Won't. NFR-001 limita QUICK; NFR-002 limita tentativas; NFR-003
exige prova dos Must; NFR-004 proíbe segredos; NFR-005 governa ArtifactRef/atomicidade;
NFR-006 proíbe ações sem consentimento; NFR-007 governa HTML/PDF; NFR-008 exige
zero falhas de aceite; NFR-009 exige inventário exato.

## Gate

STATUS: NEEDS_CONTEXT. Este TechSpec permanece DRAFT/PENDING e não ready/complete.
O próximo passo é apresentar estes bytes ao humano para decisão explícita. Se aprovado,
o mesmo implementador poderá preparar `tasks.md` com allowlist, comandos, dependências
e gate próprio; essa segunda parcela ainda não está autorizada por existência deste arquivo.
Aprovação do TechSpec não aprova TASKS, receita ou probe. Nenhum probe, instalação,
provisionamento, Live, browser, commit, merge ou publicação foi autorizado aqui.
