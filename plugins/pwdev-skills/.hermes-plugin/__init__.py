"""Hermes Agent registration adapter for PWDEV Skills."""

from pathlib import Path


EXPECTED_SKILLS = ("skill-refactor",)


def _plugin_root() -> Path:
    """Find the plugin root in git-clone and flattened install layouts."""
    here = Path(__file__).resolve().parent
    for candidate in (here.parent, here):
        skills = candidate / "skills"
        if skills.is_symlink():
            raise RuntimeError("pwdev-skills: unsafe skills tree")
        if skills.is_dir():
            return candidate
    raise RuntimeError("pwdev-skills: skills directory not found")


def _validated_skills(plugin_root: Path):
    """Return the closed, confined inventory before any registration callback."""
    skills_root = plugin_root / "skills"
    if skills_root.is_symlink():
        raise RuntimeError("pwdev-skills: unsafe skills tree")

    entries = sorted((entry for entry in skills_root.iterdir() if entry.name != "__pycache__"),
                     key=lambda path: path.name)
    if tuple(entry.name for entry in entries) != EXPECTED_SKILLS:
        raise RuntimeError("pwdev-skills: invalid skills inventory (expected exactly 1 skill: skill-refactor)")

    canonical_root = skills_root.resolve(strict=True)
    validated = []
    for skill in entries:
        skill_file = skill / "SKILL.md"
        if skill.is_symlink() or not skill.is_dir():
            raise RuntimeError("pwdev-skills: unsafe skills tree")
        if skill_file.is_symlink() or not skill_file.is_file():
            raise RuntimeError("pwdev-skills: unsafe skills tree")
        try:
            canonical_file = skill_file.resolve(strict=True)
            canonical_file.relative_to(canonical_root)
        except (OSError, RuntimeError, ValueError):
            raise RuntimeError("pwdev-skills: unsafe skills tree")
        validated.append((skill.name, canonical_file))
    return validated


def register(ctx) -> None:
    """Register the validated inventory. No hook: the skill loads on demand.

    The SKILL.md is larger than Hermes' inline bootstrap limit, so it is never injected into the
    first turn; Hermes lists it and loads it with skill_view("pwdev-skills:skill-refactor").
    Validation completes before the first callback; a rejected callback propagates immediately.
    """
    skills = _validated_skills(_plugin_root())
    for name, skill_file in skills:
        ctx.register_skill(name, skill_file)
