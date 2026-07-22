# External CLI Delegation Protocol

Shared contract for the delegation commands (`/pwdev-code:codex`,
`/pwdev-code:opencode`, `/pwdev-code:kimi`, `/pwdev-code:gemini`,
`/pwdev-code:kiro`, `/pwdev-code:delegate`) and the runner script
`${CLAUDE_PLUGIN_ROOT}/scripts/run-agent.sh`.

## 1. Architecture

```text
Claude Code (orchestrator)
   │
   ├── /pwdev-code:codex      ─┐
   ├── /pwdev-code:opencode    │
   ├── /pwdev-code:kimi        ├── /pwdev-code:delegate (auto-select)
   ├── /pwdev-code:gemini      │
   └── /pwdev-code:kiro       ─┘
         │
         ▼
   run-agent.sh <agent> <write|read> "<task>"
   (allowlist → safety prompt → timeout → write-lock → audit)
         │
         ▼
   External CLI works in the SAME repository
         │
         ▼
   Claude reviews git status / git diff, runs tests,
   and gives its OWN critical verdict (never commits)
```

Claude never applies the delegated change itself and never rubber-stamps the
agent's summary. The external agent produces the diff; Claude owns the review.

## 2. Supported agents & installation

| Agent | Binary | Non-interactive invocation | Best for | Install |
|-------|--------|---------------------------|----------|---------|
| Codex CLI | `codex` | `codex exec "<prompt>"` | Objective implementation, bugfixes, tests | `npm i -g @openai/codex` |
| OpenCode | `opencode` | `opencode run [--model M] "<prompt>"` | Provider/model flexibility | `curl -fsSL https://opencode.ai/install \| bash` or `npm i -g opencode-ai` |
| Kimi Code CLI | `kimi` | `kimi --quiet --prompt "<prompt>"` (older versions: positional prompt — the script auto-detects) | Large repos, extensive refactors | `curl -LsSf https://code.kimi.com/install.sh \| bash` |
| Gemini CLI | `gemini` | `gemini [--model M] --prompt "<prompt>"` | Broad-context analysis, docs, review (read-only by default) | `npm i -g @google/gemini-cli` |
| Kiro CLI | `kiro-cli` | `kiro-cli chat --no-interactive [--trust-all-tools] "<prompt>"` | Agentic/spec-driven implementation, AWS-stack tasks | official installer at https://kiro.dev (headless docs: https://kiro.dev/docs/cli/headless/) |

Model/auth environment variables respected natively by the CLIs (the script
does not reimplement them): `OPENCODE_MODEL`, `GEMINI_MODEL`, `KIRO_API_KEY`
(enables Kiro headless auth, skipping browser login).

Each CLI must be authenticated once interactively (run it standalone) before
delegation can work non-interactively.

## 3. Configuration (optional)

Delegation works with zero config. To customize per agent, add entries to
`.planning/config.json` under the same `external_models` namespace already
used by the `/pwdev-code:review` external reviewer:

```json
"external_models": {
  "reviewer": { "cmd": "codex exec", "enabled": false, "timeout_s": 300 },
  "codex":    { "timeout_s": 600 },
  "opencode": { "model": "anthropic/claude-sonnet-4-5" },
  "gemini":   { "model": "gemini-2.5-pro", "timeout_s": 900 },
  "kimi":     { "extra_args": "" },
  "kiro":     { "timeout_s": 900 }
}
```

Per-agent keys (all optional): `model` (passed as `--model` where supported),
`timeout_s` (default 600), `extra_args` (verbatim extra CLI flags).
Timeout precedence: config `timeout_s` > env `DELEGATE_TIMEOUT_S` > 600.
Model precedence: config `model` > native env var > CLI default.
Unlike `reviewer`, delegation agents need no `enabled` flag — they only run
when a human invokes a delegation command.

## 4. The mandatory safety prompt

