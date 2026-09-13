# Power ledger — plan: .planning/power/features/specflow-m01/plan.md

Created: 2026-09-12T10:36:05Z

## Progress

Task 05: correction round 1 aguarda Emenda 04 DRAFT/PENDING — review SPEC FAIL / QUALITY FAIL confirmou 2 Important: ArtifactRef não resolve o snapshot pré-aprovação e testes não recomputam/rejeitam adulteração do recibo. A Task 05 tem quatro arquivos e precisa de um quinto snapshot regular endereçável antes da correção.

Task 05: minor (deferred): relatório e documentos auxiliares ainda contêm narrativa pré-binding (`approved_scope: null`/sem ApprovalRef) ao lado do recibo materializado; reconciliar redação sem reescrever snapshots históricos em etapa permitida.

M01 plan: amendment 03 aprovada pelo humano em 2026-09-13T08:53:00Z; Task 05 passa a produzir ApprovalRef pré-Run determinístico e reproduzível, distinto dos IDs reais de Loop que somente Task 06 observará. Nenhum probe foi autorizado por esta aprovação.

M01 plan: amendment 03 DRAFT/PENDING — corrige o ciclo em que Task 05 exigia Loop Run IDs antes de Task 06 poder criar o Run. Propõe ApprovalRef pré-Run com IDs determinísticos e reproduzíveis derivados do gate Power humano e snapshot real; Task 06 continua bloqueada até aprovação e revisão.

Task 05: BLOCKED após aprovação humana do preview em 2026-09-13T08:39:37Z; `whoami --json` não demonstra identidade e não existem `run_id`, `gate_id`, `decision_id` ou ArtifactRef operacionais reais para compor ApprovalRef. Preservar `approved_scope: null`, `NOT_RUN` e não executar Task 06 até que o runtime forneça esses dados verificáveis.

Task 04: complete (snapshot `fb14629`, correction round 1, re-review SPEC PASS / QUALITY PASS; TechSpec e TASKS aprovados com snapshots preservados; 31 testes OK; sem probes).

Task 04: correction round 1 aberta em 2026-09-13T08:27:00Z após review SPEC FAIL / QUALITY FAIL — 1 Important confirmado: a suíte removeu `interface-decisions.md` da cobertura e ocultou seu digest/RuntimeRecipe stale. O arquivo está fora da allowlist; a correção deve classificar explicitamente o snapshot no TechSpec permitido, restaurar teste de cobertura e renovar o gate do TechSpec.

Task 04: TechSpec reconciliado aprovado pelo humano em 2026-09-13T08:19:39Z; snapshot pré-gate `adcafa36482c90a988a6af8a723a77dabdf051891ffe2e8e39a4df806c734364`. Retomada do mesmo implementador autorizada somente para registrar o fechamento derivado, reconciliar o digest dependente e apresentar TASKS ao gate próprio; aprovação operacional e probes permanecem bloqueados.

Task 03: complete (snapshot `fb14629`, correction round 1, re-review SPEC PASS / QUALITY PASS em 2026-09-13T00:47:00Z; 6 testes focados OK; suíte combinada preserva exatamente 6 falhas stale atribuídas à Task 04; sem probes).

Task 03: correction round 1 aberta em 2026-09-13T00:44:00Z após review SPEC FAIL / QUALITY FAIL — 2 Important confirmados: handoff operacional ainda aponta à Task 04 em vez de separar Tasks 04/05/06, e testes focados não exercitam casos negativos reais. O Minor sobre alegação de outputs integrais foi deferido para correção de redação no relatório; nenhum probe é necessário.

Task 03: minor (deferred): o relatório afirma que outputs integrais estão em runtime-command-qualification.md, mas o artefato preserva somente resumos e hashes; corrigir a alegação sem reexecutar comandos.

M01 plan: amendment 02 aprovada pelo humano em 2026-09-13T00:34:42Z; plano, mapa e traceabilidade agora têm sete tasks. Task 03 pode encerrar com suíte focada verde e seis consumidores stale explicitamente transferidos à Task 04; nenhuma mutação operacional autorizada.

Task 03: NEEDS_PLAN_FIX — 5 testes focados OK, mas suíte combinada reproduziu 6 falhas stale novas causadas por consumidores fora da allowlist da Amendment 01; nenhum probe ocorreu. Amendment 02 DRAFT/PENDING propõe reconciliação em tarefas separadas antes de qualquer gate operacional.

