#!/usr/bin/env bash
# Runtime-neutral fleet helpers. Source this file from launch/run adapters.
set -Eeuo pipefail

flow_require_runtime() {
  case "${1:-}" in codex|claude) ;; *) printf 'unsupported fleet runtime: %s\n' "${1:-}" >&2; return 2;; esac
}
flow_require_regular() { [[ -f "$1" && ! -L "$1" ]]; }
flow_require_no_symlink_path() {
  local path=$1 part current; current=${2:-$(pwd -P)}
  [[ "$path" != /* && "$path" != *..* ]] || return 1
  while IFS= read -r part; do [[ -z "$part" || "$part" == . || "$part" == .. ]] && continue; [[ ! -L "$current/$part" ]] || return 1; current="$current/$part"; done < <(printf '%s\n' "$path" | tr '/' '\n')
}
flow_json_runtime() { jq -er '.runtime | select(. == "codex" or . == "claude")' "$1"; }