`run-agent.sh` wraps every task in a standardized prompt (source of truth:
the `build_prompt` function in the script). It states the repo path, the MODE
(WRITE or READ-ONLY), and 10 non-negotiable rules:

1. NEVER run `git commit`, `git push`, or any history-modifying command.
2. NEVER read or modify `.env` files, secrets, credentials, keys, or tokens.
3. Respect the project's conventions, style, and CLAUDE.md instructions.
4. After code changes, run the relevant tests and report their result.
5. Stay strictly within the scope of the task — no drive-by changes.
6. NEVER delete or rewrite files unrelated to the task.
7. NEVER create branches, change git config, or touch CI/CD credentials.
8. NEVER install global dependencies or modify anything outside the repo.
9. If the task is ambiguous or risky, stop and report instead of guessing.
10. End with a concise summary: what changed, what was tested, open concerns.

## 5. Safety protocol (enforced by script + command)

- **Allowlist.** Only `codex`, `opencode`, `kimi`, `gemini`, `kiro` — the
  script exits 2 for anything else. No arbitrary command execution.
- **Human confirmation.** The command shows the EXACT `run-agent.sh` line and
  requires explicit confirmation before the FIRST external run in a session
  (same rule as `/pwdev-code:review` STEP 3.5). Never runs silently.
- **Timeout.** Every run is wrapped in `timeout`/`gtimeout` (warn-and-continue
  if the binary is missing).
- **Write lock.** In write mode the script holds `.planning/delegation/.lock`
  (mkdir-lock, released on exit). Two concurrent write delegations are
  impossible by construction — the second exits 4.
- **Read-only verification.** The script snapshots `git status --porcelain`
  before the run; in read mode any working-tree change afterwards →
  `READ-ONLY VIOLATION`, exit 3.
- **Output artifact.** stdout is mirrored (`tee`) to
  `.planning/delegation/<UTC-timestamp>-<agent>.md` when `.planning/` exists.
- **Audit.** Best-effort log:
  `audit-log.sh event delegate DELEGATE external_run <agent> '{"mode":...,"exit":...,"timeout_s":...}'`.
- **No safe interpolation shortcuts.** The task/prompt is always passed as a
  single quoted argument — never interpolated into a shell string.

Script exit codes: `0` ok · `2` usage/allowlist · `3` read-only violation ·
`4` write lock held · `124` timeout · `127` CLI not installed.

## 6. Agent selection matrix (used by /pwdev-code:delegate)

| Task nature | Agent | Why |
|-------------|-------|-----|
| Objective implementation, bugfix, well-scoped tests | codex | strongest direct non-interactive execution |
| A specific model/provider was requested, or flexibility matters | opencode | `--model` / `OPENCODE_MODEL` routing |
| Large repo, extensive refactor, many files | kimi | long-context exploration |
| Agentic/spec-driven implementation, AWS-stack tasks | kiro | spec-driven agent, AWS tooling |
| Analysis, architecture, documentation, second opinion | gemini | broad context; read-only by default |

Rules: ONE primary agent per task; a second agent only for read-only review;
announce the choice and the reason before executing; if the chosen CLI is not
installed, announce the fallback (next candidate or Claude-only).

## 7. Mandatory review checklist (Claude, after EVERY delegation)

Never skip, even on exit 0:

1. `git status --short` — list every touched file.
2. `git diff --stat`, then read the FULL `git diff` (per-file if large).
3. Scope check — flag files outside the task scope; flag ANY touch of
   `.env*`, secrets, lockfiles not implied by the task, or CI configs.
4. Run the relevant test suite yourself (do not trust the agent's claim).
5. Critical evaluation with your OWN judgment: correctness, conventions,
   simplicity, missing edge cases.
6. NEVER commit or push. If the result is bad, PROPOSE a revert
   (`git checkout -- <files>` / `git clean -n`) — never execute it without
   human confirmation.

Verdicts: `APPROVED FOR COMMIT` | `NEEDS ADJUSTMENTS` | `RECOMMEND REVERT`.
