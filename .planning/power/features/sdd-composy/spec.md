# SDD Composy — Design

Status: APPROVED
Source: approved design conversation
Updated: 2026-09-08

## Problem

The six skills in `formacao-inteligencia-artificial/spec-driven-development/processo/` define a useful sequential SDD workflow, but they lack a portable plugin boundary, persistent operational task state, codebase context, consolidated status, machine-verifiable traceability, bounded autonomous correction, and parallel execution. The new `sdd-composy` plugin must preserve the human-readable PRD-to-review workflow while adding those capabilities without depending on `pwdev-flow` at runtime.

The plugin must run from the same portable artifacts in Claude Code and Codex. A workflow started in one runtime must be resumable in the other.

## Approach

Create an independent marketplace plugin named `sdd-composy`. Adapt the six existing process skills into namespaced `sdd-*` skills and add initialization, codebase mapping, user stories, verification, status, trace, quick, loop, fleet, task-state, and synchronization capabilities.

Human contracts remain under `tasks/prd-<slug>/`. Operational state, projections, logs, and runtime bookkeeping live under `.planning/sdd-composy/`. Markdown remains the human contract format; validated JSON and JSONL provide operational state and traceability.

The lifecycle is:

```text
INIT -> MAP -> PRD -> STORIES -> TECHSPEC -> TASKS
                                            |
                              EXECUTE -> QA -> EVIDENCE -> REVIEW -> VERIFY
                                       ^       autonomous LOOP       |
                                       +-----------------------------+
                                            |
                                         COMPLETE
```

`QUICK` is a bounded reduced path. `FLEET` runs independent ready tasks in isolated Git worktrees. Fleet presentation prefers cmux and falls back to tmux or headless operation.

## Decisions

### Decision 1 — Independent plugin

- **Options:** copy all behavior; depend directly on `pwdev-flow`; build an independent plugin from adapted components.
- **Choice:** build an independent plugin from adapted components.
- **Why:** preserves portability and allows an SDD-specific artifact protocol without runtime coupling.
- **Trade-off:** deterministic helpers and fleet safeguards must be maintained separately.
- **Reversible:** yes; shared libraries may be extracted later if both plugins stabilize around the same contracts.

### Decision 2 — Dual artifact roots

- **Options:** move all artifacts under `.planning`; keep everything under `tasks`; separate human and operational artifacts.
- **Choice:** keep human contracts under `tasks/prd-<slug>/` and operational state under `.planning/sdd-composy/`.
- **Why:** preserves compatibility with the existing process while avoiding machine-state noise in product documents.
- **Trade-off:** synchronization and divergence detection are required.
- **Reversible:** partially; migration would require an explicit compatibility plan.

### Decision 3 — Portable Claude Code and Codex support

- **Options:** Codex only; Claude Code only; shared core with thin runtime adapters.
- **Choice:** shared skills, references, schemas, and scripts with thin runtime adapters.
- **Why:** the same workflow can resume across both runtimes.
- **Trade-off:** runtime-specific behavior must remain isolated and tested twice.
- **Reversible:** no without dropping an approved core capability.

### Decision 4 — User stories as a distinct gate

- **Options:** keep detailed stories inside the PRD; generate them during TechSpec; add `sdd-stories` between PRD and TechSpec.
- **Choice:** add `sdd-stories` after an approved PRD and before TechSpec.
- **Why:** product behavior, journeys, edge cases, and scenarios need refinement before architecture without turning the PRD into an implementation document.
- **Trade-off:** one additional artifact and gate for user-facing work.
- **Reversible:** yes; internal technical work may mark stories `NOT_APPLICABLE` with a justification.

### Decision 5 — Three state representations

- **Options:** one mutable JSON; Markdown only; separate operational state, event history, and derived trace.
- **Choice:** mutable validated task/state JSON, append-only semantic JSONL, and a rebuildable trace projection.
- **Why:** current state, historical audit, and relationship queries have different consistency requirements.
- **Trade-off:** projection rebuild and synchronization helpers are required.
- **Reversible:** no without losing either audit integrity or query clarity.

### Decision 6 — Bounded autonomous loop

- **Options:** approval per iteration; unbounded Ralph-style loop; bounded state-driven autonomy.
- **Choice:** autonomous `EXECUTE -> QA -> EVIDENCE (when required) -> REVIEW -> VERIFY` cycles with a default maximum of 3 iterations.
- **Why:** supports self-correction while retaining deterministic stopping conditions.
- **Trade-off:** some recoverable work will stop for a human after the cap.
- **Reversible:** yes through configuration within enforced safe limits.

### Decision 7 — Fleet UI adapters

