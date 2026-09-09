# Task 03 — re-review 1

Data: 2026-09-09
Range revisado: `d4cd716..b1301d0`
Modo: somente leitura da implementação; este arquivo é o único artefato produzido pela re-review.

## SPEC

PASS

## QUALITY

PASS

## Baseline e preservação

- HEAD observado: `b1301d0`.
- Baseline local observado: `M tests/test_sdd_composy_hermes.py`; o diretório administrativo `.planning/power/features/sdd-composy-corrections/` já estava não rastreado.
- O patch corretivo permanece nos três arquivos aprovados para a Task 03.
- Nenhum arquivo de implementação ou teste foi alterado. As reproduções usaram somente repositório temporário; este relatório é o único arquivo gravado.

## FINDINGS

### Important 1 — a remapagem elimina campos JSON desconhecidos

ADDRESSED

`build_map()` agora carrega o objeto canônico anterior, descarta com segurança valores que não sejam objetos e mescla `{**previous, **current}`. Assim, extensões desconhecidas sobrevivem enquanto os campos conhecidos atuais prevalecem. A reprodução exata confirmou `future_field == {"keep": true}`, `schema == "sdd-composy.codebase"` e contagem observada atualizada após publicação. A regressão em `tests/test_sdd_composy_runtime.py` cobre tanto a preservação de campos desconhecidos quanto a atualização de campos conhecidos.

### Important 2 — a localização modifica evidência dinâmica do usuário

ADDRESSED

`write_map()` agora escolhe os blocos estáticos do idioma antes de interpolar comandos, fontes, caminhos e evidências. Não há mais substituição global no documento renderizado. A reprodução exata em `pt-BR` confirmou a presença de `none observed/package.json` e a ausência de `nenhum observado/package.json`; o texto estático permaneceu localizado. A regressão em `tests/test_sdd_composy_language.py` cobre o caminho dinâmico que originou o finding.

### Findings novos

Nenhum.

## Verificações executadas

- `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_sdd_composy_runtime tests.test_sdd_composy_language -v`: PASS, 57 testes em 1,902 s.
- `git diff --check d4cd716..b1301d0`: PASS.
- Reprodução temporária de `future_field`: PASS, preservado após `build_map()` e `write_map()`; campos conhecidos foram atualizados.
- Reprodução temporária `pt-BR` com `none observed/package.json`: PASS, evidência preservada e nenhum caminho traduzido foi emitido.

## REVIEW

APPROVED

Os dois findings Important da revisão inicial foram corrigidos e possuem evidência comportamental fresca. Não há finding remanescente nesta rodada.

## Contagem

- Critical: 0
- Important não resolvido: 0
- Minor: 0
