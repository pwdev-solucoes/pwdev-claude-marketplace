---
type: PROBE_RECIPE
okf_version: "0.2"
generated:
  by: agent:pwdev-power
  at: "2026-09-13T00:30:00Z"
lifecycle:
  status: DRAFT
human_approval: PENDING
sources:
  - resource: .planning/power/features/specflow-m01/task-01-brief.md
  - resource: .planning/power/features/specflow-m01/runtime-command-qualification.md
verified: []
---

# M01 — RuntimeRecipe propostas, sem probes

Propostas produzidas pela Task 03. A Task 04 reconcilia somente consumidores stale e
gates documentais; a Task 05 apresenta a aprovação operacional e vincula identidade/
ApprovalRef reais; somente a Task 06 poderá executar receitas aprovadas. Executável,
versão e sintaxe foram observados somente
por discovery/version/help/status. Nenhum argv mutável foi executado e nenhum
ApprovalRef foi fabricado. Todas as receitas seguem `approved_scope: null`,
`observed: NOT_RUN`, `result: NOT_RUN` e nenhuma evidência operacional.

```json
{
  "status": "BLOCKED",
  "approved_scope": null,
  "result": "NOT_RUN",
  "runtime_recipes": [
    {
      "id": "RCP-DAEMON-START-001",
      "executable": "/Users/paulosoares/.local/bin/compozy",
      "argv": ["daemon", "start"],
      "cwd": "/Users/paulosoares/Projetos/skills-ia/pwdev-claude-marketplace/.worktrees/pwdev-composyos",
      "mutable_scope": ["host-daemon:/Users/paulosoares/.compozy/daemon.sock", ".planning/power/features/specflow-m01/probe/runtime/daemon-owned.json"],
      "approved_scope": null,
      "expected": "iniciar somente o daemon identificado e registrar identidade/saúde",
      "observed": "NOT_RUN", "result": "NOT_RUN", "evidence_refs": []
    },
    {
      "id": "RCP-EXTENSION-VALIDATE-001",
      "executable": "/Users/paulosoares/.local/bin/compozy",
      "argv": ["extension", "validate", ".planning/power/features/specflow-m01/probe/fixture/extension"],
      "cwd": "/Users/paulosoares/Projetos/skills-ia/pwdev-claude-marketplace/.worktrees/pwdev-composyos",
      "mutable_scope": [".planning/power/features/specflow-m01/probe/fixture/extension", ".planning/power/features/specflow-m01/probe/evidence/extension-validate.json"],
      "approved_scope": null,
      "expected": "validar apenas o bundle sintético confinado sem executar seu código",
      "observed": "NOT_RUN", "result": "NOT_RUN", "evidence_refs": []
    },
    {
      "id": "RCP-EXTENSION-DEV-001",
      "executable": "/Users/paulosoares/.local/bin/compozy",
      "argv": ["extension", "dev", ".planning/power/features/specflow-m01/probe/fixture/extension", "--workspace", "specflow-m01-probe-20260913"],
      "cwd": "/Users/paulosoares/Projetos/skills-ia/pwdev-claude-marketplace/.worktrees/pwdev-composyos",
      "mutable_scope": [".planning/power/features/specflow-m01/probe/fixture/extension", ".planning/power/features/specflow-m01/probe/runtime/workspace-specflow-m01-probe-20260913.json", ".planning/power/features/specflow-m01/probe/evidence/extension-dev.json"],
      "approved_scope": null,
      "expected": "vincular somente a extensão sintética ao workspace dedicado após gate",
      "observed": "NOT_RUN", "result": "NOT_RUN", "evidence_refs": []
    },
    {
      "id": "RCP-LOOP-VALIDATE-001",
      "executable": "/Users/paulosoares/.local/bin/compozy",
      "argv": ["loop", "validate", "--file", ".planning/power/features/specflow-m01/probe/fixture/specflow-m01-loop.yaml", "--name", "specflow-m01-qualification", "--workspace", "specflow-m01-probe-20260913"],
      "cwd": "/Users/paulosoares/Projetos/skills-ia/pwdev-claude-marketplace/.worktrees/pwdev-composyos",
      "mutable_scope": [".planning/power/features/specflow-m01/probe/fixture/specflow-m01-loop.yaml", ".planning/power/features/specflow-m01/probe/evidence/loop-validate.json"],
      "approved_scope": null,
      "expected": "validar a definição sintética sem salvar",
      "observed": "NOT_RUN", "result": "NOT_RUN", "evidence_refs": []
    },
    {
      "id": "RCP-LOOP-CREATE-001",
      "executable": "/Users/paulosoares/.local/bin/compozy",
      "argv": ["loop", "create", "--file", ".planning/power/features/specflow-m01/probe/fixture/specflow-m01-loop.yaml", "--expected-version", "0", "--workspace", "specflow-m01-probe-20260913"],
      "cwd": "/Users/paulosoares/Projetos/skills-ia/pwdev-claude-marketplace/.worktrees/pwdev-composyos",
      "mutable_scope": [".planning/power/features/specflow-m01/probe/fixture/specflow-m01-loop.yaml", ".planning/power/features/specflow-m01/probe/runtime/loop-owned.json", ".planning/power/features/specflow-m01/probe/evidence/loop-create.json"],
      "approved_scope": null,
      "expected": "publicar somente o Loop sintético com CAS inicial no workspace dedicado",
      "observed": "NOT_RUN", "result": "NOT_RUN", "evidence_refs": []
    },
    {
      "id": "RCP-LOOP-DRY-RUN-001",
      "executable": "/Users/paulosoares/.local/bin/compozy",
      "argv": ["loop", "run", "--dry-run", "--name", "specflow-m01-qualification", "--network", "local", "--workspace", "specflow-m01-probe-20260913", "--config-file", ".planning/power/features/specflow-m01/probe/fixture/run-config.yaml"],
      "cwd": "/Users/paulosoares/Projetos/skills-ia/pwdev-claude-marketplace/.worktrees/pwdev-composyos",
      "mutable_scope": [".planning/power/features/specflow-m01/probe/fixture/run-config.yaml", ".planning/power/features/specflow-m01/probe/evidence/loop-dry-run.json"],
      "approved_scope": null,
      "expected": "pré-visualizar Network Local sem criar Run",
      "observed": "NOT_RUN", "result": "NOT_RUN", "evidence_refs": []
    },
    {
      "id": "RCP-LOOP-RUN-001",
      "executable": "/Users/paulosoares/.local/bin/compozy",
      "argv": ["loop", "run", "--name", "specflow-m01-qualification", "--network", "local", "--workspace", "specflow-m01-probe-20260913", "--config-file", ".planning/power/features/specflow-m01/probe/fixture/run-config.yaml"],
      "cwd": "/Users/paulosoares/Projetos/skills-ia/pwdev-claude-marketplace/.worktrees/pwdev-composyos",
      "mutable_scope": [".planning/power/features/specflow-m01/probe/fixture/run-config.yaml", ".planning/power/features/specflow-m01/probe/runtime/run-owned.json", ".planning/power/features/specflow-m01/probe/evidence/loop-run.json"],
      "approved_scope": null,
      "expected": "criar um Run Network Local com budgets 3/2/1 no config confinado",
      "observed": "NOT_RUN", "result": "NOT_RUN", "evidence_refs": []
    }
  ]
}
```

