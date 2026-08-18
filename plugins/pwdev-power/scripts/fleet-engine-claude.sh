#!/usr/bin/env bash
# The Claude privileged vector. This file, and only this file, may name the Claude provider or
# add a Claude permission flag.

power_engine_claude_skill_ref() { printf '/pwdev-power:%s' "$1"; }

power_engine_claude_prompt_suffix() { power_result_contract_prose "$1"; }

power_engine_claude_stage_command() {
  # $1 worktree  $2 schema  $3 result-file  $4 prompt
  FLOW_ENGINE_CWD=$1                     # claude has no --cd; the runner chdirs for it
  FLOW_ENGINE_RESULT_FROM_STDOUT=true
  FLOW_ENGINE_COMMAND=(claude -p --dangerously-skip-permissions --no-session-persistence \
    --output-format json "$4")
}

# claude -p --output-format json wraps the answer in an envelope. Unwrap it, strip a fence the
# model may have added, and fail closed: any failure leaves the result file empty and the
# runner rejects the stage.
power_engine_claude_publish_result() {
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
