"""One generation from a catalog item: estimate → cache → guard → provider → ledger."""
from __future__ import annotations

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


def run(item_id: str, params: dict, confirmar: bool = False, acima_do_orcamento: bool = False,
        saida: str | None = None, so_estimar: bool = False) -> dict:
    working = cat.load()
    item = cat.find(working, item_id)
    if item["status"] in ("removido", "deprecado"):
        raise providers.Unsupported(f"{item_id} está {item['status']} no catálogo; escolha outro "
                                    "(`pwdev-media catalogo recomendar`)")
    if item["via"] == "local":
        raise providers.Unsupported(f"{item_id} roda local, dentro do pipeline de cada plugin; não pelo `gerar`")
    est = spend.estimate(item, quantity(item, params))
    if so_estimar:
        return {"estimativa": est}
    provider = providers.get(item["provedor"])
    h = spend.request_hash(item_id, params)
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
