#!/usr/bin/env bash
# Run a fleet member's autonomous lifecycle on the codex runtime.
#
# This wrapper only pins the runtime identity. The whole lifecycle — locks, contract hashes,
# process-group ownership, result validation, per-stage commits and the correction cap —
# belongs to the shared fleet-run.sh, exactly as it does for every other runtime.
set -Eeuo pipefail
SCRIPT_DIR=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd -P)

fail() { printf 'codex-fleet-run: %s\n' "$*" >&2; exit 2; }

[[ $# -eq 2 || $# -eq 3 ]] || fail 'usage: codex-fleet-run.sh <slug> <worktree> [permission-mode]'
SLUG=$1
[[ $SLUG =~ ^[a-z0-9][a-z0-9-]*$ && $SLUG == *[a-z]* && $SLUG != dashboard ]] || fail "invalid slug: $SLUG"
if [[ $# -eq 3 ]]; then
  [[ $3 == danger-full-access ]] || fail 'permission mode must be danger-full-access'
fi

POWER_FLEET_RUNTIME=codex
export POWER_FLEET_RUNTIME
exec "$SCRIPT_DIR/fleet-run.sh" "$@"
