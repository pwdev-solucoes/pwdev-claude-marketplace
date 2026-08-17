#!/usr/bin/env bash
# Guarded standalone external-provider runner for PWDEV Flow.
set -Eeuo pipefail

ALLOWLIST="codex opencode kimi gemini kiro"
DEFAULT_TIMEOUT_S=600
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

usage() {
  echo "usage: run-agent.sh [--preview] <codex|opencode|kimi|gemini|kiro> <write|read> <task>" >&2
  exit 2
}

PREVIEW=false
if [[ ${1:-} == --preview ]]; then PREVIEW=true; shift; fi
[[ $# -ge 3 ]] || usage
AGENT="$1"
MODE="$2"
shift 2
TASK="$*"
[[ -n "$TASK" ]] || usage

case " $ALLOWLIST " in *" $AGENT "*) ;; *) exit 2 ;; esac
case "$MODE" in write|read) ;; *) exit 2 ;; esac

TOPLEVEL="$(git rev-parse --show-toplevel 2>/dev/null)" || {
  echo "run-agent.sh must be run inside a Git repository" >&2
  exit 2
}
cd "$TOPLEVEL"

safe_repo_dir() {
  local relative=$1 create=${2:-false} current=$TOPLEVEL component next canonical
  local old_ifs=$IFS
  [[ $relative != /* && $relative != *..* ]] || return 1
  IFS=/
  for component in $relative; do
    [[ -n $component && $component != . ]] || continue
    next=$current/$component
    [[ ! -L $next ]] || { IFS=$old_ifs; return 1; }
    if [[ -e $next ]]; then
      [[ -d $next ]] || { IFS=$old_ifs; return 1; }
    else
      [[ $create == true ]] || { IFS=$old_ifs; return 1; }
      mkdir "$next" || { IFS=$old_ifs; return 1; }
      [[ ! -L $next && -d $next ]] || { IFS=$old_ifs; return 1; }
    fi
    canonical=$(cd -- "$next" 2>/dev/null && pwd -P) || { IFS=$old_ifs; return 1; }
    case $canonical in "$TOPLEVEL"|"$TOPLEVEL"/*) ;; *) IFS=$old_ifs; return 1 ;; esac
    current=$canonical
  done
  IFS=$old_ifs
}

require_repo_regular() {
  local path=$1
  [[ -e $path && -f $path && ! -L $path ]]
}

BINARY="$AGENT"
[[ "$AGENT" == "kiro" ]] && BINARY="kiro-cli"

CONFIG_PATH=".planning/flow/config.json"
MODEL=""
TIMEOUT_S="$DEFAULT_TIMEOUT_S"
AUDIT_ENABLED=false
EXTRA_ARGS=()

config_error() {
  echo "invalid Flow external-provider configuration" >&2
  exit 2
}

if [[ -e "$CONFIG_PATH" ]]; then
  safe_repo_dir .planning/flow false || config_error
  require_repo_regular "$CONFIG_PATH" || config_error
  command -v jq >/dev/null 2>&1 || config_error

  # Validate before extracting anything. In particular, this avoids shell word
  # splitting or type coercion for JSON values supplied by configuration.
  jq -e --arg agent "$AGENT" '
    def provider: (.external_models[$agent] // {});
    type == "object"
    and ((.external_models // {}) | type == "object")
    and (provider | type == "object")
    and (provider | ((has("model") | not) or (.model | type == "string")))
    and (provider | ((has("timeout_s") | not) or (.timeout_s | type == "number" and . > 0 and floor == .)))
    and (provider | ((has("extra_args") | not) or (.extra_args | type == "array" and all(.[]; type == "string" and index("\u0000") == null))))
  ' "$CONFIG_PATH" >/dev/null 2>&1 || config_error

  MODEL="$(jq -r --arg agent "$AGENT" '.external_models[$agent].model // empty' "$CONFIG_PATH")"
  TIMEOUT_S="$(jq -r --arg agent "$AGENT" '.external_models[$agent].timeout_s // 600' "$CONFIG_PATH")"
  [[ "$(jq -r '.audit == true' "$CONFIG_PATH")" == "true" ]] && AUDIT_ENABLED=true

  # NUL-delimited jq output lets every array element remain exactly one Bash
  # argument, including values containing spaces, semicolons, or newlines.
  while IFS= read -r -d '' extra_arg; do
    EXTRA_ARGS+=("$extra_arg")
  done < <(jq -j --arg agent "$AGENT" '.external_models[$agent].extra_args // [] | .[] | . + "\u0000"' "$CONFIG_PATH")
fi

reject_unsafe_extra_args() {
  local extra_arg
  (( ${#EXTRA_ARGS[@]} > 0 )) || return 0
  # Codex exposes many aliases and generic configuration overrides that can
  # recreate an unrestricted execution vector. Standalone Codex therefore
  # fails closed for configured extra arguments; its typed model field is the
  # only optional provider setting accepted by this wrapper.
  [[ $AGENT != codex ]] || config_error
  for extra_arg in "${EXTRA_ARGS[@]}"; do
    # These options can weaken the fixed standalone safety boundary or change
    # its repository root. They are not delegable configuration.
    case "$extra_arg" in
      --dangerously-bypass-approvals-and-sandbox|--dangerously-bypass-approvals-and-sandbox=*|--cd|--cd=*|-C|-C*)
        config_error
        ;;
    esac

    case "$AGENT:$MODE:$extra_arg" in
      # The runner fixes Kiro's interaction mode, and read mode must never
      # grant the write-only blanket tools permission.
      kiro:*:--interactive|kiro:*:--interactive=*|kiro:read:--trust-all-tools|kiro:read:--trust-all-tools=*)
        config_error
        ;;
      # The runner owns the mandatory prompt and places it as the final,
      # single argument for providers that expose a prompt option.
      kimi:*:--prompt|kimi:*:--prompt=*|gemini:*:--prompt|gemini:*:--prompt=*)
        config_error
        ;;
    esac
  done
}
reject_unsafe_extra_args

command -v "$BINARY" >/dev/null 2>&1 || {
  echo "external provider binary not found: $BINARY" >&2
  exit 127
}

FLOW_STATE=false
if [[ -e .planning/flow || -L .planning/flow ]]; then
  safe_repo_dir .planning/flow false || config_error
  FLOW_STATE=true
fi

LOCK_DIR=""

repo_status() {
  git status --porcelain -- . ':(exclude).planning/flow/delegation'
}
STATUS_BEFORE="$(repo_status)"

build_prompt() {
  local mode_instruction
  if [[ "$MODE" == "write" ]]; then
    mode_instruction="WRITE — you may create or modify repository files only when necessary for the task."
  else
    mode_instruction="READ-ONLY — analysis only. You MUST NOT create, modify, or delete any file."
  fi

  cat <<EOF
You are working inside the Git repository at: $TOPLEVEL
MODE: $mode_instruction

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

# Build argument vectors only. Configuration values are individual array
# elements and are never evaluated as shell source or interpolated into a
# command string.
CMD=()
append_extra_args() {
  # Bash 3.2 treats an empty array expansion as unset under `set -u`.
  if (( ${#EXTRA_ARGS[@]} > 0 )); then
    CMD+=("${EXTRA_ARGS[@]}")
  fi
}
case "$AGENT" in
  codex)
    CMD=(codex exec --ephemeral --cd "$TOPLEVEL")
    [[ -n "$MODEL" ]] && CMD+=(--model "$MODEL")
    CMD+=("$PROMPT")
    ;;
  opencode)
    CMD=(opencode run)
    [[ -n "$MODEL" ]] && CMD+=(--model "$MODEL")
    append_extra_args
    CMD+=("$PROMPT")
    ;;
  kimi)
    CMD=(kimi --quiet)
    append_extra_args
    if kimi --help </dev/null 2>/dev/null | grep -q -- '--prompt'; then
      CMD+=(--prompt "$PROMPT")
    else
      CMD+=("$PROMPT")
    fi
    ;;
  gemini)
    CMD=(gemini)
    [[ -n "$MODEL" ]] && CMD+=(--model "$MODEL")
    append_extra_args
    CMD+=(--prompt "$PROMPT")
    ;;
  kiro)
    CMD=(kiro-cli chat --no-interactive)
    [[ "$MODE" == "write" ]] && CMD+=(--trust-all-tools)
    append_extra_args
    CMD+=("$PROMPT")
    ;;
esac

render_provider_argv() {
  local argument
  printf 'provider argv:'
  for argument in "${CMD[@]}"; do printf ' %q' "$argument"; done
  printf '\n'
}
PROVIDER_ARGV=$(render_provider_argv)
# The token authorizes one exact argument vector, and the task text that feeds
# that vector is attacker-influenceable, so the binding must be a cryptographic
# digest: a CRC is cheap to collide, which would let a stale token authorize a
# different command.
command -v shasum >/dev/null 2>&1 || {
  echo "run-agent.sh: shasum is required to bind the confirmation token" >&2
  exit 2
}
CONFIRMATION_TOKEN=$(printf '%s' "$PROVIDER_ARGV" | shasum -a 256 | awk '{print $1}')
[[ $CONFIRMATION_TOKEN =~ ^[0-9a-f]{64}$ ]] || {
  echo "run-agent.sh: could not derive the confirmation token" >&2
  exit 2
}
printf '%s\nconfirmation token: %s\n' "$PROVIDER_ARGV" "$CONFIRMATION_TOKEN"
if [[ $PREVIEW == true ]]; then exit 0; fi
if [[ ${FLOW_DELEGATION_CONFIRM_TOKEN:-} != "$CONFIRMATION_TOKEN" ]]; then
  echo "run-agent.sh: exact provider argv was not confirmed; run with --preview first" >&2
  exit 5
fi
if [[ "$MODE" == "write" ]]; then
  safe_repo_dir .planning/flow/delegation true || {
    echo "run-agent.sh: unsafe delegation state path" >&2
    exit 2
  }
  FLOW_STATE=true
  LOCK_DIR=".planning/flow/delegation/.lock"
  if ! mkdir "$LOCK_DIR" 2>/dev/null; then
    echo "another write delegation holds $LOCK_DIR" >&2
    exit 4
  fi
  trap '[[ -z "${LOCK_DIR:-}" ]] || rmdir "$LOCK_DIR" 2>/dev/null || true' EXIT
fi

TIMEOUT_BIN=""
for candidate in timeout gtimeout; do
  if command -v "$candidate" >/dev/null 2>&1; then
    TIMEOUT_BIN="$candidate"
    break
  fi
done
[[ -n "$TIMEOUT_BIN" ]] || echo "warning: timeout/gtimeout unavailable; running without a time limit" >&2

OUT=""
if [[ "$FLOW_STATE" == true ]]; then
  safe_repo_dir .planning/flow/delegation true || {
    echo "run-agent.sh: unsafe delegation state path" >&2
    exit 2
  }
  out_reservation="$(mktemp ".planning/flow/delegation/$(date -u +%Y%m%dT%H%M%SZ)-$AGENT.XXXXXX")"
  OUT="${out_reservation}.md"
  # mktemp only reserves the bare template; the published `.md` destination is a
  # separate name, so validate it before the rename. Without this, `mv` and the
  # later `tee -a` would follow a symlink planted at that path.
  if [[ -e $OUT || -L $OUT ]]; then
    rm -f "$out_reservation"
    echo "run-agent.sh: delegation output destination already exists" >&2
    exit 2
  fi
  mv "$out_reservation" "$OUT"
  require_repo_regular "$OUT" || {
    echo "run-agent.sh: delegation output destination is unsafe" >&2
    exit 2
  }
  # Keep the standardized prompt with the provider output as an execution
  # record; audit logging deliberately never receives either value.
  printf '%s\n\n' "$PROMPT" >"$OUT"
fi

echo "delegating to $AGENT (mode: $MODE, timeout: ${TIMEOUT_S}s)"
set +e
if [[ -n "$TIMEOUT_BIN" ]]; then
  if [[ -n "$OUT" ]]; then
    "$TIMEOUT_BIN" "$TIMEOUT_S" "${CMD[@]}" </dev/null 2>&1 | tee -a "$OUT"
    RC=${PIPESTATUS[0]}
  else
    "$TIMEOUT_BIN" "$TIMEOUT_S" "${CMD[@]}" </dev/null
    RC=$?
  fi
else
  if [[ -n "$OUT" ]]; then
    "${CMD[@]}" </dev/null 2>&1 | tee -a "$OUT"
    RC=${PIPESTATUS[0]}
  else
    "${CMD[@]}" </dev/null
    RC=$?
  fi
fi
set -e

if [[ "$MODE" == "read" && "$STATUS_BEFORE" != "$(repo_status)" ]]; then
  echo "READ-ONLY VIOLATION: $AGENT modified the working tree" >&2
  exit 3
fi

# Audit is best-effort so its result cannot replace the provider result. Report
# only the semantic action name on failure; never echo audit input or output.
if [[ "$AUDIT_ENABLED" == true && -f "$SCRIPT_DIR/flow_audit.py" ]]; then
  if ! python3 "$SCRIPT_DIR/flow_audit.py" --root "$TOPLEVEL" record \
    --action external_run --skill flow-delegate --target "$AGENT" \
    --detail "{\"provider\":\"$AGENT\",\"mode\":\"$MODE\",\"exit\":$RC,\"timeout_s\":$TIMEOUT_S}" \
    >/dev/null 2>&1; then
    echo "warning: external_run audit record failed" >&2
  fi
fi

[[ "$RC" -ne 124 ]] || echo "$AGENT timed out after ${TIMEOUT_S}s" >&2
exit "$RC"
