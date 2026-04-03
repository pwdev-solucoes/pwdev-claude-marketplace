---
description: Preview the current status line output with sample data
argument-hint: "[minimal | full] (default: full)"
---

# /pwdev-statusline:preview — Preview Status Line

## Role
Runs the status line script with sample data so the user can see the output without restarting Claude Code.

## Procedure

### STEP 1 — Check installation

1. Verify `~/.claude/statusline.sh` exists
2. If not → tell the user to run `/pwdev-statusline:install` first

### STEP 2 — Run preview

If `$ARGUMENTS` is "minimal" or empty:
```bash
echo '{"workspace":{"current_dir":"'$(pwd)'"},"model":{"display_name":"Opus 4.6"},"context_window":{"used_percentage":35,"total_input_tokens":50000,"total_output_tokens":12000},"rate_limits":{"five_hour":{"used_percentage":10}}}' | bash ~/.claude/statusline.sh
```

If `$ARGUMENTS` is "full":
```bash
echo '{"workspace":{"current_dir":"'$(pwd)'"},"model":{"display_name":"Opus 4.6"},"context_window":{"used_percentage":72,"total_input_tokens":500000,"total_output_tokens":120000},"rate_limits":{"five_hour":{"used_percentage":85}},"session_name":"feature/auth-refactor"}' | bash ~/.claude/statusline.sh
```

### STEP 3 — Show info

Print a legend of each section:
```
Legend:
  📂 Directory     — current working directory
  🤖 Model         — active Claude model
  🌿 Git Branch    — current branch (if in a git repo)
  📊 Context       — context window usage (bar + percentage)
  🔢 Tokens        — total input + output tokens
  ⏱️  Rate Limit    — 5-hour rate limit usage (green < 80%, red >= 80%)
  📛 Session       — session name (if set)
```