RuntimeRecipe = {id: string, executable: string, argv: string[], cwd: string,
mutable_scope: string[], approved_scope: ApprovalRef|null, expected: string,
observed: string, result: PASS|FAIL|ENVIRONMENT_FAILURE|NOT_RUN,
evidence_refs: ArtifactRef[]}. Ausência de argv comprovado impede execução.

## Preflight e budgets

Exigir TASKS aprovado/fresco, gate operacional separado ligado a estes bytes,
daemon/workspace/checkout e ator humano demonstrados, preview e
`contract_root = execution_root = checkout_root`. aprovação stale, digest divergente,
identidade vazia, argv divergente ou recurso alheio mantém BLOCKED/NOT_RUN.

Budgets: 3 tentativas totais incluindo a primeira, janela de ausência de progresso 2
e fan-out 1, persistidos em filhos/retomada, sem Fleet, paralelismo ou merge automático.
O futuro `probe/fixture/run-config.yaml` precisa conter esses valores e integrar o
snapshot aprovado antes de ser criado/usado.

`loop approve` não integra RuntimeRecipe[] ainda: `run-id` e `gate-id` devem vir do
Run realmente criado e ser ligados ao ator humano real. Inventá-los violaria o contrato.
A Task 05 deverá obter a aprovação operacional e vincular uma receita adicional aos
IDs reais quando eles puderem ser apresentados sem execução antecipada. Somente a
Task 06 poderá executar o argv aprovado e observar IDs de Run/gate; qualquer dado ainda
indisponível mantém a receita BLOCKED/NOT_RUN. A Task 04 não executa nem aprova receitas.

## Cleanup proposto

Política: cleanup somente de recursos próprios registrados. Registrar ID, path,
revisão e proprietário antes de limpar. Não remover recurso desconhecido, alheio,
sem identidade coincidente ou fora de `.planning/power/features/specflow-m01/probe/`.
O daemon host só pode ser parado se esta execução provar que o iniciou e houver
autorização específica. Preservar evidência, branch, checkout e dados por padrão.

## Gate

Primeiro gate: TASKS revisado. Depois, em decisão separada, apresentar receitas,
escopo mutável, cleanup e budgets. STATUS: NEEDS_CONTEXT. Nenhum comando mutável
ou probe ocorreu nesta Task 03.
