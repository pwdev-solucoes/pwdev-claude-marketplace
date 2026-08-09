#!/bin/bash
# fleet-up.sh — bring up one fleet member for /pwdev-code:fleet: an isolated
# git worktree + docker-compose stack on its own ports + a tmux window
# running fleet-run.sh (the headless plan→execute→review→verify pipeline).
#
# Usage:
#   fleet-up.sh <phase-slug>
#
# Env:
#   DRY_RUN=1   print the planned actions instead of running them
#
# Exit codes: 0 ok | 2 usage/config | 3 already active | 4 lock held
set -Eeuo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
TEMPLATES_DIR="$(cd "$SCRIPT_DIR/../templates" && pwd)"
DRY_RUN="${DRY_RUN:-0}"

SLUG="${1:-}"
[ -n "$SLUG" ] || { echo "usage: fleet-up.sh <phase-slug>" >&2; exit 2; }
case "$SLUG" in *[!a-zA-Z0-9._-]*) echo "❌ slug must be alnum/dash/dot/underscore only: $SLUG" >&2; exit 2 ;; esac

command -v jq >/dev/null 2>&1 || { echo "❌ jq is required (brew install jq)" >&2; exit 2; }
command -v tmux >/dev/null 2>&1 || { echo "❌ tmux is required" >&2; exit 2; }
command -v docker >/dev/null 2>&1 || { echo "❌ docker is required" >&2; exit 2; }

TOPLEVEL="$(git rev-parse --show-toplevel 2>/dev/null)" || { echo "❌ not inside a git repository" >&2; exit 2; }
cd "$TOPLEVEL"

[ -f ".planning/phases/${SLUG}/spec.md" ] && [ -f ".planning/phases/${SLUG}/decisions.md" ] || {
  echo "❌ ${SLUG}: no spec.md/decisions.md — run /pwdev-code:design ${SLUG} first" >&2; exit 2;
}

mkdir -p .planning/fleet
[ -f ".planning/fleet/${SLUG}.json" ] && { echo "❌ ${SLUG}: already active (see .planning/fleet/${SLUG}.json)" >&2; exit 3; }

# Fleet bookkeeping (.planning/fleet/*.json, the pane wrapper, the mkdir-lock
# dir) is machine-local ephemeral state, same spirit as pwdev-audit.db — never
# versioned. This deliberately does NOT write to the main repo's .gitignore
# (fleet-up.sh must never touch the human's current working tree — an
# uncommitted change there previously caused a spurious "untracked file
# would be overwritten" conflict on a later `fleet-teardown.sh --merge`).
# Suggest it once instead, and let the human add it via their normal flow.
if ! grep -qxF ".planning/fleet/" .gitignore 2>/dev/null; then
  echo "ℹ️ tip: add '.planning/fleet/' to your .gitignore (bookkeeping only, not versioned)" >&2
fi

CFG=".planning/config.json"
cfg() { [ -f "$CFG" ] && jq -r "$1 // $2" "$CFG" 2>/dev/null || echo "$2" | tr -d '"'; }
MAX_CONCURRENT=$(cfg '.fleet.max_concurrent' 3)
PORT_BASE_APP=$(cfg '.fleet.port_base_app' 3000)
PORT_BASE_DB=$(cfg '.fleet.port_base_db' 5432)
PORT_STEP=$(cfg '.fleet.port_step' 10)
PERMISSION_MODE=$(cfg '.fleet.permission_mode' '"bypassPermissions"')
COMPOSE_FILE=$(cfg '.fleet.compose_file' '"docker-compose.fleet.yml"')
TMUX_SESSION="pwdev-fleet"

# --- Port slot allocation (mkdir-lock: same pattern as run-agent.sh) ---
LOCK=".planning/fleet/.lock"
mkdir -p .planning/fleet
if ! mkdir "$LOCK" 2>/dev/null; then
  echo "❌ another /pwdev-code:fleet launch is in progress (remove $LOCK if stale)" >&2
  exit 4
fi
trap 'rmdir "$LOCK" 2>/dev/null || true' EXIT

