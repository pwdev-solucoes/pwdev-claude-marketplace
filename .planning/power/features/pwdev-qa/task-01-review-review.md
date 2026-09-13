# Task 01 — re-review do fix round 1

Data: 2026-09-12
Range revisado: `5b24fc6..6f9fe9a`
Escopo: somente os dois findings Important da revisão anterior; HEAD não foi movido.

## Verificação fresca

- `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_qa_core -v` — PASS, 9 testes.
- `git diff --check 5b24fc6..6f9fe9a` — PASS.
- A correção altera somente três dos cinco arquivos autorizados da tarefa.
- O vocabulário permanece conforme o brief: casos/critérios usam `PASS`, `FAIL`, `BLOCKED`,
  `NOT_RUN`, `NOT_APPLICABLE`; o parecer global usa `PASS`, `FAIL`, `BLOCKED`.

## Finding 1 — diagnóstico obrigatório para sanitização pendente

**ADDRESSED.** `plugins/pwdev-qa/references/artifacts.md:23-25` agora exige explicitamente um
diagnóstico quando a revisão de sanitização está `pending`, além de impedir cópia e `PASS`.
`test_pending_sanitization_requires_an_explicit_diagnostic` protege o vínculo completo entre
estado pendente e diagnóstico obrigatório.

## Finding 2 — cenários comportamentais do roteador e somente leitura

**ADDRESSED.** As novas fixtures interpretam os contratos Markdown e exercitam, com filesystem
temporário, precedência da intenção explícita de review sobre superfície/risco, resolução de uma
skill regular instalada e rejeição de alvo ausente, diretório e symlink. Também exercitam
critérios ausentes/zero aplicáveis como `BLOCKED`. A tabela de workflows ganhou um modo
machine-readable; review/status são avaliados como `read-only` e o teste compara os bytes da
árvore temporária antes e depois. Isso fecha a evidência determinística exigida nesta tarefa;
smoke com os runtimes reais continua corretamente reservado para F05.

## REVIEW

APPROVED. Os dois findings Important estão endereçados; nenhum finding desta re-review permanece
aberto.
