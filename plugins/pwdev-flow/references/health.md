# Health diagnostic contract

Health evaluates the repository and PWDEV Flow workspace without fixing findings. Run only commands that are already available locally and distinguish product failures from missing tooling or unavailable external data.

## Modes

- `full` — Flow workspace, code quality, tests, documentation, Git, dependencies, and local security checks;
- `workspace` — Flow structure, state, gates, artifacts, memory, audit, and migration consistency;
- `deps` — declared dependencies, lockfiles, locally available audit commands, and stale-version evidence.

## Evidence collection

1. Read applicable `AGENTS.md`, Flow config/state, and repository manifests without reading secrets.
2. Validate required Flow paths, Markdown links, active phase artifacts, gate/state consistency, memory index targets, and audit JSONL integrity.
3. Discover verification commands from manifests and governance; do not guess package-manager commands.
4. Run existing lint, typecheck, test, or build commands only when they are safe and relevant to the selected mode.
5. Inspect Git status and recent history read-only.
6. Run dependency or vulnerability tools only when already installed. Network-backed checks require separate authorization and must state their freshness.
7. Search for secret-handling risks by filenames, configuration, and code patterns without opening prohibited secret files.

## Score

Score each observed area `A` through `F`:

- `A` — all required evidence passes and no material finding exists;
- `B` — minor non-blocking findings;
- `C` — material maintenance or coverage gaps;
- `D` — broken required checks or high-risk process gaps;
- `F` — critical vulnerability, data-loss risk, invalid audit, or unusable workflow state.

Use `N/A` when evidence does not apply or cannot be collected. Never convert missing evidence into a passing grade. One critical finding caps the overall score at `F`; any `D` caps it at `D`.

## Output

Report urgent findings first, then a scorecard with evidence command, result, confidence, and recommended next action. Do not implement fixes. Persist `.planning/flow/reports/health/<date>.md` or `deps/<date>.md` only when the user requests a report or an active Flow phase already authorizes it.
