# Task 02 — revisão

Data: 2026-09-12
Range revisado: `6f9fe9a..eeccfc2`
Modo: revisão somente leitura; nenhum subagente; este relatório é o único arquivo produzido.

## SPEC

FAIL

A skill entrega a tabela de sete campos na ordem exata, distingue `playwright-cli` de
Playwright Test, seleciona a opção mobile pela plataforma e proíbe instalação automática.
Entretanto, os cenários determinísticos atribuem disponibilidade a partir de evidência
insuficiente e fabricam um probe negativo a partir de uma simples ausência no inventário. Há
também claims atuais sem fonte/data no resultado produzido e um comando local que diverge da
documentação oficial citada. Isso viola CA-004/CA-022 e o contrato de claims atuais.

## QUALITY

FAIL

Verificação fresca:

- `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_qa_tooling tests.test_qa_core`
  — PASS, 14 testes.
- `git diff --check 6f9fe9a..eeccfc2` — PASS.
- O pacote contém os três arquivos de implementação/teste declarados e o relatório da tarefa;
  HEAD permaneceu em `eeccfc2`.
- As fontes oficiais foram consultadas em 2026-09-12. Playwright documenta execução de suíte
  em CI com `npx playwright test`; Appium confirma UiAutomator2 para Android e XCUITest para
  iOS. A documentação atual de `playwright-cli` documenta o fallback local como
  `npx --no-install playwright --version`, não o comando registrado na skill.

Os testes verdes não afastam os defeitos: o helper de teste codifica a semântica incorreta de
disponibilidade, e o teste de claims valida apenas domínio e formato de data, não a associação
entre cada claim e a evidência oficial que efetivamente o sustenta.

## FINDINGS

### Important — o avaliador fabrica `missing` e promove dependências parciais a `available`

Em `tests/test_qa_tooling.py:60-66`, qualquer chave ausente vira `missing` com a evidência
inventada `command -v ... -> not found`, embora nenhuma execução negativa tenha sido fornecida.
O cenário em `tests/test_qa_tooling.py:103-112` passa apenas `npx` e transforma a omissão de
`playwright-cli` em um probe que não ocorreu. No sentido oposto,
`tests/test_qa_tooling.py:90-99` declara Appium UiAutomator2 `available` somente por encontrar
`appium`, sem comprovar o driver, SDK, ADB ou dispositivo. O mesmo modelo trata `npx` como prova
de Playwright Test em `tooling.md:15`, ainda que a própria skill determine `unverified` quando
faltam browser, driver ou outro pré-requisito (`SKILL.md:67-69`). Isso permite recomendações
fictícias justamente no comportamento que CA-022 exige impedir. Modele o inventário com probe,
resultado e evidência explícitos, diferencie `missing` de `unverified` e só atribua `available`
após comprovar a ferramenta e os pré-requisitos necessários ao uso recomendado.

### Important — claims atuais não chegam ao output com fonte/data e o teste não comprova a fonte

As regras de `tooling.md:14-17` fazem claims atuais como “Node.js 18 or newer” e compatibilidade
dos drivers, mas `recommend()` apenas copia `prerequisites` (`tests/test_qa_tooling.py:62-69`):
as linhas produzidas não incluem URL nem data e tampouco marcam esses fatos como `unverified`.
Isso contradiz `SKILL.md:38-40` e `SKILL.md:60-61`, que exigem fonte/data junto do claim em
`prerequisites` ou `evidence`. O teste em `tests/test_qa_tooling.py:120-135` examina somente o
ledger separado e aceita qualquer URL dos domínios permitidos, sem verificar que a página
sustenta o claim nem que a recomendação resultante carrega sua proveniência. Faça a fonte/data
parte do dado normalizado consumido pelo output (ou marque o claim `unverified`) e teste a linha
final de sete campos, não apenas a sintaxe do ledger.

### Important — o probe local de `playwright-cli` diverge da fonte oficial atual

`plugins/pwdev-qa/skills/qa-tooling/SKILL.md:45-46` registra
`npx --no-install playwright-cli --version`. A documentação oficial citada pelo próprio pacote,
consultada em 2026-09-12, registra `npx --no-install playwright --version` e orienta usar
`npx playwright cli` quando a versão local está disponível:
https://github.com/microsoft/playwright-cli#local-installation. Assim, a alegação do relatório
de que os requisitos/comportamento foram verificados contra essa fonte não sustenta o probe
entregue. Como o brief aprovado também contém o valor divergente, reconcilie explicitamente o
contrato com a fonte atual antes de alterar o literal; enquanto isso, não o declare verificado.
Adicione um cenário que valide a forma documentada do fallback sem instalar pacotes.

### Critical

Nenhum.

### Minor

Nenhum.

## REVIEW

CHANGES_REQUESTED

Corrigir os três findings Important antes de prosseguir: tornar os estados de disponibilidade
derivados apenas de probes e pré-requisitos observados, transportar fonte/data (ou
`unverified`) para cada claim atual no output e reconciliar o probe `npx` com a documentação
oficial e a especificação aprovada. Depois, repetir a suíte focada, a regressão de núcleo e o
`diff --check` com evidência fresca.
