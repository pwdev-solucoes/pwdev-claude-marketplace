#!/usr/bin/env bash
# Drive one fleet member's autonomous lifecycle inside its worktree.
#
# Never invoked directly. The runtime is pinned by <runtime>-fleet-run.sh, and this script
# refuses to start if that runtime disagrees with the one bound into the member record.
#
# Owns: the runner lock, contract verification, process-group ownership, structured result
# validation, per-stage commits, and the two-cycle correction cap. Identical for every runtime;
# only the privileged vector differs, and it lives in exactly one adapter.
set -Eeuo pipefail

SCRIPT_DIR=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd -P)
# shellcheck source=fleet-common.sh
source "$SCRIPT_DIR/fleet-common.sh"
# shellcheck source=cmux-common.sh
source "$SCRIPT_DIR/cmux-common.sh"

fail() { printf 'fleet-run: %s\n' "$*" >&2; exit 1; }

[[ $# -ge 2 && $# -le 4 ]] \
  || fail 'usage: <runtime>-fleet-run.sh <slug> <worktree> [permission-mode] [--resume]'
SLUG=$1
WORKTREE=$2
RESUME=false
for arg in "${@:3}"; do
  case $arg in
    danger-full-access) ;;
    --resume) RESUME=true ;;
    *) fail "unexpected argument: $arg" ;;
  esac
done

EXPECTED_RUNTIME=${POWER_FLEET_RUNTIME:-}
[[ -n $EXPECTED_RUNTIME ]] || fail 'no runtime pinned; start through <runtime>-fleet-run.sh'
power_require_runtime "$EXPECTED_RUNTIME" || exit 2

command -v jq >/dev/null 2>&1 || fail 'jq is required'
PYTHON3_BIN=$(command -v python3) || fail 'python3 is required'

[[ -d $WORKTREE ]] || fail "no such worktree: $WORKTREE"
WORKTREE=$(cd "$WORKTREE" && pwd -P)

EXPECTED_BRANCH=power-fleet/$SLUG

# Derive the main checkout from git itself: the first porcelain entry is the main worktree.
# Never take it from the environment, which the provider could have changed.
MAIN_ROOT=$(git -C "$WORKTREE" worktree list --porcelain 2>/dev/null | awk '/^worktree /{print substr($0,10); exit}') \
  || fail 'cannot resolve the main worktree'
[[ -n $MAIN_ROOT && -d $MAIN_ROOT ]] || fail 'cannot resolve the main worktree'
MAIN_ROOT=$(cd "$MAIN_ROOT" && pwd -P)

FLEET_DIR=$MAIN_ROOT/.planning/power/fleet
MEMBER_FILE=$FLEET_DIR/$SLUG.json
STATUS_FILE=$WORKTREE/.planning/power/fleet-status.json
LOG_DIR=$WORKTREE/.planning/power/fleet-logs
RESULT_DIR=$WORKTREE/.planning/power/fleet-results
FEATURE_REL=.planning/power/features/$SLUG
SCHEMA=$(cd -- "$SCRIPT_DIR/../templates" && pwd -P)/fleet-result.schema.json

require_regular_nosymlink() { [[ -f $1 && ! -L $1 ]]; }
require_regular_nosymlink "$SCHEMA" || fail "missing result schema: $SCHEMA"

# Read the cap from the schema rather than restating it: Codex is held to the schema natively and
# the prose contract quotes the same number, so a third hand-maintained copy here is one more
# place for the drift the schema exists to prevent.
MESSAGE_MAX=$(jq -er '.properties.message.maxLength | select(type == "number" and . > 0)' "$SCHEMA" 2>/dev/null) \
  || fail 'result schema does not declare a message length limit'

mkdir -p "$LOG_DIR" "$RESULT_DIR" "$(dirname "$STATUS_FILE")"

# ---- identity ------------------------------------------------------------------------------

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