M01 plan: amendment 01 aprovada pelo humano em 2026-09-13T00:13:19Z; plano M01 agora tem cinco tasks, mapa/traceabilidade reconciliados e TASKS anterior invalidado como stale. Liberada somente a nova Task 03 de qualificação read-only; nenhuma mutação operacional autorizada.

M01 plan: amendment 01 DRAFT/PENDING — propõe nova Task 03 somente leitura para qualificar comandos e preparar RuntimeRecipe concreta antes dos probes; aguarda gate humano e não autoriza daemon, links, Runs ou qualquer mutação.

Task 02: complete (snapshot `fb14629`, review Important ADDRESSED, final gate chain PASS em 2026-09-13T00:07:36Z; 14 testes focados e 46 com suítes adjacentes OK; 2 minors deferred; sem probes).

Task 02: TASKS reconciliado aprovado novamente pelo humano em 2026-09-13T00:02:44Z; snapshot pré-gate `62e84e21284a77aa80fff6d827fc9e39e38b7f690861b342e07f38d820fc2332`; retomada autorizada apenas para reconciliar o gate, verificar e encerrar a tarefa, sem liberar Task 03/probes.

Task 02: NEEDS_CONTEXT em 2026-09-13T00:01:40Z — TechSpec corrigido APPROVED, TASKS reconciliado DRAFT/PENDING com digest `a952198143a3f8b9a97e88331a2fd7bc048c7117a00babcf67025c42cccfd88c`; 13 testes focados e 45 com suítes adjacentes OK; aguardando novo gate humano de TASKS, sem probes.

Task 02: TechSpec corrigido aprovado novamente pelo humano em 2026-09-12T23:57:17Z; snapshot pré-gate `f047d562a41062daf1003d363d49cd130ade8d9430fb9b7a9ad943085afbb633`; retomada autorizada somente para reconciliar digest/testes de TASKS e apresentar seu novo gate, sem probes.

Task 02: correction round 1 re-review em 2026-09-12T19:16:57Z — Important ADDRESSED, nenhuma regressão no escopo, 44 testes focados/adjacentes OK; aguardando novo gate humano do TechSpec revisado. TASKS permanece DRAFT/PENDING stale e probes bloqueados.

Task 02: correction round 1 aberta em 2026-09-12T19:10:48Z após review SPEC FAIL / QUALITY FAIL — 1 Important confirmado; TechSpec e TASKS devem voltar a DRAFT/PENDING porque a correção semântica invalida os gates anteriores. Nenhum probe liberado.

Task 02: minor (deferred): IDs DEC-004/DEC-005 têm significados diferentes entre TechSpec e interface-decisions; definir correspondência explícita ou IDs distintos em reconciliação futura.

Task 02: minor (deferred): corpos de TechSpec/TASKS ainda narram gates pendentes apesar dos frontmatters então aprovados; preservar snapshots e reconciliar orientação por registro controlado quando os contratos forem reabertos/atualizados.

Task 02: TASKS aprovado pelo humano em 2026-09-12T19:05:36Z; somente o bloco de aprovação derivado foi atualizado; retomada do mesmo implementador autorizada para reconciliar o gate, validar e encerrar antes da revisão independente, sem probes.

Task 02: NEEDS_CONTEXT em 2026-09-12T19:04:28Z — `tasks.md` DRAFT/PENDING com TASK-002 pending e allowlist de cinco caminhos; verificação independente fresca com 9 testes focados e 41 com suítes adjacentes OK; aguardando gate humano de TASKS, sem receita executável ou probes.

Task 02: TechSpec aprovado pelo humano em 2026-09-12T19:00:09Z; somente o bloco de aprovação derivado foi atualizado, preservando os demais bytes do snapshot; retomada autorizada para preparar `tasks.md` DRAFT/PENDING, sem probes.

Task 02: NEEDS_CONTEXT em 2026-09-12T18:59:15Z — TechSpec DRAFT/PENDING, compatibility e interface-decisions BLOCKED/NOT_RUN, `tasks.md` ausente; verificação independente fresca com 8 testes focados e 40 com suítes adjacentes OK; aguardando gate humano do TechSpec, sem probes.

Task 01: complete (snapshot `fb14629`, review SPEC PASS / QUALITY PASS em 2026-09-12T18:49:03Z; 10 testes focados e 32 com suíte adjacente OK; sem probes).

Task 01: minor (deferred): `.planning/power/features/specflow-m01/probe-recipe.md` ainda diz para aguardar o gate de Stories já aprovado; reconciliar quando a receita for atualizada pelos gates técnicos/operacionais, preservando BLOCKED até lá.

