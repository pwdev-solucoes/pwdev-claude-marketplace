#!/usr/bin/env bash
# Provision one explicitly acknowledged, isolated Flow fleet member.
set -Eeuo pipefail

usage() { printf 'Usage: %s <lowercase-slug>\n' "${0##*/}" >&2; exit 2; }
fail_preflight() { printf 'fleet-up: %s\n' "$*" >&2; exit 2; }

SLUG=${1:-}
[[ $# -eq 1 ]] || usage
[[ $SLUG =~ ^[a-z0-9][a-z0-9-]*$ ]] || fail_preflight "invalid slug: $SLUG"
REPO_ROOT=$(git rev-parse --show-toplevel 2>/dev/null) || fail_preflight 'run inside a Git repository'
cd "$REPO_ROOT"
REPO_PARENT=$(cd "$REPO_ROOT/.." && pwd -P)
REPO_NAME=$(basename "$REPO_ROOT")
CONFIG=$REPO_ROOT/.planning/flow/config.json
PHASE_DIR=$REPO_ROOT/.planning/flow/phases/$SLUG
FLEET_DIR=$REPO_ROOT/.planning/flow/fleet
MEMBER_FILE=$FLEET_DIR/$SLUG.json
PANE_FILE=$FLEET_DIR/$SLUG.pane.sh
BRANCH=flow-fleet/$SLUG
PROJECT_NAME=flow-fleet-$SLUG
WORKTREE_PATH=$REPO_PARENT/$REPO_NAME-fleet-$SLUG
TMUX_WINDOW=pwdev-flow-fleet:$SLUG
COMPOSE_FILE=docker-compose.flow-fleet.yml
SCRIPT_DIR=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd -P)
TEMPLATE=$SCRIPT_DIR/../templates/docker-compose.flow-fleet.yml
RUNTIME=${FLOW_FLEET_RUNTIME:-codex}
case "$RUNTIME" in codex|claude) ;; *) fail_preflight "unsupported fleet runtime: $RUNTIME";; esac

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
    if [[ -e $next ]]; then
      [[ -d $next ]] || { IFS=$old_ifs; return 1; }
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
safe_repo_dir() { safe_dir_under "$REPO_ROOT" "$1" "${2:-false}"; }
safe_worktree_dir() { safe_dir_under "$WORKTREE_PATH" "$1" "${2:-false}"; }
require_regular_nosymlink() { [[ -e $1 && -f $1 && ! -L $1 ]]; }
require_absent_destination() { [[ ! -e $1 && ! -L $1 ]]; }

contract_is_approved() {
  awk '/^[[:space:]]*(-[[:space:]]+)?Status:[[:space:]]*/ { fields++; normalized=$0; sub(/^[[:space:]]*(-[[:space:]]+)?/, "", normalized); if (normalized == "Status: APPROVED") approved++ } END { exit !(fields == 1 && approved == 1) }' "$1"
}
port_in_use() { (: >/dev/tcp/127.0.0.1/"$1") >/dev/null 2>&1; }

