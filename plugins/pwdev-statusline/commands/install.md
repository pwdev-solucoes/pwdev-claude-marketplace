---
description: Install the PWDEV status line into Claude Code global settings
argument-hint: "[--force] (overwrite existing statusline.sh)"
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

1. Read the template script from this plugin:
   `plugins/pwdev-statusline/templates/statusline.sh`

### STEP 3 — Install the script

1. Determine the target path: `~/.claude/statusline.sh`
2. If the file already exists and `$ARGUMENTS` does NOT contain `--force`:
   - Show the user the diff between the existing file and the template
   - Ask: "Status line script already exists. Overwrite? (y/n)"
   - If no → skip to STEP 4
3. Copy the template content to `~/.claude/statusline.sh`
4. Make it executable: `chmod +x ~/.claude/statusline.sh`

### STEP 4 — Configure Claude Code settings

1. Read `~/.claude/settings.json`
2. Check if `statusLine` key already exists:
   - If it already points to `bash ~/.claude/statusline.sh` → inform user it's already configured, skip
   - Otherwise → set the `statusLine` configuration:
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
   ```
