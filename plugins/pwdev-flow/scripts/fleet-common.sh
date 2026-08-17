#!/usr/bin/env bash
# Runtime-neutral fleet helpers. Source this file from launch adapters.
set -Eeuo pipefail

flow_require_runtime() {
  case "${1:-}" in codex|claude) ;; *) printf 'unsupported fleet runtime: %s\n' "${1:-}" >&2; return 2;; esac
}
