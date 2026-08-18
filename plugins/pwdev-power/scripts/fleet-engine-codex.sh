#!/usr/bin/env bash
# The Codex privileged vector. This file, and only this file, may name the Codex provider or
# add a Codex permission flag.

power_engine_codex_skill_ref() { printf '$power-%s' "$1"; }

# Codex enforces the schema natively, so the prompt only has to name the stage.
power_engine_codex_prompt_suffix() {
  printf 'Your final message must match the provided schema with stage set to %s.' "$1"
}

power_engine_codex_stage_command() {
  # $1 worktree  $2 schema  $3 result-file  $4 prompt
  FLOW_ENGINE_CWD=                       # --cd does the work; the runner stays put
  FLOW_ENGINE_RESULT_FROM_STDOUT=false   # codex writes the result file itself
  FLOW_ENGINE_COMMAND=(codex exec --dangerously-bypass-approvals-and-sandbox --ephemeral \
    --cd "$1" --output-schema "$2" --output-last-message "$3" "$4")
}

power_engine_codex_publish_result() { return 0; }
