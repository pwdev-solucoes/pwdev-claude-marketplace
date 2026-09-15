#!/usr/bin/env bash
set -Eeuo pipefail
# Interactive fleet vector. The unattended (headless) path runs the LOOP through
# scripts/loop-engine-hermes.py; this adapter only opens the member session for a human.
# Arguments: <worktree> <prompt-file> <plugin-root>

sdd_engine_hermes_interactive_command() {
  SDD_ENGINE_CWD=
  SDD_ENGINE_COMMAND=(hermes chat --query-file "$2" --cli --in "$1")
}
