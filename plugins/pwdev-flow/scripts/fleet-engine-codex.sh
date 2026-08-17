#!/usr/bin/env bash
set -Eeuo pipefail
# The Codex privileged vector is intentionally isolated in this adapter.
flow_engine_codex() {
  local prompt=$1; shift
  codex exec --sandbox danger-full-access -c approval_policy=never --add-dir "$PWD" "$@" "$prompt"
}
