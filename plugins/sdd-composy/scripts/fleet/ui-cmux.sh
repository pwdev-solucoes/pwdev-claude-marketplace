#!/usr/bin/env bash
set -Eeuo pipefail
fleet_cmux_bin(){ printf '%s\n' "${SDD_CMUX_BIN:-cmux}"; }
fleet_cmux_call(){ local b; b=$(fleet_cmux_bin); command -v "$b" >/dev/null 2>&1 || { echo 'fleet cmux: cmux unavailable' >&2; return 127; }; "$b" "$@"; }
fleet_cmux_uuid(){ python3 - "$1" <<'PY'
import re,sys
m=re.search(r'(?i)\b[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}\b',sys.argv[1])
if not m: raise SystemExit(1)
print(m.group(0))
PY
}
fleet_cmux_title(){ printf 'sdd-composy:%s:%s\n' "$1" "$2"; }
fleet_cmux_handle_read(){ local h=$1; [[ -f "$h" && ! -L "$h" ]] || return 1; python3 - "$h" <<'PY'
import json,sys
try:d=json.load(open(sys.argv[1]))
except Exception:raise SystemExit(1)
keys=('workspace_id','surface_id','fleet_id','member_id','cwd','title')
if d.get('driver')!='cmux' or any(not isinstance(d.get(k),str) or not d[k] for k in keys):raise SystemExit(1)
print(*(d[k] for k in keys),sep='\t')
PY
}
fleet_cmux_publish_handle(){ python3 - "$@" <<'PY'
import json,os,sys,tempfile
p,w,s,f,m,c,t=sys.argv[1:]; parent=os.path.dirname(p) or '.'; os.makedirs(parent,exist_ok=True)
fd,tmp=tempfile.mkstemp(prefix='.'+os.path.basename(p)+'.',dir=parent,text=True)
try:
 with os.fdopen(fd,'w') as out:
  json.dump({'driver':'cmux','workspace_id':w,'surface_id':s,'fleet_id':f,'member_id':m,'cwd':c,'title':t},out,sort_keys=True); out.write('\n'); out.flush(); os.fsync(out.fileno())
 os.replace(tmp,p)
finally:
 if os.path.exists(tmp):os.unlink(tmp)
PY
}
fleet_cmux_base_owner(){ local w=$1 f=$2 m=$3 title=$4 work statuses; work=$(fleet_cmux_call --id-format uuids list-workspaces 2>/dev/null) || return 1; grep -F "$w" <<<"$work" | grep -F "$title" >/dev/null || return 1; statuses=$(fleet_cmux_call list-status --workspace "$w" 2>/dev/null) || return 1; grep -Fx 'sdd-composy-owner sdd-composy-fleet' <<<"$statuses" >/dev/null && grep -Fx "sdd-composy-fleet $f" <<<"$statuses" >/dev/null && grep -Fx "sdd-composy-member $m" <<<"$statuses" >/dev/null; }
fleet_cmux_prove_owner(){ local w=$1 s=$2 f=$3 m=$4 title=$5 surfaces; fleet_cmux_base_owner "$w" "$f" "$m" "$title" || return 1; surfaces=$(fleet_cmux_call --id-format uuids list-pane-surfaces --workspace "$w" 2>/dev/null) || return 1; grep -F "$s" <<<"$surfaces" >/dev/null; }
fleet_ui_cmux_start(){
 local h=$1 cwd=$2 fleet_id=$3 member_id=$4; shift 4
 [[ $# -gt 0 ]] || { echo 'fleet cmux: command is required' >&2; return 2; }
 [[ -d "$cwd" && ! -L "$cwd" ]] || { echo 'fleet cmux: unsafe cwd' >&2; return 1; }
 [[ ! -e "$h" && ! -L "$h" ]] || { echo 'fleet cmux: handle already exists' >&2; return 1; }
 local title existing command_raw command_out w surfaces s; title=$(fleet_cmux_title "$fleet_id" "$member_id")
 existing=$(fleet_cmux_call --id-format uuids list-workspaces 2>/dev/null) || return 1
 grep -F "$title" <<<"$existing" >/dev/null && { echo "fleet cmux: workspace collision: $title" >&2; return 1; }
 printf -v command_raw '%q ' "$@"; command_raw=${command_raw% }
 command_out=$(fleet_cmux_call --id-format uuids new-workspace --name "$title" --cwd "$cwd" --command "$command_raw" --focus false) || return 1
 w=$(fleet_cmux_uuid "$command_out") || { echo 'fleet cmux: workspace identity unavailable' >&2; return 1; }
 fleet_cmux_call set-status sdd-composy-owner sdd-composy-fleet --workspace "$w" >/dev/null || return 1
 fleet_cmux_call set-status sdd-composy-fleet "$fleet_id" --workspace "$w" >/dev/null || return 1
 fleet_cmux_call set-status sdd-composy-member "$member_id" --workspace "$w" >/dev/null || return 1
 surfaces=$(fleet_cmux_call --id-format uuids list-pane-surfaces --workspace "$w") || return 1
 s=$(fleet_cmux_uuid "$surfaces") || { echo 'fleet cmux: surface identity unavailable' >&2; return 1; }
 fleet_cmux_publish_handle "$h" "$w" "$s" "$fleet_id" "$member_id" "$cwd" "$title"
}
fleet_ui_cmux_inspect(){ local h=$1 w s f m c title; IFS=$'\t' read -r w s f m c title < <(fleet_cmux_handle_read "$h") || return 1; if fleet_cmux_prove_owner "$w" "$s" "$f" "$m" "$title"; then printf '{"alive":true,"driver":"cmux","exit_status":null,"surface_id":"%s","workspace_id":"%s"}\n' "$s" "$w"; elif fleet_cmux_base_owner "$w" "$f" "$m" "$title"; then printf '{"alive":false,"driver":"cmux","exit_status":null,"surface_id":"%s","workspace_id":"%s"}\n' "$s" "$w"; else return 1; fi; }
fleet_ui_cmux_status(){ local h=$1 text=$2 color=${3:-blue} w s f m c title; IFS=$'\t' read -r w s f m c title < <(fleet_cmux_handle_read "$h") || return 1; fleet_cmux_prove_owner "$w" "$s" "$f" "$m" "$title" || return 1; fleet_cmux_call set-status sdd-composy-state "$text" --workspace "$w" --color "$color" >/dev/null; }
fleet_ui_cmux_flash(){ local h=$1 w s f m c title; IFS=$'\t' read -r w s f m c title < <(fleet_cmux_handle_read "$h") || return 1; fleet_cmux_prove_owner "$w" "$s" "$f" "$m" "$title" || return 1; fleet_cmux_call trigger-flash --workspace "$w" --surface "$s" >/dev/null; }
fleet_ui_cmux_teardown(){ local h=$1 w s f m c title; IFS=$'\t' read -r w s f m c title < <(fleet_cmux_handle_read "$h") || return 1; fleet_cmux_prove_owner "$w" "$s" "$f" "$m" "$title" || return 1; fleet_cmux_call close-surface --workspace "$w" --surface "$s" >/dev/null || return 1; rm -f -- "$h"; }
fleet_ui_teardown(){ fleet_ui_cmux_teardown "$@"; }
