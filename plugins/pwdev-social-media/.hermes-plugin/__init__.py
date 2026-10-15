"""Hermes adapter for pwdev-social-media: registers the social-* skills and a first-turn bootstrap."""
from pathlib import Path


def _plugin_dir() -> Path:
    here = Path(__file__).resolve().parent
    for candidate in (here.parent, here):
        if (candidate / "skills" / "social-criar" / "SKILL.md").is_file():
            return candidate
    raise RuntimeError("pwdev-social-media: cannot find the skills directory")


def _skills(root: Path) -> list:
    found = []
    for folder in sorted((root / "skills").iterdir()):
        skill = folder / "SKILL.md"
        if folder.name.startswith("social-") and not folder.is_symlink() and skill.is_file() and not skill.is_symlink():
            found.append((folder.name, skill))
    return found


def _bootstrap(root: Path) -> str:
    return (
        "<EXTREMELY_IMPORTANT>\n"
        "pwdev-social-media is available: AI creatives for social media on top of the `pwdev-media` CLI. "
        "Route by intent with skill_view(\"pwdev-social-media:social-<name>\"): social-criar (end to end; "
        "start here), social-imagem (generate an image), social-video (AI video), social-carrossel, social-post, "
        "social-reels (9:16), social-formatos (sizes, safe zones, every format), social-lote (test batches), "
        "social-revisao (quality gate), social-entrega (handoff), social-contexto (setup and status); "
        "supporting skills: social-conceito, social-prompt, social-consistencia, social-custo, social-curadoria, "
        "social-upscale, social-alt-text, social-figma, social-marca, social-vault, social-video-curto. "
        "Never generate without `pwdev-media gerar ... --estimar` and the user's explicit yes, never print an API "
        "key, never invent data in a piece, never publish. Subagents are Claude-only: run their steps inline. "
        f"If a namespaced skill_view is not found, read {root / 'skills'}/<name>/SKILL.md directly; "
        f"plugin-relative paths in skills resolve against {root}.\n"
        "</EXTREMELY_IMPORTANT>"
    )


def register(ctx):
    root = _plugin_dir()
    skills = _skills(root)
    if not skills:
        raise RuntimeError("pwdev-social-media: cannot find the skills directory")
    for name, path in skills:
        ctx.register_skill(name, path)
    bootstrap = _bootstrap(root)

    def pre_llm_call(is_first_turn=None, **kwargs):
        return {"context": bootstrap} if is_first_turn else None

    ctx.register_hook("pre_llm_call", pre_llm_call)
