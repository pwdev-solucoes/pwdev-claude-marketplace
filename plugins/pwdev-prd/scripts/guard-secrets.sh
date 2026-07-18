#!/bin/sh
# guard-secrets.sh — PreToolUse guard (Read|Bash).
# Deterministic enforcement of the pwdev-prd security rule: never read
# .env, *.pem, *.key or id_rsa* files. exit 2 blocks the tool call;
# anything else lets it through.

INPUT=$(cat 2>/dev/null)

if command -v jq >/dev/null 2>&1; then
  TARGET=$(printf '%s' "$INPUT" | jq -r '.tool_input.file_path // .tool_input.command // empty' 2>/dev/null)
else
  TARGET=$(printf '%s' "$INPUT" | sed -n 's/.*"\(file_path\|command\)"[[:space:]]*:[[:space:]]*"\([^"]*\)".*/\2/p' | head -1)
fi

[ -n "$TARGET" ] || exit 0

# Templates are safe and explicitly encouraged.
case "$TARGET" in
  *.env.example*|*.env.template*|*.env.sample*) exit 0 ;;
esac

if printf '%s' "$TARGET" | grep -Eq '(^|[/ "'"'"'])\.env([^a-zA-Z]|\.local|\.production|\.development|\.staging|$)|\.pem([^a-zA-Z]|$)|\.key([^a-zA-Z]|$)|id_rsa'; then
  echo "pwdev-prd guard: blocked access to secret file ($TARGET). Use .env.example instead." >&2
  exit 2
fi

exit 0
