#!/bin/sh
# check-setup.sh — diagnóstico da configuração do pwdev-glpi.
# O PAT nunca é impresso por inteiro (máscara: 5 primeiros + 4 últimos chars).
#
# Uso:
#   check-setup.sh            # tabela de diagnóstico
#   check-setup.sh --store    # lê o PAT com input mascarado e grava no Keychain

set -u

SERVICE="pwdev-glpi"
PKG="@soarescbm/mcp-glpi"

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

# --- modo --store: grava o PAT no Keychain sem ecoar ------------------------
if [ "${1:-}" = "--store" ]; then
  if ! command -v security >/dev/null 2>&1; then
    echo "Keychain indisponível (não é macOS)." >&2
    echo "Alternativa: adicione ao seu profile do shell:" >&2
    echo '  export GLPI_PAT="seu-token-de-api"' >&2
    exit 1
  fi
  printf "Cole o API token (PAT) do GLPI (input oculto): "
  stty -echo 2>/dev/null || true
  read -r TOKEN
  stty echo 2>/dev/null || true
  echo
  if [ -z "$TOKEN" ]; then
    echo "Nada informado — abortado." >&2
    exit 1
  fi
  if [ ${#TOKEN} -lt 16 ]; then
    echo "Aviso: o servidor exige PAT com no mínimo 16 caracteres — confira o token." >&2
  fi
  security add-generic-password -a "$USER" -s "$SERVICE" -w "$TOKEN" -U
  echo "PAT gravado no Keychain (service: $SERVICE) — $(mask "$TOKEN")"
  exit 0
fi

# --- diagnóstico ------------------------------------------------------------
printf '%-22s %-12s %s\n' "VERIFICAÇÃO" "STATUS" "DETALHE"
printf '%-22s %-12s %s\n' "-----------" "------" "-------"

# curl / node / npx
if command -v curl >/dev/null 2>&1; then
  printf '%-22s %-12s %s\n' "curl" "ok" ""
else
  printf '%-22s %-12s %s\n' "curl" "AUSENTE" "instale curl"
fi

if command -v node >/dev/null 2>&1; then
  NODE_MAJOR=$(node -v | sed 's/^v//' | cut -d. -f1)
  if [ "$NODE_MAJOR" -ge 20 ] 2>/dev/null; then
    printf '%-22s %-12s %s\n' "node" "ok" "$(node -v)"
  else
    printf '%-22s %-12s %s\n' "node" "FALHOU" "$(node -v) — o servidor exige >=20"
  fi
else
  printf '%-22s %-12s %s\n' "node" "AUSENTE" "instale Node.js 20+"
fi

if command -v npx >/dev/null 2>&1; then
  printf '%-22s %-12s %s\n' "npx" "ok" ""
else
  printf '%-22s %-12s %s\n' "npx" "AUSENTE" "vem com o Node.js/npm"
fi

# base url
BASE="${GLPI_BASE_URL:-}"
if [ -n "$BASE" ]; then
  case "$BASE" in
    */apirest.php)
      printf '%-22s %-12s %s\n' "GLPI_BASE_URL" "ok" "$BASE" ;;
    *)
      printf '%-22s %-12s %s\n' "GLPI_BASE_URL" "FALHOU" "deve terminar em /apirest.php" ;;
  esac
else
  printf '%-22s %-12s %s\n' "GLPI_BASE_URL" "AUSENTE" "export no profile + reinicie a sessão"
fi

# PAT (env ou keychain)
TOKEN="${GLPI_PAT:-}"
SRC="env"
if [ -z "$TOKEN" ] && command -v security >/dev/null 2>&1; then
  TOKEN="$(security find-generic-password -s "$SERVICE" -w 2>/dev/null || true)"
  SRC="keychain"
fi
if [ -n "$TOKEN" ]; then
  if [ ${#TOKEN} -lt 16 ]; then
    printf '%-22s %-12s %s\n' "PAT" "FALHOU" "$(mask "$TOKEN") — menos de 16 chars (servidor rejeita)"
  else
    printf '%-22s %-12s %s\n' "PAT" "ok" "$(mask "$TOKEN") (via $SRC)"
  fi
else
  printf '%-22s %-12s %s\n' "PAT" "AUSENTE" "check-setup.sh --store ou export GLPI_PAT"
fi

# App-Token (opcional)
if [ -n "${GLPI_APP_TOKEN:-}" ]; then
  printf '%-22s %-12s %s\n' "GLPI_APP_TOKEN" "ok" "setado"
else
  printf '%-22s %-12s %s\n' "GLPI_APP_TOKEN" "—" "não setado (opcional)"
fi

# REST: initSession → killSession
if [ -n "$BASE" ] && [ -n "$TOKEN" ]; then
  if [ -n "${GLPI_APP_TOKEN:-}" ]; then
    RESP=$(curl -sS -m 15 -H "Authorization: user_token $TOKEN" \
      -H "App-Token: ${GLPI_APP_TOKEN}" "$BASE/initSession" 2>/dev/null || true)
  else
    RESP=$(curl -sS -m 15 -H "Authorization: user_token $TOKEN" \
      "$BASE/initSession" 2>/dev/null || true)
  fi
  case "$RESP" in
    *'"session_token"'*)
      printf '%-22s %-12s %s\n' "REST initSession" "ok" "autenticado"
      ST=$(printf '%s' "$RESP" | sed -n 's/.*"session_token":"\([^"]*\)".*/\1/p')
      if [ -n "$ST" ]; then
        if [ -n "${GLPI_APP_TOKEN:-}" ]; then
          curl -sS -m 15 -o /dev/null -H "Session-Token: $ST" \
            -H "App-Token: ${GLPI_APP_TOKEN}" "$BASE/killSession" 2>/dev/null || true
        else
          curl -sS -m 15 -o /dev/null -H "Session-Token: $ST" \
            "$BASE/killSession" 2>/dev/null || true
        fi
      fi
      ;;
    *ERROR_GLPI_LOGIN*|*401*)
      printf '%-22s %-12s %s\n' "REST initSession" "FALHOU" "PAT inválido — regenere o API token no GLPI" ;;
    *APP_TOKEN*)
      printf '%-22s %-12s %s\n' "REST initSession" "FALHOU" "instância exige App-Token — export GLPI_APP_TOKEN" ;;
    *'<html'*|*'<!DOCTYPE'*)
      printf '%-22s %-12s %s\n' "REST initSession" "FALHOU" "resposta HTML — URL errada ou API REST desabilitada" ;;
    *)
      printf '%-22s %-12s %s\n' "REST initSession" "FALHOU" "sem resposta válida — confira URL e rede" ;;
  esac
else
  printf '%-22s %-12s %s\n' "REST initSession" "pulado" "config incompleta"
fi

# pacote npm
PKG_VER=$(npm view "$PKG" version 2>/dev/null || true)
if [ -n "$PKG_VER" ]; then
  printf '%-22s %-12s %s\n' "npm $PKG" "ok" "$PKG_VER"
else
  printf '%-22s %-12s %s\n' "npm $PKG" "FALHOU" "sem rede ou pacote indisponível (npx não baixará)"
fi

echo
echo "Config incompleta = plugin em modo consultivo (entrega o passo a passo, não executa)."
echo "Após alterar env vars, reinicie a sessão do Claude Code."
