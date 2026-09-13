"""Hermes adapter for the shared GLPI skill."""

from pathlib import Path

BOOTSTRAP_MARKER = "pwdev-glpi-bootstrap"
CONTEXT_SPILL_LIMIT = 4000


def _plugin_dir():
    location = Path(__file__).resolve().parent
    return location.parent if location.name == ".hermes-plugin" else location


def _skill_body(skill_path):
    text = skill_path.read_text(encoding="utf-8")
    if text.startswith("---\n"):
        _, _, text = text.partition("\n---\n")
    return text.strip()


def register(ctx):
    root = _plugin_dir()
    skills = root / "skills"
    skill = skills / "glpi" / "SKILL.md"
    if not skill.is_file():
        raise RuntimeError(f"pwdev-glpi: skills directory not found at {skills}")
    ctx.register_skill("glpi", skill)

    def pre_llm_call(*, is_first_turn=False, **_kwargs):
        if not is_first_turn:
            return None
        context = (
            "<EXTREMELY_IMPORTANT>\n"
            f"{BOOTSTRAP_MARKER}\n"
            "Use the shared GLPI skill for ticket and ITSM operations.\n\n"
            f"{_skill_body(skill)}\n"
            "</EXTREMELY_IMPORTANT>"
        )
        return {"context": context}

    ctx.register_hook("pre_llm_call", pre_llm_call)
