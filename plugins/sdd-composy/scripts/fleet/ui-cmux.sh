#!/usr/bin/env bash
set -Eeuo pipefail
fleet_cmux_bin(){ printf '%s\n' "${SDD_CMUX_BIN:-cmux}"; }
fleet_cmux_call(){ local b; b=$(fleet_cmux_bin); command -v "$b" >/dev/null 2>&1 || { echo 'fleet cmux: cmux unavailable' >&2; return 127; }; "$b" "$@"; }
fleet_cmux_json_id(){ python3 - "$1" <<'PY'
import json,sys
try: d=json.loads(sys.argv[1])
except Exception: raise SystemExit(1)
def f(x):
 if isinstance(x,dict):
  for k in ('id','workspace_id','workspaceId','surface_id','surfaceId','pane_id','paneId'):
   if x.get(k): return str(x[k])
  for v in x.values():
   z=f(v)
   if z:return z
 if isinstance(x,list):
  for v in x:
   z=f(v)
   if z:return z
z=f(d)
if not z: raise SystemExit(1)
print(z)
PY
}
fleet_cmux_handle_read(){ local h=$1; [[ -f "$h" && ! -L "$h" ]] || return 1; python3 - "$h" <<'PY'
import json,sys
d=json.load(open(sys.argv[1]))
if d.get('driver')!='cmux' or not d.get('workspace_id') or not d.get('surface_id') or not d.get('fleet_id'): raise SystemExit(1)
print(d['workspace_id'],d['surface_id'],d['fleet_id'],d.get('cwd',''))
PY
}
fleet_cmux_owned(){ local w=$1 fleet_id=$2 raw; raw=$(fleet_cmux_call list-workspaces --json 2>/dev/null) || return 1; python3 - "$raw" "$w" "$fleet_id" <<'PY'
import json,sys
try:d=json.loads(sys.argv[1])
except Exception:raise SystemExit(1)
n=sys.argv[2]; fleet_id=sys.argv[3]
def f(x):
 if isinstance(x,dict):
  if str(x.get('id',''))==n and (x.get('sdd_composy') is True or x.get('owner') in ('sdd-composy','sdd_composy')) and str(x.get('sdd_composy_fleet',''))==fleet_id: return True
  return any(f(v) for v in x.values())
 if isinstance(x,list): return any(f(v) for v in x)
 return False
raise SystemExit(0 if f(d) else 1)
PY
}
fleet_ui_cmux_start(){
 local h=$1 cwd=$2 name=${3:-sdd-composy}; shift 3; local fleet_id=${SDD_FLEET_ID:-$name}; [[ $# -gt 0 ]] || return 2
 [[ -d "$cwd" && ! -L "$cwd" ]] || { echo 'fleet cmux: unsafe cwd' >&2; return 1; }
 [[ ! -e "$h" && ! -L "$h" ]] || { echo 'fleet cmux: handle already exists' >&2; return 1; }
 local w s; w=$(fleet_cmux_json_id "$(fleet_cmux_call new-workspace --json --name "$name" --cwd "$cwd")") || return 1
 # Ownership is established before the handle becomes usable.  Later calls
 # prove this marker through list-workspaces and therefore cannot touch a
 # pre-existing or foreign workspace.
 fleet_cmux_call set-workspace-meta --workspace "$w" --owner sdd-composy --fleet-driver cmux --sdd-composy-fleet "$fleet_id" >/dev/null || { echo 'fleet cmux: cannot establish workspace ownership' >&2; return 1; }
 s=$(fleet_cmux_json_id "$(fleet_cmux_call new-split --json --workspace "$w" --cwd "$cwd")") || return 1
python3 - "$h" "$w" "$s" "$fleet_id" "$cwd" <<'PY'
import json,sys
from pathlib import Path
Path(sys.argv[1]).write_text(json.dumps({'driver':'cmux','workspace_id':sys.argv[2],'surface_id':sys.argv[3],'fleet_id':sys.argv[4],'cwd':sys.argv[5]},sort_keys=True)+'\n')
PY
}
fleet_ui_cmux_status(){ local h=$1 text=$2 color=${3:-blue} w s f c; read -r w s f c < <(fleet_cmux_handle_read "$h") || return 1; fleet_cmux_owned "$w" "$f" || return 1; fleet_cmux_call set-status --workspace "$w" --surface "$s" --color "$color" --text "$text" >/dev/null; }
fleet_ui_cmux_flash(){ local h=$1 w s f c; read -r w s f c < <(fleet_cmux_handle_read "$h") || return 1; fleet_cmux_owned "$w" "$f" || return 1; fleet_cmux_call flash --workspace "$w" --surface "$s" >/dev/null; }
fleet_ui_cmux_teardown(){ local h=$1 w s f c; read -r w s f c < <(fleet_cmux_handle_read "$h") || return 1; fleet_cmux_owned "$w" "$f" || return 1; fleet_cmux_call close-surface --workspace "$w" --surface "$s" >/dev/null || return 1; rm -f -- "$h"; }
fleet_ui_teardown(){ fleet_ui_cmux_teardown "$@"; }