# find (not ls-glob or bash arrays) so this stays correct on both bash 3.2
# (macOS default /bin/bash — empty arrays + `set -u` throw "unbound
# variable" there) and modern bash, and never trips `pipefail` on zero matches.
ACTIVE=$(find .planning/fleet -maxdepth 1 -name '*.json' 2>/dev/null | wc -l | tr -d ' ')
if [ "$ACTIVE" -ge "$MAX_CONCURRENT" ]; then
  echo "❌ fleet.max_concurrent ($MAX_CONCURRENT) reached — teardown a slug first" >&2
  exit 2
fi

USED_INDEXES=""
while IFS= read -r f; do
  [ -n "$f" ] || continue
  USED_INDEXES="$USED_INDEXES $(jq -r '.port_index // empty' "$f" 2>/dev/null)"
done < <(find .planning/fleet -maxdepth 1 -name '*.json' 2>/dev/null)
INDEX=0
while echo " $USED_INDEXES " | grep -q " $INDEX "; do INDEX=$((INDEX + 1)); done
if [ "$INDEX" -ge "$MAX_CONCURRENT" ]; then
  echo "❌ no free port slot under fleet.max_concurrent ($MAX_CONCURRENT)" >&2
  exit 2
fi

APP_PORT=$((PORT_BASE_APP + PORT_STEP * INDEX))
DB_PORT=$((PORT_BASE_DB + PORT_STEP * INDEX))
PROJECT_NAME="fleet-${SLUG}"
REPO_NAME="$(basename "$TOPLEVEL")"
WORKTREE_PATH="$(cd .. && pwd)/${REPO_NAME}-fleet-${SLUG}"
BRANCH="fleet/${SLUG}"

echo "▶ fleet-up: ${SLUG} → worktree=${WORKTREE_PATH} branch=${BRANCH} app_port=${APP_PORT} db_port=${DB_PORT}"

# Deterministic port assignment only avoids collisions between fleet slugs —
# it says nothing about ports already held by unrelated processes on this
# machine (a local Postgres, another project's dev server, ...). Check that
# directly instead of letting `docker compose up` fail with a confusing
# "address already in use" deep in its own output.
port_in_use() {
  (exec 3<>"/dev/tcp/127.0.0.1/$1") 2>/dev/null && { exec 3<&- 2>/dev/null; exec 3>&- 2>/dev/null; return 0; }
  return 1
}
PORT_CONFLICT=0
for p in "$APP_PORT" "$DB_PORT"; do
  port_in_use "$p" && { echo "⚠️ port $p is already in use on this machine" >&2; PORT_CONFLICT=1; }
done
if [ "$PORT_CONFLICT" -eq 1 ] && [ "$DRY_RUN" != "1" ]; then
  echo "❌ refusing to start ${SLUG} — free the port(s) above or change fleet.port_base_app/port_base_db/port_step in .planning/config.json" >&2
  exit 2
fi

if [ "$DRY_RUN" = "1" ]; then
  cat <<EOF
[DRY_RUN] would run:
  git worktree add "$WORKTREE_PATH" -b "$BRANCH"
  write "$WORKTREE_PATH/.env.fleet" (APP_PORT=$APP_PORT DB_PORT=$DB_PORT PROJECT_NAME=$PROJECT_NAME)
  cp "$TEMPLATES_DIR/$COMPOSE_FILE" "$WORKTREE_PATH/$COMPOSE_FILE"
  docker compose -p "$PROJECT_NAME" -f "$WORKTREE_PATH/$COMPOSE_FILE" --env-file "$WORKTREE_PATH/.env.fleet" up -d [db|full]
  write .planning/fleet/${SLUG}.pane.sh (wrapper) + tmux new-session/new-window -t "$TMUX_SESSION":"$SLUG" running it
  write .planning/fleet/${SLUG}.json
EOF
  exit 0
fi

# --- Worktree ---
git status --short >/dev/null 2>&1 || true
git worktree add "$WORKTREE_PATH" -b "$BRANCH" >/dev/null

