# Task 01 — revisão

Data: 2026-09-09
Range revisado: `2941fb1..4b2ba00`
Modo: somente leitura da implementação; este arquivo é o único artefato produzido pela revisão.

## Veredictos

- SPEC: FAIL
- QUALITY: FAIL

## Baseline e preservação

- HEAD observado antes das verificações: `4b2ba00a2e7b58425dfe290f938f86a054996ae0`.
- Baseline local observado antes das verificações: `M tests/test_sdd_composy_hermes.py`; `plugins/sdd-composy/scripts/sdd_status.py` estava limpo no checkout. O diretório administrativo `.planning/power/features/sdd-composy-corrections/` já estava não rastreado.
- Nenhum arquivo de implementação ou teste foi alterado pela revisão. As reproduções usaram apenas repositórios temporários.

## Findings

### Important — `status()` segue ancestrais symlinkados e atribui confiança alta a fonte externa

Em `plugins/sdd-composy/scripts/sdd_status.py:31-44`, os destinos individuais são testados com `is_symlink()`, mas os ancestrais controlados `.planning` e `.planning/sdd-composy` não são validados. Um repositório temporário com `.planning` apontando por symlink para outro diretório e com `sdd-composy/config.json` nesse destino retornou `sources.config.state == "valid"` e `confidence == "high"`, em vez de `unsafe_symlink`/`malformed`. O mesmo problema faz um diretório `trace` symlinkado ser reclassificado como `divergent`, pois `verify()` captura a recusa do symlink e `status()` transforma qualquer `ok == false` em divergência (`sdd_status.py:37-42`). Isso viola a recusa de symlinks nos ancestrais controlados e permite que estado fora da árvore física do repositório participe da agregação. Os testes novos cobrem symlink no destino, mas não nos ancestrais (`tests/test_sdd_composy_observability.py:199-210`).

### Important — registros de LOOP/fleet com tipo JSON inválido não falham fechados

`_records()` aceita qualquer JSON sintaticamente válido e sempre devolve `valid` (`plugins/sdd-composy/scripts/sdd_status.py:92-101`). Assim, um `loops/bad.json` contendo `[]` foi publicado como fonte `valid` com confiança alta e status `uninitialized`. Para fleet, `_fleet_records()` descarta silenciosamente o mesmo valor não objeto e devolve `missing` (`sdd_status.py:103-117`). O brief exige validar fontes e tipos JSON antes da agregação, sem permitir que ramos posteriores escondam fonte malformada. A suíte adicionada usa apenas objetos válidos para LOOP/fleet e, portanto, não detecta a regressão.

### Minor — nome do teste contradiz a asserção exercitada

`test_canonical_task_queue_filters_feature_and_complete_is_not_active` afirma `alpha["status"] == "active"` em `tests/test_sdd_composy_observability.py:240-249`. O comportamento conservador pode ser correto para impedir que tarefas completas concluam a feature, mas o nome declara o oposto e reduz a clareza da regressão. Renomear o teste ou explicitar que “não autoriza concluir” significa permanecer `active` evita interpretação ambígua.

## Verificações executadas

- `python3 -m unittest tests.test_sdd_composy_observability tests.test_sdd_composy_tasks -v`: PASS, 62 testes em 0,495 s.
- `git diff --check 2941fb1..4b2ba00`: PASS.
- Reproduções temporárias de ancestral `.planning` symlinkado e de registros `loops/fleet` com JSON array: FAIL conforme findings acima.
- `git status --short` após as verificações confirmou preservação do baseline de implementação/testes.

## Contagem

- Critical: 0
- Important: 2
- Minor: 1

