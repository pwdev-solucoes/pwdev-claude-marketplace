"""Checks on a rendered video and the quality gate.

The gate prints PASSOU only when every blocking rule holds:
- no silence of RESPIRO seconds or more in the middle of the video (head and tail have a small
  allowance);
- no clipping (true peak below -0.1 dBTP);
- when a cut timeline is given: every spoken word is covered by a caption cue.
Loudness out of the social range (-20 to -10 LUFS) is a warning, not a block.
"""
from __future__ import annotations

import re
from pathlib import Path

from . import audio, tools

RESPIRO = 0.25
HEAD_ALLOWANCE = 0.3
TAIL_ALLOWANCE = 0.5
MAX_TRUE_PEAK = -0.1
LUFS_RANGE = (-20.0, -10.0)


def loudness(path: str | Path) -> dict:
    out = tools.run(["ffmpeg", "-hide_banner", "-nostats", "-i", str(path), "-vn", "-af", "ebur128=peak=true",
                     "-f", "null", "-"]).stderr.decode("utf-8", "replace")
    summary = out[out.rfind("Summary:"):] if "Summary:" in out else out
    lufs = re.search(r"I:\s*([-+]?[\d.]+|-inf)\s*LUFS", summary)
    peak = re.search(r"Peak:\s*([-+]?[\d.]+|-inf)\s*dBFS", summary)
    to_float = lambda m: float("-inf") if not m or m.group(1) == "-inf" else float(m.group(1))
    return {"lufs": to_float(lufs), "pico_dbtp": to_float(peak)}


def breaths(env: audio.Envelope) -> list[tuple[float, float]]:
    inner = []
    for a, b in audio.silences(env, RESPIRO):
        if a <= HEAD_ALLOWANCE and (b - a) <= HEAD_ALLOWANCE + 0.05:
            continue
        if b >= env.duration - 0.02 and (b - a) <= TAIL_ALLOWANCE:
            continue
        inner.append((a, b))
    return inner


def caption_gaps(timeline: dict, cues: list[dict]) -> list[str]:
    covered = []
    for w in timeline.get("palavras", []):
        mid = (w["inicio"] + w["fim"]) / 2
        if not any(c["inicio"] <= mid <= c["fim"] for c in cues):
            covered.append(f"{w['w']} ({w['inicio']:.2f}s)")
    return covered


def gate(path: str | Path, timeline: dict | None = None, cues: list[dict] | None = None) -> dict:
    info = tools.probe(path)
    env = audio.envelope(path)
    found = breaths(env)
    loud = loudness(path)
    problems, warnings = [], []
    if info["duracao"] <= 0:
        problems.append("vídeo vazio")
    if found:
        listed = ", ".join(f"{a:.2f}–{b:.2f}s" for a, b in found[:8])
        problems.append(f"{len(found)} respiro(s) de {RESPIRO}s ou mais: {listed}")
    if loud["pico_dbtp"] > MAX_TRUE_PEAK:
        problems.append(f"áudio estourando (pico {loud['pico_dbtp']:.1f} dBTP)")
    if loud["lufs"] != float("-inf") and not (LUFS_RANGE[0] <= loud["lufs"] <= LUFS_RANGE[1]):
        warnings.append(f"volume médio {loud['lufs']:.1f} LUFS (redes sociais: {LUFS_RANGE[0]:.0f} a {LUFS_RANGE[1]:.0f})")
    if timeline is not None and cues is not None:
        gaps = caption_gaps(timeline, cues)
        if gaps:
            problems.append(f"{len(gaps)} palavra(s) fora da legenda: {', '.join(gaps[:6])}")
    return {"veredito": "PASSOU" if not problems else "REPROVOU", "problemas": problems, "avisos": warnings,
            "duracao": round(info["duracao"], 3), "respiros": found, **loud}
