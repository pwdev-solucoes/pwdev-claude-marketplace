#!/bin/sh
# audit-log.sh — semantic audit helper called from pwdev-code commands at
# meaningful moments (phase gates, decisions). Complements the mechanical
# logging done by audit-hook.sh. Best-effort: any failure exits 0.
#
# Usage:
#   audit-log.sh event <command> <phase> <action> [target] [detail]
#   audit-log.sh decision <phase> <decision> [rationale] [alternatives]
#
# Examples:
#   audit-log.sh event design DESIGN gate_passed spec.md '{"decisions":4}'
#   audit-log.sh decision DESIGN "Use PostgreSQL" "Relational fit" "MongoDB, SQLite"

DB=".planning/pwdev-audit.db"

grep -q '"audit"[[:space:]]*:[[:space:]]*true' .planning/config.json 2>/dev/null || exit 0
command -v sqlite3 >/dev/null 2>&1 || exit 0
[ -f "$DB" ] || exit 0

esc() { printf '%s' "$1" | sed "s/'/''/g"; }

MODE="$1"

case "$MODE" in
  event)
    CMD=$(esc "$2"); PHASE=$(esc "$3"); ACTION=$(esc "$4")
    TARGET=$(esc "${5:-}"); DETAIL=$(esc "${6:-}")
    sqlite3 "$DB" "INSERT INTO events (plugin, command, phase, action, target, detail) \
      VALUES ('pwdev-code', '$CMD', '$PHASE', '$ACTION', '$TARGET', '$DETAIL');" 2>/dev/null
    ;;
  decision)
    PHASE=$(esc "$2"); DECISION=$(esc "$3")
    RATIONALE=$(esc "${4:-}"); ALTERNATIVES=$(esc "${5:-}")
    sqlite3 "$DB" "INSERT INTO decisions (phase, decision, rationale, alternatives) \
      VALUES ('$PHASE', '$DECISION', '$RATIONALE', '$ALTERNATIVES');" 2>/dev/null
    ;;
esac

exit 0
