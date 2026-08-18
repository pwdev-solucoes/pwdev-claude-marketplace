#!/bin/sh
# audit-log.sh — the portable audit path, called explicitly by the skills.
#
# Works on every runtime, unlike hooks. Best-effort by construction: it always exits 0, because
# a failed audit record must never change, roll back, or replace the lifecycle result it was
# describing. It warns on stderr instead.
#
# Records only after the durable fact. An audit trail of intentions is a trail of things that
# may not have happened.

REPO_ROOT=$(git rev-parse --show-toplevel 2>/dev/null) || exit 0
CONFIG="$REPO_ROOT/.planning/power/config.json"
DB="$REPO_ROOT/.planning/power/audit/pwdev-audit.db"

# Three conditions, all required: opted in, sqlite3 present, and the database already created.
# Creating the database is the act that turns auditing on, so this never creates one.
[ -f "$CONFIG" ] || exit 0
command -v sqlite3 >/dev/null 2>&1 || exit 0
[ -f "$DB" ] || exit 0

if command -v jq >/dev/null 2>&1; then
  ENABLED=$(jq -r 'if (.audit // false) == true then "yes" else "no" end' "$CONFIG" 2>/dev/null)
else
  ENABLED=$(grep -q '"audit"[[:space:]]*:[[:space:]]*true' "$CONFIG" && echo yes || echo no)
fi
[ "$ENABLED" = yes ] || exit 0

ALLOWED_ACTIONS="started completed failed gate_approved gate_rejected gate_blocked artifact_written decision_recorded ruling_recorded task_dispatched task_reviewed fix_round verify_verdict fleet_launched fleet_stage fleet_teardown kanban_bridged model_resolved"

warn() { echo "pwdev-power audit: $*" >&2; exit 0; }

esc() { printf '%s' "$1" | sed "s/'/''/g"; }

# Model names and prompts carry both cost signal and user content, so they never enter the
# trail. spawn records a tier, not a model name.
reject_secretlike() {
  printf '%s' "$1" | grep -Eqi 'password|secret|token|api[_-]?key|credential|prompt|model' && return 0
  return 1
}

record() { # action phase target detail
  action=$1; phase=$2; target=$3; detail=$4
  case " $ALLOWED_ACTIONS " in
    *" $action "*) ;;
    *) warn "unknown action rejected: $action" ;;
  esac
  reject_secretlike "$detail" && warn "detail rejected: it names a secret-like or excluded field"
  reject_secretlike "$target" && warn "target rejected: it names a secret-like field"

  # Targets are recorded relative to the repository root; absolute paths never enter the trail.
  #
  # Try both spellings of the root. git rev-parse returns the canonical path, so on macOS it
  # reports /private/var/... while a caller working in /var/... passes the symlinked form —
  # matching only one of them lets an absolute path through.
  alt_root=$REPO_ROOT
  case "$REPO_ROOT" in
    /private/*) alt_root=${REPO_ROOT#/private} ;;
    *) alt_root=/private$REPO_ROOT ;;
  esac
  case "$target" in
    "$REPO_ROOT"/*) target=${target#"$REPO_ROOT"/} ;;
    "$alt_root"/*) target=${target#"$alt_root"/} ;;
  esac

  # Whatever remains must not be absolute. Recording a bare filename loses less than recording
  # the machine's directory layout.
  case "$target" in
    /*) warn "target rejected: it is an absolute path outside the repository" ;;
  esac

  sqlite3 "$DB" "
    CREATE TABLE IF NOT EXISTS events (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      schema_version INTEGER NOT NULL DEFAULT 1,
      timestamp TEXT NOT NULL,
      command TEXT,
      phase TEXT,
      action TEXT NOT NULL,
      target TEXT,
      detail TEXT
    );
    INSERT INTO events (timestamp, command, phase, action, target, detail)
    VALUES ('$(date -u +%Y-%m-%dT%H:%M:%SZ)', '$(esc "$COMMAND")', '$(esc "$phase")',
            '$(esc "$action")', '$(esc "$target")', '$(esc "$detail")');
  " 2>/dev/null || warn "record failed for action $action"
  exit 0
}

SUB=${1:-}
[ -n "$SUB" ] || warn 'usage: audit-log.sh <event|spawn|decision|gate> ...'
shift

case "$SUB" in
  event)    COMMAND=${1:-}; record "${3:-}" "${2:-}" "${4:-}" "${5:-}" ;;
  spawn)    COMMAND=${1:-}; record task_dispatched "${2:-}" "${3:-}" "tier=${4:-unspecified} ${5:-}" ;;
  decision) COMMAND=decision; record decision_recorded "${1:-}" "${2:-}" "${3:-}" ;;
  gate)     COMMAND=gate
            case "${2:-}" in
              APPROVED) a=gate_approved ;;
              REJECTED) a=gate_rejected ;;
              BLOCKED)  a=gate_blocked ;;
              *) warn "unknown gate result: ${2:-}" ;;
            esac
            record "$a" "${1:-}" "${3:-}" "" ;;
  *) warn "unknown subcommand: $SUB" ;;
esac
