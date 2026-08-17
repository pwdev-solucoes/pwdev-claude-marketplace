#!/usr/bin/env bash
set -Eeuo pipefail
SCRIPT_DIR=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd -P)
[[ $# -ge 2 ]] || { printf 'Usage: %s <slug> <worktree-path> [permission-mode]\n' "${0##*/}" >&2; exit 2; }
SLUG=$1; WORKTREE=$2; shift 2
FLOW_FLEET_RUNTIME=claude; export FLOW_FLEET_RUNTIME
cd -- "$WORKTREE"
exec "$SCRIPT_DIR/fleet-run-core.sh" claude "Execute the approved PWDEV Flow phase '$SLUG' in this registered worktree."
