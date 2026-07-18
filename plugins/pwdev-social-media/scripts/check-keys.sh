#!/usr/bin/env bash
# Reporta quais chaves existem. Nunca imprime valor.
set -euo pipefail
printf '%-22s %s\n' "FERRAMENTA" "CHAVE"
printf '%-22s %s\n' "----------" "-----"
for pair in \
  "Ideogram:IDEOGRAM_API_KEY" \
  "Leonardo:LEONARDO_API_KEY" \
  "Flux (BFL):BFL_API_KEY" \
  "Runway:RUNWAY_API_KEY" \
  "Freepik/Magnific:FREEPIK_API_KEY"; do
  nome="${pair%%:*}"; var="${pair##*:}"
  if [ -n "${!var:-}" ]; then st="configurada"; else st="ausente → modo prompt"; fi
  printf '%-22s %s\n' "$nome" "$st"
done