# The runtime check here is what makes the fixed-runtime rule enforceable rather than merely
# stated: a runner whose adapter disagrees with the bound member refuses to start.
member_binding_matches() {
  require_regular_nosymlink "$MEMBER_FILE" || return 1
  jq -e --arg slug "$SLUG" --arg branch "$EXPECTED_BRANCH" --arg worktree "$WORKTREE" \
        --arg runtime "$EXPECTED_RUNTIME" --argjson resume "$RESUME" '
    type == "object"
      and .slug == $slug
      and .branch == $branch
      and .worktree_path == $worktree
      and .runtime == $runtime
      # A stopped member is NEEDS_HUMAN on purpose, so only an explicit --resume may pick it up:
      # the flag is the human saying they looked, which is exactly what that status asks for.
      and (.status == "ACTIVE" or .status == "RUNNING" or ($resume and .status == "NEEDS_HUMAN"))
      and (.spec_sha256 | type == "string" and test("^[0-9a-f]{64}$"))
      and (.plan_sha256 | type == "string" and test("^[0-9a-f]{64}$"))
  ' "$MEMBER_FILE" >/dev/null 2>&1
}

worktree_identity_matches() { registered_worktree_matches && member_binding_matches; }

sha256_of() {
  if command -v shasum >/dev/null 2>&1; then shasum -a 256 "$1" | awk '{print $1}'
  elif command -v sha256sum >/dev/null 2>&1; then sha256sum "$1" | awk '{print $1}'
  else openssl dgst -sha256 "$1" | awk '{print $NF}'; fi
}

spec_matches_bound_member() {
  local spec=$WORKTREE/$FEATURE_REL/spec.md bound_spec
  [[ -f $spec ]] || return 1
  bound_spec=$(jq -er '.spec_sha256' "$MEMBER_FILE" 2>/dev/null) || return 1
  [[ $(sha256_of "$spec") == "$bound_spec" ]] || return 1
  return 0
}

contracts_match_bound_member() {
  local plan=$WORKTREE/$FEATURE_REL/plan.md bound_plan
  spec_matches_bound_member || return 1
  [[ -f $plan ]] || return 1
  bound_plan=$(jq -er '.plan_sha256' "$MEMBER_FILE" 2>/dev/null) || return 1
  [[ $(sha256_of "$plan") == "$bound_plan" ]] || return 1
  return 0
}

# The plan stage writes one of the bound contracts, so it cannot be held to both of them.
#
# references/artifacts.md places the executable plan at features/<slug>/plan.md, and fleet-up.sh
# hashes those exact bytes at launch. The plan stage is asked to decompose the spec into that same
# file, so any faithful run invalidates the binding that guards it and the member stops on its own
# first stage — not on a tampered contract, but on the artifact it was told to produce.
#
# So the plan stage is guarded by spec.md alone, and plan.md is re-bound from the bytes it
# committed. spec.md is what a human approved and stays frozen for the whole run; plan.md is
# frozen again the moment the stage that owns it is done.
contract_guard_after_provider() {
  local stage=$1
  if [[ $stage == plan ]]; then spec_matches_bound_member; else contracts_match_bound_member; fi
}

rebind_plan_contract() {
  local plan=$WORKTREE/$FEATURE_REL/plan.md new temp
  [[ -f $plan ]] || return 1
  new=$(sha256_of "$plan") || return 1
  [[ $new =~ ^[0-9a-f]{64}$ ]] || return 1
  temp=$(mktemp "$FLEET_DIR/.$SLUG.json.XXXXXX") || return 1
  if jq --arg plan "$new" --arg now "$(date -u +%Y-%m-%dT%H:%M:%SZ)" \
       '.plan_sha256 = $plan | .updated_at = $now' "$MEMBER_FILE" >"$temp" 2>/dev/null \
     && [[ -s $temp ]] && jq -e 'type == "object"' "$temp" >/dev/null 2>&1; then
    mv "$temp" "$MEMBER_FILE" && return 0
  fi
  rm -f "$temp"
  return 1
}

worktree_identity_matches || fail 'registered fleet member does not match canonical Git worktree registration'
contracts_match_bound_member || fail 'approved fleet contracts do not match the bound member'

CMUX_WORKSPACE_ID=$(jq -er '.cmux_workspace_id // ""' "$MEMBER_FILE" 2>/dev/null || printf '')
AUDIT_ENABLED=$(jq -er 'if (.audit // false) == true then "true" else "false" end' \
  "$MAIN_ROOT/.planning/power/config.json" 2>/dev/null || printf 'false')

# The adapter is selected from the runtime already validated against the member, and that
# runtime passed an allowlist, so this interpolation is not injectable.
ENGINE_ADAPTER=$SCRIPT_DIR/fleet-engine-$EXPECTED_RUNTIME.sh
require_regular_nosymlink "$ENGINE_ADAPTER" || fail "missing runtime adapter: $ENGINE_ADAPTER"
# shellcheck source=/dev/null
source "$ENGINE_ADAPTER"

