#!/usr/bin/env bash
# ╔══════════════════════════════════════════════════════════════════════════════╗
# ║  PWDEV Status Line for Claude Code                                         ║
# ║  Rich terminal status bar with model, git, context, rate limits & tokens   ║
# ╚══════════════════════════════════════════════════════════════════════════════╝

# ── Configuration (edited by /pwdev-statusline:customize) ────────────────────
SHOW_BRAND=1
SHOW_USER=1
SHOW_SESSION=1
SHOW_DIR=1
SHOW_MODEL=1
SHOW_GIT=1
SHOW_CTX=1
SHOW_TOKENS=1
SHOW_RATE=1
SEP=" | "
DIR_MAX_SEGMENTS=3   # trailing path segments to keep (0 = full path)

# ── ANSI color codes (bold) — per-segment, editable ──────────────────────────
GREEN=$'\033[1;32m'
BLUE=$'\033[1;34m'
CYAN=$'\033[1;36m'
MAGENTA=$'\033[1;35m'
YELLOW=$'\033[1;33m'
RED=$'\033[1;31m'
WHITE=$'\033[1;37m'
RESET=$'\033[0m'

COLOR_BRAND="$GREEN"
COLOR_USER="$WHITE"
COLOR_SESSION="$WHITE"
COLOR_DIR="$BLUE"
COLOR_MODEL="$CYAN"
COLOR_GIT="$MAGENTA"
COLOR_TOKENS="$WHITE"

input=$(cat)

# Guard: if jq is not available, print a minimal line and exit
if ! command -v jq >/dev/null 2>&1; then
  echo "jq not found"
  exit 0
fi

# Guard: if input is empty or not valid JSON, print a minimal line and exit
if ! printf '%s' "$input" | jq empty >/dev/null 2>&1; then
  echo "(no data)"
  exit 0
fi

