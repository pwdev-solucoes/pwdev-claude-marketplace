"""Hermes adapter for pwdev-github: registers the github-* skills and a first-turn bootstrap."""
from pathlib import Path


def _plugin_dir() -> Path:
    here = Path(__file__).resolve().parent
    for candidate in (here.parent, here):
        if (candidate / "skills" / "github-issues" / "SKILL.md").is_file():
            return candidate
    raise RuntimeError("pwdev-github: cannot find the skills directory")


def _skills(root: Path) -> list:
    found = []
    for folder in sorted((root / "skills").iterdir()):
        skill = folder / "SKILL.md"
        if folder.name.startswith("github-") and not folder.is_symlink() and skill.is_file() and not skill.is_symlink():
            found.append((folder.name, skill))
    return found


def _bootstrap(root: Path) -> str:
    return (
        "<EXTREMELY_IMPORTANT>\n"
        "pwdev-github is available: GitHub Projects from templates, roadmap publishing and "
        "day-to-day issue work through the gh CLI. Route by intent with "
        "skill_view(\"pwdev-github:github-<name>\"): github-init (setup), github-project (create "
        "a Project from a preset or template), github-publish (publish a pwdev-roadmap/1 "
        "roadmap.json), github-issues (create, update, close issues; sub-issues, blocked-by, "
        "Project fields), github-status. Load a skill only when the request needs it; never "
        "write to GitHub without a preview and the user's explicit yes. Tools: terminal (gh, "
        f"python3), read_file, write_file. If a namespaced skill_view is not found, read "
        f"{root / 'skills'}/<name>/SKILL.md directly; plugin-relative paths in skills resolve "
        f"against {root}.\n"
        "</EXTREMELY_IMPORTANT>"
    )


def register(ctx):
    root = _plugin_dir()
    skills = _skills(root)
    if not skills:
        raise RuntimeError("pwdev-github: cannot find the skills directory")
    for name, path in skills:
        ctx.register_skill(name, path)
    bootstrap = _bootstrap(root)

    def pre_llm_call(is_first_turn=None, **kwargs):
        return {"context": bootstrap} if is_first_turn else None

    ctx.register_hook("pre_llm_call", pre_llm_call)
