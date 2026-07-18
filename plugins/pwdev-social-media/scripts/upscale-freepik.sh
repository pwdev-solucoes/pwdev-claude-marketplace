#!/usr/bin/env bash
# Freepik/Magnific — upscale. Antes de usar: existe original em resolução maior?
# uso: upscale-freepik.sh --file caminho.png [--scale 2] --confirm
source "$(dirname "$0")/lib.sh"

FILE=""; SCALE=2
while [ $# -gt 0 ]; do
  case "$1" in
    --file) FILE="$2"; shift 2;; --scale) SCALE="$2"; shift 2;;
    --confirm) shift;; *) shift;;
  esac
done

[ -f "$FILE" ] || die "arquivo não encontrado: $FILE"
require_key FREEPIK_API_KEY "Freepik/Magnific"
guard_spend "$@"
api_disclaimer "https://docs.freepik.com"
warn "antes de gastar: existe o original em resolução maior, ou dá para reexportar do vetor?"
ensure_out

b64=$(base64 < "$FILE" | tr -d '\n')
info "enviando upscale ${SCALE}× — $(basename "$FILE")"
resp=$(curl -sS -X POST "https://api.freepik.com/v1/ai/image-upscaler" \
  -H "x-freepik-api-key: $FREEPIK_API_KEY" \
  -H "Content-Type: application/json" \
  -d "{\"image\":\"$b64\",\"scale_factor\":\"${SCALE}x\"}") || die "falha na chamada"

echo "$resp" | python3 -c '
import json,sys
try: d=json.load(sys.stdin)
except Exception: sys.exit("resposta não-JSON — contrato pode ter mudado")
print(json.dumps(d, ensure_ascii=False)[:600])'
log_generation "freepik-magnific" "upscaler" "upscale ${SCALE}x" "" "$FILE" "ver painel"
