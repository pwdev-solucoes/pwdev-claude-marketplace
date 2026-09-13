---
type: EVIDENCE_REPORT
okf_version: "0.2"
generated:
  by: agent:codex
  at: "2026-09-10T19:37:05Z"
lifecycle:
  status: INCOMPLETE
sources:
  - .planning/power/features/sdd-composy-corrections/matrix.md
  - .planning/power/features/sdd-composy-corrections/runs/offline/summary.json
verified: []
---

# Evidência da Tarefa 08 — fase offline

## Veredito

`INCOMPLETE`. A regressão offline passou, mas nenhuma inferência real foi executada. Os cenários
reais permanecem `NOT_RUN`, e fleet real permanece `BLOCKED` até acknowledgement humano externo.
Este documento não aprova a aceitação global nem marca evidência como `VERIFIED`.

## Baseline e preflight

- Commit antes da fase: `3e491f8e6f033f00c111896318e2c1aa723c6211`.
- `plugins/sdd-composy/scripts/sdd_status.py` antes/depois:
  `7e409d9f9238a7dfcd4feea2d3f9842670565e2ad8bf8b9864c6cee656b5002a`.
- `tests/test_sdd_composy_hermes.py` antes:
  `771c07d5a360515384b9e5f20b075873dfbc091e5bc6c599e0af5dfa3746e3f4`.
- Snapshot Git inicial: alterações administrativas preexistentes em `ledger.md`, relatório e
  revisões das Tasks 05–07; nenhum diff em `sdd_status.py` ou no baseline Hermes.
- Disponíveis, exit code 0: Hermes Agent `0.21.1`, Codex CLI `0.153.4`, Claude Code `2.1.267`,
  Git `2.50.1`, jq `1.7.1`, Docker Compose `5.1.3`, cmux `0.64.22`.
- `hermes --help`, `hermes plugins doctor plugins/sdd-composy --ci`, `codex exec --help`,
  `claude --help` e `cmux --help`: exit code 0. O preflight não realizou inferência.

## Execução offline

Comando:

```text
python3 scripts/sdd_runtime_smoke.py --mode offline --runtime all --language both --scenario all --output .planning/power/features/sdd-composy-corrections/runs/offline
```

- Resultado: `PASS`; 36/36 combinações `PASS`.
- Cobertura: 3 runtimes × 2 idiomas × read-only, lifecycle, fleet, handoff, evidence e compose.
- Cada combinação usou repositório Git temporário exclusivo e cópia local fail-closed do plugin.
- Os cenários executaram: `sdd-status` com sentinelas; init→map→import→next e LOOP real de cinco
  estágios com engine local; launcher fleet com dois worktrees e runtime mismatch; handoff durável;
  evidência ausente/antiga/adulterada e status divergente; Compose, cmux e merge em fixtures.
- Chamadas de provider: Hermes 0, Codex 0, Claude 0.
- Timeout máximo contratado: 300 segundos por chamada.
- Orçamento contratado: máximo 28 chamadas por runtime.
- Uso/tokens/custo: `null` (indisponível; nenhum zero foi inventado).
- Hash do plugin copiado: `d101d5fb9b03048a1342a104c9786b0e210e329c190239b6f805e52282d0b9e3`.
- Duração por cenário: 0.000587s–1.371612s; exit codes, hashes, task/worktree e recursos estão
  preservados individualmente no sumário.
- Hash do sumário: `da6e4153c7ba495e09dbc22e568535b420ce223f5dea9e23049969cb4ad26d15`.

| Cenário | Hermes offline | Codex offline | Claude offline | Hermes real | Codex real | Claude real |
|---|---|---|---|---|---|---|
| read-only pt-BR/en-US | PASS | PASS | PASS | NOT_RUN | NOT_RUN | NOT_RUN |
| lifecycle pt-BR/en-US | PASS | PASS | PASS | NOT_RUN | NOT_RUN | NOT_RUN |
| fleet pt-BR | PASS | PASS | PASS | BLOCKED | BLOCKED | BLOCKED |
| fleet en-US/mismatch | PASS | PASS | PASS | NOT_RUN | NOT_RUN | NOT_RUN |
| handoff com IDs/gates | PASS | PASS | PASS | NOT_RUN | NOT_RUN | NOT_RUN |
| evidência adulterada/status divergente | PASS | PASS | PASS | NOT_RUN | NOT_RUN | NOT_RUN |
| compose/cmux/pós-merge | PASS | PASS | PASS | NOT_RUN | NOT_RUN | NOT_RUN |

Campos de duração e exit code por cenário real são `null` porque os cenários não rodaram.

## Verificação

Re-review round 2 fechou os dois Important remanescentes: o handoff usa consumidores/adapters
offline reais sobre arquivos persistidos e valida aprovação sintética escopada; a cópia isolada
recusa famílias de token/auth, `id_*`, chaves privadas, keystore e certificados, preservando
somente amostras documentais. A execução renovada produziu 36/36 `PASS` sem chamadas de provider.

- `python3 -m unittest tests.test_sdd_composy_runtime_smoke tests.test_sdd_composy_hermes -v`:
  21 testes, PASS.
- `python3 -m unittest discover -s tests -p 'test_sdd_composy*.py' -v`: 367 testes, PASS.
- `python3 scripts/validate_readme_plugins.py`: 16 plugins validados, PASS.
- `python3 -m unittest tests.test_readme_marketplace -v`: 1 teste, PASS.
- `bash -n plugins/sdd-composy/scripts/fleet/*.sh`: PASS.
- `git diff --check`: PASS.

## Gate pendente para execução real

Antes de qualquer fleet real, o humano precisa reconhecer explicitamente os três lançamentos
via `scripts/fleet/launch.sh --runtime hermes|codex|claude ...`, dois membros isolados e o limite
de 300 segundos/28 chamadas por runtime. Também precisa reconhecer:

- Hermes: `hermes -z PROMPT --in WORKTREE`, exigindo isolamento comprovado ou consentimento
  específico; sem `--yolo`.
- Codex seguro: `codex exec --sandbox workspace-write --ephemeral --cd WORKTREE ...`.
- Claude seguro: `claude -p --no-session-persistence --output-format json PROMPT`.
- Se for pedido `danger-full-access`, os vetores passam respectivamente a
  `--dangerously-bypass-approvals-and-sandbox` (Codex) e `--dangerously-skip-permissions`
  (Claude); isso exige acknowledgement explícito separado e não está autorizado por este relatório.

Sem esse acknowledgement, o harness deve continuar produzindo `BLOCKED`, nunca `PASS`.
