#!/bin/bash
# fleet-run.sh — the headless pipeline driver for one /pwdev-code:fleet
# member. Runs INSIDE the tmux window fleet-up.sh created for this slug.
# Sequentially invokes `claude -p` for plan → execute → review → verify
# (with a bounded fix loop), all unattended, inside the isolated worktree
# fleet-up.sh already created and pointed a docker-compose stack at.
#
# Usage:
#   fleet-run.sh <phase-slug> <worktree-path> [permission-mode]
#
# Never merges, never pushes, never touches anything outside this worktree.
# On any halt condition it writes .planning/fleet-status.json with
# status=NEEDS_HUMAN and a reason, then returns (the caller keeps the tmux
# pane open so a human can read the log and intervene).
set -Eeuo pipefail

SLUG="${1:-}"
WORKTREE="${2:-}"
PERMISSION_MODE="${3:-bypassPermissions}"
MAX_FIX_ITERATIONS=2

[ -n "$SLUG" ] && [ -n "$WORKTREE" ] || { echo "usage: fleet-run.sh <slug> <worktree-path> [permission-mode]" >&2; exit 2; }
cd "$WORKTREE"
mkdir -p .planning

LOG_DIR=".planning/fleet-logs"
mkdir -p "$LOG_DIR"

status_write() {
  # status_write <stage> <status: RUNNING|NEEDS_HUMAN|DONE> <message>
  local stage="$1" status="$2" message="$3"
  jq -n --arg slug "$SLUG" --arg stage "$stage" --arg status "$status" \
        --arg message "$message" --arg updated_at "$(date -u +%Y-%m-%dT%H:%M:%SZ)" \
    '{slug:$slug, stage:$stage, status:$status, message:$message, updated_at:$updated_at}' \
    > .planning/fleet-status.json
}

commit_stage_artifacts() {
  local stage="$1"
  git add -A -- .planning >/dev/null 2>&1 || true
  if ! git diff --cached --quiet 2>/dev/null; then
    git commit -q -m "chore(fleet): ${SLUG} — ${stage} artifacts" || true
  fi
}

# Wraps a command's own instructions with an override for unattended runs:
# wherever the command says "wait for approval" / "ask the human", proceed
# with the best-judgment default instead — there is no human in this pane.
# Any genuine stop condition must end with a FLEET_* marker line instead of
# a question, so this script can grep it deterministically.
autonomous_prompt() {
  local base="$1" extra_markers="$2"
  cat <<EOF
${base}

AUTONOMOUS FLEET MODE — you are running headless and unattended inside an
isolated git worktree, with no human able to answer questions or approve
anything in this turn. Apply these overrides:
- Wherever this command's instructions say to "wait for approval", "ask the
  human", present a y/n choice, or pause for confirmation: proceed
  automatically with the best-judgment default instead of pausing.
- The ONLY exception is a genuine stop condition this command itself defines
  (e.g. STOPPED:<condition>, a prohibited/destructive action, a missing
  prerequisite this command cannot resolve, review_gate BLOCKED with no
  auto-fix path). Do not guess through those — report them instead.
- End your final response with these machine-readable marker line(s), exactly
  as specified, in addition to your normal summary:
${extra_markers}
EOF
}

# run_stage <stage-name> <slash-command-text> <extra-marker-instructions>
# Returns the log file path on stdout; caller inspects it for markers.
run_stage() {
  local stage="$1" slash_cmd="$2" markers="$3"
  local log="${LOG_DIR}/${stage}-$(date -u +%Y%m%dT%H%M%SZ).log"
  status_write "$stage" "RUNNING" "starting ${stage}"
  local prompt
  prompt="$(autonomous_prompt "$slash_cmd" "$markers")"
  set +e
  claude -p "$prompt" --permission-mode "$PERMISSION_MODE" </dev/null >"$log" 2>&1
  local rc=$?
  set -e
  commit_stage_artifacts "$stage"
  if [ "$rc" -ne 0 ]; then
    status_write "$stage" "NEEDS_HUMAN" "claude exited ${rc} during ${stage} — see ${log}"
    echo "$log"
    return 1
  fi
  echo "$log"
  return 0
}

halt() {
  local stage="$1" reason="$2"
  status_write "$stage" "NEEDS_HUMAN" "$reason"
  echo "🛑 ${SLUG}: NEEDS_HUMAN at ${stage} — ${reason}"
  exit 1
}

echo "▶ fleet-run: ${SLUG} in ${WORKTREE} (permission-mode=${PERMISSION_MODE})"

