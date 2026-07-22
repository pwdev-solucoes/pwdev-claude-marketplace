#!/bin/bash
# run-agent.sh — delegate a task to an external coding CLI (codex, opencode,
# kimi, gemini, kiro) with a standardized safety prompt, timeout, write-lock,
# read-only verification, and best-effort audit logging.
#
# NOTE: unlike the audit scripts (POSIX sh, best-effort, always exit 0), this
# script performs active execution — failures must surface to the orchestrator,
# so it uses bash strict mode and meaningful exit codes.
#
# Usage:
#   run-agent.sh <codex|opencode|kimi|gemini|kiro> <write|read> <task...>
#
# Exit codes:
#   0 ok | 2 usage/allowlist | 3 read-only violation | 4 write lock held
#   124 timeout | 127 CLI not installed
#
# Protocol details: ../references/delegation.md
set -Eeuo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
ALLOWLIST="codex opencode kimi gemini kiro"
DEFAULT_TIMEOUT=600

usage() {
  echo "usage: run-agent.sh <codex|opencode|kimi|gemini|kiro> <write|read> <task>" >&2
  exit 2
}

AGENT="${1:-}"; MODE="${2:-}"
shift 2 2>/dev/null || usage
TASK="$*"
[ -n "$TASK" ] || usage
case " $ALLOWLIST " in
  *" $AGENT "*) ;;
  *) echo "❌ agent '$AGENT' not in allowlist ($ALLOWLIST)" >&2; exit 2 ;;
esac
case "$MODE" in write|read) ;; *) usage ;; esac

# kiro's binary is kiro-cli
BINARY="$AGENT"
[ "$AGENT" = "kiro" ] && BINARY="kiro-cli"
command -v "$BINARY" >/dev/null 2>&1 || {
  echo "❌ '$BINARY' CLI not found. Install instructions: references/delegation.md" >&2
  exit 127
}

TOPLEVEL="$(git rev-parse --show-toplevel 2>/dev/null)" || {
  echo "❌ not inside a git repository" >&2
  exit 2
}
cd "$TOPLEVEL"

# Optional per-agent config: .planning/config.json → external_models.<agent>
MODEL=""; TIMEOUT_S="${DELEGATE_TIMEOUT_S:-$DEFAULT_TIMEOUT}"; EXTRA_ARGS=""
if [ -f .planning/config.json ] && command -v jq >/dev/null 2>&1; then
  MODEL=$(jq -r ".external_models.\"$AGENT\".model // empty" .planning/config.json 2>/dev/null || true)
  CFG_T=$(jq -r ".external_models.\"$AGENT\".timeout_s // empty" .planning/config.json 2>/dev/null || true)
  EXTRA_ARGS=$(jq -r ".external_models.\"$AGENT\".extra_args // empty" .planning/config.json 2>/dev/null || true)
  [ -n "$CFG_T" ] && TIMEOUT_S="$CFG_T"
fi

# timeout binary (coreutils gtimeout on macOS); warn-and-continue if absent
TIMEOUT_BIN=""
for t in timeout gtimeout; do
  command -v "$t" >/dev/null 2>&1 && { TIMEOUT_BIN="$t"; break; }
done
[ -n "$TIMEOUT_BIN" ] || echo "⚠️ 'timeout' not available — running without time limit" >&2

# Write-mode lock: never two write agents at once
LOCK=".planning/delegation/.lock"
if [ "$MODE" = "write" ] && [ -d .planning ]; then
  mkdir -p .planning/delegation
  if ! mkdir "$LOCK" 2>/dev/null; then
    echo "❌ another write delegation is running (remove $LOCK if stale)" >&2
    exit 4
  fi
  trap 'rmdir "$LOCK" 2>/dev/null || true' EXIT
fi

# Baseline for read-only verification. Excludes .planning/delegation — the
# script itself writes the output copy (and lock) there, which would
# otherwise register as a false read-only violation.
repo_status() { git status --porcelain -- . ':(exclude).planning/delegation' 2>/dev/null || true; }
STATUS_BEFORE="$(repo_status)"

