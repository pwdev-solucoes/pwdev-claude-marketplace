#!/usr/bin/env bash
set -Eeuo pipefail
source "$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd -P)/fleet-common.sh"
flow_run_core() {
  local runtime=${1:?runtime required}; shift
  flow_require_runtime "$runtime"
  case "$runtime" in codex) source "$(dirname -- "${BASH_SOURCE[0]}")/fleet-engine-codex.sh"; flow_engine_codex "$@";; claude) source "$(dirname -- "${BASH_SOURCE[0]}")/fleet-engine-claude.sh"; flow_engine_claude "$@";; esac
}
