"""fal: any model through the queue API (https://fal.ai/docs/model-apis/model-endpoints/queue).

The output schema is model-specific, so files are collected from every `url` found in the
result (images[].url, image.url, video.url, audio.url...). The input is passed as given:
`params["entrada"]` holds the model's own fields, plus `prompt`.
"""
from __future__ import annotations

from pathlib import Path

from .. import http
from .base import Provider, Result, write_bytes

QUEUE = "https://queue.fal.run"
MEDIA = {"image": "png", "images": "png", "video": "mp4", "audio": "mp3", "audio_file": "mp3"}


def find_urls(node, key: str = "") -> list[tuple[str, str]]:
    found = []
    if isinstance(node, dict):
        if isinstance(node.get("url"), str) and node["url"].startswith("http"):
            found.append((key, node["url"]))
        for k, v in node.items():
            if k != "url":
                found.extend(find_urls(v, k))
    elif isinstance(node, list):
        for v in node:
            found.extend(find_urls(v, key))
    return found


class Fal(Provider):
    name = "fal"
    operations = ("imagem", "video", "upscale", "lipsync", "recorte", "musica", "sfx")

    def headers(self) -> dict:
        return {"Authorization": f"Key {self.key()}"}

    def _run(self, item: dict, params: dict, out_dir: Path) -> Result:
        model = item["modelo"]
        body = {"prompt": params["prompt"], **(params.get("entrada") or {})} if params.get("prompt") \
            else dict(params.get("entrada") or {})
        sub = http.request("POST", f"{QUEUE}/{model}", self.headers(), body).json()
        req = http.require(sub, "request_id", where="fal queue")
        status_url = sub.get("status_url") or f"{QUEUE}/{model}/requests/{req}/status"
        response_url = sub.get("response_url") or f"{QUEUE}/{model}/requests/{req}"

        def check():
            st = http.request("GET", status_url, self.headers()).json()
            state = http.require(st, "status", where="fal status")
            if state == "COMPLETED":
                if st.get("error"):
                    raise RuntimeError(f"fal: {st.get('error_type', 'erro')}: {st['error']}")
                return st
            return None

        self.wait(check, f"pedido {req} no fal")
        result = http.request("GET", response_url, self.headers()).json()
        urls = find_urls(result)
        if not urls:
            raise http.ContractError("fal: o resultado não trouxe nenhum arquivo (campo 'url')")
        files = [write_bytes(out_dir, key or "saida", MEDIA.get(key, "bin"),
                             http.request("GET", url, timeout=600).body) for key, url in urls]
        return Result(files, None, {"request_id": req})

    op_imagem = op_video = op_upscale = op_lipsync = op_recorte = op_musica = op_sfx = _run

    def ping(self) -> str:
        self.key()
        return "chave presente (o fal não tem verificação gratuita; ela é testada na primeira geração)"
