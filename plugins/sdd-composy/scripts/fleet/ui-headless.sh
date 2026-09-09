#!/usr/bin/env bash
# Presentation-only detached runner. Lifecycle truth remains in fleet/run.sh.
set -Eeuo pipefail

fleet_ui_headless_start() {
  local handle=$1 cwd=$2 log=${SDD_FLEET_UI_LOG:-/dev/null}; shift 2
  [[ $# -gt 0 ]] || { echo "fleet headless: command is required" >&2; return 2; }
  [[ -d "$cwd" && ! -L "$cwd" ]] || { echo "fleet headless: unsafe cwd" >&2; return 1; }
  [[ ! -e "$handle" && ! -L "$handle" ]] || { echo "fleet headless: handle already exists" >&2; return 1; }
  mkdir -p "$(dirname "$handle")"
  (cd -- "$cwd" && exec nohup "$@" >"$log" 2>&1 </dev/null) &
  local pid=$!
  python3 - "$handle" "$pid" "$cwd" "$log" <<'PY'
import json,sys
from pathlib import Path
Path(sys.argv[1]).write_text(json.dumps({'driver':'headless','pid':int(sys.argv[2]),'cwd':sys.argv[3],'log':sys.argv[4]},sort_keys=True)+'\n')
PY
}

fleet_ui_teardown() {
  local handle=$1 pid
  [[ -f "$handle" && ! -L "$handle" ]] || return 1
  pid=$(python3 - "$handle" <<'PY'
import json,sys
try: print(int(json.load(open(sys.argv[1]))['pid']))
except Exception: raise SystemExit(1)
PY
  ) || return 1
  kill -TERM "$pid" 2>/dev/null || true
  local attempt=0
  while kill -0 "$pid" 2>/dev/null && (( attempt < 40 )); do sleep 0.05; attempt=$((attempt + 1)); done
  if kill -0 "$pid" 2>/dev/null; then
    echo "fleet headless: process did not terminate" >&2
    return 1
  fi
  rm -f -- "$handle"
}
