#!/usr/bin/env bash
# Provision one fleet member: worktree, ports, Docker stack, cmux workspace, and the central
# member record that binds all of it to an approved, hashed contract.
#
# Never invoked directly. The runtime is pinned by <runtime>-fleet-up.sh before this runs,
# because a privileged vector chosen by default is a privileged vector chosen by accident.
set -Eeuo pipefail

SCRIPT_DIR=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd -P)
# shellcheck source=fleet-common.sh
source "$SCRIPT_DIR/fleet-common.sh"
# shellcheck source=cmux-common.sh
source "$SCRIPT_DIR/cmux-common.sh"

fail_preflight() { printf 'fleet-up: %s\n' "$*" >&2; exit 2; }

[[ $# -eq 1 ]] || fail_preflight 'usage: <runtime>-fleet-up.sh <slug>'
SLUG=$1
[[ $SLUG =~ ^[a-z0-9][a-z0-9-]*$ && $SLUG == *[a-z]* && $SLUG != dashboard ]] \
  || fail_preflight "invalid slug: $SLUG"

RUNTIME=${POWER_FLEET_RUNTIME:-}
[[ -n $RUNTIME ]] || fail_preflight 'no runtime pinned; launch through <runtime>-fleet-up.sh'
power_require_runtime "$RUNTIME" || exit 2

command -v jq >/dev/null 2>&1 || fail_preflight 'jq is required'
command -v git >/dev/null 2>&1 || fail_preflight 'git is required'

REPO_ROOT=$(git rev-parse --show-toplevel 2>/dev/null) || fail_preflight 'not inside a Git repository'
REPO_ROOT=$(cd "$REPO_ROOT" && pwd -P)
cd "$REPO_ROOT"

BRANCH_CURRENT=$(git rev-parse --abbrev-ref HEAD 2>/dev/null) || fail_preflight 'cannot read current branch'
[[ $BRANCH_CURRENT != HEAD ]] || fail_preflight 'detached HEAD; check out a named branch first'
BASE_COMMIT=$(git rev-parse HEAD)

REPO_PARENT=$(cd "$REPO_ROOT/.." && pwd -P)
REPO_NAME=$(basename "$REPO_ROOT")
BRANCH=power-fleet/$SLUG
PROJECT_NAME=power-fleet-$SLUG
WORKTREE_PATH=$REPO_PARENT/$REPO_NAME-fleet-$SLUG
FLEET_DIR=$REPO_ROOT/.planning/power/fleet
MEMBER_FILE=$FLEET_DIR/$SLUG.json
PANE_FILE=$FLEET_DIR/$SLUG.pane.sh
FEATURE_REL=.planning/power/features/$SLUG
FEATURE_DIR=$REPO_ROOT/$FEATURE_REL
CONFIG=$REPO_ROOT/.planning/power/config.json
COMPOSE_FILE=docker-compose.power-fleet.yml
# Named so that the secret guards recognise it: their pattern anchors on a delimiter before
# ".env", so a name like ".fleet.env" would slip past them.
ENV_FILE=.env.fleet
TEMPLATE=$SCRIPT_DIR/../templates/$COMPOSE_FILE

sha256_of() {
  if command -v shasum >/dev/null 2>&1; then shasum -a 256 "$1" | awk '{print $1}'
  elif command -v sha256sum >/dev/null 2>&1; then sha256sum "$1" | awk '{print $1}'
  else openssl dgst -sha256 "$1" | awk '{print $NF}'; fi
}

# A state path that is a symlink is a state path someone else controls.
require_safe_dir() {
  local p=$1
  [[ ! -L $p ]] || return 1
  [[ ! -e $p || -d $p ]] || return 1
  return 0
}

require_absent() { [[ ! -e $1 && ! -L $1 ]]; }

port_in_use() { (: >/dev/tcp/127.0.0.1/"$1") >/dev/null 2>&1; }

# ---- preflight ---------------------------------------------------------------------------

[[ -f $CONFIG ]] || fail_preflight 'no .planning/power/config.json; run init first'
jq -e 'type == "object"' "$CONFIG" >/dev/null 2>&1 || fail_preflight 'config root is not an object'

SPEC=$FEATURE_DIR/spec.md
PLAN=$FEATURE_DIR/plan.md
[[ -f $SPEC ]] || fail_preflight "no spec at $FEATURE_REL/spec.md"
[[ -f $PLAN ]] || fail_preflight "no plan at $FEATURE_REL/plan.md"

# Exactly one, not at least one: a second approval line inside an example block makes the
# approval ambiguous, and ambiguity here means launching unapproved work.
approved_count=$(grep -c '^Status: APPROVED[[:space:]]*$' "$SPEC" || true)
[[ $approved_count -eq 1 ]] \
  || fail_preflight "spec must carry exactly one 'Status: APPROVED' field (found $approved_count)"

require_safe_dir "$FLEET_DIR" || fail_preflight 'unsafe fleet state path'
mkdir -p "$FLEET_DIR"
require_absent "$MEMBER_FILE" || fail_preflight "fleet member already exists: $SLUG"
require_absent "$WORKTREE_PATH" || fail_preflight "worktree destination already exists: $WORKTREE_PATH"
! git show-ref --verify --quiet "refs/heads/$BRANCH" || fail_preflight "branch already exists: $BRANCH"

# Refuse if the generated runtime files are already tracked here.
! git cat-file -e "HEAD:$COMPOSE_FILE" 2>/dev/null || fail_preflight "compose destination already tracked: $COMPOSE_FILE"
! git cat-file -e "HEAD:$ENV_FILE" 2>/dev/null || fail_preflight "generated fleet environment already tracked: $ENV_FILE"
[[ -f $TEMPLATE ]] || fail_preflight "missing packaged compose template: $TEMPLATE"

power_cmux_require || fail_preflight 'cmux is required for a fleet'

# Fleet configuration, defaults-first so every existing known or unknown field wins.
FLEET_DEFAULTS='{"port_base_app":3000,"port_base_db":5432,"port_step":10,"permission_mode":"danger-full-access","auto_simplify":false,"compose_file":"docker-compose.power-fleet.yml"}'
jq -e '(.fleet // {}) | type == "object"' "$CONFIG" >/dev/null 2>&1 || fail_preflight 'config .fleet is not an object'
FLEET_CFG=$(jq -c --argjson d "$FLEET_DEFAULTS" '$d * (.fleet // {})' "$CONFIG") \
  || fail_preflight 'cannot merge fleet configuration'

PERMISSION_MODE=$(jq -er '.permission_mode' <<<"$FLEET_CFG") || fail_preflight 'invalid fleet.permission_mode'
[[ $PERMISSION_MODE == danger-full-access ]] \
  || fail_preflight "fleet.permission_mode must be danger-full-access, found: $PERMISSION_MODE"
jq -e '.auto_simplify == false' <<<"$FLEET_CFG" >/dev/null \
  || fail_preflight 'fleet.auto_simplify must be the JSON boolean false'
CFG_COMPOSE=$(jq -er '.compose_file' <<<"$FLEET_CFG") || fail_preflight 'invalid fleet.compose_file'
[[ $CFG_COMPOSE == "$COMPOSE_FILE" ]] || fail_preflight "fleet.compose_file must be $COMPOSE_FILE"

PORT_BASE_APP=$(jq -er '.port_base_app | select(type == "number" and . > 0 and floor == .)' <<<"$FLEET_CFG") || fail_preflight 'invalid fleet.port_base_app'
PORT_BASE_DB=$(jq -er '.port_base_db | select(type == "number" and . > 0 and floor == .)' <<<"$FLEET_CFG") || fail_preflight 'invalid fleet.port_base_db'
PORT_STEP=$(jq -er '.port_step | select(type == "number" and . > 0 and floor == .)' <<<"$FLEET_CFG") || fail_preflight 'invalid fleet.port_step'

# ---- recovery ----------------------------------------------------------------------------

WORKTREE_CREATED=false
STACK_UP=false
CMUX_WORKSPACE_ID=
LOCK_HELD=false
LOCK_DIR=$FLEET_DIR/.lock

recover() {
  local code=$1 message=$2
  set +e
  printf 'fleet-up: %s\n' "$message" >&2
  if [[ -n $CMUX_WORKSPACE_ID ]]; then
    power_cmux_close_workspace "$CMUX_WORKSPACE_ID"
  fi
  if [[ $STACK_UP == true ]]; then
    (cd "$WORKTREE_PATH" && docker compose -p "$PROJECT_NAME" --env-file "$ENV_FILE" -f "$COMPOSE_FILE" down) >/dev/null 2>&1
  fi
  if [[ $WORKTREE_CREATED == true ]]; then
    git worktree remove --force "$WORKTREE_PATH" >/dev/null 2>&1
    git worktree prune >/dev/null 2>&1
    git branch -D "$BRANCH" >/dev/null 2>&1
  fi
  rm -f "$MEMBER_FILE" "$PANE_FILE"
  if [[ $LOCK_HELD == true ]]; then rmdir "$LOCK_DIR" >/dev/null 2>&1; fi
  exit "$code"
}

release_lock() {
  if [[ $LOCK_HELD == true ]]; then
    rmdir "$LOCK_DIR" >/dev/null 2>&1 && LOCK_HELD=false
  fi
}

# ---- allocation lock ---------------------------------------------------------------------
# mkdir is atomic on POSIX and needs no flock, which macOS does not ship.

mkdir "$LOCK_DIR" 2>/dev/null || fail_preflight 'fleet allocation is already locked'
LOCK_HELD=true
trap 'recover 1 "interrupted during provisioning"' HUP INT TERM

# First free slot, not an incrementing counter: teardown must release a slot for reuse.
INDEX=0
while :; do
  slot_used=false
  shopt -s nullglob
  for member in "$FLEET_DIR"/*.json; do
    member_index=$(jq -er '.port_index' "$member" 2>/dev/null) \
      || recover 2 "malformed fleet member: ${member##*/}"
    [[ $member_index == "$INDEX" ]] && { slot_used=true; break; }
  done
  shopt -u nullglob
  [[ $slot_used == false ]] && break
  INDEX=$((INDEX + 1))
  [[ $INDEX -lt 64 ]] || recover 2 'no free fleet port slot below 64'
done

APP_PORT=$((PORT_BASE_APP + PORT_STEP * INDEX))
DB_PORT=$((PORT_BASE_DB + PORT_STEP * INDEX))

(( APP_PORT >= 1 && APP_PORT <= 65535 && DB_PORT >= 1 && DB_PORT <= 65535 && APP_PORT != DB_PORT )) \
  || recover 2 'allocated ports are invalid or overlapping'

shopt -s nullglob
for member in "$FLEET_DIR"/*.json; do
  member_app=$(jq -er '.app_port' "$member" 2>/dev/null) || recover 2 "malformed fleet member: ${member##*/}"
  member_db=$(jq -er '.db_port' "$member" 2>/dev/null) || recover 2 "malformed fleet member: ${member##*/}"
  if [[ $APP_PORT == "$member_app" || $APP_PORT == "$member_db" || $DB_PORT == "$member_app" || $DB_PORT == "$member_db" ]]; then
    recover 2 "allocated ports collide with member ${member##*/}"
  fi
