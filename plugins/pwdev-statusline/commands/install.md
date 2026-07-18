---
description: Install the PWDEV status line into Claude Code global settings
argument-hint: "[--force] (overwrite existing statusline.sh)"
disable-model-invocation: true
---

# /pwdev-statusline:install — Install Status Line

## Role
Installs the PWDEV status line script and configures Claude Code to use it.

## Procedure

### STEP 1 — Check prerequisites

1. Verify `jq` is installed on the system. If not, warn the user:
   ```
   ⚠️  jq is required for the status line. Install it:
   - Ubuntu/Debian: sudo apt install jq
   - macOS: brew install jq
   - Fedora: sudo dnf install jq
   ```
   Continue anyway (jq is only needed at runtime).

### STEP 2 — Read the template

1. Read the template script from
   `${CLAUDE_PLUGIN_ROOT}/templates/statusline.sh`.

### STEP 3 — Install the script

1. Target path: `~/.claude/statusline.sh`
2. **Idempotent check**: if the target exists and is IDENTICAL to the
   template → inform "already installed and up to date", skip to STEP 4.
3. If the target exists and differs, and `$ARGUMENTS` does NOT contain
   `--force`:
   - Show the user the diff between the existing file and the template
     (their copy may carry customizations from /pwdev-statusline:customize)
   - Ask: "Status line script already exists. Overwrite? (y/n)"
   - If no → skip to STEP 4
4. Copy the template content to `~/.claude/statusline.sh`
5. Make it executable: `chmod +x ~/.claude/statusline.sh`

### STEP 4 — Configure Claude Code settings

1. Read `~/.claude/settings.json`
2. Check if `statusLine` key already exists:
   - If it already points to `bash ~/.claude/statusline.sh` → inform user it's already configured, skip
   - Otherwise → set the `statusLine` configuration (merge — never drop other keys):
     ```json
     {
       "statusLine": {
         "type": "command",
         "command": "bash ~/.claude/statusline.sh"
       }
     }
     ```
3. Write the updated settings back to `~/.claude/settings.json`

### STEP 5 — Verify

1. Run a quick test: `echo '{}' | bash ~/.claude/statusline.sh`
2. If the output contains "(no data)" or a partial line → installation is OK
3. Print success message:
   ```
   ✅ PWDEV Status Line installed!

   📍 Script: ~/.claude/statusline.sh
   ⚙️  Settings: ~/.claude/settings.json (statusLine configured)

   Restart Claude Code to see the status line.
   Customize with /pwdev-statusline:customize
   ```

## Note on payload fields

The script reads `context_window`, `rate_limits`, and `session_name` from the
statusline stdin payload. Fields absent in your Claude Code version degrade
gracefully (the segment is hidden). If a segment never appears, check the
current payload schema with a real render.
