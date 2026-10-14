"""Spend guard, monthly budget, ledger and generation cache.

Rules:
- a paid call needs `confirmar=True`; without it the caller only gets the estimate;
- a call that would pass the monthly budget is refused unless `acima_do_orcamento=True`;
- every paid generation is appended to ~/.pwdev/media/ledger.jsonl;
- the same request (model + parameters) already generated and still on disk is reused, free.
"""
from __future__ import annotations

import datetime as dt
import hashlib
import json
from pathlib import Path

from . import paths


class NeedsConfirmation(RuntimeError):
    def __init__(self, estimate: dict):
        super().__init__("chamada paga sem confirmação")
        self.estimate = estimate


class OverBudget(RuntimeError):
    pass


def request_hash(item_id: str, params: dict) -> str:
    blob = json.dumps({"item": item_id, "params": params}, sort_keys=True, ensure_ascii=False)
    return hashlib.sha256(blob.encode("utf-8")).hexdigest()[:16]


def estimate(item: dict, quantidade: float) -> dict:
    """Estimated cost. `quantidade` is in the item's price unit (seconds, images, uses...)."""
    preco = item["preco"]
    paid = item["via"] != "local"
    value = preco.get("valor")
    if not paid:
        total = 0.0
    elif value is None or preco.get("unidade") in ("mes", "ano"):
        total = None  # unknown per-use price: the provider reports the real cost afterwards
    else:
        total = round(value * quantidade, 4)
    return {"item": item["id"], "pago": paid, "quantidade": quantidade, "unidade": preco.get("unidade"),
            "valor_unitario": value, "total_usd": total, "fonte": preco.get("fonte"),
            "verificado_em": preco.get("verificado_em")}


def config() -> dict:
    path = paths.config_file()
    return json.loads(path.read_text(encoding="utf-8")) if path.is_file() else {}


def set_budget(usd: float | None) -> None:
    cfg = config()
    if usd is None:
        cfg.pop("orcamento_mensal_usd", None)
    else:
        cfg["orcamento_mensal_usd"] = float(usd)
    paths.config_file().write_text(json.dumps(cfg, indent=2) + "\n", encoding="utf-8")


def entries(month: str | None = None) -> list[dict]:
    path = paths.ledger_file()
    if not path.is_file():
        return []
    rows = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
    return [r for r in rows if month is None or r["data"].startswith(month)]


def month_total(month: str | None = None) -> float:
    month = month or dt.date.today().strftime("%Y-%m")
    total = 0.0
    for row in entries(month):
        cost = row.get("custo_real_usd")
        if cost is None:
            cost = row.get("estimativa_usd")
        total += cost or 0.0
    return round(total, 4)


def guard(est: dict, confirmar: bool, acima_do_orcamento: bool = False) -> None:
    if not est["pago"]:
        return
    if not confirmar:
        raise NeedsConfirmation(est)
    budget = config().get("orcamento_mensal_usd")
    if budget is not None and not acima_do_orcamento:
        expected = month_total() + (est["total_usd"] or 0.0)
        if expected > budget:
            raise OverBudget(f"passaria do orçamento do mês: US$ {expected:.2f} de US$ {budget:.2f}. "
                             "Aumente com `pwdev-media custo orcamento <valor>` ou confirme acima do orçamento.")


def cached(h: str) -> list[str] | None:
    for row in reversed(entries()):
        if row.get("hash") == h and row.get("arquivos") and all(Path(p).is_file() for p in row["arquivos"]):
            return row["arquivos"]
    return None


def record(item: dict, est: dict, h: str, arquivos: list[str], custo_real: float | None,
           extra: dict | None = None) -> dict:
    row = {"data": dt.datetime.now().isoformat(timespec="seconds"), "item": item["id"],
           "provedor": item["provedor"], "categoria": item["categoria"], "hash": h,
           "estimativa_usd": est["total_usd"], "custo_real_usd": custo_real, "arquivos": arquivos,
           **(extra or {})}
    with paths.ledger_file().open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(row, ensure_ascii=False) + "\n")
    return row
