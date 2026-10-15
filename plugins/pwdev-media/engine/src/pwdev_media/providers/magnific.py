"""Magnific (formerly Freepik AI) image upscaler.

POST https://api.magnific.com/v1/ai/image-upscaler with header `x-magnific-api-key` and JSON
`{"image": <base64>, "scale_factor": "2x"|"4x"|"8x"|"16x"}` →
`data.task_id`, `data.status` (CREATED, IN_PROGRESS, COMPLETED, FAILED), `data.generated[]` URLs
(https://docs.magnific.com/api-reference/image-upscaler-creative/post-image-upscaler). The result is
polled at GET .../image-upscaler/{task_id}, the API's usual pattern for async tasks; if that path
changes, the call fails with a clear message instead of guessing. Output limit: 25.3 MP.
"""
from __future__ import annotations

import base64
from pathlib import Path

from .. import http
from .base import Provider, Result, Unsupported, write_bytes

URL = "https://api.magnific.com/v1/ai/image-upscaler"
SCALES = ("2x", "4x", "8x", "16x")
MAX_PIXELS = 25_300_000


class Magnific(Provider):
    name = "magnific"
    operations = ("upscale",)
    poll_seconds = 4.0

    def headers(self) -> dict:
        return {"x-magnific-api-key": self.key()}

    def op_upscale(self, item: dict, params: dict, out_dir: Path) -> Result:
        src = params.get("arquivo")
        if not src or not Path(src).expanduser().is_file():
            raise Unsupported("upscale precisa de --arquivo <imagem local>")
        scale = str(params.get("escala") or "2x")
        if scale not in SCALES:
            raise Unsupported(f"--escala deve ser uma de {', '.join(SCALES)}")
        image = base64.b64encode(Path(src).expanduser().read_bytes()).decode()
        body = {"image": image, "scale_factor": scale}
        if params.get("prompt"):
            body["prompt"] = params["prompt"]
        sub = http.request("POST", URL, self.headers(), body).json()
        task_id = http.require(sub, "data", "task_id", where="magnific submit")

        def check():
            st = http.request("GET", f"{URL}/{task_id}", self.headers()).json()
            data = http.require(st, "data", where="magnific poll")
            status = http.require(data, "status", where="magnific poll")
            if status == "COMPLETED":
                return data
            if status == "FAILED":
                raise RuntimeError("Magnific: upscale falhou")
            return None

        done = self.wait(check, f"upscale {task_id} no Magnific")
        urls = http.require(done, "generated", where="magnific result")
        if not urls:
            raise http.ContractError("Magnific: tarefa completa sem imagem")
        files = [write_bytes(out_dir, f"upscale-{scale}", "png", http.request("GET", u, timeout=300).body) for u in urls]
        return Result(files, None, {"task": task_id, "escala": scale})

    def ping(self) -> str:
        self.key()
        return "chave presente (o Magnific não tem verificação gratuita; ela é testada no primeiro upscale)"
