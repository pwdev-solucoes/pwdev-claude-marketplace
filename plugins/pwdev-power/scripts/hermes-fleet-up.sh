#!/usr/bin/env bash
# Launch a fleet member on the hermes runtime.
#
# This wrapper only pins the runtime identity. Provisioning — locks, ports, worktree, compose,
# cmux workspace, contract hashes — belongs to the shared fleet-up.sh, identically for every
# runtime.
set -Eeuo pipefail
SCRIPT_DIR=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd -P)
exec "$SCRIPT_DIR/fleet-launch-core.sh" hermes "$SCRIPT_DIR/fleet-up.sh" "$@"
