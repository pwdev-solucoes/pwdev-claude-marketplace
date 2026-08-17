#!/usr/bin/env bash
set -Eeuo pipefail
SCRIPT_DIR=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd -P)
fail() { printf 'claude-fleet-run: %s\n' "$*" >&2; exit 2; }
[[ $# -eq 2 || $# -eq 3 ]] || { printf 'Usage: %s <lowercase-slug> <worktree-path> [danger-full-access]\n' "${0##*/}" >&2; exit 2; }
SLUG=$1; WORKTREE=$2
[[ $SLUG =~ ^[a-z0-9][a-z0-9-]*$ ]] || fail "invalid slug: $SLUG"
if [[ $# -eq 3 ]]; then [[ $3 == danger-full-access ]] || fail 'permission mode must be danger-full-access'; fi
FLOW_FLEET_RUNTIME=claude; export FLOW_FLEET_RUNTIME
cd -- "$WORKTREE" || fail 'worktree path is unavailable'
exec "$SCRIPT_DIR/fleet-run-core.sh" claude "Execute the approved PWDEV Flow phase '$SLUG' in this registered worktree."
