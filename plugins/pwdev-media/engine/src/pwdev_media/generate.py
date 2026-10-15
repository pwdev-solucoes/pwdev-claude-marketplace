"""One generation from a catalog item: estimate → cache → guard → provider → ledger."""
from __future__ import annotations

import base64
from pathlib import Path

from . import catalog as cat
from . import paths, providers, spend


def quantity(item: dict, params: dict) -> float:
    unit = item["preco"].get("unidade")
    if unit == "segundo":
        return float(params.get("duration") or params.get("duracao") or 5)
    if unit == "imagem":
        return float(params.get("n") or 1)
    if unit == "minuto":
        return float(params.get("duracao") or 60) / 60
    return 1.0


MIME = {".png": "image/png", ".jpg": "image/jpeg", ".jpeg": "image/jpeg", ".webp": "image/webp"}


def local_inputs(params: dict) -> tuple[dict, dict]:
    """(params for the provider, params for the cache key).

    A local first-frame image becomes a data URI; local input files are part of the cache key by
    content size and modification time, so editing the file means a new generation.
    """
    sent, keyed = dict(params), dict(params)
    for field in ("imagem_inicial", "arquivo"):
        value = params.get(field)
        if not value or str(value).startswith(("http://", "https://", "data:")):
            continue
        path = Path(value).expanduser()
        if not path.is_file():
            raise FileNotFoundError(f"arquivo não encontrado: {path}")
        stat = path.stat()
        keyed[field] = f"{path.resolve()}@{stat.st_size}:{int(stat.st_mtime)}"
        if field == "imagem_inicial":
            mime = MIME.get(path.suffix.lower())
            if not mime:
                raise ValueError(f"imagem inicial deve ser PNG, JPG ou WebP: {path.name}")
            sent[field] = f"data:{mime};base64," + base64.b64encode(path.read_bytes()).decode()
        else:
            sent[field] = str(path)
    return sent, keyed


def run(item_id: str, params: dict, confirmar: bool = False, acima_do_orcamento: bool = False,
        saida: str | None = None, so_estimar: bool = False) -> dict:
    working = cat.load()
    item = cat.find(working, item_id)
    if item["status"] in ("removido", "deprecado"):
        raise providers.Unsupported(f"{item_id} está {item['status']} no catálogo; escolha outro "
                                    "(`pwdev-media catalogo recomendar`)")
    if item["via"] == "local":
        raise providers.Unsupported(f"{item_id} roda local, dentro do pipeline de cada plugin; não pelo `gerar`")
    if item["via"] == "assinatura":
        api = [i["id"] for i in working["itens"] if i["provedor"] == item["provedor"] and i["via"] == "api"
               and i["status"] not in ("removido", "deprecado")]
        hint = f" Pela API: {', '.join(api)}." if api else " Use o app do provedor."
        raise providers.Unsupported(f"{item_id} é a assinatura do app, que não gera por API.{hint}")
    est = spend.estimate(item, quantity(item, params))
    if so_estimar:
        return {"estimativa": est}
    provider = providers.get(item["provedor"])
    params, keyed = local_inputs(params)
    h = spend.request_hash(item_id, keyed)
    reuse = spend.cached(h)
    if reuse:
        return {"estimativa": est, "arquivos": reuse, "cache": True, "custo_real_usd": 0.0}
    provider.key()  # missing key fails before asking for money
    spend.guard(est, confirmar, acima_do_orcamento)
    out_dir = Path(saida).expanduser() if saida else paths.outputs_dir() / h
    result = provider.generate(item, params, out_dir)
    spend.record(item, est, h, result.arquivos, result.custo_real_usd, result.extra)
    return {"estimativa": est, "arquivos": result.arquivos, "cache": False,
            "custo_real_usd": result.custo_real_usd, "exige_rotulo_ia": item.get("exige_rotulo_ia", True),
            "licenca_comercial": item["licenca_comercial"]}