# --- Ignore fleet-local files inside the worktree, committed immediately so
#     execute.md's "uncommitted work" check never trips on our own scaffolding ---
(
  cd "$WORKTREE_PATH"
  NEED_IGNORE=0
  for pattern in ".env.fleet" "/${COMPOSE_FILE}" ".planning/fleet-status.json" ".planning/fleet-logs/"; do
    grep -qxF "$pattern" .gitignore 2>/dev/null || { echo "$pattern" >> .gitignore; NEED_IGNORE=1; }
  done
  if [ "$NEED_IGNORE" -eq 1 ]; then
    git add .gitignore
    git commit -q -m "chore(fleet): ignore fleet-local scaffolding files"
  fi
)

# --- Env file + compose ---
[ -f "$TEMPLATES_DIR/$COMPOSE_FILE" ] || { echo "❌ missing template $TEMPLATES_DIR/$COMPOSE_FILE" >&2; exit 2; }
cp "$TEMPLATES_DIR/$COMPOSE_FILE" "$WORKTREE_PATH/$COMPOSE_FILE"
cat > "$WORKTREE_PATH/.env.fleet" <<EOF
FLEET_PROJECT_NAME=${PROJECT_NAME}
FLEET_APP_PORT=${APP_PORT}
FLEET_APP_INTERNAL_PORT=3000
FLEET_DB_PORT=${DB_PORT}
FLEET_DB_NAME=app
FLEET_DB_USER=app
FLEET_DB_PASSWORD=app
FLEET_APP_DOCKERFILE=Dockerfile
EOF

COMPOSE_ARGS=(-p "$PROJECT_NAME" -f "$WORKTREE_PATH/$COMPOSE_FILE" --env-file "$WORKTREE_PATH/.env.fleet")
if [ -f "$WORKTREE_PATH/Dockerfile" ]; then
  docker compose "${COMPOSE_ARGS[@]}" up -d
else
  echo "ℹ️ no Dockerfile in worktree — starting db service only"
  docker compose "${COMPOSE_ARGS[@]}" up -d db
fi

# --- tmux ---
if ! tmux has-session -t "$TMUX_SESSION" 2>/dev/null; then
  tmux new-session -d -s "$TMUX_SESSION" -n dashboard "\"$SCRIPT_DIR/fleet-dashboard.sh\""
fi
# Write a tiny wrapper script instead of inlining a nested-quoted command
# string for tmux (fragile — easy to get an unterminated quote, and tmux
# then just silently closes the window). The wrapper keeps the pane open
# after fleet-run.sh exits (remain-on-exit is off by default, so tmux would
# otherwise destroy the window the instant the pipeline finishes or halts —
# before a human can read the final status).
PANE_SCRIPT="$TOPLEVEL/.planning/fleet/${SLUG}.pane.sh"
cat > "$PANE_SCRIPT" <<EOF
#!/bin/bash
"$SCRIPT_DIR/fleet-run.sh" "$SLUG" "$WORKTREE_PATH" "$PERMISSION_MODE"
echo
echo "---- fleet-run finished (${SLUG}) — press Enter to close this pane ----"
read -r _
EOF
chmod +x "$PANE_SCRIPT"
tmux new-window -t "$TMUX_SESSION" -n "$SLUG" "bash \"$PANE_SCRIPT\""

# --- Bookkeeping ---
jq -n \
  --arg slug "$SLUG" --arg branch "$BRANCH" --arg worktree "$WORKTREE_PATH" \
  --argjson app_port "$APP_PORT" --argjson db_port "$DB_PORT" --argjson port_index "$INDEX" \
  --arg project_name "$PROJECT_NAME" --arg tmux_window "${TMUX_SESSION}:${SLUG}" \
  --arg started_at "$(date -u +%Y-%m-%dT%H:%M:%SZ)" \
  '{slug:$slug, branch:$branch, worktree_path:$worktree, app_port:$app_port, db_port:$db_port,
    port_index:$port_index, project_name:$project_name, tmux_window:$tmux_window, started_at:$started_at}' \
  > ".planning/fleet/${SLUG}.json"

echo "✅ ${SLUG} up — tmux window ${TMUX_SESSION}:${SLUG}, app:${APP_PORT} db:${DB_PORT}"
