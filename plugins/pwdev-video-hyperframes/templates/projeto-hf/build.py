#!/usr/bin/env python3
"""pwdev-video-hyperframes · project builder (standard library only).

Reads projeto.json (schema pwdev-projeto-video/1, shared with pwdev-video-remotion) and the cut
artifacts in its edit folder, and writes index.html in the official HyperFrames format. Custom
scenes live in compositions/ and are written with the official HyperFrames skills.

    python3 build.py novo <pasta-do-projeto> --edit <pasta-edit> [--formato reels-9x16] [--nome x]
    python3 build.py montar                 # index.html from projeto.json (respects "amostra")
    python3 build.py amostra <inicio> <fim> # build only that stretch (seconds on the cut)
    python3 build.py completo               # clear the sample and build the whole video
    python3 build.py estudio [--parar|--status]
    python3 build.py hf <args...>           # pinned HyperFrames CLI in this project
    python3 build.py render [--max-silencio s] [--qualidade draft|standard|high]
    python3 build.py gsap                   # baixa a cópia local verificada do GSAP (render offline)

Times come from the measured cut; nothing here estimates a time.
"""
from __future__ import annotations

import html
import json
import math
import os
import shutil
import subprocess
import sys
from pathlib import Path

HYPERFRAMES = "0.8.158"   # pinned: the same project re-renders identically
GSAP = "3.14.2"
GSAP_SRI = "sha384-sG0Hv1tP1lZCk9KQmrIbY/XNwi+OY84GQqhMscbnsoBFqAz8KNCil1kvfL3Hbbk2"  # integrity of the pinned CDN file
HERE = Path(__file__).resolve().parent
GSAP_URL = f"https://cdn.jsdelivr.net/npm/gsap@{GSAP}/dist/gsap.min.js"
GSAP_LOCAL = "assets/vendor/gsap.min.js"
TEMPLATE_FILES = ("build.py", "package.json", "hyperframes.json", "assets/fonts", "compositions/LEIA.md")


# ---------------------------------------------------------------------------- helpers

def die(msg: str, code: int = 2) -> None:
    print(msg, file=sys.stderr)
    sys.exit(code)


def media_cli() -> str:
    found = shutil.which("pwdev-media") or str(Path.home() / ".local" / "bin" / "pwdev-media")
    if not Path(found).exists():
        die("pwdev-media não encontrado: instale o núcleo (pwdev-media, skill media-setup).", 6)
    return found


def media(*args: str) -> dict:
    result = subprocess.run([media_cli(), "--json", *args], capture_output=True, text=True)
    if result.returncode not in (0, 1):
        die(result.stderr.strip() or result.stdout.strip(), result.returncode)
    return json.loads(result.stdout)


def env_with_tools() -> dict:
    pwdev_bin = str(Path.home() / ".pwdev" / "bin")
    # HyperFrames sends anonymous usage telemetry by default; these two variables turn it off.
    return {**os.environ, "PATH": pwdev_bin + os.pathsep + os.environ.get("PATH", ""),
            "HYPERFRAMES_NO_TELEMETRY": "1", "DO_NOT_TRACK": "1"}


def hf(args: list[str], cwd: Path | None = None, check: bool = True) -> int:
    npx = shutil.which("npx") or die("npx não encontrado: instale o Node 22+ (skill vhf-setup).", 6)
    code = subprocess.run([npx, "--yes", f"hyperframes@{HYPERFRAMES}", *args], cwd=cwd or HERE,
                          env=env_with_tools()).returncode
    if check and code != 0:
        sys.exit(code)
    return code


def load_project() -> dict:
    path = HERE / "projeto.json"
    if not path.is_file():
        die("projeto.json não existe: crie o projeto com `build.py novo`.")
    return json.loads(path.read_text(encoding="utf-8"))


