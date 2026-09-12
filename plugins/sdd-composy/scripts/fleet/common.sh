#!/usr/bin/env bash
# Provider-neutral fleet primitives.  This file deliberately owns no UI/processes.
set -euo pipefail

fleet_die() { echo "fleet: $*" >&2; return 1; }
fleet_abs() { python3 - "$1" <<'PY'
from pathlib import Path
import sys
p=Path(sys.argv[1])
print(p.absolute())
PY
}
fleet_safe_path() {
  local root="$1" path="$2"; [[ "$path" != /* ]] || return 1
  python3 - "$root" "$path" <<'PY'
from pathlib import Path
import sys
r=Path(sys.argv[1]).absolute(); p=(r/sys.argv[2]).absolute()
try: p.relative_to(r)
except ValueError: raise SystemExit(1)
for q in [r, *p.parents, p]:
    if q.exists() and q.is_symlink(): raise SystemExit(1)
PY
}
fleet_hash() { sha256sum "$1" 2>/dev/null | awk '{print $1}' || shasum -a 256 "$1" | awk '{print $1}'; }
fleet_lock() {
  local lock="$1" timeout="${2:-30}"; local end=$((SECONDS+timeout))
  while ! ( set -o noclobber; echo "$$" > "$lock" ) 2>/dev/null; do
    (( SECONDS >= end )) && fleet_die "lock timeout: $lock"
    sleep 0.05
  done
}
fleet_unlock() { rm -f -- "$1"; }
fleet_state_dir() { printf '%s/.planning/sdd-composy/fleet/%s\n' "$1" "$2"; }
fleet_require_regular() { [[ -f "$1" && ! -L "$1" ]]; }
fleet_json_string() { jq -er --arg key "$2" '.[$key] | select(type == "string" and length > 0)' "$1" 2>/dev/null; }
fleet_no_symlink_components() {
  python3 - "$1" <<'PY'
from pathlib import Path
import sys
p=Path(sys.argv[1])
for q in (p, *p.parents):
    if q.is_symlink() and str(q) not in ('/tmp','/private/tmp','/var'):
        raise SystemExit(1)
PY
}
# Select presentation only. The selected driver never changes fleet lifecycle truth.
fleet_select_ui() {
  local requested=${1:-auto}
  local cmux_bin="${SDD_CMUX_BIN:-cmux}"
  case "$requested" in
    headless) printf 'headless\n' ;;
    tmux) command -v tmux >/dev/null 2>&1 || { echo 'fleet: tmux unavailable' >&2; return 1; }; printf 'tmux\n' ;;
    cmux) command -v "$cmux_bin" >/dev/null 2>&1 || { echo 'fleet: cmux unavailable' >&2; return 1; }; printf 'cmux\n' ;;
    auto) if command -v "$cmux_bin" >/dev/null 2>&1; then printf 'cmux\n'; elif command -v tmux >/dev/null 2>&1; then printf 'tmux\n'; else printf 'headless\n'; fi ;;
    *) echo "fleet: unsupported UI driver: $requested" >&2; return 2 ;;
  esac
}
fleet_port_available() {
  python3 - "$1" <<'PY'
import errno,socket,sys
s=socket.socket(); s.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
try: s.bind(('127.0.0.1', int(sys.argv[1])))
except OSError as e:
    # Restricted CI sandboxes can deny bind() even when no listener exists.
    # Only a definitive address-in-use result makes the slot unavailable.
    raise SystemExit(1 if e.errno in (errno.EADDRINUSE, errno.EADDRNOTAVAIL) else 0)
finally: s.close()
PY
}
fleet_allocate_port() {
  local state="$1" start="${2:-43000}" end="${3:-43100}"; [[ "$start" =~ ^[0-9]+$ && "$end" =~ ^[0-9]+$ && "$start" -le "$end" ]] || fleet_die "invalid port range"
  local lock="$state/.ports.lock" p; mkdir -p "$state"
  fleet_lock "$lock" 30
  for ((p=start;p<=end;p++)); do
    [[ -e "$state/port-$p" ]] && continue
    fleet_port_available "$p" || continue
    ( set -o noclobber; printf '%s\n' "${FLEET_ID:-fleet}" > "$state/port-$p" ) 2>/dev/null || continue
    printf '%s\n' "$p"; fleet_unlock "$lock"; return 0
  done
  fleet_unlock "$lock"; fleet_die "no free port in range $start-$end"
}
fleet_write_runtime_env() {
  local state="$1" port="$2"; local env="$state/runtime.env"
  [[ ! -e "$env" && ! -L "$env" ]] || fleet_die "runtime env already exists"
  umask 077
  printf 'COMPOSE_PROJECT_NAME=sdd_fleet_%s\nSDD_FLEET_PORT=%s\n' "${FLEET_ID:-fleet}" "$port" > "$env"
  chmod 600 "$env"
}
fleet_verify_binding() {
  local record="$1"; [[ -f "$record" && ! -L "$record" ]] || return 1
  python3 - "$record" <<'PY'
import hashlib,json,sys
from pathlib import Path
d=json.loads(Path(sys.argv[1]).read_text()); p=Path(d['contract_path'])
if p.is_symlink() or not p.is_file(): raise SystemExit(1)
if hashlib.sha256(p.read_bytes()).hexdigest()!=d.get('contract_sha256'): raise SystemExit(1)
PY
}
