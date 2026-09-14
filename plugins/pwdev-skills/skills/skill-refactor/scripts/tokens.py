#!/usr/bin/env python3
"""Measure a skill's size per file, per context layer and per load scenario.

Sizes are reported in characters, bytes, words, lines and tokens. Tokens come
from a generic tokenizer (tiktoken ``o200k_base``) when it is installed; otherwise
a ``chars / 4`` estimate is used and every number is labelled ``estimate`` so a
reader never mistakes it for a measurement. Empirical per-runtime token usage is
a different measurement and is recorded by ``bench.py``.

Usage:
    tokens.py <skill_dir> [--baseline <dir>] [--json] [--encoding o200k_base] [--no-tiktoken]
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple

DEFAULT_ENCODING = "o200k_base"
FRONTMATTER = re.compile(r"^---\n(.*?)\n---\n(.*)$", re.S)

# Load scenarios describe which files an agent actually has in context for a
# kind of request. They are the unit that matters: a shorter reference nobody
# loads saves nothing, and a longer core is paid on every activation.
DEFAULT_SCENARIOS: List[Tuple[str, List[str]]] = [
    ("review-only (core)", ["SKILL.md#body"]),
    ("refactor (core + refactoring)", ["SKILL.md#body", "references/refactoring.md"]),
    ("refactor + evaluation (core + both references)",
     ["SKILL.md#body", "references/refactoring.md", "references/evaluation.md"]),
    ("everything (worst case)", ["SKILL.md#body", "references/*.md", "README.md", "evals/evals.json"]),
]


class Tokenizer:
    """Generic tokenizer with an explicit, labelled fallback."""

    def __init__(self, encoding: str = DEFAULT_ENCODING, allow_tiktoken: bool = True):
        self.encoding_name = encoding
        self._encoder = None
        if allow_tiktoken:
            try:
                import tiktoken  # type: ignore

                self._encoder = tiktoken.get_encoding(encoding)
            except Exception:  # missing package or encoding: fall back, but say so
                self._encoder = None
        self.source = f"tiktoken:{encoding}" if self._encoder else "estimate:chars/4"

    def count(self, text: str) -> int:
        if self._encoder is not None:
            return len(self._encoder.encode(text, disallowed_special=()))
        return round(len(text) / 4)


def split_frontmatter(text: str) -> Tuple[str, str]:
    match = FRONTMATTER.match(text)
    return (match.group(1), match.group(2)) if match else ("", text)


def description_of(frontmatter: str) -> str:
    match = re.search(r"^description:[ \t]*(>-?|\|-?)?[ \t]*\n?((?:[ \t]+.*(?:\n|$))+|.*)", frontmatter, re.M)
    if not match:
        return ""
    if match.group(1):  # block scalar: indented continuation lines
        return " ".join(line.strip() for line in match.group(2).splitlines() if line.strip())
    return match.group(2).strip()


def measure_text(text: str, tokenizer: Tokenizer) -> Dict[str, int]:
    return {
        "chars": len(text),
        "bytes": len(text.encode("utf-8")),
        "words": len(text.split()),
        "lines": text.count("\n") + (1 if text and not text.endswith("\n") else 0),
        "tokens": tokenizer.count(text),
    }


def skill_files(skill_dir: Path) -> List[Path]:
    """Files an agent may load into context. Scripts run; they are never read in."""
    files = [p for p in sorted(skill_dir.rglob("*")) if p.is_file() and not p.is_symlink()]
    skipped_dirs = {"__pycache__", "scripts", "benchmarks"}
    return [p for p in files
            if not skipped_dirs.intersection(p.relative_to(skill_dir).parts[:-1])
            and p.suffix in {".md", ".json", ".yaml", ".yml", ".txt"}]


def measure_skill(skill_dir: Path, tokenizer: Optional[Tokenizer] = None,
                  scenarios: Optional[List[Tuple[str, List[str]]]] = None) -> Dict:
    tokenizer = tokenizer or Tokenizer()
    skill_dir = Path(skill_dir)
    files: Dict[str, Dict[str, int]] = {}
    for path in skill_files(skill_dir):
        files[path.relative_to(skill_dir).as_posix()] = measure_text(path.read_text(encoding="utf-8"), tokenizer)

    layers: Dict[str, Dict[str, int]] = {}
    skill_md = skill_dir / "SKILL.md"
    if skill_md.is_file():
        frontmatter, body = split_frontmatter(skill_md.read_text(encoding="utf-8"))
        layers["SKILL.md#description"] = measure_text(description_of(frontmatter), tokenizer)
        layers["SKILL.md#frontmatter"] = measure_text(frontmatter, tokenizer)
        layers["SKILL.md#body"] = measure_text(body, tokenizer)
    for rel, stats in files.items():
        if rel != "SKILL.md":
            layers[rel] = stats

    def expand(pattern: str) -> List[str]:
        if pattern in layers:
            return [pattern]
        if "*" in pattern:
            return sorted(rel for rel in layers if Path(rel).match(pattern) and "#" not in rel)
        return []

    scenario_rows = {}
    for name, patterns in (scenarios or DEFAULT_SCENARIOS):
        members = [m for p in patterns for m in expand(p)]
        totals = {k: sum(layers[m][k] for m in members) for k in ("chars", "bytes", "words", "lines", "tokens")}
        scenario_rows[name] = {"members": members, **totals}

    return {
        "skill_dir": str(skill_dir),
        "tokens_source": tokenizer.source,
        "files": files,
        "layers": layers,
        "scenarios": scenario_rows,
        "total": {k: sum(s[k] for s in files.values()) for k in ("chars", "bytes", "words", "lines", "tokens")},
    }


def _delta(after: int, before: Optional[int]) -> str:
    if before is None:
        return "new"
    diff = after - before
    pct = f" ({diff / before * 100:+.0f}%)" if before else ""
    return f"{diff:+d}{pct}"


def render_markdown(current: Dict, baseline: Optional[Dict] = None) -> str:
    source = current["tokens_source"]
    label = "tokens" if source.startswith("tiktoken") else "tokens (estimate)"
    out = [f"# Skill size — `{Path(current['skill_dir']).name}`", "",
           f"Token source: `{source}`" + ("" if source.startswith("tiktoken") else
                                          " — install `tiktoken` for measured counts"), ""]

    def table(title: str, key: str, cols: Tuple[str, ...] = ("chars", "words", "tokens")):
        out.append(f"## {title}")
        out.append("")
        head = "| Item | " + " | ".join(c if c != "tokens" else label for c in cols)
        if baseline:
            head += f" | Δ {label}"
        out.append(head + " |")
        out.append("|---|" + "---:|" * (len(cols) + (1 if baseline else 0)))
        base_rows = baseline.get(key, {}) if baseline else {}
        for name, row in current[key].items():
            cells = [f"{row[c]:,}" for c in cols]
            if baseline:
                cells.append(_delta(row["tokens"], base_rows.get(name, {}).get("tokens")))
            out.append(f"| `{name}` | " + " | ".join(cells) + " |")
        total = current["total"] if key == "files" else None
        if total:
            cells = [f"{total[c]:,}" for c in cols]
            if baseline:
                cells.append(_delta(total["tokens"], baseline["total"]["tokens"]))
            out.append("| **total** | " + " | ".join(cells) + " |")
        out.append("")

    table("Files", "files", ("chars", "bytes", "words", "lines", "tokens"))
    table("Context layers", "layers")
    table("Load scenarios", "scenarios")
    return "\n".join(out)


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("skill_dir", type=Path)
    parser.add_argument("--baseline", type=Path, help="previous version of the skill, for deltas")
    parser.add_argument("--json", action="store_true", help="emit JSON instead of Markdown")
    parser.add_argument("--encoding", default=DEFAULT_ENCODING)
    parser.add_argument("--no-tiktoken", action="store_true", help="force the labelled chars/4 estimate")
    args = parser.parse_args(argv)
    if not (args.skill_dir / "SKILL.md").is_file():
        parser.error(f"{args.skill_dir} has no SKILL.md")
    tokenizer = Tokenizer(args.encoding, allow_tiktoken=not args.no_tiktoken)
    current = measure_skill(args.skill_dir, tokenizer)
    baseline = measure_skill(args.baseline, tokenizer) if args.baseline else None
    if args.json:
        print(json.dumps({"current": current, "baseline": baseline}, indent=2, ensure_ascii=False))
    else:
        print(render_markdown(current, baseline))
    return 0


if __name__ == "__main__":
    sys.exit(main())
