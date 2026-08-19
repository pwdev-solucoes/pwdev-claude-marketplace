#!/usr/bin/env bash
# Tear one fleet member down: stop its stack, close its cmux workspace, and remove the central
# member record.
#
# Without --merge this preserves the branch and the worktree. Teardown never destroys work and
# never destroys data: the database volume outlives the member and is reported, not removed.
set -Eeuo pipefail

SCRIPT_DIR=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd -P)
# shellcheck source=cmux-common.sh
source "$SCRIPT_DIR/cmux-common.sh"

fail() { printf 'fleet-teardown: %s\n' "$*" >&2; exit 2; }

MERGE=false
SLUG=
while [[ $# -gt 0 ]]; do
  case $1 in
    --merge) MERGE=true; shift ;;
    -*) fail "unknown option: $1" ;;
    *) [[ -z $SLUG ]] || fail 'exactly one slug'; SLUG=$1; shift ;;
  esac
done

[[ -n $SLUG ]] || fail 'usage: fleet-teardown.sh <slug> [--merge]'
[[ $SLUG =~ ^[a-z0-9][a-z0-9-]*$ ]] || fail "invalid slug: $SLUG"

command -v jq >/dev/null 2>&1 || fail 'jq is required'

REPO_ROOT=$(git rev-parse --show-toplevel 2>/dev/null) || fail 'not inside a Git repository'
REPO_ROOT=$(cd "$REPO_ROOT" && pwd -P)
cd "$REPO_ROOT"

FLEET_DIR=$REPO_ROOT/.planning/power/fleet
MEMBER_FILE=$FLEET_DIR/$SLUG.json
PANE_FILE=$FLEET_DIR/$SLUG.pane.sh
ENV_FILE=.env.fleet
COMPOSE_FILE=docker-compose.power-fleet.yml

[[ -f $MEMBER_FILE && ! -L $MEMBER_FILE ]] || fail "no fleet member: $SLUG"

read_field() { jq -er "$1" "$MEMBER_FILE" 2>/dev/null; }

WORKTREE=$(read_field '.worktree_path') || fail 'member record is invalid'
BRANCH=$(read_field '.branch') || fail 'member record is invalid'
BASE_BRANCH=$(read_field '.base_branch // ""') || BASE_BRANCH=
PROJECT_NAME=$(read_field '.project_name') || fail 'member record is invalid'
WORKSPACE_ID=$(read_field '.cmux_workspace_id // ""') || WORKSPACE_ID=
SURFACE_ID=$(read_field '.cmux_surface_id // ""') || SURFACE_ID=
MODE=$(read_field '.mode // "auto"') || MODE=auto
STATUS=$(read_field '.status') || fail 'member record is invalid'

# ---- merge gate ------------------------------------------------------------------------------

if [[ $MERGE == true ]]; then
  [[ $STATUS == DONE ]] || fail "refusing to merge a member that is not DONE (status: $STATUS)"

  STATUS_FILE=$WORKTREE/.planning/power/fleet-status.json
  [[ -f $STATUS_FILE ]] || fail 'refusing to merge without a runner status file'
  jq -e '
    type == "object"
      and .status == "DONE"
      and (.verdict | . == "APPROVED" or . == "CAVEATS")
      and (.correction_cycles | type == "number" and floor == . and . >= 0 and . <= 2)
  ' "$STATUS_FILE" >/dev/null 2>&1 || fail 'refusing to merge: terminal status does not validate'

  [[ -n $BASE_BRANCH ]] || fail 'member record has no base branch to merge into'
  git diff --quiet && git diff --cached --quiet \
    || fail 'refusing to merge into a dirty working tree'
fi

# ---- stack -------------------------------------------------------------------------------------

if [[ -d $WORKTREE && -f $WORKTREE/$COMPOSE_FILE ]]; then
  # Deliberately no --volumes: teardown never destroys data on its own.
  if (cd "$WORKTREE" && docker compose -p "$PROJECT_NAME" --env-file "$ENV_FILE" -f "$COMPOSE_FILE" down) >/dev/null 2>&1; then
    printf 'fleet-teardown: stack %s stopped\n' "$PROJECT_NAME"
    printf 'fleet-teardown: database volume %s_power-fleet-db was kept; remove it with `docker volume rm %s_power-fleet-db` when its data is no longer needed\n' \
      "$PROJECT_NAME" "$PROJECT_NAME"
  else
    printf 'fleet-teardown: warning: could not stop stack %s; inspect it manually\n' "$PROJECT_NAME" >&2
  fi
