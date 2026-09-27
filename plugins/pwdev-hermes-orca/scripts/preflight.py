#!/usr/bin/env python3
"""Read-only readiness check before Hermes coordinates Orca workers.

Checks: running inside an Orca terminal, Orca runtime ready, current directory is an Orca
worktree, GitHub CLI authenticated for this repository, and pwdev-feat >= 3.2.0 (feat-loop)
installed for each routed agent. Never mutates anything.

    python3 preflight.py [--json] [--agents claude,codex]

Exit 0 when there is no blocker, 1 otherwise.
"""
from __future__ import annotations

import argparse
import glob
import json
import os
import re
import subprocess
import sys
from pathlib import Path

MIN_FEAT = (3, 2, 0)
KNOWN_AGENTS = ("claude", "codex", "opencode")


def run(*cmd: str, timeout: int = 20) -> tuple[int, str]:
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
    except (OSError, subprocess.TimeoutExpired) as exc:
        return 127, str(exc)
    return proc.returncode, (proc.stdout or "") + (proc.stderr or "")


def version(text: str) -> tuple[int, ...] | None:
    match = re.match(r"^(\d+)\.(\d+)\.(\d+)", text.strip())
    return tuple(int(part) for part in match.groups()) if match else None


def fmt(ver: tuple[int, ...] | None) -> str:
    return ".".join(map(str, ver)) if ver else "?"


def newest(paths: list[str], reader) -> tuple[int, ...] | None:
    found = [v for v in (reader(p) for p in paths) if v]
    return max(found) if found else None


def manifest_version(path: str) -> tuple[int, ...] | None:
    try:
        return version(json.loads(Path(path).read_text(encoding="utf-8")).get("version", ""))
    except (OSError, ValueError):
        return None


def skill_version(path: str) -> tuple[int, ...] | None:
    try:
        match = re.search(r"^\s*version:\s*([0-9.]+)", Path(path).read_text(encoding="utf-8"), re.M)
    except OSError:
        return None
    return version(match.group(1)) if match else None


def feat_version(agent: str, home: Path, project: Path) -> tuple[int, ...] | None:
    """Newest pwdev-feat visible to the agent; None when it cannot be found."""
    if agent == "claude":
        paths = glob.glob(str(home / ".claude/plugins/cache/*/pwdev-feat/*/.claude-plugin/plugin.json"))
        return newest(paths, manifest_version)
    if agent == "codex":
        paths = glob.glob(str(home / ".codex/plugins/cache/**/pwdev-feat/**/.codex-plugin/plugin.json"), recursive=True)
        return newest(paths, manifest_version)
    if agent == "opencode":
        paths = [str(p / "feat-loop/SKILL.md") for p in (project / ".opencode/skills", home / ".config/opencode/skills")]
        return newest([p for p in paths if os.path.isfile(p)], skill_version)
    return None


def check(agents: list[str], home: Path, project: Path) -> dict:
    blockers, warnings, facts = [], [], {}

    handle = os.environ.get("ORCA_TERMINAL_HANDLE", "")
    facts["orca_terminal"] = bool(handle)
    if not handle:
        blockers.append("fora de um terminal do Orca (ORCA_TERMINAL_HANDLE ausente): abra o Hermes numa aba do Orca")

    code, out = run("orca", "status", "--json")
    runtime = {}
    if code == 0:
        try:
            runtime = json.loads(out).get("result", {}).get("runtime", {})
        except ValueError:
            pass
    facts["orca_runtime"] = runtime.get("state", "unreachable")
    facts["orca_version"] = runtime.get("appVersion")
    if runtime.get("state") != "ready" or not runtime.get("reachable"):
        blockers.append("runtime do Orca não está pronto (`orca status --json`); rode `orca open`")

    code, out = run("orca", "worktree", "current", "--json")
    worktree = {}
    if code == 0:
        try:
            worktree = json.loads(out).get("result", {}).get("worktree", {}) or {}
        except ValueError:
            pass
    facts["orca_worktree"] = worktree.get("id")
    facts["orca_project"] = worktree.get("projectId")
    if not worktree:
        blockers.append("o diretório atual não é uma worktree do Orca (`orca worktree current`); rode `orca repo add --path .`")

    code, out = run("orca", "skills", "get", "orchestration")
    facts["orca_orchestration_skill"] = code == 0
    if code != 0:
        blockers.append("`orca skills get orchestration` falhou: atualize a CLI do Orca")

    code, out = run("gh", "auth", "status")
    facts["gh_auth"] = code == 0
    if code != 0:
        blockers.append("GitHub CLI sem autenticação: rode `gh auth login`")
    else:
        code, out = run("gh", "repo", "view", "--json", "nameWithOwner,defaultBranchRef")
        try:
            repo = json.loads(out) if code == 0 else {}
        except ValueError:
            repo = {}
        facts["gh_repo"] = repo.get("nameWithOwner")
        facts["default_branch"] = (repo.get("defaultBranchRef") or {}).get("name")
        if not repo:
            blockers.append("`gh repo view` falhou: o diretório atual não aponta para um repositório GitHub")

    facts["pwdev_feat"] = {}
    for agent in agents:
        found = feat_version(agent, home, project)
        facts["pwdev_feat"][agent] = fmt(found) if found else None
        if found is None:
            blockers.append(f"{agent}: pwdev-feat não encontrado (precisa ≥ {fmt(MIN_FEAT)} com feat-loop)")
        elif found < MIN_FEAT:
            blockers.append(f"{agent}: pwdev-feat {fmt(found)} instalado; atualize para ≥ {fmt(MIN_FEAT)} (feat-loop)")
    if not agents:
        warnings.append("nenhum agente informado em --agents: disponibilidade do pwdev-feat não verificada")

    return {"ok": not blockers, "blockers": blockers, "warnings": warnings, "facts": facts}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--json", action="store_true", help="emit JSON")
    parser.add_argument("--agents", default="", help="comma-separated routed agents (claude,codex,opencode)")
    args = parser.parse_args(argv)
    agents = [a.strip() for a in args.agents.split(",") if a.strip()]
    unknown = [a for a in agents if a not in KNOWN_AGENTS]
    if unknown:
        parser.error(f"unknown agent(s): {', '.join(unknown)}")
    report = check(agents, Path.home(), Path.cwd())
    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        for line in report["blockers"]:
            print(f"BLOCKER  {line}")
        for line in report["warnings"]:
            print(f"WARNING  {line}")
        print("OK" if report["ok"] else "NOT READY")
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