for binary in git jq docker tmux shasum python3; do command -v "$binary" >/dev/null 2>&1 || fail_preflight "required binary unavailable: $binary"; done
[[ "$RUNTIME" == codex ]] || command -v claude >/dev/null 2>&1 || fail_preflight 'required binary unavailable: claude'
BASE_BRANCH=$(git symbolic-ref --quiet --short HEAD 2>/dev/null) || fail_preflight 'fleet launch requires a named current branch'
[[ -n $BASE_BRANCH ]] || fail_preflight 'fleet launch requires a named current branch'
BASE_COMMIT=$(git rev-parse --verify HEAD 2>/dev/null) || fail_preflight 'unable to resolve base commit'
[[ $BASE_COMMIT =~ ^[0-9a-f]{40,64}$ ]] || fail_preflight 'invalid base commit'
INITIATING_ROOT=$REPO_ROOT
safe_repo_dir .planning/flow false || fail_preflight 'unsafe .planning/flow path'
safe_repo_dir ".planning/flow/phases/$SLUG" false || fail_preflight "unsafe phase path for $SLUG"
if [[ -e $FLEET_DIR || -L $FLEET_DIR ]]; then safe_repo_dir .planning/flow/fleet false || fail_preflight 'unsafe fleet state path'; fi
require_regular_nosymlink "$CONFIG" || fail_preflight "missing or unsafe fleet configuration: $CONFIG"
require_regular_nosymlink "$PHASE_DIR/spec.md" && require_regular_nosymlink "$PHASE_DIR/decisions.md" || fail_preflight "missing or unsafe approved contracts for $SLUG"
contract_is_approved "$PHASE_DIR/spec.md" || fail_preflight "spec must contain exactly one Status: APPROVED field"
contract_is_approved "$PHASE_DIR/decisions.md" || fail_preflight "decisions must contain exactly one Status: APPROVED field"
SPEC_SHA256=$(shasum -a 256 "$PHASE_DIR/spec.md" | awk '{print $1}') || fail_preflight 'could not hash approved spec'
DECISIONS_SHA256=$(shasum -a 256 "$PHASE_DIR/decisions.md" | awk '{print $1}') || fail_preflight 'could not hash approved decisions'
[[ $SPEC_SHA256 =~ ^[0-9a-f]{64}$ && $DECISIONS_SHA256 =~ ^[0-9a-f]{64}$ ]] || fail_preflight 'invalid approved contract hash'
require_regular_nosymlink "$TEMPLATE" || fail_preflight "missing compose template: $TEMPLATE"
git cat-file -e "HEAD:$COMPOSE_FILE" 2>/dev/null && fail_preflight "compose destination already exists: $COMPOSE_FILE"
git cat-file -e 'HEAD:.env.fleet' 2>/dev/null && fail_preflight 'generated fleet environment destination already exists'
GITIGNORE_MODE=$(git ls-tree HEAD -- .gitignore | awk 'NR == 1 { print $1 }')
[[ $GITIGNORE_MODE != 120000 ]] || fail_preflight '.gitignore must not be a symlink'
MAX_CONCURRENT=$(jq -er '.fleet.max_concurrent | select(type == "number" and . > 0 and floor == .)' "$CONFIG") || fail_preflight 'invalid fleet.max_concurrent'
PORT_BASE_APP=$(jq -er '.fleet.port_base_app | select(type == "number" and . > 0 and floor == .)' "$CONFIG") || fail_preflight 'invalid fleet.port_base_app'
PORT_BASE_DB=$(jq -er '.fleet.port_base_db | select(type == "number" and . > 0 and floor == .)' "$CONFIG") || fail_preflight 'invalid fleet.port_base_db'
PORT_STEP=$(jq -er '.fleet.port_step | select(type == "number" and . > 0 and floor == .)' "$CONFIG") || fail_preflight 'invalid fleet.port_step'
PERMISSION_MODE=$(jq -er '.fleet.permission_mode' "$CONFIG") || fail_preflight 'missing fleet.permission_mode'
jq -e '.fleet.auto_simplify | type == "boolean" and . == false' "$CONFIG" >/dev/null 2>&1 || fail_preflight 'fleet auto_simplify must be the JSON boolean false'
CONFIG_COMPOSE_FILE=$(jq -er '.fleet.compose_file | select(type == "string")' "$CONFIG") || fail_preflight 'missing fleet.compose_file'
[[ $PERMISSION_MODE == danger-full-access ]] || fail_preflight 'fleet permission_mode must be danger-full-access'
[[ $CONFIG_COMPOSE_FILE == "$COMPOSE_FILE" ]] || fail_preflight "fleet compose_file must be $COMPOSE_FILE"
AUDIT_ENABLED=false
[[ $(jq -r '.audit == true' "$CONFIG") == true ]] && AUDIT_ENABLED=true

best_effort_audit() {
  local action=$1 status=$2 detail
  [[ $AUDIT_ENABLED == true ]] || return 0
  detail=$(jq -nc --arg slug "$SLUG" --arg status "$status" '{slug:$slug,status:$status}') || {
    printf 'warning: %s audit record failed\n' "$action" >&2; return 0;
  }
  if ! python3 "$SCRIPT_DIR/flow_audit.py" --root "$REPO_ROOT" record \
    --action "$action" --skill flow-fleet --status "$status" \
    --target ".planning/flow/fleet/$SLUG.json" --detail "$detail" >/dev/null 2>&1; then
    printf 'warning: %s audit record failed\n' "$action" >&2
  fi
}

