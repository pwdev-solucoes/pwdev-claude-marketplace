"""Engine-neutral render plan: projeto.json + cut artifacts → everything a renderer needs, resolved.

Both video plugins share the same decisions, computed once here:
- the sample window (`amostra`) and every time shifted into it; items outside it are dropped and
  items crossing its edges are clipped;
- caption cues with the spelling corrections applied (punctuation kept);
- the safe zone of the format and the pixel position of captions and texts inside it;
- music and effect volumes converted from dB to linear gain.

Schema `pwdev-plano-render/1`. Times are seconds from the start of the window.
"""
from __future__ import annotations

import json
from pathlib import Path

from .. import formats
from . import project

SCHEMA = "pwdev-plano-render/1"
PUNCT = ".,;:?!…"
CAPTION_SIZE = {"discreta": 54, "destaque": 72}
TEXT_SIZE = {"rotulo": 56, "titulo": 96}


class Window:
    def __init__(self, a: float, b: float):
        self.a, self.b = a, b

    def clip(self, start: float, end: float):
        s, e = max(start, self.a), min(end, self.b)
        return (round(s - self.a, 3), round(e - s, 3)) if e - s > 0.02 else None


def _fix(word: str, fixes: dict[str, str]) -> str:
    bare = word.strip(PUNCT).lower()
    if bare in fixes:
        return fixes[bare] + word[len(word.rstrip(PUNCT)):]
    return word


def layout(fmt: dict, legenda: dict) -> dict:
    """Pixel positions inside the safe zone, scaled to the format (1080 px reference)."""
    w, h = fmt["largura"], fmt["altura"]
    sx, sy, sw, sh = formats.safe_box(fmt)
    unit = min(w, h) / 1080
    cap = round(CAPTION_SIZE[legenda["estilo"]] * unit)
    cap_top = min(max(round(legenda.get("y", 0.7) * h), sy), sy + sh - round(cap * 2.6))
    return {
        "unidade": round(unit, 4),
        "zona_segura": {"x": sx, "y": sy, "largura": sw, "altura": sh},
        "legenda": {"topo": cap_top, "esquerda": sx, "largura": sw, "tamanho": cap},
        "texto_topo": {"topo": sy + round(0.02 * h), "centro": sy + sh // 2 - round(60 * unit),
                       "base": sy + sh - round(200 * unit)},
        "texto_tamanho": {k: round(v * unit) for k, v in TEXT_SIZE.items()},
    }


def build(proj: dict, timeline: dict, cues: list[dict]) -> dict:
    total = timeline["duracao"]
    errors = project.validate(proj, total)
    if errors:
        raise ValueError("projeto.json com problemas: " + "; ".join(errors))
    fmt = formats.get(proj["formato"])
    amostra = proj.get("amostra")
    win = Window(amostra["inicio"], amostra["fim"]) if amostra else Window(0.0, total)
    fixes = {k.lower(): v for k, v in (proj.get("correcoes") or {}).items()}
    pos = layout(fmt, proj["legenda"])
    edit = Path(proj["edit"])

    out_cues = []
    if proj["legenda"].get("ativa", True):
        for c in cues:
            span = win.clip(c["inicio"], c["fim"])
            if not span:
                continue
            start, dur = span
            words = [{"texto": _fix(w["w"], fixes), "inicio": round(max(w["inicio"] - win.a, start), 3)}
                     for w in c["palavras"]]
            out_cues.append({"inicio": start, "duracao": dur, "palavras": words})

    def spans(items, extra):
        out = []
        for item in items:
            span = win.clip(item["inicio"], item["fim"])
            if span:
                out.append({"inicio": span[0], "duracao": span[1], **extra(item)})
        return out

    textos = spans(proj.get("textos", []), lambda t: {
        "texto": t["texto"], "tipo": t["tipo"], "posicao": t.get("posicao", "topo"),
        "topo": pos["texto_topo"][t.get("posicao", "topo")], "tamanho": pos["texto_tamanho"][t["tipo"]]})
    blocos = spans(proj.get("blocos", []), lambda b: {
        "zoom": float(b.get("zoom", 1.0)), "origem": b.get("origem", "50% 35%")})
    cenas = spans(proj.get("cenas", []), lambda c: {
        "src": c["src"], "sobre_a_pessoa": bool(c.get("sobre_a_pessoa", False))})

    audio_cfg = proj.get("audio") or {}
    trilha = audio_cfg.get("trilha")
    efeitos = [{"inicio": round(e["t"] - win.a, 3), "arquivo": str(Path(e["arquivo"]).expanduser()),
                "volume": round(10 ** (float(e.get("volume_db", -12)) / 20), 4)}
               for e in audio_cfg.get("efeitos", []) if win.a <= e["t"] < win.b]

    return {
        "schema": SCHEMA, "nome": proj["nome"], "formato": proj["formato"],
        "largura": fmt["largura"], "altura": fmt["altura"], "fps": int(proj.get("fps", 30)),
        "duracao": round(win.b - win.a, 3), "amostra": bool(amostra),
        "janela": {"inicio": win.a, "fim": win.b},
        "video": {"arquivo": str(edit / "cut.mp4"), "inicio_midia": win.a},
        "estilo": proj["estilo"], "legenda": {"estilo": proj["legenda"]["estilo"], **pos["legenda"]},
        "zona_segura": pos["zona_segura"], "unidade": pos["unidade"],
        "cues": out_cues, "textos": textos, "blocos": blocos, "cenas": cenas,
        "audio": {"trilha": {"arquivo": str(Path(trilha["arquivo"]).expanduser()),
                             "volume": round(10 ** (float(trilha.get("volume_db", -23)) / 20), 4)} if trilha else None,
                  "efeitos": efeitos},
    }


def from_files(project_file: str | Path) -> dict:
    proj = project.load(project_file)
    edit = Path(proj["edit"])
    for name in ("cut_timeline.json", "legendas.json"):
        if not (edit / name).is_file():
            raise FileNotFoundError(f"falta {name} em {edit} (rode `pwdev-media video cortar`)")
    timeline = json.loads((edit / "cut_timeline.json").read_text(encoding="utf-8"))
    cues = json.loads((edit / "legendas.json").read_text(encoding="utf-8"))["cues"]
    return build(proj, timeline, cues)
