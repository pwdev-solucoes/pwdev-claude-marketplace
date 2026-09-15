#!/usr/bin/env bash
set -Eeuo pipefail

# OpenCode runtime adapter. The runner owns lifecycle, locks and result validation;
# this adapter owns only the provider vector and never falls back to another runtime.

sdd_engine_opencode_skill_ref() { printf 'sdd-composy:%s' "$1"; }

sdd_engine_opencode_prompt_suffix() {
  printf 'Your final message must be exactly one JSON object with stage=%s, status OK|FAILED|NEEDS_HUMAN, message, and verdict.' "$1"
}

sdd_engine_opencode_stage_command() {
  if [[ ${SDD_OPENCODE_ISOLATED:-0} != 1 && ${SDD_OPENCODE_AUTOMATION_CONSENT:-0} != 1 ]]; then
    printf '%s\n' 'OpenCode automation requires proven isolation or specific user consent' >&2
    return 2
  fi
  FLOW_ENGINE_CWD=$1; SDD_ENGINE_CWD=$1
  FLOW_ENGINE_RESULT_FROM_STDOUT=true; SDD_ENGINE_RESULT_FROM_STDOUT=true
  local auto=()
  [[ ${SDD_FLEET_PERMISSION_MODE:-safe} != danger-full-access ]] || auto=(--auto)
  FLOW_ENGINE_COMMAND=(opencode run --dir "$1" --format json ${auto[@]+"${auto[@]}"} "$4")
  SDD_ENGINE_COMMAND=("${FLOW_ENGINE_COMMAND[@]}")
}

sdd_engine_opencode_interactive_command() {
  local prompt
  prompt=$(<"$2")
  SDD_ENGINE_CWD=
  SDD_ENGINE_COMMAND=(opencode "$1" --prompt "$prompt")
}

# OpenCode reports NDJSON events on stdout with the message text in `.part.text`.
# The result is the last text part that is a JSON object, falling back to the joined
# text parts; anything else fails closed.
# Arguments: <raw-stdout-file> <result-file>
sdd_engine_opencode_publish_result() {
  local raw=$1 result=$2
  jq -se '
    def object_or_null: try (fromjson | if type == "object" then . else null end) catch null;
    [ .[] | select(type == "object" and .type == "text") | .part.text | select(type == "string") ] as $parts
    | if ($parts | length) == 0 then error("no text part") else . end
    | (($parts | last | object_or_null) // ($parts | join("") | object_or_null))
    | if . == null then error("result is not object") else . end
  ' "$raw" >"$result" 2>/dev/null
}
