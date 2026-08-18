# Safety

## Read boundaries

Never read, print, or copy a secret. That includes `.env` and its environment variants,
`*.pem`, `*.key`, `id_rsa*`, credential stores, and any generated `.env.fleet`. `.env.example`,
`.env.template` and `.env.sample` are documentation and are allowed.

The packaged `guard-secrets.sh` enforces this on the Claude adapter as a `PreToolUse` hook.
The other runtimes have no equivalent hook, so on those the rule is yours to keep.

## Write boundaries

- Never write outside the repository, except where the human explicitly directs.
- **Never edit the user's own configuration.** Not `~/.hermes/SOUL.md`, not
  `~/.hermes/config.yaml`, not `~/.config/cmux/cmux.json`, not `~/.claude/settings.json`.
  When an integration is missing, print the exact command and let the human run it.
- Never commit on a default branch without explicit consent. Branch first.
- Never `git push`, open a pull request, or merge unless the human asked in this session.

## Privileged vectors

Three runtimes, three dangerous flags:

| Runtime | Flag | Meaning |
|---|---|---|
| Claude | `--dangerously-skip-permissions` | no permission prompts |
| Codex | `--dangerously-bypass-approvals-and-sandbox` | no approvals, no sandbox |
| Hermes | `--yolo` (plus `--accept-hooks`) | no dangerous-command approval, hooks auto-accepted |

Each vector is constructed in exactly one place — `fleet-engine-<runtime>.sh` — and nothing
else in this plugin may build a provider command or add a permission flag. Before the first
launch of a fleet, disclose the exact command shape of the runtime you are and require
explicit acknowledgement of its flag. No acknowledgement, no launch.

Never pass `--ignore-rules` or `--safe-mode` to Hermes: they strip `AGENTS.md`/`SOUL.md`
injection and disable plugins, which silently removes the very disciplines this plugin exists
to enforce.

## The fixed-runtime rule

The runtime is fixed by the launcher chosen before any mutation, is written into the fleet
member record, and a runner whose adapter disagrees with that record refuses to start. No
configuration value, environment variable, argument, or state field may turn one vector into
another. You are one runtime; use your own launcher and never another's.

## Destructive operations

- Never `rm -rf` a path you did not create in this session.
- Never `git worktree remove --force` on your own initiative. Show `git status --porcelain -uall`
  and offer choices.
- Never `docker compose down --volumes`. Teardown does not destroy data; it reports what it
  kept.
- Never close, focus, or send input to a cmux workspace whose identifier you did not record.
