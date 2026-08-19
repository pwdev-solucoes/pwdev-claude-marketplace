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

# Is cmux answering right now?
power_cmux_alive() {
  local bin=$1 socket
  socket=$(power_cmux_socket)
  [[ -S $socket ]] || return 1
  CMUX_SOCKET_PATH=$socket "$bin" ping >/dev/null 2>&1
}

# Start cmux and wait for its socket to answer.
#
# Only launch paths ask for this, and they announce it. Starting a GUI application is a visible
# thing to do to someone's screen, and starting one in order to *close* a workspace would be
# absurd — so teardown and the dashboard never call it.
#
# Whatever cmux does on startup, including reopening a previously saved session, is the app's own
# configured behaviour. This function starts it the same way the human would and then waits; it
# does not choose what the app restores.
power_cmux_start() {
  local bin=$1 bundle deadline timeout=${POWER_CMUX_START_TIMEOUT:-90}

  # /Applications/cmux.app/Contents/Resources/bin/cmux -> /Applications/cmux.app
  bundle=${bin%/Contents/Resources/bin/cmux}
  if [[ $bundle != "$bin" && -d $bundle ]]; then
    open -a "$bundle" >/dev/null 2>&1 || return 1
  elif command -v open >/dev/null 2>&1; then
    open -a cmux >/dev/null 2>&1 || return 1
  else
    return 1
  fi

  # Poll rather than sleep a guessed constant: a cold start can take a minute, and a warm one is
  # ready in seconds. The socket path itself can change across a restart, so re-resolve it every
  # round instead of caching the one that existed before.
  deadline=$((SECONDS + timeout))
  while [[ $SECONDS -lt $deadline ]]; do
    power_cmux_alive "$bin" && return 0
    sleep 1
  done
  return 1
}

# Fail closed. A fleet that cannot reach cmux must say so, not quietly run somewhere the human
# cannot see it.
#
# Pass --start from a launch path to have a stopped cmux started rather than reported. Set
# POWER_CMUX_NO_AUTOSTART=1 to turn that back off without editing the caller.
power_cmux_require() {
  local bin socket start=false
  [[ ${1:-} == --start && ${POWER_CMUX_NO_AUTOSTART:-0} != 1 ]] && start=true
  if ! bin=$(power_cmux_bin); then
    printf 'cmux: CLI not found. Install cmux, or set PWDEV_POWER_CMUX_BIN to its path.\n' >&2
    return 2
  fi

  if [[ $start == true ]] && ! power_cmux_alive "$bin"; then
    printf 'cmux: not running; starting it and waiting for its socket\n' >&2
    if power_cmux_start "$bin"; then
      printf 'cmux: started\n' >&2
    else
      printf 'cmux: could not start cmux within %ss. Start it yourself and retry.\n' \
        "${POWER_CMUX_START_TIMEOUT:-90}" >&2
      return 2
    fi
  fi

  socket=$(power_cmux_socket)
  if [[ ! -S $socket ]]; then
    printf 'cmux: no socket at %s. Start cmux and retry.\n' "$socket" >&2
    return 2
  fi
  local ping_error
  if ! ping_error=$(CMUX_SOCKET_PATH=$socket "$bin" ping 2>&1); then
    # Distinguish "not running" from "running but refusing you". By default cmux only accepts
    # connections from processes it started, so an agent launched from an ordinary terminal
    # gets a live socket and a closed door — and "did not answer" would send someone looking
    # for a crashed app that is in fact running fine.
    case $ping_error in
      *"Access denied"*|*"only processes started inside cmux"*)
        printf 'cmux: the socket refused this process. cmux only accepts connections from processes it started.\n' >&2
        printf 'cmux: run this session from a terminal inside cmux, or allow local processes in cmux settings.\n' >&2
        ;;
      *)
        printf 'cmux: socket at %s did not answer ping. Start cmux and retry.\n' "$socket" >&2
        ;;
    esac
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