done
shopt -u nullglob

port_in_use "$APP_PORT" && recover 2 "app port is already occupied: $APP_PORT"
port_in_use "$DB_PORT" && recover 2 "database port is already occupied: $DB_PORT"

# ---- contracts ---------------------------------------------------------------------------
# Hash the exact approved working-tree bytes, not HEAD bytes: an approved spec is frequently
# not committed yet, and hashing HEAD would bind the member to a different document.

SPEC_SHA=$(sha256_of "$SPEC") || recover 2 'cannot hash spec'
PLAN_SHA=$(sha256_of "$PLAN") || recover 2 'cannot hash plan'
[[ $SPEC_SHA =~ ^[0-9a-f]{64}$ ]] || recover 2 'spec hash is malformed'
[[ $PLAN_SHA =~ ^[0-9a-f]{64}$ ]] || recover 2 'plan hash is malformed'

# ---- worktree ----------------------------------------------------------------------------

git worktree add "$WORKTREE_PATH" -b "$BRANCH" >/dev/null 2>&1 \
  || recover 2 "cannot create worktree at $WORKTREE_PATH"
WORKTREE_CREATED=true

# Adopt the approved contracts inside the worktree, byte for byte. Never stage or commit the
# initiating working tree.
mkdir -p "$WORKTREE_PATH/$FEATURE_REL"
cp "$SPEC" "$WORKTREE_PATH/$FEATURE_REL/spec.md" || recover 2 'cannot adopt spec'
cp "$PLAN" "$WORKTREE_PATH/$FEATURE_REL/plan.md" || recover 2 'cannot adopt plan'
cmp -s "$SPEC" "$WORKTREE_PATH/$FEATURE_REL/spec.md" || recover 2 'adopted spec differs from the approved bytes'
cmp -s "$PLAN" "$WORKTREE_PATH/$FEATURE_REL/plan.md" || recover 2 'adopted plan differs from the approved bytes'

