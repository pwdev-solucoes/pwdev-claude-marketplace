#!/usr/bin/env bash
set -euo pipefail
HERE=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
. "$HERE/common.sh"
usage(){ echo "usage: launch.sh --runtime claude|codex|hermes --root ROOT --fleet-id ID --base-branch BRANCH --task TASK.json [--task TASK.json ...] [--compose] [--ui auto|cmux|tmux|headless]" >&2; exit 2; }
root= fleet_id= base_branch= compose=0; ui=auto; tasks=(); prepare=0; runtime=
while (($#)); do case "$1" in
  --root) root=${2:-}; shift 2;; --fleet-id) fleet_id=${2:-}; shift 2;;
  --prepare-only) prepare=1; shift;; --runtime) runtime=${2:-}; shift 2;;
  --base-branch) base_branch=${2:-}; shift 2;; --task) tasks+=("${2:-}"); shift 2;; --compose) compose=1; shift;; --ui) ui=${2:-}; shift 2;; *) usage;; esac; done
[[ -n "$root" && -n "$fleet_id" && -n "$base_branch" && ${#tasks[@]} -gt 0 ]] || usage
case "$runtime" in claude) record_runtime=claude-code; cli_runtime=claude;; codex|hermes) record_runtime=$runtime; cli_runtime=$runtime;; '') fleet_die 'launch runtime is required';; *) fleet_die 'unsupported fleet runtime';; esac
root=$(fleet_abs "$root"); [[ -d "$root/.git" || -f "$root/.git" ]] || fleet_die "root is not a git repository"
root=$(cd -- "$root" && pwd -P)
git_root=$(git -C "$root" rev-parse --show-toplevel 2>/dev/null) || fleet_die 'root is not a git repository'
git_root=$(cd -- "$git_root" && pwd -P)
[[ $git_root == "$root" ]] || fleet_die 'root must be the exact Git worktree root'
[[ $prepare == 1 ]] || command -v "$cli_runtime" >/dev/null || fleet_die 'runtime unavailable'
ui=$(fleet_select_ui "$ui") || exit $?
state=$(fleet_state_dir "$root" "$fleet_id")
fleet_no_symlink_components "$state" || fleet_die 'fleet state path has a symlink component'
mkdir -p "$state/members"
export FLEET_ID="$fleet_id"
fleet_preexisting=0; [[ -e "$state/fleet.json" || -L "$state/fleet.json" ]] && fleet_preexisting=1
preexisting_members=(); while IFS= read -r -d '' f; do preexisting_members+=("$f"); done < <(find "$state/members" -maxdepth 1 -type f -name '*.json' -print0 2>/dev/null)
lock="$state/.lock"; fleet_lock "$lock"; trap 'fleet_unlock "$lock"' EXIT
[[ "$fleet_id" =~ ^[A-Za-z0-9._-]+$ ]] || fleet_die "invalid fleet id"
command -v git >/dev/null || fleet_die "git is required"
git -C "$root" show-ref --verify --quiet "refs/heads/$base_branch" || fleet_die "unknown base branch"

python3 - "$root" "$state" "$fleet_id" "$base_branch" "$ui" "$record_runtime" "${tasks[@]}" <<'PY'
import json,sys,hashlib,re,os,tempfile
from pathlib import Path
root,state=map(Path,sys.argv[1:3]); fleet_id=sys.argv[3]; base_branch=sys.argv[4]; ui=sys.argv[5]; runtime=sys.argv[6]; files=[Path(x) for x in sys.argv[7:]]
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
      if not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_-]*',tid) or any(oid==tid for _,oid in seen): raise SystemExit('fleet: invalid or duplicate task identity')
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
      records.append({'schema_version':'2','id':tid,'task_id':tid,'slug':tid.lower(),'contract_path':str(contract.absolute()),'contract_sha256':h,'allowed_paths':norm,'verification_commands':task['verification_commands'],'state':'locked','status':'pending','runtime':runtime,'ui':ui,'repository_root':str(root.resolve()),'owner':{'kind':'sdd-composy-fleet','fleet_id':fleet_id,'member_id':tid}})
out=state/'members'; out.mkdir(parents=True,exist_ok=True)
if (state/'fleet.json').exists() or (state/'fleet.json').is_symlink(): raise SystemExit('fleet: fleet metadata already exists')
destinations=[out/(r['id']+'.json') for r in records]
for r,destination in zip(records,destinations):
    if destination.exists() or destination.is_symlink(): raise SystemExit(f"fleet: member metadata already exists: {r['id']}")
def publish(path,data):
    fd,tmp=tempfile.mkstemp(prefix='.'+path.name+'.',dir=path.parent)
    try:
      with os.fdopen(fd,'w') as stream: json.dump(data,stream,sort_keys=True,indent=2); stream.write('\n')
      os.replace(tmp,path)
    finally:
      if os.path.exists(tmp): os.unlink(tmp)
for r,destination in zip(records,destinations): publish(destination,r)
publish(state/'fleet.json',{'schema_version':'2','fleet_id':fleet_id,'base_branch':base_branch,'runtime':runtime,'ui':ui,'owner':{'kind':'sdd-composy-fleet','fleet_id':fleet_id},'members':[r['id'] for r in records]})
PY

