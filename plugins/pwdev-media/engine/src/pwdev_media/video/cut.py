"""Cut by the waveform: EDL → segments → cut.mp4 + cut_timeline.json.

Rules (measured on the audio, never estimated):
- each interval starts at the real onset of its first word and ends after the real offset of its
  last word, plus a short pad, so a word is never clipped;
- every silence of `RESPIRO` seconds or more inside an interval is removed, leaving `PAD` seconds
  on each side, so a joint has about 2 × PAD of quiet;
- audio gets a few milliseconds of fade at each joint to avoid clicks.

Timeline schema `pwdev-corte/1`: {"schema", "fonte", "duracao", "segmentos": [{"src_inicio",
"src_fim", "dst_inicio", "dst_fim"}], "palavras": [{"w", "inicio", "fim", "p"}]} with word times
on the cut.
"""
from __future__ import annotations

import json
from pathlib import Path

from . import audio, tools

TIMELINE_SCHEMA = "pwdev-corte/1"
RESPIRO = 0.25        # a silence this long is a breath/pause and goes away
PAD = 0.06            # kept on each side of a removed silence (joint ≈ 0.12 s)
LEAD_SEARCH = 0.35    # Whisper may place a word start up to ~0.3 s early or late
TAIL_SEARCH = 0.45
TAIL_PAD = 0.08       # after the last loud frame of a phrase (keeps the end of the word)
MIN_SEGMENT = 0.08
FADE = 0.008


def _real_start(env: audio.Envelope, t: float, floor: float) -> float:
    found = audio.onset(env, max(floor, t - LEAD_SEARCH), t + LEAD_SEARCH)
    start = (found if found is not None else t) - PAD
    return round(max(start, floor, 0.0), 3)


def _real_end(env: audio.Envelope, t: float, ceiling: float) -> float:
    thr = env.threshold
    lo = int(max(t - 0.1, 0) / audio.FRAME)
    hi = min(int(min(t + TAIL_SEARCH, ceiling) / audio.FRAME), len(env.db) - 1)
    last = None
    for i in range(lo, hi + 1):
        if env.db[i] >= thr:
            last = i
    end = (last + 1) * audio.FRAME + TAIL_PAD if last is not None else t + TAIL_PAD
    return round(min(max(end, t), ceiling, env.duration), 3)


def plan(edl: dict, env: audio.Envelope) -> list[tuple[float, float]]:
    """Source segments to keep, in order."""
    out = []
    intervals = edl["intervalos"]
    for n, iv in enumerate(intervals):
        prev_end = intervals[n - 1]["fim"] if n and intervals[n - 1]["fim"] <= iv["inicio"] else 0.0
        nxt = intervals[n + 1]["inicio"] if n + 1 < len(intervals) and intervals[n + 1]["inicio"] >= iv["fim"] \
            else env.duration
        a = _real_start(env, iv["inicio"], prev_end)
        b = _real_end(env, iv["fim"], nxt)
        cursor = a
        for s0, s1 in audio.silences(env, RESPIRO, a, b):
            keep_end = s0 + PAD
            if keep_end - cursor >= MIN_SEGMENT:
                out.append((round(cursor, 3), round(keep_end, 3)))
            cursor = s1 - PAD
        if b - cursor >= MIN_SEGMENT:
            out.append((round(cursor, 3), round(b, 3)))
    return out


def remap_words(words: list[dict], segments: list[dict]) -> list[dict]:
    """Words whose middle falls inside a kept segment, with times on the cut."""
    out = []
    for w in words:
        mid = (w["inicio"] + w["fim"]) / 2
        for seg in segments:
            if seg["src_inicio"] <= mid < seg["src_fim"]:
                shift = seg["dst_inicio"] - seg["src_inicio"]
                out.append({**w, "inicio": round(max(w["inicio"], seg["src_inicio"]) + shift, 3),
                            "fim": round(min(w["fim"], seg["src_fim"]) + shift, 3)})
                break
    return out


def filtergraph(segments: list[tuple[float, float]], has_video: bool) -> str:
    parts, labels = [], []
    for i, (a, b) in enumerate(segments):
        d = b - a
        if has_video:
            parts.append(f"[0:v]trim=start={a:.3f}:end={b:.3f},setpts=PTS-STARTPTS[v{i}]")
        parts.append(f"[0:a]atrim=start={a:.3f}:end={b:.3f},asetpts=PTS-STARTPTS,"
                     f"afade=t=in:st=0:d={FADE},afade=t=out:st={max(d - FADE, 0):.3f}:d={FADE}[a{i}]")
        labels.append(f"[v{i}][a{i}]" if has_video else f"[a{i}]")
    parts.append("".join(labels) + f"concat=n={len(segments)}:v={1 if has_video else 0}:a=1"
                 + ("[v][a]" if has_video else "[a]"))
    return ";\n".join(parts)


def render(edl: dict, edit_dir: Path, words: list[dict] | None = None, qualidade: str = "padrao") -> dict:
    src = edl["fonte"]
    info = tools.probe(src)
    env = audio.envelope(src)
    segs = plan(edl, env)
    if not segs:
        raise ValueError("o corte ficou vazio: confira os intervalos do EDL")
    edit_dir.mkdir(parents=True, exist_ok=True)
    graph_file = edit_dir / "corte.filtergraph"
    graph_file.write_text(filtergraph(segs, info["video"] is not None), encoding="utf-8")
    out = edit_dir / "cut.mp4"
    crf = {"rascunho": "28", "padrao": "18", "alta": "14"}[qualidade]
    maps = ["-map", "[v]", "-map", "[a]"] if info["video"] else ["-map", "[a]"]
    vcodec = ["-c:v", "libx264", "-preset", "veryfast", "-crf", crf, "-pix_fmt", "yuv420p"] if info["video"] else []
    tools.run(["ffmpeg", "-v", "error", "-y", "-i", src, "-filter_complex_script", str(graph_file), *maps,
               *vcodec, "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-movflags", "+faststart", str(out)])
    timeline, t = [], 0.0
    for a, b in segs:
        timeline.append({"src_inicio": a, "src_fim": b, "dst_inicio": round(t, 3), "dst_fim": round(t + b - a, 3)})
        t += b - a
    doc = {"schema": TIMELINE_SCHEMA, "fonte": src, "duracao": round(t, 3), "segmentos": timeline,
           "palavras": remap_words(words or [], timeline)}
    (edit_dir / "cut_timeline.json").write_text(json.dumps(doc, ensure_ascii=False, indent=1), encoding="utf-8")
    return {"arquivo": str(out), "duracao": doc["duracao"], "segmentos": len(segs),
            "duracao_original": round(info["duracao"], 3)}
