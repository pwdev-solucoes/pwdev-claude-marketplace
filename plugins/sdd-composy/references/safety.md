# SDD Composy safety contract

These constraints apply to every skill, deterministic helper, autonomous loop, fleet member, and runtime adapter.

## Repository and secret boundaries

- Operate only inside the repository and explicitly authorized writable locations. Inspect Git status first and preserve unrelated user changes.
- Never read or expose `.env`, credentials, tokens, private keys, certificates, secret-manager values, or existing fleet environment files. Clearly non-secret examples such as `.env.example` may be inspected.
- Never read, display, migrate, reuse, adopt, or audit an existing fleet environment file. Only the packaged fleet lifecycle may generate its own isolated runtime file.
- Stop and request a sanitized substitute when a task would require secret contents.
- Reject symlinked or non-regular operational inputs and destination chains where a regular owned file is required. Confine evidence and state paths to their approved roots.

## Mutation integrity

- Preserve unknown JSON fields during supported updates.
- Validate schemas before publication, write through same-directory temporary files, and atomically replace destinations.
- Append semantic events only after the represented action succeeds ([trace.md](trace.md)).
- Report Markdown/JSON conflicts before writing and require an explicit resolution ([synchronization.md](synchronization.md)).
- Never overwrite existing governance files, symlinks, `.agents`, or `.claude` paths. Initialization creates missing files and diagnoses conflicts.

## Human authority and scope

- Never infer human approval from artifact existence, metadata, prior summaries, or model confidence.
- Never let autonomous execution change approved requirements, stories, architecture, acceptance criteria, or scope.
- Stop on any terminal reason of the loop contract ([loop.md](loop.md)): scope, architecture, destructive work, external authorization, no progress, environment failure, cancellation.
- Do not commit, push, create or rewrite branches, publish, deploy, install globally, or mutate external services without explicit authorization.

## Fleet and evidence

- Never merge fleet branches automatically. Fleet branches and worktrees remain recoverable after failure, and integration requires explicit authorization.
- Reject fleet work that fails the admission criteria in [fleet.md](fleet.md).
- Presentation adapters never own process lifecycle truth. Losing a cmux, tmux, or headless presentation must not fabricate completion or release owned work unsafely.
- Accept only confined, hashed evidence as defined in [artifacts.md](artifacts.md) ("Synchronization and evidence").
- Run commands that directly support completion claims. Distinguish test failures, environment failures, and unverified assumptions; stale output and another worker's summary are not proof.
