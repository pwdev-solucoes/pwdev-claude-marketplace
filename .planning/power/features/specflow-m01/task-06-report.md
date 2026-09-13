---
type: TASK_REPORT
okf_version: "0.2"
generated:
  by: agent:pwdev-power
  at: "2026-09-13T09:43:17Z"
lifecycle:
  status: NEEDS_CONTEXT
human_approval: PENDING
sources:
  - resource: .planning/power/features/specflow-m01/task-06-brief.md
  - resource: .planning/power/features/specflow-m01/plan-amendment-05-probe-fixture-gate.md
  - resource: .planning/power/features/specflow-m01/probe-recipe.md
verified:
  - event: focused_tests
    result: passed
    at: "2026-09-13T09:43:17Z"
  - event: combined_m01_tests
    result: passed
    at: "2026-09-13T09:43:17Z"
  - event: diff_check
    result: passed
    at: "2026-09-13T09:43:17Z"
---

# M01 Task 06 — fixtures e preview operacional renovado

STATUS: NEEDS_CONTEXT

A fase estática/read-only autorizada pela Emenda 05 está pronta. O ApprovalRef da
Task 05 permanece histórico/stale; nenhum ApprovalRef novo foi materializado e nenhum
resultado comportamental foi promovido.

## TDD e verificação

- RED válido: `python3 -m unittest tests.test_sdd_flow_m01_compatibility` executou 6
  testes e falhou em 6 asserções porque as quatro fixtures ainda não existiam.
- GREEN focado: o mesmo comando executou 6 testes e terminou `OK`.
- Suíte combinada: `python3 -m unittest tests.test_sdd_flow_m01_compatibility tests.test_sdd_flow_m01_recipe tests.test_sdd_flow_m01_qualification tests.test_sdd_flow_m01_contracts`
  executou 39 testes e terminou `OK`.
- `git diff --check`: exit code 0, sem saída.
- Observação read-only: `/Users/paulosoares/.local/bin/compozy version` retornou
  `compozy 0.3.0-beta.25` com exit code 0.

## ResourceSet estático

Todos os paths são relativos, arquivos regulares, sem symlink e confinados ao
checkout:

| Path | SHA-256 |
|---|---|
| `tests/test_sdd_flow_m01_compatibility.py` | `6fbe0ce718056c925d807c8033bf84236f1611c239339bb8250f048d188f487a` |
| `.planning/power/features/specflow-m01/probe/fixture/extension/extension.toml` | `2a295e23687684bc683c2e751c60b38f20d4fc88ceef14a4989d6a85000d9c96` |
| `.planning/power/features/specflow-m01/probe/fixture/extension/agents/probe/AGENT.md` | `9651e228e3979d26b581c2c1db11c1672248cb71362065ef941d6575f02f6bf8` |
| `.planning/power/features/specflow-m01/probe/fixture/specflow-m01-loop.yaml` | `fecabbc17bdddf452d4973b24defddd3a555dd907c0ae1de425c62e5c5a23faf` |
| `.planning/power/features/specflow-m01/probe/fixture/run-config.yaml` | `4a662133b00b1b3d3a88c5e7539b82763c389b3b0a6008c89bc57305b7564685` |

O manifesto declara uma extensão resource-only `specflow-m01-probe`, compatibilidade
mínima beta.25 e somente o diretório `agents`. O agente `probe` usa
`permissions: approve-reads`. O Loop usa `apiVersion: compozy.loop/v1`, nome
`specflow-m01-qualification`, `concurrency: forbid`, limite 3 e janela sem progresso
2. O config por Run fixa `iteration_cap: 3`, `no_progress_window: 2` e
`fan_out_width: 1`.

## Preview das sete receitas para novo gate

Executável observado: `/Users/paulosoares/.local/bin/compozy`, versão
`compozy 0.3.0-beta.25`. CWD proposto:
`/Users/paulosoares/Projetos/skills-ia/pwdev-claude-marketplace/.worktrees/pwdev-composyos`.

1. `daemon start`; escopo: socket host identificado e
   `probe/runtime/daemon-owned.json`; esperado: iniciar e identificar somente o daemon.
2. `extension validate .planning/power/features/specflow-m01/probe/fixture/extension`;
   escopo: diretório da extensão e `probe/evidence/extension-validate.json`; esperado:
   validar o bundle sintético sem executar código.
3. `extension dev .planning/power/features/specflow-m01/probe/fixture/extension --workspace specflow-m01-probe-20260913`;
   escopo: extensão, registro do workspace dedicado e evidência `extension-dev.json`;
   esperado: vincular somente a extensão sintética.
4. `loop validate --file .planning/power/features/specflow-m01/probe/fixture/specflow-m01-loop.yaml --name specflow-m01-qualification --workspace specflow-m01-probe-20260913`;
   escopo: Loop fixture e `probe/evidence/loop-validate.json`; esperado: validar sem salvar.
5. `loop create --file .planning/power/features/specflow-m01/probe/fixture/specflow-m01-loop.yaml --expected-version 0 --workspace specflow-m01-probe-20260913`;
   escopo: Loop fixture, `probe/runtime/loop-owned.json` e evidência
   `loop-create.json`; esperado: publicar somente o Loop sintético com CAS inicial.
6. `loop run --dry-run --name specflow-m01-qualification --network local --workspace specflow-m01-probe-20260913 --config-file .planning/power/features/specflow-m01/probe/fixture/run-config.yaml`;
   escopo: run config e `probe/evidence/loop-dry-run.json`; esperado: preview Network
   Local sem criar Run.
7. `loop run --name specflow-m01-qualification --network local --workspace specflow-m01-probe-20260913 --config-file .planning/power/features/specflow-m01/probe/fixture/run-config.yaml`;
   escopo: run config, `probe/runtime/run-owned.json` e evidência `loop-run.json`;
   esperado: Run Network Local com budgets 3/2/1.

Cleanup proposto continua limitado a recursos próprios previamente registrados; não
remove recurso desconhecido, alheio ou fora do prefixo do probe. O daemon host não
pode ser parado sem prova de propriedade e autorização específica. Os testes
table-driven representam gate falso, digest alterado, traversal, symlink,
concorrência, interrupção antes/depois da publicação, retomada e observer tentando
mutação; não executam o runtime.

## Gate necessário

É necessária nova decisão humana sobre estes bytes finais, beta.25, sete argv,
escopos, cleanup e budgets antes da fase mutável. Nenhum `extension`, Loop, Run,
daemon mutation, probe, Docker, browser, Live, instalação, publicação, cleanup,
commit ou push foi executado nesta tarefa.
