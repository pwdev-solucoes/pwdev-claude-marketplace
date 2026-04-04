---
description: Customize the status line — toggle sections, change colors, or reorder segments
argument-hint: "<action> (e.g., show, hide-tokens, hide-rate, hide-session, colors, reorder)"
---

# /pwdev-statusline:customize — Customize Status Line

## Role
Interactively customizes the status line script based on user preferences.

## Input
$ARGUMENTS: the customization action.

## Available Actions

### `show` (default if no argument)
Display the current status line configuration. Read `~/.claude/statusline.sh` and list:
- Which sections are enabled/disabled
- Current color assignments
- Current section order

### `hide-tokens`
Comment out the tokens section (section 6) in `~/.claude/statusline.sh` and remove `$TOK_PART` from the assembly line.

### `show-tokens`
Uncomment/restore the tokens section if previously hidden.

### `hide-rate`
Comment out the rate limit section (section 5) and remove `$RATE_PART` from assembly.

### `show-rate`
Restore the rate limit section.

### `hide-session`
Comment out the session name section (section 7) and remove `$SESSION_PART` from assembly.

### `show-session`
Restore the session name section.

### `hide-git`
Comment out the git branch section (section 3) and remove `$GIT_PART` from assembly.

### `show-git`
Restore the git branch section.

### `colors`
Present a table of current color assignments and ask the user which section to recolor:
```
Section       Current Color
─────────────────────────────
PWDEV         Green
User          White
Directory     Blue
Model         Cyan
Git Branch    Magenta
Context       Yellow
Rate Limit    Green/Red
Tokens        White
Session       White
```
Then update the ANSI code for the chosen section in the script.

### `separator <char>`
Change the separator between sections. Default is ` | `. User can set any string (e.g., ` · `, ` ▸ `, ` — `).

## Procedure

1. Parse `$ARGUMENTS` to determine action
2. Read `~/.claude/statusline.sh`
3. Apply the requested modification using Edit tool
4. Show the user a preview by running: `echo '{"workspace":{"current_dir":"/test"},"model":{"display_name":"Opus"},"context_window":{"used_percentage":42,"total_input_tokens":1000,"total_output_tokens":500},"rate_limits":{"five_hour":{"used_percentage":15}},"session_name":"demo"}' | bash ~/.claude/statusline.sh`
5. Confirm the change was applied
