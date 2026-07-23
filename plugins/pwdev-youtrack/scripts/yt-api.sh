#!/bin/sh
# yt-api.sh — curl autenticado no YouTrack. O token nunca aparece no comando
# nem na saída: o header de autorização é montado aqui dentro.
#
# Uso:
#   yt-api.sh GET    "/api/agiles?fields=id,name"
#   yt-api.sh POST   "/api/commands" '{"query":"State Fixed","issues":[{"idReadable":"PROJ-1"}]}'
#   yt-api.sh DELETE "/api/issues/PROJ-1/tags/6-0"
#
# Config: YOUTRACK_BASE_URL (obrigatória) e YOUTRACK_TOKEN, ou token no
# Keychain do macOS (service pwdev-youtrack). Rode /pwdev-youtrack:init.

set -eu

METHOD="${1:-}"
PATH_Q="${2:-}"
BODY="${3:-}"

if [ -z "$METHOD" ] || [ -z "$PATH_Q" ]; then
  echo "uso: yt-api.sh METHOD \"/api/...\" ['json-body']" >&2
  exit 2
fi

BASE="${YOUTRACK_BASE_URL:-}"
if [ -z "$BASE" ]; then
  echo "YOUTRACK_BASE_URL ausente — rode /pwdev-youtrack:init" >&2
  exit 1
fi
BASE="${BASE%/}"

TOKEN="${YOUTRACK_TOKEN:-}"
if [ -z "$TOKEN" ] && command -v security >/dev/null 2>&1; then
  TOKEN="$(security find-generic-password -s pwdev-youtrack -w 2>/dev/null || true)"
fi
if [ -z "$TOKEN" ]; then
  echo "Token ausente (YOUTRACK_TOKEN ou Keychain) — rode /pwdev-youtrack:init" >&2
  exit 1
fi

if [ -n "$BODY" ]; then
  curl -sS --fail-with-body -X "$METHOD" \
    -H "Authorization: Bearer $TOKEN" \
    -H "Content-Type: application/json" \
    -H "Accept: application/json" \
    -d "$BODY" \
    "$BASE$PATH_Q"
else
  curl -sS --fail-with-body -X "$METHOD" \
    -H "Authorization: Bearer $TOKEN" \
    -H "Accept: application/json" \
    "$BASE$PATH_Q"
fi