MEMBER_COUNT=0; INDEX=0; APP_PORT=0; DB_PORT=0
validate_allocation() {
  if [[ -e $FLEET_DIR || -L $FLEET_DIR ]]; then safe_repo_dir .planning/flow/fleet false || fail_preflight 'unsafe fleet state path'; fi
  [[ ! -e $MEMBER_FILE ]] || fail_preflight "fleet member already exists: $SLUG"
  [[ ! -e $PANE_FILE && ! -L $PANE_FILE ]] || fail_preflight "fleet pane already exists: $SLUG"
  [[ ! -e $WORKTREE_PATH ]] || fail_preflight "worktree path already exists: $WORKTREE_PATH"
  git show-ref --verify --quiet "refs/heads/$BRANCH" && fail_preflight "fleet branch already exists: $BRANCH"
  MEMBER_COUNT=0
  local member member_data member_index member_app member_db slot_used
  for member in "$FLEET_DIR"/*.json; do
    [[ -f $member ]] || continue
    member_data=$(jq -er 'if type == "object" and (.port_index | type == "number" and floor == . and . >= 0 and . <= 65535) and (.app_port | type == "number" and floor == . and . >= 1 and . <= 65535) and (.db_port | type == "number" and floor == . and . >= 1 and . <= 65535) and (.app_port != .db_port) then [.port_index, .app_port, .db_port] | @tsv else error("invalid fleet member") end' "$member" 2>/dev/null) || fail_preflight "malformed fleet member: ${member##*/}"
    IFS=$'\t' read -r member_index member_app member_db <<<"$member_data"
    MEMBER_COUNT=$((MEMBER_COUNT + 1))
  done
  (( MEMBER_COUNT < MAX_CONCURRENT )) || fail_preflight "fleet capacity reached ($MAX_CONCURRENT)"
  INDEX=0
  while :; do
    slot_used=false
    for member in "$FLEET_DIR"/*.json; do
      [[ -f $member ]] || continue
      member_index=$(jq -er '.port_index' "$member") || fail_preflight "malformed fleet member: ${member##*/}"
      [[ $member_index == "$INDEX" ]] && slot_used=true
    done
    [[ $slot_used == false ]] && break
    INDEX=$((INDEX + 1))
  done
  APP_PORT=$((PORT_BASE_APP + PORT_STEP * INDEX)); DB_PORT=$((PORT_BASE_DB + PORT_STEP * INDEX))
  (( APP_PORT >= 1 && APP_PORT <= 65535 && DB_PORT >= 1 && DB_PORT <= 65535 && APP_PORT != DB_PORT )) || fail_preflight 'allocated ports are invalid or overlapping'
  for member in "$FLEET_DIR"/*.json; do
    [[ -f $member ]] || continue
    member_data=$(jq -er '[.app_port, .db_port] | @tsv' "$member") || fail_preflight "malformed fleet member: ${member##*/}"
    IFS=$'\t' read -r member_app member_db <<<"$member_data"
    if [[ $APP_PORT == "$member_app" || $APP_PORT == "$member_db" || $DB_PORT == "$member_app" || $DB_PORT == "$member_db" ]]; then fail_preflight "allocated ports collide with fleet member: ${member##*/}"; fi
  done
}

WORKTREE_CREATED=false; DOCKER_ATTEMPTED=false; TMUX_ATTEMPTED=false; POST_WORKTREE=false; STATE_CREATED_AT=; PANE_TEMPORARY=; PANE_INCOMPLETE_OWNED=false; PENDING_RECOVERY_SIGNAL=; RECOVERY_SIGNALS_DEFERRED=false
write_state() {
  local state=$1 now temporary
  now=$(date -u +%Y-%m-%dT%H:%M:%SZ); safe_repo_dir .planning/flow/fleet true || return 1
  temporary=$(mktemp "$FLEET_DIR/.${SLUG}.json.XXXXXX") || return 1
  if ! jq -n --arg slug "$SLUG" --arg runtime "$RUNTIME" --arg branch "$BRANCH" --arg worktree "$WORKTREE_PATH" --arg project "$PROJECT_NAME" --arg window "$TMUX_WINDOW" --arg compose "$COMPOSE_FILE" --arg spec_sha256 "$SPEC_SHA256" --arg decisions_sha256 "$DECISIONS_SHA256" --arg initiating_root "$INITIATING_ROOT" --arg base_branch "$BASE_BRANCH" --arg base_commit "$BASE_COMMIT" --arg status "$state" --arg created_at "$STATE_CREATED_AT" --arg updated_at "$now" --argjson app_port "$APP_PORT" --argjson db_port "$DB_PORT" --argjson index "$INDEX" --argjson worktree_created "$WORKTREE_CREATED" --argjson docker_attempted "$DOCKER_ATTEMPTED" --argjson tmux_attempted "$TMUX_ATTEMPTED" '{slug:$slug,runtime:$runtime,branch:$branch,worktree_path:$worktree,app_port:$app_port,db_port:$db_port,port_index:$index,project_name:$project,tmux_window:$window,compose_file:$compose,spec_sha256:$spec_sha256,decisions_sha256:$decisions_sha256,initiating_root:$initiating_root,base_branch:$base_branch,base_commit:$base_commit,status:$status,created_at:$created_at,updated_at:$updated_at,worktree_created:$worktree_created,docker_attempted:$docker_attempted,tmux_attempted:$tmux_attempted}' >"$temporary"; then rm -f "$temporary"; return 1; fi
  mv "$temporary" "$MEMBER_FILE"
}
RECOVERING=false
recover() {
  local result=$1 reason=$2
  [[ $RECOVERING == false ]] || exit "$result"; RECOVERING=true; trap - ERR INT TERM HUP
  if [[ $PANE_INCOMPLETE_OWNED == true ]]; then
    if rm -f -- "$PANE_FILE"; then PANE_INCOMPLETE_OWNED=false
    else printf 'fleet-up: failed to clean owned incomplete pane: %s\n' "$PANE_FILE" >&2; fi
  fi
  if [[ -n $PANE_TEMPORARY ]]; then
    if rm -f -- "$PANE_TEMPORARY"; then PANE_TEMPORARY=
    else printf 'fleet-up: failed to clean owned pane temporary: %s\n' "$PANE_TEMPORARY" >&2; fi
  fi
  if [[ $POST_WORKTREE == true ]]; then
    if write_state NEEDS_HUMAN; then printf 'fleet-up: %s; recovery state recorded at %s\n' "$reason" "$MEMBER_FILE" >&2
    else printf 'fleet-up: %s; FAILED to record recovery state at %s\n' "$reason" "$MEMBER_FILE" >&2; fi
  fi
  exit "$result"
}
queue_recovery_signal() { [[ -n $PENDING_RECOVERY_SIGNAL ]] || PENDING_RECOVERY_SIGNAL=$1; }
dispatch_recovery_signal() {
  case $1 in
    HUP) recover 129 hangup ;;
    INT) recover 130 interrupt ;;
    TERM) recover 143 termination ;;
  esac
}
handle_recovery_signal() {
  local signal=$1
  if [[ $RECOVERY_SIGNALS_DEFERRED == true ]]; then
    queue_recovery_signal "$signal"
  elif [[ -n $PENDING_RECOVERY_SIGNAL ]]; then
    dispatch_recovery_signal "$PENDING_RECOVERY_SIGNAL"
  else
    dispatch_recovery_signal "$signal"
  fi
}
defer_recovery_signals() {
  PENDING_RECOVERY_SIGNAL=
  RECOVERY_SIGNALS_DEFERRED=true
}
restore_recovery_signals() {
  local pending
  pending=$PENDING_RECOVERY_SIGNAL
  [[ -z $pending ]] || dispatch_recovery_signal "$pending"
  RECOVERY_SIGNALS_DEFERRED=false
  pending=$PENDING_RECOVERY_SIGNAL
  [[ -z $pending ]] || dispatch_recovery_signal "$pending"
  PENDING_RECOVERY_SIGNAL=
}
trap 'recover $? command-failure' ERR
trap 'handle_recovery_signal HUP' HUP
trap 'handle_recovery_signal INT' INT
trap 'handle_recovery_signal TERM' TERM

