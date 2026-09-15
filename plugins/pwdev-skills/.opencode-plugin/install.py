#!/usr/bin/env python3
"""Expose the skills of this plugin to OpenCode.

OpenCode has no plugin mechanism for Agent Skills: it discovers ``<name>/SKILL.md`` folders in
``.opencode/skills/`` (project) and ``~/.config/opencode/skills/`` (global) — see
https://opencode.ai/docs/skills. This script puts every skill under ``skills/`` there, as a
symlink by default (edits in the checkout apply immediately) or as a copy (``--copy``), and
removes only what it installed (``--uninstall``). It never touches ``opencode.json`` or any
other OpenCode setting.

    python3 .opencode-plugin/install.py                     # link into ~/.config/opencode/skills
    python3 .opencode-plugin/install.py --project .         # link into <project>/.opencode/skills
    python3 .opencode-plugin/install.py --copy              # copy instead of link
    python3 .opencode-plugin/install.py --uninstall         # remove what this script installed
    python3 .opencode-plugin/install.py --dry-run           # show the plan, change nothing
"""
from __future__ import annotations

import argparse
import os
import shutil
import sys
from pathlib import Path
from typing import List, Optional

MARKER = ".installed-by-pwdev-skills"
IGNORE = shutil.ignore_patterns("__pycache__", "*.pyc", ".DS_Store")


def plugin_root() -> Path:
    return Path(__file__).resolve().parent.parent


def skills_of(root: Path) -> List[Path]:
    return sorted(p.parent for p in (root / "skills").glob("*/SKILL.md"))


def destination(project: Optional[Path]) -> Path:
    if project is not None:
        return Path(project).resolve() / ".opencode" / "skills"
    config = os.environ.get("XDG_CONFIG_HOME")
    base = Path(config) if config else Path.home() / ".config"
    return base / "opencode" / "skills"


def _ours(target: Path, source: Path) -> bool:
    """True when `target` is something this script installed from `source`."""
    if target.is_symlink():
        try:
            return target.resolve() == source.resolve()
        except OSError:
            return False
    return target.is_dir() and (target / MARKER).is_file()


def install(root: Path, dest: Path, *, copy: bool, force: bool, dry_run: bool, out=sys.stdout) -> int:
    skills = skills_of(root)
    if not skills:
        print(f"no skills under {root / 'skills'}", file=out)
        return 1
    if not dry_run:
        dest.mkdir(parents=True, exist_ok=True)
    failures = 0
    for source in skills:
        target = dest / source.name
        if target.exists() or target.is_symlink():
            if _ours(target, source):
                if target.is_symlink() and not copy:
                    print(f"already linked  {target} -> {source}", file=out)
                    continue
                if not dry_run:
                    _remove(target)
            elif not force:
                print(f"REFUSED         {target} exists and was not installed by this script (use --force)", file=out)
                failures += 1
                continue
            elif not dry_run:
                _remove(target)
        action = "copy" if copy else "link"
        print(f"{action:<15} {target} <- {source}", file=out)
        if dry_run:
            continue
        if copy:
            shutil.copytree(source, target, symlinks=False, ignore=IGNORE)
            (target / MARKER).write_text(f"{source}\n", encoding="utf-8")
        else:
            target.symlink_to(source, target_is_directory=True)
    return 1 if failures else 0


def uninstall(root: Path, dest: Path, *, dry_run: bool, out=sys.stdout) -> int:
    for source in skills_of(root):
        target = dest / source.name
        if not (target.exists() or target.is_symlink()):
            print(f"absent          {target}", file=out)
        elif _ours(target, source):
            print(f"remove          {target}", file=out)
            if not dry_run:
                _remove(target)
        else:
            print(f"kept            {target} (not installed by this script)", file=out)
    return 0


def _remove(target: Path) -> None:
    if target.is_symlink() or target.is_file():
        target.unlink()
    else:
        shutil.rmtree(target)


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--project", type=Path, default=None, help="install into <project>/.opencode/skills instead of the global dir")
    parser.add_argument("--copy", action="store_true", help="copy the skill folders instead of symlinking them")
    parser.add_argument("--force", action="store_true", help="replace a target this script did not install")
    parser.add_argument("--uninstall", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--root", type=Path, default=None, help=argparse.SUPPRESS)  # tests
    args = parser.parse_args(argv)
    root = (args.root or plugin_root()).resolve()
    dest = destination(args.project)
    if args.uninstall:
        return uninstall(root, dest, dry_run=args.dry_run)
    return install(root, dest, copy=args.copy, force=args.force, dry_run=args.dry_run)


if __name__ == "__main__":
    sys.exit(main())
