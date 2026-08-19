#!/usr/bin/env bash
# Launch a visual fleet panel on the claude runtime.
#
# This wrapper only pins the runtime identity. Provisioning, layout, and the binding of members to
# surfaces belong to the shared fleet-panel-up.sh, identically for every runtime.
set -Eeuo pipefail
SCRIPT_DIR=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd -P)
exec "$SCRIPT_DIR/fleet-launch-core.sh" claude "$SCRIPT_DIR/fleet-panel-up.sh" "$@"
