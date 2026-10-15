"""`projeto.json`: the engine-neutral edit plan read by both video plugins (HyperFrames, Remotion).

Times are in seconds on the cut (cut.mp4). Schema `pwdev-projeto-video/1`:

{
  "schema": "pwdev-projeto-video/1",
  "nome": "criativo-bolsa",
  "edit": "/abs/path/edit",                    # folder with cut.mp4, cut_timeline.json, legendas.json
  "formato": "reels-9x16",                     # id from `pwdev-media formatos`
  "fps": 30,
  "estilo": {"fonte": "Montserrat", "texto": "#FFFFFF", "destaque": "#FF6A00", "fundo": "#0A0A0A"},
  "legenda": {"ativa": true, "estilo": "discreta" | "destaque" | "caixa", "max_palavras": 3, "y": 0.70},
  "blocos": [{"inicio", "fim", "tipo": "tela_cheia", "zoom": 1.0, "origem": "50% 35%"}],
  "textos": [{"inicio", "fim", "texto", "tipo": "rotulo" | "titulo", "posicao": "topo" | "centro" | "base"}],
  "cenas":  [{"inicio", "fim", "src": "compositions/<cena>.html|.tsx", "sobre_a_pessoa": true}],
  "audio":  {"trilha": {"arquivo", "volume_db": -23} | null, "efeitos": [{"t", "arquivo", "volume_db": -12}]},
  "correcoes": {"palavra errada": "certa"},
  "amostra": {"inicio", "fim"} | null           # build only this stretch while reviewing
}
"""
from __future__ import annotations

import json
from pathlib import Path

from .. import formats

SCHEMA = "pwdev-projeto-video/1"
TIPOS_BLOCO = {"tela_cheia"}
TIPOS_TEXTO = {"rotulo", "titulo"}
POSICOES = {"topo", "centro", "base"}
ESTILOS_LEGENDA = {"discreta", "destaque", "caixa"}
SCENE_EXTENSIONS = (".html", ".tsx")


def new(nome: str, edit: str, formato: str = "reels-9x16", fps: int = 30) -> dict:
    formats.get(formato)  # unknown format fails here
    return {"schema": SCHEMA, "nome": nome, "edit": str(Path(edit).expanduser().resolve()), "formato": formato,
            "fps": fps, "estilo": {"fonte": "Montserrat", "texto": "#FFFFFF", "destaque": "#FF6A00", "fundo": "#0A0A0A"},
            "legenda": {"ativa": True, "estilo": "discreta", "max_palavras": 3, "y": 0.70},
            "blocos": [], "textos": [], "cenas": [], "audio": {"trilha": None, "efeitos": []},
            "correcoes": {}, "amostra": None}


def _span(item: dict, where: str, duration: float | None, errors: list[str]) -> None:
    a, b = item.get("inicio"), item.get("fim")
    if not isinstance(a, (int, float)) or not isinstance(b, (int, float)):
        errors.append(f"{where}: inicio e fim numéricos")
        return
    if b <= a:
        errors.append(f"{where}: fim ({b}) antes do início ({a})")
    if a < 0 or (duration is not None and b > duration + 0.05):
        errors.append(f"{where}: fora do corte (0 a {duration:.2f}s)")


def validate(proj: dict, duration: float | None = None) -> list[str]:
    errors = []
    if proj.get("schema") != SCHEMA:
        errors.append(f"schema deve ser {SCHEMA}")
    try:
        formats.get(proj.get("formato", ""))
    except KeyError as exc:
        errors.append(str(exc).strip("'\""))
    if proj.get("legenda", {}).get("estilo") not in ESTILOS_LEGENDA:
        errors.append(f"legenda.estilo deve ser um de {sorted(ESTILOS_LEGENDA)}")
    mp = proj.get("legenda", {}).get("max_palavras")
    if not isinstance(mp, int) or not 1 <= mp <= 6:
        errors.append("legenda.max_palavras de 1 a 6")
    for n, b in enumerate(proj.get("blocos", [])):
        _span(b, f"blocos[{n}]", duration, errors)
        if b.get("tipo") not in TIPOS_BLOCO:
            errors.append(f"blocos[{n}]: tipo deve ser um de {sorted(TIPOS_BLOCO)}")
        if not 1.0 <= float(b.get("zoom", 1.0)) <= 2.0:
            errors.append(f"blocos[{n}]: zoom de 1.0 a 2.0")
    for n, t in enumerate(proj.get("textos", [])):
        _span(t, f"textos[{n}]", duration, errors)
        if not str(t.get("texto", "")).strip():
            errors.append(f"textos[{n}]: texto vazio")
        if t.get("tipo") not in TIPOS_TEXTO:
            errors.append(f"textos[{n}]: tipo deve ser um de {sorted(TIPOS_TEXTO)}")
        if t.get("posicao", "topo") not in POSICOES:
            errors.append(f"textos[{n}]: posicao deve ser uma de {sorted(POSICOES)}")
    for n, c in enumerate(proj.get("cenas", [])):
        _span(c, f"cenas[{n}]", duration, errors)
        src = str(c.get("src", ""))
        if not src.startswith("compositions/") or ".." in src or not src.endswith(SCENE_EXTENSIONS):
            errors.append(f"cenas[{n}]: src fica em compositions/ e termina em .html (HyperFrames) ou .tsx (Remotion)")
    for n, e in enumerate(proj.get("audio", {}).get("efeitos", [])):
        if not isinstance(e.get("t"), (int, float)):
            errors.append(f"audio.efeitos[{n}]: t numérico")
    amostra = proj.get("amostra")
    if amostra:
        _span(amostra, "amostra", duration, errors)
    errors += overlaps(proj)
    return errors


def overlaps(proj: dict) -> list[str]:
    """One idea at a time: two texts, or a text and a scene, may not share the screen."""
    items = [("textos", n, t) for n, t in enumerate(proj.get("textos", []))] + \
            [("cenas", n, c) for n, c in enumerate(proj.get("cenas", []))]
    found = []
    for i, (ka, na, a) in enumerate(items):
        for kb, nb, b in items[i + 1:]:
            if a.get("inicio", 0) < b.get("fim", 0) and b.get("inicio", 0) < a.get("fim", 0):
                found.append(f"{ka}[{na}] e {kb}[{nb}] ao mesmo tempo: uma ideia por vez na tela")
    return found


def load(path: str | Path) -> dict:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def save(proj: dict, path: str | Path) -> None:
    Path(path).write_text(json.dumps(proj, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
