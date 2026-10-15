"""Cut by the waveform: EDL → segments → cut.mp4 + cut_timeline.json.

Rules (measured on the audio, never estimated):
- each interval starts at the real onset of its first word and ends after the real offset of its
  last word, plus a short pad, so a word is never clipped;
- every silence of `SPLIT_AT` seconds or more inside an interval is removed, leaving `PAD` seconds
  on each side, so a joint has about 2 × PAD of quiet and the cut never holds a `RESPIRO`;
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
RESPIRO = 0.25        # the rule: no silence this long in the cut (checked by the gate)
SPLIT_AT = 0.20       # pauses from this length are cut, so measurement slack never reaches RESPIRO
PAD = 0.06            # kept on each side of a removed silence (joint ≈ 0.12 s)
LEAD_SEARCH = 0.35    # Whisper may place a word start up to ~0.3 s early or late
TAIL_SEARCH = 0.45
TAIL_PAD = 0.1        # after the last loud frame of a phrase (keeps soft word endings)
MIN_SEGMENT = 0.08
GATE_MARGIN_DB = 2.0     # simulated cut is judged this much stricter than the gate
MIN_WORD_OVERLAP = 0.05  # seconds of a word that must survive the cut for it to stay in the captions
FADE = 0.008
LIMIT = 0.84            # ≈ -1.5 dBFS sample peak, keeps true peak under -0.1 dBTP after AAC


def _real_start(env: audio.Envelope, t: float, floor: float) -> float:
    """Start of the first word, measured on the wave, never after the transcript's word start.

    Sound earlier than the transcript (Whisper is often late) moves the start back. Sound *later*
    than the transcript usually means a soft first syllable below the silence threshold, so the
    transcript time is kept: a word is never clipped to save a few frames of quiet.
    """
    found = audio.onset(env, max(floor, t - LEAD_SEARCH), t + LEAD_SEARCH)
    start = min(found, t) - PAD if found is not None else t - PAD
    return round(max(start, floor, 0.0), 3)


def _real_end(env: audio.Envelope, t: float, ceiling: float) -> float:
    """End after the last loud frame near the transcript's word end, plus TAIL_PAD.

    Whisper often ends a word late, keeping silence; the wave decides. No loud frame nearby means
    the transcript time is kept.
    """
    thr = env.threshold
    lo = int(max(t - 0.25, 0) / audio.FRAME)
    hi = min(int(min(t + TAIL_SEARCH, ceiling) / audio.FRAME), len(env.db) - 1)
    last = None
    for i in range(lo, hi + 1):
        if env.db[i] >= thr:
            last = i
    end = (last + 1) * audio.FRAME + TAIL_PAD if last is not None else t + TAIL_PAD
    return round(min(end, ceiling, env.duration), 3)


def plan(edl: dict, env: audio.Envelope) -> list[tuple[float, float]]:
    """Source segments to keep, in EDL order.

    When an interval follows the previous one in time, it starts after the previous interval's
    *real* end (the wave may extend a phrase past the transcript's end): overlapping segments
    would repeat audio. Intervals reordered back in time are independent.
    """
    out = []
    intervals = edl["intervalos"]
    real_end = 0.0
    for n, iv in enumerate(intervals):
        chronological = n > 0 and intervals[n - 1]["fim"] <= iv["inicio"]
        prev_end = max(intervals[n - 1]["fim"], real_end) if chronological else 0.0
        nxt = intervals[n + 1]["inicio"] if n + 1 < len(intervals) and intervals[n + 1]["inicio"] >= iv["fim"] \
            else env.duration
        a = max(_real_start(env, iv["inicio"], prev_end), prev_end)
        b = _real_end(env, iv["fim"], nxt)
        cursor = a
        for s0, s1 in audio.silences(env, SPLIT_AT, a, b):
            keep_end = s0 + PAD
            if keep_end - cursor >= MIN_SEGMENT:
                out.append((round(cursor, 3), round(keep_end, 3)))
            cursor = max(s1 - PAD, cursor)
        if b - cursor >= MIN_SEGMENT:
            out.append((round(cursor, 3), round(b, 3)))
        real_end = max(b, a)
    return tighten(out, env)


def tighten(segments: list[tuple[float, float]], env: audio.Envelope, passes: int = 3) -> list[tuple[float, float]]:
    """Check the joints on the would-be cut and squeeze any pause that is still too long.

    The cut is simulated by concatenating the source frames of every segment; pauses of SPLIT_AT
    or more found there (same threshold and click bridging the gate uses) are reduced to 2 × PAD
    by moving segment edges, splitting or dropping segments. The cut is then consistent with the
    gate by construction.
    """
    f = audio.FRAME
    segs = [(round(a / f), round(b / f)) for a, b in segments if b > a]
    for _ in range(passes):
        frames = [(k, i) for k, (a, b) in enumerate(segs) for i in range(a, min(b, len(env.db)))]
        if not frames:
            break
        # A small margin over the gate's threshold: encoding and the limiter shift levels by a dB or
        # two, and noise sitting right at the threshold must not decide whether a pause survives.
        virtual = audio.Envelope(db=[env.db[i] for _, i in frames], floor=env.floor, speech=env.speech,
                                 fixed=env.threshold + GATE_MARGIN_DB)
        pad = round(PAD / f)
        removals = [(round(s0 / f) + pad, round(s1 / f) - pad)
                    for s0, s1 in audio.silences(virtual, SPLIT_AT) if s0 > 0 and s1 < virtual.duration - f]
        if not removals:
            break
        drop = set()
        for r0, r1 in removals:
            drop.update(frames[v] for v in range(max(r0, 0), min(r1, len(frames))))
        new = []
        for k, (a, b) in enumerate(segs):
            run = None
            for i in range(a, b):
                if (k, i) in drop:
                    if run is not None:
                        new.append((run, i))
                        run = None
                elif run is None:
                    run = i
            if run is not None:
                new.append((run, b))
        segs = [(a, b) for a, b in new if (b - a) * f >= MIN_SEGMENT]
    # Segments that are continuous in the source become one: a joint there would add fades in the
    # middle of continuous speech, which muffles it.
    merged: list[tuple[int, int]] = []
    for a, b in segs:
        if merged and a == merged[-1][1]:
            merged[-1] = (merged[-1][0], b)
        else:
            merged.append((a, b))
    return [(round(a * f, 3), round(b * f, 3)) for a, b in merged]


def remap_words(words: list[dict], segments: list[dict]) -> list[dict]:
    """Words that overlap a kept segment, with times on the cut, clamped to the segment.

    Overlap (not the word's middle) decides: transcripts often start a word early, before its
    sound; the part that was kept still is the word and must stay in the captions.
    """
    out = []
    for w in words:
        best, best_overlap = None, 0.0
        for seg in segments:
            overlap = min(w["fim"], seg["src_fim"]) - max(w["inicio"], seg["src_inicio"])
            if overlap > best_overlap:
                best, best_overlap = seg, overlap
        if best is None or best_overlap < min(MIN_WORD_OVERLAP, (w["fim"] - w["inicio"]) * 0.5):
            continue
        shift = best["dst_inicio"] - best["src_inicio"]
        out.append({**w, "inicio": round(max(w["inicio"], best["src_inicio"]) + shift, 3),
                    "fim": round(min(w["fim"], best["src_fim"]) + shift, 3)})
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
                 + ("[v][acat]" if has_video else "[acat]"))
    # True-peak safety: recordings close to 0 dBFS overshoot after AAC encoding.
    parts.append(f"[acat]alimiter=limit={LIMIT}:level=false[a]")
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
