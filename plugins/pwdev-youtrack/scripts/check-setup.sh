#!/bin/sh
# check-setup.sh — diagnóstico da configuração do pwdev-youtrack.
# O token nunca é impresso por inteiro (máscara: 5 primeiros + 4 últimos chars).
#
# Uso:
#   check-setup.sh            # tabela de diagnóstico
#   check-setup.sh --store    # lê o token com input mascarado e grava no Keychain

set -u

SERVICE="pwdev-youtrack"

mask() {
  t="$1"
  n=${#t}
  if [ "$n" -le 12 ]; then
    echo "***"
  else
    head5=$(printf '%s' "$t" | cut -c1-5)
    tail4=$(printf '%s' "$t" | rev | cut -c1-4 | rev)
    echo "${head5}***…${tail4}"
  fi
}

# --- modo --store: grava o token no Keychain sem ecoar ---------------------
if [ "${1:-}" = "--store" ]; then
  if ! command -v security >/dev/null 2>&1; then
    echo "Keychain indisponível (não é macOS)." >&2
    echo "Alternativa: adicione ao seu profile do shell:" >&2
    echo '  export YOUTRACK_TOKEN="perm-..."' >&2
    exit 1
  fi
  printf "Cole o permanent token do YouTrack (input oculto): "
  stty -echo 2>/dev/null || true
  read -r TOKEN
  stty echo 2>/dev/null || true
  echo
  if [ -z "$TOKEN" ]; then
    echo "Nada informado — abortado." >&2
    exit 1
  fi
  security add-generic-password -a "$USER" -s "$SERVICE" -w "$TOKEN" -U
  echo "Token gravado no Keychain (service: $SERVICE) — $(mask "$TOKEN")"
  exit 0
fi

# --- diagnóstico ------------------------------------------------------------
printf '%-22s %-12s %s\n' "VERIFICAÇÃO" "STATUS" "DETALHE"
printf '%-22s %-12s %s\n' "-----------" "------" "-------"

# curl
if command -v curl >/dev/null 2>&1; then
  printf '%-22s %-12s %s\n' "curl" "ok" ""
else
  printf '%-22s %-12s %s\n' "curl" "AUSENTE" "instale curl"
fi

# base url
BASE="${YOUTRACK_BASE_URL:-}"
if [ -n "$BASE" ]; then
  printf '%-22s %-12s %s\n' "YOUTRACK_BASE_URL" "ok" "$BASE"
else
  printf '%-22s %-12s %s\n' "YOUTRACK_BASE_URL" "AUSENTE" "export no profile + reinicie a sessão"
fi

# token (env ou keychain)
TOKEN="${YOUTRACK_TOKEN:-}"
SRC="env"
if [ -z "$TOKEN" ] && command -v security >/dev/null 2>&1; then
  TOKEN="$(security find-generic-password -s "$SERVICE" -w 2>/dev/null || true)"
  SRC="keychain"
fi
if [ -n "$TOKEN" ]; then
  printf '%-22s %-12s %s\n' "token" "ok" "$(mask "$TOKEN") (via $SRC)"
else
  printf '%-22s %-12s %s\n' "token" "AUSENTE" "check-setup.sh --store ou export YOUTRACK_TOKEN"
fi

# REST: /api/users/me
if [ -n "$BASE" ] && [ -n "$TOKEN" ]; then
  BASE="${BASE%/}"
  ME=$(curl -sS -m 15 -H "Authorization: Bearer $TOKEN" \
        "$BASE/api/users/me?fields=login,name" 2>/dev/null || true)
  case "$ME" in
    *'"login"'*)
      LOGIN=$(printf '%s' "$ME" | sed -n 's/.*"login":"\([^"]*\)".*/\1/p')
      printf '%-22s %-12s %s\n' "REST /api/users/me" "ok" "login: $LOGIN" ;;
    *Unauthorized*|*401*)
      printf '%-22s %-12s %s\n' "REST /api/users/me" "FALHOU" "401 — token inválido ou expirado" ;;
    *)
      printf '%-22s %-12s %s\n' "REST /api/users/me" "FALHOU" "sem resposta válida — confira a URL" ;;
  esac

  # MCP endpoint
  MCP_CODE=$(curl -sS -o /dev/null -m 15 -w '%{http_code}' \
        -H "Authorization: Bearer $TOKEN" "$BASE/mcp" 2>/dev/null || echo "000")
  case "$MCP_CODE" in
    2*|405|406)
      printf '%-22s %-12s %s\n' "MCP $BASE/mcp" "ok" "http $MCP_CODE" ;;
    404)
      printf '%-22s %-12s %s\n' "MCP $BASE/mcp" "FALHOU" "404 — instância < 2025.3 (sem MCP embutido)" ;;
    401|403)
      printf '%-22s %-12s %s\n' "MCP $BASE/mcp" "FALHOU" "http $MCP_CODE — auth recusada no endpoint MCP" ;;
    *)
      printf '%-22s %-12s %s\n' "MCP $BASE/mcp" "FALHOU" "http $MCP_CODE" ;;
  esac
else
  printf '%-22s %-12s %s\n' "REST /api/users/me" "pulado" "config incompleta"
  printf '%-22s %-12s %s\n' "MCP endpoint" "pulado" "config incompleta"
fi

echo
echo "Config incompleta = plugin em modo consultivo (entrega o comando, não executa)."
echo "Após alterar env vars, reinicie a sessão do Claude Code."
