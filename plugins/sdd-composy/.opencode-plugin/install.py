#!/usr/bin/env python3
"""Expose SDD Composy to OpenCode: link the 17 skills and generate the 17 commands.

OpenCode has no plugin mechanism for Agent Skills. It discovers ``<name>/SKILL.md`` folders in
``.opencode/skills/`` (project) and ``~/.config/opencode/skills/`` (global), and custom commands in
the sibling ``command/`` folder — see https://opencode.ai/docs/skills and
https://opencode.ai/docs/commands. This script links every ``skills/sdd-*`` folder there and writes one
``command/sdd-<name>.md`` per ``commands/<name>.md``, so ``/sdd-<name>`` routes to the same shared skill
as ``/sdd-composy:<name>`` does on Claude Code. It removes only what it installed (``--uninstall``)
and never touches ``opencode.json`` or any other OpenCode setting.

There is deliberately no copy mode: every SKILL.md reaches ``scripts/``, ``references/`` and
``templates/`` by plugin-relative path. Those paths resolve through a symlink into the checkout and
would dangle inside a copied folder, so a copy would install skills that cannot run their helpers.

    python3 .opencode-plugin/install.py                 # link into ~/.config/opencode/{skills,command}
    python3 .opencode-plugin/install.py --project .     # link into <project>/.opencode/{skills,command}
    python3 .opencode-plugin/install.py --uninstall     # remove what this script installed
    python3 .opencode-plugin/install.py --dry-run       # show the plan, change nothing
"""
from __future__ import annotations

import argparse
import os
import re
import sys
from pathlib import Path
from typing import List, Optional

COMMAND_MARKER = "<!-- installed-by-sdd-composy -->"
COMMAND_TEMPLATE = (
    "---\n"
    "description: {description}\n"
    "---\n"
    "\n"
    "Load the `{skill}` skill with the `skill` tool and follow it for: $ARGUMENTS\n"
    "\n"
    "Return the skill's result unchanged.\n"
    f"{COMMAND_MARKER}\n"
)


class InventoryError(RuntimeError):
    """The plugin tree is not the closed, regular-file inventory the installer requires."""


def plugin_root() -> Path:
    return Path(__file__).resolve().parent.parent


def skills_of(root: Path) -> List[Path]:
    skills_dir = root / "skills"
    if skills_dir.is_symlink() or not skills_dir.is_dir():
        raise InventoryError(f"{skills_dir} must be a real directory")
    found: List[Path] = []
    for folder in sorted(skills_dir.iterdir()):
        if folder.is_symlink():
            raise InventoryError(f"{folder} is a symlink; skill folders must be real directories")
        skill = folder / "SKILL.md"
        if not (skill.exists() or skill.is_symlink()):
            continue
        if skill.is_symlink() or not skill.is_file():
            raise InventoryError(f"{skill} must be a regular file")
        found.append(folder)
    return found


def commands_of(root: Path) -> List[Path]:
    commands_dir = root / "commands"
    if not commands_dir.is_dir():
        return []
    return sorted(p for p in commands_dir.glob("*.md") if p.is_file() and not p.is_symlink())


def destination(project: Optional[Path]) -> Path:
    if project is not None:
        return Path(project).resolve() / ".opencode"
    config = os.environ.get("XDG_CONFIG_HOME")
    base = Path(config) if config else Path.home() / ".config"
    return base / "opencode"


def _description(command: Path) -> str:
    text = command.read_text(encoding="utf-8")
    match = re.search(r"^description:\s*(.+?)\s*$", text, flags=re.MULTILINE)
    return match.group(1).strip().strip('"') if match else f"SDD Composy {command.stem}"


def _render_command(command: Path) -> str:
    return COMMAND_TEMPLATE.format(description=_description(command), skill=f"sdd-{command.stem}")


def _own_link(target: Path, source: Path) -> bool:
    if not target.is_symlink():
        return False
    try:
        return target.resolve() == source.resolve()
    except OSError:
        return False


def _own_command(target: Path) -> bool:
    try:
        return target.is_file() and not target.is_symlink() and COMMAND_MARKER in target.read_text(encoding="utf-8")
    except OSError:
        return False


def _remove(target: Path) -> None:
    if target.is_symlink() or target.is_file():
        target.unlink()
    else:
        import shutil
        shutil.rmtree(target)


def install(root: Path, dest: Path, *, force: bool, dry_run: bool, out=sys.stdout) -> int:
    skills = skills_of(root)
    commands = commands_of(root)
    if not skills:
        print(f"no skills under {root / 'skills'}", file=out)
        return 1
    failures = 0
    plan: List[tuple] = []
    for source in skills:
        target = dest / "skills" / source.name
        if _own_link(target, source):
            print(f"already linked  {target} -> {source}", file=out)
            continue
        if (target.exists() or target.is_symlink()) and not force:
            print(f"REFUSED         {target} exists and was not installed by this script (use --force)", file=out)
            failures += 1
            continue
        plan.append(("link", target, source))
    for command in commands:
        target = dest / "command" / f"sdd-{command.stem}.md"
        rendered = _render_command(command)
        if _own_command(target):
            if target.read_text(encoding="utf-8") == rendered:
                print(f"already written {target}", file=out)
                continue
        elif (target.exists() or target.is_symlink()) and not force:
            print(f"REFUSED         {target} exists and was not installed by this script (use --force)", file=out)
            failures += 1
            continue
        plan.append(("command", target, rendered))
    if failures:
        return 1
    for action, target, payload in plan:
        if action == "link":
            print(f"link            {target} <- {payload}", file=out)
        else:
            print(f"write           {target}", file=out)
        if dry_run:
            continue
        target.parent.mkdir(parents=True, exist_ok=True)
        if target.exists() or target.is_symlink():
            _remove(target)
        if action == "link":
            target.symlink_to(payload, target_is_directory=True)
        else:
            target.write_text(payload, encoding="utf-8")
    return 0


def uninstall(root: Path, dest: Path, *, dry_run: bool, out=sys.stdout) -> int:
    for source in skills_of(root):
        target = dest / "skills" / source.name
        if not (target.exists() or target.is_symlink()):
            print(f"absent          {target}", file=out)
        elif _own_link(target, source):
            print(f"remove          {target}", file=out)
            if not dry_run:
                _remove(target)
        else:
            print(f"kept            {target} (not installed by this script)", file=out)
    for command in commands_of(root):
        target = dest / "command" / f"sdd-{command.stem}.md"
        if not (target.exists() or target.is_symlink()):
            print(f"absent          {target}", file=out)
        elif _own_command(target):
            print(f"remove          {target}", file=out)
            if not dry_run:
                _remove(target)
        else:
            print(f"kept            {target} (not installed by this script)", file=out)
    return 0


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--project", type=Path, default=None, help="install into <project>/.opencode instead of the global dir")
    parser.add_argument("--force", action="store_true", help="replace a target this script did not install")
    parser.add_argument("--uninstall", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--root", type=Path, default=None, help=argparse.SUPPRESS)  # tests
    args = parser.parse_args(argv)
    root = (args.root or plugin_root()).resolve()
    dest = destination(args.project)
    try:
        if args.uninstall:
            return uninstall(root, dest, dry_run=args.dry_run)
        return install(root, dest, force=args.force, dry_run=args.dry_run)
    except InventoryError as error:
        print(f"REFUSED         {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