- **Options:** cmux only; tmux only; execution core with cmux, tmux, and headless adapters.
- **Choice:** cmux preferred, tmux fallback, headless supported.
- **Why:** cmux provides a strong interactive experience but cannot be required in headless environments.
- **Trade-off:** UI handles and lifecycle behavior require adapter-specific validation.
- **Reversible:** yes; additional UI adapters can be added without changing the fleet state contract.

### Decision 8 — Safe initialization

- **Options:** overwrite governance files; create only missing files; merge automatically.
- **Choice:** create missing files, diagnose existing files, and require an explicit merge decision for conflicts.
- **Why:** repositories may already have authoritative governance.
- **Trade-off:** brownfield initialization can require a human decision.
- **Reversible:** yes.

### Decision 9 — Acceptance evidence as a distinct skill

- **Options:** keep evidence rendering inside QA; attach it to verification; add `sdd-evidence` between QA and review.
- **Choice:** add a dedicated `sdd-evidence` skill after QA and before review.
- **Why:** test execution, evidence publication, and adversarial verification have different responsibilities and failure modes.
- **Trade-off:** one additional artifact contract and lifecycle transition are required.
- **Reversible:** yes; evidence generation may remain optional when an approved task contract requires no dossier.

### Decision 10 — OKF v0.2 for generated Markdown

- **Options:** keep ad hoc Markdown; use OKF only for context; use OKF v0.2 for every project document generated by the plugin.
- **Choice:** every generated non-reserved project `.md` is an OKF v0.2 concept document; reserved `index.md` and `log.md` follow their OKF-specific structures.
- **Why:** stable metadata, provenance, lifecycle, verification, links, and progressive disclosure make SDD artifacts portable to humans and agents.
- **Trade-off:** initialization must collect an actor ID and deterministic linting is required.
- **Reversible:** partially; removing frontmatter would discard provenance and trust metadata.

## Interfaces

### Skill catalog

| Skill | Responsibility |
|---|---|
| `sdd-init` | Initialize, inspect, migrate, or resume the workspace and governance templates |
| `sdd-map` | Map project architecture, stack, domain, commands, conventions, and evidenced pitfalls |
| `sdd-prd` | Create and gate a product requirement |
| `sdd-stories` | Refine approved requirements into actors, journeys, stories, scenarios, and behavioral acceptance criteria |
| `sdd-techspec` | Specify architecture, components, contracts, integrations, and test cases |
| `sdd-tasks` | Generate, import, synchronize, query, and transition task state |
| `sdd-execute` | Implement one ready task and collect focused evidence |
| `sdd-qa` | Validate acceptance criteria and correct root-cause defects with regression tests |
| `sdd-evidence` | Validate an evidence manifest and publish a criterion-linked HTML/PDF acceptance dossier |
| `sdd-review` | Review conformity, architecture, code quality, tests, and security |
| `sdd-verify` | Adversarially reproduce evidence and verify completion claims |
| `sdd-status` | Aggregate lifecycle, gates, task progress, blockers, loop, trace, and fleet status read-only |
| `sdd-trace` | Record semantic events and build/query/verify traceability projections |
| `sdd-quick` | Deliver a bounded change through a reduced but verified workflow |
| `sdd-loop` | Run bounded autonomous implementation and correction cycles |
| `sdd-fleet` | Run independent ready tasks in isolated worktrees with UI adapters |
| `sdd-sync` | Detect and explicitly reconcile Markdown/JSON divergence |

### Human artifact interfaces

```text
tasks/prd-<slug>/
├── prd.md
├── stories.md
├── techspec.md
├── tasks.md
├── task_<n>.md
├── qa.md
├── evidence-report.html
├── evidence-report.pdf
├── codereview.md
└── evidences/
```

`stories.md` consumes an approved `prd.md` plus mapped project/domain context. It is required for user-facing behavior and externally consumed APIs. Pure internal work may mark it `NOT_APPLICABLE` with a recorded justification. TechSpec, tasks, QA, review, verification, and traceability consume its `US-*` and `SC-*` identifiers.

`tasks/` is an OKF v0.2 bundle. Its root `index.md` declares `okf_version: "0.2"`; every non-reserved generated Markdown document contains parseable YAML frontmatter with a non-empty `type`. Generated artifacts use `generated: { by, at }`, approved gates append `verified` events, upstream documents appear in `sources`, and timestamps use ISO 8601 with an explicit UTC offset. Reserved `index.md` and `log.md` retain their OKF semantics.

### Operational artifact interfaces

```text
.planning/sdd-composy/
├── config.json
├── state.json
├── context/{project,stack,domain,pitfalls}.md
├── context/codebase.json
├── tasks/index.json
├── tasks/<prd-slug>.json
├── trace/events.jsonl
├── trace/trace.json
├── loops/<loop-id>.json
├── fleet/<member-id>.json
├── fleet-results/
├── fleet-logs/
└── reports/
```