Task 01: Stories/aplicabilidade aprovadas pelo humano em 2026-09-12T18:43:31Z; retomada do mesmo implementador autorizada somente para reconciliar o gate, validar e encerrar a tarefa antes da revisão independente.

Task 01: NEEDS_CONTEXT em 2026-09-12T18:41:30Z — Stories REQUIRED em DRAFT/PENDING; matriz integralmente NOT_RUN e receita BLOCKED; verificação independente fresca com 31 testes OK; aguardando gate humano das Stories, sem probes.

Task 01: PRD aprovado pelo humano em 2026-09-12T11:28:23Z; retomada autorizada para Stories/aplicabilidade e preparação da receita, sem probes.

Task 01: partial — PRD contratual criado em DRAFT/PENDING; 5 testes focados e 27 testes com suíte adjacente passaram; aguardando gate humano antes de Stories e receita.

### Pre-flight scan

| Tasks | Shared file/interface | Producer / consumer agreement |
|---|---|---|
| 01 / 02 | `RuntimeRecipe[]`; gates de PRD/Stories | Task 01 produz a receita e os contratos de produto; Task 02 só consome depois dos gates humanos correspondentes |
| 01 / 03 | `probe-recipe.md`; `runtime-qualification.md`; `RuntimeRecipe[]` | Task 03 transforma somente a proposta vazia da Task 01 em receitas concretas ainda NOT_RUN, preservando IDs, gates e histórico |
| 01 / 04 | `tests/test_sdd_flow_m01_qualification.py`; `probe-recipe.md` | Task 04 atualiza expectativas/digests stale da Task 01 para a receita concreta sem atribuir PASS |
| 01 / 07 | `tests/test_sdd_flow_m01_qualification.py`; `runtime-qualification.md` | Task 07 reconcilia e fecha as provas iniciadas pela Task 01 sem trocar identificadores |
| 02 / 03 | `tasks.md`; `QualificationCheck[]` | Task 03 reabre o escopo stale, adiciona seu contrato e consome os checks propostos pela Task 02 sem atribuir PASS |
| 02 / 04 | `tests/test_sdd_flow_m01_contracts.py`; `compatibility.md`; `techspec.md`; `tasks.md` | Task 04 reconcilia os consumidores da Task 02, preserva histórico e renova TechSpec/TASKS |
| 02 / 07 | `compatibility.md`; `interface-decisions.md` | Task 07 atualiza a matriz e decisões da Task 02 com observações reais da Task 06 |
| 03 / 04 | `RuntimeRecipe[]` concreto; testes e digests stale | Task 04 torna todos os consumidores coerentes e a suíte combinada verde antes dos gates |
| 03 / 05 | `probe-recipe.md`; `runtime-qualification.md`; ApprovalRef | Task 05 vincula a decisão operacional real sem executar receitas nem promover checks |
| 03 / 06 | `RuntimeRecipe[]` concreto | Task 06 executa somente receitas qualificadas e autorizadas da Task 05 |
| 04 / 05 | TechSpec/TASKS vigentes; escopo de sete tasks | Task 05 exige ambos os gates renovados antes de apresentar o gate operacional |
| 04 / 06 | TechSpec/TASKS e consumidores reconciliados | Task 06 recusa qualquer digest stale antes do probe |
| 05 / 06 | `RuntimeRecipe[]` com ApprovalRef | Task 06 consome somente aprovação real/fresca e escopo/budgets/cleanup exatos |
| 05 / 07 | `runtime-qualification.md`; qualificação de comandos | Task 07 distingue descoberta/approval de prova comportamental produzida pela Task 06 |
| 06 / 07 | `RuntimeQualification` | Task 06 produz o resultado observado; Task 07 exige todos os `core_checks` em `PASS` antes do gate técnico |

| Task | Self-consistency |
|---|---|
| 01 | Cinco arquivos, comandos nomeados, PRD antes de Stories e nenhum probe mutável antes da autorização |
| 02 | Cinco arquivos, consome a receita da Task 01 e preserva gates distintos de TechSpec e TASKS |
| 03 | Cinco arquivos, somente descoberta read-only; produz receita concreta NOT_RUN e transfere seis consumidores stale explícitos |
| 04 | Cinco arquivos, reconcilia exatamente os consumidores stale, deixa suíte combinada verde e renova TechSpec/TASKS sem probe |
| 05 | Cinco arquivos após a Emenda 04 aprovada, incluindo snapshot endereçável; obtém/binda gate operacional separado, mantém resultados NOT_RUN e bloqueia se identidade não for comprovada |
| 06 | Cinco arquivos, depende de contratos aprovados, receita concreta e escopo mutável autorizado |
| 07 | Quatro arquivos, consome `RuntimeQualification` e bloqueia M02 diante de `NOT_RUN`, falha ou garantia central ausente |

