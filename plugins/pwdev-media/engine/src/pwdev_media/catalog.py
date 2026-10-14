"""Catalog of models and applications by category.

The plugin ships a curated seed (data/catalogo.json). The working copy lives in
~/.pwdev/media/catalogo.json and is what discovery updates. Two kinds of fields:

- curated (quality, commercial license, AI label, notes): written by people, never
  overwritten by discovery;
- discovered (price, limits, status): refreshed from the provider APIs, with source and date.

Nothing is invented: an unknown price stays `valor: null` and an unknown license stays
`a_verificar`.
"""
from __future__ import annotations

import copy
import datetime as dt
import json
from pathlib import Path

from . import paths

SCHEMA = "pwdev-media-catalogo/1"
VIAS = {"agregador", "api", "assinatura", "local"}
STATUS = {"ativo", "beta", "deprecado", "removido"}
LICENCAS = {"sim", "nao", "a_verificar"}
ORIGENS = {"curado", "descoberto"}
OBJETIVOS = ("barato", "equilibrado", "maximo")
CURATED = ("nome", "qualidade", "licenca_comercial", "exige_rotulo_ia", "notas", "operacao", "url")
PRICE_CHANGE = 0.10  # relative change that goes into the report
STALE_DAYS = 30
RECURRING = ("mes", "ano")


def today() -> str:
    return dt.date.today().isoformat()


def load_seed() -> dict:
    return json.loads((paths.DATA / "catalogo.json").read_text(encoding="utf-8"))


def load(path: Path | None = None) -> dict:
    """Working catalog; created from the seed on first use and topped up with new seed items."""
    path = path or paths.catalog_file()
    seed = load_seed()
    if not path.is_file():
        save(seed, path)
        return seed
    catalog = json.loads(path.read_text(encoding="utf-8"))
    known = {item["id"] for item in catalog["itens"]}
    added = [copy.deepcopy(i) for i in seed["itens"] if i["id"] not in known]
    for cid, cat in seed["categorias"].items():
        catalog["categorias"].setdefault(cid, cat)
    if added:
        catalog["itens"].extend(added)
        save(catalog, path)
    return catalog


