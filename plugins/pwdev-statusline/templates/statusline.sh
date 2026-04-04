#!/usr/bin/env bash
# ╔══════════════════════════════════════════════════════════════════════════════╗
# ║  PWDEV Status Line for Claude Code                                         ║
# ║  Rich terminal status bar with model, git, context, rate limits & tokens   ║
# ╚══════════════════════════════════════════════════════════════════════════════╝

input=$(cat)

# Guard: if jq is not available, print a minimal line and exit
if ! command -v jq >/dev/null 2>&1; then
  echo "jq not found"
  exit 0
fi

# Guard: if input is empty or not valid JSON, print a minimal line and exit
if ! echo "$input" | jq empty >/dev/null 2>&1; then
  echo "(no data)"
  exit 0
fi

# ── ANSI color codes (bold) ───────────────────────────────────────────────────
GREEN=$'\033[1;32m'
BLUE=$'\033[1;34m'
CYAN=$'\033[1;36m'
MAGENTA=$'\033[1;35m'
YELLOW=$'\033[1;33m'
RED=$'\033[1;31m'
WHITE=$'\033[1;37m'
RESET=$'\033[0m'

SEP=" | "

# ── 1. Directory (blue) ──────────────────────────────────────────────────────
CWD=$(echo "$input" | jq -r '.workspace.current_dir // "."')
DIR_PART="${BLUE}${CWD}${RESET}"

# ── 2. Model name (cyan) ─────────────────────────────────────────────────────
MODEL=$(echo "$input" | jq -r '.model.display_name // "—"')
MODEL_PART="${CYAN}${MODEL}${RESET}"

# ── 3. Git branch (magenta) ──────────────────────────────────────────────────
BRANCH=$(git -C "${CWD}" --no-optional-locks rev-parse --abbrev-ref HEAD 2>/dev/null)
GIT_PART=""
[ -n "$BRANCH" ] && GIT_PART="${MAGENTA}${BRANCH}${RESET}"

# ── 4. Context progress bar + percentage (yellow) ────────────────────────────
USED=$(echo "$input" | jq -r '.context_window.used_percentage // empty')
if [ -n "$USED" ]; then
  PCT=$(printf '%.0f' "$USED")
else
  PCT=0
fi
FILLED=$(( PCT * 10 / 100 ))
EMPTY=$(( 10 - FILLED ))
BAR=""
for i in $(seq 1 $FILLED); do BAR="${BAR}█"; done
for i in $(seq 1 $EMPTY);  do BAR="${BAR}░"; done
CTX_PART="${YELLOW}ctx:${BAR} ${PCT}%${RESET}"

# ── 5. Rate limit 5h (red/green) ─────────────────────────────────────────────
RATE_5H=$(echo "$input" | jq -r '.rate_limits.five_hour.used_percentage // empty')
if [ -n "$RATE_5H" ]; then
  RATE_PCT=$(printf '%.0f' "$RATE_5H")
  if [ "$RATE_PCT" -ge 80 ]; then
    RATE_PART="${RED}5h:${RATE_PCT}%${RESET}"
  else
    RATE_PART="${GREEN}5h:${RATE_PCT}%${RESET}"
  fi
else
  RATE_PART=""
fi

# ── 6. Tokens used (white) ───────────────────────────────────────────────────
TOTAL_IN=$(echo "$input"  | jq -r '.context_window.total_input_tokens  // 0')
TOTAL_OUT=$(echo "$input" | jq -r '.context_window.total_output_tokens // 0')
TOTAL_TOK=$(( TOTAL_IN + TOTAL_OUT ))
TOK_PART="${WHITE}tok:${TOTAL_TOK}${RESET}"

# ── 7. Session name (white) ──────────────────────────────────────────────────
SESSION_NAME=$(echo "$input" | jq -r '.session_name // empty')
SESSION_PART=""
[ -n "$SESSION_NAME" ] && SESSION_PART="${WHITE}${SESSION_NAME}${RESET}"

# ── 8. Company branding (green) ──────────────────────────────────────────────
BRAND_PART="${GREEN}PWDEV${RESET}"

# ── 9. Git user name (white) ────────────────────────────────────────────────
GIT_USER=$(git -C "${CWD}" config user.name 2>/dev/null)
USER_PART=""
[ -n "$GIT_USER" ] && USER_PART="${WHITE}${GIT_USER}${RESET}"

# ── Assemble single line ─────────────────────────────────────────────────────
LINE="${BRAND_PART}${SEP}"
[ -n "$USER_PART" ] && LINE="${LINE}${USER_PART}${SEP}"
[ -n "$SESSION_PART" ] && LINE="${LINE}${SESSION_PART}${SEP}"
LINE="${LINE}${DIR_PART}${SEP}${MODEL_PART}"
[ -n "$GIT_PART" ] && LINE="${LINE}${SEP}${GIT_PART}"
LINE="${LINE}${SEP}${CTX_PART}${SEP}${TOK_PART}"
[ -n "$RATE_PART" ] && LINE="${LINE}${SEP}${RATE_PART}"

printf "%s\n" "${LINE}"
