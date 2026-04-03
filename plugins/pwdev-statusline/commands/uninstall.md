---
description: Remove the PWDEV status line from Claude Code settings and delete the script
---

# /pwdev-statusline:uninstall — Remove Status Line

## Role
Removes the PWDEV status line configuration and script.

## Procedure

### STEP 1 — Remove settings entry

1. Read `~/.claude/settings.json`
2. Remove the `statusLine` key entirely from the JSON
3. Write the updated settings back

### STEP 2 — Delete the script

1. Check if `~/.claude/statusline.sh` exists
2. If it exists → delete it
3. If it doesn't exist → inform the user (no action needed)

### STEP 3 — Confirm

Print:
```
✅ PWDEV Status Line removed.

⚙️  statusLine entry removed from ~/.claude/settings.json
🗑️  ~/.claude/statusline.sh deleted

Restart Claude Code to apply changes.
```
