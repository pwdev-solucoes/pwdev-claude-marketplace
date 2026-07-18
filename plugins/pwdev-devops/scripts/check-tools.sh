#!/usr/bin/env bash
# Reporta quais ferramentas existem. Define o que o plugin consegue executar.
set -euo pipefail
printf '%-14s %-10s %s\n' "FERRAMENTA" "STATUS" "DOMÍNIO"
printf '%-14s %-10s %s\n' "----------" "------" "-------"
check() {
  if command -v "$1" >/dev/null 2>&1; then s="ok"; else s="ausente"; fi
  printf '%-14s %-10s %s\n' "$1" "$s" "$2"
}
check aws       "AWS, FinOps, Backup"
check kubectl   "Kubernetes"
check helm      "Kubernetes"
check docker    "Docker"
check psql      "PostgreSQL"
check pg_dump   "Backup PostgreSQL"
check terraform "IaC"
check tofu      "IaC"
check ansible   "Automação"
check gh        "GitHub, CI/CD"
check trivy     "DevSecOps"
check hadolint  "Docker lint"
check nginx     "Nginx"
check k6        "Performance"
echo
echo "Ausente = skill opera em modo consultivo (entrega o comando, não executa)."
