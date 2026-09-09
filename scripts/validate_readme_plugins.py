#!/usr/bin/env python3
"""Validate README plugin rows against Claude/Codex manifests."""
from __future__ import annotations
import json, re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ROW = re.compile(r"\[(?:\*\*)?([^\]*]+?)(?:\*\*)?\]\(\./plugins/([^/]+)/\).*?\|\s*([0-9]+\.[0-9]+\.[0-9]+)\s*\|")

def manifests():
    result = {}
    for path in sorted((ROOT / "plugins").glob("*/.claude-plugin/plugin.json")):
        data = json.loads(path.read_text())
        result[path.parent.parent.name] = data
    return result

def rows(text):
    return {m.group(2): (m.group(1), m.group(3)) for m in ROW.finditer(text)}

def validate():
    expected = manifests()
    errors = []
    parsed = {}
    for name in ("README.md", "README.pt-BR.md"):
        parsed[name] = rows((ROOT / name).read_text())
        missing = set(expected) - set(parsed[name])
        extra = set(parsed[name]) - set(expected)
        if missing: errors.append(f"{name}: missing {sorted(missing)}")
        if extra: errors.append(f"{name}: unknown {sorted(extra)}")
        for plugin, data in expected.items():
            if plugin in parsed[name]:
                label, version = parsed[name][plugin]
                if label != data["name"]: errors.append(f"{name}: {plugin} name mismatch")
                if version != data["version"]: errors.append(f"{name}: {plugin} version mismatch")
    if set(parsed["README.md"]) != set(parsed["README.pt-BR.md"]):
        errors.append("README language tables differ")
    return errors

if __name__ == "__main__":
    errors = validate()
    if errors:
        for error in errors: print(error)
        raise SystemExit(1)
    print(f"validated {len(manifests())} plugins in both READMEs")
