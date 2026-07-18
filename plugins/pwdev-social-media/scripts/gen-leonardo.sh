#!/usr/bin/env bash
# Leonardo — ilustração e consistência de estilo de marca (elements / style ref).
# uso: gen-leonardo.sh --prompt "..." [--w 1080] [--h 1350] [--n 2] [--model ID] --confirm
source "$(dirname "$0")/lib.sh"

PROMPT=""; W=1080; H=1350; N=1; MODEL="${LEONARDO_MODEL_ID:-}"
while [ $# -gt 0 ]; do
  case "$1" in
    --prompt) PROMPT="$2"; shift 2;;
    --w) W="$2"; shift 2;; --h) H="$2"; shift 2;;
    --n) N="$2"; shift 2;; --model) MODEL="$2"; shift 2;;
    --confirm) shift;; *) shift;;
  esac
done

[ -n "$PROMPT" ] || die "--prompt é obrigatório"
require_key LEONARDO_API_KEY "Leonardo"
guard_spend "$@"
api_disclaimer "https://docs.leonardo.ai"
[ -n "$MODEL" ] || warn "sem --model: a conta usará o padrão. Para consistência entre peças, fixe o modelo."
ensure_out

body=$(python3 -c '
import json,sys
p,w,h,n,m=sys.argv[1:6]
r={"prompt":p,"width":int(w),"height":int(h),"num_images":int(n)}
if m: r["modelId"]=m
print(json.dumps(r))' "$PROMPT" "$W" "$H" "$N" "$MODEL")

info "enviando job — Leonardo"
resp=$(curl -sS -X POST "https://cloud.leonardo.ai/api/rest/v1/generations" \
  -H "Authorization: Bearer $LEONARDO_API_KEY" \
  -H "Content-Type: application/json" -d "$body") || die "falha na chamada"

id=$(echo "$resp" | python3 -c '
import json,sys
d=json.load(sys.stdin)
print((d.get("sdGenerationJob") or {}).get("generationId",""))' 2>/dev/null || true)
[ -n "$id" ] || die "sem generationId — contrato pode ter mudado: ${resp:0:300}"

info "job $id — aguardando"
for i in $(seq 1 60); do
  sleep 3
  r=$(curl -sS "https://cloud.leonardo.ai/api/rest/v1/generations/$id" \
      -H "Authorization: Bearer $LEONARDO_API_KEY")
  done_=$(echo "$r" | python3 -c '
import json,sys,urllib.request,os,time
out=os.environ.get("PWSM_OUT","./.pwdev-social/gerados")
d=json.load(sys.stdin).get("generations_by_pk") or {}
if d.get("status")!="COMPLETE": print(""); raise SystemExit
for i,im in enumerate(d.get("generated_images") or [],1):
    f=f"{out}/leonardo_{int(time.time())}_{i}.png"
    urllib.request.urlretrieve(im["url"],f); print(f"gerado: {f}")
' 2>/dev/null || echo "")
  if [ -n "$done_" ]; then
    echo "$done_"
    log_generation "leonardo" "${MODEL:-default}" "$PROMPT" "" "$PWSM_OUT" "ver painel"
    exit 0
  fi
done
die "timeout aguardando o job $id"
