"""Caption cues from the words of the cut: at most N words per cue, every spoken word shown.

A cue breaks at final/comma punctuation, at a pause of PAUSA seconds, or at N words. Each cue
lasts until the next one starts (short gaps are bridged) so the caption does not flicker.
Schema `pwdev-legendas/1`: {"schema", "max_palavras", "cues": [{"inicio", "fim", "texto",
"palavras": [{"w", "inicio", "fim"}]}]}
"""
from __future__ import annotations

SCHEMA = "pwdev-legendas/1"
PAUSA = 0.3
BRIDGE = 0.4
MIN_CUE = 0.25


def build(words: list[dict], max_palavras: int = 3) -> dict:
    groups, current = [], []
    for i, w in enumerate(words):
        current.append(w)
        nxt = words[i + 1] if i + 1 < len(words) else None
        punct = w["w"].rstrip()[-1:] in ".,;:?!…"
        if nxt is None or len(current) >= max_palavras or punct or nxt["inicio"] - w["fim"] >= PAUSA:
            groups.append(current)
            current = []
    cues = []
    for n, g in enumerate(groups):
        start, end = g[0]["inicio"], g[-1]["fim"]
        nxt = groups[n + 1][0]["inicio"] if n + 1 < len(groups) else None
        if nxt is not None and nxt - end <= BRIDGE:
            end = nxt
        end = max(end, start + MIN_CUE) if nxt is None else min(max(end, start + MIN_CUE), nxt)
        cues.append({"inicio": round(start, 3), "fim": round(end, 3),
                     "texto": " ".join(w["w"] for w in g).strip(),
                     "palavras": [{"w": w["w"], "inicio": w["inicio"], "fim": w["fim"]} for w in g]})
    return {"schema": SCHEMA, "max_palavras": max_palavras, "cues": cues}


def srt(doc: dict) -> str:
    def ts(t: float) -> str:
        ms = int(round(t * 1000))
        return f"{ms // 3600000:02d}:{ms // 60000 % 60:02d}:{ms // 1000 % 60:02d},{ms % 1000:03d}"
    return "\n".join(f"{n}\n{ts(c['inicio'])} --> {ts(c['fim'])}\n{c['texto']}\n"
                     for n, c in enumerate(doc["cues"], 1))


def apply_corrections(words: list[dict], correcoes: dict[str, str]) -> list[dict]:
    """Fix words the transcription got wrong (brand names...). Keys are matched case-insensitively."""
    lowered = {k.lower(): v for k, v in correcoes.items()}
    out = []
    for w in words:
        bare = w["w"].strip(".,;:?!…").lower()
        if bare in lowered:
            tail = w["w"][len(w["w"].rstrip(".,;:?!…")):]
            w = {**w, "w": lowered[bare] + tail}
        out.append(w)
    return out
