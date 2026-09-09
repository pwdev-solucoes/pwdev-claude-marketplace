# Task 04 — re-review 1

Data: 2026-09-09
Range revisado: `e2176d5..02a1ad8`
Escopo: somente o finding Important da revisão original; o finding Minor não foi reaberto.
Modo: somente leitura da implementação; este arquivo é o único artefato produzido pela re-review.

## SPEC

PASS

## QUALITY

PASS

## FINDINGS

### Important — ADDRESSED

O guard agora usa o estágio canônico `VERIFY` em `plugins/sdd-composy/scripts/loop-engine-codex.py:71-73` e `plugins/sdd-composy/scripts/loop-engine-hermes.py:72-74`. Nos dois adapters, a validação exige contexto do repositório e do contrato e resolve uma referência durável em vez de confiar nos campos de sucesso declarados pelo provider.

`_verify_command_record()` localiza exatamente um LOOP ativo para o `task_id`, exige arquivo de evidência regular e não symlinkado em caminho relativo confinado ao repositório, confere o SHA-256 da referência, a identidade `task_id`/`loop_id`, `status: passed`, `exit_code` inteiro igual a zero, comando não vazio, SHA-256 de stdout/stderr e timestamps posteriores à publicação de REVIEW e anteriores ao deadline. Falhas são normalizadas como `successful VERIFY requires real command evidence`.

A reprodução canônica produziu os resultados exigidos para Codex e Hermes:

- `VERIFY` com `command_record` sintético apontando para `evidence/invented.json`: recusado.
- `VERIFY` com arquivo regular dentro do repositório temporário, referência íntegra, identidade correta, saída autenticada e janela temporal válida: aceito.

O teste de regressão usa exatamente `VERIFY` em maiúsculas, como emitido por `sdd_loop.orchestrate()`. Portanto o finding Important original está ADDRESSED.

### Critical

Nenhum.

### Minor

Não reaberto por instrução desta rodada.

## Verificações executadas

- Dois testes focados de VERIFY canônico, sintético e real: PASS, 2 testes em 0,003 s.
- `python3 -m unittest tests.test_sdd_composy_runtime_adapters -v`: PASS, 8 testes em 1,961 s.
- `python3 -m unittest tests.test_sdd_composy_loop -v`: PASS, 35 testes em 0,739 s.
- `git diff --check e2176d5 02a1ad8`: PASS.
- Baseline preservado: `M tests/test_sdd_composy_hermes.py` permaneceu sem alteração pela revisão; o diretório administrativo já estava não rastreado.

## REVIEW

APPROVED

O único finding Important autorizado para esta re-review foi corrigido e coberto por regressão comportamental nas duas direções. O finding Minor da revisão original permanece fora do escopo desta decisão.

## Contagem desta rodada

- Critical: 0
- Important: 0 aberto; 1 ADDRESSED
- Minor: não reaberto
