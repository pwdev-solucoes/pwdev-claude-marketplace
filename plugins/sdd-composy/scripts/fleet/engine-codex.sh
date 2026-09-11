#!/usr/bin/env bash
set -Eeuo pipefail
# The Codex privileged vector is intentionally isolated in this adapter.
# Nothing outside this file may construct a Codex command or add a permission flag.

# --- Autonomous stage interface used by sdd-fleet-run.sh -------------------------
# Every function below is contract with the shared runner. The runner owns
# process groups, locks, state and commits; the adapter owns only the vector.
# There is exactly one privileged vector per runtime, built in one place.

# How this runtime is asked to invoke a Flow capability inside the prompt.
sdd_engine_codex_skill_ref() { printf '\$sdd-composy:%s' "$1"; }

# Codex enforces the result shape natively through --output-schema, so the
# prompt only has to name the stage.
sdd_engine_codex_prompt_suffix() {
  printf 'Your final message must match the provided schema with stage set to %s.' "$1"
}

# Sets FLOW_ENGINE_COMMAND (argv array), FLOW_ENGINE_CWD (empty keeps the
# runner's directory) and FLOW_ENGINE_RESULT_FROM_STDOUT.
# Arguments: <worktree> <schema> <result-file> <prompt>
sdd_engine_codex_stage_command() {
  FLOW_ENGINE_CWD=; SDD_ENGINE_CWD=
  FLOW_ENGINE_RESULT_FROM_STDOUT=false; SDD_ENGINE_RESULT_FROM_STDOUT=false
  local permission=(--sandbox workspace-write)
  [[ ${SDD_FLEET_PERMISSION_MODE:-safe} != danger-full-access ]] || permission=(--dangerously-bypass-approvals-and-sandbox)
  FLOW_ENGINE_COMMAND=(codex exec "${permission[@]}" --ephemeral \
    --cd "$1" --output-schema "$2" --output-last-message "$3" "$4")
  SDD_ENGINE_COMMAND=("${FLOW_ENGINE_COMMAND[@]}")
}

sdd_engine_codex_interactive_command() {
  local prompt
  prompt=$(<"$2")
  SDD_ENGINE_CWD=
  SDD_ENGINE_COMMAND=(codex --cd "$1" --sandbox workspace-write "$prompt")
}

# Codex writes the structured result itself; nothing to publish.
# Arguments: <raw-stdout-file> <result-file>
sdd_engine_codex_publish_result() { return 0; }