render_plan() {
  local service_args dashboard_command pane_command pane_contents ignore_contents env_contents contract relative destination
  service_args=db; git cat-file -e HEAD:Dockerfile 2>/dev/null && service_args=full
  printf '# allocation: port_index=%s app_port=%s db_port=%s\n' "$INDEX" "$APP_PORT" "$DB_PORT"
  printf 'if (: >/dev/tcp/127.0.0.1/%q) >/dev/null 2>&1; then printf %q >&2; exit 2; fi\n' "$APP_PORT" "fleet-up: app port is already occupied: $APP_PORT\n"
  printf 'if (: >/dev/tcp/127.0.0.1/%q) >/dev/null 2>&1; then printf %q >&2; exit 2; fi\n' "$DB_PORT" "fleet-up: database port is already occupied: $DB_PORT\n"
  printf 'docker compose version >/dev/null 2>&1 || { printf %q >&2; exit 2; }\n' 'fleet-up: Docker Compose v2 is unavailable\n'
  printf 'git worktree add %q -b %q\n' "$WORKTREE_PATH" "$BRANCH"
  printf 'STATE_CREATED_AT=$(date -u +%%Y-%%m-%%dT%%H:%%M:%%SZ)\n'
  printf 'mkdir -p %q\n' "$WORKTREE_PATH/.planning/flow/phases/$SLUG"
  for contract in spec.md decisions.md; do
    relative=.planning/flow/phases/$SLUG/$contract
    destination=$WORKTREE_PATH/$relative
    printf 'if [[ -L %q || ( -e %q && ! -f %q ) ]]; then printf %q >&2; exit 2; fi\n' "$destination" "$destination" "$destination" "fleet-up: unsafe fleet contract destination: $contract\n"
    printf 'if [[ ! -e %q ]] || ! cmp -s %q %q; then contract_temporary=$(mktemp %q) || exit 2; cp %q "$contract_temporary" || exit 2; if [[ -L %q || ( -e %q && ! -f %q ) ]]; then printf %q >&2; exit 2; fi; mv "$contract_temporary" %q; fi\n' "$destination" "$PHASE_DIR/$contract" "$destination" "$WORKTREE_PATH/.planning/flow/phases/$SLUG/.${contract}.XXXXXX" "$PHASE_DIR/$contract" "$destination" "$destination" "$destination" "fleet-up: contract destination changed: $contract\n" "$destination"
  done
  printf 'if [[ -n $(git -C %q status --porcelain -- %q) ]]; then git -C %q add %q %q; git -C %q commit -m %q; fi\n' \
    "$WORKTREE_PATH" ".planning/flow/phases/$SLUG" "$WORKTREE_PATH" ".planning/flow/phases/$SLUG/spec.md" ".planning/flow/phases/$SLUG/decisions.md" "$WORKTREE_PATH" "chore(flow-fleet): adopt approved $SLUG contracts"
  ignore_contents=$'\n# Flow fleet runtime files\n.env.fleet\n.planning/flow/fleet-status.json\n'
  printf -v env_contents 'FLOW_ENV=development\nAPP_PORT=%s\nDB_PORT=%s\nPOSTGRES_DB=flow_fleet\nPOSTGRES_USER=flow_fleet\nPOSTGRES_PASSWORD=development-only\n' "$APP_PORT" "$DB_PORT"
  printf 'if [[ -L %q || ( -e %q && ! -f %q ) ]]; then printf %q >&2; exit 2; fi; ignore_temporary=$(mktemp %q) || exit 2; if [[ -e %q ]]; then cp %q "$ignore_temporary" || exit 2; fi; printf %q >> "$ignore_temporary" || exit 2; if [[ -L %q || ( -e %q && ! -f %q ) ]]; then printf %q >&2; exit 2; fi; mv "$ignore_temporary" %q; git -C %q add .gitignore; git -C %q commit -m %q\n' "$WORKTREE_PATH/.gitignore" "$WORKTREE_PATH/.gitignore" "$WORKTREE_PATH/.gitignore" 'fleet-up: .gitignore must be absent or a regular non-symlink file\n' "$WORKTREE_PATH/.gitignore.XXXXXX" "$WORKTREE_PATH/.gitignore" "$WORKTREE_PATH/.gitignore" "$ignore_contents" "$WORKTREE_PATH/.gitignore" "$WORKTREE_PATH/.gitignore" "$WORKTREE_PATH/.gitignore" 'fleet-up: .gitignore changed before publication\n' "$WORKTREE_PATH/.gitignore" "$WORKTREE_PATH" "$WORKTREE_PATH" "chore(flow-fleet): ignore local $SLUG runtime files"
  printf 'if [[ -e %q || -L %q ]]; then printf %q >&2; exit 2; fi; compose_temporary=$(mktemp %q) || exit 2; cp %q "$compose_temporary" || exit 2; if [[ -e %q || -L %q ]]; then printf %q >&2; exit 2; fi; mv "$compose_temporary" %q\n' "$WORKTREE_PATH/$COMPOSE_FILE" "$WORKTREE_PATH/$COMPOSE_FILE" 'fleet-up: compose destination already exists\n' "$WORKTREE_PATH/.${COMPOSE_FILE}.XXXXXX" "$TEMPLATE" "$WORKTREE_PATH/$COMPOSE_FILE" "$WORKTREE_PATH/$COMPOSE_FILE" 'fleet-up: compose destination changed before publication\n' "$WORKTREE_PATH/$COMPOSE_FILE"
  printf 'if [[ -e %q || -L %q ]]; then printf %q >&2; exit 2; fi; env_temporary=$(mktemp %q) || exit 2; (umask 077; printf %q > "$env_temporary"); chmod 600 "$env_temporary"; if [[ -e %q || -L %q ]]; then printf %q >&2; exit 2; fi; mv "$env_temporary" %q\n' "$WORKTREE_PATH/.env.fleet" "$WORKTREE_PATH/.env.fleet" 'fleet-up: generated fleet environment destination already exists\n' "$WORKTREE_PATH/.env.fleet.XXXXXX" "$env_contents" "$WORKTREE_PATH/.env.fleet" "$WORKTREE_PATH/.env.fleet" 'fleet-up: generated fleet environment destination changed before publication\n' "$WORKTREE_PATH/.env.fleet"
  if [[ $service_args == db ]]; then printf '(cd %q && docker compose -p %q --env-file .env.fleet -f %q up -d db)\n' "$WORKTREE_PATH" "$PROJECT_NAME" "$COMPOSE_FILE"; else printf '(cd %q && docker compose -p %q --env-file .env.fleet -f %q up -d)\n' "$WORKTREE_PATH" "$PROJECT_NAME" "$COMPOSE_FILE"; fi
  printf -v dashboard_command 'bash %q' "$SCRIPT_DIR/fleet-dashboard.sh"; printf -v pane_command 'bash %q' "$PANE_FILE"; local runtime_runner=$SCRIPT_DIR/fleet-run.sh; [[ "$RUNTIME" == claude ]] && runtime_runner=$SCRIPT_DIR/claude-fleet-run.sh; printf -v pane_contents '#!/usr/bin/env bash\nexec %q %q %q %q\n' "$runtime_runner" "$SLUG" "$WORKTREE_PATH" danger-full-access
  printf 'pane_write_recovery_state() { pane_now=$(date -u +%%Y-%%m-%%dT%%H:%%M:%%SZ); mkdir -p %q; pane_state_temporary=$(mktemp %q) || return 1; if ! jq -n --arg slug %q --arg branch %q --arg worktree %q --arg project %q --arg window %q --arg compose %q --arg spec_sha256 %q --arg decisions_sha256 %q --arg initiating_root %q --arg base_branch %q --arg base_commit %q --arg status NEEDS_HUMAN --arg created_at "$STATE_CREATED_AT" --arg updated_at "$pane_now" --argjson app_port %q --argjson db_port %q --argjson index %q --argjson worktree_created true --argjson docker_attempted true --argjson tmux_attempted false %q > "$pane_state_temporary"; then rm -f "$pane_state_temporary"; return 1; fi; mv "$pane_state_temporary" %q; }\n' "$FLEET_DIR" "$FLEET_DIR/.${SLUG}.json.XXXXXX" "$SLUG" "$BRANCH" "$WORKTREE_PATH" "$PROJECT_NAME" "$TMUX_WINDOW" "$COMPOSE_FILE" "$SPEC_SHA256" "$DECISIONS_SHA256" "$INITIATING_ROOT" "$BASE_BRANCH" "$BASE_COMMIT" "$APP_PORT" "$DB_PORT" "$INDEX" '{slug:$slug,branch:$branch,worktree_path:$worktree,app_port:$app_port,db_port:$db_port,port_index:$index,project_name:$project,tmux_window:$window,compose_file:$compose,spec_sha256:$spec_sha256,decisions_sha256:$decisions_sha256,initiating_root:$initiating_root,base_branch:$base_branch,base_commit:$base_commit,status:$status,created_at:$created_at,updated_at:$updated_at,worktree_created:$worktree_created,docker_attempted:$docker_attempted,tmux_attempted:$tmux_attempted}' "$MEMBER_FILE"
  printf 'pane_pending_signal=; pane_signals_deferred=false; pane_incomplete_owned=false; pane_recover_signal() { local result=$1 reason=$2; trap - HUP INT TERM; if [[ "$pane_incomplete_owned" == true ]]; then rm -f -- %q; pane_incomplete_owned=false; fi; if [[ -n ${pane_temporary:-} ]]; then rm -f -- "$pane_temporary"; pane_temporary=; fi; if pane_write_recovery_state; then printf %q "$reason" %q >&2; else printf %q "$reason" %q >&2; fi; exit "$result"; }; pane_queue_signal() { [[ -n "$pane_pending_signal" ]] || pane_pending_signal=$1; }; pane_dispatch_signal() { case $1 in HUP) pane_recover_signal 129 hangup ;; INT) pane_recover_signal 130 interrupt ;; TERM) pane_recover_signal 143 termination ;; esac; }; pane_handle_signal() { local signal=$1; if [[ "$pane_signals_deferred" == true ]]; then pane_queue_signal "$signal"; elif [[ -n "$pane_pending_signal" ]]; then pane_dispatch_signal "$pane_pending_signal"; else pane_dispatch_signal "$signal"; fi; }; pane_defer_signals() { pane_pending_signal=; pane_signals_deferred=true; }; pane_restore_signals() { local pending; pending=$pane_pending_signal; [[ -z "$pending" ]] || pane_dispatch_signal "$pending"; pane_signals_deferred=false; pending=$pane_pending_signal; [[ -z "$pending" ]] || pane_dispatch_signal "$pending"; pane_pending_signal=; }; trap '\''pane_handle_signal HUP'\'' HUP; trap '\''pane_handle_signal INT'\'' INT; trap '\''pane_handle_signal TERM'\'' TERM\n' "$PANE_FILE" 'fleet-up: %s; recovery state recorded at %s\n' "$MEMBER_FILE" 'fleet-up: %s; FAILED to record recovery state at %s\n' "$MEMBER_FILE"
  printf 'mkdir -p %q; pane_temporary=$(mktemp %q) || exit 1; if ! printf %q > "$pane_temporary"; then rm -f "$pane_temporary"; exit 1; fi; chmod 700 "$pane_temporary" || { rm -f "$pane_temporary"; exit 1; }; pane_defer_signals; if (set -o noclobber; : > %q) 2>/dev/null; then pane_incomplete_owned=true; pane_restore_signals; else pane_restore_signals; rm -f "$pane_temporary"; exit 1; fi; if ! cat "$pane_temporary" > %q; then pane_recover_signal 1; fi; pane_defer_signals; pane_validation_failed=false; if ! chmod 700 %q || ! cmp -s "$pane_temporary" %q; then pane_validation_failed=true; else pane_incomplete_owned=false; fi; pane_restore_signals; if [[ "$pane_validation_failed" == true ]]; then pane_recover_signal 1; fi; rm "$pane_temporary" || exit 1\n' "$FLEET_DIR" "$FLEET_DIR/.${SLUG}.pane.sh.XXXXXX" "$pane_contents" "$PANE_FILE" "$PANE_FILE" "$PANE_FILE" "$PANE_FILE"
  printf 'if ! tmux has-session -t pwdev-flow-fleet 2>/dev/null; then tmux new-session -d -s pwdev-flow-fleet -n dashboard %q; fi\n' "$dashboard_command"
  printf 'NOW=$(date -u +%%Y-%%m-%%dT%%H:%%M:%%SZ); mkdir -p %q; temporary=$(mktemp %q) || exit 1; if ! jq -n --arg slug %q --arg branch %q --arg worktree %q --arg project %q --arg window %q --arg compose %q --arg spec_sha256 %q --arg decisions_sha256 %q --arg initiating_root %q --arg base_branch %q --arg base_commit %q --arg status ACTIVE --arg created_at "$STATE_CREATED_AT" --arg updated_at "$NOW" --argjson app_port %q --argjson db_port %q --argjson index %q --argjson worktree_created true --argjson docker_attempted true --argjson tmux_attempted true %q > "$temporary"; then rm -f "$temporary"; exit 1; fi; mv "$temporary" %q\n' "$FLEET_DIR" "$FLEET_DIR/.${SLUG}.json.XXXXXX" "$SLUG" "$BRANCH" "$WORKTREE_PATH" "$PROJECT_NAME" "$TMUX_WINDOW" "$COMPOSE_FILE" "$SPEC_SHA256" "$DECISIONS_SHA256" "$INITIATING_ROOT" "$BASE_BRANCH" "$BASE_COMMIT" "$APP_PORT" "$DB_PORT" "$INDEX" '{slug:$slug,branch:$branch,worktree_path:$worktree,app_port:$app_port,db_port:$db_port,port_index:$index,project_name:$project,tmux_window:$window,compose_file:$compose,spec_sha256:$spec_sha256,decisions_sha256:$decisions_sha256,initiating_root:$initiating_root,base_branch:$base_branch,base_commit:$base_commit,status:$status,created_at:$created_at,updated_at:$updated_at,worktree_created:$worktree_created,docker_attempted:$docker_attempted,tmux_attempted:$tmux_attempted}' "$MEMBER_FILE"
  printf 'tmux new-window -t pwdev-flow-fleet -n %q %q\n' "$SLUG" "$pane_command"
}

