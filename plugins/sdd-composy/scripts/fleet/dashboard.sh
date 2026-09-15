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
# Validate the optional UI handle before printing anything: status is observational, so the handle
# is only read and projected, never passed to a presentation transport.
if [[ -n "$handle" ]]; then
  [[ ! -L "$handle" && -f "$handle" ]] || { echo 'fleet dashboard: unsafe UI handle' >&2; exit 1; }
fi
set +e
payload=$(python3 - "$root" "$state" "$fleet_id" "$handle" <<'PY'
import json, os, sys, unicodedata
from pathlib import Path
root=Path(sys.argv[1]); state=Path(sys.argv[2]); fleet_id=sys.argv[3]; handle_path=sys.argv[4]; members_dir=state/'members'
records=[]; errors=[]
def clean(value, limit=160):
    if not isinstance(value, (str, int, float, bool)) or value is None:
        return None
    text=''.join(' ' if ord(char) < 32 or ord(char) == 127 else char for char in str(value))
    return ' '.join(text.split())[:limit]
def encoded_key(value):
    return ''.join(f'%U{ord(char):06X}' if char == '%' or unicodedata.category(char).startswith('C') else char
                   for char in value)
def sanitized(value, depth=0):
    if depth > 16: return None
    if isinstance(value,str): return clean(value)
    if value is None or isinstance(value,(bool,int,float)): return value
    if isinstance(value,list): return [sanitized(item,depth+1) for item in value]
    if isinstance(value,dict):
        result={}
        for key,item in value.items():
            safe_key=encoded_key(key if isinstance(key,str) else str(key))
            if safe_key: result[safe_key]=sanitized(item,depth+1)
        return result
    return clean(value)
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
            projected_handle=sanitized(handle)
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
    status=(clean(value.get('status') or value.get('state') or 'unknown') or 'unknown').lower()
    if status == 'locked': status='pending'
    raw=value.get('worktree_path') or value.get('worktree')
    rel=''
    # Show a worktree only as a path inside the root: absolute paths are made relative, relative
    # paths are kept, and anything escaping the root is hidden.
    if isinstance(raw,str) and raw and '..' not in Path(raw).parts:
        candidate=Path(raw)
        if candidate.is_absolute():
            try: rel=candidate.relative_to(root).as_posix()
            except ValueError: rel=''
        else: rel=candidate.as_posix()
    msg=clean(value.get('message') or '') or ''
    records.append({'id':ident,'status':status,'message':msg,'worktree':rel,
                    'attention': status in {'failed','blocked','cancelled'} or value.get('attention') is True,
                    'transition': value.get('previous_status') not in (None,status)})
if errors:
    print(json.dumps({'error':'malformed','errors':errors},sort_keys=True)); raise SystemExit(3)
ui_handle=None
if handle_path:
    try: ui_handle=sanitized(json.loads(Path(handle_path).read_text(encoding='utf-8')))
    except Exception:
        print(json.dumps({'error':'malformed','errors':['malformed UI handle']},sort_keys=True)); raise SystemExit(3)
counts={}
for r in records:
    status=r.get('state',r.get('status','unknown'))
    counts[status]=counts.get(status,0)+1
attention=any(r.get('_attention',False) or r.get('attention',False) or r.get('transition',False) for r in records)
for r in records: r.pop('_attention',None)
result={'schema':'sdd-composy.fleet-dashboard','fleet_id':clean(fleet_id) or '', 'counts':counts,
        'attention':attention,'members':records}
if ui_handle is not None: result['ui_handle']=ui_handle
print(json.dumps(result,ensure_ascii=False,sort_keys=True))
PY
)
status=$?
set -e
if ((status != 0)); then
  if ((json_out)) && [[ -n "$payload" ]]; then printf '%s\n' "$payload"; fi
  errors=$(python3 -c 'import json,sys
try: print("; ".join(json.loads(sys.argv[1]).get("errors", [])))
except Exception: pass' "$payload" 2>/dev/null || true)
  echo "fleet dashboard: malformed member data${errors:+: $errors}" >&2
  exit 1
fi
if ((json_out)); then printf '%s\n' "$payload"; else
  python3 - "$payload" <<'PY'
import json,sys
d=json.loads(sys.argv[1])
if d.get('error'): raise SystemExit(d['error'])
print(f"fleet {d['fleet_id']}: " + ', '.join(f"{k}={v}" for k,v in sorted(d['counts'].items())))
for m in d['members']:
    if 'member' in m:
        details=[]
        for key in ('runtime','ui','task','loop','state'):
            if key in m: details.append(f"{key}={m[key]}")
        if 'handle' in m: details.append('handle='+json.dumps(m['handle'],ensure_ascii=False,sort_keys=True,separators=(',',':')))
        if 'next_action' in m: details.append(f"next_action={m['next_action']}")
        print(f"{m['member']}: " + ' '.join(details))
    else:
        suffix=f" — {m['message']}" if m['message'] else ''
        print(f"{m['id']}: {m['status']}{suffix}")
if 'ui_handle' in d:
    print('ui_handle=' + json.dumps(d['ui_handle'],ensure_ascii=False,sort_keys=True,separators=(',',':')))
PY
fi
