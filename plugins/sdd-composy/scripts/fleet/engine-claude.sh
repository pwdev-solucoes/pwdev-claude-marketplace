#!/usr/bin/env bash
set -Eeuo pipefail
# Interactive fleet vector. The unattended (headless) path runs the LOOP through
# scripts/loop-engine-claude.py; this adapter only opens the member session for a human.
# Arguments: <worktree> <prompt-file> <plugin-root>

sdd_engine_claude_interactive_command() {
  local prompt
  prompt=$(<"$2")
  SDD_ENGINE_CWD=
  SDD_ENGINE_COMMAND=(claude --add-dir "$1" --plugin-dir "$3" "$prompt")
}
