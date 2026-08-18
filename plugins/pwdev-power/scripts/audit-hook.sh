#!/bin/sh
# audit-hook.sh — automatic audit events on the Claude adapter only.
#
# Enrichment, never a dependency: the portable path is audit-log.sh called explicitly by the
# skills, and everything works with these hooks absent. Always exits 0.

EVENT=${1:-}
[ -n "$EVENT" ] || exit 0

INPUT=$(cat 2>/dev/null)
SCRIPT_DIR=$(cd -- "$(dirname -- "$0")" && pwd -P)

field() {
  if command -v jq >/dev/null 2>&1; then
    printf '%s' "$INPUT" | jq -r "$1 // empty" 2>/dev/null
  fi
}

case "$EVENT" in
  session_start) "$SCRIPT_DIR/audit-log.sh" event session SESSION started "" "" ;;
  stop)          "$SCRIPT_DIR/audit-log.sh" event session SESSION completed "" "" ;;
  subagent_start)
    # The agent type is a role name, not a model name, so it is safe to record.
    "$SCRIPT_DIR/audit-log.sh" event subagent SUBAGENT task_dispatched "$(field '.tool_input.subagent_type')" "" ;;
  subagent_stop)
    "$SCRIPT_DIR/audit-log.sh" event subagent SUBAGENT completed "$(field '.tool_input.subagent_type')" "" ;;
  artifact)
    TARGET=$(field '.tool_input.file_path')
    # Only Power artifacts. Source files are the diff's business, not the audit trail's.
    case "$TARGET" in
      *.planning/power/*) "$SCRIPT_DIR/audit-log.sh" event artifact ARTIFACT artifact_written "$TARGET" "" ;;
    esac ;;
esac

exit 0
