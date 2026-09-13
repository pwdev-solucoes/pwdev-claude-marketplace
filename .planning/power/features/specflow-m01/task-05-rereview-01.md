# Task 05 — re-review independente, correction rounds 1–2

SPEC: FAIL
QUALITY: FAIL
FINDINGS: Critical 0; Important 1 remanescente; Minor anterior fora do escopo desta rodada.

## Findings anteriores

1. Important — ArtifactRef do snapshot: **ADDRESSED**.
   Em `.planning/power/features/specflow-m01/probe-recipe.md:38`, 48, 58, 68, 78, 88 e 98, todos os ArtifactRef agora apontam para `probe-recipe-approved-snapshot.md`. O arquivo existe, é regular, confinado e sem symlink nos componentes do caminho; SHA-256 real `c606ebbf29d30881e54dd3e66c58d7e273a5f4bf6d49fd60b980e2171240b7c4`. O quinto arquivo foi autorizado pela Emenda 04. Os sete recibos são iguais e seus IDs conferem com recomputação independente.

2. Important — registros canônicos e testes adversariais: **NOT ADDRESSED** (correção parcial).
   - `.planning/power/features/specflow-m01/probe-recipe.md:124`–129 substitui o registro canônico de decision por prosa. Só o registro de run está copiado integralmente (116–122). A prosa não especifica a linha schema nem a serialização exata das chaves/ordem do decision record. O recibo ainda depende do brief/emenda/teste para reproduzir esses bytes, contrariando a exigência anterior de incorporar ambos os registros. Os valores dos IDs atuais estão corretos; falta completar o contrato autocontido.
   - `tests/test_sdd_flow_m01_recipe.py:245`–254 não cobre integralmente a matriz aprovada: prerequisites invertidos não aparecem nos casos; o digest stale é testado depois de alterar o path, sem restaurá-lo (252–254). Assim, o teste de digest pode passar só pelo erro de path, mesmo que a checagem de digest deixe de funcionar. A confusão de namespace, por outro lado, está efetivamente coberta por `loop-run:future` em 247 e execução para cada receita em 249–251.
   - Verificação adversarial independente em memória confirmou que o validador atual rejeita prerequisites invertidos, namespace Loop e digest isolado (`prerequisites`, `run_id`, `artifact digest`, respectivamente). Portanto não afirmo bypass atual desses três casos: o defeito remanescente é a cobertura de regressão incompleta exigida pela Emenda 04, além do registro canônico ausente. Acrescentar casos isolados para ordem e digest e copiar o decision record completo, sem probes.

## Evidências e limites

Lidos integralmente brief, report, package, review anterior, Emendas 03/04 e cinco deliverables. Os nove hashes do package conferem. Recomputação UTF-8/LF da Emenda 03 produziu:
- run: `power-approval-run:34e912e8035ae3868d153e64c3a64d72b69a5e4e57a7767fd9bc7a3f4933ce70`;
- decision: `decision:17fae407c996e1e19c03ff37b1877c27b7d5279a778853602df946826ab059c7`.

Os sete recibos coincidem, preservam prerequisites na ordem aprovada, snapshot real e separação Power/Loop. As sete receitas e matriz CORE/OPT continuam NOT_RUN.

Verificação fresca: `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_sdd_flow_m01_recipe tests.test_sdd_flow_m01_qualification tests.test_sdd_flow_m01_contracts`: 33 testes, zero falhas, exit 0. `git diff --check`: exit 0. Verde estrutural não comprova cobertura completa nem runtime. A baseline integral não foi reexecutada.

REGRESSIONS: nenhuma regressão nova confirmada no escopo; os problemas do finding 2 são lacunas remanescentes. O Minor anterior não foi reaberto.

Reviewer não moveu HEAD, não alterou implementação, não delegou e não executou probes. Apenas este relatório foi escrito. Task 06 permanece bloqueada pelo Important remanescente e gates aplicáveis; módulos dependentes continuam bloqueados por NOT_RUN. Esta revisão não concede aprovação humana nem conclui a Feature.

