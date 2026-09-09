# Task 03 — revisão

Data: 2026-09-09
Range revisado: `fe5686e..d4cd716`
Modo: somente leitura da implementação; este arquivo é o único artefato produzido pela revisão.

## SPEC

FAIL

## QUALITY

FAIL

## Baseline e preservação

- HEAD observado: `d4cd716`.
- Baseline local observado antes das verificações: `M tests/test_sdd_composy_hermes.py`; o diretório administrativo `.planning/power/features/sdd-composy-corrections/` já estava não rastreado.
- O pacote altera somente os três arquivos aprovados para a Task 03.
- Nenhum arquivo de implementação ou teste foi alterado pela revisão. As reproduções usaram apenas repositórios temporários; este relatório é o único arquivo gravado.

## FINDINGS

### Critical

Nenhum.

### Important — a remapagem elimina campos JSON desconhecidos

Em `plugins/sdd-composy/scripts/sdd_map.py:237-255`, `build_map()` lê do mapa anterior somente `source_commit` e constrói um objeto novo. Em `sdd_map.py:297` e `sdd_map.py:325-342`, `write_map()` serializa esse objeto novo e substitui `codebase.json` integralmente. Uma reprodução inicializada colocou `future_field: {"keep": true}` no mapa anterior; depois de `build_map()` seguido de `write_map()`, o campo desapareceu. Isso viola literalmente a Global Constraint “Manter campos JSON desconhecidos” e torna uma evolução compatível do schema destrutiva. A suíte nova verifica estabilidade de contagem, mas não preservação de extensões desconhecidas do JSON.

### Important — a localização modifica evidência dinâmica do usuário

Em `plugins/sdd-composy/scripts/sdd_map.py:298-324`, comandos, fontes e termos observados são interpolados primeiro, e depois uma tabela de substituições é aplicada ao documento inteiro. Em reprodução `pt-BR`, o caminho real `none observed/package.json` foi publicado como `nenhum observado/package.json` em `stack.md`. Isso viola as Global Constraints “Não traduzir [...] evidências do usuário” e idioma por blocos estáticos; também corrompe a rastreabilidade do inventário, pois o caminho documentado deixa de existir. Os testes dos dois idiomas verificam somente headings estáticos e não incluem valores dinâmicos que coincidam com tokens traduzíveis.

### Minor

Nenhum.

## Verificações executadas

- `python3 -m unittest tests.test_sdd_composy_runtime tests.test_sdd_composy_language -v`: PASS, 55 testes em 1,860 s.
- `git diff --check fe5686e..d4cd716`: PASS.
- Reprodução temporária de campo desconhecido em `codebase.json`: FAIL, `future_field` foi removido após remapagem.
- Reprodução temporária `pt-BR` com fonte `none observed/package.json`: FAIL, a evidência foi alterada para `nenhum observado/package.json`.
- Inspeção de init obrigatório, saída confinada, exclusão de `.worktrees`/contexto, rollback dos companions, limpeza de temporários e recusa de symlinks: nenhuma falha adicional encontrada no escopo exercitado.

## REVIEW

CHANGES_REQUESTED

A Task 03 não deve prosseguir ao gate seguinte enquanto os dois findings Important não forem corrigidos e cobertos por regressões comportamentais. A correção deve mesclar/preservar campos desconhecidos do mapa canônico sem permitir que campos conhecidos fiquem obsoletos e deve renderizar textos estáticos por idioma antes de inserir comandos, caminhos e demais evidências dinâmicas.

## Contagem

- Critical: 0
- Important: 2
- Minor: 0
