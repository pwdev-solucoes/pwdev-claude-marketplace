"""Hermes Agent registration adapter for PWDEV QA."""

from pathlib import Path


EXPECTED_SKILLS = tuple(sorted((
    "qa",
    "qa-tooling",
    "qa-init",
    "qa-strategy",
    "qa-test",
    "qa-explore",
    "qa-bug",
    "qa-regression",
    "qa-review",
    "qa-release",
    "qa-report",
    "qa-status",
    "qa-specialist-accessibility",
    "qa-specialist-api",
    "qa-specialist-automation",
    "qa-specialist-cicd",
    "qa-specialist-data",
    "qa-specialist-defects",
    "qa-specialist-functional",
    "qa-specialist-metrics",
    "qa-specialist-mobile",
    "qa-specialist-performance",
    "qa-specialist-production",
    "qa-specialist-readiness",
    "qa-specialist-regression",
    "qa-specialist-requirements",
    "qa-specialist-security",
    "qa-specialist-strategy",
    "qa-specialist-web",
)))


def _plugin_root() -> Path:
    """Find the plugin root in git-clone and flattened install layouts."""
    here = Path(__file__).resolve().parent
    for candidate in (here.parent, here):
        skills = candidate / "skills"
        if skills.is_symlink():
            raise RuntimeError("pwdev-qa: unsafe skills tree")
        if skills.is_dir():
            return candidate
    raise RuntimeError("pwdev-qa: skills directory not found")


def _validated_skills(plugin_root: Path):
    """Return the closed, confined inventory before any registration callback."""
    skills_root = plugin_root / "skills"
    if skills_root.is_symlink():
        raise RuntimeError("pwdev-qa: unsafe skills tree")

    entries = sorted(skills_root.iterdir(), key=lambda path: path.name)
    if tuple(entry.name for entry in entries) != EXPECTED_SKILLS:
        raise RuntimeError("pwdev-qa: invalid skills inventory (expected exactly 29 skills)")

    canonical_root = skills_root.resolve(strict=True)
    validated = []
    for skill in entries:
        skill_file = skill / "SKILL.md"
        if skill.is_symlink() or not skill.is_dir():
            raise RuntimeError("pwdev-qa: unsafe skills tree")
        if skill_file.is_symlink() or not skill_file.is_file():
            raise RuntimeError("pwdev-qa: unsafe skills tree")
        try:
            canonical_file = skill_file.resolve(strict=True)
            canonical_file.relative_to(canonical_root)
        except (OSError, RuntimeError, ValueError):
            raise RuntimeError("pwdev-qa: unsafe skills tree")
        validated.append((skill.name, canonical_file))
    return validated


def register(ctx) -> None:
    """Register the validated inventory without hooks or a false rollback guarantee.

    Validation is complete before the first callback. If Hermes rejects a callback, its exception
    propagates immediately and no later callback runs; the context API provides no transaction with
    which this adapter could roll back callbacks that already succeeded.
    """
    skills = _validated_skills(_plugin_root())
    for name, skill_file in skills:
        ctx.register_skill(name, skill_file)
