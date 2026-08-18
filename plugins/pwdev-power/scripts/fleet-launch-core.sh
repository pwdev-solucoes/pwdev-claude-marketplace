#!/usr/bin/env bash
# Pin the fleet runtime identity, then hand over.
#
# This is the only place that exports the runtime. Everything downstream reads it and refuses
# to disagree with it. Usable both as a sourced function and as an executable.
set -Eeuo pipefail

SCRIPT_DIR=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd -P)
# shellcheck source=fleet-common.sh
source "$SCRIPT_DIR/fleet-common.sh"

power_launch_core() {
  local runtime=${1:?runtime required}; shift
  power_require_runtime "$runtime"
  [[ $# -ge 1 ]] || { printf 'launch command required\n' >&2; return 2; }
  POWER_FLEET_RUNTIME=$runtime
  export POWER_FLEET_RUNTIME
  exec "$@"
}

if [[ ${BASH_SOURCE[0]} == "$0" ]]; then
  power_launch_core "$@"
fi
