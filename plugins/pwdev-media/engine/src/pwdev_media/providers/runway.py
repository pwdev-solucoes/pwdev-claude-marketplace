"""Runway image-to-video: POST https://api.dev.runwayml.com/v1/image_to_video, poll /v1/tasks/{id}.

Headers `Authorization: Bearer` and `X-Runway-Version: 2024-11-06`; body `model`, `promptImage`
(URL or data URI), `promptText`, `ratio` ("720:1280"…), `duration`. Task status SUCCEEDED with the
video URLs in `output[]`; FAILED carries `failure`. Contract carried over from pwdev-social-media
2.x and the official SDK examples; any mismatch fails loudly. Video is the most expensive item of
the stack: the duration is part of the estimate.
"""
from __future__ import annotations

from pathlib import Path

from .. import http
from .base import Provider, Result, Unsupported, write_bytes

BASE = "https://api.dev.runwayml.com/v1"
VERSION = "2024-11-06"
RATIOS = {"9:16": "720:1280", "16:9": "1280:720", "1:1": "960:960", "4:5": "832:1104"}


class Runway(Provider):
    name = "runway"
    operations = ("video",)
    poll_seconds = 5.0

    def headers(self) -> dict:
        return {"Authorization": f"Bearer {self.key()}", "X-Runway-Version": VERSION}

    def op_video(self, item: dict, params: dict, out_dir: Path) -> Result:
        image = params.get("imagem_inicial")
        if not image:
            raise Unsupported("Runway gera vídeo a partir de imagem: informe --imagem-inicial (URL ou arquivo local)")
        ratio = str(params.get("aspect_ratio") or "9:16")
        body = {"model": item["modelo"], "promptImage": image, "promptText": params["prompt"],
                "ratio": RATIOS.get(ratio, ratio), "duration": int(params.get("duration") or 5)}
        task = http.request("POST", f"{BASE}/image_to_video", self.headers(), body).json()
        task_id = http.require(task, "id", where="runway submit")

        def check():
            st = http.request("GET", f"{BASE}/tasks/{task_id}", self.headers()).json()
            status = http.require(st, "status", where="runway task")
            if status == "SUCCEEDED":
                return st
            if status in ("FAILED", "CANCELLED"):
                raise RuntimeError(f"Runway: tarefa {status}: {st.get('failure') or st.get('failureCode') or ''}")
            return None

        done = self.wait(check, f"vídeo {task_id} no Runway")
        urls = http.require(done, "output", where="runway task")
        files = [write_bytes(out_dir, "runway", "mp4", http.request("GET", u, timeout=600).body) for u in urls]
        return Result(files, None, {"task": task_id})

    def ping(self) -> str:
        data = http.request("GET", f"{BASE}/organization", self.headers(), timeout=20).json()
        credits = data.get("creditBalance")
        return "chave válida" + (f", {credits} créditos" if credits is not None else "")
