#!/usr/bin/env bash
# Build the review package for a range of commits: the commit list, the stat summary, and the
# full diff with generous context. Prints the package path on stdout.
#
# Reviewers get a file, not a paste. That keeps the diff out of the orchestrating context and
# lets the reviewer read as much of it as it needs.
set -Eeuo pipefail

usage() { printf 'usage: review-package.sh <output-dir> <base-ref> <head-ref>\n' >&2; exit 2; }

[[ $# -eq 3 ]] || usage
OUTDIR=$1
BASE=$2
HEAD=$3

[[ -d $OUTDIR ]] || { printf 'review-package: no such directory: %s\n' "$OUTDIR" >&2; exit 2; }
git rev-parse --verify --quiet "$BASE^{commit}" >/dev/null || { printf 'review-package: bad base ref: %s\n' "$BASE" >&2; exit 2; }
git rev-parse --verify --quiet "$HEAD^{commit}" >/dev/null || { printf 'review-package: bad head ref: %s\n' "$HEAD" >&2; exit 2; }

BASE_SHA=$(git rev-parse --short=7 "$BASE")
HEAD_SHA=$(git rev-parse --short=7 "$HEAD")
OUT=$OUTDIR/review-$BASE_SHA..$HEAD_SHA.diff

if [[ $BASE_SHA == "$HEAD_SHA" ]]; then
  printf 'review-package: base and head are the same commit (%s); nothing was committed\n' "$BASE_SHA" >&2
  exit 3
fi

{
  printf '# Review package %s..%s\n\n' "$BASE_SHA" "$HEAD_SHA"
  printf '## Commits\n\n'
  git log --no-decorate --oneline "$BASE..$HEAD"
  printf '\n## Files changed\n\n'
  git diff --stat "$BASE..$HEAD"
  printf '\n## Diff\n\n'
  git diff -U10 "$BASE..$HEAD"
} >"$OUT"

printf '%s\n' "$OUT"
