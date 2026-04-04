# pwdev-statusline

Rich terminal status line for Claude Code — shows model, git branch, context usage, rate limits, and token counts in a colorful, single-line bar.

## Features

- **Directory** — current working directory (blue)
- **Model** — active Claude model name (cyan)
- **Git Branch** — current branch when inside a git repo (magenta)
- **Context Bar** — visual progress bar + percentage of context window used (yellow)
- **Rate Limit** — 5-hour rate limit usage, color-coded green/red at 80% threshold
- **Tokens** — total input + output token count (white)
- **Session Name** — displayed when a session is named (white)
- **PWDEV** — company branding, always visible as the first segment (green)
- **User** — git user name from `git config user.name` (white)

## Requirements

- `jq` — JSON processor (used to parse Claude Code's status JSON)

## Commands

| Command | Description |
|---------|-------------|
| `/pwdev-statusline:install` | Install the script and configure Claude Code settings |
| `/pwdev-statusline:uninstall` | Remove the script and settings entry |
| `/pwdev-statusline:customize` | Toggle sections, change colors, reorder segments |
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
```

## License

Apache-2.0
