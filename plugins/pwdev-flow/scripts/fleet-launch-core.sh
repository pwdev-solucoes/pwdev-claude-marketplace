#!/usr/bin/env bash
set -Eeuo pipefail
source "$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd -P)/fleet-common.sh"
flow_launch_core() {
  local runtime=${1:?runtime required}; shift
  flow_require_runtime "$runtime"
  [[ $# -ge 1 ]] || { printf 'launch command required\n' >&2; return 2; }
  FLOW_FLEET_RUNTIME=$runtime; export FLOW_FLEET_RUNTIME
  exec "$@"
}

# Usable both as a sourced helper and as the executable the claude launcher execs.
if [[ ${BASH_SOURCE[0]} == "$0" ]]; then flow_launch_core "$@"; fi
