"""Hermes bootstrap for SDD Composy."""
from pathlib import Path

def _plugin_dir() -> str:
    here = Path(__file__).resolve().parent
    for candidate in (here.parent, here):
        if (candidate / "skills" / "sdd-init" / "SKILL.md").is_file():
            return str(candidate)
    raise RuntimeError("sdd-composy: skills directory not found")

def _bootstrap(root: str) -> str:
    return ("<EXTREMELY_IMPORTANT>\n"
            "SDD Composy routing is available through the registered skills. Read AGENTS.md "
            "before changing a project. Invoke the capability needed for the current request "
            "with skill_view(\"sdd-composy:skill-name\"); load its referenced local resources "
            "only when needed. Use read_file, write_file or patch, terminal, search_files, and "
            "delegate_task according to that skill. Do not start a lifecycle, mutate project "
            "state, or dispatch work merely because this bootstrap loaded. Do not fall back "
            "silently to Claude or Codex. Automated Hermes execution requires independently "
            "established isolation or the user's specific consent.\n"
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