build_prompt() {
  # Canonical copy of these rules: references/delegation.md §4
  local mode_line
  if [ "$MODE" = "write" ]; then
    mode_line="WRITE — you may create/modify files to complete the task."
  else
    mode_line="READ-ONLY — analysis only. You MUST NOT create, modify, or delete any file."
  fi
  cat <<EOF
You are working inside the git repository at: $TOPLEVEL
MODE: $mode_line

MANDATORY RULES (non-negotiable):
1. NEVER run git commit, git push, or any git history-modifying command.
2. NEVER read or modify .env files, secrets, credentials, keys, or tokens.
3. Respect the project's existing conventions, style, and CLAUDE.md instructions.
4. After code changes, run the relevant tests and report their result.
5. Stay strictly within the scope of the task below — no drive-by changes.
6. NEVER delete or rewrite files unrelated to the task.
7. NEVER create branches, change git config, or touch CI/CD credentials.
8. NEVER install global dependencies or modify anything outside this repository.
9. If the task is ambiguous or risky, stop and report instead of guessing.
10. End with a concise summary: what changed, what was tested, open concerns.

TASK:
$TASK
EOF
}
PROMPT="$(build_prompt)"

# Per-agent invocation — the only place agents differ.
# The prompt is always passed as a single quoted argument, never interpolated.
CMD=()
case "$AGENT" in
  codex)
    CMD=(codex exec "$PROMPT")
    ;;
  opencode)
    CMD=(opencode run)
    [ -n "$MODEL" ] && CMD+=(--model "$MODEL")
    CMD+=("$PROMPT")
    ;;
  kimi)
    # Older kimi versions take the prompt positionally instead of --prompt
    if kimi --help 2>/dev/null | grep -q -- '--prompt'; then
      CMD=(kimi --quiet --prompt "$PROMPT")
    else
      CMD=(kimi --quiet "$PROMPT")
    fi
    ;;
  gemini)
    CMD=(gemini)
    [ -n "$MODEL" ] && CMD+=(--model "$MODEL")
    CMD+=(--prompt "$PROMPT")
    ;;
  kiro)
    CMD=(kiro-cli chat --no-interactive)
    # --trust-all-tools only in write mode: read-only tools are trusted by
    # default, so omitting it makes mutations get rejected in read mode.
    [ "$MODE" = "write" ] && CMD+=(--trust-all-tools)
    CMD+=("$PROMPT")
    ;;
esac
# shellcheck disable=SC2206  # extra_args is intentionally word-split
[ -n "$EXTRA_ARGS" ] && CMD=("${CMD[0]}" $EXTRA_ARGS "${CMD[@]:1}")

# Output copy (best-effort, only when a .planning/ workspace exists)
OUT=""
if [ -d .planning ]; then
  mkdir -p .planning/delegation
  OUT=".planning/delegation/$(date -u +%Y%m%dT%H%M%SZ)-$AGENT.md"
fi

echo "▶ delegating to $AGENT (mode: $MODE, timeout: ${TIMEOUT_S}s)"
set +e
if [ -n "$TIMEOUT_BIN" ]; then
  if [ -n "$OUT" ]; then
    "$TIMEOUT_BIN" "$TIMEOUT_S" "${CMD[@]}" 2>&1 | tee "$OUT"; RC=${PIPESTATUS[0]}
  else
    "$TIMEOUT_BIN" "$TIMEOUT_S" "${CMD[@]}"; RC=$?
  fi
else
  if [ -n "$OUT" ]; then
    "${CMD[@]}" 2>&1 | tee "$OUT"; RC=${PIPESTATUS[0]}
  else
    "${CMD[@]}"; RC=$?
  fi
fi
set -e

# Audit (best-effort — audit-log.sh always exits 0)
"$SCRIPT_DIR/audit-log.sh" event delegate DELEGATE external_run "$AGENT" \
  "{\"mode\":\"$MODE\",\"exit\":$RC,\"timeout_s\":$TIMEOUT_S}" 2>/dev/null || true

# Read-only violation check
if [ "$MODE" = "read" ] && [ "$STATUS_BEFORE" != "$(repo_status)" ]; then
  echo "❌ READ-ONLY VIOLATION: '$AGENT' modified the working tree. Review 'git status' and revert." >&2
  exit 3
fi
[ "$RC" -eq 124 ] && echo "⏱️ '$AGENT' timed out after ${TIMEOUT_S}s" >&2
exit "$RC"
