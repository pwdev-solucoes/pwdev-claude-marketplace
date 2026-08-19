#!/usr/bin/env bash
# Run a fleet member's autonomous lifecycle on the hermes runtime.
#
# This wrapper only pins the runtime identity. The whole lifecycle — locks, contract hashes,
# process-group ownership, result validation, per-stage commits and the correction cap —
# belongs to the shared fleet-run.sh, exactly as it does for every other runtime.
set -Eeuo pipefail
SCRIPT_DIR=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd -P)

fail() { printf 'hermes-fleet-run: %s\n' "$*" >&2; exit 2; }

[[ $# -ge 2 && $# -le 4 ]] \
  || fail 'usage: hermes-fleet-run.sh <slug> <worktree> [permission-mode] [--resume]'
SLUG=$1
[[ $SLUG =~ ^[a-z0-9][a-z0-9-]*$ && $SLUG == *[a-z]* && $SLUG != dashboard ]] || fail "invalid slug: $SLUG"
for arg in "${@:3}"; do
  case $arg in
    danger-full-access|--resume) ;;
    *) fail "unexpected argument: $arg" ;;
  esac
done

POWER_FLEET_RUNTIME=hermes
export POWER_FLEET_RUNTIME
exec "$SCRIPT_DIR/fleet-run.sh" "$@"