if [[ ${DRY_RUN:-} == 1 ]]; then validate_allocation; render_plan; exit 0; fi
safe_repo_dir .planning/flow/fleet true || fail_preflight 'unsafe fleet state path'; LOCK_DIR=$FLEET_DIR/.lock; mkdir "$LOCK_DIR" 2>/dev/null || fail_preflight 'fleet allocation is already locked'
release_lock() { rmdir "$LOCK_DIR" 2>/dev/null || true; }; trap release_lock EXIT
validate_allocation
port_in_use "$APP_PORT" && fail_preflight "app port is already occupied: $APP_PORT"; port_in_use "$DB_PORT" && fail_preflight "database port is already occupied: $DB_PORT"
docker compose version >/dev/null 2>&1 || fail_preflight 'Docker Compose v2 is unavailable'
git worktree add "$WORKTREE_PATH" -b "$BRANCH"; WORKTREE_CREATED=true; POST_WORKTREE=true; STATE_CREATED_AT=$(date -u +%Y-%m-%dT%H:%M:%SZ)
safe_worktree_dir ".planning/flow/phases/$SLUG" true || recover 2 'unsafe fleet contract path'
for contract in spec.md decisions.md; do
  relative=.planning/flow/phases/$SLUG/$contract
  destination=$WORKTREE_PATH/$relative
  [[ ! -L $destination && ( ! -e $destination || -f $destination ) ]] || recover 2 "unsafe fleet contract destination: $contract"
  if [[ ! -e $destination ]] || ! cmp -s "$PHASE_DIR/$contract" "$destination"; then
    contract_temporary=$(mktemp "$WORKTREE_PATH/.planning/flow/phases/$SLUG/.${contract}.XXXXXX") || recover 2 "could not reserve contract publication: $contract"
    cp "$PHASE_DIR/$contract" "$contract_temporary" || recover 2 "could not copy approved contract: $contract"
    [[ ! -L $destination && ( ! -e $destination || -f $destination ) ]] || recover 2 "contract destination changed: $contract"
    mv "$contract_temporary" "$destination"
  fi
