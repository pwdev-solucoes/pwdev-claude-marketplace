#!/usr/bin/env bash
set -Eeuo pipefail
fleet_tmux_nonce(){ python3 - <<'PY'
import secrets
print(secrets.token_hex(12))
PY
}
fleet_tmux_write_handle(){ python3 - "$@" <<'PY'
import json,os,sys,tempfile
p,state,socket,session,pane,fleet,member,cwd=sys.argv[1:]; parent=os.path.dirname(p) or '.'; os.makedirs(parent,exist_ok=True)
d={'driver':'tmux','state':state,'socket_name':socket,'session_name':session,'pane_id':pane,'fleet_id':fleet,'member_id':member,'cwd':cwd}
fd,tmp=tempfile.mkstemp(prefix='.'+os.path.basename(p)+'.',dir=parent,text=True)
try:
 with os.fdopen(fd,'w') as out:json.dump(d,out,sort_keys=True);out.write('\n');out.flush();os.fsync(out.fileno())
 os.replace(tmp,p)
finally:
 if os.path.exists(tmp):os.unlink(tmp)
PY
}
fleet_tmux_handle_read(){ local h=$1; [[ -f "$h" && ! -L "$h" ]] || return 1; python3 - "$h" <<'PY'
import json,sys
try:d=json.load(open(sys.argv[1]))
except Exception:raise SystemExit(1)
keys=('state','socket_name','session_name','pane_id','fleet_id','member_id','cwd')
if d.get('driver')!='tmux' or any(not isinstance(d.get(k),str) for k in keys) or d['state'] not in ('recovering','active'):raise SystemExit(1)
if any(not d[k] for k in ('socket_name','session_name','fleet_id','member_id','cwd')):raise SystemExit(1)
if d['state']=='active' and not d['pane_id']:raise SystemExit(1)
print(*(d[k] for k in keys),sep='|')
PY
}
fleet_ui_tmux_start(){
 local handle=$1 cwd=$2 fleet_id=$3 member_id=$4; shift 4
 [[ $# -gt 0 ]] || { echo 'fleet tmux: command is required' >&2; return 2; }; command -v tmux >/dev/null 2>&1 || { echo 'fleet tmux: tmux unavailable' >&2; return 127; }; [[ -d "$cwd" && ! -L "$cwd" ]] || { echo 'fleet tmux: unsafe cwd' >&2; return 1; }; [[ ! -e "$handle" && ! -L "$handle" ]] || { echo 'fleet tmux: handle already exists' >&2; return 1; }
 local nonce socket session identity actual_session pane; nonce=$(fleet_tmux_nonce); socket="sdd-composy-${nonce}"; session="sdd-composy-${fleet_id}-${member_id}"
 fleet_tmux_write_handle "$handle" recovering "$socket" "$session" '' "$fleet_id" "$member_id" "$cwd"
 if tmux -L "$socket" has-session -t "$session" 2>/dev/null; then echo "fleet tmux: session collision: $session" >&2; return 1; fi
 # A dedicated server lets remain-on-exit become effective before new-session
 # starts the member command, without changing another user's tmux defaults.
 identity=$(tmux -L "$socket" start-server \; set-option -g remain-on-exit on \; new-session -d -P -F '#{session_name}|#{pane_id}' -s "$session" -c "$cwd" -- "$@") || return 1
 IFS='|' read -r actual_session pane <<<"$identity"; [[ -n "$actual_session" && -n "$pane" ]] || { echo 'fleet tmux: pane identity unavailable' >&2; return 1; }
 fleet_tmux_write_handle "$handle" recovering "$socket" "$actual_session" "$pane" "$fleet_id" "$member_id" "$cwd"
 tmux -L "$socket" set-option -p -t "$pane" @sdd-composy-owner sdd-composy-fleet >/dev/null || return 1
 tmux -L "$socket" set-option -p -t "$pane" @sdd-composy-fleet "$fleet_id" >/dev/null || return 1
 tmux -L "$socket" set-option -p -t "$pane" @sdd-composy-member "$member_id" >/dev/null || return 1
 fleet_tmux_write_handle "$handle" active "$socket" "$actual_session" "$pane" "$fleet_id" "$member_id" "$cwd"
}
fleet_tmux_inspection(){ tmux -L "$1" display-message -p -t "$2" '#{@sdd-composy-owner}|#{@sdd-composy-fleet}|#{@sdd-composy-member}|#{pane_dead}|#{pane_dead_status}'; }
fleet_ui_tmux_inspect(){ local handle=$1 state socket session pane fleet member cwd raw owner live_fleet live_member dead exit_code; IFS='|' read -r state socket session pane fleet member cwd < <(fleet_tmux_handle_read "$handle") || return 1; if [[ "$state" == recovering ]]; then if tmux -L "$socket" has-session -t "$session" 2>/dev/null; then printf '{"alive":true,"driver":"tmux","exit_status":null,"recoverable":true,"pane_id":null,"session_name":"%s"}\n' "$session"; else printf '{"alive":false,"driver":"tmux","exit_status":null,"recoverable":true,"pane_id":null,"session_name":"%s"}\n' "$session"; fi; return 0; fi; raw=$(fleet_tmux_inspection "$socket" "$pane" 2>/dev/null) || return 1; IFS='|' read -r owner live_fleet live_member dead exit_code <<<"$raw"; [[ "$owner" == sdd-composy-fleet && "$live_fleet" == "$fleet" && "$live_member" == "$member" ]] || return 1; [[ "$dead" == 0 || "$dead" == 1 ]] || return 1; if [[ "$dead" == 0 ]]; then exit_code=null; else [[ "$exit_code" =~ ^-?[0-9]+$ ]] || return 1; fi; printf '{"alive":%s,"driver":"tmux","exit_status":%s,"recoverable":true,"pane_id":"%s","session_name":"%s"}\n' "$([[ $dead == 0 ]] && printf true || printf false)" "$exit_code" "$pane" "$session"; }
fleet_ui_tmux_teardown(){ local handle=$1 state socket session pane fleet member cwd; IFS='|' read -r state socket session pane fleet member cwd < <(fleet_tmux_handle_read "$handle") || return 1; if [[ "$state" == active ]]; then fleet_ui_tmux_inspect "$handle" >/dev/null || return 1; tmux -L "$socket" kill-server >/dev/null 2>&1 || return 1; else tmux -L "$socket" kill-server >/dev/null 2>&1 || ! tmux -L "$socket" has-session -t "$session" 2>/dev/null || return 1; fi; rm -f -- "$handle"; }
fleet_ui_teardown(){ fleet_ui_tmux_teardown "$@"; }
