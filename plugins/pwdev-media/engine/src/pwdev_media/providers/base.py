"""Common provider interface."""
from __future__ import annotations

import re
import time
from dataclasses import dataclass, field
from pathlib import Path

from .. import keys


class Unsupported(RuntimeError):
    pass


@dataclass
class Result:
    arquivos: list[str]
    custo_real_usd: float | None = None
    extra: dict = field(default_factory=dict)


class Provider:
    name = ""
    operations: tuple[str, ...] = ()
    poll_seconds = 5.0
    poll_timeout = 900.0

    def key(self) -> str:
        return keys.get(self.name)

    def generate(self, item: dict, params: dict, out_dir: Path) -> Result:
        op = item.get("operacao")
        if op not in self.operations:
            raise Unsupported(f"{self.name} não faz '{op}' pelo pwdev-media (faz: {', '.join(self.operations)})")
        if not item.get("modelo"):
            raise Unsupported(f"o item {item['id']} não tem o slug do modelo (campo `modelo`). "
                              "Rode `pwdev-media catalogo atualizar` ou escolha outro item.")
        out_dir.mkdir(parents=True, exist_ok=True)
        return getattr(self, f"op_{op.replace('-', '_')}")(item, params, out_dir)

    def ping(self) -> str:
        """Cheap live check. Returns a pt-BR line; raises on failure."""
        raise NotImplementedError

    def wait(self, check, describe: str):
        """Call `check()` until it returns a non-None value, with a timeout."""
        deadline = time.monotonic() + self.poll_timeout
        while True:
            value = check()
            if value is not None:
                return value
            if time.monotonic() > deadline:
                raise TimeoutError(f"{describe}: passou de {self.poll_timeout:.0f} s sem terminar")
            time.sleep(self.poll_seconds)


def safe_name(text: str, fallback: str) -> str:
    """Names may come from a provider response: keep [a-z0-9_-] only, so a path can never escape."""
    cleaned = re.sub(r"[^a-z0-9_-]+", "-", str(text).lower()).strip("-_")[:40]
    return cleaned or fallback


def write_bytes(out_dir: Path, stem: str, ext: str, data: bytes) -> str:
    stem, ext = safe_name(stem, "saida"), safe_name(ext, "bin")
    path = out_dir / f"{stem}.{ext}"
    n = 1
    while path.exists():
        n += 1
        path = out_dir / f"{stem}-{n}.{ext}"
    path.write_bytes(data)
    return str(path)
