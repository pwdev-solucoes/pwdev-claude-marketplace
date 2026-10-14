"""OpenRouter: image (POST /api/v1/images) and video (POST /api/v1/videos, async job).

Contract: https://openrouter.ai/docs/guides/overview/multimodal/image-generation.md and
https://openrouter.ai/docs/guides/overview/multimodal/video-generation.md
"""
from __future__ import annotations

import base64
from pathlib import Path

from .. import http
from .base import Provider, Result, write_bytes

BASE = "https://openrouter.ai/api/v1"
EXT = {"image/png": "png", "image/jpeg": "jpg", "image/webp": "webp", "image/svg+xml": "svg"}
IMAGE_PARAMS = ("aspect_ratio", "resolution", "size", "n", "quality", "output_format", "background", "seed")
VIDEO_PARAMS = ("duration", "resolution", "aspect_ratio", "size", "generate_audio", "seed")


class OpenRouter(Provider):
    name = "openrouter"
    operations = ("imagem", "video")

    def headers(self) -> dict:
        return {"Authorization": f"Bearer {self.key()}", "X-Title": "pwdev-media"}

    def op_imagem(self, item: dict, params: dict, out_dir: Path) -> Result:
        body = {"model": item["modelo"], "prompt": params["prompt"]}
        body.update({k: params[k] for k in IMAGE_PARAMS if params.get(k) is not None})
        if params.get("referencias"):
            body["input_references"] = [{"type": "image_url", "image_url": {"url": u}}
                                        for u in params["referencias"]]
        data = http.request("POST", f"{BASE}/images", self.headers(), body).json()
        images = http.require(data, "data", where="openrouter images")
        if not images:
            raise http.ContractError("openrouter images: lista 'data' vazia")
        files = []
        for img in images:
            raw = base64.b64decode(http.require(img, "b64_json", where="openrouter images"))
            files.append(write_bytes(out_dir, "imagem", EXT.get(img.get("media_type"), "png"), raw))
        cost = (data.get("usage") or {}).get("cost")
        return Result(files, cost)

    def op_video(self, item: dict, params: dict, out_dir: Path) -> Result:
        body = {"model": item["modelo"], "prompt": params["prompt"]}
        body.update({k: params[k] for k in VIDEO_PARAMS if params.get(k) is not None})
        if params.get("imagem_inicial"):
            body["frame_images"] = [{"type": "image_url", "image_url": {"url": params["imagem_inicial"]},
                                     "frame_type": "first_frame"}]
        job = http.request("POST", f"{BASE}/videos", self.headers(), body).json()
        job_id = http.require(job, "id", where="openrouter videos")
        polling = job.get("polling_url") or f"{BASE}/videos/{job_id}"

        def check():
            status = http.request("GET", polling, self.headers()).json()
            state = http.require(status, "status", where="openrouter videos poll")
            if state == "completed":
                return status
            if state in ("failed", "cancelled", "expired"):
                raise RuntimeError(f"OpenRouter: geração {state}: {status.get('error', 'sem detalhe')}")
            return None

        done = self.wait(check, f"vídeo {job_id} no OpenRouter")
        urls = http.require(done, "unsigned_urls", where="openrouter videos poll")
        files = [write_bytes(out_dir, "video", "mp4", http.request("GET", u, self.headers(), timeout=600).body)
                 for u in urls]
        return Result(files, (done.get("usage") or {}).get("cost"), {"job": job_id})

    def ping(self) -> str:
        data = http.request("GET", f"{BASE}/key", self.headers(), timeout=20).json()
        info = data.get("data") or {}
        limit = info.get("limit_remaining")
        return "chave válida" + (f", saldo restante US$ {limit:.2f}" if isinstance(limit, (int, float)) else "")
