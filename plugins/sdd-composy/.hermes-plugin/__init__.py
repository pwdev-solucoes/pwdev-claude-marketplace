"""Hermes bootstrap for SDD Composy."""
from pathlib import Path
import os, re

def _plugin_dir() -> str:
    here = Path(__file__).resolve().parent
    for candidate in (here.parent, here):
        if (candidate / "skills" / "sdd-init" / "SKILL.md").is_file():
            return str(candidate)
    raise RuntimeError("sdd-composy: skills directory not found")

def _strip_frontmatter(text: str) -> str:
    match = re.match(r"^---\n[\s\S]*?\n---\n([\s\S]*)$", text)
    return (match.group(1) if match else text).strip()

def _bootstrap(root: str) -> str:
    root_path = Path(root)
    power = _strip_frontmatter((root_path / "skills/sdd-init/SKILL.md").read_text(encoding="utf-8"))
    mapping = (root_path / "references/hermes-tools.md").read_text(encoding="utf-8").strip()
    return ("<EXTREMELY_IMPORTANT>\n"
            "sdd-composy Hermes bootstrap loaded. Use the registered SDD Composy skills.\n\n"
            f"{power}\n\n{mapping}\n"
            "Do not fall back silently to Claude or Codex.\n"
            "</EXTREMELY_IMPORTANT>")

def register(ctx):
    root = Path(_plugin_dir())
    for skill in sorted((root / "skills").iterdir()):
        path = skill / "SKILL.md"
        if path.is_file():
            ctx.register_skill(skill.name, path)
    bootstrap = _bootstrap(str(root))
    def pre_llm_call(is_first_turn=None, **kwargs):
        return {"context": bootstrap} if is_first_turn else None
    ctx.register_hook("pre_llm_call", pre_llm_call)
