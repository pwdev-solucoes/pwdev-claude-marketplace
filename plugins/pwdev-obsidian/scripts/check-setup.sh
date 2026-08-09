#!/bin/sh
# check-setup.sh — diagnóstico da configuração do pwdev-obsidian.
# A API Key nunca é impressa por inteiro (máscara: 5 primeiros + 4 últimos chars).
#
# Uso:
#   check-setup.sh            # tabela de diagnóstico
#   check-setup.sh --store    # lê a API Key com input mascarado e grava no Keychain

set -u

SERVICE="pwdev-obsidian"
DEFAULT_MCP_URL="https://127.0.0.1:27124/mcp/"

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

# --- modo --store: grava a API Key no Keychain sem ecoar -------------------
if [ "${1:-}" = "--store" ]; then
  if ! command -v security >/dev/null 2>&1; then
    echo "Keychain indisponível (não é macOS)." >&2
    echo "Alternativa: adicione ao seu profile do shell:" >&2
    echo '  export OBSIDIAN_API_KEY="sua-api-key"' >&2
    exit 1
  fi
  printf "Cole a API Key da Local REST API (input oculto): "
  stty -echo 2>/dev/null || true
  read -r KEY
  stty echo 2>/dev/null || true
  echo
  if [ -z "$KEY" ]; then
    echo "Nada informado — abortado." >&2
    exit 1
  fi
  security add-generic-password -a "$USER" -s "$SERVICE" -w "$KEY" -U
  echo "API Key gravada no Keychain (service: $SERVICE) — $(mask "$KEY")"
  exit 0
fi

# --- diagnóstico ------------------------------------------------------------
printf '%-24s %-12s %s\n' "VERIFICAÇÃO" "STATUS" "DETALHE"
printf '%-24s %-12s %s\n' "-----------" "------" "-------"

# curl
if command -v curl >/dev/null 2>&1; then
  printf '%-24s %-12s %s\n' "curl" "ok" ""
else
  printf '%-24s %-12s %s\n' "curl" "AUSENTE" "instale curl"
fi

# url do MCP (só informativo — normalmente o default já serve)
MCP_URL="${OBSIDIAN_MCP_URL:-$DEFAULT_MCP_URL}"
printf '%-24s %-12s %s\n' "OBSIDIAN_MCP_URL" "ok" "$MCP_URL"

# base REST (deriva removendo o sufixo /mcp/ ou /mcp)
BASE=$(printf '%s' "$MCP_URL" | sed -e 's|/mcp/*$||')

# API key (env ou keychain)
KEY="${OBSIDIAN_API_KEY:-}"
SRC="env"
if [ -z "$KEY" ] && command -v security >/dev/null 2>&1; then
  KEY="$(security find-generic-password -s "$SERVICE" -w 2>/dev/null || true)"
  SRC="keychain"
fi
if [ -n "$KEY" ]; then
  printf '%-24s %-12s %s\n' "OBSIDIAN_API_KEY" "ok" "$(mask "$KEY") (via $SRC)"
else
  printf '%-24s %-12s %s\n' "OBSIDIAN_API_KEY" "AUSENTE" "check-setup.sh --store ou export OBSIDIAN_API_KEY"
fi

# REST health check — cert self-assinado, -k é obrigatório
if [ -n "$KEY" ]; then
  RESP=$(curl -sSk -m 10 -H "Authorization: Bearer $KEY" "$BASE/" 2>&1)
  CURL_EXIT=$?
  case "$CURL_EXIT" in
    0)
      case "$RESP" in
        *'"authenticated": true'*|*'"authenticated":true'*)
          printf '%-24s %-12s %s\n' "REST $BASE/" "ok" "autenticado" ;;
        *'"authenticated": false'*|*'"authenticated":false'*|*401*|*Unauthorized*)
          printf '%-24s %-12s %s\n' "REST $BASE/" "FALHOU" "API Key inválida — confira em Settings > Local REST API" ;;
        *)
          printf '%-24s %-12s %s\n' "REST $BASE/" "FALHOU" "resposta inesperada — confira OBSIDIAN_MCP_URL" ;;
      esac
      ;;
    7|28)
      printf '%-24s %-12s %s\n' "REST $BASE/" "FALHOU" "sem conexão — Obsidian está aberto? plugin Local REST API ativado?" ;;
    *)
      printf '%-24s %-12s %s\n' "REST $BASE/" "FALHOU" "curl erro $CURL_EXIT" ;;
  esac
else
  printf '%-24s %-12s %s\n' "REST $BASE/" "pulado" "config incompleta"
fi

echo
echo "Config incompleta = plugin em modo consultivo (entrega o passo a passo, não executa)."
echo "'sem conexão' quase sempre significa Obsidian fechado ou plugin Local REST API desativado — não é problema de API Key."
echo "Após alterar env vars, reinicie a sessão do Claude Code."
