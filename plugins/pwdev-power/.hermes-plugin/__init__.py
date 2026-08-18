"""PWDEV Power plugin for Hermes Agent.

Registers the Power skills with Hermes' native skill loader and injects the bootstrap on the
first turn of a session. Zero dependencies: Hermes runs this file directly.
"""

import os
import re
from pathlib import Path

BOOTSTRAP_MARKER = "pwdev-power:power bootstrap for hermes"

# Above this, Hermes spills injected context to a file, which breaks inline injection
# semantics. The bootstrap must stay under it with margin.
CONTEXT_SPILL_LIMIT = 10_000


def _plugin_dir() -> str:
    """Locate the directory holding skills/ and references/, for either install layout.

    - git-clone install: the plugin directory is the plugin root, so `.hermes-plugin/`,
      `skills/` and `references/` are siblings, and this module resolves `..`.
    - flattened install: the plugin files were copied to the plugin directory root, so
      `skills/` sits next to this module.

    Raises loudly when neither matches. A bootstrap that silently skips is how a broken
    install masquerades as a working one.
    """
    here = os.path.dirname(os.path.realpath(__file__))
    candidates = (
        os.path.realpath(os.path.join(here, "..")),
        here,
    )
    for candidate in candidates:
        if os.path.isfile(os.path.join(candidate, "skills", "power", "SKILL.md")):
            return candidate
    raise RuntimeError(
        "pwdev-power plugin: cannot find the skills/ tree "
        f"(looked at {candidates}). Reinstall the plugin."
    )


def _strip_frontmatter(content: str) -> str:
    match = re.match(r"^---\n[\s\S]*?\n---\n([\s\S]*)$", content)
    return (match.group(1) if match else content).strip()


def _build_bootstrap(plugin_dir: str) -> str:
    skills_dir = os.path.join(plugin_dir, "skills")

    with open(os.path.join(skills_dir, "power", "SKILL.md"), encoding="utf-8") as handle:
        body = _strip_frontmatter(handle.read())

    tools_path = os.path.join(plugin_dir, "references", "hermes-tools.md")
    with open(tools_path, encoding="utf-8") as handle:
        # Read the mapping at runtime rather than duplicating it here: one source, no drift.
        tool_mapping = handle.read().strip()

    return (
        "<EXTREMELY_IMPORTANT>\n"
        f"{BOOTSTRAP_MARKER}\n\n"
        "This repository uses PWDEV Power.\n\n"
        "The 'power' skill content is included below and is already loaded for this Hermes "
        "session. Follow it now. Do not try to load it again.\n\n"
        f"{body}\n\n"
        "## Loading PWDEV Power skills on Hermes\n\n"
        "Power skills are registered with Hermes' native skill loader: invoke one with "
        '`skill_view("pwdev-power:power-tdd")`, for example. If a namespaced lookup returns '
        "'not found', read the skill file directly instead:\n"
        f'`read_file("{skills_dir}/<skill-name>/SKILL.md")`\n\n'
        f"The Power skills directory is: `{skills_dir}`\n"
        f"The Power references directory is: `{os.path.join(plugin_dir, 'references')}`\n\n"
        f"{tool_mapping}\n"
        "</EXTREMELY_IMPORTANT>"
    )


def register(ctx):
    plugin_dir = _plugin_dir()
    skills_dir = os.path.join(plugin_dir, "skills")
    bootstrap = _build_bootstrap(plugin_dir)

    # Register every skill with Hermes' native loader so skill_view can load them on demand.
    #
    # register_skill requires a pathlib.Path. Passing a str raises AttributeError inside
    # Hermes and silently disables the whole plugin, so the tests assert the type too.
    for name in sorted(os.listdir(skills_dir)):
        skill_md = os.path.join(skills_dir, name, "SKILL.md")
        if os.path.isfile(skill_md):
            ctx.register_skill(name, Path(skill_md))

    # pre_llm_call returning {"context": ...} is the injection path that works: return values
    # from on_session_start are ignored, and ctx.inject_message refuses to be called from that
    # hook. The context is appended to the first turn's user message — never a system message.
    #
    # Hermes has no post-compaction hook, so a long session that compacts over its first turn
    # loses this. That is documented in the README; it cannot be fixed from inside the plugin.
    def pre_llm_call(
        session_id=None,
        user_message=None,
        conversation_history=None,
        is_first_turn=None,
        model=None,
        platform=None,
        **kwargs,
    ):
        if is_first_turn:
            return {"context": bootstrap}
        return None

    ctx.register_hook("pre_llm_call", pre_llm_call)
