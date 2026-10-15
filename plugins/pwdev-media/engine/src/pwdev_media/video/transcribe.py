"""Local word-level transcription.

Backends, run in an isolated `uv run --with` environment (nothing installed globally):
- `mlx`: mlx-whisper on Apple Silicon with macOS 14+ (GPU);
- `faster`: faster-whisper on CPU everywhere else.

The first run downloads the model (~1.6 GB). Output schema `pwdev-transcricao/1`:
{"schema", "fonte", "idioma", "motor", "modelo", "duracao", "palavras": [{"w", "inicio", "fim", "p"}]}
"""
from __future__ import annotations

import json
import os
import platform
import shutil
import subprocess
import tempfile
from pathlib import Path

from . import tools

SCHEMA = "pwdev-transcricao/1"
BACKENDS = {
    "mlx": {"pacote": "mlx-whisper>=0.4", "modelo": "mlx-community/whisper-large-v3-turbo"},
    "faster": {"pacote": "faster-whisper>=1.1", "modelo": "turbo"},
}

SCRIPT = r'''
import json, sys
backend, model, src, lang, prompt, out = sys.argv[1:7]
words = []
if backend == "mlx":
    import mlx_whisper
    res = mlx_whisper.transcribe(src, path_or_hf_repo=model, word_timestamps=True, language=lang or None,
                                 initial_prompt=prompt or None)
    for seg in res.get("segments", []):
        for w in seg.get("words", []):
            words.append({"w": w["word"].strip(), "inicio": round(w["start"], 3), "fim": round(w["end"], 3),
                          "p": round(float(w.get("probability", 1.0)), 3)})
    lang = res.get("language", lang)
else:
    from faster_whisper import WhisperModel
    m = WhisperModel(model, device="cpu", compute_type="int8")
    segs, info = m.transcribe(src, word_timestamps=True, language=lang or None, initial_prompt=prompt or None,
                              vad_filter=False)
    for seg in segs:
        for w in seg.words or []:
            words.append({"w": w.word.strip(), "inicio": round(w.start, 3), "fim": round(w.end, 3),
                          "p": round(float(w.probability), 3)})
    lang = info.language
json.dump({"idioma": lang, "palavras": [w for w in words if w["w"]]}, open(out, "w"), ensure_ascii=False)
'''


def default_backend() -> str:
    if platform.system() == "Darwin" and platform.machine() == "arm64":
        major = int(platform.mac_ver()[0].split(".")[0] or 0)
        if major >= 14:
            return "mlx"
    return "faster"


def transcribe(src: str | Path, out: str | Path, idioma: str = "pt", prompt: str = "",
               backend: str | None = None, modelo: str | None = None) -> dict:
    """Transcribe `src` into `out` (JSON). Returns the document."""
    src, out = Path(src).expanduser().resolve(), Path(out).expanduser()
    if not src.is_file():
        raise FileNotFoundError(f"vídeo não encontrado: {src}")
    backend = backend or default_backend()
    spec = BACKENDS[backend]
    uv = shutil.which("uv") or str(Path.home() / ".local" / "bin" / "uv")
    info = tools.probe(src)
    with tempfile.TemporaryDirectory() as tmp:
        # Decode once to 16 kHz mono WAV: faster for both backends and avoids container quirks.
        wav = Path(tmp) / "audio.wav"
        tools.run(["ffmpeg", "-v", "error", "-y", "-i", str(src), "-vn", "-ac", "1", "-ar", "16000", str(wav)])
        script, raw = Path(tmp) / "t.py", Path(tmp) / "out.json"
        script.write_text(SCRIPT, encoding="utf-8")
        env = {**os.environ, "PATH": str(tools.bin_dir()) + os.pathsep + os.environ.get("PATH", "")}
        result = subprocess.run([uv, "run", "--no-project", "--with", spec["pacote"], "python", str(script),
                                 backend, modelo or spec["modelo"], str(wav), idioma or "", prompt or "", str(raw)],
                                capture_output=True, text=True, env=env)
        if result.returncode != 0:
            raise RuntimeError("a transcrição falhou: " + result.stderr.strip()[-600:])
        data = json.loads(raw.read_text(encoding="utf-8"))
    doc = {"schema": SCHEMA, "fonte": str(src), "idioma": data["idioma"], "motor": backend,
           "modelo": modelo or spec["modelo"], "duracao": info["duracao"], "palavras": data["palavras"]}
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(doc, ensure_ascii=False, indent=1), encoding="utf-8")
    return doc


def load(path: str | Path) -> dict:
    doc = json.loads(Path(path).read_text(encoding="utf-8"))
    if doc.get("schema") != SCHEMA:
        raise ValueError(f"{path} não é uma transcrição {SCHEMA}")
    return doc
