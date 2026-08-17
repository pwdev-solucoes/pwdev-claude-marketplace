#!/usr/bin/env bash
# Render central fleet bookkeeping with current per-worktree stage state.
set -Eeuo pipefail

usage() { printf 'Usage: %s [--once]\n' "${0##*/}" >&2; exit 2; }
[[ $# -eq 0 || ( $# -eq 1 && $1 == --once ) ]] || usage
ONCE=false; [[ $# -eq 1 ]] && ONCE=true
command -v jq >/dev/null 2>&1 || { printf 'fleet-dashboard: required binary unavailable: jq\n' >&2; exit 2; }
# Resolve the repository rather than trusting the ambient directory: the tmux
# session name is a global constant, so a session created earlier from another
# repository would otherwise keep reporting that repository's fleet, and running
# from a subdirectory would silently render an empty table.
if command -v git >/dev/null 2>&1 && REPO_ROOT=$(git rev-parse --show-toplevel 2>/dev/null) && [[ -n $REPO_ROOT ]]; then
  REPO_ROOT=$(cd -- "$REPO_ROOT" && pwd -P)
else
  REPO_ROOT=$(pwd -P)
fi
FLEET_DIR=$REPO_ROOT/.planning/flow/fleet

print_row() {
  local slug=$1 ports=$2 stage=$3 status=$4 branch=$5 updated=$6 message=$7
  message=${message:0:60}
  printf '%-18s %-13s %-13s %-13s %-24s %-21s %s\n' \
    "$slug" "$ports" "$stage" "$status" "$branch" "$updated" "$message"
}

render_dashboard() {
  local member filename values slug app_port db_port branch worktree member_status member_updated
  local status_file state_values stage status updated message
  if [[ $ONCE == false ]]; then printf '\033[2J\033[H'; fi
  printf '%-18s %-13s %-13s %-13s %-24s %-21s %s\n' SLUG APP:DB STAGE STATUS BRANCH UPDATED MESSAGE
  shopt -s nullglob
  for member in "$FLEET_DIR"/*.json; do
    filename=${member##*/}; filename=${filename%.json}
    if ! values=$(jq -er --arg filename "$filename" '
      if type == "object" and
        (.slug | type == "string" and length > 0) and .slug == $filename and
        (.app_port | type == "number" and floor == . and . >= 1 and . <= 65535) and
        (.db_port | type == "number" and floor == . and . >= 1 and . <= 65535) and .app_port != .db_port and
        (.branch | type == "string" and length > 0) and
        (.worktree_path | type == "string" and length > 0) and
        (.status == "ACTIVE" or .status == "RUNNING" or .status == "DONE" or .status == "NEEDS_HUMAN") and
        (.updated_at | type == "string" and length > 0)
      then [.slug,.app_port,.db_port,.branch,.worktree_path,.status,.updated_at] | @tsv
      else error("invalid member") end
    ' "$member" 2>/dev/null); then
      print_row "$filename" UNKNOWN UNKNOWN MALFORMED UNKNOWN UNKNOWN 'malformed member'
      continue
    fi
    IFS=$'\t' read -r slug app_port db_port branch worktree member_status member_updated <<<"$values"
    status_file=$worktree/.planning/flow/fleet-status.json
    if [[ ! -f $status_file ]]; then
      print_row "$slug" "$app_port:$db_port" UNKNOWN UNKNOWN "$branch" "$member_updated" 'status unavailable'
      continue
    fi
    if ! state_values=$(jq -er --arg slug "$slug" '
      if type == "object" and .slug == $slug and
        (.stage == "plan" or .stage == "execute" or .stage == "review" or .stage == "verify" or .stage == "execute-fix" or .stage == "review-fix") and
        (.status == "RUNNING" or .status == "ACTIVE" or .status == "DONE" or .status == "NEEDS_HUMAN") and
        (.updated_at | type == "string" and length > 0) and
        (.message | type == "string" and length > 0) and
        (.verdict == "NONE" or .verdict == "APPROVED" or .verdict == "CAVEATS" or .verdict == "REJECTED")
      then [.stage,.status,.updated_at,.message] | @tsv
      else error("invalid status") end
    ' "$status_file" 2>/dev/null); then
      print_row "$slug" "$app_port:$db_port" UNKNOWN MALFORMED "$branch" "$member_updated" 'malformed status'
      continue
    fi
    IFS=$'\t' read -r stage status updated message <<<"$state_values"
    print_row "$slug" "$app_port:$db_port" "$stage" "$status" "$branch" "$updated" "$message"
  done
  shopt -u nullglob
}

if [[ $ONCE == true ]]; then render_dashboard; exit 0; fi
SLEEP_PID=
stop_dashboard() {
  trap - INT TERM
  if [[ -n $SLEEP_PID ]]; then kill -TERM "$SLEEP_PID" 2>/dev/null || true; wait "$SLEEP_PID" 2>/dev/null || true; fi
  exit 0
}
trap stop_dashboard INT TERM
while :; do
  render_dashboard
  sleep 5 & SLEEP_PID=$!
  if wait "$SLEEP_PID"; then :; fi
  SLEEP_PID=
done
