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
for path in sorted(members_dir.glob('*.json')):
    if path.is_symlink(): errors.append(f"malformed member: {path.name} (symlink)"); continue
    try: value=json.loads(path.read_text(encoding='utf-8'))
    except Exception: errors.append(f"malformed member: {path.name}"); continue
    if not isinstance(value,dict): errors.append(f"malformed member: {path.name}"); continue
    ident=str(value.get('id') or value.get('task_id') or path.stem)
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
for r in records: counts[r['status']]=counts.get(r['status'],0)+1
attention=any(r['attention'] or r['transition'] for r in records)
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
