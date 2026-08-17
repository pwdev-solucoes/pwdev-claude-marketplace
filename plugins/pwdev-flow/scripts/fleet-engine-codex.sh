#!/usr/bin/env bash
set -Eeuo pipefail
# The Codex privileged vector is intentionally isolated in this adapter.
# Nothing outside this file may construct a Codex command or add a permission flag.

# --- Autonomous stage interface used by fleet-run.sh -------------------------
# Every function below is contract with the shared runner. The runner owns
# process groups, locks, state and commits; the adapter owns only the vector.
# There is exactly one privileged vector per runtime, built in one place.

# How this runtime is asked to invoke a Flow capability inside the prompt.
flow_engine_codex_skill_ref() { printf '$flow-%s' "$1"; }

# Codex enforces the result shape natively through --output-schema, so the
# prompt only has to name the stage.
flow_engine_codex_prompt_suffix() {
  printf 'Your final message must match the provided schema with stage set to %s.' "$1"
}

# Sets FLOW_ENGINE_COMMAND (argv array), FLOW_ENGINE_CWD (empty keeps the
# runner's directory) and FLOW_ENGINE_RESULT_FROM_STDOUT.
# Arguments: <worktree> <schema> <result-file> <prompt>
flow_engine_codex_stage_command() {
  FLOW_ENGINE_CWD=
  FLOW_ENGINE_RESULT_FROM_STDOUT=false
  FLOW_ENGINE_COMMAND=(codex exec --dangerously-bypass-approvals-and-sandbox --ephemeral \
    --cd "$1" --output-schema "$2" --output-last-message "$3" "$4")
}

# Codex writes the structured result itself; nothing to publish.
# Arguments: <raw-stdout-file> <result-file>
flow_engine_codex_publish_result() { return 0; }