## Rulings

Task 05: Emenda 04 aprovada pelo humano em 2026-09-13T09:21:33Z (`user: sim`); autorizada a correção round 1 com quinto arquivo de snapshot endereçável e testes adversariais, sem autorizar probes da Task 06.

Task 05: correction round 1 incompleta — verificação do controller encontrou edição parcial: cinco dos sete ArtifactRef ainda estavam stale e o teste não havia mudado. Após retomada, os sete paths foram corrigidos e a suíte passou com 32 testes, mas o novo teste somente valida o documento vigente e ainda não demonstra rejeição das mutações exigidas; abrir correction round 2 antes da re-review.

Task 05: correction round 2 re-review em 2026-09-13 — Important 1 ADDRESSED; Important 2 NOT ADDRESSED. O recibo não contém o decision record canônico completo, e os casos negativos não isolam prerequisites invertidos nem digest alterado. Finding confirmado como real e load-bearing; abrir correction round 3 no mesmo implementador, sem probes.

Task 05: complete (snapshot `fb14629`, correction round 3 review clean em 2026-09-13T09:32:36Z; SPEC PASS / QUALITY PASS; 33 testes combinados e `git diff --check` OK; sem probes ou commits).

Task 06: execução dos probes explicitamente autorizada pelo humano em 2026-09-13T09:34:07Z (`user: sim`), restrita às sete RuntimeRecipe aprovadas, aos cinco arquivos da allowlist e ao escopo mutável declarado; Docker, browser, Live, instalação, publicação e cleanup não foram autorizados.

Task 06: BLOCKED no preflight em 2026-09-13T09:35:41Z, antes de RED ou probe — argv/allowlist divergentes, `run-config.yaml` ausente do escopo e versão observada beta.25 diferente da beta.16 aprovada. Consulta read-only fora do sandbox em 2026-09-13T09:36:40Z confirmou daemon saudável/Network Local ready; erro de socket no sandbox era ambiental, mas não remove os bloqueios contratuais.

Ruling: A Task 06 deve ser separada em preparação estática/read-only e a Task 07 deve concentrar execução/reconciliação após um novo ApprovalRef sobre fixtures, argv e versão finais, conforme Emenda 05; a autorização anterior é stale e não pode ser ampliada. Se esta decisão estiver errada, o custo é um gate humano adicional e reorganização das duas tarefas; sem ela, seria necessário violar a allowlist ou executar bytes não aprovados.

Task 06: Emenda 05 aprovada pelo humano em 2026-09-13T09:38:38Z (`user: sim`); autorizada somente preparação estática/read-only dos cinco arquivos corrigidos. Probes mutáveis permanecem bloqueados até novo gate sobre hashes finais.

Task 06: NEEDS_CONTEXT após revisão independente clean — SPEC PASS / QUALITY PASS, 39 testes combinados e `git diff --check` OK; preview operacional beta.25 materializado em `task-06-operational-gate.md`, aguardando decisão humana sem probes.

Task 06: complete (snapshot `fb14629`, review clean; gate operacional beta.25 aprovado pelo humano em 2026-09-13T09:52:10Z; 39 testes combinados OK; nenhum probe executado).

Ruling: O ApprovalRef renovado usa os registros UTF-8/LF `specflow.power-probe-run.v1` e `specflow.power-probe-decision.v1`, vinculando revisão, versão beta.25, digest do preview e digest do gate pré-aprovação; IDs Power permanecem separados dos futuros IDs Loop. Se esta decisão estiver errada, o custo é renovar o gate e refazer a Task 07; sem determinismo, a autorização não seria verificável.

Ruling: O ArtifactRef da aprovação deve resolver diretamente para `.planning/power/features/specflow-m01/probe-recipe-approved-snapshot.md`, arquivo regular com os bytes pré-aprovação e SHA-256 `c606ebbf29d30881e54dd3e66c58d7e273a5f4bf6d49fd60b980e2171240b7c4`; o recibo atual permanece em `probe-recipe.md`. Se esta decisão estiver errada, o custo é manter um quinto artefato contratual e ajustar consumidores; sem ela, a prova por path/digest permanece inválida.

Ruling: A serialização do ApprovalRef pré-Run usa registros UTF-8/LF ordenados e valores fixados na Emenda 03 aprovada; `run_id`/`decision_id` são hashes reproduzíveis, e prerequisites referenciam digests finais dos gates TechSpec/TASKS. Se esta decisão estiver errada, o custo é renovar a emenda e o gate antes de Task 06; sem ela, cada implementador poderia produzir identidades incompatíveis.

