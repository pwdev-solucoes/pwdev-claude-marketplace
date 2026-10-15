"""Provider adapters. Each one implements the operations it supports and a cheap live check."""
from __future__ import annotations

from .base import Provider, Result, Unsupported
from .bfl import BFL
from .elevenlabs import ElevenLabs
from .fal import Fal
from .ideogram import Ideogram
from .leonardo import Leonardo
from .magnific import Magnific
from .openrouter import OpenRouter
from .runway import Runway

REGISTRY: dict[str, type[Provider]] = {
    "openrouter": OpenRouter,
    "fal": Fal,
    "elevenlabs": ElevenLabs,
    "bfl": BFL,
    "ideogram": Ideogram,
    "leonardo": Leonardo,
    "runway": Runway,
    "magnific": Magnific,
}


def get(name: str) -> Provider:
    cls = REGISTRY.get(name)
    if cls is None:
        raise Unsupported(f"o provedor '{name}' ainda não tem adaptador no pwdev-media "
                          f"(disponíveis: {', '.join(sorted(REGISTRY))}). Use o app do provedor ou "
                          "um item equivalente via agregador.")
    return cls()


__all__ = ["Provider", "Result", "Unsupported", "REGISTRY", "get"]
