"""Creative formats and safe zones by platform (data/formatos.json)."""
from __future__ import annotations

import json

from . import paths


def load() -> list[dict]:
    return json.loads((paths.DATA / "formatos.json").read_text(encoding="utf-8"))["formatos"]


def get(format_id: str) -> dict:
    for fmt in load():
        if fmt["id"] == format_id:
            return fmt
    raise KeyError(f"formato '{format_id}' não existe (veja `pwdev-media formatos listar`)")


def by_platform(platform: str | None = None) -> list[dict]:
    return [f for f in load() if platform is None or platform in f["plataformas"]]


def safe_box(fmt: dict) -> tuple[int, int, int, int]:
    """Safe area in pixels as (x, y, width, height)."""
    z = fmt["zona_segura_pct"]
    w, h = fmt["largura"], fmt["altura"]
    x0 = round(w * z["esquerda"] / 100)
    y0 = round(h * z["topo"] / 100)
    x1 = w - round(w * z["direita"] / 100)
    y1 = h - round(h * z["base"] / 100)
    return x0, y0, x1 - x0, y1 - y0


def check_box(fmt: dict, box: tuple[int, int, int, int]) -> list[str]:
    """Problems of a text/element box (x, y, w, h) against the safe zone; empty list = inside."""
    sx, sy, sw, sh = safe_box(fmt)
    x, y, w, h = box
    problems = []
    if x < sx:
        problems.append(f"sai {sx - x}px pela esquerda")
    if y < sy:
        problems.append(f"sai {sy - y}px pelo topo")
    if x + w > sx + sw:
        problems.append(f"sai {x + w - (sx + sw)}px pela direita")
    if y + h > sy + sh:
        problems.append(f"sai {y + h - (sy + sh)}px pela base")
    return problems
