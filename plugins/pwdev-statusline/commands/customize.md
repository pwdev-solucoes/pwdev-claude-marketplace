---
description: Customize the status line — toggle sections, change colors, separator, or directory truncation
argument-hint: "<action> (e.g., show, hide-tokens, show-rate, colors, separator, dir-depth)"
disable-model-invocation: true
---

# /pwdev-statusline:customize — Customize Status Line

## Role
Customizes the status line via the **configuration block** at the top of
`~/.claude/statusline.sh` — every change is a 1-line edit of a config
variable, idempotent and reversible. Never comment out or restructure the
script body.

## Input
$ARGUMENTS: the customization action.

## Configuration block (top of the script)

```bash
SHOW_BRAND=1  SHOW_USER=1  SHOW_SESSION=1  SHOW_DIR=1  SHOW_MODEL=1
SHOW_GIT=1    SHOW_CTX=1   SHOW_TOKENS=1   SHOW_RATE=1
SEP=" | "
DIR_MAX_SEGMENTS=3
COLOR_BRAND / COLOR_USER / COLOR_SESSION / COLOR_DIR / COLOR_MODEL /
COLOR_GIT / COLOR_TOKENS  (assigned from GREEN/BLUE/CYAN/MAGENTA/YELLOW/RED/WHITE)
```

## Available Actions

### `show` (default if no argument)
Read the config block and present: which sections are on/off (SHOW_*),
color assignments (COLOR_*), separator, and DIR_MAX_SEGMENTS.

### `hide-<section>` / `show-<section>`
Sections: `brand`, `user`, `session`, `dir`, `model`, `git`, `ctx`,
`tokens`, `rate`. Set the matching `SHOW_<SECTION>` variable to `0` or `1`.
(One Edit; nothing else changes.)

### `colors`
Present the current COLOR_* table, ask which section to recolor and to which
of the available colors, then reassign the variable (e.g.
`COLOR_DIR="$CYAN"`). Note: ctx and rate colors are dynamic
(green/yellow/red by threshold) and not configurable per-section.

### `separator <string>`
Set `SEP="<string>"` (e.g. ` · `, ` ▸ `, ` — `).

### `dir-depth <n>`
Set `DIR_MAX_SEGMENTS=<n>` (0 = full path, N = keep last N segments with
`…/` prefix).

## Procedure

1. Verify `~/.claude/statusline.sh` exists (else → suggest install).
2. Parse `$ARGUMENTS`; apply the 1-line Edit to the config block only.
3. Preview the result:
   ```bash
   echo '{"workspace":{"current_dir":"'$(pwd)'"},"model":{"display_name":"Fable 5"},"context_window":{"used_percentage":42,"total_input_tokens":100000,"total_output_tokens":5000},"rate_limits":{"five_hour":{"used_percentage":15}},"session_name":"demo"}' | bash ~/.claude/statusline.sh
   ```
4. Confirm the change was applied.

## Prohibitions
- ❌ NEVER edit below the configuration block (script logic is not the API)
- ❌ NEVER comment out sections — use the SHOW_* toggles
