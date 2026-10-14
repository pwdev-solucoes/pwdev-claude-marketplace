"""Catalog update routine: discover models from public APIs and merge them into the catalog.

Automatic sources (no key needed):
- OpenRouter video models  GET /api/v1/videos/models  (price per second in `pricing_skus`)
- OpenRouter image models  GET /api/v1/images/models  (price kept raw: the unit is not uniform)
- npm registry: latest `hyperframes` and `remotion` (reported only; pinned project versions
  never change on their own)

Subscription products (Runway, Higgsfield, Topaz, Magnific, Adobe) have no public price API:
they become manual reminders in the report.
"""
from __future__ import annotations

from . import catalog as cat
from . import http, paths

OPENROUTER = "https://openrouter.ai/api/v1"
NPM = "https://registry.npmjs.org"
ENGINES = {"local:hyperframes": "hyperframes", "local:remotion": "remotion"}


# The docs show `per-video-second`; the live API (2026-10) answers `duration_seconds_with_audio`,
# `duration_seconds_without_audio` and `_4k` variants. The base price is the default request:
# audio on (`generate_audio` defaults to true), standard resolution.
PREFERRED_SKUS = ("per-video-second", "duration_seconds_with_audio", "duration_seconds",
                  "duration_seconds_without_audio")
PREMIUM_MARKERS = ("4k", "2k", "1080p")


def _second_price(skus: dict) -> float | None:
    if not isinstance(skus, dict):
        return None
    per_second = [k for k in skus if "second" in k]
    standard = sorted(k for k in per_second if not any(m in k.lower() for m in PREMIUM_MARKERS))
    for key in (*PREFERRED_SKUS, *standard, *sorted(per_second)):
        if key in skus:
            try:
                return float(skus[key])
            except (TypeError, ValueError):
                return None
    return None


def openrouter_videos(on: str) -> list[dict]:
    data = http.request("GET", f"{OPENROUTER}/videos/models", timeout=60).json()
    out = []
    for m in http.require(data, "data", where="openrouter videos/models"):
        model_id = http.require(m, "id", where="openrouter videos/models")
        value = _second_price(m.get("pricing_skus"))
        out.append({
            "id": f"openrouter:{model_id}", "categoria": "video-gerar", "nome": m.get("name") or model_id,
            "provedor": "openrouter", "via": "agregador", "operacao": "video", "modelo": model_id,
            "preco": {"valor": value, "unidade": "segundo" if value is not None else "a_verificar",
                      "moeda": "USD", "fonte": f"{OPENROUTER}/videos/models",
                      "verificado_em": on if value is not None else None,
                      "skus": m.get("pricing_skus") or {}},
            "limites": {"duracoes": m.get("supported_durations") or [],
                        "resolucoes": m.get("supported_resolutions") or [],
                        "proporcoes": m.get("supported_aspect_ratios") or []},
            "status": "ativo", "url": f"https://openrouter.ai/{model_id}",
        })
    return out


def openrouter_images(on: str) -> list[dict]:
    data = http.request("GET", f"{OPENROUTER}/images/models", timeout=60).json()
    out = []
    for m in http.require(data, "data", where="openrouter images/models"):
        model_id = http.require(m, "id", where="openrouter images/models")
        out.append({
            "id": f"openrouter:{model_id}", "categoria": "imagem-gerar", "nome": m.get("name") or model_id,
            "provedor": "openrouter", "via": "agregador", "operacao": "imagem", "modelo": model_id,
            "preco": {"valor": None, "unidade": "a_verificar", "moeda": "USD",
                      "fonte": f"{OPENROUTER}/images/models/{model_id}/endpoints", "verificado_em": None,
                      "bruto": m.get("pricing") or {}},
            "limites": {}, "status": "ativo", "url": f"https://openrouter.ai/{model_id}",
        })
    return out


def npm_latest(package: str) -> str:
    data = http.request("GET", f"{NPM}/{package}/latest", timeout=30).json()
    return http.require(data, "version", where=f"npm {package}")


SOURCES = {"openrouter-videos": openrouter_videos, "openrouter-imagens": openrouter_images}


def update(on: str | None = None, sources: tuple[str, ...] | None = None) -> dict:
    """Run every automatic source, save the catalog and write the pt-BR report.

    A source that fails is reported and skipped; it never empties the catalog.
    """
    on = on or cat.today()
    working = cat.load()
    diffs, failures = [], []
    for name in sources or tuple(SOURCES):
        try:
            found = SOURCES[name](on)
        except Exception as exc:  # network or contract: keep going with the other sources
            failures.append(f"{name}: {exc}")
            continue
        if not found:
            failures.append(f"{name}: a fonte respondeu vazia; nada foi marcado como removido")
            continue
        working, diff = cat.merge(working, found, name, on)
        diffs.append(diff)
    engines = []
    for item_id, package in ENGINES.items():
        try:
            latest = npm_latest(package)
        except Exception as exc:
            failures.append(f"npm {package}: {exc}")
            continue
        for item in working["itens"]:
            if item["id"] == item_id:
                if item.get("versao_mais_nova") != latest:
                    engines.append(f"{package}: {item.get('versao_mais_nova') or '?'} → {latest}")
                item["versao_mais_nova"] = latest
    working["atualizado_em"] = on
    errors = cat.validate(working)
    if errors:
        raise http.ContractError("catálogo inválido depois da atualização; nada foi salvo: " + "; ".join(errors[:5]))
    cat.save(working)
    text = cat.diff_markdown(diffs, cat.manual_reminders(working))
    if engines:
        text += "\n## Motores de render (versão fixa dos projetos não muda sozinha)\n\n" + \
                "\n".join(f"- {e}" for e in engines) + "\n"
    if failures:
        text += "\n## Fontes que falharam\n\n" + "\n".join(f"- {f}" for f in failures) + "\n"
    report = paths.reports_dir() / f"{on}.md"
    report.write_text(text, encoding="utf-8")
    return {"relatorio": str(report), "diffs": diffs, "falhas": failures, "motores": engines}
