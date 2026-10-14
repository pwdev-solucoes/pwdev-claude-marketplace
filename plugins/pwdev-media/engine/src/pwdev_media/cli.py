"""`pwdev-media` command line. Text output in pt-BR; `--json` for skills and scripts.

Exit codes: 0 ok · 2 uso · 3 precisa de confirmação · 4 orçamento · 5 erro do provedor/contrato
· 6 sem chave · 7 não suportado.
"""
from __future__ import annotations

import argparse
import json
import shutil
import sys

from . import __version__, catalog, discovery, formats, generate, http, keys, providers, schedule, spend

EXIT_CONFIRM, EXIT_BUDGET, EXIT_PROVIDER, EXIT_KEY, EXIT_UNSUPPORTED = 3, 4, 5, 6, 7


def emit(args, data, text: str) -> None:
    print(json.dumps(data, ensure_ascii=False, indent=2) if args.json else text)


def money(value) -> str:
    return "?" if value is None else f"US$ {value:.4f}".rstrip("0").rstrip(".")


def price(item: dict) -> str:
    p = item["preco"]
    if p.get("valor") is None:
        return "preço a verificar"
    return f"{money(p['valor'])}/{p['unidade']}"


# ---------------------------------------------------------------- status / chaves

def cmd_status(args) -> int:
    working = catalog.load()
    tools = {t: bool(shutil.which(t)) for t in ("ffmpeg", "node", "npx", "uv")}
    key_rows = keys.report()
    live = {}
    if args.ao_vivo:
        for row in key_rows:
            if row["origem"] and row["provedor"] in providers.REGISTRY:
                try:
                    live[row["provedor"]] = "ok: " + providers.get(row["provedor"]).ping()
                except Exception as exc:
                    live[row["provedor"]] = f"falhou: {exc}"
    budget = spend.config().get("orcamento_mensal_usd")
    data = {"versao": __version__, "ferramentas": tools, "chaves": key_rows, "ao_vivo": live,
            "catalogo": {"atualizado_em": working["atualizado_em"], "idade_dias": catalog.age_days(working),
                         "desatualizado": catalog.is_stale(working), "itens": len(working["itens"])},
            "custo_mes_usd": spend.month_total(), "orcamento_mensal_usd": budget}
    lines = [f"pwdev-media {__version__}", "",
             "Ferramentas: " + ", ".join(f"{t} {'ok' if ok else 'falta'}" for t, ok in tools.items()),
             "", "Chaves:"]
    for row in key_rows:
        where = {"env": "variável de ambiente", "keychain": "Keychain"}.get(row["origem"], "não configurada")
        extra = f" · {live[row['provedor']]}" if row["provedor"] in live else ""
        lines.append(f"  {row['provedor']:<11} {where}{extra}")
    age = data["catalogo"]
    lines += ["", f"Catálogo: {age['itens']} itens, atualizado em {age['atualizado_em']} "
                  f"({age['idade_dias']} dias)" + (" — DESATUALIZADO, rode `pwdev-media catalogo atualizar`"
                                                   if age["desatualizado"] else ""),
              f"Gasto no mês: {money(data['custo_mes_usd'])}"
              + (f" de {money(budget)}" if budget is not None else " (sem orçamento definido)")]
    emit(args, data, "\n".join(lines))
    return 0


def cmd_chaves(args) -> int:
    if args.acao == "guardar":
        print(keys.store(args.provedor))
    elif args.acao == "apagar":
        print(keys.delete(args.provedor))
    else:
        rows = keys.report()
        emit(args, rows, "\n".join(f"{r['provedor']:<11} {r['variavel']:<22} {r['origem'] or 'não configurada'}"
                                   for r in rows))
    return 0


# ---------------------------------------------------------------- catálogo

def cmd_catalogo(args) -> int:
    working = catalog.load()
    if args.acao == "categorias":
        rows = [{"id": cid, "nome": c["nome"], "itens": len(catalog.query(working, cid))}
                for cid, c in working["categorias"].items()]
        emit(args, rows, "\n".join(f"{r['id']:<16} {r['nome']} ({r['itens']})" for r in rows))
    elif args.acao == "listar":
        rows = catalog.query(working, args.categoria, args.provedor, args.via, args.todos)
        emit(args, rows, "\n".join(
            f"{i['id']:<42} {i['via']:<10} q{i.get('qualidade') or '?'} {price(i):<24} "
            f"licença {i['licenca_comercial']}" + (f" [{i['status']}]" if i["status"] != "ativo" else "")
            for i in rows) or "Nada encontrado.")
    elif args.acao == "mostrar":
        item = catalog.find(working, args.id)
        emit(args, item, json.dumps(item, ensure_ascii=False, indent=2))
    elif args.acao == "recomendar":
        have = None
        if args.so_com_chave:
            have = {r["provedor"] for r in keys.report() if r["origem"]}
        rows = catalog.recommend(working, args.categoria, args.objetivo, not args.incluir_sem_licenca, have)
        text = "\n".join(f"{n}. {i['nome']} ({i['id']}) · q{i['qualidade']} · {price(i)} · {i['via']}"
                         + (f"\n   {i['notas']}" if i.get("notas") else "")
                         for n, i in enumerate(rows[:args.limite], 1))
        emit(args, rows[:args.limite], text or "Nenhum item com nota de qualidade e licença comercial nessa categoria.")
    elif args.acao == "validar":
        errors = catalog.validate(working)
        emit(args, errors, "\n".join(errors) or "Catálogo válido.")
        return 1 if errors else 0
    elif args.acao == "atualizar":
        result = discovery.update()
        emit(args, result, open(result["relatorio"], encoding="utf-8").read() + f"\nRelatório: {result['relatorio']}")
    elif args.acao == "agendar":
        if args.remover:
            print(schedule.uninstall())
        elif args.instalar:
            print(schedule.install())
        else:
            info = schedule.plan()
            emit(args, info, info.get("comando") or f"Arquivo {info['arquivo']}:\n\n{info['conteudo']}\n"
                 "Para instalar: pwdev-media catalogo agendar --instalar")
    return 0


