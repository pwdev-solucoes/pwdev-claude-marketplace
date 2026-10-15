"""Phrases, takes and the edit decision list (EDL).

A phrase is a run of words ended by a long pause or by final punctuation. People recording to
camera repeat a sentence until it comes out right: when a phrase is followed (within a few
phrases) by another that says the same thing, the earlier one is an abandoned take. The default
rule is "the last complete take wins".

EDL schema `pwdev-edl/1`: {"schema", "fonte", "intervalos": [{"inicio", "fim", "frases": [ids]}]}
in source-video seconds. The agent may write it by hand; `from_phrase_ids` builds it from ids.
"""
from __future__ import annotations

import difflib
import json
import re
import unicodedata
from pathlib import Path

EDL_SCHEMA = "pwdev-edl/1"
PAUSE_BREAK = 0.45      # a pause this long ends a phrase
PUNCT_BREAK = 0.15      # final punctuation plus this pause ends a phrase
LOOKAHEAD = 4           # how many following phrases may retake a phrase
SIMILAR = 0.62          # similarity of normalized text that counts as the same sentence
CONTAINED = 0.7         # share of an earlier phrase's words found, in order, in a later one
CONTAINED_MIN_WORDS = 4 # shorter phrases ("vamos ver") repeat naturally and are not retakes


def normalize(text: str) -> str:
    text = unicodedata.normalize("NFKD", text.lower())
    text = "".join(c for c in text if not unicodedata.combining(c))
    return " ".join(re.sub(r"[^a-z0-9 ]+", " ", text).split())


def split(words: list[dict]) -> list[dict]:
    phrases, current = [], []
    for i, w in enumerate(words):
        current.append(w)
        nxt = words[i + 1] if i + 1 < len(words) else None
        gap = (nxt["inicio"] - w["fim"]) if nxt else None
        ends_sentence = w["w"].rstrip()[-1:] in ".?!…"
        if nxt is None or gap >= PAUSE_BREAK or (ends_sentence and gap >= PUNCT_BREAK):
            phrases.append(current)
            current = []
    out = []
    for n, ws in enumerate(phrases, 1):
        out.append({"id": f"F{n:03d}", "inicio": ws[0]["inicio"], "fim": ws[-1]["fim"],
                    "texto": " ".join(w["w"] for w in ws).strip(), "palavras": ws})
    return out


def _same_sentence(a: str, b: str) -> bool:
    na, nb = normalize(a), normalize(b)
    if not na or not nb:
        return False
    if nb.startswith(na) or (len(na.split()) >= 3 and na.split()[:3] == nb.split()[:3]):
        return True  # an abandoned start ("Hoje eu vou..." → "Hoje eu vou mostrar três...")
    if difflib.SequenceMatcher(None, na, nb).ratio() >= SIMILAR:
        return True
    # A retake that adds words around the same sentence ("se eu repetir uma frase, se ele vai tirar"
    # → "ou seja, se eu repetir uma frase, ele vai tirar e vamos ver..."): most of the earlier
    # phrase's words reappear, in order, inside the later one.
    wa, wb = na.split(), nb.split()
    if len(wa) < CONTAINED_MIN_WORDS:
        return False
    matched = sum(block.size for block in difflib.SequenceMatcher(None, wa, wb, autojunk=False).get_matching_blocks())
    return matched / len(wa) >= CONTAINED


def mark_takes(phrases: list[dict]) -> list[dict]:
    """Set `refeita_em` on every phrase that a later one retakes (keeps the last take)."""
    for i, p in enumerate(phrases):
        p.pop("refeita_em", None)
        for q in phrases[i + 1:i + 1 + LOOKAHEAD]:
            if _same_sentence(p["texto"], q["texto"]):
                p["refeita_em"] = q["id"]
                break
    return phrases


def auto_ids(phrases: list[dict]) -> list[str]:
    return [p["id"] for p in phrases if not p.get("refeita_em")]


def from_phrase_ids(phrases: list[dict], ids: list[str], fonte: str) -> dict:
    by_id = {p["id"]: p for p in phrases}
    missing = [i for i in ids if i not in by_id]
    if missing:
        raise KeyError(f"frases inexistentes: {', '.join(missing)}")
    intervals = [{"inicio": by_id[i]["inicio"], "fim": by_id[i]["fim"], "frases": [i]} for i in ids]
    return {"schema": EDL_SCHEMA, "fonte": fonte, "intervalos": intervals}


def validate_edl(edl: dict) -> list[str]:
    errors = []
    if edl.get("schema") != EDL_SCHEMA:
        errors.append(f"schema deve ser {EDL_SCHEMA}")
    if not edl.get("fonte"):
        errors.append("falta 'fonte'")
    for n, iv in enumerate(edl.get("intervalos") or []):
        if not (isinstance(iv.get("inicio"), (int, float)) and isinstance(iv.get("fim"), (int, float))):
            errors.append(f"intervalo {n}: inicio/fim numéricos")
        elif iv["fim"] <= iv["inicio"]:
            errors.append(f"intervalo {n}: fim antes do início")
    if not edl.get("intervalos"):
        errors.append("nenhum intervalo")
    return errors


def mmss(t: float) -> str:
    return f"{int(t // 60):02d}:{t % 60:05.2f}"


def markdown(phrases: list[dict], fonte: str) -> str:
    """Reading view for the agent: one line per phrase, discarded takes marked."""
    lines = [f"# Frases de {Path(fonte).name}", "",
             "Uma linha por frase. `↺ Fxxx` = tomada refeita depois (fica fora do corte automático).", ""]
    for p in phrases:
        flag = f" ↺ {p['refeita_em']}" if p.get("refeita_em") else ""
        low = [w["w"] for w in p["palavras"] if w.get("p", 1) < 0.5]
        doubt = f"  (dúvida: {', '.join(low)})" if low else ""
        lines.append(f"- **{p['id']}** [{mmss(p['inicio'])}–{mmss(p['fim'])}]{flag} {p['texto']}{doubt}")
    return "\n".join(lines) + "\n"


def write(edit_dir: Path, phrases: list[dict], fonte: str) -> dict:
    edit_dir.mkdir(parents=True, exist_ok=True)
    slim = [{k: v for k, v in p.items()} for p in phrases]
    (edit_dir / "frases.json").write_text(json.dumps(slim, ensure_ascii=False, indent=1), encoding="utf-8")
    (edit_dir / "frases.md").write_text(markdown(phrases, fonte), encoding="utf-8")
    return {"frases": len(phrases), "refeitas": sum(1 for p in phrases if p.get("refeita_em"))}
