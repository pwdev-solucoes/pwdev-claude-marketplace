#!/usr/bin/env bash
# Flux (Black Forest Labs) — fotorrealismo.
# uso: gen-flux.sh --prompt "..." [--w 1080] [--h 1350] [--seed 123] --confirm
source "$(dirname "$0")/lib.sh"

PROMPT=""; W=1080; H=1350; SEED=""; MODEL="flux-pro-1.1"
while [ $# -gt 0 ]; do
  case "$1" in
    --prompt) PROMPT="$2"; shift 2;;
    --w) W="$2"; shift 2;; --h) H="$2"; shift 2;;
    --seed) SEED="$2"; shift 2;; --model) MODEL="$2"; shift 2;;
    --confirm) shift;; *) shift;;
  esac
done

[ -n "$PROMPT" ] || die "--prompt é obrigatório"
require_key BFL_API_KEY "Flux (BFL)"
guard_spend "$@"
api_disclaimer "https://docs.bfl.ai"
ensure_out

body=$(python3 -c '
import json,sys
p,w,h,s=sys.argv[1:5]
r={"prompt":p,"width":int(w),"height":int(h)}
if s: r["seed"]=int(s)
print(json.dumps(r))' "$PROMPT" "$W" "$H" "$SEED")

info "enviando job — Flux/$MODEL"
resp=$(curl -sS -X POST "https://api.bfl.ai/v1/$MODEL" \
  -H "x-key: $BFL_API_KEY" -H "Content-Type: application/json" \
  -d "$body") || die "falha na chamada"

id=$(echo "$resp" | python3 -c 'import json,sys;print(json.load(sys.stdin).get("id",""))' 2>/dev/null || true)
[ -n "$id" ] || die "sem id de job na resposta — contrato pode ter mudado: ${resp:0:300}"

info "job $id — aguardando (Flux é assíncrono)"
for i in $(seq 1 60); do
  sleep 2
  r=$(curl -sS "https://api.bfl.ai/v1/get_result?id=$id" -H "x-key: $BFL_API_KEY")
  st=$(echo "$r" | python3 -c 'import json,sys;print(json.load(sys.stdin).get("status",""))' 2>/dev/null || echo "")
  case "$st" in
    Ready)
      echo "$r" | python3 -c '
import json,sys,urllib.request,os,time
out=os.environ.get("PWSM_OUT","./.pwdev-social/gerados")
u=json.load(sys.stdin)["result"]["sample"]
f=f"{out}/flux_{int(time.time())}.png"
urllib.request.urlretrieve(u,f); print(f"gerado: {f}")'
      log_generation "flux" "$MODEL" "$PROMPT" "$SEED" "$PWSM_OUT" "ver painel"
      exit 0;;
    Error|Failed) die "job falhou: ${r:0:300}";;
  esac
done
die "timeout aguardando o job $id"