# --- STAGE 1: plan ---
LOG=$(run_stage "plan" "/pwdev-code:plan ${SLUG}" \
  "FLEET_PLAN_STATUS: OK  (plans were generated and saved)
FLEET_PLAN_STATUS: FAILED: <one-line reason>  (spec non-decomposable, circular deps, etc.)") \
  || halt "plan" "claude invocation failed — see log"
grep -q "FLEET_NEEDS_HUMAN:" "$LOG" && halt "plan" "$(grep 'FLEET_NEEDS_HUMAN:' "$LOG" | tail -1)"
grep -q "FLEET_PLAN_STATUS: FAILED" "$LOG" && halt "plan" "$(grep 'FLEET_PLAN_STATUS: FAILED' "$LOG" | tail -1)"
ls .planning/phases/"${SLUG}"/plans/*.md >/dev/null 2>&1 || halt "plan" "no plan files were written"

# --- STAGE 2: execute (loops all waves internally) ---
LOG=$(run_stage "execute" "/pwdev-code:execute" \
  "FLEET_EXECUTE_STATUS: OK  (all planned tasks completed)
FLEET_EXECUTE_STATUS: STOPPED: <condition>  (a task hit a genuine stop condition)
FLEET_EXECUTE_STATUS: FAILED: <reason>  (a task failed twice)") \
  || halt "execute" "claude invocation failed — see log"
grep -q "FLEET_NEEDS_HUMAN:" "$LOG" && halt "execute" "$(grep 'FLEET_NEEDS_HUMAN:' "$LOG" | tail -1)"
grep -qE "FLEET_EXECUTE_STATUS: (STOPPED|FAILED)" "$LOG" && halt "execute" "$(grep -E 'FLEET_EXECUTE_STATUS: (STOPPED|FAILED)' "$LOG" | tail -1)"

# --- STAGE 3: review ---
LOG=$(run_stage "review" "/pwdev-code:review" \
  "FLEET_REVIEW_GATE: OK  (no critical findings)
FLEET_REVIEW_GATE: BLOCKED  (critical findings open)") \
  || halt "review" "claude invocation failed — see log"
grep -q "FLEET_NEEDS_HUMAN:" "$LOG" && halt "review" "$(grep 'FLEET_NEEDS_HUMAN:' "$LOG" | tail -1)"
grep -q "FLEET_REVIEW_GATE: BLOCKED" "$LOG" && halt "review" "review_gate BLOCKED — inspect .planning/phases/${SLUG}/review/code-review.md, fix manually or re-run /pwdev-code:execute --fix in this worktree, then re-review/verify by hand"

# --- STAGE 4: verify, with a bounded fix loop (mirrors execute.md's own
#     documented --fix transition: execute --fix, scoped re-review, re-verify) ---
FIX_ITER=0
while true; do
  LOG=$(run_stage "verify" "/pwdev-code:verify --strict" \
    "FLEET_VERIFY_VERDICT: APPROVED
FLEET_VERIFY_VERDICT: CAVEATS
FLEET_VERIFY_VERDICT: REJECTED
(exactly one of the three, based on the worst of the two --strict lenses)") \
    || halt "verify" "claude invocation failed — see log"
  grep -q "FLEET_NEEDS_HUMAN:" "$LOG" && halt "verify" "$(grep 'FLEET_NEEDS_HUMAN:' "$LOG" | tail -1)"

  if grep -q "FLEET_VERIFY_VERDICT: APPROVED\|FLEET_VERIFY_VERDICT: CAVEATS" "$LOG"; then
    status_write "verify" "DONE" "verified after ${FIX_ITER} fix iteration(s)"
    echo "✅ ${SLUG}: DONE ($(grep -o 'FLEET_VERIFY_VERDICT: [A-Z]*' "$LOG" | tail -1))"
    exit 0
  fi

  if ! grep -q "FLEET_VERIFY_VERDICT: REJECTED" "$LOG"; then
    halt "verify" "could not determine a verdict from the verify output — see ${LOG}"
  fi

  FIX_ITER=$((FIX_ITER + 1))
  if [ "$FIX_ITER" -gt "$MAX_FIX_ITERATIONS" ]; then
    halt "verify" "rejected after ${MAX_FIX_ITERATIONS} fix iterations — escalating, see .planning/phases/${SLUG}/verify/"
  fi

  FIX_START_SHA="$(git rev-parse HEAD)"
  LOG=$(run_stage "execute-fix" "/pwdev-code:execute --fix" \
    "FLEET_EXECUTE_STATUS: OK
FLEET_EXECUTE_STATUS: STOPPED: <condition>
FLEET_EXECUTE_STATUS: FAILED: <reason>") \
    || halt "execute-fix" "claude invocation failed — see log"
  grep -q "FLEET_NEEDS_HUMAN:" "$LOG" && halt "execute-fix" "$(grep 'FLEET_NEEDS_HUMAN:' "$LOG" | tail -1)"
  grep -qE "FLEET_EXECUTE_STATUS: (STOPPED|FAILED)" "$LOG" && halt "execute-fix" "$(grep -E 'FLEET_EXECUTE_STATUS: (STOPPED|FAILED)' "$LOG" | tail -1)"

  FIX_RANGE="${FIX_START_SHA}..HEAD"
  LOG=$(run_stage "review-fix" "/pwdev-code:review --diff ${FIX_RANGE}" \
    "FLEET_REVIEW_GATE: OK
FLEET_REVIEW_GATE: BLOCKED") \
    || halt "review-fix" "claude invocation failed — see log"
  grep -q "FLEET_NEEDS_HUMAN:" "$LOG" && halt "review-fix" "$(grep 'FLEET_NEEDS_HUMAN:' "$LOG" | tail -1)"
  grep -q "FLEET_REVIEW_GATE: BLOCKED" "$LOG" && halt "review-fix" "review_gate BLOCKED after fix iteration ${FIX_ITER} — needs a human"

  # loop back to verify
done