# Runtime files that must never reach the fleet branch: fleet-run.sh stages every stage with
# `git add -A`, and teardown --merge lands that history on the human's base branch.
{
  printf '\n# Power fleet runtime files\n'
  printf '%s\n' "$ENV_FILE"
  printf '%s\n' "$COMPOSE_FILE"
  printf '.planning/power/fleet-status.json\n'
  printf '.planning/power/fleet-logs/\n'
  printf '.planning/power/fleet-results/\n'
} >>"$WORKTREE_PATH/.gitignore" || recover 2 'cannot write worktree gitignore'

git -C "$WORKTREE_PATH" add -A >/dev/null 2>&1 || recover 2 'cannot stage adopted contracts'
git -C "$WORKTREE_PATH" commit -m "chore(power-fleet): adopt approved contracts for $SLUG" >/dev/null 2>&1 \
  || recover 2 'cannot commit adopted contracts'

# ---- compose and environment ---------------------------------------------------------------

require_absent "$WORKTREE_PATH/$COMPOSE_FILE" || recover 2 'compose destination already exists'
COMPOSE_TEMP=$(mktemp "$WORKTREE_PATH/.${COMPOSE_FILE}.XXXXXX") || recover 2 'cannot stage compose file'
cp "$TEMPLATE" "$COMPOSE_TEMP" || recover 2 'cannot copy compose template'
require_absent "$WORKTREE_PATH/$COMPOSE_FILE" || recover 2 'compose destination changed before publication'
mv "$COMPOSE_TEMP" "$WORKTREE_PATH/$COMPOSE_FILE" || recover 2 'cannot publish compose file'

