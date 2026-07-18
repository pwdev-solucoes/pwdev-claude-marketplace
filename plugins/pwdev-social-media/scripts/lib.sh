#!/usr/bin/env bash
# Biblioteca compartilhada dos wrappers de geração.
# Nunca imprime chave de API. Nunca gasta crédito sem --confirm.
set -euo pipefail

PWSM_OUT="${PWSM_OUT:-./.pwdev-social/gerados}"
PWSM_MANIFEST="${PWSM_OUT}/manifest.jsonl"

die() { printf '\033[31merro:\033[0m %s\n' "$*" >&2; exit 1; }
info() { printf '\033[36m·\033[0m %s\n' "$*" >&2; }
warn() { printf '\033[33m!\033[0m %s\n' "$*" >&2; }

# require_key VAR_NAME ferramenta
# Verifica presença sem nunca revelar o valor.
require_key() {
  local var="$1" tool="$2"
  if [ -z "${!var:-}" ]; then
    die "chave ausente: \$$var não está definida.
     $tool não pode ser chamada.
     Defina no ambiente (nunca em arquivo do projeto) e tente de novo.
     Sem a chave, use o modo prompt: a skill entrega o prompt para execução manual."
  fi
}

# guard_spend "$@" — exige --confirm explícito antes de qualquer chamada paga.
# Segunda linha de defesa: mesmo que a skill erre, o script recusa.
guard_spend() {
  for arg in "$@"; do
    [ "$arg" = "--confirm" ] && return 0
  done
  die "chamada paga bloqueada: falta --confirm.
     Este script gasta crédito da conta do usuário.
     Confirme o custo com a pessoa ANTES de repetir com --confirm."
}

ensure_out() { mkdir -p "$PWSM_OUT"; }

# log_generation ferramenta modelo prompt seed arquivo custo_estimado
# Sem manifesto não há reprodução nem auditoria.
log_generation() {
  ensure_out
  python3 - "$@" <<'PY' >> "$PWSM_MANIFEST"
import json,sys,datetime
t,model,prompt,seed,arquivo,custo = (sys.argv[1:7] + [""]*6)[:6]
print(json.dumps({
  "ts": datetime.datetime.now().isoformat(timespec="seconds"),
  "ferramenta": t, "modelo": model, "prompt": prompt,
  "seed": seed, "arquivo": arquivo, "custo_estimado": custo
}, ensure_ascii=False))
PY
  info "registrado em $PWSM_MANIFEST"
}

# Aviso de contrato de API. Endpoints e parâmetros mudam sem aviso.
api_disclaimer() {
  warn "confira o contrato atual da API em $1 — endpoints e parâmetros mudam."
}
