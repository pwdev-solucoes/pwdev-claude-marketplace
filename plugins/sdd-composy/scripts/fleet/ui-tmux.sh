#!/usr/bin/env bash
# tmux is presentation only; it never owns fleet lifecycle state.
set -Eeuo pipefail

fleet_ui_tmux_start() {
  local handle=$1 cwd=$2 session=$3; shift 3
  [[ $# -gt 0 ]] || { echo "fleet tmux: command is required" >&2; return 2; }
  command -v tmux >/dev/null 2>&1 || { echo "fleet tmux: tmux unavailable" >&2; return 127; }
  [[ -d "$cwd" && ! -L "$cwd" ]] || { echo "fleet tmux: unsafe cwd" >&2; return 1; }
  [[ ! -e "$handle" && ! -L "$handle" ]] || { echo "fleet tmux: handle already exists" >&2; return 1; }
  if tmux has-session -t "$session" 2>/dev/null; then
    echo "fleet tmux: session collision: $session" >&2; return 1
  fi
  tmux new-session -d -s "$session" -c "$cwd" -- "$@"
  python3 - "$handle" "$session" "$cwd" <<'PY'
import json,sys
from pathlib import Path
Path(sys.argv[1]).write_text(json.dumps({'driver':'tmux','session':sys.argv[2],'cwd':sys.argv[3]},sort_keys=True)+'\n')
PY
}

fleet_ui_teardown() {
  local handle=$1 session
  [[ -f "$handle" && ! -L "$handle" ]] || return 1
  session=$(python3 - "$handle" <<'PY'
import json,sys
try: print(json.load(open(sys.argv[1]))['session'])
except Exception: raise SystemExit(1)
PY
  ) || return 1
  command -v tmux >/dev/null 2>&1 || return 1
  tmux kill-session -t "$session" 2>/dev/null || true
  rm -f -- "$handle"
}
