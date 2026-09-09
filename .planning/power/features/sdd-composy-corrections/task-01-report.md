# Task 01 — relatório de execução

Data: 2026-09-09
Base observada: `2941fb1`
Status: IMPLEMENTED

## Baseline preservado

- `plugins/sdd-composy/scripts/sdd_status.py` já continha um fallback local que classificava uma fila Markdown não vazia como `active`.
- `tests/test_sdd_composy_hermes.py` já continha uma verificação local por substring desse fallback.
- Essas duas alterações foram tratadas como baseline; o arquivo Hermes não foi alterado nesta tarefa.

## Implementação

- `status()` agora lê projeções canônicas de `.planning/sdd-composy/tasks/*.json`, valida cada contrato, filtra efetivamente por `prd_slug` e distingue tarefas elegíveis das já publicadas como `ready`.
- Fontes `malformed`/`unsafe_symlink` têm precedência estável sobre tarefa running, LOOP e fleet; divergência de trace também não é apagada por fontes posteriores.
- Frontmatter sem `meta.task`, vazio ou inválido falha fechado e nunca recebe confiança alta.
- `import_tasks()` preserva campos desconhecidos, tarefas existentes somente no JSON e o estado JSON vivo; divergências de estado do Markdown são registradas, e novas tarefas pré-promovidas são recusadas.
- A validação rejeita tipos inválidos de estado, destinos/ancestrais symlink e mantém publicação atômica no mesmo diretório.
- A API pública de `sdd_trace` recebe a raiz do repositório; internamente resolve somente `.planning/sdd-composy/trace`, evitando dupla concatenação. A projeção usa temporário imprevisível, `fsync` e `os.replace`.
- Testes de status com sentinela comparam todos os bytes antes/depois, cobrindo config, JSON de tarefas, trace e arquivos externos à governança.

## TDD e evidência

- RED inicial: 60 testes, 6 falhas esperadas cobrindo prioridade malformed, task ausente/vazia, fila canônica filtrada e não regressão de estado.
- RED adicional: 2 falhas esperadas cobrindo tarefa JSON-only e symlink no nome temporário previsível do trace.
- Prova de regressão: a guarda de autoridade JSON foi revertida temporariamente; `test_import_preserves_live_json_state_and_reports_markdown_divergence` falhou (`pending != running`). O arquivo foi restaurado e os SHA-256 da versão restaurada e do backup coincidiram: `f2b60cbd6d41188f5877ebfc3f4f5c8a11aa7ad383fb00123c28b42c128eccb4`.
- GREEN final: `python3 -m unittest tests.test_sdd_composy_observability tests.test_sdd_composy_tasks -v` — 62 testes, OK.
- `PYTHONPYCACHEPREFIX=/tmp/task01-pycache python3 -m py_compile ...` — OK.
- `git diff --check` — OK.
- Uma tentativa de `py_compile` sem cache redirecionado falhou por permissão no cache global do macOS; foi classificada como falha de ambiente e repetida com cache isolado.

## Escopo e commits

- Arquivos de implementação/teste alterados somente nos cinco caminhos autorizados pela Tarefa 01.
- Este relatório é o artefato administrativo solicitado pelo brief.
- Nenhum commit foi criado, conforme instrução do executor.

STATUS: IMPLEMENTED
REPORT: .planning/power/features/sdd-composy-corrections/task-01-report.md
COMMITS: NONE
NOTE: Focused suite passed 62 tests; no commit was created.

## Fix round 1

- Corrigidos somente os dois findings Important de `task-01-review.md`; o finding Minor permaneceu diferido.
- RED: três métodos novos produziram quatro falhas esperadas: `.planning`/`sdd-composy` symlinkados eram seguidos, `trace/` symlinkado não era classificado como `unsafe_symlink`, e arrays JSON em LOOP/fleet não falhavam fechados.
- GREEN: todos os ancestrais operacionais controlados são recusados antes de qualquer leitura; `trace/` symlinkado permanece `unsafe_symlink`; `_records()` exige objetos JSON e fleet não descarta subdiretórios symlinkados.
- Verificação: `python3 -m unittest tests.test_sdd_composy_observability tests.test_sdd_composy_tasks -v` — 65 testes, OK; `git diff --check` — OK.