# ---- runner lock ---------------------------------------------------------------------------

RUNNER_LOCK=$FLEET_DIR/.$SLUG.runner.lock
mkdir "$RUNNER_LOCK" 2>/dev/null || fail "fleet member is already running: $SLUG"
LOCK_HELD=true

PROVIDER_PID=
PROVIDER_PGID=
OWNERSHIP_UNRESOLVED=false
RECOVERING=false
STATUS_FINAL=false
CORRECTION_CYCLES=0
RESULT_VERDICT=NONE

# ---- resume ---------------------------------------------------------------------------------
#
# The lifecycle is single-shot: it always starts at plan, and a stage with nothing left to do
# produces no fresh artifact and is refused as work nobody did. So a member stopped mid-flight —
# an interrupted stage, a provider that answered with nothing — could only start over, discarding
# every stage that had already succeeded.
#
# Resuming re-runs the stage recorded as current and skips only the ones before it, restoring the
# correction-cycle count so the fix loop picks up where it stopped instead of at zero. It is never
# automatic: NEEDS_HUMAN means a human must look, and --resume is how they say they have.
RESUME_STAGE=
RESUME_IN_LOOP=false

if [[ $RESUME == true ]]; then
  require_regular_nosymlink "$STATUS_FILE" || fail 'cannot resume: this member has no runner status'
  jq -e --arg slug "$SLUG" 'type == "object" and .slug == $slug' "$STATUS_FILE" >/dev/null 2>&1 \
    || fail 'cannot resume: the runner status does not belong to this member'
  RESUME_STAGE=$(jq -er '.stage' "$STATUS_FILE" 2>/dev/null) \
    || fail 'cannot resume: the runner status has no stage'
  case $RESUME_STAGE in
    plan|execute|review|verify|execute-fix|review-fix) ;;
    *) fail "cannot resume: unknown stage $RESUME_STAGE" ;;
  esac
  CORRECTION_CYCLES=$(jq -er '.correction_cycles | select(type == "number" and . >= 0 and . <= 2)' \
    "$STATUS_FILE" 2>/dev/null) || fail 'cannot resume: correction cycle count is out of range'

  # A member sitting on execute-fix, review-fix, or a verify past the first one is inside the
  # correction loop. The recorded verdict cannot say so — write_status stamps NONE when a stage
  # starts — so the position is what proves it, and the loop is re-entered from that.
  case $RESUME_STAGE in
    execute-fix|review-fix) RESUME_IN_LOOP=true ;;
    verify) if [[ $CORRECTION_CYCLES -ge 1 ]]; then RESUME_IN_LOOP=true; fi ;;
  esac
  if [[ $RESUME_IN_LOOP == true ]]; then RESULT_VERDICT=REJECTED; fi

  # The recorded count already includes the cycle whose execute-fix is about to run again, and the
  # loop increments before running it. Without this, resuming would burn a cycle it already paid
  # for and reach the cap one correction early.
  if [[ $RESUME_STAGE == execute-fix ]]; then CORRECTION_CYCLES=$((CORRECTION_CYCLES - 1)); fi

  printf 'fleet-run: resuming %s at stage %s (cycles %s)\n' "$SLUG" "$RESUME_STAGE" "$CORRECTION_CYCLES" >&2
fi

# Consume the resume point once: the named stage runs, everything before it is skipped, and from
# then on every stage runs normally.
should_run() {
  local stage=$1
  if [[ -z $RESUME_STAGE ]]; then return 0; fi
  if [[ $stage == "$RESUME_STAGE" ]]; then RESUME_STAGE=; return 0; fi
  return 1
}
RESULT_MESSAGE=
CURRENT_RAW_TEMP=
CURRENT_LOG_TEMP=
CURRENT_RESULT_TEMP=

# The provider always leads its own process group, so the whole descendant group can be proven
# gone. argv: <cwd-or-empty> <provider> [provider-args...]
PROVIDER_LAUNCHER='import os,sys
directory = sys.argv[1]
if directory:
    os.chdir(directory)
os.setsid()
os.execvp(sys.argv[2], sys.argv[2:])'

provider_group_alive() {
  [[ -n $PROVIDER_PGID ]] && kill -0 -- "-$PROVIDER_PGID" 2>/dev/null
}

