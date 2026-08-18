#!/usr/bin/env bash
# Extract exactly one task's text from a plan, plus the plan's Global Constraints block, into
# a standalone brief the implementer can read on its own.
#
# The implementer never reads the whole plan: it would pull in every other task's context and
# defeat the point of a fresh one. The brief is the contract, so the constraints travel with it
# verbatim rather than as a reference the child cannot resolve.
set -Eeuo pipefail

usage() { printf 'usage: task-brief.sh <plan-file> <task-number>\n' >&2; exit 2; }

[[ $# -eq 2 ]] || usage
PLAN=$1
NUM=$2
[[ -f $PLAN ]] || { printf 'task-brief: no such plan: %s\n' "$PLAN" >&2; exit 2; }
[[ $NUM =~ ^[0-9]{1,2}$ ]] || { printf 'task-brief: invalid task number: %s\n' "$NUM" >&2; exit 2; }

PADDED=$(printf '%02d' "$((10#$NUM))")
DIR=$(cd -- "$(dirname -- "$PLAN")" && pwd -P)
OUT=$DIR/task-$PADDED-brief.md

# Record the plan by repository-relative path: the brief is committed, and an absolute path
# would carry this machine's layout into the repository.
PLAN_ABS=$DIR/$(basename -- "$PLAN")
if REPO_ROOT=$(git -C "$DIR" rev-parse --show-toplevel 2>/dev/null); then
  PLAN_REF=${PLAN_ABS#"$REPO_ROOT"/}
else
  PLAN_REF=$PLAN_ABS
fi

# Global Constraints: from its heading to the next same-or-higher heading.
CONSTRAINTS=$(awk '
  /^## +Global Constraints/ { grab = 1; next }
  grab && /^#{1,2} / { exit }
  grab { print }
' "$PLAN")

# The task section: from "## Task NN" to the next "## ".
TASK=$(awk -v want="$PADDED" '
  $0 ~ "^## +Task +0*" want "([^0-9]|$)" { grab = 1; print; next }
  grab && /^## / { exit }
  grab { print }
' "$PLAN")

[[ -n ${TASK//[[:space:]]/} ]] || { printf 'task-brief: task %s not found in %s\n' "$PADDED" "$PLAN" >&2; exit 3; }

{
  printf '# Task %s — brief\n\n' "$PADDED"
  printf 'Plan: %s\n' "$PLAN_REF"
  printf 'Generated: %s\n\n' "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
  printf 'These are your requirements. Every value below is exact — copy it, do not round it,\n'
  printf 'do not substitute an equivalent, do not improve it.\n\n'
  printf '## Global Constraints\n'
  if [[ -n ${CONSTRAINTS//[[:space:]]/} ]]; then
    printf '%s\n\n' "$CONSTRAINTS"
  else
    printf '\n(none declared in the plan)\n\n'
  fi
  printf '%s\n' "$TASK"
} >"$OUT"

printf '%s\n' "$OUT"
