"""Ideogram 3.0: POST https://api.ideogram.ai/v2/image/generate/ideogram-3 (multipart form).

Contract: https://developer.ideogram.ai/v2/api-reference/images/generate/ideogram-3 — header
`Api-Key`; synchronous response `data[].url` (empty when `is_image_safe` is false). The image links
expire, so they are downloaded right away. Best option for images with legible text.
"""
from __future__ import annotations

from pathlib import Path

from .. import http
from .base import Provider, Result, write_bytes

URL = "https://api.ideogram.ai/v2/image/generate/ideogram-3"


class Ideogram(Provider):
    name = "ideogram"
    operations = ("imagem",)

    def op_imagem(self, item: dict, params: dict, out_dir: Path) -> Result:
        fields = {"prompt": params["prompt"],
                  "aspect_ratio": str(params.get("aspect_ratio") or "4x5").replace(":", "x"),
                  "num_images": params.get("n") or 1,
                  "seed": params.get("seed"),
                  "rendering_speed": params.get("velocidade")}
        data = http.request_multipart(URL, {"Api-Key": self.key()}, fields).json()
        images = http.require(data, "data", where="ideogram generate")
        files, blocked = [], 0
        for img in images:
            if not img.get("url"):
                blocked += 1  # is_image_safe == false
                continue
            files.append(write_bytes(out_dir, "ideogram", "png", http.request("GET", img["url"], timeout=120).body))
        if not files:
            raise RuntimeError(f"Ideogram não entregou imagem ({blocked} bloqueada(s) pelo filtro de segurança)")
        return Result(files, None, {"generation_id": data.get("generation_id"), "bloqueadas": blocked})

    def ping(self) -> str:
        self.key()
        return "chave presente (a geração usa `dry_run` só sob pedido; ela é testada na primeira geração)"
