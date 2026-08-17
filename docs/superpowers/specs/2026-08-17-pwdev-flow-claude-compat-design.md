# PWDEV Flow — Native Claude Code Compatibility Design

Date: 2026-08-17

Status: APPROVED IN CONVERSATION — PENDING WRITTEN SPEC REVIEW

## Objective

Make `pwdev-flow` a first-class plugin for both Codex and Claude Code without duplicating workflow semantics or allowing one runtime's privileged execution vector to leak into the other.

The delivered package must:

- remain fully installable and functional in Codex;
- become natively installable and functional in Claude Code;
- expose all seventeen Flow capabilities as `/pwdev-flow:*` Claude commands;
- use Claude's native headless runtime for Claude fleet execution;
- preserve one portable `.planning/flow` artifact protocol across both runtimes;
- retain the semantic, opt-in JSONL audit without Claude hooks;
- register and document the plugin in the primary Claude marketplace.

## Approved decisions

1. Claude fleet uses native `claude -p`; Codex fleet continues to use `codex exec`.
2. Claude exposes all seventeen flows as commands:
   `init`, `discover`, `design`, `plan`, `execute`, `review`, `verify`, `simplify`, `quick`, `product`, `memory`, `health`, `audit`, `maintenance`, `compat`, `delegate`, and `fleet`.
3. Audit remains the shared semantic `flow_audit.py` implementation. Claude hooks are absent.
4. The architecture is a shared core with thin runtime adapters, not a duplicated Claude implementation and not a dynamically interchangeable privileged command.
5. The next shared base release is `0.6.0`. The Claude manifest uses semantic version `0.6.0`; the Codex manifest may receive its required cachebuster suffix during Codex installation.
6. No subagents, MCP servers, or hooks are introduced in this compatibility milestone.
7. No commit, push, or pull request is authorized by this design approval.

## Package architecture

`plugins/pwdev-flow` remains one source package:

```text
plugins/pwdev-flow/
├── .claude-plugin/plugin.json
├── .codex-plugin/plugin.json
├── commands/                     # seventeen Claude command adapters
├── skills/                       # seventeen portable Codex skills
├── references/                   # shared workflow and safety contracts
├── scripts/                      # shared lifecycle plus explicit runtime adapters
└── templates/                    # shared schemas and fleet assets
```

The root marketplace and documentation also change:

```text
.claude-plugin/marketplace.json   # add pwdev-flow
README.md                         # list and explain pwdev-flow
README.pt-BR.md                   # list and explain pwdev-flow
```

Both plugin manifests describe the same product and base release. Runtime-only metadata remains in the relevant manifest rather than being forced into a lowest-common-denominator schema.

## Claude command adapters

Each `commands/<name>.md` file is a thin native Claude entry point with standard frontmatter, an argument hint where applicable, and the public slash-command name `/pwdev-flow:<name>`.

An adapter must:

1. preserve `$ARGUMENTS` exactly as the user supplied it;
2. resolve package resources through `${CLAUDE_PLUGIN_ROOT}`;
3. read the corresponding portable `skills/flow-<name>/SKILL.md` completely;
4. follow the skill's referenced contracts under `references/`;
5. identify the active runtime as `claude` when initializing or updating portable state;
6. avoid restating or forking the workflow semantics in command prose.

The `compat` command maps to `flow-compat`. All other names map directly to `flow-<name>`.

This arrangement keeps Claude's discovery and UX native while leaving behavioral rules in the shared skills and references.

## Shared artifact protocol

Claude and Codex read and write the same `.planning/flow` structures and schemas. A workflow may be initialized in one runtime and continued in the other.

Portable configuration records the adapter that last initialized state through `runtime: "claude"` or `runtime: "codex"`; this field never makes the other runtime reject otherwise valid portable artifacts.

Fleet operational state is stricter. Every central fleet member must bind:

- fleet slug and branch;
- canonical initiating root and worktree;
- base branch and base commit;
- approved contract hashes;
- ports, Compose project, and tmux window;
- exact autonomous runtime, `claude` or `codex`.

Fleet runners must reject a member whose runtime does not match their fixed adapter.

## Autonomous runtime isolation

The privileged vectors are separate source-level entry points:

- Codex runner: the existing exact `codex exec --dangerously-bypass-approvals-and-sandbox ...` vector;
- Claude runner: an exact documented `claude -p ...` vector using Claude Code's native unattended permission mechanism.

No configuration value, environment variable, model setting, provider argument, or portable state field may transform one vector into the other. Runtime selection occurs when the explicit launcher is chosen, before any worktree or process mutation, and is recorded in the central member.

The shared lifecycle may provide validation, state publication, audit, dashboard, and teardown helpers, but command construction and permission flags remain inside the runtime-specific runner adapter.

Standalone external delegation remains separate from fleet execution and never inherits either fleet bypass mechanism.

## Claude fleet lifecycle

The Claude fleet follows the same approved lifecycle contract as Codex:

1. validate required tools, named base branch, safe configuration, approved contract files, paths, and capacity before mutation;
2. reserve central state and create an isolated `flow-fleet/<slug>` worktree;
3. copy and bind the exact approved contract bytes and hashes;
4. generate owned runtime assets through safe same-directory temporary publication;
5. start isolated Docker Compose resources and a tmux pane running the fixed Claude runner;
6. record `runtime: "claude"` and publish ACTIVE only after provisioning succeeds;
7. execute `plan → execute → review → verify`, with no more than two correction cycles;
8. validate fresh structured results before commit or stage transition;
9. prove the owned Claude process group is absent before validation, commit, terminal status, audit, later stages, or lock release;
10. merge only through explicit teardown with strict terminal-state and base-branch authorization.

