#!/usr/bin/env bash
set -Eeuo pipefail
source "$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd -P)/fleet-common.sh"
flow_run_core() {
  local runtime=${1:?runtime required}; shift
  flow_require_runtime "$runtime"
  [[ $# -ge 1 ]] || { printf 'stage prompt required\n' >&2; return 2; }
  local engine_dir; engine_dir=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd -P)
  case "$runtime" in codex) source "$engine_dir/fleet-engine-codex.sh"; flow_engine_codex "$@";; claude) source "$engine_dir/fleet-engine-claude.sh"; flow_engine_claude "$@";; esac
}

# Usable both as a sourced helper and as the executable the claude runner execs.
if [[ ${BASH_SOURCE[0]} == "$0" ]]; then flow_run_core "$@"; fi
