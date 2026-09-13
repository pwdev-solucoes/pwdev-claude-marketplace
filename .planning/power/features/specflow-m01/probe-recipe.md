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
      "approved_scope": {"run_id": "power-approval-run:34e912e8035ae3868d153e64c3a64d72b69a5e4e57a7767fd9bc7a3f4933ce70", "gate_id": "gate:specflow-m01:runtime-recipe", "decision_id": "decision:17fae407c996e1e19c03ff37b1877c27b7d5279a778853602df946826ab059c7", "actor_ref": "human:user", "decision": "approved", "decided_at": "2026-09-13T08:53:00Z", "artifacts": [{"checkout_ref": {"workspace_id": "specflow-m01", "worktree_id": null, "checkout_root": "/Users/paulosoares/Projetos/skills-ia/pwdev-claude-marketplace/.worktrees/pwdev-composyos", "revision_ref": "fb146297d681a1a6a77d71b5c30772655802590a"}, "path": ".planning/power/features/specflow-m01/probe-recipe-approved-snapshot.md", "sha256": "c606ebbf29d30881e54dd3e66c58d7e273a5f4bf6d49fd60b980e2171240b7c4", "role": "contract"}], "prerequisites": ["power-gate:techspec:09bde614371cb465ea1c135244bd6c4e8cc3f3e62c0c9fdeb3dc065d70ab54f3", "power-gate:tasks:1efe23df5abe7950567a39bc9451adb5672de14f835ec111fed30bb941bd02d4"]},
      "expected": "iniciar somente o daemon identificado e registrar identidade/saúde",
      "observed": "NOT_RUN", "result": "NOT_RUN", "evidence_refs": []
    },
    {
      "id": "RCP-EXTENSION-VALIDATE-001",
      "executable": "/Users/paulosoares/.local/bin/compozy",
      "argv": ["extension", "validate", ".planning/power/features/specflow-m01/probe/fixture/extension"],
      "cwd": "/Users/paulosoares/Projetos/skills-ia/pwdev-claude-marketplace/.worktrees/pwdev-composyos",
      "mutable_scope": [".planning/power/features/specflow-m01/probe/fixture/extension", ".planning/power/features/specflow-m01/probe/evidence/extension-validate.json"],
      "approved_scope": {"run_id": "power-approval-run:34e912e8035ae3868d153e64c3a64d72b69a5e4e57a7767fd9bc7a3f4933ce70", "gate_id": "gate:specflow-m01:runtime-recipe", "decision_id": "decision:17fae407c996e1e19c03ff37b1877c27b7d5279a778853602df946826ab059c7", "actor_ref": "human:user", "decision": "approved", "decided_at": "2026-09-13T08:53:00Z", "artifacts": [{"checkout_ref": {"workspace_id": "specflow-m01", "worktree_id": null, "checkout_root": "/Users/paulosoares/Projetos/skills-ia/pwdev-claude-marketplace/.worktrees/pwdev-composyos", "revision_ref": "fb146297d681a1a6a77d71b5c30772655802590a"}, "path": ".planning/power/features/specflow-m01/probe-recipe-approved-snapshot.md", "sha256": "c606ebbf29d30881e54dd3e66c58d7e273a5f4bf6d49fd60b980e2171240b7c4", "role": "contract"}], "prerequisites": ["power-gate:techspec:09bde614371cb465ea1c135244bd6c4e8cc3f3e62c0c9fdeb3dc065d70ab54f3", "power-gate:tasks:1efe23df5abe7950567a39bc9451adb5672de14f835ec111fed30bb941bd02d4"]},
      "expected": "validar apenas o bundle sintético confinado sem executar seu código",
      "observed": "NOT_RUN", "result": "NOT_RUN", "evidence_refs": []
    },
    {
      "id": "RCP-EXTENSION-DEV-001",
      "executable": "/Users/paulosoares/.local/bin/compozy",
      "argv": ["extension", "dev", ".planning/power/features/specflow-m01/probe/fixture/extension", "--workspace", "specflow-m01-probe-20260913"],
      "cwd": "/Users/paulosoares/Projetos/skills-ia/pwdev-claude-marketplace/.worktrees/pwdev-composyos",
      "mutable_scope": [".planning/power/features/specflow-m01/probe/fixture/extension", ".planning/power/features/specflow-m01/probe/runtime/workspace-specflow-m01-probe-20260913.json", ".planning/power/features/specflow-m01/probe/evidence/extension-dev.json"],
      "approved_scope": {"run_id":"power-approval-run:34e912e8035ae3868d153e64c3a64d72b69a5e4e57a7767fd9bc7a3f4933ce70","gate_id":"gate:specflow-m01:runtime-recipe","decision_id":"decision:17fae407c996e1e19c03ff37b1877c27b7d5279a778853602df946826ab059c7","actor_ref":"human:user","decision":"approved","decided_at":"2026-09-13T08:53:00Z","artifacts":[{"checkout_ref":{"workspace_id":"specflow-m01","worktree_id":null,"checkout_root":"/Users/paulosoares/Projetos/skills-ia/pwdev-claude-marketplace/.worktrees/pwdev-composyos","revision_ref":"fb146297d681a1a6a77d71b5c30772655802590a"},"path":".planning/power/features/specflow-m01/probe-recipe-approved-snapshot.md","sha256":"c606ebbf29d30881e54dd3e66c58d7e273a5f4bf6d49fd60b980e2171240b7c4","role":"contract"}],"prerequisites":["power-gate:techspec:09bde614371cb465ea1c135244bd6c4e8cc3f3e62c0c9fdeb3dc065d70ab54f3","power-gate:tasks:1efe23df5abe7950567a39bc9451adb5672de14f835ec111fed30bb941bd02d4"]},
      "expected": "vincular somente a extensão sintética ao workspace dedicado após gate",
      "observed": "NOT_RUN", "result": "NOT_RUN", "evidence_refs": []
    },
    {
      "id": "RCP-LOOP-VALIDATE-001",
      "executable": "/Users/paulosoares/.local/bin/compozy",
      "argv": ["loop", "validate", "--file", ".planning/power/features/specflow-m01/probe/fixture/specflow-m01-loop.yaml", "--name", "specflow-m01-qualification", "--workspace", "specflow-m01-probe-20260913"],
      "cwd": "/Users/paulosoares/Projetos/skills-ia/pwdev-claude-marketplace/.worktrees/pwdev-composyos",
      "mutable_scope": [".planning/power/features/specflow-m01/probe/fixture/specflow-m01-loop.yaml", ".planning/power/features/specflow-m01/probe/evidence/loop-validate.json"],
      "approved_scope": {"run_id":"power-approval-run:34e912e8035ae3868d153e64c3a64d72b69a5e4e57a7767fd9bc7a3f4933ce70","gate_id":"gate:specflow-m01:runtime-recipe","decision_id":"decision:17fae407c996e1e19c03ff37b1877c27b7d5279a778853602df946826ab059c7","actor_ref":"human:user","decision":"approved","decided_at":"2026-09-13T08:53:00Z","artifacts":[{"checkout_ref":{"workspace_id":"specflow-m01","worktree_id":null,"checkout_root":"/Users/paulosoares/Projetos/skills-ia/pwdev-claude-marketplace/.worktrees/pwdev-composyos","revision_ref":"fb146297d681a1a6a77d71b5c30772655802590a"},"path":".planning/power/features/specflow-m01/probe-recipe-approved-snapshot.md","sha256":"c606ebbf29d30881e54dd3e66c58d7e273a5f4bf6d49fd60b980e2171240b7c4","role":"contract"}],"prerequisites":["power-gate:techspec:09bde614371cb465ea1c135244bd6c4e8cc3f3e62c0c9fdeb3dc065d70ab54f3","power-gate:tasks:1efe23df5abe7950567a39bc9451adb5672de14f835ec111fed30bb941bd02d4"]},
      "expected": "validar a definição sintética sem salvar",
      "observed": "NOT_RUN", "result": "NOT_RUN", "evidence_refs": []
    },
    {
      "id": "RCP-LOOP-CREATE-001",
      "executable": "/Users/paulosoares/.local/bin/compozy",
      "argv": ["loop", "create", "--file", ".planning/power/features/specflow-m01/probe/fixture/specflow-m01-loop.yaml", "--expected-version", "0", "--workspace", "specflow-m01-probe-20260913"],
      "cwd": "/Users/paulosoares/Projetos/skills-ia/pwdev-claude-marketplace/.worktrees/pwdev-composyos",
      "mutable_scope": [".planning/power/features/specflow-m01/probe/fixture/specflow-m01-loop.yaml", ".planning/power/features/specflow-m01/probe/runtime/loop-owned.json", ".planning/power/features/specflow-m01/probe/evidence/loop-create.json"],
      "approved_scope": {"run_id":"power-approval-run:34e912e8035ae3868d153e64c3a64d72b69a5e4e57a7767fd9bc7a3f4933ce70","gate_id":"gate:specflow-m01:runtime-recipe","decision_id":"decision:17fae407c996e1e19c03ff37b1877c27b7d5279a778853602df946826ab059c7","actor_ref":"human:user","decision":"approved","decided_at":"2026-09-13T08:53:00Z","artifacts":[{"checkout_ref":{"workspace_id":"specflow-m01","worktree_id":null,"checkout_root":"/Users/paulosoares/Projetos/skills-ia/pwdev-claude-marketplace/.worktrees/pwdev-composyos","revision_ref":"fb146297d681a1a6a77d71b5c30772655802590a"},"path":".planning/power/features/specflow-m01/probe-recipe-approved-snapshot.md","sha256":"c606ebbf29d30881e54dd3e66c58d7e273a5f4bf6d49fd60b980e2171240b7c4","role":"contract"}],"prerequisites":["power-gate:techspec:09bde614371cb465ea1c135244bd6c4e8cc3f3e62c0c9fdeb3dc065d70ab54f3","power-gate:tasks:1efe23df5abe7950567a39bc9451adb5672de14f835ec111fed30bb941bd02d4"]},
      "expected": "publicar somente o Loop sintético com CAS inicial no workspace dedicado",
      "observed": "NOT_RUN", "result": "NOT_RUN", "evidence_refs": []
    },
    {
      "id": "RCP-LOOP-DRY-RUN-001",
      "executable": "/Users/paulosoares/.local/bin/compozy",
      "argv": ["loop", "run", "--dry-run", "--name", "specflow-m01-qualification", "--network", "local", "--workspace", "specflow-m01-probe-20260913", "--config-file", ".planning/power/features/specflow-m01/probe/fixture/run-config.yaml"],
      "cwd": "/Users/paulosoares/Projetos/skills-ia/pwdev-claude-marketplace/.worktrees/pwdev-composyos",
      "mutable_scope": [".planning/power/features/specflow-m01/probe/fixture/run-config.yaml", ".planning/power/features/specflow-m01/probe/evidence/loop-dry-run.json"],
      "approved_scope": {"run_id":"power-approval-run:34e912e8035ae3868d153e64c3a64d72b69a5e4e57a7767fd9bc7a3f4933ce70","gate_id":"gate:specflow-m01:runtime-recipe","decision_id":"decision:17fae407c996e1e19c03ff37b1877c27b7d5279a778853602df946826ab059c7","actor_ref":"human:user","decision":"approved","decided_at":"2026-09-13T08:53:00Z","artifacts":[{"checkout_ref":{"workspace_id":"specflow-m01","worktree_id":null,"checkout_root":"/Users/paulosoares/Projetos/skills-ia/pwdev-claude-marketplace/.worktrees/pwdev-composyos","revision_ref":"fb146297d681a1a6a77d71b5c30772655802590a"},"path":".planning/power/features/specflow-m01/probe-recipe-approved-snapshot.md","sha256":"c606ebbf29d30881e54dd3e66c58d7e273a5f4bf6d49fd60b980e2171240b7c4","role":"contract"}],"prerequisites":["power-gate:techspec:09bde614371cb465ea1c135244bd6c4e8cc3f3e62c0c9fdeb3dc065d70ab54f3","power-gate:tasks:1efe23df5abe7950567a39bc9451adb5672de14f835ec111fed30bb941bd02d4"]},
      "expected": "pré-visualizar Network Local sem criar Run",
      "observed": "NOT_RUN", "result": "NOT_RUN", "evidence_refs": []
    },
    {
      "id": "RCP-LOOP-RUN-001",
      "executable": "/Users/paulosoares/.local/bin/compozy",
      "argv": ["loop", "run", "--name", "specflow-m01-qualification", "--network", "local", "--workspace", "specflow-m01-probe-20260913", "--config-file", ".planning/power/features/specflow-m01/probe/fixture/run-config.yaml"],
      "cwd": "/Users/paulosoares/Projetos/skills-ia/pwdev-claude-marketplace/.worktrees/pwdev-composyos",
      "mutable_scope": [".planning/power/features/specflow-m01/probe/fixture/run-config.yaml", ".planning/power/features/specflow-m01/probe/runtime/run-owned.json", ".planning/power/features/specflow-m01/probe/evidence/loop-run.json"],
      "approved_scope": {"run_id":"power-approval-run:34e912e8035ae3868d153e64c3a64d72b69a5e4e57a7767fd9bc7a3f4933ce70","gate_id":"gate:specflow-m01:runtime-recipe","decision_id":"decision:17fae407c996e1e19c03ff37b1877c27b7d5279a778853602df946826ab059c7","actor_ref":"human:user","decision":"approved","decided_at":"2026-09-13T08:53:00Z","artifacts":[{"checkout_ref":{"workspace_id":"specflow-m01","worktree_id":null,"checkout_root":"/Users/paulosoares/Projetos/skills-ia/pwdev-claude-marketplace/.worktrees/pwdev-composyos","revision_ref":"fb146297d681a1a6a77d71b5c30772655802590a"},"path":".planning/power/features/specflow-m01/probe-recipe-approved-snapshot.md","sha256":"c606ebbf29d30881e54dd3e66c58d7e273a5f4bf6d49fd60b980e2171240b7c4","role":"contract"}],"prerequisites":["power-gate:techspec:09bde614371cb465ea1c135244bd6c4e8cc3f3e62c0c9fdeb3dc065d70ab54f3","power-gate:tasks:1efe23df5abe7950567a39bc9451adb5672de14f835ec111fed30bb941bd02d4"]},
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

## Recibo canônico pré-Run

Serialização: UTF-8, LF, sem espaço final e exatamente uma LF final. `run_id` usa
`power-approval-run:` seguido do SHA-256 dos bytes canônicos:

```text
schema=specflow.power-approval-run.v1
feature=specflow-m01
task=M01.05
checkout_revision=fb146297d681a1a6a77d71b5c30772655802590a
snapshot_sha256=c606ebbf29d30881e54dd3e66c58d7e273a5f4bf6d49fd60b980e2171240b7c4
```

`decision_id` é `decision:` seguido do SHA-256 destes bytes exatos (UTF-8/LF, uma LF final):

```text
schema=specflow.power-approval-decision.v1
run_id=power-approval-run:34e912e8035ae3868d153e64c3a64d72b69a5e4e57a7767fd9bc7a3f4933ce70
gate_id=gate:specflow-m01:runtime-recipe
actor_ref=human:user
decision=approved
decided_at=2026-09-13T08:53:00Z
snapshot_sha256=c606ebbf29d30881e54dd3e66c58d7e273a5f4bf6d49fd60b980e2171240b7c4
techspec_sha256=09bde614371cb465ea1c135244bd6c4e8cc3f3e62c0c9fdeb3dc065d70ab54f3
tasks_sha256=1efe23df5abe7950567a39bc9451adb5672de14f835ec111fed30bb941bd02d4
```

Os IDs futuros do Loop pertencem a namespace distinto e não substituem este recibo Power pré-Run.

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
