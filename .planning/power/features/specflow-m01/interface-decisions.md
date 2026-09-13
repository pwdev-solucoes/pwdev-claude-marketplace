---
type: INTERFACE_DECISIONS
okf_version: "0.2"
generated:
  by: agent:pwdev-power
  at: "2026-09-13T10:00:00Z"
lifecycle:
  status: DRAFT
human_approval: PENDING
sources:
  - resource: tasks/prd-specflow/prd.md
  - resource: tasks/prd-specflow/stories.md
  - resource: .planning/power/features/specflow-m01/probe-recipe.md
verified: []
---

# M01 — decisões de interface propostas

As assinaturas são contratos de dados/nós propostos, não APIs já comprovadas do
CompozyOS. null significa não conhecido/não aplicável justificado; lista vazia somente
depois de consulta concluída. Timestamps são RFC3339 UTC, strings não vazias salvo
descrição explicitamente opcional.

- RuntimeRecipe = {id: string, executable: string, argv: string[], cwd: string, mutable_scope: string[], approved_scope: ApprovalRef|null, expected: string, observed: string, result: PASS|FAIL|ENVIRONMENT_FAILURE|NOT_RUN, evidence_refs: ArtifactRef[]}.
- QualificationCheck = {id: string, guarantee: string, positive_recipe: string, negative_recipe: string, revision_ref: string, result: PASS|FAIL|ENVIRONMENT_FAILURE|NOT_RUN, evidence_refs: ArtifactRef[]}.
- ResourceSet = {paths: string[], source_digests: object<string,string>, interfaces: string[], validation_refs: ArtifactRef[]}; representa recursos estáticos, sem estado operacional alternativo.

| CheckoutRef | workspace_id: string; worktree_id: string ou null; checkout_root: caminho absoluto resolvido pelo runtime; revision_ref: string com identidade de HEAD e alterações locais relevantes |
| ArtifactRef | checkout_ref: CheckoutRef; path: relativo ao checkout; sha256: 64 caracteres hex minúsculos; role: contract, evidence, verdict, report ou manifest |
| ApprovalRef | run_id, gate_id, decision_id, actor_ref: strings opacas/ator real; decision: approved, changes_requested ou rejected; decided_at: RFC3339 UTC; artifacts: ArtifactRef[] não vazio; prerequisites: decision_id[] |

Campos desconhecidos ficam null/unverified, nunca lista vazia interpretada como
sucesso. Lista vazia significa consulta concluída sem itens. Approvals precisam de
identidade humana comprovada pelo runtime.

## Estado observado na Task 07

O ApprovalRef renovado e os digests estavam frescos. O binding proposto
`resources.agents = ["agents"]` foi rejeitado por beta.25. Nenhuma sintaxe alternativa
é inferida; corrigir a fixture exige novo gate. Atomicidade, retomada, concorrência,
observação e isolamento permanecem NOT_RUN. STATUS: BLOCKED.
