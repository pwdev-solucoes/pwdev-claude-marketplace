---
okf_version: "0.2"
type: reference
title: "Headless runtime contract for benchmarks"
generated:
  by: "agent:claude"
  at: "2026-09-13T21:40:00Z"
lifecycle:
  status: draft
sources:
  - resource: "scripts/runtimes.py"
  - resource: "plugins/sdd-composy/scripts/loop-engine-claude.py"
    context: "Command vectors this marketplace already runs in its fleets."
  - resource: "https://developers.openai.com/api/docs/models"
    context: "Official model identifiers and prices used by the pricing table."
verified: []
---

# Headless runtime contract

`scripts/runtimes.py` runs one prompt in one isolated workspace on one runtime and
returns the same record for every runtime. This skill ships in the `pwdev-skills` plugin; the
runtimes below are the ones it measures, independently of where the plugin itself is installed. Read this when running or interpreting
`scripts/bench.py`, or when a runtime changes its CLI.

## Discovery first

`scripts/discover.py` (read-only) answers what can run here before anything is planned:

| Runtime | Signed in | Default model / effort | Models listed |
| --- | --- | --- | --- |
| Claude Code | `claude auth status` — method, provider and plan only; e-mail and organization are dropped | `~/.claude/settings.json`, env `CLAUDE_EFFORT` | no listing command: aliases from `claude --help` plus `~/.claude.json` `additionalModelOptionsCache`; full ids are accepted too |
| Codex CLI | `codex login status` | `~/.codex/config.toml`, else the model's `default_reasoning_level` | `codex debug models`, entries with `visibility: list`, with effort levels, context and the pricing table |
| Hermes Agent | `hermes status` — names of providers marked ✓; key fragments are never kept | `~/.hermes/config.yaml` | `~/.hermes/provider_models_cache.json` for the configured provider |
| OpenCode | `opencode providers list` — credential count | `~/.config/opencode/opencode.json[c]`, else the built-in default | `opencode models --verbose`: variants, context, price, free flag |

`bench.py --runtimes auto` runs every runtime discovery marks usable (Hermes still needs its
model chosen by the user). Model ids passed to `bench.py` must come from this report.

## Command vectors

