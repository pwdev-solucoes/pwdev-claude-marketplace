#!/bin/sh
# review_package.sh <base> <target> <out-dir> [-- <path>...]
# Builds the review package for an explicit range: range.txt, commits.txt,
# changed-files.txt, diffstat.txt and diff.patch in <out-dir>. Prints a JSON
# summary. Read-only on the repository: never checks out, never moves HEAD.
# Exit 2 on a bad or ambiguous range, 3 when the range is empty.

usage() { echo 'usage: review_package.sh <base> <target> <out-dir> [-- <path>...]' >&2; exit 2; }
[ $# -ge 3 ] || usage
BASE=$1; TARGET=$2; OUT=$3; shift 3
if [ "${1:-}" = "--" ]; then shift; fi

git rev-parse --verify --quiet "$BASE^{commit}" >/dev/null || { echo "review_package: bad base ref: $BASE" >&2; exit 2; }
git rev-parse --verify --quiet "$TARGET^{commit}" >/dev/null || { echo "review_package: bad target ref: $TARGET" >&2; exit 2; }
BASE_SHA=$(git rev-parse "$BASE")
TARGET_SHA=$(git rev-parse "$TARGET")
[ "$BASE_SHA" != "$TARGET_SHA" ] || { echo "review_package: base and target are the same commit ($BASE_SHA)" >&2; exit 3; }
git merge-base --is-ancestor "$BASE_SHA" "$TARGET_SHA" 2>/dev/null || \
  echo "review_package: warning: $BASE is not an ancestor of $TARGET — diff is two-dot" >&2

mkdir -p "$OUT" || exit 2
printf 'base=%s\ntarget=%s\nbase_ref=%s\ntarget_ref=%s\npaths=%s\n' "$BASE_SHA" "$TARGET_SHA" "$BASE" "$TARGET" "$*" >"$OUT/range.txt"
git log --no-decorate --oneline "$BASE_SHA..$TARGET_SHA" -- "$@" >"$OUT/commits.txt"
git diff --name-status "$BASE_SHA" "$TARGET_SHA" -- "$@" >"$OUT/changed-files.txt"
git diff --stat "$BASE_SHA" "$TARGET_SHA" -- "$@" >"$OUT/diffstat.txt"
git diff -U10 "$BASE_SHA" "$TARGET_SHA" -- "$@" >"$OUT/diff.patch"

FILES=$(wc -l <"$OUT/changed-files.txt" | tr -d ' ')
[ "$FILES" -gt 0 ] || { echo "review_package: no changes in range" >&2; exit 3; }
printf '{"ok": true, "base": "%s", "target": "%s", "changed_files": %s, "commits": %s, "package": "%s"}\n' \
  "$BASE_SHA" "$TARGET_SHA" "$FILES" "$(wc -l <"$OUT/commits.txt" | tr -d ' ')" "$OUT"
