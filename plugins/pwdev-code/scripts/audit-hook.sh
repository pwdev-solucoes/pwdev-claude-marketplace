#!/bin/sh
# audit-hook.sh <event> — pwdev-code deterministic audit trail.
# Receives the Claude Code hook JSON on stdin and records events in
# .planning/pwdev-audit.db. Best-effort by design: any failure exits 0
# so the audit trail never blocks real work.

EVENT="$1"
DB=".planning/pwdev-audit.db"
TMP=".planning/.audit-tmp"

# Audit is opt-in per project: config flag, sqlite3 binary and DB must exist.
grep -q '"audit"[[:space:]]*:[[:space:]]*true' .planning/config.json 2>/dev/null || exit 0
command -v sqlite3 >/dev/null 2>&1 || exit 0
[ -f "$DB" ] || exit 0

INPUT=$(cat 2>/dev/null)

# jget <field> — extract a string field from the hook JSON (jq when
# available, sed fallback that matches the last path segment).
jget() {
  if command -v jq >/dev/null 2>&1; then
    printf '%s' "$INPUT" | jq -r ".$1 // empty" 2>/dev/null
  else
    printf '%s' "$INPUT" | sed -n "s/.*\"${1##*.}\"[[:space:]]*:[[:space:]]*\"\([^\"]*\)\".*/\1/p" | head -1
  fi
}

now_ms() {
  perl -MTime::HiRes=time -e 'printf("%d", time()*1000)' 2>/dev/null \
    || echo "$(( $(date +%s) * 1000 ))"
}

esc() { printf '%s' "$1" | sed "s/'/''/g"; }

SESSION=$(jget session_id)

case "$EVENT" in
  session_start)
    sqlite3 "$DB" "INSERT INTO events (session_id, plugin, command, action) \
      VALUES ('$(esc "$SESSION")', 'pwdev-code', 'session', 'session_start');" 2>/dev/null
    ;;

  subagent_start)
    AGENT=$(jget agent_type)
    case "$AGENT" in
      pwdev-code:*|executor|advisor|code-reviewer|qa|verifier|researcher|roadmap|simplifier) ;;
      *) exit 0 ;;
    esac
    mkdir -p "$TMP" 2>/dev/null
    now_ms > "$TMP/${SESSION}-${AGENT##*:}.start" 2>/dev/null
    sqlite3 "$DB" "INSERT INTO events (session_id, plugin, command, agent, action) \
      VALUES ('$(esc "$SESSION")', 'pwdev-code', 'subagent', '$(esc "$AGENT")', 'started');" 2>/dev/null
    ;;

  subagent_stop)
    AGENT=$(jget agent_type)
    case "$AGENT" in
      pwdev-code:*|executor|advisor|code-reviewer|qa|verifier|researcher|roadmap|simplifier) ;;
      *) exit 0 ;;
    esac
    START_F="$TMP/${SESSION}-${AGENT##*:}.start"
    DUR=""
    if [ -f "$START_F" ]; then
      START=$(cat "$START_F" 2>/dev/null)
      rm -f "$START_F" 2>/dev/null
      case "$START" in
        ''|*[!0-9]*) ;;
        *) DUR=$(( $(now_ms) - START )) ;;
      esac
    fi
    sqlite3 "$DB" "INSERT INTO events (session_id, plugin, command, agent, action, duration_ms) \
      VALUES ('$(esc "$SESSION")', 'pwdev-code', 'subagent', '$(esc "$AGENT")', 'completed', ${DUR:-NULL});" 2>/dev/null
    ;;

  artifact)
    FP=$(jget tool_input.file_path)
    case "$FP" in
      .planning/*|*/.planning/*)
        sqlite3 "$DB" "INSERT INTO artifacts (path, type, status) \
          VALUES ('$(esc "$FP")', 'planning', 'active');" 2>/dev/null
        ;;
    esac
    ;;

  stop)
    sqlite3 "$DB" "INSERT INTO events (session_id, plugin, command, action) \
      VALUES ('$(esc "$SESSION")', 'pwdev-code', 'session', 'turn_completed');" 2>/dev/null
    ;;
esac

exit 0
