"""Black Forest Labs (FLUX): POST https://api.bfl.ai/v1/<model>, poll `polling_url` until Ready.

Contract: https://docs.bfl.ai/quick_start/generating_images — header `x-key`; submit returns
`id` and `polling_url`; statuses Ready / Error / Failed; the image is at `result.sample`, a signed
URL valid for 10 minutes, so it is downloaded right away.
"""
from __future__ import annotations

from pathlib import Path

from .. import http
from .base import Provider, Result, write_bytes

BASE = "https://api.bfl.ai/v1"
RATIOS = {"1:1": (1024, 1024), "4:5": (1024, 1280), "9:16": (768, 1344), "16:9": (1344, 768), "3:4": (896, 1184)}


class BFL(Provider):
    name = "bfl"
    operations = ("imagem",)
    poll_seconds = 1.0

    def headers(self) -> dict:
        return {"x-key": self.key(), "accept": "application/json"}

    def op_imagem(self, item: dict, params: dict, out_dir: Path) -> Result:
        width, height = params.get("largura"), params.get("altura")
        if not (width and height):
            width, height = RATIOS.get(str(params.get("aspect_ratio") or "4:5").replace("x", ":"), RATIOS["4:5"])
        body = {"prompt": params["prompt"], "width": int(width), "height": int(height)}
        if params.get("seed") is not None:
            body["seed"] = int(params["seed"])
        job = http.request("POST", f"{BASE}/{item['modelo']}", self.headers(), body).json()
        polling = http.require(job, "polling_url", where="bfl submit")

        def check():
            st = http.request("GET", polling, self.headers()).json()
            status = http.require(st, "status", where="bfl poll")
            if status == "Ready":
                return st
            if status in ("Error", "Failed", "Content Moderated", "Request Moderated"):
                raise RuntimeError(f"BFL: geração {status}: {st.get('details') or st.get('result') or ''}")
            return None

        done = self.wait(check, f"imagem {job.get('id', '?')} na BFL")
        url = http.require(done, "result", "sample", where="bfl result")
        return Result([write_bytes(out_dir, "flux", "png", http.request("GET", url, timeout=120).body)],
                      None, {"job": job.get("id")})

    def ping(self) -> str:
        self.key()
        return "chave presente (a BFL não tem verificação gratuita; ela é testada na primeira geração)"
