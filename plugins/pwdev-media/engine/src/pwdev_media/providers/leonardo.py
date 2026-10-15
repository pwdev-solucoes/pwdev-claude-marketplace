"""Leonardo (REST v1, legacy contract carried over from pwdev-social-media 2.x).

POST https://cloud.leonardo.ai/api/rest/v1/generations → `sdGenerationJob.generationId`; poll
GET /api/rest/v1/generations/{id} → `generations_by_pk.status` COMPLETE, images in
`generations_by_pk.generated_images[].url`. Leonardo now documents a v2 API (`model` +
`parameters`); migrating to it is pending. Any shape mismatch fails loudly.
Optional LEONARDO_MODEL_ID fixes the model for brand consistency.
"""
from __future__ import annotations

import os
from pathlib import Path

from .. import http
from .base import Provider, Result, write_bytes

BASE = "https://cloud.leonardo.ai/api/rest/v1"


class Leonardo(Provider):
    name = "leonardo"
    operations = ("imagem",)
    poll_seconds = 3.0

    def headers(self) -> dict:
        return {"Authorization": f"Bearer {self.key()}", "accept": "application/json"}

    def op_imagem(self, item: dict, params: dict, out_dir: Path) -> Result:
        body = {"prompt": params["prompt"], "width": int(params.get("largura") or 1080),
                "height": int(params.get("altura") or 1350), "num_images": int(params.get("n") or 1)}
        model = params.get("modelo_id") or os.environ.get("LEONARDO_MODEL_ID")
        if model:
            body["modelId"] = model
        job = http.request("POST", f"{BASE}/generations", self.headers(), body).json()
        gen_id = http.require(job, "sdGenerationJob", "generationId", where="leonardo submit")

        def check():
            data = http.request("GET", f"{BASE}/generations/{gen_id}", self.headers()).json()
            gen = http.require(data, "generations_by_pk", where="leonardo poll")
            status = gen.get("status")
            if status == "COMPLETE":
                return gen
            if status == "FAILED":
                raise RuntimeError("Leonardo: geração falhou")
            return None

        gen = self.wait(check, f"geração {gen_id} no Leonardo")
        images = http.require(gen, "generated_images", where="leonardo result")
        files = [write_bytes(out_dir, "leonardo", "png", http.request("GET", http.require(img, "url", where="leonardo image"),
                                                                        timeout=120).body) for img in images]
        if not files:
            raise http.ContractError("Leonardo: geração completa sem imagens")
        return Result(files, None, {"generation_id": gen_id, "modelo": model or "padrão da conta"})

    def ping(self) -> str:
        data = http.request("GET", f"{BASE}/me", self.headers(), timeout=20).json()
        user = ((data.get("user_details") or [{}])[0].get("user") or {}).get("username", "?")
        return f"chave válida (usuário {user})"