done
if [[ -n $(git -C "$WORKTREE_PATH" status --porcelain -- ".planning/flow/phases/$SLUG") ]]; then git -C "$WORKTREE_PATH" add ".planning/flow/phases/$SLUG/spec.md" ".planning/flow/phases/$SLUG/decisions.md"; git -C "$WORKTREE_PATH" commit -m "chore(flow-fleet): adopt approved $SLUG contracts"; fi
[[ ! -L $WORKTREE_PATH/.gitignore && ( ! -e $WORKTREE_PATH/.gitignore || -f $WORKTREE_PATH/.gitignore ) ]] || recover 2 '.gitignore must be absent or a regular non-symlink file'
IGNORE_TEMP=$(mktemp "$WORKTREE_PATH/.gitignore.XXXXXX") || recover 2 'could not reserve .gitignore publication'
if [[ -e $WORKTREE_PATH/.gitignore ]]; then cp "$WORKTREE_PATH/.gitignore" "$IGNORE_TEMP" || recover 2 'could not copy .gitignore'; fi
printf '\n# Flow fleet runtime files\n.env.fleet\n.planning/flow/fleet-status.json\n' >>"$IGNORE_TEMP" || recover 2 'could not update .gitignore'
[[ ! -L $WORKTREE_PATH/.gitignore && ( ! -e $WORKTREE_PATH/.gitignore || -f $WORKTREE_PATH/.gitignore ) ]] || recover 2 '.gitignore changed before publication'
mv "$IGNORE_TEMP" "$WORKTREE_PATH/.gitignore"; git -C "$WORKTREE_PATH" add .gitignore; git -C "$WORKTREE_PATH" commit -m "chore(flow-fleet): ignore local $SLUG runtime files"
require_absent_destination "$WORKTREE_PATH/$COMPOSE_FILE" || recover 2 'compose destination already exists'
COMPOSE_TEMP=$(mktemp "$WORKTREE_PATH/.${COMPOSE_FILE}.XXXXXX") || recover 2 'could not reserve compose publication'
cp "$TEMPLATE" "$COMPOSE_TEMP" || recover 2 'could not copy compose template'
require_absent_destination "$WORKTREE_PATH/$COMPOSE_FILE" || recover 2 'compose destination changed before publication'
mv "$COMPOSE_TEMP" "$WORKTREE_PATH/$COMPOSE_FILE"
require_absent_destination "$WORKTREE_PATH/.env.fleet" || recover 2 'generated fleet environment destination already exists'
ENV_TEMP=$(mktemp "$WORKTREE_PATH/.env.fleet.XXXXXX") || recover 2 'could not reserve fleet environment publication'
(umask 077; printf 'FLOW_ENV=development\nAPP_PORT=%s\nDB_PORT=%s\nPOSTGRES_DB=flow_fleet\nPOSTGRES_USER=flow_fleet\nPOSTGRES_PASSWORD=development-only\n' "$APP_PORT" "$DB_PORT" >"$ENV_TEMP"); chmod 600 "$ENV_TEMP"
require_absent_destination "$WORKTREE_PATH/.env.fleet" || recover 2 'generated fleet environment destination changed before publication'
mv "$ENV_TEMP" "$WORKTREE_PATH/.env.fleet"
DOCKER_ATTEMPTED=true
if [[ -f $WORKTREE_PATH/Dockerfile ]]; then (cd "$WORKTREE_PATH" && docker compose -p "$PROJECT_NAME" --env-file .env.fleet -f "$COMPOSE_FILE" up -d); else (cd "$WORKTREE_PATH" && docker compose -p "$PROJECT_NAME" --env-file .env.fleet -f "$COMPOSE_FILE" up -d db); fi
safe_repo_dir .planning/flow/fleet false || recover 2 'unsafe fleet state path'; PANE_TEMPORARY=$(mktemp "$FLEET_DIR/.${SLUG}.pane.sh.XXXXXX") || recover 2 'could not reserve fleet pane'; RUNTIME_RUNNER=$SCRIPT_DIR/fleet-run.sh; [[ "$RUNTIME" == claude ]] && RUNTIME_RUNNER=$SCRIPT_DIR/claude-fleet-run.sh; if ! printf '#!/usr/bin/env bash\nexec %q %q %q %q\n' "$RUNTIME_RUNNER" "$SLUG" "$WORKTREE_PATH" danger-full-access >"$PANE_TEMPORARY"; then recover 2 'could not write fleet pane'; fi; chmod 700 "$PANE_TEMPORARY" || recover 2 'could not secure fleet pane'
defer_recovery_signals
if (set -o noclobber; : > "$PANE_FILE") 2>/dev/null; then PANE_INCOMPLETE_OWNED=true; restore_recovery_signals; else restore_recovery_signals; recover 2 'fleet pane publication collision'; fi
if ! cat "$PANE_TEMPORARY" >"$PANE_FILE"; then recover 2 'could not populate fleet pane'; fi
defer_recovery_signals
PANE_VALIDATION_FAILED=false
if ! chmod 700 "$PANE_FILE" || ! cmp -s "$PANE_TEMPORARY" "$PANE_FILE"; then PANE_VALIDATION_FAILED=true; else PANE_INCOMPLETE_OWNED=false; fi
restore_recovery_signals
if [[ $PANE_VALIDATION_FAILED == true ]]; then recover 2 'could not validate fleet pane'; fi
if ! rm "$PANE_TEMPORARY"; then recover 2 'could not release fleet pane temporary'; fi; PANE_TEMPORARY=
TMUX_ATTEMPTED=true; printf -v dashboard_command 'bash %q' "$SCRIPT_DIR/fleet-dashboard.sh"; if ! tmux has-session -t pwdev-flow-fleet 2>/dev/null; then tmux new-session -d -s pwdev-flow-fleet -n dashboard "$dashboard_command"; fi
printf -v pane_command 'bash %q' "$PANE_FILE"; write_state ACTIVE; tmux new-window -t pwdev-flow-fleet -n "$SLUG" "$pane_command"
best_effort_audit fleet_launched ACTIVE
printf 'fleet-up: provisioned %s at %s\n' "$SLUG" "$WORKTREE_PATH"
