#!/usr/bin/env bash
set -Eeuo pipefail
# Interactive fleet vector. The unattended (headless) path runs the LOOP through
# scripts/loop-engine-codex.py; this adapter only opens the member session for a human.
# Arguments: <worktree> <prompt-file> <plugin-root>

sdd_engine_codex_interactive_command() {
  local prompt
  prompt=$(<"$2")
  SDD_ENGINE_CWD=
  SDD_ENGINE_COMMAND=(codex --cd "$1" --sandbox workspace-write "$prompt")
}
