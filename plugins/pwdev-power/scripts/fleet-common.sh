#!/usr/bin/env bash
# Shared fleet vocabulary. Source this; do not execute it.

power_require_runtime() {
  case "${1:-}" in
    claude|codex|hermes) return 0 ;;
    *) printf 'unsupported fleet runtime: %s\n' "${1:-}" >&2; return 2 ;;
  esac
}

# The structured-result contract, written as prose.
#
# Codex enforces templates/fleet-result.schema.json natively through --output-schema. Claude
# and Hermes have no equivalent, so for them the contract has to travel inside the prompt. It
# lives here, once, rather than in each adapter: two hand-maintained copies of a schema drift,
# and the drift is silent until a stage fails to parse.
#
# Keep this in sync with templates/fleet-result.schema.json and with validate_result in
# fleet-run.sh.
power_result_contract_prose() {
  local stage=$1 verdict
  if [[ $stage == verify ]]; then
    verdict='"APPROVED", "CAVEATS" or "REJECTED"'
  else
    verdict='"NONE"'
  fi
  printf '%s ' \
    'Your final message must be exactly one JSON object and nothing else: no prose, no explanation, no markdown code fence.' \
    'It must have exactly these four keys:' \
    "stage (exactly \"$stage\")," \
    'status ("OK", "FAILED" or "NEEDS_HUMAN"),' \
    'message (a non-empty single-line summary),' \
    "and verdict ($verdict)."
}

# Strip an accidental markdown fence and validate that what remains is one JSON object.
# Used by the runtimes whose output arrives as bare text.
power_publish_bare_json() {
  local raw=$1 result=$2
  # sed -E, not plain sed: BSD sed's BRE has no \? quantifier, so the opening fence silently
  # survives and the whole result fails to parse.
  jq -e '.' <(
    sed -E -e '1s/^[[:space:]]*```([[:alnum:]]+)?[[:space:]]*$//' \
           -e '$s/^[[:space:]]*```[[:space:]]*$//' "$raw"
  ) >"$result" 2>/dev/null
}
