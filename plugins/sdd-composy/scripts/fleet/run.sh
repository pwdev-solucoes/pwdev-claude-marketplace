#!/usr/bin/env bash
# Run one authorized SDD fleet task autonomously inside its registered fleet worktree.
set -Eeuo pipefail

usage() { printf 'Usage: %s <lowercase-slug> <worktree-path> [danger-full-access]\n' "${0##*/}" >&2; exit 2; }
fail() { printf 'sdd-fleet-run: %s\n' "$*" >&2; exit 2; }
[[ $# -eq 2 || $# -eq 3 ]] || usage
SLUG=$1; WORKTREE_INPUT=$2
EXPECTED_RUNTIME=${SDD_FLEET_RUNTIME:-}
case "$EXPECTED_RUNTIME" in codex|hermes|opencode) CLI_RUNTIME=$EXPECTED_RUNTIME;; claude-code) CLI_RUNTIME=claude;; '') fail 'fleet runtime is required';; *) fail "unsupported fleet runtime: $EXPECTED_RUNTIME";; esac
[[ $SLUG =~ ^[A-Za-z0-9][A-Za-z0-9-]*$ && $SLUG != dashboard && $SLUG != DASHBOARD ]] || fail "invalid slug: $SLUG"
SDD_FLEET_PERMISSION_MODE=safe
if [[ $# -eq 3 ]]; then [[ $3 == danger-full-access ]] || fail 'permission mode must be danger-full-access'; SDD_FLEET_PERMISSION_MODE=danger-full-access; fi
# $EXPECTED_RUNTIME is constrained to codex|hermes|opencode|claude above, so it names the provider binary.
for binary in git jq "$CLI_RUNTIME" shasum awk python3 sleep; do command -v "$binary" >/dev/null 2>&1 || fail "required binary unavailable: $binary"; done
PYTHON3_BIN=$(command -v python3)

WORKTREE=$(cd -- "$WORKTREE_INPUT" 2>/dev/null && pwd -P) || fail 'worktree path is unavailable'
MEMBER_WORKTREE=""
EXPECTED_BRANCH=sdd-fleet/$SLUG
WORKTREE_LIST=$(git -C "$WORKTREE" worktree list --porcelain 2>/dev/null) || fail 'unable to inspect Git worktree registration'
FIRST_REGISTRATION=${WORKTREE_LIST%%$'\n'*}
[[ $FIRST_REGISTRATION == worktree\ * ]] || fail 'unable to derive initiating worktree root'
MAIN_INPUT=${FIRST_REGISTRATION#worktree }
MAIN_ROOT=$(cd -- "$MAIN_INPUT" 2>/dev/null && pwd -P) || fail 'initiating worktree root is unavailable'
FLEET_DIR=$MAIN_ROOT/.planning/sdd-composy/fleet
if [[ -d "$FLEET_DIR/$SLUG" ]]; then FLEET_DIR=$FLEET_DIR/$SLUG; fi
MEMBER_FILE=$FLEET_DIR/members/$SLUG.json
[[ -f $MEMBER_FILE ]] || MEMBER_FILE=$FLEET_DIR/$SLUG.json
if [[ -n ${SDD_FLEET_MEMBER_FILE:-} ]]; then
  MEMBER_FILE=$SDD_FLEET_MEMBER_FILE
  MEMBER_FILE=$(cd -- "${MEMBER_FILE%/*}" 2>/dev/null && printf '%s/%s' "$PWD" "${MEMBER_FILE##*/}") || fail 'unsafe explicit member binding'
  case "$MEMBER_FILE" in */.planning/sdd-composy/fleet/*/members/*.json) ;; *) fail 'unsafe explicit member binding';; esac
  [[ -f $MEMBER_FILE && ! -L $MEMBER_FILE ]] || fail 'unsafe explicit member binding'
  FLEET_DIR=${MEMBER_FILE%/members/*}
  EXPECTED_BRANCH=$(jq -er '.branch' "$MEMBER_FILE") || fail 'missing registered branch'
fi

safe_dir_under() {
  local base=$1 relative=$2 create=${3:-false} current component next canonical old_ifs
  base=$(cd -- "$base" 2>/dev/null && pwd -P) || return 1
  current=$base; old_ifs=$IFS
  [[ $relative != /* && $relative != *..* ]] || return 1
  IFS=/
  for component in $relative; do
    [[ -n $component && $component != . ]] || continue
    next=$current/$component
    [[ ! -L $next ]] || { IFS=$old_ifs; return 1; }
    if [[ -e $next ]]; then [[ -d $next ]] || { IFS=$old_ifs; return 1; }
    else
      [[ $create == true ]] || { IFS=$old_ifs; return 1; }
      mkdir "$next" || { IFS=$old_ifs; return 1; }
      [[ ! -L $next && -d $next ]] || { IFS=$old_ifs; return 1; }
    fi
    canonical=$(cd -- "$next" 2>/dev/null && pwd -P) || { IFS=$old_ifs; return 1; }
    case $canonical in "$base"|"$base"/*) ;; *) IFS=$old_ifs; return 1 ;; esac
    current=$canonical
  done
  IFS=$old_ifs
}
safe_main_dir() { safe_dir_under "$MAIN_ROOT" "$1" "${2:-false}"; }
safe_worktree_dir() { safe_dir_under "$WORKTREE" "$1" "${2:-false}"; }
require_regular_nosymlink() { [[ -e $1 && -f $1 && ! -L $1 ]]; }

registered_worktree_matches() {
  local list line active=false
  list=$(git -C "$WORKTREE" worktree list --porcelain 2>/dev/null) || return 1
  while IFS= read -r line; do
    case $line in
      worktree\ *) if [[ ${line#worktree } == "$WORKTREE" ]]; then active=true; else active=false; fi ;;
      branch\ *) if [[ $active == true && ${line#branch } == "refs/heads/$EXPECTED_BRANCH" ]]; then return 0; fi ;;
    esac
  done <<<"$list"
  return 1
}

member_binding_matches() {
  require_regular_nosymlink "$MEMBER_FILE" || return 1
  MEMBER_WORKTREE=$(jq -r '.worktree_path // ""' "$MEMBER_FILE" 2>/dev/null)
  MEMBER_WORKTREE=$(cd -- "$MEMBER_WORKTREE" 2>/dev/null && pwd -P) || return 1
  jq -e --arg slug "$SLUG" --arg branch "$EXPECTED_BRANCH" --arg worktree "$WORKTREE" --arg runtime "$EXPECTED_RUNTIME" --arg root "$MAIN_ROOT" '
    type == "object" and .schema_version == "2" and .slug == $slug and .branch == $branch and
    .worktree_path == $worktree and .repository_root == $root and .runtime == $runtime and (.status == "pending" or .status == "running")
  ' "$MEMBER_FILE" >/dev/null 2>&1
}

worktree_identity_matches() {
  local current_root current_branch current_list current_first current_main
  current_root=$(git -C "$WORKTREE" rev-parse --show-toplevel 2>/dev/null) || return 1
  [[ $current_root == "$WORKTREE" ]] || return 1
  current_branch=$(git -C "$WORKTREE" symbolic-ref --quiet --short HEAD 2>/dev/null) || return 1
  [[ $current_branch == "$EXPECTED_BRANCH" ]] || return 1
  registered_worktree_matches || return 1
  current_list=$(git -C "$WORKTREE" worktree list --porcelain 2>/dev/null) || return 1
  current_first=${current_list%%$'\n'*}; [[ $current_first == worktree\ * ]] || return 1
  current_main=$(cd -- "${current_first#worktree }" 2>/dev/null && pwd -P) || return 1
  [[ $current_main == "$MAIN_ROOT" ]] || return 1
  member_binding_matches
}

safe_main_dir .planning/sdd-composy/fleet false || fail 'registered fleet member central state path is unsafe'
require_regular_nosymlink "$MEMBER_FILE" || fail "registered fleet member is unavailable or unsafe for $SLUG"
if ! jq -e '.schema_version == "2"' "$MEMBER_FILE" >/dev/null 2>&1; then fail 'legacy fleet member requires explicit migration'; fi
if ! jq -e --arg slug "$SLUG" --arg branch "$EXPECTED_BRANCH" --arg worktree "$WORKTREE" '
  type == "object" and .slug == $slug and .branch == $branch and .worktree_path == $worktree and (.status | type == "string")
' "$MEMBER_FILE" >/dev/null 2>&1; then fail "registered fleet member does not bind $SLUG to the supplied worktree"; fi
CENTRAL_STATUS=$(jq -r '.status // ""' "$MEMBER_FILE")
[[ $CENTRAL_STATUS == pending || $CENTRAL_STATUS == running ]] || fail "central member status $CENTRAL_STATUS cannot start a runner"
BOUND_LOOP_ID=$(jq -r '.interaction.loop.id // ""' "$MEMBER_FILE")
worktree_identity_matches || fail 'registered fleet member does not match canonical Git worktree registration'
SCRIPT_DIR=$(cd -- "${BASH_SOURCE[0]%/*}" && pwd -P)
[[ -n $BOUND_LOOP_ID ]] || fail 'fleet member has no bound LOOP; relaunch it with launch.sh'
BOUND_TASK_ID=$(jq -er '.task_id' "$MEMBER_FILE") || fail 'bound headless member has no task identity'
BOUND_LOOP_TASK=$(jq -er '.interaction.loop.task_id' "$MEMBER_FILE") || fail 'bound headless member has no LOOP task identity'
[[ $BOUND_LOOP_TASK == "$BOUND_TASK_ID" ]] || fail 'bound headless LOOP task identity diverges'
# The LOOP runs unattended here, so the human approval must already be on record; the runner
# never infers or supplies it.
jq -e '.approval.by | type == "string" and length > 0' "$MEMBER_FILE" >/dev/null 2>&1 \
  || fail 'headless member has no recorded human approval; relaunch with --human-approved --approved-by <actor>'

RUNNER_LOCK=$FLEET_DIR/.${SLUG}.runner.lock
safe_main_dir .planning/sdd-composy/fleet false || fail 'unsafe central fleet state path'
mkdir "$RUNNER_LOCK" 2>/dev/null || fail "fleet member is already running: $SLUG"
ORCHESTRATOR_PID=
release() {
  if [[ -n $ORCHESTRATOR_PID ]]; then
    # The orchestrator leads its own process group; take the provider down with it.
    kill -TERM -- "-$ORCHESTRATOR_PID" 2>/dev/null || kill -TERM "$ORCHESTRATOR_PID" 2>/dev/null || true
    wait "$ORCHESTRATOR_PID" 2>/dev/null || true
  fi
  rmdir "$RUNNER_LOCK" 2>/dev/null || true
}
trap release EXIT
trap 'exit 143' TERM
trap 'exit 130' INT
trap 'exit 129' HUP

"$PYTHON3_BIN" -c 'import os,sys; os.setsid(); os.execvp(sys.argv[1], sys.argv[1:])' \
  "$PYTHON3_BIN" - "$SCRIPT_DIR" "$MAIN_ROOT" "$WORKTREE" "$MEMBER_FILE" "$BOUND_TASK_ID" "$BOUND_LOOP_ID" "$CLI_RUNTIME" <<'PY' &
import importlib.util, json, os, subprocess, sys, tempfile
from datetime import datetime, timezone
from pathlib import Path

script_dir, main_root, worktree, member_file, task_id, loop_id, runtime = sys.argv[1:]
sys.path.insert(0, str(Path(script_dir).parent)); sys.path.insert(0, script_dir)
import interactive_state, sdd_loop, sdd_state

def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path); module = importlib.util.module_from_spec(spec)
    assert spec.loader; spec.loader.exec_module(module); return module

def now():
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")

def git(*args):
    return subprocess.run(["git", "-C", worktree, *args], capture_output=True, text=True, check=True).stdout

member = interactive_state.load_member(member_file)
record = sdd_loop.status(main_root, loop_id)
if record["id"] != loop_id or record["task_id"] != task_id: raise SystemExit(2)
engine_module = load("sdd_fleet_headless_engine", Path(script_dir).parent / f"loop-engine-{runtime}.py")
# Authorization mirrors the engine adapters: SDD_<RUNTIME>_ISOLATED or _AUTOMATION_CONSENT, plus the
# permission mode. The LOOP root tells the runtime where the VERIFY command record belongs.
prefix = "SDD_" + runtime.upper() + "_"
extra = {"permission_mode": os.environ.get("SDD_FLEET_PERMISSION_MODE", "safe"), "loop_root": main_root}
if os.environ.get(prefix + "ISOLATED") == "1": extra["isolation_confirmed"] = True
if os.environ.get(prefix + "AUTOMATION_CONSENT") == "1": extra["automation_consent"] = True
if member["interaction"]["state"] == "starting":
    interactive_state.transition(member_file, "starting", "running", {"next_action": "observe-headless-loop"}, now())
engine = lambda contract: engine_module.run(contract, Path(worktree), loop_root=Path(main_root))
loop = sdd_loop.orchestrate(main_root, task_id, engine, loop_id=loop_id, max_iterations=record["max_iterations"],
                            human_approved=bool((member.get("approval") or {}).get("by")), contract_extra=extra)

commit, status, message = None, "failed", f"LOOP stopped: {loop.get('stop_reason', loop['status'])}"
if loop["status"] == "completed":
    allowed = member.get("allowed_paths") or []
    changed = [line[3:].split(" -> ")[-1] for line in git("status", "--porcelain", "--untracked-files=all").splitlines()]
    outside = [path for path in changed if not any(path == a.rstrip("/") or path.startswith(a.rstrip("/") + "/") for a in allowed)]
    if outside:
        status, message = "blocked", "changes outside allowed paths: " + ", ".join(sorted(outside))
    else:
        if changed:
            git("add", "-A", "--", *changed)
            git("commit", "-q", "-m", f"sdd-fleet: {task_id} ({loop_id})")
        commit = git("rev-parse", "HEAD").strip()
        status, message = "completed", f"LOOP {loop_id} completed"
elif loop["status"] in {"needs_human", "blocked", "external_authorization", "destructive_action", "destructive_request",
                        "scope_expansion", "scope_drift", "architectural_ambiguity", "new_architecture", "third_rejection"}:
    status = "blocked"

owner = member["owner"]
relative = f".planning/sdd-composy/fleet/{owner['fleet_id']}/results/{member['id']}.json"
target = Path(main_root) / relative
target.parent.mkdir(parents=True, exist_ok=True)
stamp = now()
result = {"schema_version": "1", "member_id": member["id"], "task_id": task_id, "loop_id": loop_id,
          "loop_status": loop["status"], "status": status, "commit": commit, "message": message, "completed_at": stamp}
fd, temporary = tempfile.mkstemp(prefix="." + target.name + ".", dir=target.parent)
with os.fdopen(fd, "w") as stream:
    json.dump(result, stream, indent=2, sort_keys=True); stream.write("\n")
os.replace(temporary, target)
interactive_state.finish(member_file, status, result_path=relative, message=message, commit=commit, now=stamp)
interaction = interactive_state.load_member(member_file)["interaction"]["state"]
if interaction in {"running", "awaiting_human"}:
    interactive_state.transition(member_file, interaction, status if status != "cancelled" else "failed",
                                 {"next_action": "inspect-result"}, stamp)
sdd_state.fleet_changed(main_root, member["id"], status, task_id=task_id)
print(json.dumps(result, sort_keys=True))
raise SystemExit(0 if status == "completed" else 1)
PY
ORCHESTRATOR_PID=$!
set +e
wait "$ORCHESTRATOR_PID"; STATUS=$?
set -e
ORCHESTRATOR_PID=
exit "$STATUS"
