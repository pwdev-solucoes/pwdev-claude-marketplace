#!/usr/bin/env bash
# Ideogram — melhor da lista para imagem COM TEXTO legível.
# uso: gen-ideogram.sh --prompt "..." [--ratio 4x5] [--n 2] [--seed 123] --confirm
source "$(dirname "$0")/lib.sh"

PROMPT=""; RATIO="ASPECT_4_5"; N=1; SEED=""
while [ $# -gt 0 ]; do
  case "$1" in
    --prompt) PROMPT="$2"; shift 2;;
    --ratio)  RATIO="ASPECT_${2//x/_}"; shift 2;;
    --n)      N="$2"; shift 2;;
    --seed)   SEED="$2"; shift 2;;
    --confirm) shift;;
    *) shift;;
  esac
done

[ -n "$PROMPT" ] || die "--prompt é obrigatório"
require_key IDEOGRAM_API_KEY "Ideogram"
guard_spend "$@"
api_disclaimer "https://developer.ideogram.ai"
ensure_out

body=$(python3 -c '
import json,sys
p,r,n,s = sys.argv[1:5]
req = {"prompt": p, "aspect_ratio": r, "num_images": int(n)}
if s: req["seed"] = int(s)
print(json.dumps({"image_request": req}))' "$PROMPT" "$RATIO" "$N" "$SEED")

info "gerando $N imagem(ns) — Ideogram"
resp=$(curl -sS -X POST "https://api.ideogram.ai/generate" \
  -H "Api-Key: $IDEOGRAM_API_KEY" \
  -H "Content-Type: application/json" \
  -d "$body") || die "falha na chamada"

echo "$resp" | python3 -c '
import json,sys,urllib.request,os,time
out=os.environ.get("PWSM_OUT","./.pwdev-social/gerados")
try: d=json.load(sys.stdin)
except Exception: sys.exit("resposta não-JSON — contrato da API pode ter mudado")
imgs=d.get("data") or []
if not imgs: sys.exit(f"sem imagens na resposta: {json.dumps(d)[:400]}")
for i,im in enumerate(imgs,1):
    u=im.get("url")
    if not u: continue
    f=f"{out}/ideogram_{int(time.time())}_{i}.png"
    urllib.request.urlretrieve(u,f)
    print(f"gerado: {f}")
'
log_generation "ideogram" "default" "$PROMPT" "$SEED" "$PWSM_OUT" "ver painel"
