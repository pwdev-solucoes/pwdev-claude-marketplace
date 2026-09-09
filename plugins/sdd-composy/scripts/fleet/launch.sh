#!/usr/bin/env bash
set -euo pipefail
HERE=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
. "$HERE/common.sh"
usage(){ echo "usage: launch.sh --root ROOT --fleet-id ID --base-branch BRANCH --task TASK.json [--task TASK.json ...] [--compose] [--ui auto|cmux|tmux|headless]" >&2; exit 2; }
root= fleet_id= base_branch= compose=0; ui=auto; tasks=()
while (($#)); do case "$1" in
  --root) root=${2:-}; shift 2;; --fleet-id) fleet_id=${2:-}; shift 2;;
  --base-branch) base_branch=${2:-}; shift 2;; --task) tasks+=("${2:-}"); shift 2;; --compose) compose=1; shift;; --ui) ui=${2:-}; shift 2;; *) usage;; esac; done
[[ -n "$root" && -n "$fleet_id" && -n "$base_branch" && ${#tasks[@]} -gt 0 ]] || usage
root=$(fleet_abs "$root"); [[ -d "$root/.git" || -f "$root/.git" ]] || fleet_die "root is not a git repository"
ui=$(fleet_select_ui "$ui") || exit $?
state=$(fleet_state_dir "$root" "$fleet_id"); mkdir -p "$state/members"
export FLEET_ID="$fleet_id"
fleet_preexisting=0; [[ -e "$state/fleet.json" || -L "$state/fleet.json" ]] && fleet_preexisting=1
preexisting_members=(); while IFS= read -r -d '' f; do preexisting_members+=("$f"); done < <(find "$state/members" -maxdepth 1 -type f -name '*.json' -print0 2>/dev/null)
lock="$state/.lock"; fleet_lock "$lock"; trap 'fleet_unlock "$lock"' EXIT
[[ "$fleet_id" =~ ^[A-Za-z0-9._-]+$ ]] || fleet_die "invalid fleet id"
command -v git >/dev/null || fleet_die "git is required"
git -C "$root" show-ref --verify --quiet "refs/heads/$base_branch" || fleet_die "unknown base branch"

python3 - "$root" "$state" "$fleet_id" "$base_branch" "$ui" "${tasks[@]}" <<'PY'
import json,sys,hashlib
from pathlib import Path
root,state=map(Path,sys.argv[1:3]); fleet_id=sys.argv[3]; base_branch=sys.argv[4]; ui=sys.argv[5]; files=[Path(x) for x in sys.argv[6:]]
seen=[]; records=[]
for f in files:
    if f.is_symlink(): raise SystemExit(f"fleet: task symlink rejected: {f}")
    try: data=json.loads(f.read_text())
    except Exception as e: raise SystemExit(f"fleet: invalid task: {e}")
    if isinstance(data,dict) and isinstance(data.get('tasks'),list): entries=data['tasks']
    else: entries=[data]
    for task in entries:
      if not isinstance(task,dict): raise SystemExit('fleet: task must be an object')
      tid=str(task.get('id','')); paths=task.get('allowed_paths',[])
      if not tid or task.get('state') != 'ready': raise SystemExit(f'fleet: task {tid or "?"} is not ready')
      if task.get('dependencies_complete') is False or task.get('dependencies') not in (None,[]) and task.get('dependencies_complete') is not True:
          raise SystemExit(f'fleet: task {tid} has incomplete dependencies')
      for key in ('acceptance_criteria','verification_commands'):
          if not isinstance(task.get(key),list) or not task[key] or any(not str(x).strip() for x in task[key]): raise SystemExit(f'fleet: task {tid} missing {key}')
      if not isinstance(paths,list): raise SystemExit(f'fleet: task {tid} invalid allowed_paths')
      norm=[]
      for raw in paths:
        p=Path(str(raw));
        if p.is_absolute() or '..' in p.parts: raise SystemExit(f'fleet: unsafe path {raw}')
        q=(root/p).absolute()
        cur=root
        for part in p.parts:
          cur=cur/part
          if cur.exists() and cur.is_symlink(): raise SystemExit(f'fleet: symlink path {raw}')
        norm.append(p.as_posix())
      for old,oid in seen:
        for a in norm:
          for b in old:
            if a==b or a.startswith(b.rstrip('/')+'/') or b.startswith(a.rstrip('/')+'/'): raise SystemExit(f'fleet: path collision {tid}/{oid}')
      seen.append((norm,tid))
      contract=Path(str(task.get('contract_path', f)))
      if contract.is_symlink() or not contract.exists(): raise SystemExit(f'fleet: dirty contract {tid}')
      blob=contract.read_bytes(); h=hashlib.sha256(blob).hexdigest()
      records.append({'id':tid,'contract_path':str(contract),'contract_sha256':h,'allowed_paths':norm,'state':'locked'})
out=state/'members'; out.mkdir(parents=True,exist_ok=True)
if (state/'fleet.json').exists() or (state/'fleet.json').is_symlink(): raise SystemExit('fleet: fleet metadata already exists')
destinations=[out/(r['id']+'.json') for r in records]
for r,destination in zip(records,destinations):
    if destination.exists() or destination.is_symlink(): raise SystemExit(f"fleet: member metadata already exists: {r['id']}")
for r,destination in zip(records,destinations):
    destination.write_text(json.dumps(r,sort_keys=True,indent=2)+'\n')
(state/'fleet.json').write_text(json.dumps({'fleet_id':fleet_id,'base_branch':base_branch,'ui':ui,'members':[r['id'] for r in records]},sort_keys=True,indent=2)+'\n')
PY

created=(); port=; runtime_created=0; state_created=1; compose_created=0; compose_started=0; base="sdd-fleet/$fleet_id"; work="$root/../.sdd-fleet-$fleet_id-$(basename "$root")"; branch="$base"
cleanup(){ local rc=$?; if ((rc!=0)); then
  if ((compose_started)); then docker compose --project-name "sdd_fleet_$fleet_id" --env-file "$state/runtime.env" -f "$state/docker-compose.yml" down >/dev/null 2>&1 || true; fi
  if ((compose_created)); then rm -f "$state/docker-compose.yml"; fi
  [[ -n "$port" ]] && rm -f "$state/port-$port"
  if ((runtime_created)); then rm -f "$state/runtime.env"; fi
  if ((state_created)); then
    if ((fleet_preexisting == 0)); then
      rm -f "$state/fleet.json"
      for f in "$state"/members/*.json; do [[ -f "$f" ]] && rm -f "$f"; done
    else
      for f in "$state"/members/*.json; do
        [[ -f "$f" ]] || continue
        keep=0; for old in "${preexisting_members[@]}"; do [[ "$f" == "$old" ]] && keep=1; done
        if ((keep==0)); then rm -f "$f"; fi
      done
    fi
  fi
  for p in "${created[@]}"; do git -C "$root" worktree remove --force "$p" >/dev/null 2>&1 || true; done
fi; fleet_unlock "$lock"; exit "$rc"; }
trap cleanup EXIT
git -C "$root" show-ref --verify --quiet "refs/heads/$branch" && fleet_die "branch collision: $branch"
git -C "$root" worktree add -b "$branch" "$work" "$base_branch" >/dev/null
created+=("$work")
[[ "${SDD_FLEET_FAIL_AFTER_WORKTREE:-}" == 1 ]] && fleet_die "injected post-worktree failure"
port=$(fleet_allocate_port "$state" "${SDD_FLEET_PORT_START:-43000}" "${SDD_FLEET_PORT_END:-43100}")
fleet_write_runtime_env "$state" "$port"
runtime_created=1
if ((compose)); then
  command -v docker >/dev/null || fleet_die "docker is required for Compose startup"
  docker compose version >/dev/null 2>&1 || fleet_die "Docker Compose v2 is required"
  [[ ! -e "$state/docker-compose.yml" && ! -L "$state/docker-compose.yml" ]] || fleet_die "Compose file already exists"
  cp "$HERE/../../../templates/docker-compose.sdd-fleet.yml" "$state/docker-compose.yml"
  compose_created=1
  docker compose --project-name "sdd_fleet_$fleet_id" --env-file "$state/runtime.env" -f "$state/docker-compose.yml" up -d >/dev/null || fleet_die "Compose startup failed"
  compose_started=1
fi
for f in "${tasks[@]}"; do :; done
python3 - "$state" "$work" "$branch" "$port" <<'PY'
import json,sys
from pathlib import Path
s=Path(sys.argv[1]); work=Path(sys.argv[2]); branch=sys.argv[3]; port=sys.argv[4]
for p in (s/'members').glob('*.json'):
 d=json.loads(p.read_text()); d.update({'branch':branch,'worktree':str(work),'port':int(port)}); p.write_text(json.dumps(d,sort_keys=True,indent=2)+'\n')
PY
printf '%s\n' "$(cat "$state/fleet.json")"
