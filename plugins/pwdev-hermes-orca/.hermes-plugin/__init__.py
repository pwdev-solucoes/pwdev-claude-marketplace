"""Hermes adapter for pwdev-hermes-orca: registers the coordinator skill and, inside an Orca
terminal only, injects a short first-turn bootstrap. Zero dependencies: Hermes runs this file
directly."""
import os
from pathlib import Path

BOOTSTRAP_MARKER = "pwdev-hermes-orca bootstrap"

# Above this, Hermes spills injected context to a file, which breaks inline injection.
CONTEXT_SPILL_LIMIT = 10_000

# Orca exports this in every terminal it manages; outside Orca the coordinator has no Run to bind.
ORCA_TERMINAL_ENV = "ORCA_TERMINAL_HANDLE"


def _plugin_dir() -> Path:
    """Plugin root for the git-clone layout (`.hermes-plugin/` beside `skills/`) or a flat copy."""
    here = Path(__file__).resolve().parent
    for candidate in (here.parent, here):
        if (candidate / "skills" / "hermes-orca" / "SKILL.md").is_file():
            return candidate
    raise RuntimeError("pwdev-hermes-orca: cannot find the skills directory")


def _skills(root: Path) -> list:
    found = []
    for folder in sorted((root / "skills").iterdir()):
        skill = folder / "SKILL.md"
        if skill.is_file():
            found.append((folder.name, skill))
    return found


def _bootstrap(root: Path) -> str:
    return (
        "<EXTREMELY_IMPORTANT>\n"
        f"{BOOTSTRAP_MARKER}\n"
        "Esta sessão Hermes roda num terminal do Orca e pode coordenar workers supervisionados do "
        "Orca a partir de issues do GitHub. Quando o usuário pedir para orquestrar, despachar ou "
        "resolver issues com workers do Orca, carregue a skill com "
        'skill_view("pwdev-hermes-orca:hermes-orca") e siga-a exatamente. Não crie Run, Task ou '
        "worker só porque este bootstrap carregou. Nunca substitua um worker do Orca por "
        "delegate_task. Se o skill_view namespaced não for encontrado, leia "
        f"{root / 'skills' / 'hermes-orca' / 'SKILL.md'} diretamente; caminhos references/, "
        f"scripts/ e templates/ da skill são relativos a {root}.\n"
        "</EXTREMELY_IMPORTANT>"
    )


def register(ctx):
    root = _plugin_dir()
    skills = _skills(root)
    if not skills:
        raise RuntimeError("pwdev-hermes-orca: cannot find the skills directory")
    # register_skill needs a pathlib.Path: a str raises inside Hermes and disables the plugin.
    for name, path in skills:
        ctx.register_skill(name, Path(path))
    bootstrap = _bootstrap(root)

    def pre_llm_call(is_first_turn=None, **kwargs):
        if is_first_turn and os.environ.get(ORCA_TERMINAL_ENV):
            return {"context": bootstrap}
        return None

    ctx.register_hook("pre_llm_call", pre_llm_call)
