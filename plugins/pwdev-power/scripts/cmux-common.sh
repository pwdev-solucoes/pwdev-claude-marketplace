#!/usr/bin/env bash
# cmux access layer. Every fragile thing about talking to cmux lives here: finding the binary,
# finding the socket, proving the daemon answers, and never stealing the human's focus.
#
# Source this; do not execute it.

# Resolve the CLI. cmux is frequently not on PATH even when the app is installed.
power_cmux_bin() {
  if [[ -n ${PWDEV_POWER_CMUX_BIN:-} && -x ${PWDEV_POWER_CMUX_BIN} ]]; then
    printf '%s\n' "$PWDEV_POWER_CMUX_BIN"; return 0
  fi
  local candidate
  if candidate=$(command -v cmux 2>/dev/null); then
    printf '%s\n' "$candidate"; return 0
  fi
  for candidate in \
    /Applications/cmux.app/Contents/Resources/bin/cmux \
    "$HOME/Applications/cmux.app/Contents/Resources/bin/cmux"
  do
    [[ -x $candidate ]] && { printf '%s\n' "$candidate"; return 0; }
  done
  return 1
}

# Resolve the socket. The path cmux itself last wrote wins over any default.
power_cmux_socket() {
  if [[ -n ${CMUX_SOCKET_PATH:-} ]]; then
    printf '%s\n' "$CMUX_SOCKET_PATH"; return 0
  fi
  local pointer=/tmp/cmux-last-socket-path recorded
  if [[ -f $pointer ]]; then
    recorded=$(<"$pointer")
    recorded=${recorded%%$'\n'*}
    [[ -n $recorded ]] && { printf '%s\n' "$recorded"; return 0; }
  fi
  printf '%s\n' "$HOME/.local/state/cmux/cmux.sock"
}

# Fail closed. A fleet that cannot reach cmux must say so, not quietly run somewhere the human
# cannot see it.
power_cmux_require() {
  local bin socket
  if ! bin=$(power_cmux_bin); then
    printf 'cmux: CLI not found. Install cmux, or set PWDEV_POWER_CMUX_BIN to its path.\n' >&2
    return 2
  fi
  socket=$(power_cmux_socket)
  if [[ ! -S $socket ]]; then
    printf 'cmux: no socket at %s. Start cmux and retry.\n' "$socket" >&2
    return 2
  fi
  if ! CMUX_SOCKET_PATH=$socket "$bin" ping >/dev/null 2>&1; then
    printf 'cmux: socket at %s did not answer ping. Start cmux and retry.\n' "$socket" >&2
    return 2
  fi
  POWER_CMUX_BIN=$bin
  POWER_CMUX_SOCKET=$socket
  export POWER_CMUX_BIN POWER_CMUX_SOCKET
  return 0
}

# Every call goes through here, with the socket pinned explicitly so automation is auditable.
power_cmux() {
  [[ -n ${POWER_CMUX_BIN:-} ]] || { printf 'cmux: power_cmux_require was not called\n' >&2; return 2; }
  CMUX_SOCKET_PATH=$POWER_CMUX_SOCKET "$POWER_CMUX_BIN" "$@"
}

# Create one workspace for a fleet member and print its UUID.
#
# --focus false is not optional: creating a workspace that grabs focus is a click in the
# human's face, and the human may be reading something else entirely.
power_cmux_new_workspace() {
  local name=$1 cwd=$2 command=$3 out id
  out=$(power_cmux --json --id-format uuids new-workspace \
        --name "$name" --cwd "$cwd" --command "$command" --focus false 2>/dev/null) || return 1
  id=$(printf '%s' "$out" | jq -er '
    ( .workspace_id // .workspaceId // .workspace.id // .id )
    | select(type == "string" and length > 0)
  ' 2>/dev/null) || return 1
  printf '%s\n' "$id"
}

# Close only a workspace whose id we recorded ourselves. The caller passes the id it stored;
# never resolve one by name here.
power_cmux_close_workspace() {
  local id=$1
  [[ -n $id ]] || return 2
  power_cmux close-workspace --workspace "$id" >/dev/null 2>&1
}

power_cmux_workspace_exists() {
  local id=$1
  [[ -n $id ]] || return 2
  power_cmux list-workspaces --json 2>/dev/null \
    | jq -e --arg id "$id" 'any(.. | objects | select((.id? // .workspace_id?) == $id); true)' >/dev/null 2>&1
}

# Human-visible state. All of it is best-effort: losing a status line must never fail a stage.
power_cmux_status()   { power_cmux set-status power-fleet "$2" --workspace "$1" --icon hammer --color "${3:-#ff9500}" >/dev/null 2>&1 || true; }
power_cmux_progress() { power_cmux set-progress "$2" --label "${3:-}" --workspace "$1" >/dev/null 2>&1 || true; }
power_cmux_color()    { power_cmux workspace-action --action set-color --color "$2" --workspace "$1" >/dev/null 2>&1 || true; }
power_cmux_notify()   { power_cmux notify --title "$1" --body "$2" >/dev/null 2>&1 || true; }
