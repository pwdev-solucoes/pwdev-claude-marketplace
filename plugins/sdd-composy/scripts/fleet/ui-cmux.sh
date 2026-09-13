#!/usr/bin/env bash
set -Eeuo pipefail
fleet_cmux_bin(){ printf '%s\n' "${SDD_CMUX_BIN:-cmux}"; }
fleet_cmux_call(){ local b; b=$(fleet_cmux_bin); command -v "$b" >/dev/null 2>&1 || { echo 'fleet cmux: cmux unavailable' >&2; return 127; }; "$b" "$@"; }
fleet_cmux_uuid(){ python3 - "$1" <<'PY'
import re,sys
m=re.search(r'(?i)\b[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}\b',sys.argv[1])
if not m:raise SystemExit(1)
print(m.group(0))
PY
}
fleet_cmux_nonce(){ python3 - <<'PY'
import secrets
print(secrets.token_hex(16))
PY
}
fleet_cmux_write_handle(){ python3 - "$@" <<'PY'
import json,os,sys,tempfile
p,state,w,s,f,m,c,t,n,marker=sys.argv[1:]; parent=os.path.dirname(p) or '.'; os.makedirs(parent,exist_ok=True)
d={'driver':'cmux','state':state,'workspace_id':w,'surface_id':s,'fleet_id':f,'member_id':m,'cwd':c,'title':t,'nonce':n,'ownership_marker':marker}
fd,tmp=tempfile.mkstemp(prefix='.'+os.path.basename(p)+'.',dir=parent,text=True)
try:
 with os.fdopen(fd,'w') as out: json.dump(d,out,sort_keys=True); out.write('\n'); out.flush(); os.fsync(out.fileno())
 os.replace(tmp,p)
finally:
 if os.path.exists(tmp):os.unlink(tmp)
PY
}
fleet_cmux_handle_read(){ local h=$1; [[ -f "$h" && ! -L "$h" ]] || return 1; python3 - "$h" <<'PY'
import json,sys
try:d=json.load(open(sys.argv[1]))
except Exception:raise SystemExit(1)
required=('state','workspace_id','surface_id','fleet_id','member_id','cwd','title','nonce','ownership_marker')
if d.get('driver')!='cmux' or any(not isinstance(d.get(k),str) for k in required) or d['state'] not in ('recovering','active'):raise SystemExit(1)
if any(not d[k] for k in ('fleet_id','member_id','cwd','title','nonce','ownership_marker')):raise SystemExit(1)
if d['state']=='active' and (not d['workspace_id'] or not d['surface_id']):raise SystemExit(1)
print(*(d[k] for k in required),sep='\t')
PY
}
fleet_cmux_workspace_by_title(){ python3 - "$1" "$2" <<'PY'
import re,sys
title=sys.argv[2]; ids=[]
for line in sys.argv[1].splitlines():
 if title in line:
  m=re.search(r'(?i)\b[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}\b',line)
  if m:ids.append(m.group(0))
if len(ids)!=1:raise SystemExit(1)
print(ids[0])
PY
}
fleet_cmux_resolve_workspace(){ local w=$1 title=$2 marker=$3 tree; tree=$(fleet_cmux_call --json --id-format uuids tree --all 2>/dev/null) || return 1; python3 - "$tree" "$w" "$title" "$marker" <<'PY'
import json,sys
try:d=json.loads(sys.argv[1])
except Exception:raise SystemExit(1)
wanted,title,marker=sys.argv[2:]; found=[]
for window in d.get('windows',[]):
 for workspace in window.get('workspaces',[]):
  if workspace.get('title')==title and workspace.get('description')==marker and (wanted=='-' or str(workspace.get('id'))==wanted):found.append(str(workspace.get('id')))
if len(found)!=1:raise SystemExit(1)
print(found[0])
PY
}
fleet_cmux_surface_from_tree(){ python3 - "$1" "$2" "$3" "$4" <<'PY'
import json,sys
try:d=json.loads(sys.argv[1])
except Exception:raise SystemExit(1)
wanted,title,marker=sys.argv[2:]; matches=[]
for window in d.get('windows',[]):
 for workspace in window.get('workspaces',[]):
  if str(workspace.get('id'))!=wanted or workspace.get('title')!=title or workspace.get('description')!=marker:continue
  for pane in workspace.get('panes',[]):
   for surface in pane.get('surfaces',[]):
    if surface.get('type')=='terminal' and isinstance(surface.get('id'),str):matches.append(surface['id'])
if len(matches)!=1:raise SystemExit(1)
print(matches[0])
PY
}
fleet_cmux_base_owner(){ local w=$1 f=$2 m=$3 title=$4 marker=$5 resolved statuses; resolved=$(fleet_cmux_resolve_workspace "$w" "$title" "$marker") || return 1; statuses=$(fleet_cmux_call list-status --workspace "$resolved" 2>/dev/null) || return 1; grep -Fx 'sdd-composy-owner=sdd-composy-fleet' <<<"$statuses" >/dev/null && grep -Fx "sdd-composy-fleet=$f" <<<"$statuses" >/dev/null && grep -Fx "sdd-composy-member=$m" <<<"$statuses" >/dev/null; }
fleet_cmux_prove_owner(){ local w=$1 s=$2 f=$3 m=$4 title=$5 marker=$6 tree actual; fleet_cmux_base_owner "$w" "$f" "$m" "$title" "$marker" || return 1; tree=$(fleet_cmux_call --json --id-format uuids tree --workspace "$w" 2>/dev/null) || return 1; actual=$(fleet_cmux_surface_from_tree "$tree" "$w" "$title" "$marker") || return 1; [[ "$actual" == "$s" ]]; }
fleet_ui_cmux_start(){
 local h=$1 cwd=$2 fleet_id=$3 member_id=$4; shift 4
 [[ $# -gt 0 ]] || { echo 'fleet cmux: command is required' >&2; return 2; }; [[ -d "$cwd" && ! -L "$cwd" ]] || { echo 'fleet cmux: unsafe cwd' >&2; return 1; }; [[ ! -e "$h" && ! -L "$h" ]] || { echo 'fleet cmux: handle already exists' >&2; return 1; }
 local nonce title marker existing command_raw w tree s; nonce=$(fleet_cmux_nonce); title="sdd-composy:${fleet_id}:${member_id}:${nonce}"; marker="sdd-composy-fleet:${nonce}:${fleet_id}:${member_id}"
 fleet_cmux_write_handle "$h" recovering - - "$fleet_id" "$member_id" "$cwd" "$title" "$nonce" "$marker"
 existing=$(fleet_cmux_call --id-format uuids list-workspaces 2>/dev/null) || return 1
 fleet_cmux_workspace_by_title "$existing" "$title" >/dev/null 2>&1 && { echo "fleet cmux: workspace collision: $title" >&2; return 1; }
 printf -v command_raw '%q ' "$@"; command_raw=${command_raw% }
 fleet_cmux_call --id-format uuids new-workspace --name "$title" --description "$marker" --cwd "$cwd" --command "$command_raw" --focus false >/dev/null || return 1
 w=$(fleet_cmux_resolve_workspace - "$title" "$marker") || { echo 'fleet cmux: workspace identity unavailable' >&2; return 1; }
 fleet_cmux_write_handle "$h" recovering "$w" - "$fleet_id" "$member_id" "$cwd" "$title" "$nonce" "$marker"
 fleet_cmux_call set-status sdd-composy-owner sdd-composy-fleet --workspace "$w" >/dev/null || return 1
 fleet_cmux_call set-status sdd-composy-fleet "$fleet_id" --workspace "$w" >/dev/null || return 1
 fleet_cmux_call set-status sdd-composy-member "$member_id" --workspace "$w" >/dev/null || return 1
 tree=$(fleet_cmux_call --json --id-format uuids tree --workspace "$w") || return 1
 s=$(fleet_cmux_surface_from_tree "$tree" "$w" "$title" "$marker") || { echo 'fleet cmux: unique command surface identity unavailable' >&2; return 1; }
 fleet_cmux_write_handle "$h" active "$w" "$s" "$fleet_id" "$member_id" "$cwd" "$title" "$nonce" "$marker"
}
fleet_ui_cmux_inspect(){ local h=$1 state w s f m c title nonce marker resolved; IFS=$'\t' read -r state w s f m c title nonce marker < <(fleet_cmux_handle_read "$h") || return 1; if [[ "$state" == recovering ]]; then resolved=$(fleet_cmux_resolve_workspace "$w" "$title" "$marker") || return 1; printf '{"alive":true,"driver":"cmux","exit_status":null,"recoverable":true,"surface_id":null,"workspace_id":"%s"}\n' "$resolved"; elif fleet_cmux_prove_owner "$w" "$s" "$f" "$m" "$title" "$marker"; then printf '{"alive":true,"driver":"cmux","exit_status":null,"recoverable":true,"surface_id":"%s","workspace_id":"%s"}\n' "$s" "$w"; else return 1; fi; }
fleet_ui_cmux_status(){ local h=$1 text=$2 color=${3:-blue} state w s f m c title nonce marker; IFS=$'\t' read -r state w s f m c title nonce marker < <(fleet_cmux_handle_read "$h") || return 1; [[ "$state" == active ]] && fleet_cmux_prove_owner "$w" "$s" "$f" "$m" "$title" "$marker" || return 1; fleet_cmux_call set-status sdd-composy-state "$text" --workspace "$w" --color "$color" >/dev/null; }
fleet_ui_cmux_flash(){ local h=$1 state w s f m c title nonce marker; IFS=$'\t' read -r state w s f m c title nonce marker < <(fleet_cmux_handle_read "$h") || return 1; [[ "$state" == active ]] && fleet_cmux_prove_owner "$w" "$s" "$f" "$m" "$title" "$marker" || return 1; fleet_cmux_call trigger-flash --workspace "$w" --surface "$s" >/dev/null; }
fleet_ui_cmux_teardown(){ local h=$1 state w s f m c title nonce marker resolved; IFS=$'\t' read -r state w s f m c title nonce marker < <(fleet_cmux_handle_read "$h") || return 1; if [[ "$state" == active ]]; then fleet_cmux_prove_owner "$w" "$s" "$f" "$m" "$title" "$marker" || return 1; resolved=$w; else resolved=$(fleet_cmux_resolve_workspace "$w" "$title" "$marker") || return 1; fi; fleet_cmux_call close-workspace --workspace "$resolved" >/dev/null || return 1; rm -f -- "$h"; }
fleet_ui_teardown(){ fleet_ui_cmux_teardown "$@"; }
