"""Hermes adapter for pwdev-fumadocs: registers the fumadocs-* skills and a first-turn bootstrap."""
from pathlib import Path


def _plugin_dir() -> Path:
    here = Path(__file__).resolve().parent
    for candidate in (here.parent, here):
        if (candidate / "skills" / "fumadocs-setup" / "SKILL.md").is_file():
            return candidate
    raise RuntimeError("pwdev-fumadocs: cannot find the skills directory")


def _skills(root: Path) -> list:
    found = []
    for folder in sorted((root / "skills").iterdir()):
        skill = folder / "SKILL.md"
        if folder.name.startswith("fumadocs-") and not folder.is_symlink() and skill.is_file() and not skill.is_symlink():
            found.append((folder.name, skill))
    return found


def _bootstrap(root: Path) -> str:
    return (
        "<EXTREMELY_IMPORTANT>\n"
        "pwdev-fumadocs is available: Fumadocs documentation sites built from the live official "
        "docs. Route by intent with skill_view(\"pwdev-fumadocs:fumadocs-<name>\"): fumadocs-setup "
        "(new site or add Fumadocs to an app), fumadocs-content (MDX pages, meta.json, navigation, "
        "migration), fumadocs-feature (search, llms.txt, MCP, OG, OpenAPI, i18n, static export), "
        "fumadocs-doctor (errors, health, upgrades). Load a skill only when the request needs it; "
        "never write Fumadocs API code from memory, and never install packages or run a generator "
        "without the user's explicit yes. Tools: terminal (python3, npx, the package manager), "
        f"read_file, write_file, and the fumadocs MCP tools when configured. If a namespaced "
        f"skill_view is not found, read {root / 'skills'}/<name>/SKILL.md directly; plugin-relative "
        f"paths in skills resolve against {root}.\n"
        "</EXTREMELY_IMPORTANT>"
    )


def register(ctx):
    root = _plugin_dir()
    skills = _skills(root)
    if not skills:
        raise RuntimeError("pwdev-fumadocs: cannot find the skills directory")
    for name, path in skills:
        ctx.register_skill(name, path)
    bootstrap = _bootstrap(root)

    def pre_llm_call(is_first_turn=None, **kwargs):
        return {"context": bootstrap} if is_first_turn else None

    ctx.register_hook("pre_llm_call", pre_llm_call)
