---
name: sdd-init
description: >
  Initialize or resume the SDD Composy workspace of a repository: preview missing
  governance and OKF bundle files, apply only approved absent paths, persist the
  artifact language, and verify. Use when a project needs SDD set up or resumed —
  'inicializar o SDD', 'configurar o workspace SDD', 'run init first', or when any
  SDD skill returned not_initialized. Do NOT use for generic CLAUDE.md or repository
  setup outside SDD Composy, or for other plugins' init.
metadata:
  version: 0.1.0
---

# SDD Init

Initialize or resume the repository contract shared by every supported runtime: governance
files, the `.claude -> .agents` compatibility link, and the `tasks/index.md` OKF v0.2 bundle root.
The bundled `scripts/sdd_init.py` helper owns safe-path checks, atomic no-overwrite publication,
template rendering, conflict tokens, and verification; this skill owns intent, approval,
routing, and reporting. Script paths are relative to the plugin root (`${CLAUDE_PLUGIN_ROOT}` on
Claude Code; the installed plugin or linked skill folder elsewhere).

## Inputs

- Repository root: the current repository unless the user supplies another real directory.
- Actor ID: ask when absent; it must use the `provider:name` form required by the helper
  (for example `agent:sdd-init` or `human:paulo`).
- Language: pass `--lang pt-BR` or `--lang en-US`. If omitted on the first init, present the
  helper's `choices` result and ask the user to choose; do not generate artifacts yet. Only the
  approved apply persists the preference in `.planning/sdd-composy/config.json`; later runs reuse it.
- Optional arguments: pass through the requested repository path, actor, and exact plan token.

Initialization reads only the packaged templates and the helper's allow-listed repository metadata.

## Procedure

1. Resolve the repository root and actor without changing project files.
2. Run the preview and present its JSON result, including actions, conflicts, unchanged paths,
   and `plan_token`:

   ```sh
   python3 "${CLAUDE_PLUGIN_ROOT}/scripts/sdd_init.py" plan <repo> --actor <actor> [--lang pt-BR|en-US]
   ```

3. If conflicts are present, stop and explain them. Applying a brownfield repository requires the
   exact `plan_token` returned by the preview; never invent or shorten it. Only after the user
   approves that exact plan, run:

   ```sh
   python3 "${CLAUDE_PLUGIN_ROOT}/scripts/sdd_init.py" apply <repo> --actor <actor> --plan-token <plan_token> --lang <selected-language>
   ```

   With no conflicts, apply may use the plan output directly. The helper is idempotent and creates
   only absent paths.
4. Verify with the same actor and report its JSON result:

   ```sh
   python3 "${CLAUDE_PLUGIN_ROOT}/scripts/sdd_init.py" verify <repo> --actor <actor>
   ```

   A failed verification is a failed initialization: report `missing`, `index_ok`, and
   `claude_link_ok` without repairing or overwriting files.

## Read when

- `references/runtime.md` — the current runtime cannot be identified from the host's tools, or
  a `claude_compatibility` value other than `symlink` needs explaining.

## Output

Return the helper's result and a concise summary: repository root, actor, created paths,
conflicts, and verification status. Preserve the source commit and actor metadata the helper
recorded. Do not interpret the repository or add architectural intent; mapping is a later stage.

Safety: Do not commit, push, or publish. Do not read or expose `.env`, credentials, tokens, private keys, certificates, or fleet environment files. Full contract: `references/safety.md`.