Ruling: As seis falhas combinadas da Task 03 são stale legítimas introduzidas pela mudança aprovada de RuntimeRecipe/TASKS e não podem ser aceitas como baseline; como seus consumidores excedem a allowlist de cinco arquivos, o plano precisa de duas tarefas adicionais antes do probe. Se esta decisão estiver errada, o custo é mais gates e coordenação; avançar sem ela ocultaria regressões e usaria contratos divergentes.

Ruling: `task-brief.sh` também omitiu os tipos transitivos da nova Task 03; o controller anexou ao brief as nove cláusulas exatas já validadas para RuntimeRecipe, QualificationCheck, ResourceSet, CheckoutRef, ArtifactRef, ApprovalRef e invariantes. Se esta decisão estiver errada, o brief falhará na revisão antes de qualquer probe, e deverá ser regenerado sem promover os gates.

Ruling: Task 03 não pode ser despachada enquanto `probe-recipe.md` mantiver RuntimeRecipe[] vazio e não houver comando qualificado nem ApprovalRef do escopo mutável; os gates de PRD/Stories/TechSpec/TASKS não substituem essas condições. Se esta decisão estiver errada, a execução fica conservadoramente atrasada; o custo de avançar sem ela seria probe não autorizado e evidência inválida.

Ruling: O finding Important da revisão é real e load-bearing: a Task 02 deve especificar Stories NOT_APPLICABLE/QUICK com identidade nativa, IDs US/SC nulos somente sob dispensa/contrato aprovado, RF/CA/teste obrigatórios e casos positivos/negativos; como isso muda semântica já aprovada, TechSpec e TASKS voltam a DRAFT/PENDING preservando os eventos históricos e exigirão novos gates. Se esta decisão estiver errada, o custo é repetir dois gates e invalidar temporariamente escopo que poderia ter permanecido aprovado; nenhum probe será executado nesse intervalo.

Ruling: A Task 02 repete a condição confirmada da Task 01: seus cinco arquivos estão ausentes em `fb14629` e o plano proíbe commit; a revisão usará `task-02-review-package.md` com base, escopo e hashes de snapshot integral. Se esta decisão estiver errada, o custo é refazer a revisão após commit explicitamente autorizado, mantendo Task 03 bloqueada.

Ruling: Dividir a Task 02 em duas parcelas, primeiro TechSpec e depois TASKS/escopo, usando o mesmo implementador entre os gates; a primeira pode criar teste, compatibility.md, interface-decisions.md e TechSpec, mas não tasks.md nem executar probes. Se esta decisão estiver errada, haverá uma retomada adicional, porém nenhum contrato downstream será produzido antes do gate que o plano exige.

Ruling: `task-brief.sh` gerou a seção da Task 02 sem materializar os tipos transitivos exigidos; o controller anexou ao brief as cláusulas exatas da spec para RuntimeRecipe, QualificationCheck, ResourceSet, CheckoutRef, ArtifactRef e ApprovalRef e suas invariantes, antes do despacho. Se esta decisão estiver errada, o brief será bloqueado pela revisão e deverá ser regenerado, sem promover TechSpec ou TASKS.

Ruling: Como a Task 01 proíbe commit e todos os seus cinco arquivos estão ausentes em `fb14629`, `review-package.sh` rejeita deterministicamente `BASE == HEAD`; a revisão independente usará `task-01-review-package.md`, que fixa base, escopo e hashes e exige leitura integral dos cinco arquivos novos. Se esta decisão estiver errada, a revisão pode não receber semântica de diff equivalente; o custo é refazer a revisão após um commit explicitamente autorizado, sem promover a Task 02 enquanto isso.

Ruling: Executar a Task 01 em duas parcelas separadas pelo gate humano do PRD; o primeiro despacho cria `tests/test_sdd_flow_m01_qualification.py` e `tasks/prd-specflow/prd.md` e retorna aguardando decisão, e o mesmo implementador retoma os demais arquivos após aprovação. Se esta decisão estiver errada, a Task 01 exigirá uma rodada adicional de coordenação, mas não produzirá Stories antes do gate obrigatório.

Ruling: Usar somente skills e coordenação do pwdev-power na autoria; os arquivos de `plugins/sdd-composy/` são fontes estáticas de requisitos e templates. Se esta decisão estiver errada, alguma garantia auxiliar de outro plugin poderá precisar ser reintroduzida por mudança de plano e novo gate.
