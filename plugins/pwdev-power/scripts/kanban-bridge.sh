#!/usr/bin/env bash
# Bridge approved phases onto the Hermes Kanban board, and mirror the board back into cmux.
#
# This route does not duplicate orchestration: the board dispatches, and this script translates
# in one direction and reflects in the other. What changes owner is documented in
# references/kanban.md — read it before using this.
set -Eeuo pipefail

SCRIPT_DIR=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd -P)
# shellcheck source=cmux-common.sh
source "$SCRIPT_DIR/cmux-common.sh"

fail() { printf 'kanban-bridge: %s\n' "$*" >&2; exit 2; }

usage() {
  cat >&2 <<'USAGE'
usage:
  kanban-bridge.sh preview <slug...>     show what would be created; creates nothing
  kanban-bridge.sh create  <slug...>     create one card per approved phase
  kanban-bridge.sh mirror                reflect board state into cmux
  kanban-bridge.sh status                print board state for these phases
USAGE
  exit 2
}

[[ $# -ge 1 ]] || usage
ACTION=$1; shift

command -v jq >/dev/null 2>&1 || fail 'jq is required'
command -v hermes >/dev/null 2>&1 || fail 'the hermes CLI is required for the Kanban route'

REPO_ROOT=$(git rev-parse --show-toplevel 2>/dev/null) || fail 'not inside a Git repository'
REPO_ROOT=$(cd "$REPO_ROOT" && pwd -P)
cd "$REPO_ROOT"

REPO_PARENT=$(cd "$REPO_ROOT/.." && pwd -P)
REPO_NAME=$(basename "$REPO_ROOT")
FLEET_DIR=$REPO_ROOT/.planning/power/fleet

sha256_of() {
  if command -v shasum >/dev/null 2>&1; then shasum -a 256 "$1" | awk '{print $1}'
  elif command -v sha256sum >/dev/null 2>&1; then sha256sum "$1" | awk '{print $1}'
  else openssl dgst -sha256 "$1" | awk '{print $NF}'; fi
}

# Same entry gate as a native launch. The board has no opinion about approval, so this is the
# only thing standing between an unapproved spec and an unattended worker.
validate_slug() {
  local slug=$1 dir=$REPO_ROOT/.planning/power/features/$slug
  [[ $slug =~ ^[a-z0-9][a-z0-9-]*$ ]] || fail "invalid slug: $slug"
  [[ -f $dir/spec.md ]] || fail "no spec for $slug"
  [[ -f $dir/plan.md ]] || fail "no plan for $slug"
  local n
  n=$(grep -c '^Status: APPROVED[[:space:]]*$' "$dir/spec.md" || true)
  [[ $n -eq 1 ]] || fail "spec for $slug must carry exactly one 'Status: APPROVED' field (found $n)"
}

card_args() {
  local slug=$1 dir=$REPO_ROOT/.planning/power/features/$slug spec_sha7
  spec_sha7=$(sha256_of "$dir/spec.md" | cut -c1-7)
  # The idempotency key carries the spec hash so relaunching the same approved phase returns
  # the same card, while an edited spec produces a genuinely new one.
  printf '%s\0' \
    "power-fleet: $slug" \
    --workspace "worktree:$REPO_PARENT/$REPO_NAME-fleet-$slug" \
    --branch "power-fleet/$slug" \
    --skill power-execute \
    --idempotency-key "power-$slug-$spec_sha7" \
    --max-retries 2 \
    --max-runtime 2h \
    --created-by pwdev-power \
    --json
}

render_args() {
  local slug=$1
  printf 'hermes kanban create'
  while IFS= read -r -d '' arg; do printf ' %q' "$arg"; done < <(card_args "$slug")
  printf '\n'
}

case $ACTION in
  preview)
    [[ $# -ge 1 ]] || usage
    for slug in "$@"; do validate_slug "$slug"; done
    printf 'These cards would be created. Nothing has been created yet.\n\n'
    for slug in "$@"; do render_args "$slug"; done
    printf '\nThen: hermes kanban dispatch --dry-run --json\n'
    ;;

  create)
    [[ $# -ge 1 ]] || usage
    for slug in "$@"; do validate_slug "$slug"; done
    mkdir -p "$FLEET_DIR"
    for slug in "$@"; do
      args=()
      while IFS= read -r -d '' arg; do args+=("$arg"); done < <(card_args "$slug")
      out=$(hermes kanban create "${args[@]}") || fail "cannot create the card for $slug"
      task_id=$(printf '%s' "$out" | jq -er '(.id // .task_id // .task.id) | tostring' 2>/dev/null) \
        || fail "hermes did not return a task id for $slug"
      printf 'kanban-bridge: %s -> task %s\n' "$slug" "$task_id"

      # Record the task id next to the contract hashes. The hashes stay ours on this route:
      # the board cannot tell an edited spec from an approved one.
      member=$FLEET_DIR/$slug.json
      if [[ -f $member ]]; then
        tmp=$(mktemp "$FLEET_DIR/.$slug.json.XXXXXX")
        jq --arg id "$task_id" '.kanban_task_id = $id' "$member" >"$tmp" && mv "$tmp" "$member"
      else
        dir=$REPO_ROOT/.planning/power/features/$slug
        tmp=$(mktemp "$FLEET_DIR/.$slug.json.XXXXXX")
        jq -n --arg slug "$slug" --arg id "$task_id" \
              --arg spec "$(sha256_of "$dir/spec.md")" --arg plan "$(sha256_of "$dir/plan.md")" \
              --arg wt "$REPO_PARENT/$REPO_NAME-fleet-$slug" \
              --arg created "$(date -u +%Y-%m-%dT%H:%M:%SZ)" \
          '{schema_version:1,slug:$slug,runtime:"hermes",route:"kanban",
            branch:("power-fleet/"+$slug),worktree_path:$wt,
            cmux_workspace_id:"",spec_sha256:$spec,plan_sha256:$plan,
            kanban_task_id:$id,status:"ACTIVE",created_at:$created,updated_at:$created}' \
          >"$tmp" && mv "$tmp" "$member"
      fi
    done
    printf '\nNothing runs until you dispatch. Preview first:\n'
    printf '  hermes kanban dispatch --dry-run --json\n'
    ;;

  status)
    hermes kanban list --json | jq -r '
      (.tasks // .) | map(select((.title // "") | startswith("power-fleet:")))
      | if length == 0 then "(no power-fleet cards)"
        else .[] | "\(.id)\t\(.status)\t\(.title)" end'
    ;;

  mirror)
    power_cmux_require || fail 'cmux is not reachable'
    shopt -s nullglob
    for member in "$FLEET_DIR"/*.json; do
      task_id=$(jq -er '.kanban_task_id // empty' "$member" 2>/dev/null) || continue
      [[ -n $task_id ]] || continue
      slug=$(jq -er '.slug' "$member")
      workspace=$(jq -er '.cmux_workspace_id // ""' "$member")
      [[ -n $workspace ]] || continue

      card=$(hermes kanban show "$task_id" --json 2>/dev/null) || continue
      state=$(printf '%s' "$card" | jq -er '(.status // .state // "unknown")')

      case $state in
        running)          power_cmux_status "$workspace" "$slug running" ;;
        done)             power_cmux_status "$workspace" "$slug done"; power_cmux_color "$workspace" Green ;;
        review|blocked)   power_cmux_status "$workspace" "$slug $state"; power_cmux_color "$workspace" Red
                          power_cmux_notify "power-fleet: $slug" "card is $state and needs a human" ;;
        *)                power_cmux_status "$workspace" "$slug $state" ;;
      esac
      printf 'kanban-bridge: %s is %s\n' "$slug" "$state"
    done
    shopt -u nullglob
    ;;

  *) usage ;;
esac
