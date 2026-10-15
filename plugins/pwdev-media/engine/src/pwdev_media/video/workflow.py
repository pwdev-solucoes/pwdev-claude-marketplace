"""The edit folder and the steps the CLI exposes.

<edit>/ (next to the raw videos, never inside them; originals are never touched)
  fonte.mp4            only when several raw files were joined
  transcricao.json     pwdev-transcricao/1 (source times)
  frases.json / .md    phrases with takes marked (reading view for the agent)
  edl.json             pwdev-edl/1
  cut.mp4              the cut
  cut_timeline.json    pwdev-corte/1 (segments + words on the cut)
  legendas.json / .srt pwdev-legendas/1
  correcoes.json       optional {"palavra errada": "certa"} for captions
"""
from __future__ import annotations

import json
from pathlib import Path

from . import captions, check, cut, phrases, tools, transcribe


def edit_path(edit: str | Path) -> Path:
    path = Path(edit).expanduser().resolve()
    path.mkdir(parents=True, exist_ok=True)
    return path


def read(path: Path) -> dict:
    if not path.is_file():
        raise FileNotFoundError(f"falta {path.name} em {path.parent} (rode a etapa anterior)")
    return json.loads(path.read_text(encoding="utf-8"))


def join(out: str | Path, files: list[str]) -> dict:
    """Concatenate several raw recordings (same orientation) into one source, re-encoded."""
    out = Path(out).expanduser()
    out.parent.mkdir(parents=True, exist_ok=True)
    info = tools.probe(files[0])
    w, h = info["video"]["largura"], info["video"]["altura"]
    inputs, chains, labels = [], [], []
    for i, f in enumerate(files):
        inputs += ["-i", str(Path(f).expanduser())]
        chains.append(f"[{i}:v]scale={w}:{h}:force_original_aspect_ratio=decrease,pad={w}:{h}:(ow-iw)/2:(oh-ih)/2,"
                      f"fps=30,setsar=1[v{i}]")
        chains.append(f"[{i}:a]aresample=48000,aformat=channel_layouts=stereo[a{i}]")
        labels.append(f"[v{i}][a{i}]")
    graph = ";".join(chains) + ";" + "".join(labels) + f"concat=n={len(files)}:v=1:a=1[v][a]"
    tools.run(["ffmpeg", "-v", "error", "-y", *inputs, "-filter_complex", graph, "-map", "[v]", "-map", "[a]",
               "-c:v", "libx264", "-preset", "veryfast", "-crf", "16", "-pix_fmt", "yuv420p", "-c:a", "aac",
               "-b:a", "192k", str(out)])
    return {"arquivo": str(out), "partes": len(files)}


def do_transcribe(video: str, edit: str, idioma: str, prompt: str, motor: str | None) -> dict:
    e = edit_path(edit)
    doc = transcribe.transcribe(video, e / "transcricao.json", idioma, prompt, motor)
    summary = do_phrases(edit)
    return {"palavras": len(doc["palavras"]), "idioma": doc["idioma"], "motor": doc["motor"], **summary}


def do_phrases(edit: str) -> dict:
    e = edit_path(edit)
    doc = read(e / "transcricao.json")
    found = phrases.mark_takes(phrases.split(doc["palavras"]))
    summary = phrases.write(e, found, doc["fonte"])
    return {**summary, "leitura": str(e / "frases.md")}


def do_assemble(edit: str, ids: list[str] | None) -> dict:
    e = edit_path(edit)
    doc = read(e / "transcricao.json")
    found = json.loads((e / "frases.json").read_text(encoding="utf-8")) if (e / "frases.json").is_file() \
        else phrases.mark_takes(phrases.split(doc["palavras"]))
    chosen = ids or phrases.auto_ids(found)
    edl = phrases.from_phrase_ids(found, chosen, doc["fonte"])
    (e / "edl.json").write_text(json.dumps(edl, ensure_ascii=False, indent=1), encoding="utf-8")
    kept = sum(iv["fim"] - iv["inicio"] for iv in edl["intervalos"])
    return {"frases": len(chosen), "descartadas": len(found) - len(chosen), "fala_aprox_s": round(kept, 2),
            "edl": str(e / "edl.json")}


def do_cut(edit: str, qualidade: str, max_palavras: int) -> dict:
    e = edit_path(edit)
    edl = read(e / "edl.json")
    errors = phrases.validate_edl(edl)
    if errors:
        raise ValueError("EDL inválido: " + "; ".join(errors))
    words = read(e / "transcricao.json")["palavras"] if (e / "transcricao.json").is_file() else []
    result = cut.render(edl, e, words, qualidade)
    legend = do_captions(edit, max_palavras)
    return {**result, "legendas": legend["cues"]}


def do_captions(edit: str, max_palavras: int) -> dict:
    e = edit_path(edit)
    timeline = read(e / "cut_timeline.json")
    words = timeline["palavras"]
    if (e / "correcoes.json").is_file():
        words = captions.apply_corrections(words, read(e / "correcoes.json"))
    doc = captions.build(words, max_palavras)
    (e / "legendas.json").write_text(json.dumps(doc, ensure_ascii=False, indent=1), encoding="utf-8")
    (e / "legendas.srt").write_text(captions.srt(doc), encoding="utf-8")
    return {"cues": len(doc["cues"]), "arquivo": str(e / "legendas.json")}


def do_gate(video: str, edit: str | None, max_silencio: float = check.RESPIRO) -> dict:
    timeline = cues = None
    if edit:
        e = edit_path(edit)
        if (e / "cut_timeline.json").is_file() and (e / "legendas.json").is_file():
            timeline = read(e / "cut_timeline.json")
            cues = read(e / "legendas.json")["cues"]
    return check.gate(video, timeline, cues, max_silencio)


def cut_text(edit: str) -> str:
    """The speech of the cut as plain text, for the agent to proofread names and words."""
    timeline = read(edit_path(edit) / "cut_timeline.json")
    return " ".join(w["w"] for w in timeline["palavras"])