# ---------------------------------------------------------------- formatos

def cmd_formatos(args) -> int:
    if args.acao == "listar":
        rows = formats.by_platform(args.plataforma)
        emit(args, rows, "\n".join(f"{f['id']:<18} {f['largura']}x{f['altura']:<6} {f['nome']}" for f in rows))
        return 0
    fmt = formats.get(args.id)
    if args.acao == "mostrar":
        x, y, w, h = formats.safe_box(fmt)
        emit(args, {**fmt, "zona_segura_px": [x, y, w, h]},
             f"{fmt['nome']} {fmt['largura']}x{fmt['altura']}\nZona segura: x {x}–{x + w}, y {y}–{y + h}\n{fmt['notas']}")
        return 0
    box = tuple(int(v) for v in args.caixa.split(","))
    problems = formats.check_box(fmt, box)
    emit(args, problems, "Dentro da zona segura." if not problems else "Fora da zona segura: " + "; ".join(problems))
    return 0 if not problems else 1


# ---------------------------------------------------------------- gerar / custo

def cmd_gerar(args) -> int:
    params = {"prompt": args.prompt}
    for field in ("duration", "aspect_ratio", "resolution", "n", "seed", "voz", "imagem_inicial", "duracao"):
        value = getattr(args, field, None)
        if value is not None:
            params[field] = value
    if args.entrada:
        params["entrada"] = json.loads(args.entrada)
    result = generate.run(args.item, params, args.confirmar, args.acima_do_orcamento, args.saida, args.estimar)
    est = result["estimativa"]
    head = (f"Estimativa: {money(est['total_usd'])} ({est['quantidade']:g} {est['unidade']} × "
            f"{money(est['valor_unitario'])}, preço de {est['verificado_em'] or 'data desconhecida'})")
    if args.estimar:
        emit(args, result, head)
        return 0
    lines = [head, "Reaproveitado do cache, sem custo." if result["cache"] else
             f"Custo informado pelo provedor: {money(result.get('custo_real_usd'))}"]
    lines += [f"Arquivo: {p}" for p in result["arquivos"]]
    if result.get("exige_rotulo_ia"):
        lines.append("Lembrete: marque como conteúdo gerado por IA ao publicar (Meta/TikTok).")
    if result.get("licenca_comercial") != "sim":
        lines.append(f"Atenção: licença comercial {result.get('licenca_comercial')} para este modelo.")
    emit(args, result, "\n".join(lines))
    return 0


def cmd_custo(args) -> int:
    if args.acao == "orcamento":
        if args.valor is not None:
            spend.set_budget(None if args.valor < 0 else args.valor)
        budget = spend.config().get("orcamento_mensal_usd")
        emit(args, {"orcamento_mensal_usd": budget},
             f"Orçamento mensal: {money(budget)}" if budget is not None else "Sem orçamento definido.")
        return 0
    rows = spend.entries(args.mes)
    total = spend.month_total(args.mes) if args.mes else round(sum(
        (r.get("custo_real_usd") if r.get("custo_real_usd") is not None else r.get("estimativa_usd")) or 0
        for r in rows), 4)
    text = "\n".join(f"{r['data']}  {r['item']:<40} {money(r.get('custo_real_usd') or r.get('estimativa_usd'))}"
                     for r in rows) or "Nenhuma geração registrada."
    emit(args, {"itens": rows, "total_usd": total}, text + f"\nTotal: {money(total)}")
    return 0


# ---------------------------------------------------------------- parser

def parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="pwdev-media", description="Núcleo da suíte pwdev de mídia")
    p.add_argument("--json", action="store_true", help="saída em JSON")
    sub = p.add_subparsers(dest="cmd", required=True)

    sub.add_parser("versao")
    s = sub.add_parser("status")
    s.add_argument("--ao-vivo", action="store_true", help="testa cada chave com uma chamada gratuita")

    s = sub.add_parser("chaves")
    s.add_argument("acao", choices=("listar", "guardar", "apagar"), nargs="?", default="listar")
    s.add_argument("provedor", nargs="?")

    s = sub.add_parser("catalogo")
    s.add_argument("acao", choices=("categorias", "listar", "mostrar", "recomendar", "validar", "atualizar", "agendar"))
    s.add_argument("id", nargs="?")
    s.add_argument("--categoria")
    s.add_argument("--provedor")
    s.add_argument("--via", choices=sorted(catalog.VIAS))
    s.add_argument("--todos", action="store_true", help="inclui removidos e deprecados")
    s.add_argument("--objetivo", choices=catalog.OBJETIVOS, default="equilibrado")
    s.add_argument("--incluir-sem-licenca", action="store_true")
    s.add_argument("--so-com-chave", action="store_true", help="só provedores com chave configurada")
    s.add_argument("--limite", type=int, default=5)
    s.add_argument("--instalar", action="store_true")
    s.add_argument("--remover", action="store_true")

    s = sub.add_parser("formatos")
    s.add_argument("acao", choices=("listar", "mostrar", "conferir"))
    s.add_argument("id", nargs="?")
    s.add_argument("--plataforma")
    s.add_argument("--caixa", help="x,y,largura,altura do elemento, em pixels")

    s = sub.add_parser("gerar")
    s.add_argument("item", help="id do catálogo, ex.: openrouter:google/veo-3.1")
    s.add_argument("--prompt", required=True)
    s.add_argument("--duration", type=int, help="vídeo: segundos")
    s.add_argument("--duracao", type=float, help="áudio: segundos")
    s.add_argument("--aspect-ratio", dest="aspect_ratio")
    s.add_argument("--resolution")
    s.add_argument("--n", type=int)
    s.add_argument("--seed", type=int)
    s.add_argument("--voz", help="voice_id do TTS")
    s.add_argument("--imagem-inicial", dest="imagem_inicial", help="URL ou data URL do primeiro quadro")
    s.add_argument("--entrada", help="JSON com campos próprios do modelo (fal)")
    s.add_argument("--saida", help="pasta de saída")
    s.add_argument("--estimar", action="store_true", help="só mostra a estimativa")
    s.add_argument("--confirmar", action="store_true", help="autoriza a chamada paga")
    s.add_argument("--acima-do-orcamento", action="store_true")

    s = sub.add_parser("custo")
    s.add_argument("acao", choices=("extrato", "orcamento"), nargs="?", default="extrato")
    s.add_argument("valor", nargs="?", type=float, help="orçamento mensal em US$ (negativo remove)")
    s.add_argument("--mes", help="AAAA-MM")
    return p


def main(argv: list[str] | None = None) -> int:
    args = parser().parse_args(argv)
    try:
        if args.cmd == "versao":
            print(__version__)
            return 0
        if args.cmd in ("catalogo", "formatos") and args.acao in ("mostrar", "conferir") and not args.id:
            print("Informe o id.", file=sys.stderr)
            return 2
        if args.cmd == "catalogo" and args.acao == "recomendar" and not args.categoria:
            print("Informe --categoria (veja `pwdev-media catalogo categorias`).", file=sys.stderr)
            return 2
        if args.cmd == "chaves" and args.acao != "listar" and not args.provedor:
            print("Informe o provedor.", file=sys.stderr)
            return 2
        if args.cmd == "formatos" and args.acao == "conferir" and not args.caixa:
            print("Informe --caixa x,y,largura,altura.", file=sys.stderr)
            return 2
        handler = {"status": cmd_status, "chaves": cmd_chaves, "catalogo": cmd_catalogo,
                   "formatos": cmd_formatos, "gerar": cmd_gerar, "custo": cmd_custo}[args.cmd]
        return handler(args)
    except spend.NeedsConfirmation as exc:
        est = exc.estimate
        emit(args, {"precisa_confirmar": True, "estimativa": est},
             (f"Chamada paga: estimativa {money(est['total_usd'])} ({est['quantidade']:g} {est['unidade']}). "
              if est["total_usd"] is not None else
              "Chamada paga com preço por uso desconhecido no catálogo; o provedor informa o custo real depois. ")
             + "Peça o ok da pessoa e rode de novo com --confirmar.")
        return EXIT_CONFIRM
    except spend.OverBudget as exc:
        print(str(exc), file=sys.stderr)
        return EXIT_BUDGET
    except keys.MissingKey as exc:
        print(str(exc), file=sys.stderr)
        return EXIT_KEY
    except providers.Unsupported as exc:
        print(str(exc), file=sys.stderr)
        return EXIT_UNSUPPORTED
    except (http.HttpError, http.ContractError, TimeoutError, RuntimeError) as exc:
        print(f"Erro do provedor: {exc}", file=sys.stderr)
        return EXIT_PROVIDER
    except (KeyError, ValueError) as exc:
        print(str(exc).strip("'\""), file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
