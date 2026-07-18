# pwdev-statusline v1.1.0

Rich terminal status line for Claude Code — shows model, git branch, context usage, rate limits, and token counts in a colorful, single-line bar.

## What's New in v1.1.0

- **Configuration block**: all customization (SHOW_* toggles, colors,
  separator, directory depth) lives in variables at the top of the script —
  `/customize` edits one line, idempotently, instead of commenting code out.
- **Single jq pass**: all payload fields extracted in ONE `jq` call
  (was ~8 per render) — noticeably faster status updates.
- **Dynamic colors**: context bar turns green/yellow/red (<60 / 60-79 / ≥80%);
  rate limit gains a yellow tier (50-79%).
- **Readable segments**: tokens formatted as `512k` / `1.2M`; directory shows
  `~` and truncates to the last N segments (`…/a/b/c`, configurable).
- **Robustness**: non-numeric payload values no longer cause arithmetic
  errors — the segment just hides; template read via `${CLAUDE_PLUGIN_ROOT}`
  (the old relative path broke marketplace installs).
- **Safer commands**: `uninstall` confirms before deleting (your script may
  carry customizations); `install` is idempotent when already up to date;
  all 4 commands are manual-only (`disable-model-invocation`).

## Features

- **PWDEV** — company branding, first segment (green)
- **User** — git user name from `git config user.name` (white)
- **Session Name** — displayed when a session is named (white)
- **Directory** — cwd with `~` substitution, truncated (blue)
- **Model** — active Claude model name (cyan)
- **Git Branch** — current branch when inside a git repo (magenta)
- **Context Bar** — visual bar + percentage, green/yellow/red by usage
- **Tokens** — total in+out, formatted `512k`/`1.2M` (white)
- **Rate Limit** — 5-hour usage, green/yellow/red (50%/80% thresholds)

Every section can be toggled; fields absent from the payload hide gracefully.

## Requirements

- `jq` — JSON processor (used to parse Claude Code's status JSON)

## Commands

| Command | Description |
|---------|-------------|
| `/pwdev-statusline:install` | Install the script and configure Claude Code settings (idempotent) |
| `/pwdev-statusline:uninstall` | Remove the script and settings entry (asks first) |
| `/pwdev-statusline:customize` | Toggle sections, change colors, separator, directory depth |
| `/pwdev-statusline:preview` | Preview the status line output with sample data |

## Quick Start

```
/pwdev-statusline:install
```

Then restart Claude Code.

## Customization

```
/pwdev-statusline:customize show          # see current config
/pwdev-statusline:customize hide-tokens   # hide token counter
/pwdev-statusline:customize colors        # change section colors
/pwdev-statusline:customize separator ·   # change separator
/pwdev-statusline:customize dir-depth 2   # keep last 2 path segments
```

## License

Apache-2.0