require_absent "$WORKTREE_PATH/$ENV_FILE" || recover 2 'generated fleet environment already exists'
ENV_TEMP=$(mktemp "$WORKTREE_PATH/.${ENV_FILE}.XXXXXX") || recover 2 'cannot stage fleet environment'
# umask before the write, not chmod after: the throwaway password must never exist
# world-readable, not even for an instant.
(
  umask 077
  {
    printf 'COMPOSE_PROJECT_NAME=%s\n' "$PROJECT_NAME"
    printf 'POWER_ENV=development\n'
    printf 'APP_PORT=%s\n' "$APP_PORT"
    printf 'DB_PORT=%s\n' "$DB_PORT"
    printf 'POSTGRES_DB=power_fleet\n'
    printf 'POSTGRES_USER=power_fleet\n'
    printf 'POSTGRES_PASSWORD=development-only\n'
  } >"$ENV_TEMP"
) || recover 2 'cannot write fleet environment'
chmod 600 "$ENV_TEMP"
require_absent "$WORKTREE_PATH/$ENV_FILE" || recover 2 'fleet environment destination changed before publication'
mv "$ENV_TEMP" "$WORKTREE_PATH/$ENV_FILE" || recover 2 'cannot publish fleet environment'

if [[ -f $WORKTREE_PATH/Dockerfile ]]; then
  (cd "$WORKTREE_PATH" && docker compose -p "$PROJECT_NAME" --env-file "$ENV_FILE" -f "$COMPOSE_FILE" up -d) >/dev/null 2>&1 \
    || recover 2 'cannot start the fleet stack'