terminate_owned_provider() {
  [[ -n $PROVIDER_PGID ]] || return 0
  kill -TERM -- "-$PROVIDER_PGID" 2>/dev/null || true
  local attempt=0
  while provider_group_alive && (( attempt < 20 )); do sleep 0.1; attempt=$((attempt + 1)); done
  if provider_group_alive; then kill -KILL -- "-$PROVIDER_PGID" 2>/dev/null || true; fi
  [[ -z $PROVIDER_PID ]] || wait "$PROVIDER_PID" 2>/dev/null || true
  attempt=0
  while provider_group_alive && (( attempt < 20 )); do sleep 0.05; attempt=$((attempt + 1)); done
  if provider_group_alive; then
    printf 'fleet-run: owned provider process group did not terminate\n' >&2
    return 1
  fi
  PROVIDER_PID=
  PROVIDER_PGID=
  return 0
}

# An unresolved group is a deliberate signal, not a bug: the provider may have left dev servers
# or child containers alive, and advancing past that would corrupt the worktree.
ensure_provider_absent() {
  if terminate_owned_provider; then return 0; fi
  OWNERSHIP_UNRESOLVED=true
  printf 'fleet-run: provider ownership is unresolved; retaining runner lock for explicit recovery\n' >&2
  return 1
}

cleanup_owned() {
  set +e
  [[ $OWNERSHIP_UNRESOLVED == false ]] || return 1
  ensure_provider_absent || return 1
  rm -f "$CURRENT_RAW_TEMP" "$CURRENT_LOG_TEMP" "$CURRENT_RESULT_TEMP" 2>/dev/null
  if [[ $LOCK_HELD == true ]]; then
    if rmdir "$RUNNER_LOCK" 2>/dev/null; then LOCK_HELD=false
    else printf 'fleet-run: failed to release runner lock\n' >&2; return 1; fi
  fi
  return 0
}

on_exit() {
  local code=$?
  if [[ $RECOVERING == false && $STATUS_FINAL == false && $code -ne 0 ]]; then
    write_status "${CURRENT_STAGE:-plan}" NEEDS_HUMAN "runner exited unexpectedly (code $code)" NONE 2>/dev/null || true
  fi
  cleanup_owned
}
trap on_exit EXIT
trap 'RECOVERING=true; needs_human "${CURRENT_STAGE:-plan}" "interrupted"' HUP INT TERM

# ---- status ---------------------------------------------------------------------------------

write_status() {
  local stage=$1 status=$2 message=$3 verdict=$4 temp
  temp=$(mktemp "$(dirname "$STATUS_FILE")/.fleet-status.XXXXXX") || return 1
  jq -n --arg slug "$SLUG" --arg stage "$stage" --arg status "$status" \
        --arg message "$message" --arg verdict "$verdict" \
        --arg updated "$(date -u +%Y-%m-%dT%H:%M:%SZ)" \
        --argjson cycles "$CORRECTION_CYCLES" \
    '{slug:$slug,stage:$stage,status:$status,message:$message,verdict:$verdict,correction_cycles:$cycles,updated_at:$updated}' \
    >"$temp" || { rm -f "$temp"; return 1; }
  mv "$temp" "$STATUS_FILE" || { rm -f "$temp"; return 1; }

  # Human-visible state. Best-effort: losing a status line must never fail a stage.
  if [[ -n $CMUX_WORKSPACE_ID ]] && power_cmux_require >/dev/null 2>&1; then
    # tr, not ${status,,}: macOS ships bash 3.2, where that expansion is a bad substitution.
    power_cmux_status "$CMUX_WORKSPACE_ID" "$SLUG $stage $(printf '%s' "$status" | tr '[:upper:]' '[:lower:]')"
    case $status in
      NEEDS_HUMAN) power_cmux_color "$CMUX_WORKSPACE_ID" Red
                   power_cmux_notify "power-fleet: $SLUG" "needs human at $stage: $message" ;;
      OK) [[ $stage == verify && $verdict != REJECTED ]] && power_cmux_color "$CMUX_WORKSPACE_ID" Green ;;
    esac
  fi
  return 0
}

update_member_status() {
  local status=$1 temp
  require_regular_nosymlink "$MEMBER_FILE" || return 1
  temp=$(mktemp "$FLEET_DIR/.$SLUG.json.XXXXXX") || return 1
  jq --arg status "$status" --arg updated "$(date -u +%Y-%m-%dT%H:%M:%SZ)" \
    '.status = $status | .updated_at = $updated' "$MEMBER_FILE" >"$temp" \
    || { rm -f "$temp"; return 1; }
  mv "$temp" "$MEMBER_FILE" || { rm -f "$temp"; return 1; }
}

