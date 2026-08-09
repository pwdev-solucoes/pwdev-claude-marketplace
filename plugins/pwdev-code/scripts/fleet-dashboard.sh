#!/bin/bash
# fleet-dashboard.sh — live status table for /pwdev-code:fleet. Runs as the
# "dashboard" tmux window (one per fleet session), or once via --once for
# /pwdev-code:fleet --status.
#
# Reads:
#   .planning/fleet/*.json          (main repo — one per active slug: ports, worktree, branch)
#   <worktree>/.planning/fleet-status.json  (per worktree — stage/status written by fleet-run.sh)
#
# Usage:
#   fleet-dashboard.sh          # loops, refreshing every 5s (tmux window)
#   fleet-dashboard.sh --once   # print the table once and exit
set -Eeuo pipefail

TOPLEVEL="$(git rev-parse --show-toplevel 2>/dev/null)" || { echo "❌ not inside a git repository" >&2; exit 2; }
cd "$TOPLEVEL"
command -v jq >/dev/null 2>&1 || { echo "❌ jq is required" >&2; exit 2; }

render() {
  echo "pwdev-code fleet — $(date -u +%Y-%m-%dT%H:%M:%SZ)"
  echo
  printf '%-16s %-10s %-16s %-10s %-9s %-8s %s\n' "SLUG" "APP:DB" "STAGE" "STATUS" "PORT-IDX" "BRANCH" "MESSAGE"
  printf '%-16s %-10s %-16s %-10s %-9s %-8s %s\n' "----" "------" "-----" "------" "--------" "------" "-------"

  shopt -s nullglob
  local found=0
  for f in .planning/fleet/*.json; do
    [ -f "$f" ] || continue
    found=1
    local slug worktree app_port db_port branch
    slug=$(jq -r '.slug' "$f")
    worktree=$(jq -r '.worktree_path' "$f")
    app_port=$(jq -r '.app_port' "$f")
    db_port=$(jq -r '.db_port' "$f")
    branch=$(jq -r '.branch' "$f")

    local stage="—" status="STARTING" message="—"
    local status_file="${worktree}/.planning/fleet-status.json"
    if [ -f "$status_file" ]; then
      stage=$(jq -r '.stage // "—"' "$status_file" 2>/dev/null || echo "—")
      status=$(jq -r '.status // "—"' "$status_file" 2>/dev/null || echo "—")
      message=$(jq -r '.message // "—"' "$status_file" 2>/dev/null || echo "—")
    elif [ ! -d "$worktree" ]; then
      status="MISSING"
      message="worktree not found — see .planning/fleet/${slug}.json"
    fi

    printf '%-16s %-10s %-16s %-10s %-9s %-8s %s\n' \
      "$slug" "${app_port}:${db_port}" "$stage" "$status" "-" "$branch" "$(printf '%.60s' "$message")"
  done

  if [ "$found" -eq 0 ]; then
    echo "(no active fleet members — run /pwdev-code:fleet <phase-slug> to start one)"
  fi
}

if [ "${1:-}" = "--once" ]; then
  render
  exit 0
fi

trap 'exit 0' INT TERM
while true; do
  clear
  render
  echo
  echo "(refreshing every 5s — Ctrl-C to stop watching, fleet keeps running)"
  sleep 5
done