| Runtime | Vector (fixed part) | Model | Skill exposure |
| --- | --- | --- | --- |
| Claude Code | `claude -p <prompt> --output-format json --no-session-persistence --dangerously-skip-permissions --add-dir <ws>` | `--model <id>`, `--max-budget-usd <x>` | `--plugin-dir <run>/plugin` — a generated plugin holding one copy of the skill |
| Codex CLI | `codex exec --json --ephemeral --skip-git-repo-check --dangerously-bypass-approvals-and-sandbox --cd <ws> --output-last-message <f> <prompt>` | `-m <slug>` | `<ws>/AGENTS.md` pointing at `<ws>/skills/<name>/SKILL.md` (Codex has no plugin-dir flag; this measures execution, not native catalogue discovery) |
| OpenCode | `opencode run --format json --dir <ws> --dangerously-skip-permissions <prompt>` | `-m <provider>/<model>`, `--variant <low\|medium\|high…>`; omit `-m` for the configured default (`opencode/big-pickle` with no config on 2026-09-13) | **native**: `<ws>/.opencode/skills/<name>/SKILL.md`, loaded through OpenCode's `skill` tool; the harness runs `git init` in the workspace so discovery stops there instead of walking up. Global skills in the user's profile still load |
| Hermes Agent | `TERMINAL_CWD=<ws> hermes -z <prompt> --in <ws> --no-restore-cwd --usage-file <f> --yolo --accept-hooks` | `-m <model> --provider <p>`; omit `-m` to use the configured model (`--hermes-model default`) | `<ws>/AGENTS.md` pointing at `<ws>/skills/<name>/SKILL.md` — `--skills` only accepts names Hermes already trusts, and trusting the workspace would edit the user's config. `TERMINAL_CWD` is mandatory: Hermes' shell and file tools anchor on it, not on the process cwd or `--in` (without it the agent worked from the user's home and timed out) |

The bypass flags are acceptable only because the working directory is a throw-away
workspace and every protected path (the skill in the repository, the version copies) is
fingerprinted before and after the call: any change outside the workspace fails the run.
Hermes additionally requires `hermes_automation_acknowledged=True`
(`bench.py --acknowledge-hermes-automation`); never add `--ignore-rules` or `--safe-mode`.

## What each runtime reports

| Field | Claude Code | Codex CLI | Hermes Agent | OpenCode |
| --- | --- | --- | --- | --- |
| Result text | `result` in the JSON envelope (`type: result`, `subtype: success`, `is_error: false`) | file named by `--output-last-message` | stdout | `text` events, joined |
| Usage | `usage.{input_tokens, output_tokens, cache_read_input_tokens, cache_creation_input_tokens}` | last `turn.completed` event: `usage.{input_tokens, cached_input_tokens, output_tokens}` | `--usage-file` JSON: token counts, `model`, `api_calls`, estimated cost | sum of every `step_finish.part.tokens {input, output, reasoning, cache.read, cache.write}`; `input` excludes cache |
| Cost | `total_cost_usd` (real) | none — computed from `usage` × pricing table (`cost_source: pricing_table`) | estimated by Hermes (`cost_source: estimated`) | sum of `step_finish.part.cost`, priced by OpenCode from models.dev (`cost_source: runtime`); 0 for free Zen models |
| Model observed | keys of `modelUsage` | any event carrying `model` | `model` in the usage file | not in events — read from `opencode export <sessionID>` (`modelID`, `providerID`, `variant`) |
| Other | `duration_ms`, `num_turns`, `session_id` | event count | `api_calls` | steps, tools used, whether the `skill` tool was called |

`record.json` (one per run): `runtime`, `version`, `model_requested`, `model_observed`,
`status` (`PASS` envelope ok · `FAIL` non-zero exit or bad envelope or protected path changed ·
`BLOCKED` timeout or missing consent · `NOT_RUN` executable or model rejected, or budget),
`reason`, `exit_code`, `started_at`, `ended_at`, `duration_seconds`,
`usage.{input_tokens, output_tokens, cache_read_tokens, cache_write_tokens, total_tokens}`,
`usage_source`, `cost_usd`, `cost_source`, `command` (sanitized), `protected_changed`,
`stdout_path`, `stderr_path`, `result_path`.

## Rules the adapters enforce

- A model id the runtime rejects is `NOT_RUN` with the runtime's message. Nothing is
  substituted, and no id is invented: pass exactly the identifiers the runtime documents.
- A provider quota or usage-limit refusal ("hit your usage limit", rate limit, insufficient
  credits) is also `NOT_RUN`: the run proves nothing about the skill. Observed on
  2026-09-13 for Codex (ChatGPT plan quota, reset 2026-09-19).
- A run stopped by `--max-budget-usd` is `NOT_RUN` for the same reason, and its cost is still
  recorded: Claude returns `subtype: error_max_budget_usd`, `terminal_reason: budget_exhausted`
  and the amount already charged. Usage and cost are parsed before the exit code is judged, so a
  failed run never reports a null cost — the protocol puts failures in the numerator of cost per
  success. Size the cap from the model's observed rate, not from the cheapest model's bill: on
  2026-09-13 the same review case cost US$ 0.08 per 100k context tokens on `claude-sonnet-5` and
  US$ 13.7 per 100k on `claude-fable-5-1`.
- Protected-path fingerprints skip `__pycache__/` and `*.pyc`: the interpreter running the
  harness writes those, not the run. `record.protected_diff` lists what did change.
- The child process gets a minimal environment (`PATH`, `HOME`, `USER`, `TMPDIR`, locale)
  and its own process group; a timeout sends `SIGTERM` then `SIGKILL` to the group.
- Every stored string is passed through `sanitize()`: `token=`, `api_key=`, bearer headers
  and `/Users/<name>` paths are redacted before anything is written.
- Versions come from `<binary> --version` at run time and are written into `summary.json`.
- Every record carries `model_effective`/`effort_effective` with their source, and the observed
  model where the runtime reports one. Omitting effort is a choice to use the configured default,
  recorded as such; `--<runtime>-effort` passes it explicitly (`--effort`, `-c model_reasoning_effort=`,
  `--reasoning`, `--variant`).
- `opencode export` is written to a file: piped, it is cut at 64 KiB. A provider 5xx or overload
  ("service temporarily overloaded") is `NOT_RUN`.

- OpenCode can exit `0` after an `error` event (rate limit, provider failure). An error event is
  never a `PASS`; a rate-limit message is `NOT_RUN`. Free Zen models are rate-limited.

## Observed on 2026-09-13

`claude` 2.1.270, `codex-cli` 0.153.4, `Hermes Agent v0.21.1`, `opencode` 1.17.11 (no provider
credentials: only the seven free `opencode/*` Zen models were available). The pricing table in
`evals/evals.json` (`matrix.pricing`) is dated and sourced; refresh it before claiming
Codex costs.
