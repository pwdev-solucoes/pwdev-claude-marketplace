#!/usr/bin/env bash
# Claude pane entry point. It only pins the runtime identity; the whole
# autonomous lifecycle — locks, contract hashes, process-group ownership,
# result validation, per-stage commits and the correction cap — belongs to the
# shared fleet-run.sh, exactly as it does for Codex.
set -Eeuo pipefail
SCRIPT_DIR=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd -P)
fail() { printf 'claude-fleet-run: %s\n' "$*" >&2; exit 2; }
[[ $# -eq 2 || $# -eq 3 ]] || { printf 'Usage: %s <lowercase-slug> <worktree-path> [danger-full-access]\n' "${0##*/}" >&2; exit 2; }
SLUG=$1
[[ $SLUG =~ ^[a-z0-9][a-z0-9-]*$ && $SLUG == *[a-z]* && $SLUG != dashboard ]] || fail "invalid slug: $SLUG"
if [[ $# -eq 3 ]]; then [[ $3 == danger-full-access ]] || fail 'permission mode must be danger-full-access'; fi
FLOW_FLEET_RUNTIME=claude; export FLOW_FLEET_RUNTIME
exec "$SCRIPT_DIR/fleet-run.sh" "$@"
