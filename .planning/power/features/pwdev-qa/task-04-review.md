# Task 04 — revisão

Data: 2026-09-12
Range revisado: `135985c..99fcc6b`
Modo: revisão somente leitura; nenhum subagente; este relatório é o único arquivo produzido.

## SPEC

PASS

As três skills entregam contratos utilizáveis para seus workflows consumidores. Estratégia produz
registro de riscos, matriz de cobertura, condições de entrada/saída, lacunas e risco residual;
requisitos produz avaliação por critério com ID e texto exatos, aplicabilidade, oráculo,
rastreabilidade e perguntas focadas; funcional produz condições identificadas e rastreáveis com
partição, precondições, ação, resultado observável e necessidades de ambiente, dados e evidência.

Os procedimentos preservam alvo, contrato, IDs e textos fornecidos, mantêm proposta separada da
fonte autoritativa e não inventam limites, resultados ou autorizações. Critérios ambíguos,
contraditórios ou sem oráculo ficam `BLOCKED`; fronteiras e comportamentos de erro ausentes também
bloqueiam a condição afetada. Cada skill contém as seis seções contratuais e dois cenários de
referência — sucesso e falha/limitação — cobrindo risco/cobertura, ambiguidade de critério e
partições positiva, negativa, de fronteira e de erro.

## QUALITY

PASS

Verificação fresca:

- `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest -v tests.test_qa_specialists
  tests.test_qa_core tests.test_qa_tooling tests.test_qa_runtime_contracts` — PASS, 28 testes.
- `git diff --check 135985c..99fcc6b` — PASS.
- O pacote altera exatamente os quatro arquivos de implementação/teste declarados e o relatório
  da tarefa; HEAD permaneceu em `99fcc6b` durante a revisão.

Os testes parseiam os cenários de referência e verificam os resultados relevantes, em vez de
somente procurar os nomes das seções: ordenação de risco, cobertura, bloqueio por oráculo ausente,
preservação do critério ambíguo sem limiar inventado e cobertura funcional observável. Os exemplos
são compactos, mas coerentes com os formatos de saída completos descritos em cada skill. Eles não
são apresentados como avaliação real de agente; essa verificação permanece corretamente atribuída
a F05-24.

## FINDINGS

### Critical

Nenhum.

### Important

Nenhum.

### Minor

Nenhum.

## REVIEW

APPROVED

F02-04 atende ao brief e pode prosseguir. A aprovação cobre os contratos e cenários determinísticos
desta tarefa; CA-002 ainda depende da avaliação integrada dos cenários com agente prevista em
F05-24 e não deve ser considerada concluída apenas por estes testes.
