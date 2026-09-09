# Fleet core

The fleet core accepts only ready task contracts with explicit acceptance criteria,
verification commands, complete dependencies, safe non-symlink paths, and no path
overlap. `launch.sh` creates a plugin-owned `sdd-fleet/<id>` branch and a sibling
worktree while leaving the central worktree untouched. Every member record binds the
task contract SHA-256, branch, and worktree. A lock serializes launch state and all
partial failures remove only worktrees created by that invocation; branches and
records remain recoverable. The core never merges branches or starts provider/UI
processes. `.env.fleet` is never read.
# Hermes fleet

O adapter `scripts/fleet/engine-hermes.sh` é o único ponto que constrói o vetor `hermes run`.
O runner continua responsável por locks, hashes, resultados e teardown. A rota Kanban é uma
integração futura/experimental e não deve ser tratada como validada sem Hermes real.
