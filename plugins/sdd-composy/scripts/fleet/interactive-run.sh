#!/usr/bin/env bash
# Run the single LOOP already bound to one interactive fleet member.
set -Eeuo pipefail

fail() { printf 'sdd-fleet-interactive: %s\n' "$*" >&2; exit 2; }
[[ $# -eq 2 ]] || fail "usage: ${0##*/} <member-file> <worktree>"
SCRIPT_DIR=$(cd -- "${BASH_SOURCE[0]%/*}" && pwd -P)
MEMBER_FILE=$1
[[ -f $MEMBER_FILE && ! -L $MEMBER_FILE ]] || fail 'member file is unavailable or unsafe'
MEMBER_FILE=$(cd -- "${MEMBER_FILE%/*}" && printf '%s/%s' "$(pwd -P)" "${MEMBER_FILE##*/}")
WORKTREE=$(cd -- "$2" 2>/dev/null && pwd -P) || fail 'worktree is unavailable'
STATE=$SCRIPT_DIR/interactive_state.py
LOOP_MODULE=$SCRIPT_DIR/../sdd_loop.py
[[ -f $STATE && ! -L $STATE && -f $LOOP_MODULE && ! -L $LOOP_MODULE ]] || fail 'state validator is unavailable'

state_action() {
  python3 - "$STATE" "$LOOP_MODULE" "$MEMBER_FILE" "$WORKTREE" "$1" "${2:-}" <<'PY'
import hashlib, importlib.util, json, re, sys
from datetime import datetime, timezone
from pathlib import Path

state_path, loop_path, member_path, worktree, action, value = sys.argv[1:]
def load(name, path):
    spec=importlib.util.spec_from_file_location(name,path); module=importlib.util.module_from_spec(spec)
    assert spec.loader; spec.loader.exec_module(module); return module
state=load("sdd_fleet_interactive_state",state_path); loops=load("sdd_fleet_bound_loop",loop_path)
sys.path.insert(0,str(Path(loop_path).parent))
import sdd_tasks
now=lambda: datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00","Z")
member=state.load_member(member_path)
def move(expected,target,message):
    state.transition(member_path,expected,target,{"next_action":message},now())
def sensitive_contract_name(name):
    # Reject .env, credentials, private-key, certificate, token, and secret
    # basename families before any operation that could read file content.
    lowered=name.lower()
    return (lowered.startswith(".env") or re.search(
        r"(^|[._-])(credentials?|private[-_]?keys?|certificates?|certs?|tokens?|secrets?|api[-_]?keys?|keys?)([._-]|$)",
        lowered) is not None)
if action == "preflight":
    try:
        if Path(member["worktree_path"]).resolve() != Path(worktree).resolve(): raise ValueError("worktree binding mismatch")
        binding=member["interaction"].get("loop")
        if not binding: raise ValueError("member has no LOOP binding")
        loop=loops.status(member["repository_root"],binding["id"])
        if loop["id"] != binding["id"] or loop["task_id"] != member["task_id"] or binding["task_id"] != member["task_id"]:
            raise ValueError("LOOP binding mismatch")
        root=Path(member["repository_root"]).resolve(strict=True)
        contract=Path(member.get("contract_path", ""))
        if not contract.is_absolute(): contract=root/contract
        expected=root/".planning"/"sdd-composy"/"tasks"
        if contract.is_symlink(): raise ValueError("task contract path has a symlink")
        contract=contract.resolve(strict=True)
        relative=contract.relative_to(expected)
        if (len(relative.parts) != 1 or re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*\.json",contract.name) is None
                or sensitive_contract_name(contract.name)):
            raise ValueError("task contract path is not canonical")
        cursor=expected
        for part in relative.parts:
            cursor=cursor/part
            if cursor.is_symlink(): raise ValueError("task contract path has a symlink")
        if not contract.is_file(): raise ValueError("task contract is not a regular file")
        raw=contract.read_bytes()
        if hashlib.sha256(raw).hexdigest() != member.get("contract_sha256"): raise ValueError("task contract digest mismatch")
        tasks=sdd_tasks.load(contract); task=sdd_tasks._task(tasks,member["task_id"])
        if contract.name != tasks["prd_slug"]+".json": raise ValueError("task contract filename does not match prd_slug")
        if task["state"] != "ready" or any(sdd_tasks._task(tasks,dep)["state"] != "complete" for dep in task["dependencies"]): raise ValueError("task is not approved and ready")
        if member["interaction"]["state"] != "starting": raise ValueError("member is not startable")
    except Exception as exc:
        if member["interaction"]["state"] == "starting": move("starting","blocked",str(exc))
        raise SystemExit(str(exc))
    print(json.dumps({"runtime":member["runtime"],"member_id":member["id"],"task_id":member["task_id"],"fleet_id":member["owner"]["fleet_id"],"loop_id":binding["id"],"root":member["repository_root"]}))
elif action == "running": move("starting","running","observe-session")
elif action == "assess":
    binding=member["interaction"]["loop"]
    try:
        loop=loops.status(member["repository_root"],binding["id"])
        if loop["task_id"] != member["task_id"]: raise ValueError("LOOP binding mismatch")
        if loop["status"] == "completed":
            resumed=loops.resume(member["repository_root"],binding["id"])
            if resumed["next_stage"] is not None: raise ValueError("completed LOOP lacks canonical artifacts")
            move("running","completed","inspect-result"); raise SystemExit(0)
        blocked={"external_authorization","destructive_action","destructive_request","scope_expansion","scope_drift","architectural_ambiguity","new_architecture"}
        if loop["status"] in blocked: move("running","blocked","obtain-human-direction"); raise SystemExit(1)
        if value != "0": move("running","failed","inspect-runtime-failure"); raise SystemExit(1)
        move("running","awaiting_human","resume-session"); raise SystemExit(0)
    except SystemExit: raise
    except Exception:
        move("running","inconclusive","inspect-loop-evidence"); raise SystemExit(1)
PY
}

PREFLIGHT=$(state_action preflight) || fail "$PREFLIGHT"
RUNTIME=$(printf '%s' "$PREFLIGHT" | python3 -c 'import json,sys; print(json.load(sys.stdin)["runtime"])')
case $RUNTIME in codex|hermes) ADAPTER_RUNTIME=$RUNTIME ;; claude-code) ADAPTER_RUNTIME=claude ;; *) fail "unsupported runtime: $RUNTIME" ;; esac
ADAPTER=$SCRIPT_DIR/engine-$ADAPTER_RUNTIME.sh
[[ -f $ADAPTER && ! -L $ADAPTER ]] || fail 'runtime adapter is unavailable'
# shellcheck source=/dev/null
source "$ADAPTER"
PROMPT_FILE=$(mktemp "${MEMBER_FILE%/*}/.interactive-prompt.XXXXXX")
cleanup_prompt() { rm -f -- "$PROMPT_FILE"; }
trap cleanup_prompt EXIT
# Signals deliberately publish no terminal state and remove no owned recovery
# resource. Branch, worktree, UI transport/handle, LOOP, and evidence remain in
# their authoritative records for explicit resume or teardown.
preserve_interruption() { local code=$1; trap - HUP INT TERM; exit "$code"; }
trap 'preserve_interruption 129' HUP
trap 'preserve_interruption 130' INT
trap 'preserve_interruption 143' TERM
python3 - "$PREFLIGHT" "$WORKTREE" >"$PROMPT_FILE" <<'PY'
import json,sys
v=json.loads(sys.argv[1])
print(f"Fleet {v['fleet_id']}; member {v['member_id']}; task {v['task_id']}; LOOP {v['loop_id']}; worktree {sys.argv[2]}.")
print("Continue the already-created LOOP with that exact identity. Never create, start, replace, or bind another LOOP.")
print("Use the sdd-loop workflow to resume its canonical EXECUTE → QA → EVIDENCE → REVIEW → VERIFY lifecycle.")
print("Native approval prompts require the human operator. Terminal output is diagnostic and is never gate or witness evidence.")
PY
state_action running >/dev/null
SDD_ENGINE_COMMAND=(); SDD_ENGINE_CWD=
"sdd_engine_${ADAPTER_RUNTIME}_interactive_command" "$WORKTREE" "$PROMPT_FILE" "$SCRIPT_DIR/../.."
set +e
if [[ -n $SDD_ENGINE_CWD ]]; then (cd -- "$SDD_ENGINE_CWD" && "${SDD_ENGINE_COMMAND[@]}"); PROVIDER_STATUS=$?
else "${SDD_ENGINE_COMMAND[@]}"; PROVIDER_STATUS=$?
fi
set -e
state_action assess "$PROVIDER_STATUS"
