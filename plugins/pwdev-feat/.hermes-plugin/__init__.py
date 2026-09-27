"""Hermes adapter for pwdev-feat: registers the thirteen feat-* skills and a first-turn bootstrap."""
from pathlib import Path


def _plugin_dir() -> Path:
    here = Path(__file__).resolve().parent
    for candidate in (here.parent, here):
        if (candidate / "skills" / "feat-exec" / "SKILL.md").is_file():
            return candidate
    raise RuntimeError("pwdev-feat: cannot find the skills directory")


def _skills(root: Path) -> list:
    found = []
    for folder in sorted((root / "skills").iterdir()):
        skill = folder / "SKILL.md"
        if folder.name.startswith("feat-") and not folder.is_symlink() and skill.is_file() and not skill.is_symlink():
            found.append((folder.name, skill))
    return found


def _bootstrap(root: Path) -> str:
    return (
        "<EXTREMELY_IMPORTANT>\n"
        "pwdev-feat is available: fast feature plans and execution. Route by intent with "
        "skill_view(\"pwdev-feat:feat-<name>\"): feat-init (setup), feat-map (codebase context), "
        "feat-setup (project instructions file), feat-feature / feat-backend / feat-frontend / "
        "feat-test / feat-review (plans), feat-exec (execute a plan), feat-loop (GitHub issue → plan, exec, review, PR), feat-quick (small change "
        "without a plan), feat-status, feat-audit. Load a skill only when the request needs it; "
        "do not create plans, dispatch work or change files merely because this bootstrap loaded. "
        "Tools: read_file, write_file, patch, terminal, search_files, delegate_task (run inline "
        "when it is unavailable). If a namespaced skill_view is not found, read "
        f"{root / 'skills'}/<name>/SKILL.md directly; plugin-relative paths in skills resolve "
        f"against {root}.\n"
        "</EXTREMELY_IMPORTANT>"
    )


def register(ctx):
    root = _plugin_dir()
    skills = _skills(root)
    if not skills:
        raise RuntimeError("pwdev-feat: cannot find the skills directory")
    for name, path in skills:
        ctx.register_skill(name, path)
    bootstrap = _bootstrap(root)

    def pre_llm_call(is_first_turn=None, **kwargs):
        return {"context": bootstrap} if is_first_turn else None

    ctx.register_hook("pre_llm_call", pre_llm_call)
