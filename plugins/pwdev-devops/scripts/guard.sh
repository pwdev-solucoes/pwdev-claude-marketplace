#!/usr/bin/env bash
# Segunda barreira de segurança. Classifica um comando e bloqueia mutação
# sem --confirm. Independente da instrução da skill: instrução falha, trava não.
#
# uso: guard.sh --check "<comando>" [--confirm] [--env prod|staging|dev]
set -euo pipefail

CMD=""; CONFIRM=0; ENVIRON="desconhecido"
while [ $# -gt 0 ]; do
  case "$1" in
    --check) CMD="$2"; shift 2;;
    --confirm) CONFIRM=1; shift;;
    --env) ENVIRON="$2"; shift 2;;
    *) shift;;
  esac
done
[ -n "$CMD" ] || { echo "uso: guard.sh --check \"<comando>\" [--confirm]" >&2; exit 2; }

red()  { printf '\033[31m%s\033[0m\n' "$*" >&2; }
ylw()  { printf '\033[33m%s\033[0m\n' "$*" >&2; }
grn()  { printf '\033[32m%s\033[0m\n' "$*" >&2; }

# --- proibido sempre: nem com --confirm ---
PROIBIDO='(terraform[[:space:]]+destroy|DROP[[:space:]]+(DATABASE|SCHEMA)|TRUNCATE|mkfs|dd[[:space:]]+if=|rm[[:space:]]+-rf[[:space:]]+/([[:space:]]|$))'
if echo "$CMD" | grep -qiE "$PROIBIDO"; then
  red "🛑 BLOQUEADO — comando na lista de proibidos"
  red "   $CMD"
  red "   Este plugin não executa isto, nem com --confirm."
  red "   Entregue o procedimento; quem roda é o humano."
  exit 3
fi

# --- destrutivo ---
DESTRUTIVO='(kubectl[[:space:]]+delete|delete-|terminate-|docker[[:space:]]+(rm|rmi|system[[:space:]]+prune)|DROP[[:space:]]+(TABLE|INDEX)|DELETE[[:space:]]+FROM)'
# --- mutação ---
MUTACAO='(kubectl[[:space:]]+(apply|scale|rollout|patch|label|cordon|drain|edit)|aws[[:space:]].*[[:space:]](create|update|put|modify|attach|detach)-|docker[[:space:]]+(run|build|push|stop|restart)|systemctl[[:space:]]+(start|stop|restart|enable|disable)|nginx[[:space:]]+-s|terraform[[:space:]]+apply|ansible-playbook|INSERT|UPDATE|CREATE|ALTER|REINDEX|VACUUM[[:space:]]+FULL)'

classe="leitura"
echo "$CMD" | grep -qiE "$MUTACAO"    && classe="mutacao"
echo "$CMD" | grep -qiE "$DESTRUTIVO" && classe="destrutivo"

case "$classe" in
  leitura)
    grn "✓ leitura — liberado"
    exit 0;;
  mutacao)
    if [ "$CONFIRM" -eq 1 ]; then
      ylw "⚠ mutação autorizada (--confirm) — ambiente: $ENVIRON"
      exit 0
    fi
    red "⚠ MUTAÇÃO BLOQUEADA — falta --confirm"
    red "   $CMD"
    red "   Ambiente: $ENVIRON"
    red "   Apresente comando, efeito, reversibilidade e blast radius ao usuário."
    red "   Só repita com --confirm após 'sim' explícito PARA ESTE comando."
    exit 4;;
  destrutivo)
    if [ "$CONFIRM" -eq 1 ] && [ "$ENVIRON" != "prod" ]; then
      ylw "🛑 destrutivo autorizado em '$ENVIRON' — verifique backup antes"
      exit 0
    fi
    red "🛑 DESTRUTIVO BLOQUEADO"
    red "   $CMD"
    red "   Ambiente: $ENVIRON"
    [ "$ENVIRON" = "prod" ] && red "   Destrutivo em produção exige que o humano execute." \
                            || red "   Exige --confirm E verificação de backup."
    exit 5;;
esac
