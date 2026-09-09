# Task 04 — revisão

Data: 2026-09-09
Range revisado: `b1301d0..e2176d5`
Modo: somente leitura da implementação; este arquivo é o único artefato produzido pela revisão.

## SPEC

FAIL

## QUALITY

FAIL

## Baseline e preservação

- HEAD observado: `e2176d5`.
- Baseline local observado antes das verificações: `M tests/test_sdd_composy_hermes.py`; o diretório administrativo `.planning/power/features/sdd-composy-corrections/` já estava não rastreado. `plugins/sdd-composy/scripts/sdd_status.py` estava limpo neste checkout.
- O pacote altera somente os cinco arquivos declarados para a Task 04.
- Nenhum arquivo de implementação ou teste foi alterado pela revisão. As reproduções usaram diretórios temporários; este relatório é o único arquivo gravado.

## FINDINGS

### Critical

Nenhum.

### Important — o guard de VERIFY não é executado para o estágio canônico e aceita evidência declarada pelo provider

Em `plugins/sdd-composy/scripts/loop-engine-codex.py:35-38` e `plugins/sdd-composy/scripts/loop-engine-hermes.py:36-39`, a validação adicional é condicionada a `value["stage"] == "verify"`. O contrato consumido de `sdd_loop.orchestrate`, porém, usa os nomes canônicos `EXECUTE`, `QA`, `EVIDENCE`, `REVIEW` e `VERIFY`. Uma reprodução chamou `validate_result(..., "VERIFY")` nos dois adapters com `status: "completed"` e um `command_record` inteiramente sintético; ambos aceitaram o resultado. Mesmo no ramo minúsculo, o adapter confia apenas nos campos `command`, `exit_code` e `status` devolvidos pelo modelo, sem resolver um registro regular confinado ao repositório, conferir SHA-256, identidade, saída ou frescor. Isso contraria o step que exige rejeitar uma resposta OK sem evidência de comando VERIFY real e a Global Constraint que proíbe marcar evidência verificada por texto do modelo. O guard final de `sdd_loop._verify_completion()` ainda falha fechado ao concluir o LOOP, mas os adapters não cumprem o contrato declarado e podem publicar o estágio canônico antes dessa rejeição tardia. O teste novo usa somente `"verify"` minúsculo e, por isso, não exerce a integração real.

### Minor — a evidência de testes do relatório afirma captura de ambiente que a suíte não realiza

`tests/test_sdd_composy_runtime_adapters.py:45-65` e `:71-83` capturam somente `argv` e `cwd`; nenhuma fake serializa ou verifica `os.environ`. A inspeção do código mostra um ambiente reduzido a `PATH`, `LC_ALL=C` e `LANG=C`, sem cópia explícita de credenciais, mas a afirmação de TDD no relatório de que as fakes exercitam `argv/cwd/env` não é sustentada por regressão automatizada. Inclua uma asserção do ambiente efetivamente recebido pelo processo fake, especialmente para impedir regressão que volte a herdar credenciais.

## Verificações executadas

- `python3 -m unittest tests.test_sdd_composy_runtime_adapters -v`: PASS, 7 testes em 2,000 s.
- `python3 -m unittest tests.test_sdd_composy_loop -v`: PASS, 35 testes em 0,746 s.
- `python3 -m unittest tests.test_sdd_composy_hermes -v`: FAIL, 1 de 4 testes; a asserção local preexistente ainda exige o literal removido `hermes run`, divergência já registrada no relatório e atribuída à Task 08.
- `git diff --check b1301d0 e2176d5`: PASS.
- `bash -n plugins/sdd-composy/scripts/fleet/engine-hermes.sh`: PASS.
- Sonda temporária do bootstrap em layout achatado: PASS, 17 skills registradas como `Path`, contexto inicial de 656 caracteres e nenhum disparo implícito observado; o layout original também passou na suíte.
- Inspeção/sondas de argv, `cwd`, prompt com metacaracteres, arquivo final exclusivo Codex, JSONL ignorado pelo Codex, JSON estrito Hermes, processo não-zero, executável indisponível, timeout, identidade divergente e autorização Hermes: nenhuma falha adicional encontrada.
- Sonda do estágio canônico `VERIFY` com `command_record` sintético: FAIL de segurança contratual; Codex e Hermes aceitaram o resultado.

## REVIEW

CHANGES_REQUESTED

A Task 04 não deve prosseguir ao gate seguinte enquanto o finding Important não for corrigido. Os adapters devem reconhecer o enum canônico `VERIFY` e rejeitar evidência autoatestada pelo provider, alinhando o `command_record` ao mecanismo verificável e confinado usado por `sdd_loop._verify_completion()`. A regressão deve passar o estágio exatamente como `orchestrate()` o produz e provar que um objeto inventado pelo provider não é aceito como evidência real.

## Contagem

- Critical: 0
- Important: 1
- Minor: 1
