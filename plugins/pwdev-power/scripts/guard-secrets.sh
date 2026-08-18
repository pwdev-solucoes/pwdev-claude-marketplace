#!/bin/sh
# guard-secrets.sh — PreToolUse guard (Read|Bash) for the Claude adapter.
#
# Deterministic enforcement of the read boundary in references/safety.md: never read a secret
# file. exit 2 blocks the tool call; anything else lets it through.
#
# The other runtimes have no equivalent hook, so there the rule is the agent's to keep. This
# hook is enforcement where enforcement is available, not the source of the rule.

INPUT=$(cat 2>/dev/null)

if command -v jq >/dev/null 2>&1; then
  TARGET=$(printf '%s' "$INPUT" | jq -r '.tool_input.file_path // .tool_input.command // empty' 2>/dev/null)
else
  TARGET=$(printf '%s' "$INPUT" | sed -n 's/.*"\(file_path\|command\)"[[:space:]]*:[[:space:]]*"\([^"]*\)".*/\2/p' | head -1)
fi

[ -n "$TARGET" ] || exit 0

# Templates are documentation and are explicitly encouraged.
case "$TARGET" in
  *.env.example*|*.env.template*|*.env.sample*) exit 0 ;;
esac

# The generated fleet environment matches the .env pattern below on purpose: it holds a
# throwaway database password, and naming it so that this guard recognises it is why it is
# called .env.fleet rather than something that would slip past the anchor.
if printf '%s' "$TARGET" | grep -Eq '(^|[/ "'"'"'])\.env([^a-zA-Z]|\.local|\.production|\.development|\.staging|$)|\.pem([^a-zA-Z]|$)|\.key([^a-zA-Z]|$)|id_rsa|\.p12([^a-zA-Z]|$)|\.pfx([^a-zA-Z]|$)|credentials\.json'; then
  echo "pwdev-power guard: blocked access to a secret file ($TARGET). Use the .example variant." >&2
  exit 2
fi

exit 0
