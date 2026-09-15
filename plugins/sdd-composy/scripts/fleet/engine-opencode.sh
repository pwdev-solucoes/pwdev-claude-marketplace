#!/usr/bin/env bash
set -Eeuo pipefail
# Interactive fleet vector. The unattended (headless) path runs the LOOP through
# scripts/loop-engine-opencode.py; this adapter only opens the member session for a human.
# Arguments: <worktree> <prompt-file> <plugin-root>

sdd_engine_opencode_interactive_command() {
  local prompt
  prompt=$(<"$2")
  SDD_ENGINE_CWD=
  SDD_ENGINE_COMMAND=(opencode "$1" --prompt "$prompt")
}