def save(catalog: dict, path: Path | None = None) -> Path:
    path = path or paths.catalog_file()
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(".tmp")
    tmp.write_text(json.dumps(catalog, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    tmp.replace(path)
    return path


def _is_date(value) -> bool:
    try:
        dt.date.fromisoformat(value)
        return True
    except (TypeError, ValueError):
        return False


def validate(catalog: dict) -> list[str]:
    errors = []
    if catalog.get("schema") != SCHEMA:
        errors.append(f"schema deve ser {SCHEMA}")
    if not _is_date(catalog.get("atualizado_em")):
        errors.append("atualizado_em deve ser uma data AAAA-MM-DD")
    categorias = catalog.get("categorias") or {}
    if not categorias:
        errors.append("sem categorias")
    seen = set()
    for n, item in enumerate(catalog.get("itens") or []):
        where = item.get("id") or f"itens[{n}]"
        for field in ("id", "categoria", "nome", "provedor", "via", "preco", "licenca_comercial", "status",
                      "origem"):
            if field not in item:
                errors.append(f"{where}: falta '{field}'")
        if item.get("id") in seen:
            errors.append(f"{where}: id repetido")
        seen.add(item.get("id"))
        if item.get("categoria") not in categorias:
            errors.append(f"{where}: categoria desconhecida '{item.get('categoria')}'")
        if item.get("via") not in VIAS:
            errors.append(f"{where}: via deve ser uma de {sorted(VIAS)}")
        if item.get("status") not in STATUS:
            errors.append(f"{where}: status deve ser um de {sorted(STATUS)}")
        if item.get("licenca_comercial") not in LICENCAS:
            errors.append(f"{where}: licenca_comercial deve ser uma de {sorted(LICENCAS)}")
        if item.get("origem") not in ORIGENS:
            errors.append(f"{where}: origem deve ser uma de {sorted(ORIGENS)}")
        q = item.get("qualidade")
        if q is not None and (not isinstance(q, int) or not 1 <= q <= 5):
            errors.append(f"{where}: qualidade deve ser 1 a 5 ou null")
        preco = item.get("preco") or {}
        for field in ("valor", "unidade", "moeda", "fonte", "verificado_em"):
            if field not in preco:
                errors.append(f"{where}: preco sem '{field}'")
        if preco.get("valor") is not None:
            if not isinstance(preco["valor"], (int, float)) or preco["valor"] < 0:
                errors.append(f"{where}: preco.valor deve ser número >= 0 ou null")
            if not preco.get("fonte"):
                errors.append(f"{where}: preço com valor precisa de fonte")
            if not _is_date(preco.get("verificado_em")):
                errors.append(f"{where}: preço com valor precisa de verificado_em")
    return errors


def find(catalog: dict, item_id: str) -> dict:
    for item in catalog["itens"]:
        if item["id"] == item_id:
            return item
    raise KeyError(f"item '{item_id}' não está no catálogo (veja `pwdev-media catalogo listar`)")


def query(catalog: dict, categoria: str | None = None, provedor: str | None = None,
          via: str | None = None, incluir_removidos: bool = False) -> list[dict]:
    items = []
    for item in catalog["itens"]:
        if categoria and item["categoria"] != categoria:
            continue
        if provedor and item["provedor"] != provedor:
            continue
        if via and item["via"] != via:
            continue
        if not incluir_removidos and item["status"] in ("removido", "deprecado"):
            continue
        items.append(item)
    return items


def recommend(catalog: dict, categoria: str, objetivo: str = "equilibrado",
              apenas_comercial: bool = True, provedores: set[str] | None = None) -> list[dict]:
    """Ranked candidates. Items without curated quality are left out until someone rates them."""
    if objetivo not in OBJETIVOS:
        raise ValueError(f"objetivo deve ser um de {OBJETIVOS}")
    pool = [i for i in query(catalog, categoria) if i.get("qualidade")]
    if apenas_comercial:
        pool = [i for i in pool if i["licenca_comercial"] == "sim"]
    if provedores is not None:
        pool = [i for i in pool if i["provedor"] in provedores or i["via"] == "local"]

    def price(item):
        # A subscription (per month/year) is not comparable with a per-use price: it goes last.
        value = item["preco"]["valor"]
        if value is None or item["preco"].get("unidade") in RECURRING:
            return float("inf")
        return value

    if objetivo == "barato":
        pool = [i for i in pool if i["qualidade"] >= 3]
        return sorted(pool, key=lambda i: (price(i), -i["qualidade"]))
    if objetivo == "maximo":
        return sorted(pool, key=lambda i: (-i["qualidade"], price(i)))
    good = sorted([i for i in pool if i["qualidade"] >= 4], key=lambda i: (price(i), -i["qualidade"]))
    rest = sorted([i for i in pool if i["qualidade"] < 4], key=lambda i: (-i["qualidade"], price(i)))
    return good + rest


def age_days(catalog: dict, on: str | None = None) -> int:
    ref = dt.date.fromisoformat(on or today())
    return (ref - dt.date.fromisoformat(catalog["atualizado_em"])).days


def is_stale(catalog: dict, on: str | None = None) -> bool:
    return age_days(catalog, on) > STALE_DAYS


def merge(catalog: dict, discovered: list[dict], fonte: str, on: str | None = None) -> tuple[dict, dict]:
    """Merge one discovery source into the catalog. Returns (new catalog, diff).

    `discovered` is the full list a source returned now (same entry shape, without curated
    fields). Items of that source missing from the list are marked `removido`, never deleted.
    """
    on = on or today()
    result = copy.deepcopy(catalog)
    by_id = {item["id"]: item for item in result["itens"]}
    diff = {"fonte": fonte, "data": on, "novos": [], "removidos": [], "preco": [], "voltaram": []}
    seen = set()
    for new in discovered:
        seen.add(new["id"])
        old = by_id.get(new["id"])
        if old is None:
            item = {"qualidade": None, "licenca_comercial": "a_verificar", "exige_rotulo_ia": True,
                    "notas": "", **new, "origem": "descoberto", "fonte_descoberta": fonte}
            result["itens"].append(item)
            by_id[item["id"]] = item
            diff["novos"].append(item["id"])
            continue
        before = old["preco"].get("valor")
        after = new["preco"].get("valor")
        if before and after is not None and abs(after - before) / before > PRICE_CHANGE:
            diff["preco"].append({"id": old["id"], "antes": before, "depois": after,
                                  "unidade": new["preco"].get("unidade")})
        if old["status"] == "removido":
            diff["voltaram"].append(old["id"])
        for field, value in new.items():
            if field not in CURATED and field != "origem":
                old[field] = value
        if old["status"] == "removido":
            old["status"] = new.get("status", "ativo")
        old["fonte_descoberta"] = fonte
    for item in result["itens"]:
        if item.get("fonte_descoberta") == fonte and item["id"] not in seen and item["status"] != "removido":
            item["status"] = "removido"
            diff["removidos"].append(item["id"])
    result["atualizado_em"] = on
    return result, diff


def diff_markdown(diffs: list[dict], lembretes: list[dict]) -> str:
    lines = [f"# Atualização do catálogo · {diffs[0]['data'] if diffs else today()}", ""]
    if not any(d["novos"] or d["removidos"] or d["preco"] or d["voltaram"] for d in diffs):
        lines += ["Nenhuma mudança nas fontes automáticas.", ""]
    for d in diffs:
        if not (d["novos"] or d["removidos"] or d["preco"] or d["voltaram"]):
            continue
        lines += [f"## {d['fonte']}", ""]
        if d["novos"]:
            lines.append(f"- **Novos ({len(d['novos'])})**, sem nota de qualidade até a curadoria: "
                         + ", ".join(f"`{i}`" for i in d["novos"]))
        if d["removidos"]:
            lines.append(f"- **Sumiram da fonte ({len(d['removidos'])})**, marcados como removidos: "
                         + ", ".join(f"`{i}`" for i in d["removidos"]))
        if d["voltaram"]:
            lines.append("- **Voltaram:** " + ", ".join(f"`{i}`" for i in d["voltaram"]))
        for p in d["preco"]:
            change = (p["depois"] - p["antes"]) / p["antes"] * 100
            lines.append(f"- **Preço** `{p['id']}`: {p['antes']} → {p['depois']} por {p['unidade']} "
                         f"({change:+.0f}%)")
        lines.append("")
    if lembretes:
        lines += ["## Conferir à mão (sem API pública de preços)", ""]
        lines += [f"- {r['nome']}: {r['url']} (última verificação: {r['verificado_em'] or 'nunca'})"
                  for r in lembretes]
        lines.append("")
    return "\n".join(lines)


def manual_reminders(catalog: dict) -> list[dict]:
    """Subscription items whose price can only be checked by a person, one per provider."""
    out, seen = [], set()
    for item in catalog["itens"]:
        if item["via"] == "assinatura" and item["provedor"] not in seen and item["status"] != "removido":
            seen.add(item["provedor"])
            out.append({"nome": item["nome"], "url": item.get("url", ""),
                        "verificado_em": item["preco"].get("verificado_em")})
    return out