needs_human() {
  local stage=$1 message=$2 verdict=${3:-NONE}
  RECOVERING=true
  write_status "$stage" NEEDS_HUMAN "$message" "$verdict" || true
  update_member_status NEEDS_HUMAN || true
  STATUS_FINAL=true
  printf 'fleet-run: %s\n' "$message" >&2
  exit 1
}

validate_result() {
  local stage=$1 file=$2
  jq -e --arg stage "$stage" --argjson cap "$MESSAGE_MAX" '
    type == "object"
      and (keys_unsorted | sort) == ["message","stage","status","verdict"]
      and .stage == $stage
      and (.status | . == "OK" or . == "FAILED" or . == "NEEDS_HUMAN")
      and (.message | type == "string" and length > 0 and length <= $cap)
      and (.verdict | . == "NONE" or . == "APPROVED" or . == "CAVEATS" or . == "REJECTED")
  ' "$file" >/dev/null 2>&1
}

# Repair what carries no information; reject everything else.
#
# Only Codex is held to templates/fleet-result.schema.json natively. Claude and Hermes get the
# contract as prose, and real runs show prose is not reliably honoured: three stages were failed
# for a 507-, a 520-character message and for a `verdict` the model simply left out. Each miss
# costs a whole provider invocation and discards work that was already written and committed.
#
# Two deviations carry no information and are repaired here:
#
#   - a `message` past the schema's cap is trimmed. It is display text — the dashboard cuts it to
#     60 characters and nothing downstream parses it.
#   - a missing `verdict` outside the verify stage is set to "NONE", the only value the contract
#     allows there. On verify it stays required, because there the verdict *is* the result.
#
# Everything else stays strict. A result that is not one JSON object, names the wrong stage,
# invents a key, or carries an unknown status is still a failed stage.
normalize_result() {
  local stage=$1 file=$2 temp
  temp=$(mktemp "$RESULT_DIR/.normalize.XXXXXX") || return 1
  if jq --argjson cap "$MESSAGE_MAX" --arg stage "$stage" '
       (if (.message | type) == "string" and (.message | length) > $cap
        then .message = (.message[0:($cap - 1)] + "…")
        else . end)
       | (if $stage != "verify" and (has("verdict") | not)
          then .verdict = "NONE"
          else . end)
     ' "$file" >"$temp" 2>/dev/null && [[ -s $temp ]]; then
    mv "$temp" "$file" && return 0
  fi
  rm -f "$temp"
  return 1
}

# Did this stage actually do anything? Ask git, not the filesystem.
#
# An earlier version compared stat mtimes, which are second-granular: a stage that rewrote the
# same artifact within a second looked like a stage that produced nothing. Git sees the content.
#
# Both halves are needed. A stage that commits its own work as it goes (execute does, one commit
# per task) leaves a clean tree but a moved HEAD; a stage that only writes an artifact leaves
# HEAD alone but a dirty tree. Only doing neither is "well-formed JSON describing work nobody
# did", which is exactly what this catches.
stage_produced_work() {
  local before_head=$1 after_head dirty
  after_head=$(git -C "$WORKTREE" rev-parse HEAD 2>/dev/null) || return 1
  [[ $before_head != "$after_head" ]] && return 0
  dirty=$(git -C "$WORKTREE" status --porcelain -- "$FEATURE_REL" 2>/dev/null) || return 1
  [[ -n $dirty ]]
}

best_effort_stage_audit() {
  local stage=$1 status=$2
  [[ $AUDIT_ENABLED == true ]] || return 0
  "$SCRIPT_DIR/audit-log.sh" event fleet "$stage" fleet_stage \
    ".planning/power/fleet-status.json" "slug=$SLUG status=$status" >/dev/null 2>&1 \
    || printf 'warning: fleet_stage audit record failed\n' >&2
  return 0
}

# ---- stages -----------------------------------------------------------------------------------

CURRENT_STAGE=plan

