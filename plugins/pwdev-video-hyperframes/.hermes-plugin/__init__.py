"""Hermes adapter for pwdev-video-hyperframes: registers the vhf-* skills and a first-turn bootstrap."""
from pathlib import Path


def _plugin_dir() -> Path:
    here = Path(__file__).resolve().parent
    for candidate in (here.parent, here):
        if (candidate / "skills" / "vhf-editar" / "SKILL.md").is_file():
            return candidate
    raise RuntimeError("pwdev-video-hyperframes: cannot find the skills directory")


def _skills(root: Path) -> list:
    found = []
    for folder in sorted((root / "skills").iterdir()):
        skill = folder / "SKILL.md"
        if folder.name.startswith("vhf-") and not folder.is_symlink() and skill.is_file() and not skill.is_symlink():
            found.append((folder.name, skill))
    return found


def _bootstrap(root: Path) -> str:
    return (
        "<EXTREMELY_IMPORTANT>\n"
        "pwdev-video-hyperframes is available: talking-video editing by conversation with HyperFrames "
        "(cut by the waveform, captions, zooms, scenes, sound, studio, quality gate), on top of the "
        "`pwdev-media` CLI. Route by intent with skill_view(\"pwdev-video-hyperframes:vhf-<name>\"): "
        "vhf-editar (edit a video end to end; start here), vhf-corte (cut only), vhf-plano (what appears "
        "on screen), vhf-cenas (custom animated scene), vhf-som (music and effects), vhf-revisar (render "
        "and deliver), vhf-variacoes (versions, hooks, formats), vhf-setup (tools). Never modify the raw "
        "videos, never invent numbers or claims that are not in the speech, never spend money without the "
        "user's explicit yes, and deliver only when the gate prints PASSOU. Tools: terminal, read_file, "
        f"write_file, patch. If a namespaced skill_view is not found, read {root / 'skills'}/<name>/SKILL.md "
        f"directly; plugin-relative paths in skills resolve against {root}.\n"
        "</EXTREMELY_IMPORTANT>"
    )


def register(ctx):
    root = _plugin_dir()
    skills = _skills(root)
    if not skills:
        raise RuntimeError("pwdev-video-hyperframes: cannot find the skills directory")
    for name, path in skills:
        ctx.register_skill(name, path)
    bootstrap = _bootstrap(root)

    def pre_llm_call(is_first_turn=None, **kwargs):
        return {"context": bootstrap} if is_first_turn else None

    ctx.register_hook("pre_llm_call", pre_llm_call)
