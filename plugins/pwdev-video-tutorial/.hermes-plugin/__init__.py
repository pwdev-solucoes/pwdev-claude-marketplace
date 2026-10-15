"""Hermes adapter for pwdev-video-tutorial: registers the vtut-* skills and a first-turn bootstrap."""
from pathlib import Path


def _plugin_dir() -> Path:
    here = Path(__file__).resolve().parent
    for candidate in (here.parent, here):
        if (candidate / "skills" / "vtut-roteiro" / "SKILL.md").is_file():
            return candidate
    raise RuntimeError("pwdev-video-tutorial: cannot find the skills directory")


def _skills(root: Path) -> list:
    found = []
    for folder in sorted((root / "skills").iterdir()):
        skill = folder / "SKILL.md"
        if folder.name.startswith("vtut-") and not folder.is_symlink() and skill.is_file() and not skill.is_symlink():
            found.append((folder.name, skill))
    return found


def _bootstrap(root: Path) -> str:
    return (
        "<EXTREMELY_IMPORTANT>\n"
        "pwdev-video-tutorial is available: explainer and tutorial videos of software systems built "
        "from the real system. Route by intent with skill_view(\"pwdev-video-tutorial:vtut-<name>\"): "
        "vtut-explorar (code scan + playwright-cli navigation, system map), vtut-roadmap (series of "
        "videos), vtut-roteiro (storytelling script), vtut-narrar (narration), vtut-gravar (screen "
        "recording), vtut-montar (final video and text tutorial), vtut-revisar (check, render, deliver), "
        "vtut-setup (tools). Never ask for, type or store a password (the person logs in), never show "
        "real personal data (mask it or use fictitious data), never submit forms outside a test "
        "environment without the user's yes, and never put on screen anything the system does not do. "
        "Tools: terminal, read_file, write_file, patch. If a namespaced skill_view is not found, read "
        f"{root / 'skills'}/<name>/SKILL.md directly; plugin-relative paths in skills resolve against {root}.\n"
        "</EXTREMELY_IMPORTANT>"
    )


def register(ctx):
    root = _plugin_dir()
    skills = _skills(root)
    if not skills:
        raise RuntimeError("pwdev-video-tutorial: cannot find the skills directory")
    for name, path in skills:
        ctx.register_skill(name, path)
    bootstrap = _bootstrap(root)

    def pre_llm_call(is_first_turn=None, **kwargs):
        return {"context": bootstrap} if is_first_turn else None

    ctx.register_hook("pre_llm_call", pre_llm_call)
