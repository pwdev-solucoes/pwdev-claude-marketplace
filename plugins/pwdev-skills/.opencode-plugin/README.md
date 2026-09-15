# OpenCode adapter

OpenCode has no plugin format for Agent Skills. It discovers `<name>/SKILL.md` folders in
`.opencode/skills/` (project) and `~/.config/opencode/skills/` (global), plus the compatible
folders `.claude/skills/`, `~/.claude/skills/`, `.agents/skills/` and `~/.agents/skills/`
([opencode.ai/docs/skills](https://opencode.ai/docs/skills)). A Claude Code *plugin* install lives
in Claude's plugin cache, which OpenCode does not read — so this plugin ships an installer instead
of a manifest.

`install.py` puts every skill under `../skills/` where OpenCode looks, and nothing else:

```bash
python3 plugins/pwdev-skills/.opencode-plugin/install.py                 # symlinks into ~/.config/opencode/skills
python3 plugins/pwdev-skills/.opencode-plugin/install.py --project .     # symlinks into ./.opencode/skills
python3 plugins/pwdev-skills/.opencode-plugin/install.py --copy          # copies (for a machine without the checkout)
python3 plugins/pwdev-skills/.opencode-plugin/install.py --uninstall     # removes only what it installed
python3 plugins/pwdev-skills/.opencode-plugin/install.py --dry-run       # prints the plan
```

- A symlink means edits in the checkout apply at once; a copy carries a marker file
  (`.installed-by-pwdev-skills`) so `--uninstall` can tell it from the user's own skills.
- A target that this script did not create is refused unless `--force` is given, and is never
  removed by `--uninstall`.
- `XDG_CONFIG_HOME` is honoured for the global directory. `opencode.json` and every other
  OpenCode setting stay untouched.

Once installed, the agent lists `skill-refactor` and loads it on demand through its native `skill`
tool; scripts run from the installed folder.