created=(); branches=(); ports=(); port=; runtime_created=0; state_created=1; compose_created=0; compose_started=0; base="sdd-fleet/$fleet_id"
cleanup(){ local rc=$?; set +e; if ((rc!=0)); then
  if ((compose_started)); then docker compose --project-name "sdd_fleet_$fleet_id" --env-file "$state/runtime.env" -f "$state/docker-compose.yml" down >/dev/null 2>&1 || true; fi
  if ((compose_created)); then rm -f "$state/docker-compose.yml"; fi
  [[ -n "$port" ]] && rm -f "$state/port-$port"
  if ((${#ports[@]})); then for allocated in "${ports[@]}"; do rm -f "$state/port-$allocated"; done; fi
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
  if ((${#created[@]})); then for p in "${created[@]}"; do git -C "$root" worktree remove --force "$p" >/dev/null 2>&1 || true; done; fi
  git -C "$root" worktree prune >/dev/null 2>&1 || true
  if ((${#branches[@]})); then for b in "${branches[@]}"; do git -C "$root" branch -D "$b" >/dev/null 2>&1 || true; done; fi
fi; fleet_unlock "$lock"; exit "$rc"; }
trap cleanup EXIT
for member_file in "$state"/members/*.json; do
member=$(fleet_json_string "$member_file" id)
branch="$base/$member"; work="$root/../.sddcomposy-fleet-$fleet_id-$member-$(basename "$root")"
git -C "$root" show-ref --verify --quiet "refs/heads/$branch" && fleet_die "branch collision: $branch"
git -C "$root" worktree add -b "$branch" "$work" "$base_branch" >/dev/null
work=$(cd "$work" && pwd -P)
created+=("$work")
branches+=("$branch")
[[ "${SDD_FLEET_FAIL_AFTER_WORKTREE:-}" == 1 ]] && fleet_die "injected post-worktree failure"
port=$(fleet_allocate_port "$state" "${SDD_FLEET_PORT_START:-43000}" "${SDD_FLEET_PORT_END:-43100}")
ports+=("$port")
if ((runtime_created == 0)); then fleet_write_runtime_env "$state" "$port"; runtime_created=1; fi
python3 - "$member_file" "$work" "$branch" "$port" "$record_runtime" "$fleet_id" "$compose" <<'PY'
import json,sys,os,tempfile
from datetime import datetime,timezone
from pathlib import Path
p=Path(sys.argv[1]); d=json.loads(p.read_text()); work=str(Path(sys.argv[2]).resolve()); branch=sys.argv[3]; port=int(sys.argv[4]); now=datetime.now(timezone.utc).isoformat().replace('+00:00','Z'); fleet_id=sys.argv[6]; compose_project='sdd_fleet_'+fleet_id
d.update(worktree=work,worktree_path=work,branch=branch,port=port,runtime=sys.argv[5],started_at=now,updated_at=now,resources={'branch':branch,'worktree_path':work,'port':port,'compose_project':compose_project,'compose_file':'.planning/sdd-composy/fleet/'+fleet_id+'/docker-compose.yml','compose_allocated':sys.argv[7]=='1'})
fd,tmp=tempfile.mkstemp(prefix='.'+p.name+'.',dir=p.parent)
with os.fdopen(fd,'w') as stream: json.dump(d,stream,sort_keys=True,indent=2); stream.write('\n')
os.replace(tmp,p)
PY
done
if ((compose)); then
  command -v docker >/dev/null || fleet_die "docker is required for Compose startup"
  docker compose version >/dev/null 2>&1 || fleet_die "Docker Compose v2 is required"
  [[ ! -e "$state/docker-compose.yml" && ! -L "$state/docker-compose.yml" ]] || fleet_die "Compose file already exists"
  cp "$HERE/../../templates/docker-compose.sdd-fleet.yml" "$state/docker-compose.yml"
  compose_created=1
  compose_sha256=$(fleet_hash "$state/docker-compose.yml")
  for member_file in "$state"/members/*.json; do
    python3 - "$member_file" "$compose_sha256" <<'PY'
import json,os,sys,tempfile
from pathlib import Path
p=Path(sys.argv[1]); d=json.loads(p.read_text()); d['resources']['compose_sha256']=sys.argv[2]
fd,tmp=tempfile.mkstemp(prefix='.'+p.name+'.',dir=p.parent)
with os.fdopen(fd,'w') as stream: json.dump(d,stream,sort_keys=True,indent=2); stream.write('\n')
os.replace(tmp,p)
PY
  done
  docker compose --project-name "sdd_fleet_$fleet_id" --env-file "$state/runtime.env" -f "$state/docker-compose.yml" up -d >/dev/null || fleet_die "Compose startup failed"
  compose_started=1
fi
if ((prepare == 0)); then
  . "$HERE/ui-$ui.sh"
  # Validate every approved phase before starting any runner. Never manufacture approvals.
  for member_file in "$state"/members/*.json; do
    work=$(fleet_json_string "$member_file" worktree); slug=$(fleet_json_string "$member_file" slug)
    for contract in spec decisions; do
      file="$work/.planning/sdd-composy/phases/$slug/$contract.md"
      fleet_require_regular "$file" || fleet_die "missing approved phase contract: $file"
      [[ $(awk '/^Status: APPROVED$/ {n++} END {print n+0}' "$file") == 1 ]] || fleet_die 'phase requires existing approval'
    done
  done
  # Once processes start, preserve all recovery resources on any dispatch failure.
  trap 'fleet_unlock "$lock"' EXIT
  for member_file in "$state"/members/*.json; do
    work=$(fleet_json_string "$member_file" worktree); slug=$(fleet_json_string "$member_file" slug)
    handle="$state/$slug.ui.json"
    cmd=(env "SDD_FLEET_RUNTIME=$record_runtime" "SDD_FLEET_MEMBER_FILE=$member_file" "$HERE/run.sh" "$slug" "$work")
    if [[ $ui == headless ]]; then fleet_ui_headless_start "$handle" "$work" "${cmd[@]}"
    else "fleet_ui_${ui}_start" "$handle" "$work" "$fleet_id-$slug" "${cmd[@]}"; fi
  done
fi
printf '%s\n' "$(cat "$state/fleet.json")"