def save_project(proj: dict) -> None:
    (HERE / "projeto.json").write_text(json.dumps(proj, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def read_json(path: Path) -> dict:
    if not path.is_file():
        die(f"falta {path} (rode o corte antes: pwdev-media video cortar).")
    return json.loads(path.read_text(encoding="utf-8"))


def copy_if_changed(src: Path, dest: Path) -> str:
    dest.parent.mkdir(parents=True, exist_ok=True)
    if not dest.exists() or dest.stat().st_size != src.stat().st_size or dest.stat().st_mtime < src.stat().st_mtime:
        shutil.copy2(src, dest)
    return dest.relative_to(HERE).as_posix()


def esc(text: str) -> str:
    return html.escape(str(text), quote=True)


def num(x: float) -> str:
    return f"{x:.3f}".rstrip("0").rstrip(".") or "0"


def vendor_gsap(dest: Path) -> bool:
    """Keep a verified copy of the pinned GSAP in the project, so renders work offline."""
    import base64
    import hashlib
    import urllib.request
    target = dest / GSAP_LOCAL
    try:
        with urllib.request.urlopen(GSAP_URL, timeout=30) as resp:
            data = resp.read()
    except OSError:
        return False
    digest = "sha384-" + base64.b64encode(hashlib.sha384(data).digest()).decode()
    if digest != GSAP_SRI:
        die(f"o GSAP baixado não confere com a integridade esperada ({digest}); nada foi gravado.", 5)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(data)
    return True


def gsap_tag() -> str:
    if (HERE / GSAP_LOCAL).is_file():
        return f'<script src="{GSAP_LOCAL}"></script>'
    return f'<script src="{GSAP_URL}" integrity="{GSAP_SRI}" crossorigin="anonymous"></script>'


# ---------------------------------------------------------------------------- composition

class Window:
    """Maps cut times to composition times for a sample [a, b) or the whole cut."""

    def __init__(self, a: float, b: float):
        self.a, self.b = a, b

    @property
    def duration(self) -> float:
        return self.b - self.a

    def clip(self, start: float, end: float):
        s, e = max(start, self.a), min(end, self.b)
        return (s - self.a, e - s) if e - s > 0.02 else None


def safe_box(fmt: dict) -> tuple[int, int, int, int]:
    z, w, h = fmt["zona_segura_pct"], fmt["largura"], fmt["altura"]
    x0, y0 = round(w * z["esquerda"] / 100), round(h * z["topo"] / 100)
    return x0, y0, w - round(w * z["direita"] / 100) - x0, h - round(h * z["base"] / 100) - y0


def css(fmt: dict, style: dict, legenda: dict) -> str:
    w, h = fmt["largura"], fmt["altura"]
    sx, sy, sw, sh = safe_box(fmt)
    unit = min(w, h) / 1080
    cap_size = round({"destaque": 72, "caixa": 46}.get(legenda["estilo"], 54) * unit)
    cap_top = min(max(round(legenda.get("y", 0.7) * h), sy), sy + sh - round(cap_size * 2.6))
    return f"""
      @font-face {{ font-family: "Montserrat"; src: url("assets/fonts/Montserrat.ttf") format("truetype");
                   font-weight: 100 900; }}
      * {{ margin: 0; padding: 0; box-sizing: border-box; }}
      html, body {{ width: {w}px; height: {h}px; overflow: hidden; background: {style['fundo']}; }}
      #root {{ position: relative; width: {w}px; height: {h}px; overflow: hidden;
               font-family: "{style['fonte']}", "Montserrat", sans-serif; }}
      #fala {{ position: absolute; inset: 0; width: 100%; height: 100%; object-fit: cover; }}
      .cue {{ position: absolute; left: {sx}px; width: {sw}px; top: {cap_top}px; text-align: center;
              font-size: {cap_size}px; line-height: 1.15; font-weight: {800 if legenda['estilo'] == 'destaque' else 700};
              color: {style['texto']}; {'text-transform: uppercase;' if legenda['estilo'] == 'destaque' else ''}
              text-shadow: 0 {round(3 * unit)}px {round(10 * unit)}px rgba(0,0,0,.65), 0 0 {round(2 * unit)}px #000; }}
      .cue .w {{ display: inline-block; padding: 0 {round(8 * unit)}px; border-radius: {round(10 * unit)}px; }}
      .cue .faixa {{ {'background: rgba(10,10,10,.82); padding: ' + str(round(10 * unit)) + 'px ' + str(round(18 * unit)) + 'px; border-radius: ' + str(round(12 * unit)) + 'px; box-decoration-break: clone; -webkit-box-decoration-break: clone;' if legenda['estilo'] == 'caixa' else ''} }}
      .texto {{ position: absolute; left: {sx}px; width: {sw}px; text-align: center; color: {style['texto']};
                font-weight: 800; line-height: 1.1; }}
      .texto.rotulo {{ font-size: {round(56 * unit)}px; }}
      .texto.rotulo span {{ background: {style['destaque']}; color: {style['fundo']}; padding: {round(10 * unit)}px {round(22 * unit)}px;
                            border-radius: {round(14 * unit)}px; display: inline-block; }}
      .texto.titulo {{ font-size: {round(96 * unit)}px; text-transform: uppercase;
                       text-shadow: 0 {round(4 * unit)}px {round(18 * unit)}px rgba(0,0,0,.6); }}
      .texto.topo {{ top: {sy + round(0.02 * h)}px; }}
      .texto.centro {{ top: {sy + sh // 2 - round(60 * unit)}px; }}
      .texto.base {{ top: {sy + sh - round(200 * unit)}px; }}
      .cena {{ position: absolute; inset: 0; }}
"""


def build(proj: dict) -> dict:
    edit = Path(proj["edit"])
    timeline = read_json(edit / "cut_timeline.json")
    cues = read_json(edit / "legendas.json")["cues"] if proj["legenda"].get("ativa", True) else []
    validation = media("video", "projeto", str(HERE / "projeto.json"))
    if validation["erros"]:
        die("projeto.json com problemas:\n- " + "\n- ".join(validation["erros"]), 1)
    fmt = media("formatos", "mostrar", proj["formato"])
    w, h = fmt["largura"], fmt["altura"]
    total = timeline["duracao"]
    amostra = proj.get("amostra")
    win = Window(amostra["inicio"], amostra["fim"]) if amostra else Window(0.0, total)
    fix = {k.lower(): v for k, v in (proj.get("correcoes") or {}).items()}
    video_src = copy_if_changed(edit / "cut.mp4", HERE / "assets" / "cut.mp4")

    body, script = [], []
    D = num(win.duration)
    body.append(f'<video id="fala" class="clip" src="{video_src}" data-start="0" data-duration="{D}" '
                f'data-media-start="{num(win.a)}" data-has-audio="true" data-track-index="0" playsinline></video>')

    # camera: base zoom per block, eased in at the block start
    for n, b in enumerate(proj.get("blocos", [])):
        span = win.clip(b["inicio"], b["fim"])
        if not span:
            continue
        start, _ = span
        origin = b.get("origem", "50% 35%")
        script.append(f'tl.set("#fala", {{ transformOrigin: "{origin}" }}, {num(start)});')
        script.append(f'tl.to("#fala", {{ scale: {float(b.get("zoom", 1.0))}, duration: 0.35, ease: "power2.out" }}, {num(start)});')

    # captions: one timed element per cue, each word lights up at its own measured time
    for n, c in enumerate(cues):
        span = win.clip(c["inicio"], c["fim"])
        if not span:
            continue
        start, dur = span
        words = []
        for k, w_ in enumerate(c["palavras"]):
            text = w_["w"]
            bare = text.strip(".,;:?!…").lower()
            if bare in fix:  # fix a word the transcription got wrong, keeping its punctuation
                text = fix[bare] + text[len(text.rstrip(".,;:?!…")):]
            words.append(f'<span class="w" id="c{n}w{k}">{esc(text)}</span>')
        body.append(f'<div id="c{n}" class="clip cue" data-start="{num(start)}" data-duration="{num(dur)}" '
                    f'data-track-index="2"><span class="faixa">{" ".join(words)}</span></div>')
        script.append(f'tl.fromTo("#c{n}", {{ opacity: 0, y: 14 }}, {{ opacity: 1, y: 0, duration: 0.12 }}, {num(start)});')
        if proj["legenda"]["estilo"] == "destaque":
            # the word being said sits on a highlight pill with dark text (readable on any footage)
            st = proj["estilo"]
            for k, w_ in enumerate(c["palavras"]):
                on = max(w_["inicio"] - win.a, start)
                nxt = c["palavras"][k + 1]["inicio"] - win.a if k + 1 < len(c["palavras"]) else start + dur
                off = max(min(nxt, start + dur), on + 0.04)
                script.append(f'tl.set("#c{n}w{k}", {{ backgroundColor: "{st["destaque"]}", color: "{st["fundo"]}" }}, {num(on)});')
                script.append(f'tl.set("#c{n}w{k}", {{ backgroundColor: "rgba(0,0,0,0)", color: "{st["texto"]}" }}, {num(off)});')

    # texts (labels, titles): enter on their word, one idea at a time
    for n, t in enumerate(proj.get("textos", [])):
        span = win.clip(t["inicio"], t["fim"])
        if not span:
            continue
        start, dur = span
        inner = f"<span>{esc(t['texto'])}</span>" if t["tipo"] == "rotulo" else esc(t["texto"])
        body.append(f'<div id="t{n}" class="clip texto {t["tipo"]} {t.get("posicao", "topo")}" '
                    f'data-start="{num(start)}" data-duration="{num(dur)}" data-track-index="3">{inner}</div>')
        script.append(f'tl.fromTo("#t{n}", {{ opacity: 0, y: 30, scale: 0.94 }}, '
                      f'{{ opacity: 1, y: 0, scale: 1, duration: 0.28, ease: "back.out(1.6)" }}, {num(start)});')

    # custom scenes written with the official HyperFrames skills
    for n, c in enumerate(proj.get("cenas", [])):
        span = win.clip(c["inicio"], c["fim"])
        if not span:
            continue
        if not (HERE / c["src"]).is_file():
            die(f"cena {c['src']} não existe em compositions/.", 1)
        start, dur = span
        body.append(f'<div id="cena{n}" class="clip cena" data-composition-id="cena{n}" '
                    f'data-composition-src="{esc(c["src"])}" data-start="{num(start)}" data-duration="{num(dur)}" '
                    f'data-track-index="4"></div>')

    # audio: music bed under the voice and sound effects on their frame
    audio_cfg = proj.get("audio") or {}
    trilha = audio_cfg.get("trilha")
    if trilha:
        src = copy_if_changed(Path(trilha["arquivo"]).expanduser(), HERE / "assets" / "audio" / Path(trilha["arquivo"]).name)
        vol = 10 ** (float(trilha.get("volume_db", -23)) / 20)
        body.append(f'<audio id="trilha" src="{src}" data-start="0" data-duration="{D}" data-volume="{vol:.4f}" '
                    f'data-fade-in="0.5" data-fade-out="1" data-track-index="5"></audio>')
    for n, e in enumerate(audio_cfg.get("efeitos", [])):
        if not (win.a <= e["t"] < win.b):
            continue
        path = Path(e["arquivo"]).expanduser()
        length = media("video", "sondar", str(path))["duracao"]
        src = copy_if_changed(path, HERE / "assets" / "audio" / path.name)
        vol = 10 ** (float(e.get("volume_db", -12)) / 20)
        dur = min(length, win.b - e["t"])
        body.append(f'<audio id="sfx{n}" src="{src}" data-start="{num(e["t"] - win.a)}" data-duration="{num(dur)}" '
                    f'data-volume="{vol:.4f}" data-track-index="6"></audio>')

    page = f"""<!doctype html>
<html lang="pt-BR">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width={w}, height={h}" />
    <!-- gerado por build.py (pwdev-video-hyperframes) a partir de projeto.json: edite o projeto, não este arquivo -->
    {gsap_tag()}
    <style>{css(fmt, proj['estilo'], proj['legenda'])}    </style>
  </head>
  <body>
    <div id="root" data-composition-id="main" data-start="0" data-duration="{D}" data-width="{w}" data-height="{h}">
      {chr(10).join('      ' + line for line in body).lstrip()}
    </div>
    <script>
      window.__timelines = window.__timelines || {{}};
      const tl = gsap.timeline({{ paused: true }});
      {chr(10).join('      ' + line for line in script).lstrip()}
      window.__timelines["main"] = tl;
      tl.seek(0);
    </script>
  </body>
</html>
"""
    (HERE / "index.html").write_text(page, encoding="utf-8")
    return {"index": str(HERE / "index.html"), "duracao": round(win.duration, 3), "amostra": bool(amostra),
            "legendas": sum(1 for line in body if 'class="clip cue"' in line),
            "textos": sum(1 for line in body if "clip texto" in line),
            "cenas": sum(1 for line in body if "clip cena" in line)}


# ---------------------------------------------------------------------------- commands

def cmd_novo(argv: list[str]) -> None:
    import argparse
    p = argparse.ArgumentParser(prog="build.py novo")
    p.add_argument("destino")
    p.add_argument("--edit", required=True)
    p.add_argument("--formato", default="reels-9x16")
    p.add_argument("--nome")
    a = p.parse_args(argv)
    dest = Path(a.destino).expanduser().resolve()
    if (dest / "projeto.json").exists():
        die(f"{dest} já é um projeto: reabra com `python3 {dest / 'build.py'} estudio`.")
    edit = Path(a.edit).expanduser().resolve()
    if dest == edit or edit in dest.parents:
        die("o projeto fica ao lado da pasta edit, não dentro dela.")
    dest.mkdir(parents=True, exist_ok=True)
    for rel in TEMPLATE_FILES:
        src, out = HERE / rel, dest / rel
        out.parent.mkdir(parents=True, exist_ok=True)
        if src.is_dir():
            shutil.copytree(src, out, dirs_exist_ok=True)
        else:
            shutil.copy2(src, out)
    (dest / "renders").mkdir(exist_ok=True)
    offline = "" if vendor_gsap(dest) else " (sem internet: o GSAP vem do CDN até rodar `build.py gsap`)"
    nome = a.nome or dest.name
    (dest / "meta.json").write_text(json.dumps({"id": nome, "name": nome}, indent=2) + "\n", encoding="utf-8")
    result = subprocess.run([media_cli(), "--json", "video", "projeto", str(dest / "projeto.json"), "--novo",
                             "--edit", str(edit), "--formato", a.formato, "--nome", nome], capture_output=True, text=True)
    if result.returncode not in (0, 1):
        die(result.stderr.strip())
    print(f"Projeto criado em {dest}{offline}. Próximo passo: python3 '{dest / 'build.py'}' montar")


def cmd_render(argv: list[str]) -> None:
    quality = "standard"
    if "--qualidade" in argv:
        quality = argv[argv.index("--qualidade") + 1]
    proj = load_project()
    info = build(proj)
    name = proj["nome"] + ("-amostra" if info["amostra"] else "")
    out = HERE / "renders" / f"{name}.mp4"
    hf(["render", "-q", quality, "-f", str(proj.get("fps", 30)), "-o", str(out)])
    args = ["video", "portao", str(out)]
    if "--max-silencio" in argv:  # tutorials: pauses while the screen loads are expected
        args += ["--max-silencio", argv[argv.index("--max-silencio") + 1]]
    if not info["amostra"]:
        args += ["--edit", proj["edit"]]
    gate = media(*args)
    print(json.dumps({"arquivo": str(out), "veredito": gate["veredito"], "problemas": gate["problemas"],
                      "avisos": gate["avisos"]}, ensure_ascii=False, indent=2))
    sys.exit(0 if gate["veredito"] == "PASSOU" else 1)


def main(argv: list[str]) -> None:
    if not argv:
        die(__doc__)
    cmd, rest = argv[0], argv[1:]
    if cmd == "novo":
        cmd_novo(rest)
    elif cmd == "montar":
        print(json.dumps(build(load_project()), ensure_ascii=False, indent=2))
    elif cmd == "amostra":
        if len(rest) != 2:
            die("uso: build.py amostra <inicio> <fim>")
        a, b = float(rest[0]), float(rest[1])
        if not 0 < b - a <= 30:
            die("a amostra tem de 8 a 15 s (máximo 30).")
        proj = load_project()
        proj["amostra"] = {"inicio": a, "fim": b}
        save_project(proj)
        print(json.dumps(build(proj), ensure_ascii=False, indent=2))
    elif cmd == "completo":
        proj = load_project()
        proj["amostra"] = None
        save_project(proj)
        print(json.dumps(build(proj), ensure_ascii=False, indent=2))
    elif cmd == "estudio":
        if "--parar" in rest:
            hf(["preview", "--stop"])
        elif "--status" in rest:
            hf(["preview", "--status"])
        else:
            build(load_project())
            hf(["preview", "--background"])
    elif cmd == "gsap":
        print("GSAP local gravado." if vendor_gsap(HERE) else "Sem internet: tente de novo depois.")
    elif cmd == "hf":
        sys.exit(hf(rest, check=False))
    elif cmd == "render":
        cmd_render(rest)
    else:
        die(__doc__)


if __name__ == "__main__":
    main(sys.argv[1:])
