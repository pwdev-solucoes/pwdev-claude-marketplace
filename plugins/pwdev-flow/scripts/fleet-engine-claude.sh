#!/usr/bin/env bash
set -Eeuo pipefail
# Native Claude vector; no Codex flags or shell interpolation are accepted.
# Nothing outside this file may construct a Claude command or add a permission flag.

# --- Autonomous stage interface used by fleet-run.sh -------------------------
# Every function below is contract with the shared runner. The runner owns
# process groups, locks, state and commits; the adapter owns only the vector.
# There is exactly one privileged vector per runtime, built in one place.

# How this runtime is asked to invoke a Flow capability inside the prompt.
flow_engine_claude_skill_ref() { printf '/pwdev-flow:%s' "$1"; }

# Claude Code has no --output-schema equivalent, so the result contract has to
# travel inside the prompt. Keep this in sync with templates/fleet-result.schema.json
# and with validate_result in fleet-run.sh.
flow_engine_claude_prompt_suffix() {
  local stage=$1 verdict
  if [[ $stage == verify ]]; then verdict='"APPROVED", "CAVEATS" or "REJECTED"'; else verdict='"NONE"'; fi
  printf '%s ' \
    'Your final message must be exactly one JSON object and nothing else: no prose, no explanation, no markdown code fence.' \
    'It must have exactly these four keys:' \
    "stage (exactly \"$stage\")," \
    'status ("OK", "FAILED" or "NEEDS_HUMAN"),' \
    'message (a non-empty single-line summary),' \
    "and verdict ($verdict)."
}

# Sets FLOW_ENGINE_COMMAND (argv array), FLOW_ENGINE_CWD and
# FLOW_ENGINE_RESULT_FROM_STDOUT. Claude Code works from its current directory
# and reports the final message on stdout, so the runner runs it inside the
# worktree and captures stdout separately from the log.
# Arguments: <worktree> <schema> <result-file> <prompt>
flow_engine_claude_stage_command() {
  FLOW_ENGINE_CWD=$1
  FLOW_ENGINE_RESULT_FROM_STDOUT=true
  FLOW_ENGINE_COMMAND=(claude -p --dangerously-skip-permissions --no-session-persistence \
    --output-format json "$4")
}

# Turns the `claude -p --output-format json` envelope into the structured stage
# result the runner validates. Fails closed: any missing field, provider-reported
# error, or non-JSON final message leaves an empty result the runner rejects.
# Arguments: <raw-stdout-file> <result-file>
flow_engine_claude_publish_result() {
  local raw=$1 result=$2
  jq -e '
    if type != "object" then error("provider envelope is not an object")
    elif (.is_error // false) == true then error("provider reported is_error")
    elif (.result | type) != "string" then error("provider envelope carries no result text")
    else (.result
          | sub("^[[:space:]]*```(json)?[[:space:]]*"; "")
          | sub("[[:space:]]*```[[:space:]]*$"; "")
          | fromjson)
    end
  ' "$raw" >"$result" 2>/dev/null
}
