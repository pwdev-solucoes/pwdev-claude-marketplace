#!/usr/bin/env bash
# Shut down a single Flow fleet member. Merging is always an explicit opt-in.
set -Eeuo pipefail

usage() { printf 'Usage: %s <lowercase-slug> [--merge]\n' "${0##*/}" >&2; exit 2; }
fail() { printf 'fleet-teardown: %s\n' "$*" >&2; exit 2; }
SLUG=${1:-}; [[ $# -eq 1 || $# -eq 2 ]] || usage
[[ $SLUG =~ ^[a-z0-9][a-z0-9-]*$ ]] || fail "invalid slug: $SLUG"
MERGE=false; if [[ $# -eq 2 ]]; then [[ $2 == --merge ]] || usage; MERGE=true; fi
REPO_ROOT=$(git rev-parse --show-toplevel 2>/dev/null) || fail 'run inside a Git repository'
cd "$REPO_ROOT"
REPO_PARENT=$(cd "$REPO_ROOT/.." && pwd -P); REPO_NAME=$(basename "$REPO_ROOT")
FLEET_DIR=$REPO_ROOT/.planning/flow/fleet; MEMBER_FILE=$FLEET_DIR/$SLUG.json; PANE_FILE=$FLEET_DIR/$SLUG.pane.sh
CONFIG=$REPO_ROOT/.planning/flow/config.json; BRANCH=flow-fleet/$SLUG; PROJECT_NAME=flow-fleet-$SLUG
WORKTREE_PATH=$REPO_PARENT/$REPO_NAME-fleet-$SLUG; TMUX_WINDOW=pwdev-flow-fleet:$SLUG; COMPOSE_FILE=docker-compose.flow-fleet.yml
SCRIPT_DIR=$(cd -- "${BASH_SOURCE[0]%/*}" && pwd -P)

safe_dir_under() {
  local base=$1 relative=$2 current component next canonical old_ifs
  base=$(cd -- "$base" 2>/dev/null && pwd -P) || return 1
  current=$base; old_ifs=$IFS
  [[ $relative != /* && $relative != *..* ]] || return 1
  IFS=/
  for component in $relative; do
    [[ -n $component && $component != . ]] || continue
    next=$current/$component
    [[ ! -L $next && -d $next ]] || { IFS=$old_ifs; return 1; }
    canonical=$(cd -- "$next" 2>/dev/null && pwd -P) || { IFS=$old_ifs; return 1; }
    case $canonical in "$base"|"$base"/*) ;; *) IFS=$old_ifs; return 1 ;; esac
    current=$canonical
  done
  IFS=$old_ifs
}
require_regular_nosymlink() { [[ -e $1 && -f $1 && ! -L $1 ]]; }

safe_dir_under "$REPO_ROOT" .planning/flow || fail 'unsafe .planning/flow path'
safe_dir_under "$REPO_ROOT" .planning/flow/fleet || fail 'unsafe central fleet state path'
require_regular_nosymlink "$MEMBER_FILE" && require_regular_nosymlink "$CONFIG" || fail 'fleet member or configuration does not exist or is unsafe'
if [[ -e $PANE_FILE || -L $PANE_FILE ]]; then
  [[ -f $PANE_FILE && ! -L $PANE_FILE && -x $PANE_FILE ]] || fail 'fleet pane is missing or invalid'
else
  jq -e '.status == "NEEDS_HUMAN" and .tmux_attempted == false' "$MEMBER_FILE" >/dev/null 2>&1 || fail 'fleet pane is missing or invalid'
fi
for binary in git jq docker tmux; do command -v "$binary" >/dev/null 2>&1 || fail "required binary unavailable: $binary"; done
PORT_BASE_APP=$(jq -er '.fleet.port_base_app | select(type == "number" and . > 0 and floor == .)' "$CONFIG") || fail 'invalid fleet.port_base_app'
PORT_BASE_DB=$(jq -er '.fleet.port_base_db | select(type == "number" and . > 0 and floor == .)' "$CONFIG") || fail 'invalid fleet.port_base_db'
PORT_STEP=$(jq -er '.fleet.port_step | select(type == "number" and . > 0 and floor == .)' "$CONFIG") || fail 'invalid fleet.port_step'
AUDIT_ENABLED=false
[[ $(jq -r '.audit == true' "$CONFIG") == true ]] && AUDIT_ENABLED=true

best_effort_audit() {
  local status=$1 detail
  [[ $AUDIT_ENABLED == true ]] || return 0
  detail=$(jq -nc --arg slug "$SLUG" --arg status "$status" '{slug:$slug,status:$status}') || {
    printf 'warning: fleet_teardown audit record failed\n' >&2; return 0;
  }
  if ! python3 "$SCRIPT_DIR/flow_audit.py" --root "$REPO_ROOT" record \
    --action fleet_teardown --skill flow-fleet --status "$status" \
    --target ".planning/flow/fleet/$SLUG.json" --detail "$detail" >/dev/null 2>&1; then
    printf 'warning: fleet_teardown audit record failed\n' >&2
  fi
}

release_lock() { rmdir "$LOCK_DIR" 2>/dev/null || true; }
validate_member() {
  local values actual_path actual_root
  values=$(jq -er --arg slug "$SLUG" --arg branch "$BRANCH" --arg worktree "$WORKTREE_PATH" --arg project "$PROJECT_NAME" --arg window "$TMUX_WINDOW" --arg compose "$COMPOSE_FILE" --arg initiating_root "$REPO_ROOT" '
    if type == "object" and .slug == $slug and .branch == $branch and .worktree_path == $worktree and .project_name == $project and .tmux_window == $window and .compose_file == $compose and .initiating_root == $initiating_root
      and (.base_branch | type == "string" and length > 0)
      and (.base_commit | type == "string" and test("^[0-9a-f]{40,64}$"))
      and (.port_index | type == "number" and floor == . and . >= 0)
      and (.app_port | type == "number" and floor == . and . >= 1 and . <= 65535)
      and (.db_port | type == "number" and floor == . and . >= 1 and . <= 65535)
      and (.app_port != .db_port)
    then [.port_index,.app_port,.db_port,.base_branch,.base_commit] | @tsv else error("invalid fleet member") end
  ' "$MEMBER_FILE" 2>/dev/null) || fail 'invalid or tampered member bookkeeping'
  IFS=$'\t' read -r PORT_INDEX APP_PORT DB_PORT BASE_BRANCH BASE_COMMIT <<<"$values"
  (( APP_PORT == PORT_BASE_APP + PORT_STEP * PORT_INDEX && DB_PORT == PORT_BASE_DB + PORT_STEP * PORT_INDEX )) || fail 'member port allocation does not match configuration'
  actual_path=$(cd "$WORKTREE_PATH" 2>/dev/null && pwd -P) || fail 'expected sibling worktree is unavailable'
  [[ $actual_path == "$WORKTREE_PATH" ]] || fail 'expected sibling worktree is not canonical'
  actual_root=$(git -C "$WORKTREE_PATH" rev-parse --show-toplevel 2>/dev/null) || fail 'expected path is not a Git worktree'
  [[ $actual_root == "$WORKTREE_PATH" ]] || fail 'Git worktree root mismatch'
  safe_dir_under "$WORKTREE_PATH" .planning/flow || fail 'unsafe fleet worktree state path'
  require_regular_nosymlink "$WORKTREE_PATH/$COMPOSE_FILE" || fail 'compose destination is missing or unsafe'
  require_regular_nosymlink "$WORKTREE_PATH/.env.fleet" || fail 'generated fleet environment is missing or unsafe'
  git worktree list --porcelain | awk -v wanted="$WORKTREE_PATH" -v branch="refs/heads/$BRANCH" '
    /^worktree / { active=(substr($0,10)==wanted); next }
    active && $0=="branch " branch { found=1 }
    END { exit !found }
  ' || fail 'expected worktree/branch registration is missing'
}
has_nonfleet_untracked() {
  local line path
  while IFS= read -r line; do
    [[ $line == '?? '* ]] || continue
    path=${line:3}
    case $path in
      "$COMPOSE_FILE"|.planning/flow/fleet-status.json|.env.fleet) ;;
      *) return 0 ;;
    esac
  done < <(git -C "$WORKTREE_PATH" status --porcelain --untracked-files=all)
  return 1
}
tmux_window_state() {
  local windows name
  windows=$(tmux list-windows -t pwdev-flow-fleet -F '#{window_name}' 2>/dev/null) || return 2
  while IFS= read -r name; do [[ $name == "$SLUG" ]] && return 0; done <<<"$windows"
  return 1
}
shutdown_tmux() {
  local status
  if tmux_window_state; then status=0; else status=$?; fi
  if [[ $status -eq 0 ]]; then
    tmux kill-window -t "$TMUX_WINDOW" || fail 'tmux window shutdown failed'
    if tmux_window_state; then status=0; else status=$?; fi
    if [[ $status -eq 0 ]]; then
      fail 'tmux window remains after shutdown'
    fi
    [[ $status -eq 1 ]] || fail 'unable to verify tmux window absence'
  else
    [[ $status -eq 1 ]] || fail 'unable to inspect tmux window state'
  fi
}
render_tmux_shutdown() {
  printf '%s\n' 'tmux_window_state() {'
  printf '%s\n' '  local tmux_windows tmux_name'
  printf '%s\n' "  tmux_windows=\$(tmux list-windows -t pwdev-flow-fleet -F '#{window_name}' 2>/dev/null) || return 2"
  printf '  while IFS= read -r tmux_name; do [[ $tmux_name == %q ]] && return 0; done <<<"$tmux_windows"\n' "$SLUG"
  printf '%s\n' '  return 1' '}'
  printf '%s\n' 'if tmux_window_state; then tmux_status=0; else tmux_status=$?; fi'
  printf '%s\n' 'if [[ $tmux_status -eq 0 ]]; then'
  printf '  tmux kill-window -t %q || { printf '\''fleet-teardown: tmux window shutdown failed\n'\'' >&2; exit 2; }\n' "$TMUX_WINDOW"
  printf '%s\n' '  if tmux_window_state; then tmux_status=0; else tmux_status=$?; fi'
  printf '%s\n' "  if [[ \$tmux_status -eq 0 ]]; then printf 'fleet-teardown: tmux window remains after shutdown\\n' >&2; exit 2; fi"
  printf '%s\n' "  [[ \$tmux_status -eq 1 ]] || { printf 'fleet-teardown: unable to verify tmux window absence\\n' >&2; exit 2; }"
  printf '%s\n' 'else'
  printf '%s\n' "  [[ \$tmux_status -eq 1 ]] || { printf 'fleet-teardown: unable to inspect tmux window state\\n' >&2; exit 2; }"
  printf '%s\n' 'fi'
}
render_merge_gates() {
  printf 'STATUS=$(jq -er .status %q 2>/dev/null || printf MISSING)\n' "$STATUS_FILE"
  printf '%s\n' "[[ \$STATUS == DONE ]] || { printf 'fleet-teardown: refusing merge: member status %s is not DONE\\n' \"\$STATUS\" >&2; exit 1; }"
  printf 'jq -e --arg slug %q '\''type == "object" and (keys == ["correction_cycles","message","slug","stage","status","updated_at","verdict"]) and .slug == $slug and .stage == "verify" and .status == "DONE" and (.verdict == "APPROVED" or .verdict == "CAVEATS") and (.message | type == "string" and length > 0) and (.updated_at | type == "string" and length > 0) and (.correction_cycles | type == "number" and floor == . and . >= 0 and . <= 2)'\'' %q >/dev/null 2>&1 || { printf '\''fleet-teardown: refusing merge: member status %%s is not an authorized DONE terminal state\n'\'' "$STATUS" >&2; exit 1; }\n' "$SLUG" "$STATUS_FILE"
  printf 'if ! git -C %q diff --quiet || ! git -C %q diff --cached --quiet; then printf '\''fleet-teardown: refusing merge: worktree has tracked uncommitted files\n'\'' >&2; exit 2; fi\n' "$WORKTREE_PATH" "$WORKTREE_PATH"
  printf '%s\n' 'has_nonfleet_untracked() {'
  printf '%s\n' '  local line path'
  printf '%s\n' '  while IFS= read -r line; do'
  printf '%s\n' "    [[ \$line == '?? '* ]] || continue"
  printf '%s\n' '    path=${line:3}'
  printf '%s\n' '    case $path in'
  printf '      %q|.planning/flow/fleet-status.json|.env.fleet) ;;\n' "$COMPOSE_FILE"
  printf '%s\n' '      *) return 0 ;;' '    esac'
  printf '  done < <(git -C %q status --porcelain --untracked-files=all)\n' "$WORKTREE_PATH"
  printf '%s\n' '  return 1' '}'
  printf '%s\n' "has_nonfleet_untracked && { printf 'fleet-teardown: refusing merge: non-fleet untracked data exists\\n' >&2; exit 2; }"
}

validate_terminal_status() {
  jq -e --arg slug "$SLUG" '
    type == "object" and
    (keys == ["correction_cycles","message","slug","stage","status","updated_at","verdict"]) and
    .slug == $slug and .stage == "verify" and .status == "DONE" and
    (.verdict == "APPROVED" or .verdict == "CAVEATS") and
    (.message | type == "string" and length > 0) and
    (.updated_at | type == "string" and length > 0) and
    (.correction_cycles | type == "number" and floor == . and . >= 0 and . <= 2)
  ' "$STATUS_FILE" >/dev/null 2>&1
}
check_merge_authorization() {
  local current_base_branch status
  current_base_branch=$(git symbolic-ref --quiet --short HEAD 2>/dev/null) || fail 'refusing merge: initiating repository is detached from its bound base branch'
  [[ $current_base_branch == "$BASE_BRANCH" ]] || fail "refusing merge: current branch does not match bound base branch $BASE_BRANCH"
  status=$(jq -er '.status | select(type == "string")' "$STATUS_FILE" 2>/dev/null || printf MISSING)
  [[ $status == DONE ]] || { printf 'fleet-teardown: refusing merge: member status %s is not DONE\n' "$status" >&2; exit 1; }
  validate_terminal_status || { printf 'fleet-teardown: refusing merge: member status %s is not an authorized DONE terminal state\n' "$status" >&2; exit 1; }
  if ! git -C "$WORKTREE_PATH" diff --quiet || ! git -C "$WORKTREE_PATH" diff --cached --quiet; then fail 'refusing merge: worktree has tracked uncommitted files'; fi
  if has_nonfleet_untracked; then fail 'refusing merge: non-fleet untracked data exists'; fi
  return 0
}
render_merge_and_removal() {
  printf 'if ! git merge --no-ff %q; then\n' "$BRANCH"
  printf '%s\n' '  if git rev-parse -q --verify MERGE_HEAD >/dev/null 2>&1; then'
  printf '%s\n' '    if git merge --abort; then'
  printf '%s\n' "      printf 'fleet-teardown: merge conflict aborted; recovery state preserved\\n' >&2"
  printf '%s\n' '    else'
  printf '%s\n' "      printf 'fleet-teardown: merge failed and abort failed; manual recovery required\\n' >&2"
  printf '%s\n' '    fi' '  else'
  printf '%s\n' "    printf 'fleet-teardown: merge failed before a merge state was created; recovery state preserved\\n' >&2"
  printf '%s\n' '  fi' '  exit 1' 'fi'
  printf 'STATUS_BACKUP=$(mktemp %q) || { printf '\''fleet-teardown: could not preserve recovery status\n'\'' >&2; exit 2; }\n' "$FLEET_DIR/.${SLUG}.status.XXXXXX"
  printf 'cp %q "$STATUS_BACKUP" || { printf '\''fleet-teardown: could not preserve recovery status\n'\'' >&2; exit 2; }\n' "$STATUS_FILE"
  printf 'rm -f %q %q\n' "$WORKTREE_PATH/$COMPOSE_FILE" "$STATUS_FILE"
  printf 'if ! git worktree remove %q; then\n' "$WORKTREE_PATH"
  printf '  mkdir -p %q\n' "$(dirname "$STATUS_FILE")"
  printf '  if cp "$STATUS_BACKUP" %q; then\n' "$STATUS_FILE"
  printf '%s\n' '    rm -f "$STATUS_BACKUP"'
  printf '%s\n' "    printf 'fleet-teardown: worktree removal failed; recovery status was restored\\n' >&2"
  printf '%s\n' '    exit 2' '  fi'
  printf '%s\n' "  printf 'fleet-teardown: worktree removal failed; status restore failed; backup preserved at %s\\n' \"\$STATUS_BACKUP\" >&2"
  printf '%s\n' '  exit 2' 'fi'
  printf '%s\n' 'rm -f "$STATUS_BACKUP"'
  printf 'rm -f %q; rm %q\n' "$PANE_FILE" "$MEMBER_FILE"
  printf '%s\n' "printf 'fleet-teardown: merged and removed worktree for %s\\n' '$SLUG'"
}

if [[ ${DRY_RUN:-} != 1 ]]; then
  safe_dir_under "$REPO_ROOT" .planning/flow/fleet || fail 'unsafe central fleet state path'
  LOCK_DIR=$FLEET_DIR/.lock; mkdir "$LOCK_DIR" 2>/dev/null || fail 'fleet lifecycle is already locked'; trap release_lock EXIT
fi
validate_member
STATUS_FILE=$WORKTREE_PATH/.planning/flow/fleet-status.json
if [[ $MERGE == true ]]; then require_regular_nosymlink "$STATUS_FILE" || fail 'merge status is missing or unsafe'; fi
if [[ ${DRY_RUN:-} == 1 ]]; then
  if [[ $MERGE == true ]]; then
    render_merge_gates
    check_merge_authorization
  fi
  printf '(cd %q && docker compose -p %q --env-file .env.fleet -f %q down)\n' "$WORKTREE_PATH" "$PROJECT_NAME" "$COMPOSE_FILE"
  render_tmux_shutdown
  if [[ $MERGE == true ]]; then
    render_merge_and_removal
    exit 0
  fi
  printf 'rm -f %q; rm %q\n' "$PANE_FILE" "$MEMBER_FILE"
  printf '%s\n' "printf 'fleet-teardown: stopped %s; preserved branch and worktree\\n' '$SLUG'"
  exit 0
fi
[[ $MERGE == false ]] || check_merge_authorization
(cd "$WORKTREE_PATH" && docker compose -p "$PROJECT_NAME" --env-file .env.fleet -f "$COMPOSE_FILE" down)
shutdown_tmux
if [[ $MERGE == false ]]; then rm -f "$PANE_FILE"; rm "$MEMBER_FILE"; best_effort_audit STOPPED; printf 'fleet-teardown: stopped %s; preserved branch and worktree\n' "$SLUG"; exit 0; fi
if ! git merge --no-ff "$BRANCH"; then
  if git rev-parse -q --verify MERGE_HEAD >/dev/null 2>&1; then
    if git merge --abort; then printf 'fleet-teardown: merge conflict aborted; recovery state preserved\n' >&2
    else printf 'fleet-teardown: merge failed and abort failed; manual recovery required\n' >&2; fi
  else printf 'fleet-teardown: merge failed before a merge state was created; recovery state preserved\n' >&2; fi
  exit 1
fi
STATUS_BACKUP=$(mktemp "$FLEET_DIR/.${SLUG}.status.XXXXXX") || fail 'could not preserve recovery status'
cp "$STATUS_FILE" "$STATUS_BACKUP" || fail 'could not preserve recovery status'
rm -f "$WORKTREE_PATH/$COMPOSE_FILE" "$STATUS_FILE"
if ! git worktree remove "$WORKTREE_PATH"; then
  mkdir -p "$(dirname "$STATUS_FILE")"
  if cp "$STATUS_BACKUP" "$STATUS_FILE"; then
    rm -f "$STATUS_BACKUP"
    fail 'worktree removal failed; recovery status was restored'
  fi
  fail "worktree removal failed; status restore failed; backup preserved at $STATUS_BACKUP"
fi
rm -f "$STATUS_BACKUP" "$PANE_FILE"; rm "$MEMBER_FILE"; best_effort_audit MERGED; printf 'fleet-teardown: merged and removed worktree for %s\n' "$SLUG"