build_prompt() {
  local stage=$1 capability arguments instruction skill_ref suffix
  case $stage in
    plan)        capability=plan;    arguments=;        instruction='decompose the approved specification into an executable plan' ;;
    execute)     capability=execute; arguments=;        instruction='execute the approved plan task by task, with review between tasks' ;;
    review)      capability=review;  arguments=;        instruction='review the implemented work against the approved contracts' ;;
    verify)      capability=verify;  arguments=;        instruction='adversarially verify the implementation and write a verdict' ;;
    execute-fix) capability=execute; arguments=' --fix'; instruction='execute only the bounded correction tasks from the rejected verification' ;;
    review-fix)  capability=review;  arguments=;        instruction='review only the current correction cycle and write its fix review artifact' ;;
    *) return 1 ;;
  esac
  skill_ref=$("power_engine_${EXPECTED_RUNTIME}_skill_ref" "$capability")
  suffix=$("power_engine_${EXPECTED_RUNTIME}_prompt_suffix" "$stage")
  printf 'AUTONOMOUS FLEET MODE. You are running unattended in an isolated worktree for feature "%s". ' "$SLUG"
  printf 'There is no human to ask, so every approval gate is pre-granted for the approved contracts in %s. ' "$FEATURE_REL"
  printf 'Do not ask questions, do not wait for confirmation, and never widen scope beyond those contracts. '
  printf 'Run %s%s and %s. ' "$skill_ref" "$arguments" "$instruction"
  printf 'If you cannot proceed, return status NEEDS_HUMAN with a one-line reason rather than guessing. '
  printf '%s' "$suffix"
}

run_stage() {
  local stage=$1
  CURRENT_STAGE=$stage
  local timestamp before_head provider_status result_file invalid_file raw_file

  worktree_identity_matches || needs_human "$stage" 'fleet member identity changed before the stage'
  contracts_match_bound_member || needs_human "$stage" 'approved fleet contracts changed before the stage'

  write_status "$stage" OK "starting $stage" NONE || needs_human "$stage" "cannot publish $stage status"
  update_member_status RUNNING || true

  timestamp=$(date -u +%Y%m%dT%H%M%SZ)
  result_file=$RESULT_DIR/$stage-$timestamp.json
  invalid_file=$RESULT_DIR/$stage-$timestamp.invalid.json
  raw_file=$RESULT_DIR/$stage-$timestamp.raw
  CURRENT_RAW_TEMP=$(mktemp "$RESULT_DIR/.$stage-raw.XXXXXX")
  CURRENT_LOG_TEMP=$(mktemp "$LOG_DIR/.$stage-log.XXXXXX")
  CURRENT_RESULT_TEMP=$(mktemp "$RESULT_DIR/.$stage-result.XXXXXX")

  before_head=$(git -C "$WORKTREE" rev-parse HEAD 2>/dev/null) \
    || needs_human "$stage" 'cannot read worktree HEAD'

  local prompt
  prompt=$(build_prompt "$stage") || needs_human "$stage" "unknown stage: $stage"

  "power_engine_${EXPECTED_RUNTIME}_stage_command" "$WORKTREE" "$SCHEMA" "$CURRENT_RESULT_TEMP" "$prompt"

  "$PYTHON3_BIN" -c "$PROVIDER_LAUNCHER" "$FLOW_ENGINE_CWD" "${FLOW_ENGINE_COMMAND[@]}" \
    >"$CURRENT_RAW_TEMP" 2>"$CURRENT_LOG_TEMP" &
  PROVIDER_PID=$!
  PROVIDER_PGID=$PROVIDER_PID

  if wait "$PROVIDER_PID"; then provider_status=0; else provider_status=$?; fi

  # Reaping a successful leader does not release ownership.
  if ! ensure_provider_absent; then
    RECOVERING=true
    trap - HUP INT TERM
    printf 'fleet-run: refusing to continue %s while provider ownership is unresolved\n' "$stage" >&2
    exit 1
  fi

  mv "$CURRENT_LOG_TEMP" "$LOG_DIR/$stage-$timestamp.log" 2>/dev/null || true
  CURRENT_LOG_TEMP=

  [[ $provider_status -eq 0 ]] || needs_human "$stage" "provider exited with status $provider_status during $stage"

  if [[ $FLOW_ENGINE_RESULT_FROM_STDOUT == true ]]; then
    "power_engine_${EXPECTED_RUNTIME}_publish_result" "$CURRENT_RAW_TEMP" "$CURRENT_RESULT_TEMP" || true
  fi

  worktree_identity_matches || needs_human "$stage" 'fleet member identity changed during provider execution'
  contract_guard_after_provider "$stage" || needs_human "$stage" 'approved fleet contracts changed during provider execution'

  [[ ! -s $CURRENT_RESULT_TEMP ]] || normalize_result "$stage" "$CURRENT_RESULT_TEMP" || true

  if [[ ! -s $CURRENT_RESULT_TEMP ]] || ! validate_result "$stage" "$CURRENT_RESULT_TEMP"; then
    mv "$CURRENT_RESULT_TEMP" "$invalid_file" 2>/dev/null || true
    CURRENT_RESULT_TEMP=
    # Keep the provider's own bytes, not only the parsed file.
    #
    # The parsed file is empty in exactly the case that most needs explaining — an answer nothing
    # could parse — so preserving it alone preserves nothing. A real execute-fix stage exited 0
    # with empty stdout and left a zero-byte artifact and no way to tell why.
    #
    # fleet-results/ is in the worktree gitignore, so this never rides along on a --merge, and the
    # reporting rules still forbid printing it: hand over the path, never the contents.
    mv "$CURRENT_RAW_TEMP" "$raw_file" 2>/dev/null || true
    CURRENT_RAW_TEMP=
    needs_human "$stage" "invalid structured result for $stage"
  fi

  RESULT_VERDICT=$(jq -er '.verdict' "$CURRENT_RESULT_TEMP")
  RESULT_MESSAGE=$(jq -er '.message' "$CURRENT_RESULT_TEMP")
  local result_status
  result_status=$(jq -er '.status' "$CURRENT_RESULT_TEMP")

  mv "$CURRENT_RESULT_TEMP" "$result_file" || needs_human "$stage" "cannot publish $stage result"
  CURRENT_RESULT_TEMP=
  rm -f "$CURRENT_RAW_TEMP"; CURRENT_RAW_TEMP=

  [[ $result_status == OK ]] || needs_human "$stage" "$RESULT_MESSAGE" "$RESULT_VERDICT"

  stage_produced_work "$before_head" \
    || needs_human "$stage" "missing fresh $stage artifact"

  if ! git -C "$WORKTREE" add -A || ! git -C "$WORKTREE" commit -m "chore(power-fleet): $SLUG $stage" >/dev/null 2>&1; then
    # An empty commit is not a failure: a review stage may legitimately change nothing.
    git -C "$WORKTREE" diff --cached --quiet 2>/dev/null \
      || needs_human "$stage" "failed to commit $stage changes"
  fi

  # Re-bind after the commit, never before: the bytes that bind the member must be the bytes that
  # landed on the branch, not whatever was in the worktree mid-stage.
  if [[ $stage == plan ]]; then
    rebind_plan_contract || needs_human "$stage" 'cannot re-bind the plan contract after the plan stage'
  fi

  write_status "$stage" OK "$RESULT_MESSAGE" "$RESULT_VERDICT" || needs_human "$stage" "cannot publish $stage status"
  best_effort_stage_audit "$stage" OK
}

