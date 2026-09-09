# Task 02 — re-review 2

Data: 2026-09-09
Range revisado: `649c862..fe5686e`
Escopo: somente o finding Important residual da re-review 1.
Modo: somente leitura da implementação; este arquivo é o único artefato produzido nesta rodada.

## Veredictos

- SPEC: PASS
- QUALITY: PASS

## Baseline e preservação

- HEAD observado antes das verificações: `fe5686e`.
- Baseline local: `M tests/test_sdd_composy_hermes.py`; `plugins/sdd-composy/scripts/sdd_status.py` estava limpo. O diretório administrativo `.planning/power/features/sdd-composy-corrections/` já estava não rastreado.
- Nenhum arquivo de implementação ou teste foi alterado. Todas as reproduções usaram diretórios temporários.

## Reavaliação do finding residual

### ADDRESSED — todas as etapas de publicação agora reportam falha parcial

O bloco protegido de `apply()` agora cobre criação dos documentos e diretórios, compatibilidade `.claude`, persistência de idioma e publicação do estado. O plano de publicação é calculado antes das mutações e a captura de `OSError`/`ValueError` devolve `ok: false`, `created`, `pending`, `conflicts`, `actor` e `error` para falhas em qualquer dessas etapas.

Na reprodução com falha injetada em `os.symlink`, o resultado registrou exatamente os sete documentos já criados e deixou apenas `.claude` e `.planning/sdd-composy/state.json` em `pending`; a exceção não escapou. Na falha tardia de `_atomic_json` para `state.json`, o resultado registrou os documentos, `.claude` e `.planning/sdd-composy/config.json` em `created`, deixando somente o estado em `pending`.

Como controle adicional, uma falha injetada em `persist_language` também retornou resultado estruturado, com `.planning/sdd-composy/config.json` e o estado pendentes. O comportamento cobre o problema residual sem marcar inicialização como bem-sucedida.

## Verificações executadas

- `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_sdd_composy_runtime tests.test_sdd_composy_language -v`: PASS, 52 testes em 1,725 s.
- `git diff --check 649c862..fe5686e`: PASS.
- Falha injetada em `os.symlink`: PASS, retorno estruturado e listas exatas.
- Falha tardia injetada em publicação de `state.json`: PASS, somente o estado ficou pendente.
- Falha adicional injetada em `persist_language`: PASS, configuração e estado ficaram pendentes.
- `git status --short` após as verificações confirmou a preservação do baseline.

## Contagem residual

- Critical: 0
- Important: 0
- Minor: 0
