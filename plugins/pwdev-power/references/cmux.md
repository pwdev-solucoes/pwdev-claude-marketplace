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

Record the **workspace UUID** returned by `new-workspace --id-format uuids`, not the name.
Names are for humans and can collide; the UUID is what makes "close only what I created"
provable. Short refs (`workspace:2`) are fine in prose and examples, never in state.

## Prohibitions

- **Never steal focus.** No `focus-pane`, `focus-panel`, `select-workspace`, or focus-changing
  `tab-action` unless the human asked for it in this session. These are clicks in the human's
  face. Pass `--focus false` on every creation and move.
- **Never close a workspace whose UUID you did not record** in `fleet/<slug>.json`.
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
