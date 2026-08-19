#!/usr/bin/env bash
# Report fleet state by joining two independently validated sources: the central member record
# and the per-worktree runner status.
#
# This is a status line, not a transcript. It never prints absolute worktree paths, raw provider
# output, prompts, or result payloads.
set -Eeuo pipefail

SCRIPT_DIR=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd -P)

ONCE=false
[[ ${1:-} == --once ]] && ONCE=true

command -v jq >/dev/null 2>&1 || { printf 'fleet-dashboard: jq is required\n' >&2; exit 2; }

# Resolve the repository rather than trusting the ambient directory.
REPO_ROOT=$(git rev-parse --show-toplevel 2>/dev/null) || REPO_ROOT=$(pwd -P)
REPO_ROOT=$(cd "$REPO_ROOT" && pwd -P)
FLEET_DIR=$REPO_ROOT/.planning/power/fleet

truncate_message() {
  local m=$1
  printf '%s' "${m:0:60}"
}

render() {
  printf '%-16s %-7s %-7s %-11s %-9s %-6s %-6s %s\n' SLUG RUNTIME MODE STAGE STATUS APP DB MESSAGE
  printf '%s\n' '----------------------------------------------------------------------------------------'

  local found=false member filename values slug runtime mode app db branch worktree status stage rstatus verdict message

  shopt -s nullglob
  for member in "$FLEET_DIR"/*.json; do
    found=true
    filename=$(basename "$member" .json)

    # Validate the member, including that its filename agrees with its slug field.
    values=$(jq -er --arg filename "$filename" '
      if type == "object"
        and (.slug | type == "string" and length > 0) and .slug == $filename
        and (.runtime | . == "claude" or . == "codex" or . == "hermes")
        and (.app_port | type == "number" and floor == . and . >= 1 and . <= 65535)
        and (.db_port  | type == "number" and floor == . and . >= 1 and . <= 65535)
        and .app_port != .db_port
        and (.branch | type == "string" and length > 0)
        and (.worktree_path | type == "string" and length > 0)
        and (.status | . == "ACTIVE" or . == "RUNNING" or . == "DONE" or . == "NEEDS_HUMAN")
      then [.slug, .runtime, (.mode // "auto"), .app_port, .db_port, .branch, .worktree_path, .status] | @tsv
      else error("invalid member") end
    ' "$member" 2>/dev/null) || {
      printf '%-16s %-7s %-7s %-11s %-9s %-6s %-6s %s\n' "$filename" '?' '?' '?' MALFORMED '-' '-' 'member record is invalid'
      continue
    }

    IFS=$'\t' read -r slug runtime mode app db branch worktree status <<<"$values"

    stage='-'; rstatus=$status; verdict='-'; message=''
    if [[ -f $worktree/.planning/power/fleet-status.json ]]; then
      if ! IFS=$'\t' read -r stage rstatus verdict message < <(jq -er '
        if type == "object"
          and (.stage | . == "plan" or . == "execute" or . == "review" or . == "verify"
                        or . == "execute-fix" or . == "review-fix")
          and (.status | . == "OK" or . == "DONE" or . == "FAILED" or . == "NEEDS_HUMAN")
          and (.verdict | . == "NONE" or . == "APPROVED" or . == "CAVEATS" or . == "REJECTED")
          and (.message | type == "string")
        then [.stage, .status, .verdict, .message] | @tsv
        else error("invalid status") end
      ' "$worktree/.planning/power/fleet-status.json" 2>/dev/null); then
        stage='?'; rstatus='MALFORMED'; verdict='-'; message='runner status is invalid'
      fi
    elif [[ $mode == visual ]]; then
      message='driven by a human in a panel pane'
    else
      message='status unavailable'
    fi

    [[ $verdict == NONE || $verdict == '-' ]] || message="[$verdict] $message"

    printf '%-16s %-7s %-7s %-11s %-9s %-6s %-6s %s\n' \
      "$slug" "$runtime" "$mode" "$stage" "$rstatus" "$app" "$db" "$(truncate_message "$message")"
  done
  shopt -u nullglob

  [[ $found == true ]] || printf '(no fleet members)\n'
}

if [[ $ONCE == true ]]; then
  render
  exit 0
fi

cleanup_loop() { [[ -n ${SLEEP_PID:-} ]] && kill "$SLEEP_PID" 2>/dev/null; exit 0; }
trap cleanup_loop HUP INT TERM

while :; do
  printf '\033[2J\033[H'
  render
  printf '\n(refreshing every 5s; Ctrl-C to stop)\n'
  sleep 5 &
  SLEEP_PID=$!
  wait "$SLEEP_PID" 2>/dev/null || true
done
