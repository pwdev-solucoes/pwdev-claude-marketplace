#!/usr/bin/env bash
set -Eeuo pipefail
# Native Claude vector; no Codex flags or shell interpolation are accepted.
flow_engine_claude() {
  local prompt=$1; shift
  command -v claude >/dev/null 2>&1 || { printf 'claude CLI is required\n' >&2; return 127; }
  claude -p --dangerously-skip-permissions --no-session-persistence --output-format json "$@" "$prompt"
}
