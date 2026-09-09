# Task 02 — revisão

Data: 2026-09-09
Range revisado: `eb433a8..664e314`
Modo: somente leitura da implementação; este arquivo é o único artefato produzido pela revisão.

## Veredictos

- SPEC: FAIL
- QUALITY: FAIL

## Baseline e preservação

- HEAD observado antes das verificações: `664e314`.
- Baseline local observado antes das verificações: `M tests/test_sdd_composy_hermes.py`; `plugins/sdd-composy/scripts/sdd_status.py` estava limpo no checkout. O diretório administrativo `.planning/power/features/sdd-composy-corrections/` já estava não rastreado.
- Nenhum arquivo de implementação ou teste foi alterado pela revisão. As reproduções usaram somente diretórios temporários. Este relatório é o único arquivo gravado.

## Findings

### Important — o renderer `pt-BR` deixa grande parte dos documentos em inglês

`plugins/sdd-composy/scripts/sdd_localization.py:17-150` faz substituições de fragmentos isolados, mas não localiza todos os blocos estáticos exigidos pelo brief. Uma inicialização real em `pt-BR` deixou 16 linhas/frases em inglês em `AGENTS.md`, incluindo “The map is observation…”, “Keep changes…” e “The focused rules…”. As quatro regras também mantiveram trechos inteiros em inglês, como “Apply only the concern-specific rule…”, “This rule does not define…” e “Return rejected gates…”. O teste `tests/test_sdd_composy_language.py:144-157` verifica apenas um marcador traduzido por arquivo, portanto passa mesmo com documentos mistos. Isso viola tanto “Localizar todos os textos” quanto a escolha exclusiva de idioma no init.

### Important — `plan` segue ancestral symlinkado em caminho controlado pelo plugin

Em `plugins/sdd-composy/scripts/sdd_init.py:207-220`, cada destino é consultado diretamente com `is_symlink()`, `exists()` e `read_text()`, sem validar antes os ancestrais. Em reprodução temporária, `.agents/rules` apontava por symlink para um diretório externo e `plan` leu o arquivo externo `testing.md`, classificando-o apenas como conflito `file`. A validação de ancestral só ocorre depois, em `apply`, por `_safe_relative()` (`sdd_init.py:313-320`). Assim, o preview não cumpre a recusa de symlinks nos ancestrais controlados e pode ler conteúdo fora do repositório.

### Important — validação manual aceita estados que violam `state.schema.json`

`_valid_state()` em `plugins/sdd-composy/scripts/sdd_init.py:120-130` valida apenas uma parte do schema. Ele não valida tipo/padrão de `active_prd` e `active_task`, formato de `updated_at`, estrutura dos itens de `blockers`/`loops`/`fleet`, nem o mínimo de `trace.source_event_count`. Uma reprodução alterou o estado para `active_prd: 123`, `updated_at: "not-a-date"` e `trace.source_event_count: -5`; `_valid_state()`, `verify().state_ok` e uma reaplicação retornaram sucesso. Portanto configuração/estado inválido pode ser tratado como autoridade válida, contrariando a exigência de estado conforme `state.schema.json` e de rejeição antes da publicação.

### Important — falha no meio da publicação deixa estado parcial sem relatório preciso

`apply()` publica cada destino sequencialmente em `plugins/sdd-composy/scripts/sdd_init.py:313-348`, mas não captura falhas para devolver a lista acumulada de criações nem realiza rollback. Ao injetar `OSError` na terceira chamada de `os.link`, permaneceram `AGENTS.md`, `CLAUDE.md`, `.agents/` e `.agents/rules/`; a CLI devolve somente `{"ok": false, "error": "injected-mid-publication"}`. Logo a implementação não reporta “publicação parcial com precisão”, embora o relatório afirme que essa condição foi coberta. `test_atomic_failure_cleans_temporary_publication_file` verifica apenas a limpeza do arquivo temporário e que `state.json` não foi publicado, não a exatidão do resultado parcial.

## Verificações executadas

- `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_sdd_composy_runtime tests.test_sdd_composy_language -v`: PASS, 47 testes em 1,831 s.
- `git diff --check eb433a8..664e314`: PASS.
- Inicialização temporária `pt-BR` com inspeção de todos os seis documentos: FAIL, conteúdo estático em inglês permaneceu em cinco documentos.
- Reprodução temporária com `.agents/rules` symlinkado para fora do repositório: FAIL, `plan` leu/classificou o arquivo externo.
- Reprodução temporária de estado incompatível com `state.schema.json`: FAIL, `_valid_state`, `verify` e reaplicação aceitaram o estado.
- Reprodução temporária de falha na terceira publicação atômica: FAIL, artefatos parciais sobreviveram sem lista estruturada de criações.
- `git status --short` após a suíte confirmou que o baseline local de implementação/testes permaneceu preservado.

## Contagem

- Critical: 0
- Important: 4
- Minor: 0
