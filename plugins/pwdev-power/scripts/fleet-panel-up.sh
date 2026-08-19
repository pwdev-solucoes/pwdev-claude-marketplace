#!/usr/bin/env bash
# Provision one to four fleet members and put them side by side in a single cmux workspace, each
# pane an interactive provider session the human can watch and steer.
#
# Never invoked directly. The runtime is pinned by <runtime>-fleet-panel.sh before this runs,
# because a privileged vector chosen by default is a privileged vector chosen by accident.
#
# Why one call and not one split per member: every layout surface carries its own command, so a
# member's session starts from a shell-quoted file exactly like the autonomous runner's does.
# Growing the grid with new-split plus send would type a privileged command into a live shell and
# reintroduce the injection and timing bugs fleet-up.sh avoids on purpose.
set -Eeuo pipefail

SCRIPT_DIR=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd -P)
# shellcheck source=fleet-common.sh
source "$SCRIPT_DIR/fleet-common.sh"
# shellcheck source=cmux-common.sh
source "$SCRIPT_DIR/cmux-common.sh"

fail() { printf 'fleet-panel: %s\n' "$*" >&2; exit 2; }

PANEL_MAX=4

[[ $# -ge 1 ]] || fail 'at least one slug is required'
[[ $# -le $PANEL_MAX ]] || fail "a panel holds at most $PANEL_MAX members, got $#"

for slug in "$@"; do
  [[ $slug =~ ^[a-z0-9][a-z0-9-]*$ && $slug == *[a-z]* && $slug != dashboard ]] \
    || fail "invalid slug: $slug"
done

# Duplicates would provision one member and then collide on the second, after the first has
# already built a worktree. Cheaper to refuse up front.
if [[ $(printf '%s\n' "$@" | sort -u | wc -l) -ne $# ]]; then
  fail 'the same slug was requested more than once'
fi

RUNTIME=${POWER_FLEET_RUNTIME:-}
[[ -n $RUNTIME ]] || fail 'no runtime pinned; launch through <runtime>-fleet-panel.sh'
power_require_runtime "$RUNTIME" || exit 2

command -v jq >/dev/null 2>&1 || fail 'jq is required'
command -v git >/dev/null 2>&1 || fail 'git is required'

REPO_ROOT=$(git rev-parse --show-toplevel 2>/dev/null) || fail 'not inside a Git repository'
REPO_ROOT=$(cd "$REPO_ROOT" && pwd -P)
FLEET_DIR=$REPO_ROOT/.planning/power/fleet

power_cmux_require --start || fail 'cmux is required for a panel'

# One panel at a time. A second one could not reuse the first's workspace without splitting into
# it and typing a command in, so the honest answer is to refuse and say why.
if [[ -d $FLEET_DIR ]]; then
  shopt -s nullglob
  for member in "$FLEET_DIR"/*.json; do
    if jq -e '.mode == "visual" and (.cmux_workspace_id | type == "string")' "$member" >/dev/null 2>&1; then
      fail "a visual fleet panel is already active ($(basename "$member" .json)); tear it down first"
    fi
  done
  shopt -u nullglob
fi

LAUNCHER=$SCRIPT_DIR/fleet-up.sh
[[ -f $LAUNCHER ]] || fail "missing launcher: $LAUNCHER"

# ---- provision ------------------------------------------------------------------------------
# Members are provisioned one at a time and the first failure stops the run. Whatever already
# succeeded is kept and shown: a member that failed is evidence, and destroying its siblings to
# tidy up would destroy the evidence with them.

PROVISIONED=()
FAILED=

for slug in "$@"; do
  if POWER_FLEET_MODE=visual POWER_FLEET_DEFER_WORKSPACE=1 "$LAUNCHER" "$slug"; then
    PROVISIONED+=("$slug")
  else
    FAILED=$slug
    break
  fi
done

if [[ ${#PROVISIONED[@]} -eq 0 ]]; then
  fail "no member could be provisioned (first failure: ${FAILED:-unknown})"
fi

# ---- layout ---------------------------------------------------------------------------------
# One pane per member: a column for one, side by side for two, a 2x2 grid from three. Nesting
# direction nodes inside children is undocumented but accepted, and it is what makes the grid a
# single call.

pane_node() {
  jq -n --arg cmd "bash $FLEET_DIR/$1.pane.sh" \
    '{pane: {surfaces: [{type: "terminal", command: $cmd}]}}'
}

row() { jq -n --argjson a "$1" --argjson b "$2" \
  '{direction: "horizontal", split: 0.5, children: [$a, $b]}'; }

stack() { jq -n --argjson a "$1" --argjson b "$2" \
  '{direction: "vertical", split: 0.5, children: [$a, $b]}'; }

P0=$(pane_node "${PROVISIONED[0]}")
case ${#PROVISIONED[@]} in
  1) LAYOUT=$P0 ;;
  2) LAYOUT=$(row "$P0" "$(pane_node "${PROVISIONED[1]}")") ;;
  3) LAYOUT=$(stack "$(row "$P0" "$(pane_node "${PROVISIONED[1]}")")" "$(pane_node "${PROVISIONED[2]}")") ;;
  4) LAYOUT=$(stack "$(row "$P0" "$(pane_node "${PROVISIONED[1]}")")" \
                    "$(row "$(pane_node "${PROVISIONED[2]}")" "$(pane_node "${PROVISIONED[3]}")")") ;;
  *) fail "unexpected member count: ${#PROVISIONED[@]}" ;;
esac

# Stale registrations from an interrupted run would be read as this run's answer.
for slug in "${PROVISIONED[@]}"; do rm -f "$FLEET_DIR/$slug.surface"; done

WORKSPACE_ID=$(power_cmux_new_workspace_layout \
  "power-fleet panel" "$REPO_ROOT" "$LAYOUT") \
  || fail 'cannot create the panel workspace'
[[ -n $WORKSPACE_ID ]] || fail 'cmux did not return a workspace id'

power_cmux_status "$WORKSPACE_ID" "panel ${#PROVISIONED[@]} member(s)"
power_cmux_color "$WORKSPACE_ID" Blue

# ---- bind members to their surfaces -----------------------------------------------------------
# Each pane writes its own CMUX_SURFACE_ID before exec-ing the provider, so the binding is the
# pane's own report rather than an assumption that layout order equals pane order.

# macOS ships bash 3.2, where expanding an empty array under `set -u` is an unbound-variable
# error rather than an empty list. The ${x[@]+"${x[@]}"} guard is what makes "all panes reported"
# — the success case — not crash the launcher.
DEADLINE=$((SECONDS + 30))
PENDING=("${PROVISIONED[@]}")
while [[ ${#PENDING[@]} -gt 0 && $SECONDS -lt $DEADLINE ]]; do
  REMAINING=()
  for slug in "${PENDING[@]}"; do
    [[ -s $FLEET_DIR/$slug.surface ]] || REMAINING+=("$slug")
  done
  PENDING=(${REMAINING[@]+"${REMAINING[@]}"})
  [[ ${#PENDING[@]} -gt 0 ]] && sleep 1
done

UNBOUND=()
for slug in "${PROVISIONED[@]}"; do
  member=$FLEET_DIR/$slug.json
  surface=
  [[ -s $FLEET_DIR/$slug.surface ]] && surface=$(<"$FLEET_DIR/$slug.surface")

  if [[ -z $surface ]]; then
    UNBOUND+=("$slug")
  fi

  temp=$(mktemp "$FLEET_DIR/.$slug.json.XXXXXX") || fail 'cannot stage member update'
  jq --arg ws "$WORKSPACE_ID" --arg surface "$surface" \
     '.cmux_workspace_id = $ws
      | .cmux_surface_id = (if $surface == "" then null else $surface end)
      | .updated_at = (now | todateiso8601)' \
     "$member" >"$temp" || { rm -f "$temp"; fail "cannot update member: $slug"; }
  mv "$temp" "$member" || fail "cannot publish member update: $slug"
done

# ---- report -----------------------------------------------------------------------------------

printf 'fleet-panel: %d member(s) on %s in one workspace: %s\n' \
  "${#PROVISIONED[@]}" "$RUNTIME" "${PROVISIONED[*]}"

if [[ ${#UNBOUND[@]} -gt 0 ]]; then
  printf 'fleet-panel: warning: no surface id reported by: %s\n' "${UNBOUND[*]}" >&2
  printf 'fleet-panel: tearing those members down will close the whole panel, not just their pane\n' >&2
fi

if [[ -n $FAILED ]]; then
  printf 'fleet-panel: %s failed to provision; the panel holds the members that succeeded\n' "$FAILED" >&2
  exit 1
fi
