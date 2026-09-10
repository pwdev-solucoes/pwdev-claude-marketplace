#!/usr/bin/env bash
# Bounded fleet teardown; failed cleanup preserves recovery state.
set -Eeuo pipefail
HERE=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd -P)
. "$HERE/common.sh"
fail(){ printf 'fleet-teardown: %s\n' "$*" >&2; exit 2; }
usage(){ printf 'Usage: %s --root ROOT --fleet-id ID --member-id ID [--merge --confirm CONFIRM-SDD-MERGE]\n' "${0##*/}" >&2; exit 2; }
root= fleet= member= merge=false confirm=
while (($#)); do case "$1" in
  --root) root=${2:-}; shift 2;; --fleet-id) fleet=${2:-}; shift 2;;
  --member-id|--member) member=${2:-}; shift 2;; --merge) merge=true; shift;;
  --confirm) confirm=${2:-}; shift 2;; *) usage;; esac; done
[[ -n $root && -n $fleet && -n $member ]] || usage
[[ $fleet =~ ^[A-Za-z0-9._-]+$ && $member =~ ^[A-Za-z0-9._-]+$ ]] || fail 'invalid fleet or member identity'
root=$(fleet_abs "$root"); [[ -d "$root/.git" || -f "$root/.git" ]] || fail 'root is not a git repository'
root=$(cd -- "$root" && pwd -P)
state=$(fleet_state_dir "$root" "$fleet"); member_file="$state/members/$member.json"
fleet_require_regular "$member_file" || fail 'member metadata is missing or unsafe'
[[ $merge == false || $confirm == CONFIRM-SDD-MERGE ]] || fail 'merge requires explicit confirmation token CONFIRM-SDD-MERGE'
command -v git >/dev/null 2>&1 || fail 'git is required'
branch=$(fleet_json_string "$member_file" branch) || fail 'member branch is missing'
worktree=$(fleet_json_string "$member_file" worktree_path 2>/dev/null || fleet_json_string "$member_file" worktree) || fail 'member worktree is missing'
status=$(jq -er '.status // .state // ""' "$member_file" 2>/dev/null) || fail 'member status is invalid'
if [[ $merge == true && $status != completed ]]; then fail "refusing merge: member status $status is not completed"; fi
raw_worktree=$worktree
if [[ "$raw_worktree" = /* ]]; then candidate=$raw_worktree; else candidate=$root/$raw_worktree; fi
fleet_no_symlink_components "$candidate" || fail 'member worktree path or parent is a symlink'
if [[ "$raw_worktree" = /* ]]; then worktree=$(fleet_abs "$raw_worktree"); else worktree=$(fleet_abs "$root/$raw_worktree"); fi
worktree=$(cd "$worktree" 2>/dev/null && pwd -P) || fail 'member worktree is missing or unsafe'
[[ "$worktree" != "$root" && "$worktree" != "$root"/* ]] || fail 'member worktree must be outside repository root'
if [[ $merge == true ]]; then
  fleet_verify_binding "$member_file" || fail 'refusing merge: task contract changed'
  jq -e '.verification_commands | type == "array" and length > 0 and all(.[]; type == "string" and length > 0)' "$member_file" >/dev/null || fail 'refusing merge: verification commands missing'
  result=$(fleet_json_string "$member_file" result_path 2>/dev/null || true); [[ -n $result ]] || fail 'refusing merge: completed member has no result'
  [[ "$result" = /* ]] && result_path=$result || result_path=$root/$result
  fleet_require_regular "$result_path" || fail 'refusing merge: result is missing or unsafe'
  result_commit=$(jq -er '.commit | select(type == "string" and test("^[0-9a-f]{40}$"))' "$result_path" 2>/dev/null) || fail 'refusing merge: result identity or commit is invalid'
  jq -e --arg id "$member" '(.member_id == $id) and (.status == "completed")' "$result_path" >/dev/null 2>&1 || fail 'refusing merge: result identity or commit is invalid'
  [[ -n $(git -C "$root" symbolic-ref --quiet --short HEAD 2>/dev/null || true) ]] || fail 'refusing merge: repository is detached'
  git -C "$root" diff --quiet && git -C "$root" diff --cached --quiet || fail 'refusing merge: repository is dirty'
fi
[[ -d "$worktree" && ! -L "$worktree" ]] || fail 'member worktree is missing or unsafe'
actual=$(git -C "$worktree" rev-parse --show-toplevel 2>/dev/null || true); [[ "$actual" == "$worktree" ]] || fail 'member worktree identity does not match'
if [[ $merge == true ]]; then
  actual_commit=$(git -C "$worktree" rev-parse HEAD 2>/dev/null) || fail 'refusing merge: member HEAD is unavailable'
  branch_commit=$(git -C "$root" rev-parse "$branch" 2>/dev/null) || fail 'refusing merge: member branch is unavailable'
  [[ "$result_commit" == "$actual_commit" && "$result_commit" == "$branch_commit" ]] || fail 'refusing merge: result commit is not the registered member tip'
fi
resources=$(jq -e '.resources | type == "object"' "$member_file" >/dev/null 2>&1 && echo yes || echo no)
[[ $resources == yes ]] || fail 'member resources are missing; recovery state preserved'
jq -e '.resources.compose_allocated | type == "boolean"' "$member_file" >/dev/null 2>&1 || fail 'Compose allocation flag is missing or invalid; recovery state preserved'
compose_allocated=$(jq -r '.resources.compose_allocated' "$member_file")
jq -e --arg root "$root" --arg fleet "$fleet" --arg member "$member" --arg branch "$branch" --arg worktree "$worktree" \
  '(.repository_root == $root) and (.owner.kind == "sdd-composy-fleet") and (.owner.fleet_id == $fleet) and (.owner.member_id == $member) and (.resources.branch == $branch) and (.resources.worktree_path == $worktree)' \
  "$member_file" >/dev/null || fail 'resource ownership does not match member identity; recovery state preserved'
if [[ "$compose_allocated" == true ]]; then
  compose_file=$(jq -er '.resources.compose_file | select(type == "string" and length > 0)' "$member_file" 2>/dev/null) || fail 'owned Compose file is unspecified; recovery state preserved'
  project=$(jq -er '.resources.compose_project | select(type == "string" and length > 0)' "$member_file" 2>/dev/null) || fail 'owned Compose project is unspecified; recovery state preserved'
  expected_compose=$(jq -er '.resources.compose_sha256 | select(type == "string" and test("^[a-f0-9]{64}$"))' "$member_file" 2>/dev/null) || fail 'Compose ownership hash is missing or invalid; recovery state preserved'
  expected_file=".planning/sdd-composy/fleet/$fleet/docker-compose.yml"
  [[ "$compose_file" == "$expected_file" ]] || fail 'Compose file is not the fleet-owned central resource; recovery state preserved'
  compose_path="$root/$compose_file"
  [[ -f "$compose_path" && ! -L "$compose_path" ]] || fail 'owned Compose file is missing or unsafe; recovery state preserved'
  fleet_no_symlink_components "$compose_path" || fail 'recorded Compose path or parent is a symlink'
  [[ $(fleet_hash "$compose_path") == "$expected_compose" ]] || fail 'Compose file ownership hash changed; recovery state preserved'
  command -v docker >/dev/null 2>&1 || fail 'docker is required to stop the recorded Compose project'
  docker compose --project-name "$project" -f "$compose_path" down >/dev/null || fail 'Compose shutdown failed; recovery state preserved'
fi
lock="$state/.$member.runner.lock"
if [[ -e "$lock" || -L "$lock" ]]; then [[ -d "$lock" && ! -L "$lock" ]] || fail 'runner lock is unsafe'; rmdir "$lock" 2>/dev/null || fail 'runner lock could not be released; recovery state preserved'; fi
if [[ $merge == false ]]; then rm -f -- "$member_file"; printf 'fleet-teardown: stopped %s; preserved branch and worktree\n' "$member"; exit 0; fi
if ! git -C "$root" merge --no-ff "$branch"; then git -C "$root" merge --abort >/dev/null 2>&1 || true; fail "merge failed; recovery state preserved for $member"; fi
git -C "$root" merge-base --is-ancestor "$branch" HEAD || fail 'post-merge verification failed; recovery state preserved'
python3 - "$root" "$member_file" <<'PY' || fail 'post-merge tests failed; merged code, worktree and metadata preserved for recovery'
import json,subprocess,sys
from pathlib import Path
root,record=map(Path,sys.argv[1:]); data=json.loads(record.read_text())
contract=json.loads(Path(data['contract_path']).read_text())
entries=contract.get('tasks',[contract]); task=next((t for t in entries if t.get('id')==data['id']),None)
if not task or task.get('verification_commands')!=data['verification_commands']: raise SystemExit('verification commands do not match bound task')
for command in task['verification_commands']:
    if subprocess.run(command,shell=True,cwd=root,executable='/bin/bash').returncode: raise SystemExit(1)
PY
git -C "$root" worktree remove "$worktree" >/dev/null 2>&1 || fail 'worktree removal failed; merged branch and metadata preserved'
rm -f -- "$member_file"; printf 'fleet-teardown: merged and removed worktree for %s\n' "$member"