Acceptance evidence is stored below `tasks/prd-<slug>/evidences/` as a validated `manifest.json`, screenshots or attachments, and generated report formats. Every evidence file uses a confined repository-relative path and carries a SHA-256 digest. HTML content is escaped or sanitized; arbitrary manifest HTML is prohibited. PDF export is optional when no supported renderer is available, but a requested PDF fails if any expected image is not loaded.

### Governance templates

`sdd-init` provides templates for:

```text
AGENTS.md
CLAUDE.md
.agents/
├── rules/
│   ├── 00-sdd-composy.md
│   ├── architecture.md
│   ├── testing.md
│   └── workflow.md
└── skills/
```

`AGENTS.md` is canonical and records the codebase structure, workflow, commands, conventions, gates, artifact locations, and safety constraints. `CLAUDE.md` is a short compatibility document directing Claude Code to `AGENTS.md`. The `.claude` compatibility link targets `.agents` only when neither path already conflicts and the runtime contract confirms the directory layouts are compatible. Existing governance files or directories are never overwritten; conflicts are diagnosed and require an explicit merge decision.

### State helpers

```text
sdd_state.py inspect|transition|verify
sdd_tasks.py import|list|next|start|block|transition|verify|sync
sdd_trace.py record|build|query|verify
sdd_sync.py inspect|plan|apply
sdd_evidence.py build|verify|export
```

All mutations validate schemas, preserve supported unknown fields, write through same-directory temporary files, and atomically replace destinations. Synchronization reports conflicts before any write and never silently chooses Markdown or JSON.

### Task states

```text
pending -> ready -> running -> qa_required -> evidence_required -> review_required -> verify_required -> complete
                      |              |                    |                   |                |
                      +-> blocked     +-> rejected         +-> rejected        +-> rejected     +-> rejected

rejected -> ready
```

Additional terminal state: `skipped`, requiring an explicit justification. A task cannot become ready before dependencies are complete. A task cannot become complete without fresh test evidence, non-blocking QA and review, approved verification, and consistent traceability.

### Traceability model

The derived graph connects:

```text
PRD -> RF -> US -> SC -> CA -> TechSpec -> Task -> Code -> Test -> Evidence manifest -> Artifact hash -> Verdict
```

`events.jsonl` is append-only semantic history. `trace.json` is derived and never edited directly. It records the source event count and can be rebuilt and verified deterministically.

### Loop contract

The loop runs one task or feature through `sdd-execute`, `sdd-qa`, `sdd-evidence` when required, `sdd-review`, and `sdd-verify`. Default maximum: **3 iterations**. It stops on completion, iteration cap, missing progress, scope expansion, architectural ambiguity, destructive action, external authorization need, unrecoverable environment failure, or user cancellation. It resumes only from durably published stage state.

### Fleet contract

Fleet accepts only ready tasks with complete dependencies, explicit acceptance criteria, known verification commands, and no known overlapping paths. Each member receives an isolated Git worktree and operational record. Merge is never automatic and always requires explicit authorization.

The presentation driver order is `cmux -> tmux -> headless`. cmux operations are restricted to the workspace created by the plugin. Each member may have a workspace, pane, and surface handle. Completion, failure, or human-attention states may trigger a cmux flash. Process ownership, locks, worktrees, and task state remain independent of the UI driver.

## Constraints

- Support Claude Code and Codex from the same portable contracts.
- Plugin identifier and directory name are exactly `sdd-composy`.
- The plugin has no runtime dependency on `pwdev-flow` or `pwdev-feat`.
- Human contracts remain under `tasks/prd-<slug>/`.
- Operational state remains under `.planning/sdd-composy/`.
- Never read `.env`, credentials, tokens, private keys, certificates, or existing fleet environment files.
- Never overwrite existing governance files, symlinks, `.agents`, or `.claude` paths.
- Never infer human approval from artifact existence.
- Never edit `trace.json` directly or repair an invalid audit trail automatically.
- Never merge fleet branches automatically.
- Never let autonomous execution change approved requirements, stories, architecture, or scope.
- Evidence manifests accept only confined relative paths, known status/type enums, escaped or sanitized text, and verified regular files.
- All generated project Markdown conforms to OKF v0.2; runtime-facing `SKILL.md`, command adapters, and plugin documentation follow their host schemas instead of being treated as OKF bundle concepts.
- The default quick limit is **5 implementation files**; crossing it escalates to the full workflow.
- The default autonomous loop limit is **3 iterations**.
- Runtime-specific provider command vectors are built only in their dedicated adapters.
- cmux is a presentation adapter and must not own process lifecycle truth.