# ── Single jq pass: extract every field at once (tab-separated) ──────────────
# Fields absent from the payload degrade to "-" and their segment is hidden.
IFS=$'\t' read -r CWD MODEL USED RATE_5H TOTAL_IN TOTAL_OUT SESSION_NAME <<EOF
$(printf '%s' "$input" | jq -r '[
  (.workspace.current_dir // "."),
  (.model.display_name // "-"),
  (.context_window.used_percentage // "-"),
  (.rate_limits.five_hour.used_percentage // "-"),
  (.context_window.total_input_tokens // 0),
  (.context_window.total_output_tokens // 0),
  (.session_name // "-")
] | @tsv')
EOF

# num_int VALUE → echoes integer or empty on non-numeric input
num_int() {
  case "$1" in
    ''|-|*[!0-9.]*) echo "" ;;
    *) printf '%.0f' "$1" 2>/dev/null ;;
  esac
}

# fmt_tokens N → 1.2M / 512k / 950
fmt_tokens() {
  local n=$1
  if   [ "$n" -ge 1000000 ]; then printf '%d.%dM' $((n/1000000)) $((n%1000000/100000))
  elif [ "$n" -ge 1000 ];    then printf '%dk' $((n/1000))
  else printf '%d' "$n"; fi
}

# ── 1. Brand ─────────────────────────────────────────────────────────────────
BRAND_PART="${COLOR_BRAND}PWDEV${RESET}"

# ── 2. Git user name ─────────────────────────────────────────────────────────
GIT_USER=$(git -C "${CWD}" config user.name 2>/dev/null)
USER_PART=""
[ -n "$GIT_USER" ] && USER_PART="${COLOR_USER}${GIT_USER}${RESET}"

# ── 3. Session name ──────────────────────────────────────────────────────────
SESSION_PART=""
[ "$SESSION_NAME" != "-" ] && [ -n "$SESSION_NAME" ] && SESSION_PART="${COLOR_SESSION}${SESSION_NAME}${RESET}"

# ── 4. Directory (~ substitution + truncation) ───────────────────────────────
DIR_DISPLAY="${CWD/#$HOME/\~}"
if [ "$DIR_MAX_SEGMENTS" -gt 0 ]; then
  IFS='/' read -ra SEGS <<< "$DIR_DISPLAY"
  COUNT=${#SEGS[@]}
  if [ "$COUNT" -gt "$DIR_MAX_SEGMENTS" ]; then
    KEPT=("${SEGS[@]: -DIR_MAX_SEGMENTS}")
    DIR_DISPLAY="…/$(IFS='/'; echo "${KEPT[*]}")"
  fi
fi
DIR_PART="${COLOR_DIR}${DIR_DISPLAY}${RESET}"

# ── 5. Model name ────────────────────────────────────────────────────────────
MODEL_PART="${COLOR_MODEL}${MODEL}${RESET}"

# ── 6. Git branch ────────────────────────────────────────────────────────────
BRANCH=$(git -C "${CWD}" --no-optional-locks rev-parse --abbrev-ref HEAD 2>/dev/null)
GIT_PART=""
[ -n "$BRANCH" ] && GIT_PART="${COLOR_GIT}${BRANCH}${RESET}"

# ── 7. Context progress bar (green <60% / yellow / red >=80%) ────────────────
CTX_PART=""
PCT=$(num_int "$USED")
if [ -n "$PCT" ]; then
  FILLED=$(( PCT * 10 / 100 )); [ "$FILLED" -gt 10 ] && FILLED=10
  BAR=""
  for ((i=0; i<FILLED; i++)); do BAR="${BAR}█"; done
  for ((i=FILLED; i<10; i++)); do BAR="${BAR}░"; done
  if   [ "$PCT" -ge 80 ]; then CTX_COLOR="$RED"
  elif [ "$PCT" -ge 60 ]; then CTX_COLOR="$YELLOW"
  else CTX_COLOR="$GREEN"; fi
  CTX_PART="${CTX_COLOR}ctx:${BAR} ${PCT}%${RESET}"
fi

# ── 8. Tokens used ───────────────────────────────────────────────────────────
IN_N=$(num_int "$TOTAL_IN");  IN_N=${IN_N:-0}
OUT_N=$(num_int "$TOTAL_OUT"); OUT_N=${OUT_N:-0}
TOK_PART="${COLOR_TOKENS}tok:$(fmt_tokens $((IN_N + OUT_N)))${RESET}"

# ── 9. Rate limit 5h (green <50% / yellow / red >=80%) ───────────────────────
RATE_PART=""
RATE_PCT=$(num_int "$RATE_5H")
if [ -n "$RATE_PCT" ]; then
  if   [ "$RATE_PCT" -ge 80 ]; then RATE_COLOR="$RED"
  elif [ "$RATE_PCT" -ge 50 ]; then RATE_COLOR="$YELLOW"
  else RATE_COLOR="$GREEN"; fi
  RATE_PART="${RATE_COLOR}5h:${RATE_PCT}%${RESET}"
fi

# ── Assemble single line (honoring SHOW_* toggles) ───────────────────────────
LINE=""
append() { [ -n "$1" ] && { [ -n "$LINE" ] && LINE="${LINE}${SEP}"; LINE="${LINE}$1"; }; }

[ "$SHOW_BRAND"   = 1 ] && append "$BRAND_PART"
[ "$SHOW_USER"    = 1 ] && append "$USER_PART"
[ "$SHOW_SESSION" = 1 ] && append "$SESSION_PART"
[ "$SHOW_DIR"     = 1 ] && append "$DIR_PART"
[ "$SHOW_MODEL"   = 1 ] && append "$MODEL_PART"
[ "$SHOW_GIT"     = 1 ] && append "$GIT_PART"
[ "$SHOW_CTX"     = 1 ] && append "$CTX_PART"
[ "$SHOW_TOKENS"  = 1 ] && append "$TOK_PART"
[ "$SHOW_RATE"    = 1 ] && append "$RATE_PART"

printf "%s\n" "${LINE}"
