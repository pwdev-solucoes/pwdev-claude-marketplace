#!/bin/bash
# fleet-teardown.sh — stop and clean up one /pwdev-code:fleet member.
# Always stops the worktree's docker-compose stack and closes its tmux
# window. Only merges/removes the worktree when --merge is passed AND the
# worktree's own fleet-status.json says status=DONE — never merges a
# rejected or still-running pipeline.
#
# Usage:
#   fleet-teardown.sh <phase-slug> [--merge]
#
# Env:
#   DRY_RUN=1   print the planned actions instead of running them
set -Eeuo pipefail

DRY_RUN="${DRY_RUN:-0}"
SLUG="${1:-}"
MERGE=0
[ "${2:-}" = "--merge" ] && MERGE=1
[ -n "$SLUG" ] || { echo "usage: fleet-teardown.sh <phase-slug> [--merge]" >&2; exit 2; }

command -v jq >/dev/null 2>&1 || { echo "❌ jq is required" >&2; exit 2; }

TOPLEVEL="$(git rev-parse --show-toplevel 2>/dev/null)" || { echo "❌ not inside a git repository" >&2; exit 2; }
cd "$TOPLEVEL"

BOOKKEEPING=".planning/fleet/${SLUG}.json"
[ -f "$BOOKKEEPING" ] || { echo "❌ ${SLUG}: not an active fleet member (no ${BOOKKEEPING})" >&2; exit 2; }

WORKTREE=$(jq -r '.worktree_path' "$BOOKKEEPING")
BRANCH=$(jq -r '.branch' "$BOOKKEEPING")
PROJECT_NAME=$(jq -r '.project_name' "$BOOKKEEPING")
TMUX_WINDOW=$(jq -r '.tmux_window' "$BOOKKEEPING")
COMPOSE_FILE_NAME=$(jq -r '.compose_file // "docker-compose.fleet.yml"' "$BOOKKEEPING" 2>/dev/null || echo "docker-compose.fleet.yml")

STATUS="UNKNOWN"
STATUS_FILE="${WORKTREE}/.planning/fleet-status.json"
[ -f "$STATUS_FILE" ] && STATUS=$(jq -r '.status // "UNKNOWN"' "$STATUS_FILE" 2>/dev/null || echo "UNKNOWN")

echo "▶ fleet-teardown: ${SLUG} (status=${STATUS}, merge=${MERGE})"

if [ "$DRY_RUN" = "1" ]; then
  cat <<EOF
[DRY_RUN] would run:
  docker compose -p "$PROJECT_NAME" -f "${WORKTREE}/${COMPOSE_FILE_NAME}" down
  tmux kill-window -t "$TMUX_WINDOW"
$( [ "$MERGE" -eq 1 ] && [ "$STATUS" = "DONE" ] && echo "  git merge --no-ff \"$BRANCH\"  (status=DONE)
  git worktree remove \"$WORKTREE\"" )
$( [ "$MERGE" -eq 1 ] && [ "$STATUS" != "DONE" ] && echo "  (merge REFUSED — status is '$STATUS', not DONE)" )
  rm "$BOOKKEEPING"
EOF
  exit 0
fi

# --- docker down (best-effort — worktree/compose may already be gone) ---
if [ -f "${WORKTREE}/${COMPOSE_FILE_NAME}" ]; then
  docker compose -p "$PROJECT_NAME" -f "${WORKTREE}/${COMPOSE_FILE_NAME}" down || \
    echo "⚠️ docker compose down failed for ${PROJECT_NAME} — check manually" >&2
else
  echo "ℹ️ no compose file found at ${WORKTREE}/${COMPOSE_FILE_NAME} — skipping docker down"
fi

# --- tmux window ---
tmux kill-window -t "$TMUX_WINDOW" 2>/dev/null || echo "ℹ️ tmux window ${TMUX_WINDOW} already gone"

MERGED=0
if [ "$MERGE" -eq 1 ]; then
  if [ "$STATUS" = "DONE" ]; then
    if git merge --no-ff "$BRANCH" -m "merge: fleet/${SLUG} (verified DONE)"; then
      MERGED=1
      git worktree remove "$WORKTREE" --force 2>/dev/null || \
        echo "⚠️ could not remove worktree ${WORKTREE} automatically — remove it manually" >&2
    else
      echo "❌ merge conflict merging ${BRANCH} — resolve manually, worktree preserved at ${WORKTREE}" >&2
      git merge --abort 2>/dev/null || true
    fi
  else
    echo "⚠️ --merge requested but status is '${STATUS}' (not DONE) — refusing to merge. Worktree preserved at ${WORKTREE}." >&2
  fi
fi

rm -f "$BOOKKEEPING" ".planning/fleet/${SLUG}.pane.sh"

if [ "$MERGED" -eq 1 ]; then
  echo "✅ ${SLUG} merged and cleaned up."
else
  echo "✅ ${SLUG} docker+tmux stopped. Worktree preserved at ${WORKTREE} (branch ${BRANCH}) — merge manually with:"
  echo "   git merge --no-ff ${BRANCH}"
fi
