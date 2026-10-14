"""API keys: environment variable first, then the macOS Keychain (service pwdev-media-<provider>).

A key value is never printed or logged. `status` only reports where a key was found.
"""
from __future__ import annotations

import getpass
import os
import platform
import shutil
import subprocess

# provider -> environment variable read by the adapter
ENV = {
    "openrouter": "OPENROUTER_API_KEY",
    "fal": "FAL_KEY",
    "elevenlabs": "ELEVENLABS_API_KEY",
    "replicate": "REPLICATE_API_TOKEN",
    "runway": "RUNWAYML_API_SECRET",
    "magnific": "FREEPIK_API_KEY",
    "kling": "KLING_API_KEY",
    "bfl": "BFL_API_KEY",
    "ideogram": "IDEOGRAM_API_KEY",
    "leonardo": "LEONARDO_API_KEY",
    "higgsfield": "HIGGSFIELD_API_KEY",
}


class MissingKey(RuntimeError):
    pass


def service(provider: str) -> str:
    return f"pwdev-media-{provider}"


def _keychain_available() -> bool:
    return platform.system() == "Darwin" and shutil.which("security") is not None


def _from_keychain(provider: str) -> str | None:
    if not _keychain_available():
        return None
    result = subprocess.run(["security", "find-generic-password", "-s", service(provider), "-w"],
                            capture_output=True, text=True)
    value = result.stdout.strip()
    return value or None


def lookup(provider: str) -> tuple[str | None, str | None]:
    """(value, source) where source is 'env', 'keychain' or None."""
    var = ENV.get(provider)
    if var and os.environ.get(var):
        return os.environ[var], "env"
    value = _from_keychain(provider)
    if value:
        return value, "keychain"
    return None, None


def get(provider: str) -> str:
    value, _ = lookup(provider)
    if not value:
        var = ENV.get(provider, f"<chave de {provider}>")
        raise MissingKey(f"sem chave para {provider}: guarde com `pwdev-media chaves guardar {provider}` "
                         f"ou exporte {var}")
    return value


def store(provider: str, secret: str | None = None) -> str:
    """Save a key in the Keychain (asks for it with hidden input). Returns a pt-BR message."""
    if provider not in ENV:
        raise ValueError(f"provedor desconhecido: {provider} (conhecidos: {', '.join(sorted(ENV))})")
    if not _keychain_available():
        return (f"Sem Keychain neste sistema. Defina a variável {ENV[provider]} no perfil do terminal "
                f"(Windows: setx {ENV[provider]} \"<chave>\") e abra um terminal novo.")
    secret = secret or getpass.getpass(f"Cole a chave de {provider} (não aparece na tela): ").strip()
    if not secret:
        return "Nada guardado: a chave veio vazia."
    user = os.environ.get("USER") or getpass.getuser()
    subprocess.run(["security", "add-generic-password", "-U", "-s", service(provider), "-a", user,
                    "-w", secret], check=True, capture_output=True)
    return (f"Chave de {provider} guardada no Keychain ({service(provider)}). "
            f"O pwdev-media lê de lá sozinho; não precisa exportar {ENV[provider]}.")


def delete(provider: str) -> str:
    if not _keychain_available():
        return f"Sem Keychain neste sistema: remova a variável {ENV.get(provider, provider)} do perfil."
    result = subprocess.run(["security", "delete-generic-password", "-s", service(provider)],
                            capture_output=True, text=True)
    return "Chave removida." if result.returncode == 0 else "Não havia chave guardada para esse provedor."


def report() -> list[dict]:
    return [{"provedor": p, "variavel": ENV[p], "origem": lookup(p)[1]} for p in sorted(ENV)]
