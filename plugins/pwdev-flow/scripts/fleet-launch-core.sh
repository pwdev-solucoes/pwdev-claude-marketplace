#!/usr/bin/env bash
set -Eeuo pipefail
source "$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd -P)/fleet-common.sh"
flow_launch_core() {
  local runtime=${1:?runtime required}; shift
  flow_require_runtime "$runtime"
  FLOW_FLEET_RUNTIME=$runtime; export FLOW_FLEET_RUNTIME
  exec "$@"
}
