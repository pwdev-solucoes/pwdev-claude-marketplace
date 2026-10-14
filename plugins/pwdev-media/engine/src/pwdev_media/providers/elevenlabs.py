"""ElevenLabs: music (POST /v1/music), sound effects (POST /v1/sound-generation) and
text to speech (POST /v1/text-to-speech/{voice_id}). All answer with the audio bytes.
"""
from __future__ import annotations

from pathlib import Path

from .. import http
from .base import Provider, Result, Unsupported, write_bytes

BASE = "https://api.elevenlabs.io/v1"


class ElevenLabs(Provider):
    name = "elevenlabs"
    operations = ("musica", "sfx", "tts")

    def headers(self) -> dict:
        return {"xi-api-key": self.key(), "Accept": "audio/mpeg"}

    def _audio(self, url: str, body: dict, out_dir: Path, stem: str) -> Result:
        resp = http.request("POST", url, self.headers(), body, timeout=600)
        if not resp.body or resp.headers.get("Content-Type", "audio").startswith("application/json"):
            raise http.ContractError(f"ElevenLabs: esperava áudio e veio {resp.body[:200]!r}")
        return Result([write_bytes(out_dir, stem, "mp3", resp.body)])

    def op_musica(self, item: dict, params: dict, out_dir: Path) -> Result:
        body = {"prompt": params["prompt"], "model_id": item["modelo"],
                "force_instrumental": params.get("instrumental", True)}
        if params.get("duracao"):
            body["music_length_ms"] = int(float(params["duracao"]) * 1000)
        if params.get("c2pa"):
            body["sign_with_c2pa"] = True
        return self._audio(f"{BASE}/music", body, out_dir, "trilha")

    def op_sfx(self, item: dict, params: dict, out_dir: Path) -> Result:
        body = {"text": params["prompt"], "model_id": item["modelo"]}
        if params.get("duracao"):
            body["duration_seconds"] = float(params["duracao"])
        return self._audio(f"{BASE}/sound-generation", body, out_dir, "efeito")

    def op_tts(self, item: dict, params: dict, out_dir: Path) -> Result:
        voice = params.get("voz")
        if not voice:
            raise Unsupported("TTS da ElevenLabs precisa de --voz <voice_id> (veja as vozes na sua conta)")
        body = {"text": params["prompt"], "model_id": item["modelo"]}
        return self._audio(f"{BASE}/text-to-speech/{voice}", body, out_dir, "narracao")

    def ping(self) -> str:
        data = http.request("GET", f"{BASE}/user/subscription", {"xi-api-key": self.key()}, timeout=20).json()
        tier = data.get("tier", "?")
        used, limit = data.get("character_count"), data.get("character_limit")
        extra = f", {used}/{limit} créditos usados" if used is not None and limit else ""
        return f"chave válida, plano {tier}{extra}"