else
  # Without a Dockerfile the app service cannot build, so bring up the database only.
  (cd "$WORKTREE_PATH" && docker compose -p "$PROJECT_NAME" --env-file "$ENV_FILE" -f "$COMPOSE_FILE" up -d db) >/dev/null 2>&1 \
    || recover 2 'cannot start the fleet database'
fi
STACK_UP=true

# ---- pane command --------------------------------------------------------------------------
# The runner is reached through a shell-quoted file, never typed into a shell. That removes the
# entire class of injection and timing bugs that sending keystrokes invites.

RUNNER=$SCRIPT_DIR/$RUNTIME-fleet-run.sh
[[ -f $RUNNER ]] || recover 2 "missing runtime runner: $RUNNER"
printf '#!/usr/bin/env bash\nexec %q %q %q %q\n' \
  "$RUNNER" "$SLUG" "$WORKTREE_PATH" danger-full-access >"$PANE_FILE" \
  || recover 2 'cannot write pane command'
chmod 700 "$PANE_FILE"

# ---- cmux workspace ------------------------------------------------------------------------

CMUX_WORKSPACE_ID=$(power_cmux_new_workspace \
  "power-fleet:$SLUG" "$WORKTREE_PATH" "bash $PANE_FILE") \
  || recover 2 'cannot create the cmux workspace'
[[ -n $CMUX_WORKSPACE_ID ]] || recover 2 'cmux did not return a workspace id'
power_cmux_status "$CMUX_WORKSPACE_ID" "$SLUG queued"

# ---- member record -------------------------------------------------------------------------

NOW=$(date -u +%Y-%m-%dT%H:%M:%SZ)
MEMBER_TEMP=$(mktemp "$FLEET_DIR/.$SLUG.json.XXXXXX") || recover 2 'cannot stage member record'
jq -n \
  --arg slug "$SLUG" \
  --arg runtime "$RUNTIME" \
  --arg branch "$BRANCH" \
  --arg base_branch "$BRANCH_CURRENT" \
  --arg base_commit "$BASE_COMMIT" \
  --arg worktree "$WORKTREE_PATH" \
  --arg project "$PROJECT_NAME" \
  --arg workspace "$CMUX_WORKSPACE_ID" \
  --arg spec "$SPEC_SHA" \
  --arg plan "$PLAN_SHA" \
  --arg created "$NOW" \
  --argjson app "$APP_PORT" \
  --argjson db "$DB_PORT" \
  --argjson index "$INDEX" \
  '{
     schema_version: 1,
     slug: $slug,
     runtime: $runtime,
     branch: $branch,
     base_branch: $base_branch,
     base_commit: $base_commit,
     worktree_path: $worktree,
     project_name: $project,
     cmux_workspace_id: $workspace,
     app_port: $app,
     db_port: $db,
     port_index: $index,
     spec_sha256: $spec,
     plan_sha256: $plan,
     kanban_task_id: null,
     status: "ACTIVE",
     created_at: $created,
     updated_at: $created
   }' >"$MEMBER_TEMP" || recover 2 'cannot build member record'
require_absent "$MEMBER_FILE" || recover 2 'member destination changed before publication'
mv "$MEMBER_TEMP" "$MEMBER_FILE" || recover 2 'cannot publish member record'

trap - HUP INT TERM
release_lock

printf 'fleet-up: %s launched on %s (app %s, db %s, branch %s)\n' \
  "$SLUG" "$RUNTIME" "$APP_PORT" "$DB_PORT" "$BRANCH"
