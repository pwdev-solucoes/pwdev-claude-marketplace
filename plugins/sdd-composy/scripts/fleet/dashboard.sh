#!/usr/bin/env bash
set -euo pipefail
usage(){ echo "usage: dashboard.sh --root ROOT --fleet-id ID [--json] [--handle HANDLE]" >&2; exit 2; }
root= fleet_id= json_out=0; handle=
while (( $# )); do case "$1" in
  --root) root=${2:-}; shift 2;; --fleet-id) fleet_id=${2:-}; shift 2;;
  --json) json_out=1; shift;; --handle) handle=${2:-}; shift 2;; *) usage;; esac; done
[[ -n "$root" && -n "$fleet_id" ]] || usage
root=$(cd -- "$root" 2>/dev/null && pwd -P) || { echo 'fleet dashboard: root unavailable' >&2; exit 1; }
state="$root/.planning/sdd-composy/fleet/$fleet_id"; members="$state/members"
[[ -d "$state" && ! -L "$state" && -d "$members" && ! -L "$members" ]] || { echo 'fleet dashboard: state unavailable' >&2; exit 1; }
payload=$(python3 - "$root" "$state" "$fleet_id" <<'PY'
import json, os, sys
from pathlib import Path
root=Path(sys.argv[1]); state=Path(sys.argv[2]); fleet_id=sys.argv[3]; members_dir=state/'members'
records=[]; errors=[]
def clean(value, limit=160):
    if not isinstance(value, (str, int, float, bool)) or value is None:
        return None
    text=''.join(' ' if ord(char) < 32 or ord(char) == 127 else char for char in str(value))
    return ' '.join(text.split())[:limit]
for path in sorted(members_dir.glob('*.json')):
    if path.is_symlink(): errors.append(f"malformed member: {path.name} (symlink)"); continue
    try: value=json.loads(path.read_text(encoding='utf-8'))
    except Exception: errors.append(f"malformed member: {path.name}"); continue
    if not isinstance(value,dict): errors.append(f"malformed member: {path.name}"); continue
    interaction=value.get('interaction')
    if isinstance(interaction,dict):
        record={}
        for source,key in ((value.get('runtime'),'runtime'),(value.get('ui'),'ui'),
                           (value.get('id') or path.stem,'member'),(value.get('task_id'),'task')):
            cleaned=clean(source)
            if cleaned: record[key]=cleaned
        binding=interaction.get('loop')
        if isinstance(binding,dict):
            loop_id=clean(binding.get('id'))
            if loop_id: record['loop']=loop_id
        handle=interaction.get('handle')
        if isinstance(handle,dict):
            projected_handle={}
            for key in ('driver','state','workspace_id','surface_id','session_name','pane_id','pid'):
                cleaned=clean(handle.get(key))
                if cleaned: projected_handle[key]=cleaned
            if projected_handle: record['handle']=projected_handle
        state_value=clean(interaction.get('state'))
        if state_value: record['state']=state_value.lower()
        timestamps={}
        for key in ('started_at','updated_at','finished_at'):
            cleaned=clean(interaction.get(key))
            if cleaned: timestamps[key]=cleaned
        if timestamps: record['timestamps']=timestamps
        next_action=clean(interaction.get('next_action'))
        if next_action: record['next_action']=next_action
        record['_attention']=record.get('state') in {'failed','blocked','cancelled','awaiting_human'}
        records.append(record)
        continue
    ident=clean(value.get('id') or value.get('task_id') or path.stem) or path.stem
    status=str(value.get('status') or value.get('state') or 'unknown').lower()
    if status == 'locked': status='pending'
    raw=value.get('worktree_path') or value.get('worktree')
    rel=''
    if isinstance(raw,str) and raw and not os.path.isabs(raw) and '..' not in Path(raw).parts:
        try: rel=Path(raw).relative_to(root).as_posix()
        except ValueError: rel=''
    msg=' '.join(str(value.get('message') or '').split())[:160]
    records.append({'id':ident,'status':status,'message':msg,'worktree':rel,
                    'attention': status in {'failed','blocked','cancelled'} or value.get('attention') is True,
                    'transition': value.get('previous_status') not in (None,status)})
if errors:
    print(json.dumps({'error':'malformed','errors':errors},sort_keys=True)); raise SystemExit(3)
counts={}
for r in records:
    status=r.get('state',r.get('status','unknown'))
    counts[status]=counts.get(status,0)+1
attention=any(r.get('_attention',False) or r.get('attention',False) or r.get('transition',False) for r in records)
for r in records: r.pop('_attention',None)
print(json.dumps({'schema':'sdd-composy.fleet-dashboard','fleet_id':fleet_id,'counts':counts,
                  'attention':attention,'members':records},ensure_ascii=False,sort_keys=True))
PY
) || { echo 'fleet dashboard: malformed member data' >&2; exit 1; }
if ((json_out)); then printf '%s\n' "$payload"; else
  python3 - "$payload" <<'PY'
import json,sys
d=json.loads(sys.argv[1])
if d.get('error'): raise SystemExit(d['error'])
print(f"fleet {d['fleet_id']}: " + ', '.join(f"{k}={v}" for k,v in sorted(d['counts'].items())))
for m in d['members']:
    if 'member' in m:
        details=[f"runtime={m.get('runtime','')}",f"ui={m.get('ui','')}",f"task={m.get('task','')}",
                 f"loop={m.get('loop','')}",f"state={m.get('state','')}"]
        if m.get('next_action'): details.append(f"next_action={m['next_action']}")
        print(f"{m['member']}: " + ' '.join(details))
    else:
        suffix=f" — {m['message']}" if m['message'] else ''
        print(f"{m['id']}: {m['status']}{suffix}")
PY
fi
if [[ -n "$handle" ]]; then
  [[ ! -L "$handle" && -f "$handle" ]] || { echo 'fleet dashboard: unsafe UI handle' >&2; exit 1; }
  here=$(dirname -- "$0")
  color=blue; case "$payload" in *attention*true*) color=red;; esac
  . "$here/ui-cmux.sh"; fleet_ui_cmux_status "$handle" "sdd fleet $fleet_id" "$color" || true
  if [ "$color" = red ]; then fleet_ui_cmux_flash "$handle" || true; fi
fi