# ---- lifecycle ----------------------------------------------------------------------------------

# A member resumed inside the correction loop skips the opening sequence entirely: its verify has
# already run and rejected, and re-running plan here would fail on the fresh-artifact check for a
# plan that is long finished.
if [[ $RESUME_IN_LOOP != true ]]; then
  if should_run plan;    then run_stage plan;    fi
  if should_run execute; then run_stage execute; fi
  if should_run review;  then run_stage review;  fi
  if should_run verify;  then run_stage verify;  fi
fi

while [[ $RESULT_VERDICT == REJECTED ]]; do
  # The cap is charged with the cycle, so a resume that lands mid-cycle does not pay for it twice.
  if should_run execute-fix; then
    if (( CORRECTION_CYCLES >= 2 )); then
      needs_human verify "verification rejected after two correction cycles: $RESULT_MESSAGE" REJECTED
    fi
    CORRECTION_CYCLES=$((CORRECTION_CYCLES + 1))
    run_stage execute-fix
  fi
  if should_run review-fix; then run_stage review-fix; fi
  if should_run verify;     then run_stage verify;     fi
done

write_status verify DONE "$RESULT_MESSAGE" "$RESULT_VERDICT" || true
update_member_status DONE || true
best_effort_stage_audit verify DONE
STATUS_FINAL=true

printf 'fleet-run: %s finished with verdict %s\n' "$SLUG" "$RESULT_VERDICT"
