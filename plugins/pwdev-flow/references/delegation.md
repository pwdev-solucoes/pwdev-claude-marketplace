# External delegation contract

Use this contract for standalone external coding CLI delegation, from either runtime. The primary agent owns provider choice, exact-command disclosure, first-run confirmation, host timeout, and independent review. The packaged `run-agent.sh` owns argument construction, locking, mutation detection, capture, and audit metadata.

## Provider matrix and binaries

| Task | Provider | Binary | Default mode |
|---|---|---|---|
| Bounded implementation, bug fix, or tests | Codex | `codex` | `write` |
| Explicit provider/model or routing flexibility | OpenCode | `opencode` | `write` |
| Large repository or extensive refactor | Kimi | `kimi` | `write` |
| Analysis, architecture, documentation, or second opinion | Gemini | `gemini` | `read` |
| Agentic/spec-driven or AWS work | Kiro | `kiro-cli` | `write` |

Accept only `codex`, `opencode`, `kimi`, `gemini`, and `kiro`, and only `read` or `write`. Announce an automatic selection and its reason. Honor an explicit allowlisted provider without silently substituting another.

## Configuration

Read only `.planning/flow/config.json`. Preserve unknown fields when another Flow operation updates it. Provider defaults are:

```json
{
  "external_models": {
    "codex": {"timeout_s": 600},
    "opencode": {"model": "provider/model", "timeout_s": 600},
    "kimi": {"timeout_s": 900},
    "gemini": {"model": "provider/model", "timeout_s": 600},
    "kiro": {"timeout_s": 900}
  }
}
```

Allow a positive integer `timeout_s` and a JSON array of string `extra_args`. Use a configured `model` as a typed `--model` value for Codex, OpenCode, and Gemini. Standalone Codex rejects every configured `extra_args` element fail-closed; its typed model field is the only optional provider argument. For other providers, pass each extra argument as one argument-vector element and never evaluate shell text. Reject arguments that change the repository root, add dangerous mode, replace mandatory prompts, or weaken Kiro read mode.

## Safe prompt

Build one standardized prompt that states the repository root, the exact task, and `READ-ONLY` or `WRITE`. Require the delegate to stay in scope, follow repository instructions, test changes, and return a concise summary. Prohibit:

- commits, pushes, branches, history edits, and Git configuration changes;
- `.env` or `.env.fleet` reads, secrets, credentials, keys, and tokens;
- global installs, external writes, deployments, and unrelated service mutation;
- deletion or rewriting of unrelated files and drive-by changes;
- guessing through ambiguity or risk.

Do not place prompts, model names, provider output, environment variables, or absolute worktree paths in semantic audit events.

## Command vectors

The runner builds arrays, never evaluated command strings:

```text
codex exec --ephemeral --cd <repository> [--model <model>] <safe-prompt>
opencode run [--model <model>] [extra_args...] <safe-prompt>
kimi --quiet [extra_args...] [--prompt] <safe-prompt>
gemini [--model <model>] [extra_args...] --prompt <safe-prompt>
kiro-cli chat --no-interactive [--trust-all-tools in write mode only] [extra_args...] <safe-prompt>
```

Standalone delegation never receives a fleet bypass vector: neither `--dangerously-bypass-approvals-and-sandbox` (Codex) nor `--dangerously-skip-permissions` (Claude). Kiro never receives `--trust-all-tools` in read mode.

Before every run, invoke the packaged runner in preview mode:

```text
bash <packaged-run-agent.sh> --preview <provider> <read|write> <task>
```

The preview prints the complete shell-escaped provider argument vector, including the standardized prompt as its final argument, and a confirmation token bound to those exact bytes as a SHA-256 digest, so task text cannot be crafted to make a stale token authorize a different vector. Require explicit confirmation of that exact expanded provider vector. Then execute the identical packaged runner invocation without `--preview` and with `FLOW_DELEGATION_CONFIRM_TOKEN` set to the displayed token. A missing or stale token fails before locks, output capture, or provider execution. Confirmation authorizes only that exact vector; any change to provider, task, mode, model, arguments, repository, or prompt requires a new preview and token. Set the host timeout to at least the configured script timeout plus 60 seconds.

## Read and write behavior

In `write` mode, acquire `.planning/flow/delegation/.lock` with one atomic directory creation and refuse another writer. Release only the owned lock.

In `read` mode, capture `git status --porcelain` before and after, excluding only `.planning/flow/delegation`. Any difference is a read-only violation. Report it and never revert automatically.

When Flow state exists, capture the standardized prompt and provider output in `.planning/flow/delegation/<timestamp>-<agent>.<unique>.md`. Treat that file as operational evidence, not proof. Never echo its contents into audit events. If neither `timeout` nor `gtimeout` is available, warn that the script cannot enforce its internal time limit; the host timeout remains mandatory.

## Exit codes

| Code | Meaning |
|---:|---|
| `2` | invalid input or configuration |
| `3` | read-only mutation violation |
| `4` | active write lock |
| `5` | exact expanded provider vector not confirmed, or confirmation token stale |
| `124` | timeout |
| `127` | selected provider binary missing |

Otherwise propagate the provider exit code. Always report the code, timeout, provider, mode, and output path when one exists. If `external_run` audit recording fails, emit only a concise semantic-action warning to stderr and preserve the provider result; never include prompt, model, output, environment, or path data in that warning.

## Mandatory independent review

After every delegation, including non-zero exits, the primary agent must:

1. inspect current Git status;
2. inspect the full unstaged and staged diff plus relevant untracked files;
3. compare all changes with the exact delegated task and repository rules;
4. run the relevant tests independently;
5. return an evidence-backed `APPROVED`, `CAVEATS`, or `REJECTED` verdict.

Never accept the delegated summary or its test claims as completion proof. When audit is enabled, record `external_run` only with provider, mode, exit code, timeout, and a safe relative target.
