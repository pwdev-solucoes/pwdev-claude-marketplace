"""Waveform analysis: RMS envelope (10 ms frames), speech/silence regions and quiet points.

The audio is decoded by ffmpeg to 16 kHz mono 16-bit PCM and analysed with the standard library.
Thresholds are relative to the recording's own noise floor, so a noisy room and a quiet studio
both work.
"""
from __future__ import annotations

import array
import math
import sys
from dataclasses import dataclass
from pathlib import Path

from . import tools

RATE = 16000
FRAME = 0.01  # seconds per RMS frame
SAMPLES = int(RATE * FRAME)
FLOOR_DB = -90.0
SILENCE_DB = -60.0


@dataclass
class Envelope:
    db: list[float]          # RMS per 10 ms frame, dBFS
    floor: float             # noise floor (10th percentile)
    speech: float            # typical speech level (90th percentile)

    @property
    def threshold(self) -> float:
        """Silence below this level.

        30% of the way from the noise floor to speech (at least floor + 6 dB), but never closer than
        10 dB to speech, so a recording without pauses is not mistaken for silence; and anything
        under -60 dBFS is always silence, so a mute recording is not mistaken for speech.
        """
        relative = max(self.floor + 6.0, self.floor + 0.3 * (self.speech - self.floor))
        return max(min(relative, self.speech - 10.0), SILENCE_DB)

    @property
    def duration(self) -> float:
        return len(self.db) * FRAME

    def at(self, t: float) -> float:
        i = min(max(int(t / FRAME), 0), len(self.db) - 1)
        return self.db[i]


def decode(path: str | Path) -> array.array:
    out = tools.run(["ffmpeg", "-v", "error", "-i", str(path), "-vn", "-ac", "1", "-ar", str(RATE),
                     "-f", "s16le", "-"]).stdout
    samples = array.array("h")
    samples.frombytes(out[: len(out) - len(out) % 2])
    if sys.byteorder == "big":
        samples.byteswap()
    return samples


def envelope_from_samples(samples: array.array) -> Envelope:
    db = []
    for start in range(0, len(samples) - SAMPLES + 1, SAMPLES):
        chunk = samples[start:start + SAMPLES]
        power = sum(s * s for s in chunk) / SAMPLES
        db.append(10 * math.log10(power / (32768.0 ** 2)) if power > 0 else FLOOR_DB)
    if not db:
        return Envelope([], FLOOR_DB, FLOOR_DB)
    ordered = sorted(db)
    floor = ordered[int(0.10 * (len(ordered) - 1))]
    speech = ordered[int(0.90 * (len(ordered) - 1))]
    return Envelope(db, floor, speech)


def envelope(path: str | Path) -> Envelope:
    return envelope_from_samples(decode(path))


def silences(env: Envelope, min_len: float = 0.25, start: float = 0.0, end: float | None = None) -> list[tuple[float, float]]:
    """Silent stretches of at least `min_len` seconds inside [start, end]."""
    end = env.duration if end is None else end
    lo, hi = int(start / FRAME), min(int(round(end / FRAME)), len(env.db))
    found, run_start = [], None
    thr = env.threshold
    for i in range(lo, hi):
        quiet = env.db[i] < thr
        if quiet and run_start is None:
            run_start = i
        elif not quiet and run_start is not None:
            if (i - run_start) * FRAME >= min_len:
                found.append((round(run_start * FRAME, 3), round(i * FRAME, 3)))
            run_start = None
    if run_start is not None and (hi - run_start) * FRAME >= min_len:
        found.append((round(run_start * FRAME, 3), round(hi * FRAME, 3)))
    return found


def speech_regions(env: Envelope, min_silence: float = 0.25, min_speech: float = 0.08) -> list[tuple[float, float]]:
    regions, cursor = [], 0.0
    for s0, s1 in silences(env, min_silence):
        if s0 - cursor >= min_speech:
            regions.append((round(cursor, 3), s0))
        cursor = s1
    if env.duration - cursor >= min_speech:
        regions.append((round(cursor, 3), round(env.duration, 3)))
    return regions


def quietest(env: Envelope, a: float, b: float) -> float:
    """Time of the quietest frame in [a, b] (ties: the one closest to the middle)."""
    lo, hi = max(int(a / FRAME), 0), min(int(b / FRAME), len(env.db) - 1)
    if hi <= lo:
        return round(a, 3)
    mid = (lo + hi) / 2
    best = min(range(lo, hi + 1), key=lambda i: (env.db[i], abs(i - mid)))
    return round(best * FRAME, 3)


def onset(env: Envelope, a: float, b: float) -> float | None:
    """First frame in [a, b] that rises above the silence threshold (a word really starting)."""
    thr = env.threshold
    for i in range(max(int(a / FRAME), 0), min(int(b / FRAME), len(env.db))):
        if env.db[i] >= thr:
            return round(i * FRAME, 3)
    return None
