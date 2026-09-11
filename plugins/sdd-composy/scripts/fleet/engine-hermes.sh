#!/usr/bin/env bash
set -Eeuo pipefail

# Hermes runtime adapter. The runner owns lifecycle, locks and result validation;
# this adapter owns only the provider vector and never falls back to another runtime.
sdd_engine_hermes_skill_ref() { printf 'sdd-composy:%s' "$1"; }
sdd_engine_hermes_prompt_suffix() {
  printf 'Return exactly one JSON object with stage=%s, status OK|FAILED|NEEDS_HUMAN, message, and verdict.' "$1"
}
sdd_engine_hermes_stage_command() {
  if [[ ${SDD_HERMES_ISOLATED:-0} != 1 && ${SDD_HERMES_AUTOMATION_CONSENT:-0} != 1 ]]; then
    printf '%s\n' 'Hermes automation requires proven isolation or specific user consent' >&2
    return 2
  fi
  FLOW_ENGINE_CWD=$1; SDD_ENGINE_CWD=$1
  FLOW_ENGINE_RESULT_FROM_STDOUT=true; SDD_ENGINE_RESULT_FROM_STDOUT=true
  FLOW_ENGINE_COMMAND=(hermes -z "$4" --in "$1")
  SDD_ENGINE_COMMAND=("${FLOW_ENGINE_COMMAND[@]}")
}
sdd_engine_hermes_interactive_command() {
  SDD_ENGINE_CWD=
  SDD_ENGINE_COMMAND=(hermes chat --query-file "$2" --cli --in "$1")
}
sdd_engine_hermes_publish_result() {
  local raw=$1 result=$2
  jq -e 'if type != "object" then error("result is not object") else . end' "$raw" >"$result"
}