fi

# ---- cmux ----------------------------------------------------------------------------------------
# Close only what this fleet recorded, by id. A target we cannot identify is one we must not touch.
#
# Panel members share one workspace, so a visual member closes its own surface and leaves the
# workspace to its siblings. The workspace goes only with the last member out — otherwise tearing
# down one phase would take the other three with it.

# Count the panel siblings that will still be registered once this member's record is removed.
panel_siblings_remaining() {
  local count=0 other
  shopt -s nullglob
  for other in "$FLEET_DIR"/*.json; do
    [[ $other == "$MEMBER_FILE" ]] && continue
    if jq -e --arg ws "$WORKSPACE_ID" '.cmux_workspace_id == $ws' "$other" >/dev/null 2>&1; then
      count=$((count + 1))
    fi
  done
  shopt -u nullglob
  printf '%s' "$count"
}

if [[ -n $WORKSPACE_ID ]]; then
  if power_cmux_require >/dev/null 2>&1; then
    CLOSE_WORKSPACE=true

    if [[ $MODE == visual && $(panel_siblings_remaining) -gt 0 ]]; then
      # Siblings are still using this workspace, so only this member's pane may go.
      CLOSE_WORKSPACE=false

      if [[ -n $SURFACE_ID ]]; then
        if power_cmux_surface_exists "$SURFACE_ID" "$WORKSPACE_ID"; then
          power_cmux_close_surface "$SURFACE_ID" "$WORKSPACE_ID" \
            && printf 'fleet-teardown: cmux pane closed\n' \
            || printf 'fleet-teardown: warning: could not close the cmux pane\n' >&2
        else
          printf 'fleet-teardown: cmux pane already gone\n'
        fi
      else
        # Without a surface id there is nothing narrower to close. Say so rather than closing the
        # workspace and taking the siblings down as a side effect.
        printf 'fleet-teardown: warning: member has no recorded pane; leaving the panel alone\n' >&2
      fi
    fi

    # The last member out closes the workspace, and the workspace takes its final pane with it.
    # Closing that pane first is not just redundant, it is refused: cmux answers
    # `invalid_state: Cannot close the last surface`.

    if [[ $CLOSE_WORKSPACE == true ]]; then
      if power_cmux_workspace_exists "$WORKSPACE_ID"; then
        power_cmux_close_workspace "$WORKSPACE_ID" \
          && printf 'fleet-teardown: cmux workspace closed\n' \
          || printf 'fleet-teardown: warning: could not close the cmux workspace\n' >&2
      else
        printf 'fleet-teardown: cmux workspace already gone\n'
      fi
    else
      printf 'fleet-teardown: panel workspace kept for its remaining members\n'
    fi
  else
    printf 'fleet-teardown: cmux is not reachable; leaving its workspace alone\n' >&2
  fi
fi

# ---- merge -----------------------------------------------------------------------------------------

if [[ $MERGE == true ]]; then
  git checkout "$BASE_BRANCH" >/dev/null 2>&1 || fail "cannot check out base branch: $BASE_BRANCH"
  git merge --no-ff -m "merge(power-fleet): $SLUG" "$BRANCH" \
    || fail "merge of $BRANCH into $BASE_BRANCH failed; resolve it manually"
  printf 'fleet-teardown: %s merged into %s\n' "$BRANCH" "$BASE_BRANCH"

  if [[ -d $WORKTREE ]]; then
    git worktree remove "$WORKTREE" >/dev/null 2>&1 || {
      printf 'fleet-teardown: worktree has uncommitted files; leaving it in place at %s\n' "$WORKTREE" >&2
    }
    git worktree prune >/dev/null 2>&1 || true
  fi
else
  printf 'fleet-teardown: branch %s and its worktree were preserved\n' "$BRANCH"
fi

# ---- member record ------------------------------------------------------------------------------------

rm -f "$MEMBER_FILE" "$PANE_FILE" "$FLEET_DIR/$SLUG.surface"
printf 'fleet-teardown: %s torn down\n' "$SLUG"
