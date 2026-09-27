#!/usr/bin/env python3
"""pwdev-feat workspace state — plans, execution status, mode and resume point.

Usage (run from the project root; prints JSON):
  feat_state.py list                    every plan with its status
  feat_state.py resolve <slug|latest>   one plan: paths, status, mode, resume step
  feat_state.py mode <plan.md>          IMPLEMENT or REPORT
  feat_state.py precheck <slug>         base commit, dirty planned files, resume step

Status comes from the ``<!-- feat-status: ... -->`` marker of plan.done.md,
falling back to the literal strings written by pwdev-feat 2.x.
"""
from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

FEATURES = Path(".planning/feat/features")
MARKER = re.compile(r"<!--\s*feat-status:\s*(COMPLETE|CAVEATS|FAILED)\s*-->")
LEGACY = [("FAILED", "FAILED"), ("WITH CAVEATS", "CAVEATS"), ("COMPLETE", "COMPLETE")]


def git(*args: str) -> str:
    try:
        proc = subprocess.run(["git", *args], text=True, capture_output=True, timeout=10)
        return proc.stdout if proc.returncode == 0 else ""
    except (OSError, subprocess.SubprocessError):
        return ""


def read(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except OSError:
        return ""


def frontmatter(text: str) -> dict[str, str]:
    match = re.match(r"^---\n(.*?)\n---\n", text, re.S)
    if not match:
        return {}
    return {k: v.strip() for k, v in re.findall(r"^([A-Za-z_]+):\s*(.*)$", match.group(1), re.M)}


def plan_type(text: str) -> str | None:
    fm = frontmatter(text)
    if fm.get("plan_type"):
        return fm["plan_type"]
    match = re.search(r"^>\s*\*\*Type:\*\*\s*([a-z]+)", text, re.M)
    return match.group(1) if match else None


def output_files(text: str) -> list[str]:
    match = re.search(r"^##\s+4\.\s*Output Format\s*$(.*?)(?=^##\s|\Z)", text, re.M | re.S)
    if not match:
        return []
    files = []
    for line in match.group(1).splitlines():
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) < 2 or not line.strip().startswith("|") or re.match(r"^[\s:-]+$", cells[0]):
            continue
        path = cells[0].strip("`").strip()
        if path and path.lower() != "file" and not path.startswith("{"):
            files.append(path)
    return files


def mode(text: str) -> str:
    if plan_type(text) == "review":
        return "REPORT"
    files = output_files(text)
    if files and all(f.startswith(".planning/") for f in files):
        return "REPORT"
    return "IMPLEMENT"


def status(feature_dir: Path) -> str:
    done = feature_dir / "plan.done.md"
    if not done.is_file():
        return "PENDING"
    text = read(done)
    marker = MARKER.search(text)
    if marker:
        return marker.group(1)
    for needle, value in LEGACY:
        if needle in text:
            return value
    return "EXECUTED"


def progress(feature_dir: Path) -> dict:
    text = read(feature_dir / "progress.md")
    if not text:
        return {"exists": False, "base_commit": None, "done": [], "resume_step": None}
    base = re.search(r"\*\*Base commit:\*\*\s*`?([0-9a-f]{7,64})`?", text)
    rows = re.findall(r"^\|\s*(\d+)\s*\|\s*([a-z]+)\s*\|", text, re.M)
    done = [int(n) for n, st in rows if st == "done"]
    pending = sorted(int(n) for n, st in rows if st != "done")
    return {"exists": True, "base_commit": base.group(1) if base else None, "done": sorted(done),
            "resume_step": pending[0] if pending else None}


def describe(feature_dir: Path) -> dict:
    plan = feature_dir / "plan.md"
    text = read(plan)
    fm = frontmatter(text)
    return {
        "slug": feature_dir.name,
        "dir": feature_dir.as_posix(),
        "plan": plan.as_posix(),
        "schema_version": 3 if fm.get("schema_version") == "3" else 2,
        "plan_type": plan_type(text),
        "status": status(feature_dir),
        "mode": mode(text),
        "outputs": output_files(text),
        "progress": progress(feature_dir),
        "reports": sorted(p.name for p in feature_dir.glob("*.md") if p.name != "plan.md"),
    }


def plans() -> list[Path]:
    if not FEATURES.is_dir():
        return []
    dirs = [d for d in FEATURES.iterdir() if d.is_dir() and (d / "plan.md").is_file()]
    return sorted(dirs, key=lambda d: (d / "plan.md").stat().st_mtime, reverse=True)


def resolve(ref: str) -> dict:
    if ref in ("", "latest"):
        for d in plans():
            if status(d) == "PENDING" or progress(d)["resume_step"]:
                return {"ok": True, **describe(d)}
        return {"ok": False, "error": "PLAN_NOT_FOUND", "hint": "no pending plan"}
    d = FEATURES / ref
    if not (d / "plan.md").is_file():
        return {"ok": False, "error": "PLAN_NOT_FOUND", "slug": ref}
    return {"ok": True, **describe(d)}


def precheck(ref: str) -> dict:
    info = resolve(ref)
    if not info.get("ok"):
        return info
    head = git("rev-parse", "HEAD").strip() or None
    porcelain = git("status", "--porcelain", "--untracked-files=all")
    dirty = {line[3:].split(" -> ")[-1].strip() for line in porcelain.splitlines() if len(line) > 3}
    planned = set(info["outputs"])
    return {
        "ok": True,
        "slug": info["slug"],
        "mode": info["mode"],
        "status": info["status"],
        "head": head,
        "base_commit": info["progress"]["base_commit"] or head,
        "branch": git("branch", "--show-current").strip() or None,
        "dirty_planned_files": sorted(planned & dirty),
        "dirty_other_files": len(dirty - planned - {p for p in dirty if p.startswith(".planning/")}),
        "resume_step": info["progress"]["resume_step"],
        "already_executed": info["status"] != "PENDING",
    }


def main(argv: list[str] | None = None) -> int:
    args = sys.argv[1:] if argv is None else argv
    if not args or args[0] not in ("list", "resolve", "mode", "precheck"):
        print(__doc__, file=sys.stderr)
        return 2
    cmd = args[0]
    if cmd == "list":
        items = [describe(d) for d in plans()]
        counts: dict[str, int] = {}
        for item in items:
            counts[item["status"]] = counts.get(item["status"], 0) + 1
        result = {"ok": True, "counts": counts, "plans": items,
                  "codebase_md": Path(".planning/feat/codebase.md").is_file(),
                  "context_docs": sorted(p.name for p in Path(".planning/feat/context").glob("*.md")),
                  "instructions_files": [n for n in ("AGENTS.md", "CLAUDE.md") if Path(n).is_file()]}
    elif cmd == "mode":
        if len(args) != 2 or not Path(args[1]).is_file():
            print(json.dumps({"ok": False, "error": "usage: mode <plan.md>"}))
            return 2
        result = {"ok": True, "mode": mode(read(Path(args[1])))}
    elif cmd == "resolve":
        result = resolve(args[1] if len(args) > 1 else "latest")
    else:
        result = precheck(args[1] if len(args) > 1 else "latest")
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0 if result.get("ok") else 1


if __name__ == "__main__":
    sys.exit(main())
