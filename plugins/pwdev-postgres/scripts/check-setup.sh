#!/bin/sh
# check-setup.sh — diagnóstico da configuração do pwdev-postgres.
# A connection string nunca é impressa com a senha (máscara: usuario:***@host).
#
# Uso:
#   check-setup.sh            # tabela de diagnóstico
#   check-setup.sh --store    # lê a connection string com input mascarado e grava no Keychain

set -u

SERVICE="pwdev-postgres"
PKG="@soarescbm/postgres-mcp"

# Mascara a senha de uma URL postgres:// para exibição segura.
mask_url() {
  u="$1"
  case "$u" in
    *://*:*@*)
      prefix=$(printf '%s' "$u" | sed -n 's|^\([^:]*://[^:/@]*\):.*@.*|\1|p')
      suffix=$(printf '%s' "$u" | sed -n 's|^[^:]*://[^@]*@\(.*\)|\1|p')
      if [ -n "$prefix" ] && [ -n "$suffix" ]; then
        echo "${prefix}:***@${suffix}"
      else
        echo "***"
      fi
      ;;
    *://*@*|*://*)
      echo "$u" ;;
    *)
      echo "***" ;;
  esac
}

# --- modo --store: grava a connection string no Keychain sem ecoar -----------
if [ "${1:-}" = "--store" ]; then
  if ! command -v security >/dev/null 2>&1; then
    echo "Keychain indisponível (não é macOS)." >&2
    echo "Alternativa: adicione ao seu profile do shell:" >&2
    echo '  export PG_MCP_DATABASE_URL="postgresql://usuario:senha@host:5432/banco"' >&2
    exit 1
  fi
  printf "Cole a connection string do Postgres (input oculto): "
  stty -echo 2>/dev/null || true
  read -r URL
  stty echo 2>/dev/null || true
  echo
  if [ -z "$URL" ]; then
    echo "Nada informado — abortado." >&2
    exit 1
  fi
  case "$URL" in
    postgres://*|postgresql://*) : ;;
    *)
      echo "Aviso: a string não começa com postgres:// ou postgresql:// — o servidor pode rejeitar." >&2
      ;;
  esac
  security add-generic-password -a "$USER" -s "$SERVICE" -w "$URL" -U
  echo "Connection string gravada no Keychain (service: $SERVICE) — $(mask_url "$URL")"
  exit 0
fi

# --- diagnóstico ------------------------------------------------------------
printf '%-26s %-12s %s\n' "VERIFICAÇÃO" "STATUS" "DETALHE"
printf '%-26s %-12s %s\n' "-----------" "------" "-------"

# node / npx
if command -v node >/dev/null 2>&1; then
  NODE_MAJOR=$(node -v | sed 's/^v//' | cut -d. -f1)
  if [ "$NODE_MAJOR" -ge 20 ] 2>/dev/null; then
    printf '%-26s %-12s %s\n' "node" "ok" "$(node -v)"
  else
    printf '%-26s %-12s %s\n' "node" "FALHOU" "$(node -v) — o servidor exige >=20"
  fi
else
  printf '%-26s %-12s %s\n' "node" "AUSENTE" "instale Node.js 20+"
fi

if command -v npx >/dev/null 2>&1; then
  printf '%-26s %-12s %s\n' "npx" "ok" ""
else
  printf '%-26s %-12s %s\n' "npx" "AUSENTE" "vem com o Node.js/npm"
fi

# connection string (env ou keychain)
URL="${PG_MCP_DATABASE_URL:-}"
SRC="env"
if [ -z "$URL" ] && command -v security >/dev/null 2>&1; then
  URL="$(security find-generic-password -s "$SERVICE" -w 2>/dev/null || true)"
  SRC="keychain"
fi
if [ -n "$URL" ]; then
  case "$URL" in
    postgres://*|postgresql://*)
      printf '%-26s %-12s %s\n' "PG_MCP_DATABASE_URL" "ok" "$(mask_url "$URL") (via $SRC)" ;;
    *)
      printf '%-26s %-12s %s\n' "PG_MCP_DATABASE_URL" "FALHOU" "deve começar com postgresql:// ou postgres://" ;;
  esac
else
  printf '%-26s %-12s %s\n' "PG_MCP_DATABASE_URL" "AUSENTE" "check-setup.sh --store ou export PG_MCP_DATABASE_URL"
fi

# opcionais
if [ -n "${PG_MCP_STATEMENT_TIMEOUT_MS:-}" ]; then
  printf '%-26s %-12s %s\n' "STATEMENT_TIMEOUT_MS" "ok" "${PG_MCP_STATEMENT_TIMEOUT_MS} ms"
else
  printf '%-26s %-12s %s\n' "STATEMENT_TIMEOUT_MS" "—" "não setado (default 10000 ms)"
fi
if [ -n "${PG_MCP_POOL_MAX:-}" ]; then
  printf '%-26s %-12s %s\n' "POOL_MAX" "ok" "${PG_MCP_POOL_MAX}"
else
  printf '%-26s %-12s %s\n' "POOL_MAX" "—" "não setado (default 5)"
fi

# conexão: psql (completo) ou TCP probe (parcial)
if [ -n "$URL" ]; then
  if command -v psql >/dev/null 2>&1; then
    OUT=$(psql "$URL" -Atc 'select 1' 2>&1)
    if [ "$OUT" = "1" ]; then
      printf '%-26s %-12s %s\n' "conexão (psql)" "ok" "select 1 respondeu"
    else
      DETAIL=$(printf '%s' "$OUT" | head -1 | cut -c1-70)
      printf '%-26s %-12s %s\n' "conexão (psql)" "FALHOU" "$DETAIL"
    fi
  else
    HOSTPORT=$(printf '%s' "$URL" | sed -n 's|^[^:]*://\([^@/]*@\)\{0,1\}\([^/?]*\).*|\2|p')
    HOST=$(printf '%s' "$HOSTPORT" | cut -d: -f1)
    PORT=$(printf '%s' "$HOSTPORT" | cut -sd: -f2)
    [ -z "$PORT" ] && PORT=5432
    if [ -n "$HOST" ] && command -v nc >/dev/null 2>&1; then
      if nc -z -w 5 "$HOST" "$PORT" 2>/dev/null; then
        printf '%-26s %-12s %s\n' "conexão (tcp)" "ok" "$HOST:$PORT aceita conexão (instale psql p/ teste completo)"
      else
        printf '%-26s %-12s %s\n' "conexão (tcp)" "FALHOU" "$HOST:$PORT inacessível — host/porta ou serviço parado"
      fi
    else
      printf '%-26s %-12s %s\n' "conexão" "pulado" "sem psql nem nc — instale psql para testar"
    fi
  fi
else
  printf '%-26s %-12s %s\n' "conexão" "pulado" "config incompleta"
fi

# pacote npm
PKG_VER=$(npm view "$PKG" version 2>/dev/null || true)
if [ -n "$PKG_VER" ]; then
  printf '%-26s %-12s %s\n' "npm $PKG" "ok" "$PKG_VER"
else
  printf '%-26s %-12s %s\n' "npm $PKG" "FALHOU" "sem rede ou pacote indisponível (npx não baixará)"
fi

echo
echo "Config incompleta = plugin em modo consultivo (entrega o passo a passo, não executa)."
echo "SEM a connection string o servidor MCP nem sobe — /mcp mostrará o servidor com erro."
echo "Após alterar env vars, reinicie a sessão do Claude Code."
