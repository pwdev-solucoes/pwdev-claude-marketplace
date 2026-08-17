#!/usr/bin/env bash
set -Eeuo pipefail
SCRIPT_DIR=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd -P)
exec "$SCRIPT_DIR/fleet-launch-core.sh" claude "$SCRIPT_DIR/fleet-up.sh" "$@"
