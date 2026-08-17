#!/usr/bin/env bash
# Run one authorized Flow phase autonomously inside its registered fleet worktree.
set -Eeuo pipefail

usage() { printf 'Usage: %s <lowercase-slug> <worktree-path> [danger-full-access]\n' "${0##*/}" >&2; exit 2; }
fail() { printf 'fleet-run: %s\n' "$*" >&2; exit 2; }
[[ $# -eq 2 || $# -eq 3 ]] || usage
SLUG=$1; WORKTREE_INPUT=$2
EXPECTED_RUNTIME=${FLOW_FLEET_RUNTIME:-codex}
case "$EXPECTED_RUNTIME" in codex|claude) ;; *) fail "unsupported fleet runtime: $EXPECTED_RUNTIME";; esac
[[ $SLUG =~ ^[a-z0-9][a-z0-9-]*$ && $SLUG == *[a-z]* && $SLUG != dashboard ]] || fail "invalid slug: $SLUG"
if [[ $# -eq 3 ]]; then [[ $3 == danger-full-access ]] || fail 'permission mode must be danger-full-access'; fi
# $EXPECTED_RUNTIME is constrained to codex|claude above, so it names the provider binary.
for binary in git jq "$EXPECTED_RUNTIME" shasum awk python3 sleep; do command -v "$binary" >/dev/null 2>&1 || fail "required binary unavailable: $binary"; done
PYTHON3_BIN=$(command -v python3)

WORKTREE=$(cd -- "$WORKTREE_INPUT" 2>/dev/null && pwd -P) || fail 'worktree path is unavailable'
EXPECTED_BRANCH=flow-fleet/$SLUG
WORKTREE_LIST=$(git -C "$WORKTREE" worktree list --porcelain 2>/dev/null) || fail 'unable to inspect Git worktree registration'
FIRST_REGISTRATION=${WORKTREE_LIST%%$'\n'*}
[[ $FIRST_REGISTRATION == worktree\ * ]] || fail 'unable to derive initiating worktree root'
MAIN_INPUT=${FIRST_REGISTRATION#worktree }
MAIN_ROOT=$(cd -- "$MAIN_INPUT" 2>/dev/null && pwd -P) || fail 'initiating worktree root is unavailable'
FLEET_DIR=$MAIN_ROOT/.planning/flow/fleet
MEMBER_FILE=$FLEET_DIR/$SLUG.json

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
  jq -e --arg slug "$SLUG" --arg branch "$EXPECTED_BRANCH" --arg worktree "$WORKTREE" --arg runtime "$EXPECTED_RUNTIME" '
    type == "object" and .slug == $slug and .branch == $branch and
    .worktree_path == $worktree and .runtime == $runtime and .status == "ACTIVE" and
    (.spec_sha256 | type == "string" and test("^[0-9a-f]{64}$")) and
    (.decisions_sha256 | type == "string" and test("^[0-9a-f]{64}$"))
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

safe_main_dir .planning/flow/fleet false || fail 'registered fleet member central state path is unsafe'
require_regular_nosymlink "$MEMBER_FILE" || fail "registered fleet member is unavailable or unsafe for $SLUG"
if ! jq -e --arg slug "$SLUG" --arg branch "$EXPECTED_BRANCH" --arg worktree "$WORKTREE" '
  type == "object" and .slug == $slug and .branch == $branch and
  .worktree_path == $worktree and (.status | type == "string") and
  (.spec_sha256 | type == "string" and test("^[0-9a-f]{64}$")) and
  (.decisions_sha256 | type == "string" and test("^[0-9a-f]{64}$"))
' "$MEMBER_FILE" >/dev/null 2>&1; then fail "registered fleet member does not bind $SLUG to the supplied worktree"; fi
CENTRAL_STATUS=$(jq -r '.status' "$MEMBER_FILE")
[[ $CENTRAL_STATUS == ACTIVE ]] || fail "central member status $CENTRAL_STATUS cannot start a runner"
IFS=$'\t' read -r BOUND_SPEC_SHA256 BOUND_DECISIONS_SHA256 <<<"$(jq -r '[.spec_sha256,.decisions_sha256] | @tsv' "$MEMBER_FILE")"
worktree_identity_matches || fail 'registered fleet member does not match canonical Git worktree registration'

SCRIPT_DIR=$(cd -- "${BASH_SOURCE[0]%/*}" && pwd -P)
SCHEMA=$(cd -- "$SCRIPT_DIR/../templates" && pwd -P)/fleet-result.schema.json
require_regular_nosymlink "$SCHEMA" || fail "missing result schema: $SCHEMA"
# The privileged vector lives in exactly one adapter, selected here from the
# runtime already bound into the central member. Nothing below builds a
# provider command or a permission flag of its own.
ENGINE_ADAPTER=$SCRIPT_DIR/fleet-engine-$EXPECTED_RUNTIME.sh
require_regular_nosymlink "$ENGINE_ADAPTER" || fail "missing runtime adapter: $ENGINE_ADAPTER"
# shellcheck source=/dev/null
source "$ENGINE_ADAPTER"
PHASE_DIR=$WORKTREE/.planning/flow/phases/$SLUG
safe_worktree_dir ".planning/flow/phases/$SLUG" false || fail "unsafe phase contract path for $SLUG"
require_regular_nosymlink "$PHASE_DIR/spec.md" && require_regular_nosymlink "$PHASE_DIR/decisions.md" || fail "missing approved phase contracts for $SLUG"
FLOW_DIR=$WORKTREE/.planning/flow; STATUS_FILE=$FLOW_DIR/fleet-status.json
LOG_DIR=$FLOW_DIR/fleet-logs; RESULT_DIR=$FLOW_DIR/fleet-results
safe_worktree_dir .planning/flow/fleet-logs true || fail 'unsafe fleet log path'
safe_worktree_dir .planning/flow/fleet-results true || fail 'unsafe fleet result path'

RUNNER_LOCK=$FLEET_DIR/.${SLUG}.runner.lock
safe_main_dir .planning/flow/fleet false || fail 'unsafe central fleet state path'
mkdir "$RUNNER_LOCK" 2>/dev/null || fail "fleet member is already running: $SLUG"
LOCK_HELD=true; CURRENT_RESULT_TEMP=; CURRENT_STATUS_TEMP=; CURRENT_LOG_TEMP=; CURRENT_RAW_TEMP=
PROVIDER_PID=; PROVIDER_PGID=; ACTIVE_STAGE=
# argv: <cwd-or-empty> <provider> [provider-args...]. The provider always leads its
# own process group so the runner can prove the whole descendant group is gone.
PROVIDER_LAUNCHER='import os,sys
directory = sys.argv[1]
if directory:
    os.chdir(directory)
os.setsid()
os.execvp(sys.argv[2], sys.argv[2:])'
STATUS_FINAL=false; RECOVERING=false; OWNERSHIP_UNRESOLVED=false; CORRECTION_CYCLES=0; INVOCATION=0
RESULT_MESSAGE=; RESULT_VERDICT=NONE
AUDIT_ENABLED=false
MAIN_CONFIG=$MAIN_ROOT/.planning/flow/config.json
if require_regular_nosymlink "$MAIN_CONFIG"; then
  [[ $(jq -r '.audit == true' "$MAIN_CONFIG" 2>/dev/null) == true ]] && AUDIT_ENABLED=true
fi

best_effort_stage_audit() {
  local stage=$1 status=$2 detail
  [[ $AUDIT_ENABLED == true ]] || return 0
  detail=$(jq -nc --arg slug "$SLUG" --arg stage "$stage" --arg status "$status" '{slug:$slug,stage:$stage,status:$status}') || {
    printf 'warning: fleet_stage audit record failed\n' >&2; return 0;
  }
  if ! python3 "$SCRIPT_DIR/flow_audit.py" --root "$MAIN_ROOT" record \
    --action fleet_stage --skill flow-fleet --phase "$stage" --status "$status" \
    --target .planning/flow/fleet-status.json --detail "$detail" >/dev/null 2>&1; then
    printf 'warning: fleet_stage audit record failed\n' >&2
  fi
}

provider_group_alive() {
  [[ -n $PROVIDER_PGID ]] && kill -0 -- "-$PROVIDER_PGID" 2>/dev/null
}

terminate_owned_provider() {
  local attempt
  [[ -n $PROVIDER_PGID ]] || return 0
  kill -TERM -- "-$PROVIDER_PGID" 2>/dev/null || true
  attempt=0
  while provider_group_alive && (( attempt < 20 )); do sleep 0.1; attempt=$((attempt + 1)); done
  if provider_group_alive; then
    kill -KILL -- "-$PROVIDER_PGID" 2>/dev/null || true
  fi
  [[ -z $PROVIDER_PID ]] || wait "$PROVIDER_PID" 2>/dev/null || true
  attempt=0
  while provider_group_alive && (( attempt < 20 )); do sleep 0.05; attempt=$((attempt + 1)); done
  if provider_group_alive; then
    printf 'fleet-run: owned provider process group did not terminate\n' >&2
    return 1
  fi
  PROVIDER_PID=; PROVIDER_PGID=
}

ensure_provider_absent() {
  if terminate_owned_provider; then return 0; fi
  OWNERSHIP_UNRESOLVED=true
  printf 'fleet-run: provider ownership is unresolved; retaining runner lock for explicit recovery\n' >&2
  return 1
}

cleanup_owned() {
  set +e
  [[ $OWNERSHIP_UNRESOLVED == false ]] || return 1
  if ! ensure_provider_absent; then return 1; fi
  if [[ -n $CURRENT_RESULT_TEMP ]]; then rm -f "$CURRENT_RESULT_TEMP"; CURRENT_RESULT_TEMP=; fi
  if [[ -n $CURRENT_STATUS_TEMP ]]; then rm -f "$CURRENT_STATUS_TEMP"; CURRENT_STATUS_TEMP=; fi
  if [[ -n $CURRENT_LOG_TEMP ]]; then rm -f "$CURRENT_LOG_TEMP"; CURRENT_LOG_TEMP=; fi
  if [[ -n $CURRENT_RAW_TEMP ]]; then rm -f "$CURRENT_RAW_TEMP"; CURRENT_RAW_TEMP=; fi
  if [[ $LOCK_HELD == true ]]; then
    if rmdir "$RUNNER_LOCK" 2>/dev/null; then LOCK_HELD=false
    else printf 'fleet-run: failed to release runner lock\n' >&2; return 1; fi
  fi
}

write_status() {
  local stage=$1 status=$2 message=$3 verdict=$4 now
  now=$(date -u +%Y-%m-%dT%H:%M:%SZ)
  safe_worktree_dir .planning/flow false || return 1
  CURRENT_STATUS_TEMP=$(mktemp "$FLOW_DIR/.fleet-status.json.XXXXXX") || return 1
  if ! jq -n --arg slug "$SLUG" --arg stage "$stage" --arg status "$status" \
    --arg message "$message" --arg verdict "$verdict" --arg updated_at "$now" \
    --argjson correction_cycles "$CORRECTION_CYCLES" \
    '{slug:$slug,stage:$stage,status:$status,message:$message,verdict:$verdict,updated_at:$updated_at,correction_cycles:$correction_cycles}' \
    >"$CURRENT_STATUS_TEMP"; then rm -f "$CURRENT_STATUS_TEMP"; CURRENT_STATUS_TEMP=; return 1; fi
  if ! mv "$CURRENT_STATUS_TEMP" "$STATUS_FILE"; then return 1; fi
  CURRENT_STATUS_TEMP=
}

status_is_done() { [[ -f $STATUS_FILE ]] && [[ $(jq -r '.status // ""' "$STATUS_FILE" 2>/dev/null) == DONE ]]; }
recover_unexpected() {
  local code=$?; [[ $RECOVERING == false ]] || exit "$code"; RECOVERING=true
  trap - ERR HUP INT TERM; set +e
  if ! ensure_provider_absent; then
    printf 'fleet-run: unexpected runner failure during %s; terminal state not published while provider ownership is unresolved\n' "${ACTIVE_STAGE:-startup}" >&2
    exit "$code"
  fi
  if [[ -n $ACTIVE_STAGE && $STATUS_FINAL == false ]] && ! status_is_done; then
    if [[ -n $CURRENT_STATUS_TEMP ]] || ! write_status "$ACTIVE_STAGE" NEEDS_HUMAN "unexpected runner failure during $ACTIVE_STAGE" NONE; then
      printf 'fleet-run: failed to publish ERR recovery status for %s\n' "$ACTIVE_STAGE" >&2
    else
      best_effort_stage_audit "$ACTIVE_STAGE" NEEDS_HUMAN
    fi
  fi
  printf 'fleet-run: unexpected runner failure during %s\n' "${ACTIVE_STAGE:-startup}" >&2
  cleanup_owned; exit "$code"
}
recover_signal() {
  local name=$1 code=$2; [[ $RECOVERING == false ]] || exit "$code"; RECOVERING=true
  trap - ERR HUP INT TERM; set +e
  if ! ensure_provider_absent; then
    printf 'fleet-run: runner received %s during %s; terminal state not published while provider ownership is unresolved\n' "$name" "${ACTIVE_STAGE:-startup}" >&2
    exit "$code"
  fi
  if [[ -n $ACTIVE_STAGE && $STATUS_FINAL == false ]] && ! status_is_done; then
    if [[ -n $CURRENT_STATUS_TEMP ]] || ! write_status "$ACTIVE_STAGE" NEEDS_HUMAN "runner terminated by $name during $ACTIVE_STAGE" NONE; then
      printf 'fleet-run: failed to publish %s recovery status for %s\n' "$name" "$ACTIVE_STAGE" >&2
    else
      best_effort_stage_audit "$ACTIVE_STAGE" NEEDS_HUMAN
    fi
  fi
  printf 'fleet-run: runner terminated by %s during %s\n' "$name" "${ACTIVE_STAGE:-startup}" >&2
  cleanup_owned; exit "$code"
}
trap recover_unexpected ERR
trap 'recover_signal HUP 129' HUP
trap 'recover_signal INT 130' INT
trap 'recover_signal TERM 143' TERM
trap cleanup_owned EXIT

if [[ -e $STATUS_FILE || -L $STATUS_FILE ]]; then
  require_regular_nosymlink "$STATUS_FILE" || fail 'local fleet status is unsafe; explicit recovery is required'
  if ! LOCAL_STATUS=$(jq -er --arg slug "$SLUG" '
    if type == "object" and .slug == $slug and
      (.stage == "plan" or .stage == "execute" or .stage == "review" or .stage == "verify" or .stage == "execute-fix" or .stage == "review-fix") and
      (.status == "RUNNING" or .status == "ACTIVE" or .status == "DONE" or .status == "NEEDS_HUMAN") and
      (.message | type == "string" and length > 0) and
      (.verdict == "NONE" or .verdict == "APPROVED" or .verdict == "CAVEATS" or .verdict == "REJECTED") and
      (.updated_at | type == "string" and length > 0) and
      (.correction_cycles | type == "number" and floor == . and . >= 0)
    then .status else error("malformed local status") end
  ' "$STATUS_FILE" 2>/dev/null); then
    fail 'local fleet status is malformed; explicit recovery is required'
  fi
  fail "local fleet status $LOCAL_STATUS is not startable; explicit recovery is required"
fi

needs_human() {
  local stage=$1 message=$2 verdict=${3:-NONE}
  if ! ensure_provider_absent; then
    printf 'fleet-run: cannot publish NEEDS_HUMAN for %s while provider ownership is unresolved\n' "$stage" >&2
    exit 1
  fi
  if ! write_status "$stage" NEEDS_HUMAN "$message" "$verdict"; then
    printf 'fleet-run: failed to publish NEEDS_HUMAN status for %s\n' "$stage" >&2
    STATUS_FINAL=true
    exit 1
  fi
  best_effort_stage_audit "$stage" NEEDS_HUMAN
  STATUS_FINAL=true; printf 'fleet-run: %s\n' "$message" >&2; exit 1
}

contract_is_approved() {
  awk '/^[[:space:]]*(-[[:space:]]+)?Status:[[:space:]]*/ { fields++; normalized=$0; sub(/^[[:space:]]*(-[[:space:]]+)?/, "", normalized); if (normalized == "Status: APPROVED") approved++ } END { exit !(fields == 1 && approved == 1) }' "$1"
}
file_sha256() { shasum -a 256 "$1" | awk '{print $1}'; }
contracts_match_bound_member() {
  safe_worktree_dir ".planning/flow/phases/$SLUG" false || return 1
  require_regular_nosymlink "$PHASE_DIR/spec.md" || return 1
  require_regular_nosymlink "$PHASE_DIR/decisions.md" || return 1
  contract_is_approved "$PHASE_DIR/spec.md" || return 1
  contract_is_approved "$PHASE_DIR/decisions.md" || return 1
  [[ $(file_sha256 "$PHASE_DIR/spec.md") == "$BOUND_SPEC_SHA256" ]] || return 1
  [[ $(file_sha256 "$PHASE_DIR/decisions.md") == "$BOUND_DECISIONS_SHA256" ]] || return 1
}

contracts_match_bound_member || needs_human plan 'approved fleet contracts do not match the bound member state'

validate_result() {
  local stage=$1 result_file=$2
  jq -e --arg expected "$stage" '
    type == "object" and (keys == ["message", "stage", "status", "verdict"]) and
    (.stage == $expected) and
    (.stage == "plan" or .stage == "execute" or .stage == "review" or .stage == "verify" or .stage == "execute-fix" or .stage == "review-fix") and
    (.status == "OK" or .status == "FAILED" or .status == "NEEDS_HUMAN") and
    ((.message | type) == "string") and ((.message | length) > 0) and
    (.verdict == "NONE" or .verdict == "APPROVED" or .verdict == "CAVEATS" or .verdict == "REJECTED") and
    (if .stage == "verify" then .verdict != "NONE" else .verdict == "NONE" end)
  ' "$result_file" >/dev/null 2>&1
}

artifact_directory() {
  case $1 in
    plan) printf '%s/plans' "$PHASE_DIR" ;;
    execute|execute-fix) printf '%s/execution' "$PHASE_DIR" ;;
    review|review-fix) printf '%s/review' "$PHASE_DIR" ;;
    verify) printf '%s/verify' "$PHASE_DIR" ;;
    *) return 1 ;;
  esac
}
artifact_snapshot() {
  local directory artifact hash; directory=$(artifact_directory "$1") || return 1
  for artifact in "$directory"/*.md; do
    [[ -f $artifact ]] || continue
    hash=$(git -C "$WORKTREE" hash-object --no-filters -- "$artifact") || return 1
    printf '%s\t%s\n' "$hash" "$artifact"
  done
}
artifact_path_is_safe() {
  local directory relative
  directory=$(artifact_directory "$1") || return 1
  relative=${directory#"$WORKTREE"/}
  if [[ -e $directory || -L $directory ]]; then safe_worktree_dir "$relative" false
  else safe_worktree_dir ".planning/flow/phases/$SLUG" false
  fi
}
artifact_has_fresh_entry() {
  local before=$1 after=$2 after_entry before_entry found; [[ -n $after ]] || return 1
  while IFS= read -r after_entry; do
    [[ -n $after_entry ]] || continue; found=false
    while IFS= read -r before_entry; do if [[ $after_entry == "$before_entry" ]]; then found=true; break; fi; done <<<"$before"
    [[ $found == false ]] && return 0
  done <<<"$after"
  return 1
}

build_prompt() {
  local stage=$1 capability arguments instruction skill suffix
  case $stage in
    plan) capability=plan; arguments=; instruction='create the approved atomic plan artifact' ;;
    execute) capability=execute; arguments=; instruction='execute the approved plan and write its execution summary' ;;
    review) capability=review; arguments=; instruction='perform scoped review and write the review artifact' ;;
    verify) capability=verify; arguments=; instruction='independently verify the phase and write the verification artifact' ;;
    execute-fix) capability=execute; arguments=' --fix'; instruction='execute only the bounded correction tasks from the rejected verification' ;;
    review-fix) capability=review; arguments=; instruction='review only the current correction cycle and write its fix review artifact' ;;
    *) return 1 ;;
  esac
  # The invocation syntax and the result contract are runtime-specific.
  skill=$("flow_engine_${EXPECTED_RUNTIME}_skill_ref" "$capability")$arguments
  suffix=$("flow_engine_${EXPECTED_RUNTIME}_prompt_suffix" "$stage")
  printf -v STAGE_PROMPT '%s ' "FLOW_FLEET_SLUG=$SLUG" "FLOW_FLEET_STAGE=$stage" \
    "Invoke $skill for phase $SLUG and $instruction." \
    'This is an already-authorized autonomous fleet stage in an isolated worktree.' \
    'Use best judgment at ordinary interactive approval gates, but obey destructive-action prohibitions, prerequisites, secret restrictions, and explicit stop conditions.' \
    "${suffix%% }"
  STAGE_PROMPT=${STAGE_PROMPT% }
}

run_stage() {
  local stage=$1 timestamp result_file invalid_file log_file provider_status message verdict before_snapshot after_snapshot
  ACTIVE_STAGE=$stage; INVOCATION=$((INVOCATION + 1))
  timestamp=$(date -u +%Y%m%dT%H%M%SZ)-$(printf '%02d' "$INVOCATION")
  result_file=$RESULT_DIR/$stage-$timestamp.json; invalid_file=$RESULT_DIR/$stage-$timestamp.invalid.json
  log_file=$LOG_DIR/$stage-$timestamp.log
  safe_worktree_dir .planning/flow/fleet-logs false || needs_human "$stage" 'unsafe fleet log path'
  safe_worktree_dir .planning/flow/fleet-results false || needs_human "$stage" 'unsafe fleet result path'
  artifact_path_is_safe "$stage" || needs_human "$stage" 'unsafe stage artifact path'
  contracts_match_bound_member || needs_human "$stage" 'approved fleet contracts do not match the bound member state'
  before_snapshot=$(artifact_snapshot "$stage"); build_prompt "$stage"
  write_status "$stage" RUNNING "running $stage" NONE
  CURRENT_RESULT_TEMP=$(mktemp "$RESULT_DIR/.${stage}-${timestamp}.json.XXXXXX")
  CURRENT_LOG_TEMP=$(mktemp "$LOG_DIR/.${stage}-${timestamp}.log.XXXXXX")
  # Only the adapter builds the privileged vector; the runner never names a provider.
  FLOW_ENGINE_COMMAND=(); FLOW_ENGINE_CWD=; FLOW_ENGINE_RESULT_FROM_STDOUT=false
  "flow_engine_${EXPECTED_RUNTIME}_stage_command" \
    "$WORKTREE" "$SCHEMA" "$CURRENT_RESULT_TEMP" "$STAGE_PROMPT"
  if [[ $FLOW_ENGINE_RESULT_FROM_STDOUT == true ]]; then
    # The provider reports its final message on stdout, so stdout is captured
    # apart from the log and converted by the adapter after ownership is proved.
    CURRENT_RAW_TEMP=$(mktemp "$RESULT_DIR/.${stage}-${timestamp}.raw.XXXXXX")
    "$PYTHON3_BIN" -c "$PROVIDER_LAUNCHER" "$FLOW_ENGINE_CWD" "${FLOW_ENGINE_COMMAND[@]}" \
      >"$CURRENT_RAW_TEMP" 2>"$CURRENT_LOG_TEMP" & PROVIDER_PID=$!; PROVIDER_PGID=$PROVIDER_PID
  else
    "$PYTHON3_BIN" -c "$PROVIDER_LAUNCHER" "$FLOW_ENGINE_CWD" "${FLOW_ENGINE_COMMAND[@]}" \
      >"$CURRENT_LOG_TEMP" 2>&1 & PROVIDER_PID=$!; PROVIDER_PGID=$PROVIDER_PID
  fi
  if wait "$PROVIDER_PID"; then provider_status=0; else provider_status=$?; fi
  if ! ensure_provider_absent; then
    RECOVERING=true; trap - ERR HUP INT TERM
    printf 'fleet-run: refusing to continue %s while provider ownership is unresolved\n' "$stage" >&2
    exit 1
  fi
  safe_worktree_dir .planning/flow/fleet-logs false || needs_human "$stage" 'fleet log path changed after the provider'
  [[ ! -e $log_file && ! -L $log_file ]] || needs_human "$stage" 'fleet log publication collision'
  mv "$CURRENT_LOG_TEMP" "$log_file"; CURRENT_LOG_TEMP=
  if ! worktree_identity_matches; then needs_human "$stage" 'fleet worktree changed after the provider; refusing stage commit'; fi
  contracts_match_bound_member || needs_human "$stage" 'approved fleet contracts changed during provider execution'
  if [[ $provider_status -ne 0 ]]; then needs_human "$stage" "provider exited non-zero for $stage: $provider_status"; fi
  if [[ -n $CURRENT_RAW_TEMP ]]; then
    "flow_engine_${EXPECTED_RUNTIME}_publish_result" "$CURRENT_RAW_TEMP" "$CURRENT_RESULT_TEMP" || true
    rm -f "$CURRENT_RAW_TEMP"; CURRENT_RAW_TEMP=
  fi
  if [[ ! -s $CURRENT_RESULT_TEMP ]] || ! validate_result "$stage" "$CURRENT_RESULT_TEMP"; then
    mv "$CURRENT_RESULT_TEMP" "$invalid_file"; CURRENT_RESULT_TEMP=; needs_human "$stage" "invalid structured result for $stage"
  fi
  mv "$CURRENT_RESULT_TEMP" "$result_file"; CURRENT_RESULT_TEMP=
  message=$(jq -r '.message' "$result_file"); verdict=$(jq -r '.verdict' "$result_file")
  if [[ $(jq -r '.status' "$result_file") != OK ]]; then needs_human "$stage" "$message" "$verdict"; fi
  artifact_path_is_safe "$stage" || needs_human "$stage" 'unsafe stage artifact path after the provider'
  after_snapshot=$(artifact_snapshot "$stage")
  if ! artifact_has_fresh_entry "$before_snapshot" "$after_snapshot"; then needs_human "$stage" "missing fresh $stage artifact"; fi
  worktree_identity_matches || needs_human "$stage" 'fleet worktree changed before commit; refusing stage commit'
  if ! git -C "$WORKTREE" add -A || ! git -C "$WORKTREE" commit -m "chore(flow-fleet): $SLUG $stage"; then needs_human "$stage" "failed to commit $stage changes"; fi
  RESULT_MESSAGE=$message; RESULT_VERDICT=$verdict; write_status "$stage" ACTIVE "$message" "$verdict"
  best_effort_stage_audit "$stage" ACTIVE
}

run_stage plan; run_stage execute; run_stage review; run_stage verify
while [[ $RESULT_VERDICT == REJECTED ]]; do
  if (( CORRECTION_CYCLES >= 2 )); then needs_human verify "verification rejected after two correction cycles: $RESULT_MESSAGE" REJECTED; fi
  CORRECTION_CYCLES=$((CORRECTION_CYCLES + 1))
  run_stage execute-fix; run_stage review-fix; run_stage verify
done
write_status verify DONE "$RESULT_MESSAGE" "$RESULT_VERDICT"; best_effort_stage_audit verify DONE; STATUS_FINAL=true
printf 'fleet-run: %s completed with %s\n' "$SLUG" "$RESULT_VERDICT"
