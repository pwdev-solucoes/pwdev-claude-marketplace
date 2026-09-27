"""Hermes adapter for pwdev-prd: registers the prd-* skills and a first-turn bootstrap."""
from pathlib import Path


def _plugin_dir() -> Path:
    here = Path(__file__).resolve().parent
    for candidate in (here.parent, here):
        if (candidate / "skills" / "prd-create" / "SKILL.md").is_file():
            return candidate
    raise RuntimeError("pwdev-prd: cannot find the skills directory")


def _skills(root: Path) -> list:
    found = []
    for folder in sorted((root / "skills").iterdir()):
        skill = folder / "SKILL.md"
        if folder.name.startswith("prd-") and not folder.is_symlink() and skill.is_file() and not skill.is_symlink():
            found.append((folder.name, skill))
    return found


def _bootstrap(root: Path) -> str:
    return (
        "<EXTREMELY_IMPORTANT>\n"
        "pwdev-prd is available: interview-driven PRDs, a roadmap with an explicit dependency "
        "chain, and GitHub publishing. Route by intent with skill_view(\"pwdev-prd:prd-<name>\"): "
        "prd-init (setup), prd-create (new PRD by interview), prd-refine (change a PRD), "
        "prd-list, prd-export (JSON or one GitHub issue), prd-roadmap (approved PRD -> roadmap "
        "with dependencies, waves, critical path, draft stories), prd-stories (evolve each "
        "feature with user stories, CA and RN), prd-publish (roadmap -> GitHub via pwdev-github), "
        "prd-audit. Load a skill only when the request needs it; do not write PRDs or change files "
        "merely because this bootstrap loaded. Tools: read_file, write_file, patch, terminal, "
        "search_files, delegate_task (write the roadmap inline when it is unavailable). If a "
        f"namespaced skill_view is not found, read {root / 'skills'}/<name>/SKILL.md directly; "
        f"plugin-relative paths in skills resolve against {root}.\n"
        "</EXTREMELY_IMPORTANT>"
    )


def register(ctx):
    root = _plugin_dir()
    skills = _skills(root)
    if not skills:
        raise RuntimeError("pwdev-prd: cannot find the skills directory")
    for name, path in skills:
        ctx.register_skill(name, path)
    bootstrap = _bootstrap(root)

    def pre_llm_call(is_first_turn=None, **kwargs):
        return {"context": bootstrap} if is_first_turn else None

    ctx.register_hook("pre_llm_call", pre_llm_call)
