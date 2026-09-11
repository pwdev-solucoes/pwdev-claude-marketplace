#!/usr/bin/env bash
set -Eeuo pipefail
fleet_tmux_handle_read(){ local h=$1; [[ -f "$h" && ! -L "$h" ]] || return 1; python3 - "$h" <<'PY'
import json,sys
try:d=json.load(open(sys.argv[1]))
except Exception:raise SystemExit(1)
keys=('session_name','pane_id','fleet_id','member_id','cwd')
if d.get('driver')!='tmux' or any(not isinstance(d.get(k),str) or not d[k] for k in keys):raise SystemExit(1)
print(*(d[k] for k in keys),sep='\t')
PY
}
fleet_tmux_publish_handle(){ python3 - "$@" <<'PY'
import json,os,sys,tempfile
p,session,pane,fleet,member,cwd=sys.argv[1:]; parent=os.path.dirname(p) or '.'; os.makedirs(parent,exist_ok=True)
fd,tmp=tempfile.mkstemp(prefix='.'+os.path.basename(p)+'.',dir=parent,text=True)
try:
 with os.fdopen(fd,'w') as out:
  json.dump({'driver':'tmux','session_name':session,'pane_id':pane,'fleet_id':fleet,'member_id':member,'cwd':cwd},out,sort_keys=True); out.write('\n'); out.flush(); os.fsync(out.fileno())
 os.replace(tmp,p)
finally:
 if os.path.exists(tmp):os.unlink(tmp)
PY
}
fleet_ui_tmux_start(){
 local handle=$1 cwd=$2 fleet_id=$3 member_id=$4; shift 4
 [[ $# -gt 0 ]] || { echo 'fleet tmux: command is required' >&2; return 2; }
 command -v tmux >/dev/null 2>&1 || { echo 'fleet tmux: tmux unavailable' >&2; return 127; }
 [[ -d "$cwd" && ! -L "$cwd" ]] || { echo 'fleet tmux: unsafe cwd' >&2; return 1; }
 [[ ! -e "$handle" && ! -L "$handle" ]] || { echo 'fleet tmux: handle already exists' >&2; return 1; }
 local session="sdd-composy-${fleet_id}-${member_id}" identity actual_session pane
 if tmux has-session -t "$session" 2>/dev/null; then echo "fleet tmux: session collision: $session" >&2; return 1; fi
 identity=$(tmux new-session -d -P -F '#{session_name}|#{pane_id}' -s "$session" -c "$cwd" -- "$@") || return 1
 IFS='|' read -r actual_session pane <<<"$identity"
 [[ -n "$actual_session" && -n "$pane" ]] || { echo 'fleet tmux: pane identity unavailable' >&2; return 1; }
 tmux set-option -p -t "$pane" remain-on-exit on >/dev/null || return 1
 tmux set-option -p -t "$pane" @sdd-composy-owner sdd-composy-fleet >/dev/null || return 1
 tmux set-option -p -t "$pane" @sdd-composy-fleet "$fleet_id" >/dev/null || return 1
 tmux set-option -p -t "$pane" @sdd-composy-member "$member_id" >/dev/null || return 1
 fleet_tmux_publish_handle "$handle" "$actual_session" "$pane" "$fleet_id" "$member_id" "$cwd"
}
fleet_tmux_inspection(){ tmux display-message -p -t "$1" '#{@sdd-composy-owner}|#{@sdd-composy-fleet}|#{@sdd-composy-member}|#{pane_dead}|#{pane_dead_status}'; }
fleet_ui_tmux_inspect(){
 local handle=$1 session pane fleet member cwd raw owner live_fleet live_member dead status
 IFS=$'\t' read -r session pane fleet member cwd < <(fleet_tmux_handle_read "$handle") || return 1
 raw=$(fleet_tmux_inspection "$pane" 2>/dev/null) || return 1
 IFS='|' read -r owner live_fleet live_member dead status <<<"$raw"
 [[ "$owner" == sdd-composy-fleet && "$live_fleet" == "$fleet" && "$live_member" == "$member" ]] || return 1
 [[ "$dead" == 0 || "$dead" == 1 ]] || return 1
 if [[ "$dead" == 0 ]]; then status=null; else [[ "$status" =~ ^-?[0-9]+$ ]] || return 1; fi
 printf '{"alive":%s,"driver":"tmux","exit_status":%s,"pane_id":"%s","session_name":"%s"}\n' "$([[ $dead == 0 ]] && printf true || printf false)" "$status" "$pane" "$session"
}
fleet_ui_tmux_teardown(){ local handle=$1 session pane fleet member cwd; IFS=$'\t' read -r session pane fleet member cwd < <(fleet_tmux_handle_read "$handle") || return 1; fleet_ui_tmux_inspect "$handle" >/dev/null || return 1; tmux kill-pane -t "$pane" >/dev/null 2>&1 || return 1; rm -f -- "$handle"; }
fleet_ui_teardown(){ fleet_ui_tmux_teardown "$@"; }
