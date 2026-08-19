#!/usr/bin/env bash
# The Hermes privileged vector. This file, and only this file, may name the Hermes provider or
# add a Hermes permission flag.

power_engine_hermes_skill_ref() { printf 'pwdev-power:power-%s' "$1"; }

# Hermes has no --output-schema, so the contract travels in the prompt, from the one shared
# source in fleet-common.sh.
power_engine_hermes_prompt_suffix() { power_result_contract_prose "$1"; }

power_engine_hermes_stage_command() {
  # $1 worktree  $2 schema  $3 result-file  $4 prompt
  #
  # --in sets the working directory: the fleet owns the worktree, because the contract hashes
  # are bound to it, so hermes' own --worktree must not be used here.
  #
  # -z prints only the final response text, with no banner and no session line, so the result
  # arrives on stdout as bare JSON rather than inside an envelope.
  FLOW_ENGINE_CWD=
  FLOW_ENGINE_RESULT_FROM_STDOUT=true
  FLOW_ENGINE_COMMAND=(hermes -z "$4" --in "$1" --yolo --accept-hooks)
}

power_engine_hermes_publish_result() { power_publish_bare_json "$1" "$2"; }

# Visual fleet members are not implemented for this runtime.
#
# Declared rather than omitted so the panel fails with a sentence instead of an unbound-function
# error, and so the gap is visible to anyone reading the engine.
power_engine_hermes_interactive_command() {
  printf 'visual mode is not implemented for the hermes runtime\n' >&2
  return 2
}