Dashboard and teardown are shared only where their behavior is runtime-neutral. They validate the recorded runtime and refuse ambiguous or mismatched state.

## Audit

Audit remains opt-in through `.planning/flow/config.json` and is written by `flow_audit.py`.

Both runtimes use the same action vocabulary and timing:

- `fleet_launched` after durable ACTIVE state and successful tmux launch;
- `fleet_stage` after atomic stage-outcome publication;
- `fleet_teardown` after verified shutdown or merge outcome;
- `external_run` after a standalone delegated provider run.

Claude hooks are deliberately absent. This avoids runtime-exclusive telemetry being mistaken for a portable workflow trail.

## Safety and failure behavior

All existing repository and secret boundaries remain binding. In addition:

- Claude CLI availability is a pre-mutation requirement for Claude fleet launch;
- Codex CLI availability is not accepted as a substitute;
- a runtime mismatch fails before provider, Docker, tmux, merge, or state mutation;
- symlinked or wrong-type operational paths and destinations fail closed;
- existing runtime environment files are never read or adopted;
- malformed, stale, contradictory, or identity-mismatched state cannot authorize merge;
- signal and unexpected-error recovery retains ownership until the entire autonomous process group is proven absent;
- unresolved process ownership retains its recovery lock and cannot publish false terminal completion;
- audit failure remains a sanitized warning and never replaces the lifecycle result.

## Versioning and distribution

The compatibility release uses shared base version `0.6.0`.

- `.claude-plugin/plugin.json` contains `0.6.0` and Claude marketplace metadata.
- `.codex-plugin/plugin.json` is set to base `0.6.0` before the official Codex cachebuster is applied exactly once for installation.
- `.claude-plugin/marketplace.json` registers `pwdev-flow` using the conventions of `pwdev-code`.
- Root README files list the plugin, its dual-runtime support, seventeen commands, semantic audit, delegation, and isolated native fleets.

Claude and Codex installations must be validated independently from their respective installed copies, not only from the source tree.

## Test strategy

Implementation follows strict RED → GREEN cycles.

### Structural tests

Tests require:

- both manifests with compatible base versions;
- exactly seventeen Claude commands and seventeen Codex skills;
- one-to-one command-to-skill mapping;
- resolved `${CLAUDE_PLUGIN_ROOT}` resource references;
- preserved `$ARGUMENTS` behavior;
- Claude marketplace registration and README entries;
- absence of hooks, MCP servers, and apps;
- valid shared Markdown links and existing package invariants.

### Behavioral tests

All autonomous tests run in temporary Git repositories with fake executables. They require:

- Claude launch fails before mutation when `claude` is unavailable;
- Claude launcher records `runtime: "claude"`;
- Claude runner invokes the exact approved native Claude vector;
- Claude runner never contains the Codex dangerous flag or calls the Codex binary;
- Codex runner remains fixed to its existing exact vector;
- runtime mismatch blocks before external execution;
- approved contract hashes, path containment, atomic state, strict teardown, audit ordering, signal recovery, descendant termination, correction cap, and base-branch binding work for Claude;
- dashboard and teardown handle both explicit runtimes without weakening either contract;
- portable non-fleet artifacts can be continued across runtimes.

No real Claude, Codex, Docker, tmux, provider, or network process is invoked by tests.

### Regression and release gates

The release requires:

1. all existing Codex tests remain green;
2. all new Claude structural and behavioral tests pass;
3. shell, Python, JSON, frontmatter, links, placeholder, whitespace, and diff-integrity checks pass;
4. all Codex skills and the Codex plugin pass official validators;
5. the Claude plugin and marketplace pass the locally available Claude validation command;
6. source and both installed packages have the expected inventories and byte parity for their installation model;
7. the Codex cachebuster runs exactly once after the final source change;
8. local Codex and Claude installations are smoke-tested without launching real autonomous work;
9. an independent code review finds no Critical or Important issue.

## Documentation deliverables

Documentation must explain:

- how to install and update the plugin in Claude Code and Codex;
- the seventeen Claude commands;
- the shared `.planning/flow` protocol;
- which fleet runtime each host uses;
- the separate privileged vectors and their safety boundary;
- why audit is semantic and hook-free;
- how to migrate from `pwdev-code` without changing source artifacts;
- how to inspect, teardown, and recover fleet state.

## Out of scope

- Claude-specific subagents or model-routing profiles;
- Claude hooks or automatic tool telemetry;
- MCP servers or apps;
- changing the standalone provider allowlist;
- changing the portable Flow lifecycle semantics beyond runtime identity;
- publishing, pushing, committing, or opening a pull request;
- redesigning `pwdev-code`.

## Acceptance criteria

The milestone is complete when:

1. Claude Code discovers and exposes all seventeen `/pwdev-flow:*` commands.
2. Every command consumes the shared portable skill/reference contract.
3. Claude fleet uses only native Claude headless execution in an isolated fleet worktree.
4. Codex fleet continues to use only its existing Codex execution vector.
5. Runtime identity is bound and validated across launch, stages, dashboard, audit, and teardown.
6. Shared non-fleet artifacts are interoperable between Claude and Codex.
7. Both marketplaces and root documentation identify the plugin accurately.
8. All structural, behavioral, regression, validator, installation, parity, and review gates pass.
9. No real autonomous runtime or external provider is exercised during tests.
10. No Critical or Important review finding remains.
