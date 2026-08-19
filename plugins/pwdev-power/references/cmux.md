# cmux

cmux is the terminal surface this plugin orchestrates through. It replaces the tmux layer of
earlier PWDEV plugins, and it earns the swap by carrying state the human can see — sidebar
status, progress, colour, notifications — instead of a dashboard pane that has to be watched.

## Model

Four levels, plus one trap:

- **Window** — a top-level macOS window.
- **Workspace** — a tab-like group inside a window. The UI calls it a "tab"; the CLI calls it
  a workspace. This is the fleet member's unit.
- **Pane** — a split region inside a workspace.
- **Surface** — a tab inside a pane; terminal, browser, simulator or agent-session.

The trap: **focus is orthogonal to layout.** The workspace the human is looking at is not
presumptively your target. An agent can run in one workspace while the human reads another.

## Access

`scripts/cmux-common.sh` owns everything fragile. Resolve, in order:

- **Binary**: `$PWDEV_POWER_CMUX_BIN`, then `cmux` on `PATH`, then
  `/Applications/cmux.app/Contents/Resources/bin/cmux`. It is frequently not on `PATH`.
- **Socket**: `$CMUX_SOCKET_PATH`, then the path inside `/tmp/cmux-last-socket-path`, then
  `~/.local/state/cmux/cmux.sock`.

Then `cmux ping`. **Fail closed**: if the socket does not answer, cmux is not running. Say so
with the command to fix it and stop. Never degrade silently into doing the work somewhere the
human cannot see it.

**Launch paths may start it.** `power_cmux_require --start` opens the app and waits for its socket
— polling, because a cold start can take a minute and a warm one seconds, and because a restart can
move the socket path. It announces itself, and `POWER_CMUX_NO_AUTOSTART=1` turns it off. Only
`fleet-up.sh` and `fleet-panel-up.sh` ask for it: teardown, the runner's status publishing and the
Kanban bridge never do, because starting a GUI application in order to close a workspace would be
absurd. What cmux restores on startup is the app's own configured behaviour, not this plugin's
choice.

## Verbs this plugin uses

Deliberately few, mirroring the minimal tmux surface it replaces.

```bash
cmux ping
cmux list-workspaces --json
cmux --json --id-format uuids new-workspace \
  --name "power-fleet:<slug>" --cwd "<worktree>" --command "bash <pane-file>" --focus false
cmux close-workspace --workspace "<uuid>"
cmux capture-pane --workspace "<uuid>" --lines 200
```

Panel layout, which is how a visual fleet gets on screen:

```bash
cmux new-workspace --name "power-fleet panel" --cwd "<repo>" --layout "<json>" --focus false
cmux surface-health --workspace "<uuid>" --id-format uuids
cmux close-surface --surface "<uuid>"
```

Human-visible state, which is the actual reason for cmux:

```bash
cmux set-status power-fleet "<slug> <stage>" --workspace "<uuid>" --icon hammer --color "#ff9500"
cmux set-progress 0.5 --label "<stage>" --workspace "<uuid>"
cmux workspace-action --action set-color --color Green --workspace "<uuid>"
cmux notify --title "power-fleet: <slug>" --body "<one line>"
cmux markdown open <path> --focus false
```

Colour convention: amber while running, `Green` on DONE, `Red` on NEEDS_HUMAN.

## Identity

Record **UUIDs**, not names. Names are for humans and can collide; the UUID is what makes "close
only what I created" provable. Short refs (`workspace:2`) are fine in prose and examples, never in
state — refs are positional and shift as workspaces open and close.

**`new-workspace` does not return a UUID.** Verified against 0.64.22: it ignores both `--json` and
`--id-format uuids`, in either flag position, and answers `OK workspace:12` on stdout. So the ref
is parsed out of that line and resolved through `list-workspaces --json --id-format both`
immediately, while it still points at the workspace just created. `power_cmux_new_workspace` and
`power_cmux_new_workspace_layout` both do this; do not reintroduce a bare `jq` over that output.

A **surface** id cannot be resolved this way at all, because the panel creates four at once. Each
pane reports its own `CMUX_SURFACE_ID` instead — cmux auto-sets it in every terminal it owns, and
self-registration beats an index guess.

## Layout

`--layout` accepts **nested** `direction` nodes inside `children`, which is what makes a 2×2 grid a
single call. This is undocumented — the `--help` examples show only one level — and verified by
experiment, so treat it as a behaviour to re-check when cmux updates.

Each layout surface carries its own `command`, executed in that surface's shell. That is the whole
reason the panel is built this way instead of `new-split` plus `send`: a privileged command
belongs in a shell-quoted file, never typed into a live shell.

## What cmux does not give you

`cmux feed tui` and `feed.list` **do not see Claude Code.** The feed's bridge covers the agents
listed by `cmux hooks` — codex, opencode, hermes-agent and others — and Claude Code is not among
them; its hooks are injected by the cmux Claude wrapper and surface as **notifications** instead.
Verified with a live permission prompt pending: the feed stayed empty while `list-notifications`
carried `Claude Code | Claude is waiting for your input`, scoped to the right workspace. So the
attention layer for a Claude panel is `notify`, `trigger-flash` and `list-notifications` — not the
feed.

Surfaces of type `agentSession` are opaque to automation: `read-screen`, `capture-pane` and `send`
all refuse with `Surface is not a terminal`. A panel built on them could not be read or driven, so
this plugin builds panels out of terminal surfaces.

## Prohibitions

- **Never steal focus.** No `focus-pane`, `focus-panel`, `select-workspace`, or focus-changing
  `tab-action` unless the human asked for it in this session. These are clicks in the human's
  face. Pass `--focus false` on every creation and move.
- **Never close a workspace or surface whose UUID you did not record** in `fleet/<slug>.json`.
- **Never build a manifest by diffing against a baseline.** "Everything that was not here before is
  mine" also captures whatever the human opened meanwhile, and closing that is closing their work.
- **Never use focus as a workaround.** If the CLI rejects a target you believe is valid, report
  it and stop; do not focus something and retry.
- Avoid `drag-surface-to-split`: it resolves the workspace from UI focus and fails when the
  caller's workspace is not the visible one.
- Never write to `~/.config/cmux/cmux.json`. Terminal rendering belongs to Ghostty config and
  both belong to the human.

## Markdown for gates

`cmux markdown open <path> --focus false` puts a plan or spec in a formatted panel with live
reload. Write the whole file first, then open it — the panel never shows a half-written file.
Use it at approval gates so the human reads a rendered document instead of scrollback.
