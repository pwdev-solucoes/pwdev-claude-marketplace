# Task 05 — revisão

Data: 2026-09-12
Range revisado: `99fcc6b..3846a91`
Modo: revisão somente leitura; nenhum subagente; este relatório é o único arquivo produzido.

## SPEC

FAIL

Os contratos Web e API cobrem os comportamentos pedidos: o probe local de Playwright usa
`npx --no-install playwright --version`, a exploração usa sessão própria `qa-report` e refs de
snapshot fresco, e Playwright Test permanece separado como suíte repetível/CI. API mantém
autenticação e autorização distintas, cobre erros documentados e exige ausência observável de
efeito duplicado para idempotência. As três skills têm as seis seções contratuais e os pares de
cenários sucesso/limitação, sem autorizar execução.

O cenário de sucesso mobile, porém, declara Android e iOS `READY` sem representar todos os
pré-requisitos que o próprio contrato torna obrigatórios. Isso permite prontidão derivada de um
subconjunto de probes e viola CA-004; a ausência de dispositivo é bloqueada corretamente, mas
ausência de host, build ou signing não é exercitada.

## QUALITY

FAIL

Verificação fresca:

- `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest -v tests.test_qa_specialists
  tests.test_qa_core tests.test_qa_tooling tests.test_qa_runtime_contracts` — PASS, 34 testes.
- `git diff --check 99fcc6b..3846a91` — PASS.
- O pacote altera exatamente os quatro arquivos de implementação/teste declarados e o relatório
  da tarefa; HEAD permaneceu em `3846a91` durante a revisão.
- A modificação preexistente em `.planning/power/features/pwdev-qa/ledger.md` e os artefatos não
  rastreados de revisões anteriores foram preservados sem alteração.

Os testes verdes não cobrem a contradição de prontidão mobile: eles afirmam exatamente as linhas
reduzidas da tabela, mas não fornecem probes de host, build, ADB/conectividade ou signing e não
verificam que a omissão de qualquer um deles impede `READY`.

## FINDINGS

### Important — cenário mobile promove pré-requisitos parciais a `READY`

Em `plugins/pwdev-qa/skills/qa-specialist-mobile/SKILL.md:29-44`, o contrato exige, para Android,
SDK, ADB, build, device/emulator e driver; para iOS, exige macOS, Xcode/SDK, build/signing,
device/simulator e driver. O formato de saída também exige disponibilidades separadas de tool,
host, SDK, driver, build, device e service com evidência de probe (`SKILL.md:50-56`). Entretanto,
as linhas `platform-ready` em `SKILL.md:63-67` contêm apenas nome da ferramenta, SDK, driver e
device. Em particular, a linha iOS pode ficar `READY` sem host macOS, build ou signing, e a linha
Android sem ADB ou build, embora `SKILL.md:76-79` determine que build ou host ausente/não testado
bloqueia ou deixa a capacidade não verificada.

O teste em `tests/test_qa_specialists.py:309-340` cristaliza esse subconjunto como sucesso e não
exercita probes omitidos. Complete o cenário com todas as dimensões obrigatórias e evidência
explícita de probe, e adicione casos em que host/build/signing ou ADB ausente/não executado
resultem em `BLOCKED`/`unverified`, nunca `READY`.

### Critical

Nenhum.

### Minor

Nenhum.

## REVIEW

CHANGES_REQUESTED

Corrigir o finding Important antes de prosseguir: tornar a prontidão mobile dependente de todos
os pré-requisitos declarados, com probes separados por plataforma, e testar ao menos uma ausência
além de dispositivo. Depois, repetir a suíte focada, as regressões F01/F02 e o `diff --check` com
evidência fresca.
