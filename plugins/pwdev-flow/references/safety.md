# PWDEV Flow safety policy

Apply these rules to every Flow skill and delegated worker.

## Repository boundaries

- Read and write only within the repository and explicitly authorized writable locations.
- Inspect working-tree status before editing and preserve unrelated user changes.
- Do not delete, revert, overwrite, or clean files outside the exact task scope.
- Prefer reversible edits and validate exact targets before destructive operations.

## Secrets

- Never read or expose `.env` files, credentials, access tokens, private keys, certificates, or secret-manager values.
- Configuration examples may be inspected only when clearly non-secret, such as `.env.example`.
- Never read, display, migrate, audit, reuse, or adopt `.env.fleet`; only the packaged fleet lifecycle may generate it inside its isolated worktree.
- Stop and ask for a sanitized substitute when completion would require secret contents.

## Git and external effects

- Do not commit, push, create branches, rewrite history, publish packages, deploy, send messages, or mutate external services without explicit user authorization.
- Do not install global dependencies or change system configuration.
- Treat network calls, dependency installation, and external CLI delegation as separate actions subject to runtime approval rules.
- Treat `--dangerously-bypass-approvals-and-sandbox` as fleet-only authorization for the exact acknowledged autonomous command. Never add it to standalone delegation or reuse its acknowledgement for another command.
- For standalone delegation, confirm the complete expanded provider argument vector and pass only its byte-bound preview token. Any provider, repository, mode, model, argument, prompt, or task change invalidates that confirmation.
- Reject symlinked or non-regular Flow state, contract, configuration, log, result, runtime, and lifecycle destination chains. Publish owned files through same-directory temporaries and atomic renames where the packaged lifecycle defines them.
- Keep ownership of every dangerous fleet process group until group absence is proven. Terminal state, audit, commits, subsequent stages, and runner-lock release must follow that proof; an unresolved group retains the lock for explicit recovery.

## Evidence

- Run the command that directly proves each completion claim.
- Distinguish test failures, environment failures, and unverified assumptions.
- Never claim success from stale output or another agent's summary.

## Audit and migration

- Record semantic metadata only; never store command environment dumps or file contents in audit detail.
- Reject secret-like detail keys and targets before appending an event.
- Keep legacy migration source files unchanged and create Flow targets exclusively.
- Preview exact archive and migration targets before any move or copy.
- Never use maintenance as permission to delete historical artifacts.
- Keep fleet and delegation state under `.planning/flow/`; never write Flow results back into legacy `.planning/fleet` or `.planning/delegation` paths.