## Out of scope

- Reusing `pwdev-flow` files dynamically at runtime.
- Replacing project issue trackers or external project-management systems.
- Continuous telemetry for every model or tool invocation.
- Automatic approval of PRDs, stories, TechSpecs, plans, or merges.
- Automatic repair of malformed JSONL history or conflicting Markdown/JSON state.
- Reading or adopting existing secret environment files.
- Cloud orchestration or distributed execution outside the local Git/worktree model.

## Acceptance criteria

- AC-01: Both Claude Code and Codex discover and execute all 17 `sdd-*` skills from one plugin package.
- AC-02: `sdd-init` creates missing SDD state and governance files from templates without overwriting existing `AGENTS.md`, `CLAUDE.md`, `.agents`, or `.claude` paths.
- AC-03: When safe and compatible, initialization creates the approved `.claude` to `.agents` symbolic-link relationship and a `CLAUDE.md` pointer to canonical `AGENTS.md`; otherwise it reports an actionable conflict without mutation.
- AC-04: `sdd-map` produces human context documents and a structured codebase index using repository evidence without reading secrets.
- AC-05: An approved PRD can produce `stories.md` with stable `US-*` and `SC-*` identifiers that downstream artifacts reference.
- AC-06: `sdd-tasks` rejects invalid transitions and does not select a task whose dependencies are incomplete.
- AC-07: task state connects RF, US, SC, CA, test IDs, evidence, and verdicts without duplicating full upstream content.
- AC-08: semantic events append to valid JSONL only after their represented action succeeds.
- AC-09: `trace.json` can be rebuilt deterministically and integrity verification detects missing or dangling relationships.
- AC-10: `sdd-status` reports the lifecycle, last gate, task counts, blockers, loop state, fleet state, trace health, and exact next valid action without changing files.
- AC-11: `sdd-quick` escalates before editing when scope exceeds five implementation files or requires architecture, migration, destructive work, or unknown verification.
- AC-12: `sdd-loop` completes or stops according to explicit conditions and never exceeds three iterations by default.
- AC-13: the same persisted loop can resume from the last durable stage without repeating an already published successful stage.
- AC-14: fleet refuses tasks that are not ready, have incomplete dependencies, lack verification commands, or have confirmed path overlap.
- AC-15: fleet operates with cmux when available, falls back to tmux or headless, and does not depend on UI survival for lifecycle correctness.
- AC-16: fleet never merges without explicit authorization and preserves recoverable branches/worktrees after failure.
- AC-17: synchronization detects Markdown/JSON divergence and requires an explicit resolution before conflicting writes.
- AC-18: plugin manifests, skill frontmatter, JSON schemas, deterministic helpers, and both runtime adapters pass their applicable validators and tests.
- AC-19: `sdd-evidence` separates criterion result from evidence type and links every artifact to requirement, story, scenario, criterion, test, confined path, and SHA-256 digest.
- AC-20: evidence HTML sanitizes untrusted values, unknown statuses fail validation, and requested PDF export fails when expected images do not load.
- AC-21: every generated non-reserved project Markdown file contains OKF v0.2 frontmatter with non-empty `type`, valid timestamps, provenance, and lifecycle metadata appropriate to its gate.
- AC-22: deterministic linting validates the `tasks/` OKF bundle, reserved `index.md`/`log.md`, internal links, sources, generated actors, and verified human gates without rejecting permitted unknown extensions.

## Risks

- **Dual-source divergence:** Markdown contracts and JSON state may disagree. Mitigation: explicit authority boundaries, deterministic projections, and conflict-first synchronization.
- **Symlink incompatibility:** Claude and agent directory layouts may diverge or pre-exist. Mitigation: compatibility preflight and no overwrite policy.
- **Autonomous churn:** a loop may change code without converging. Mitigation: progress detection, three-iteration cap, scope binding, and fresh verification.
- **Parallel conflicts:** declared paths may miss dynamic overlap. Mitigation: advisory preflight plus strict integration review and no automatic merge.
- **Runtime drift:** Claude and Codex adapters may behave differently. Mitigation: shared schemas and cross-runtime contract tests.
- **Schema evolution:** persisted operational JSON may outlive plugin releases. Mitigation: versioned schemas, preserved unknown fields, and explicit migrations.
- **Context staleness:** the codebase map may drift. Mitigation: record the mapped commit and treat code as authoritative when contradicted.
- **Excessive process:** small changes may be slowed by the full workflow. Mitigation: bounded `sdd-quick` with automatic escalation boundaries.
- **OKF metadata drift:** document bodies and lifecycle frontmatter may disagree. Mitigation: deterministic OKF linting at generation, synchronization, status, and verification gates.
