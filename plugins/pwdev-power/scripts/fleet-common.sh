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
# fleet-run.sh — every constraint they enforce, including the message length. A limit the
# validator applies but the prompt never states rejects well-formed work for a rule the model was
# never told, and only on the runtimes that read this prose: Codex learns it from the schema.
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
    'message (a non-empty single-line summary of at most 500 characters; a longer message is rejected),' \
    "and verdict ($verdict)."
  # status describes the stage, verdict describes the feature, and conflating them costs the fix
  # loop: a verify that rejects and says FAILED is a stage the runner cannot advance past.
  if [[ $stage == verify ]]; then
    printf '%s ' \
      'status is how this stage went, not what you concluded about the feature: use "OK" whenever you reached a verdict at all, including a rejection.' \
      'Reserve "FAILED" for being unable to verify, and "NEEDS_HUMAN" for needing a person before anything else happens.' \
      'A rejection belongs in verdict, as "REJECTED" with status "OK" — that is what opens the bounded fix loop.'
  else
    printf '%s ' \
      'status is how this stage went: "OK" if it produced its artifact, "FAILED" if it could not, "NEEDS_HUMAN" if a person must look first.'
  fi
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
