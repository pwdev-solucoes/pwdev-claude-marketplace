#!/usr/bin/env bash
# Resolve (and create) the working directory for one feature's execution, and make sure its
# ledger exists. Prints the absolute directory path on stdout and nothing else, so callers can
# capture it directly.
#
# Unlike the audit helpers, failures here must surface: every later step writes into the path
# this script prints.
set -Eeuo pipefail

usage() { printf 'usage: power-workspace.sh <feature-slug>\n' >&2; exit 2; }

[[ $# -eq 1 ]] || usage
SLUG=$1
[[ $SLUG =~ ^[a-z0-9][a-z0-9-]*$ ]] || { printf 'power-workspace: invalid slug: %s\n' "$SLUG" >&2; exit 2; }

REPO_ROOT=$(git rev-parse --show-toplevel 2>/dev/null) || {
  printf 'power-workspace: not inside a Git repository\n' >&2; exit 2; }

DIR=$REPO_ROOT/.planning/power/features/$SLUG

# Refuse to follow a symlinked state path: the whole execution writes here.
if [[ -e $DIR && ! -d $DIR ]] || [[ -L $DIR ]]; then
  printf 'power-workspace: unsafe feature path: %s\n' "$DIR" >&2; exit 2
fi

mkdir -p "$DIR"

PLAN=$DIR/plan.md
LEDGER=$DIR/ledger.md

if [[ ! -f $LEDGER ]]; then
  # The first line binds the ledger to its plan. A controller that reads a ledger belonging to
  # a different plan is exactly how completed tasks get dispatched a second time.
  {
    printf '# Power ledger — plan: %s\n\n' ".planning/power/features/$SLUG/plan.md"
    printf 'Created: %s\n\n' "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
    printf '## Progress\n\n'
    printf '## Rulings\n\n'
  } >"$LEDGER"
fi

if [[ ! -f $PLAN ]]; then
  printf 'power-workspace: warning: no plan at %s\n' "$PLAN" >&2
fi

printf '%s\n' "$DIR"
