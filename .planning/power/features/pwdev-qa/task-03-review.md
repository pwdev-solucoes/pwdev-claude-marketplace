# Task 03 — revisão

Data: 2026-09-12
Range revisado: `e4e111c..cc9429a`
Modo: revisão somente leitura; nenhum subagente; este relatório é o único arquivo produzido.

## SPEC

PASS

Os três contratos tratam os nomes de ferramentas como candidatos condicionados à superfície
efetivamente observada, mapeiam leitura, escrita, execução e carregamento sob demanda e exigem
diagnóstico distinto para `missing` e `unverified`. As instruções proíbem instalação, alteração de
configuração pessoal, flags de bypass, execução fictícia e uso de outro runtime como atalho.

O contrato Hermes separa corretamente o registro por `register_skill` com `pathlib.Path` do
carregamento posterior por `skill_view`, inclusive exigindo probes independentes. Nenhum runtime é
declarado verificado nesta entrega: o relatório registra as limitações da sessão e preserva o smoke
real de descoberta/invocação para a etapa de aceitação integrada planejada em F05-03.

## QUALITY

PASS

Verificação fresca:

- `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest -v tests.test_qa_runtime_contracts` — PASS,
  5 testes.
- `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest -v tests.test_qa_core tests.test_qa_tooling` —
  PASS, 16 testes.
- `git diff --check e4e111c..cc9429a` — PASS.
- O pacote altera os quatro arquivos declarados de implementação/teste e o relatório da tarefa;
  HEAD permaneceu em `cc9429a` durante a revisão.

Os cenários cobrem as quatro capacidades nos três runtimes, probe negativo explícito, probe não
executado, sucesso completo e incompleto, limites de segurança e a separação específica de Hermes.
Os probes simulados validam a semântica do contrato, mas não são tratados como evidência de runtime:
essa limitação está explicitamente registrada no relatório e nos próprios mapeamentos.

## FINDINGS

### Critical

Nenhum.

### Important

Nenhum.

### Minor

Nenhum.

## REVIEW

APPROVED

F01-03 atende ao brief e pode prosseguir. A aprovação desta tarefa não verifica Claude Code, Codex
ou Hermes em ambiente real; qualquer declaração futura de runtime verificado continua condicionada
ao smoke real de todas as quatro capacidades e à evidência integrada prevista em F05-03.
