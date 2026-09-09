---
name: sdd-init
description: >
  Initialize or resume an SDD Composy workspace safely. Inspect the repository,
  preview missing governance and OKF bundle files, apply only approved absent
  paths, and verify the resulting shared workspace. Use for SDD initialization,
  governance setup, or resuming an existing SDD Composy workspace.
metadata:
  version: 0.1.0
---

# SDD Init

Initialize the repository contract used by both Claude Code and Codex. The
portable workflow lives here; runtime entry points only route to this skill.
Read `references/runtime.md` for the adapter boundary and
`references/safety.md` for the shared safety contract before operating.

## Inputs

- Repository root: the current repository unless the user supplies another
  real directory.
- Actor ID: ask when absent; it must use the `provider:name` form required by
  the helper (for example `agent:sdd-init` or `human:paulo`).
- Language: pass `--lang pt-BR` or `--lang en-US` when selecting the workspace
  artifact language. If omitted on the first init, present the helper's
  `choices` result and ask the user to choose; do not generate artifacts yet.
  Only the approved apply persists the preference in
  `.planning/sdd-composy/config.json` and subsequent init runs reuse it.
- Optional arguments: preserve and pass through the requested repository path,
  actor, and exact plan token.

Never read `.env`, credentials, tokens, private keys, certificates,
or existing fleet environment files. Initialization only reads the packaged
templates and the helper's allow-listed repository metadata.

## Procedure

1. Resolve the repository root and actor without changing project files.
2. Run the shared helper's inspection/plan operation and present its JSON
   result, including actions, conflicts, unchanged paths, and `plan_token`.
   The helper is `${CLAUDE_PLUGIN_ROOT}/scripts/sdd_init.py` when invoked by
   Claude Code; runtimes without that variable should resolve the same bundled
   `scripts/sdd_init.py` path from the installed plugin.

   ```sh
   python3 "${CLAUDE_PLUGIN_ROOT}/scripts/sdd_init.py" plan <repo> --actor <actor> [--lang pt-BR|en-US]
   ```

   The helper exposes this preview as `inspect|plan`; use `plan` for the
   machine-readable preview consumed by the next step.
3. If conflicts are present, stop and explain them. Applying a brownfield
   repository requires the exact `plan_token` returned by the preview; never
   invent or shorten it. If the user approves applying that exact plan, run:

   ```sh
   python3 "${CLAUDE_PLUGIN_ROOT}/scripts/sdd_init.py" apply <repo> --actor <actor> --plan-token <plan_token> --lang <selected-language>
   ```

   With no conflicts, apply may use the plan output directly. The helper is
   idempotent and creates only absent governance paths, the `.claude ->
   .agents` compatibility link, and the `tasks/index.md` OKF v0.2 bundle root.
4. Run verification using the same actor and report its JSON result:

   ```sh
   python3 "${CLAUDE_PLUGIN_ROOT}/scripts/sdd_init.py" verify <repo> --actor <actor>
   ```

   A failed verification is a failed initialization; report `missing`,
   `index_ok`, and `claude_link_ok` without repairing or overwriting files.

## Output

Return the helper's result and a concise summary of the repository root, actor,
created paths, conflicts, and verification status. Preserve the source commit
and generated actor metadata recorded by the helper. Do not reinterpret the
map or add architectural intent; mapping is a later shared capability.

## Boundaries

The Python helper owns safe-path checks, atomic no-overwrite publication,
template rendering, conflict tokens, and verification. This skill owns intent,
approval, routing, and reporting only. Do not duplicate lifecycle gates,
artifact schemas, or runtime-specific policy here; follow the shared
references and let the helper enforce its write contract.
