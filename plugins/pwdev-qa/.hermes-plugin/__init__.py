"""Hermes Agent registration adapter for PWDEV QA."""

from pathlib import Path


def _plugin_root() -> Path:
    """Find the plugin root in git-clone and flattened install layouts."""
    here = Path(__file__).resolve().parent
    for candidate in (here.parent, here):
        skills = candidate / "skills"
        if skills.is_dir():
            return candidate
    raise RuntimeError("pwdev-qa: skills directory not found")


def register(ctx) -> None:
    """Register installed skills for on-demand loading without conversation hooks."""
    skills_root = _plugin_root() / "skills"
    skills = [path for path in skills_root.iterdir() if (path / "SKILL.md").is_file()]
    for skill in sorted(skills, key=lambda path: path.name):
        ctx.register_skill(skill.name, skill / "SKILL.md")
