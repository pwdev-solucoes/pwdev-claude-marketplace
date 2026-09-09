# Task 01 — re-review round 1

Data: 2026-09-09
Range revisado: `4b2ba00..eb433a8`
Escopo: somente os dois findings Important de `task-01-review.md`; o finding Minor diferido não foi reaberto.

## Veredictos

- SPEC: PASS
- QUALITY: PASS

## Baseline e preservação

- HEAD observado: `eb433a8b4f370ec3ec9925d9433f01045beb51a8`.
- Baseline local preservado: `M tests/test_sdd_composy_hermes.py`; o diretório administrativo `.planning/power/features/sdd-composy-corrections/` já estava não rastreado.
- Nenhum arquivo de implementação ou teste foi alterado. Todas as reproduções usaram diretórios temporários.

## Revalidação dos findings

### ADDRESSED — ancestrais symlinkados em `status()`

O código agora verifica `.planning` e `.planning/sdd-composy` antes de ler qualquer fonte, além de classificar o diretório `trace/` symlinkado diretamente como `unsafe_symlink`. A reprodução original com `.planning` apontando para uma árvore externa retornou `status == "malformed"`, todas as seis fontes com estado `unsafe_symlink` e confiança baixa. A reprodução com apenas `trace/` symlinkado retornou `status == "malformed"` e `sources.trace.state == "unsafe_symlink"`. Os testes `test_status_rejects_each_controlled_symlink_ancestor` e `test_trace_directory_symlink_is_unsafe_not_divergent` cobrem os casos corrigidos.

### ADDRESSED — tipos JSON inválidos em LOOP/fleet

`_records()` agora exige que cada registro JSON seja objeto e retorna `malformed` para outros tipos. `_fleet_records()` preserva esse diagnóstico e também recusa subdiretórios symlinkados. As reproduções originais com `bad.json` contendo `[]` em `loops/` e `fleet/` retornaram `status == "malformed"`, estado da fonte `malformed` e confiança baixa. O teste `test_loop_and_fleet_non_object_json_fail_closed` cobre ambos os casos.

## Verificações

- `python3 -m unittest tests.test_sdd_composy_observability tests.test_sdd_composy_tasks -v`: PASS, 65 testes em 0,441 s.
- `git diff --check 4b2ba00..eb433a8`: PASS.
- Reproduções temporárias dos dois findings: PASS.

## Findings deste round

- Critical: 0
- Important: 0
- Minor: 0 (o Minor anterior permaneceu diferido e fora do escopo desta re-review)

