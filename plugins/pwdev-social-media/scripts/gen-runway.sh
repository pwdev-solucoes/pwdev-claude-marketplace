#!/usr/bin/env bash
# Runway — vídeo a partir de imagem. Requer imagem de origem.
# uso: gen-runway.sh --image URL --prompt "..." [--dur 5] [--ratio 720:1280] --confirm
source "$(dirname "$0")/lib.sh"

IMG=""; PROMPT=""; DUR=5; RATIO="720:1280"; MODEL="gen4_turbo"
while [ $# -gt 0 ]; do
  case "$1" in
    --image) IMG="$2"; shift 2;; --prompt) PROMPT="$2"; shift 2;;
    --dur) DUR="$2"; shift 2;; --ratio) RATIO="$2"; shift 2;;
    --model) MODEL="$2"; shift 2;; --confirm) shift;; *) shift;;
  esac
done

[ -n "$IMG" ] || die "--image é obrigatório (Runway gera a partir de imagem)"
require_key RUNWAY_API_KEY "Runway"
guard_spend "$@"
api_disclaimer "https://docs.dev.runwayml.com"
warn "vídeo é o item mais caro da stack — confirme a duração antes de repetir"
ensure_out

body=$(python3 -c '
import json,sys
i,p,d,r,m=sys.argv[1:6]
print(json.dumps({"promptImage":i,"promptText":p,"duration":int(d),"ratio":r,"model":m}))' \
  "$IMG" "$PROMPT" "$DUR" "$RATIO" "$MODEL")

info "enviando job de vídeo — Runway/$MODEL, ${DUR}s"
resp=$(curl -sS -X POST "https://api.dev.runwayml.com/v1/image_to_video" \
  -H "Authorization: Bearer $RUNWAY_API_KEY" \
  -H "X-Runway-Version: 2024-11-06" \
  -H "Content-Type: application/json" -d "$body") || die "falha na chamada"

id=$(echo "$resp" | python3 -c 'import json,sys;print(json.load(sys.stdin).get("id",""))' 2>/dev/null || true)
[ -n "$id" ] || die "sem id de task — contrato pode ter mudado: ${resp:0:300}"
info "task $id — acompanhe; vídeo leva minutos"
log_generation "runway" "$MODEL" "$PROMPT" "" "task:$id" "ver painel"
echo "task: $id"
