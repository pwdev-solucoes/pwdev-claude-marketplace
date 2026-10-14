"""Hermes adapter for pwdev-media: registers the media-* skills and a first-turn bootstrap."""
from pathlib import Path


def _plugin_dir() -> Path:
    here = Path(__file__).resolve().parent
    for candidate in (here.parent, here):
        if (candidate / "skills" / "media-setup" / "SKILL.md").is_file():
            return candidate
    raise RuntimeError("pwdev-media: cannot find the skills directory")


def _skills(root: Path) -> list:
    found = []
    for folder in sorted((root / "skills").iterdir()):
        skill = folder / "SKILL.md"
        if folder.name.startswith("media-") and not folder.is_symlink() and skill.is_file() and not skill.is_symlink():
            found.append((folder.name, skill))
    return found


def _bootstrap(root: Path) -> str:
    return (
        "<EXTREMELY_IMPORTANT>\n"
        "pwdev-media is available: catalog of AI media models by category, providers (OpenRouter, "
        "fal, ElevenLabs), API keys, cost guard and creative formats, through the `pwdev-media` CLI. "
        "Route by intent with skill_view(\"pwdev-media:media-<name>\"): media-setup (install, keys, "
        "status), media-catalogo (which model/app for a task), media-atualizar (refresh the catalog), "
        "media-gerar (generate image/video/audio), media-custo (spend and budget), media-formatos "
        "(sizes and safe zones). Load a skill only when the request needs it. Never run a paid "
        "generation without showing the estimate and getting the user's explicit yes in this session, "
        "and never print an API key. Tools: terminal, read_file, write_file. If a namespaced "
        f"skill_view is not found, read {root / 'skills'}/<name>/SKILL.md directly; plugin-relative "
        f"paths in skills resolve against {root}.\n"
        "</EXTREMELY_IMPORTANT>"
    )


def register(ctx):
    root = _plugin_dir()
    skills = _skills(root)
    if not skills:
        raise RuntimeError("pwdev-media: cannot find the skills directory")
    for name, path in skills:
        ctx.register_skill(name, path)
    bootstrap = _bootstrap(root)

    def pre_llm_call(is_first_turn=None, **kwargs):
        return {"context": bootstrap} if is_first_turn else None

    ctx.register_hook("pre_llm_call", pre_llm_call)