# Resolve a short ref (workspace:12) to its UUID.
#
# Refs are positional: they shift as workspaces open and close. Resolve one the moment it is
# minted and never cache it, or the id recorded for a member can end up pointing at somebody
# else's workspace — and teardown closes by id.
power_cmux_resolve_workspace_ref() {
  local ref=$1
  [[ -n $ref ]] || return 2
  power_cmux list-workspaces --json --id-format both 2>/dev/null \
    | jq -er --arg ref "$ref" '
        .workspaces[]? | select(.ref == $ref) | .id
        | select(type == "string" and length > 0)
      ' 2>/dev/null
}

# Create one workspace for a fleet member and print its UUID.
#
# --focus false is not optional: creating a workspace that grabs focus is a click in the
# human's face, and the human may be reading something else entirely.
#
# cmux 0.64.22 ignores --json and --id-format on new-workspace, in either flag position, and
# answers with a bare "OK workspace:12" on stdout. Parsing that as JSON fails, which used to
# take the whole fleet launch down at its first workspace. Both paths are kept: the JSON one
# so a build that honours the flags is used directly, and the ref one because it is what works
# today. The UUID requirement itself is not negotiable — the member record binds teardown to an
# id, and "close only what I created" is only provable against an id.
power_cmux_new_workspace() {
  local name=$1 cwd=$2 command=$3 out id ref
  out=$(power_cmux --json --id-format uuids new-workspace \
        --name "$name" --cwd "$cwd" --command "$command" --focus false 2>/dev/null) || return 1

  if id=$(printf '%s' "$out" | jq -er '
    ( .workspace_id // .workspaceId // .workspace.id // .id )
    | select(type == "string" and length > 0)
  ' 2>/dev/null); then
    printf '%s\n' "$id"
    return 0
  fi

  # sed, not grep: a caller running with `set -o pipefail` would see a non-matching grep fail
  # the whole pipeline before the explicit emptiness check below can report it properly.
  ref=$(printf '%s' "$out" | sed -n 's/.*\(workspace:[0-9][0-9]*\).*/\1/p' | head -1)
  [[ -n $ref ]] || return 1
  id=$(power_cmux_resolve_workspace_ref "$ref") || return 1
  [[ -n $id ]] || return 1
  printf '%s\n' "$id"
}

# Create the panel workspace from a layout and print its UUID.
#
# A panel is one workspace holding one pane per member, built in a single call. That is not a
# cosmetic choice: each layout surface carries its own `command`, so the member's session is
# launched the same way the autonomous runner is — through a shell-quoted file, never typed into
# a shell. Building the same grid with new-split plus send would reintroduce exactly the
# injection and timing bugs fleet-up.sh:274 exists to avoid.
#
# Nesting `direction` nodes inside `children` is undocumented — the cmux --help examples only
# show one level — but 0.64.22 accepts it, which is what makes a 2x2 grid one call instead of
# three.
power_cmux_new_workspace_layout() {
  local name=$1 cwd=$2 layout=$3 out ref id
  out=$(power_cmux new-workspace --name "$name" --cwd "$cwd" --layout "$layout" --focus false 2>/dev/null) \
    || return 1
  ref=$(printf '%s' "$out" | sed -n 's/.*\(workspace:[0-9][0-9]*\).*/\1/p' | head -1)
  [[ -n $ref ]] || return 1
  id=$(power_cmux_resolve_workspace_ref "$ref") || return 1
  [[ -n $id ]] || return 1
  printf '%s\n' "$id"
}

# Close only a surface whose id we recorded ourselves.
#
# Members of a panel share one workspace, so tearing one member down must close its surface.
# Closing the workspace would take every sibling with it.
# The workspace is not optional: cmux refuses an explicit --surface without --workspace or
# --window, and it is the right thing to pass anyway — the id came from a member record that
# names both.
power_cmux_close_surface() {
  local id=$1 workspace=$2
  [[ -n $id && -n $workspace ]] || return 2
  power_cmux close-surface --surface "$id" --workspace "$workspace" >/dev/null 2>&1
}

# surface-health is workspace-scoped and defaults to the caller's, which for an agent launched
# outside cmux is whatever happens to be selected. Pass the workspace the member was recorded in,
# or the answer is about somebody else's panel.
power_cmux_surface_exists() {
  local id=$1 workspace=$2
  [[ -n $id && -n $workspace ]] || return 2
  power_cmux surface-health --workspace "$workspace" --id-format uuids 2>/dev/null \
    | grep -qF "$id"
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
