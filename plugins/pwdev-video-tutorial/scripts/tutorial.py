#!/usr/bin/env python3
"""pwdev-video-tutorial · system tutorials and explainer videos (standard library only).

    tutorial.py codigo <raiz-do-codigo> [--saida codigo.json]        # routes, screens, forms, menus, permissions
    tutorial.py cobertura <codigo.json> --visitadas <urls.txt>         # code routes never reached on screen
    tutorial.py validar <roadmap.json|roteiro.json>                    # schema + order by prerequisites
    tutorial.py narrar <roteiro.json> --pasta <dir> [--voz pf_dora] [--velocidade 1.0] [--de-arquivos <dir>]
    tutorial.py script <roteiro.json> --pasta <dir>                    # Playwright code for playwright-cli run-code
    tutorial.py gravar <roteiro.json> --pasta <dir> [--sessao tutorial] [--estado auth.json] [--manter]
    tutorial.py montar <dir> --edit <edit> [--formato youtube-16x9]    # edit folder for the video plugins
    tutorial.py conferir <dir> [--roteiro roteiro.json]                # narration sync, masks, chapters
    tutorial.py texto <dir> --roteiro <roteiro.json> [--saida tutorial.md]

Everything shown comes from the real system: the code scan and the live navigation. Nothing is
invented, passwords never pass through here (the person logs in; the session is saved), and
personal data on screen is blurred by the `mascarar` selectors of the script.
"""
from __future__ import annotations

import argparse
import html
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

ROADMAP_SCHEMA = "pwdev-roadmap-videos/1"
ROTEIRO_SCHEMA = "pwdev-roteiro-tutorial/1"
CODIGO_SCHEMA = "pwdev-codigo-sistema/1"
CENAS_SCHEMA = "pwdev-cenas-tutorial/1"
HYPERFRAMES = "0.8.158"
SKIP_DIRS = {"node_modules", "vendor", ".git", "dist", "build", ".next", ".nuxt", "storage", "coverage",
             "__pycache__", ".venv", "venv", "target", "public/build", ".turbo", ".cache"}
CODE_EXT = {".php", ".js", ".jsx", ".ts", ".tsx", ".vue", ".py", ".rb", ".html", ".svelte"}
MAX_FILES = 6000
ACOES = {"ir", "clicar", "preencher", "pressionar", "passar", "selecionar", "rolar", "esperar", "destacar"}
LOCATOR_METHODS = {"Role", "Text", "Label", "Placeholder", "TestId", "Title", "AltText"}
LOCATOR_OPTIONS = {"name", "exact", "level", "checked", "disabled", "expanded", "includeHidden", "pressed", "selected"}
_JS_STR = r"'(?:[^'\\\n]|\\.)*'|\"(?:[^\"\\\n]|\\.)*\""
_JS_VALUE = rf"{_JS_STR}|true|false|-?\d+(?:\.\d+)?"
LOCATOR_RE = re.compile(rf"^getBy(\w+)\(\s*({_JS_STR})\s*(?:,\s*\{{(.*)\}}\s*)?\)$", re.S)
LOCATOR_OPT_RE = re.compile(rf"\s*(\w+)\s*:\s*({_JS_VALUE})\s*(?:,|$)")
PII_HINT = re.compile(r"(e-?mail|cpf|cnpj|telefone|celular|phone|senha|password|cart[aã]o|card|rg\b|endere[cç]o)", re.I)
TTS_VOICES = {"pf_dora": "feminina", "pm_alex": "masculina", "pm_santa": "masculina"}
FONT_PAUSE = 0.4  # seconds of breathing room after the narration of a scene
LONG_SILENCE = 3.0  # silent screen time after the narration that deserves a warning
GATE_SILENCE = 5.0  # longest pause the tutorial render gate accepts


def die(msg: str, code: int = 2) -> None:
    print(msg, file=sys.stderr)
    sys.exit(code)


def load(path: str | Path) -> dict:
    p = Path(path).expanduser()
    if not p.is_file():
        die(f"arquivo não encontrado: {p}")
    return json.loads(p.read_text(encoding="utf-8"))


def write_json(path: Path, data) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def tool(name: str) -> str:
    local = Path.home() / ".pwdev" / "bin" / name
    if local.is_file():
        return str(local)
    found = shutil.which(name)
    if not found:
        die(f"{name} não encontrado (skill vtut-setup).", 6)
    return found


# ============================================================================ code scan

ROUTE_PATTERNS = [
    ("laravel", re.compile(r"Route::(get|post|put|patch|delete|any|match|resource|apiResource|view)\(\s*['\"]([^'\"]+)['\"]"), ("metodo", "caminho")),
    ("express", re.compile(r"\b(?:app|router)\.(get|post|put|patch|delete)\(\s*['\"](/[^'\"]*)['\"]"), ("metodo", "caminho")),
    ("react-router", re.compile(r"<Route\b[^>]*\bpath=\{?['\"]([^'\"]+)['\"]"), ("caminho",)),
    ("router", re.compile(r"\bpath:\s*['\"](/?[\w\-/:*.\[\]]*)['\"]"), ("caminho",)),
    ("django", re.compile(r"\b(?:re_)?path\(\s*r?['\"]([^'\"]*)['\"]"), ("caminho",)),
    ("rails", re.compile(r"^\s*(get|post|put|patch|delete|resources|resource)\s+[:'\"]([\w/\-:]+)", re.M), ("metodo", "caminho")),
]
NAME_RE = re.compile(r"->name\(\s*['\"]([^'\"]+)['\"]")
LINK_RE = re.compile(r"<(?:a|Link|NuxtLink|router-link|RouterLink)\b[^>]*?(?:href|to)=\{?['\"]([^'\"{}]+)['\"]\}?[^>]*>\s*([^<{]{2,60}?)\s*</", re.S)
BLADE_LINK_RE = re.compile(r"<a\b[^>]*href=\"\{\{\s*route\(\s*'([^']+)'[^}]*\}\}\"[^>]*>\s*([^<{]{2,60}?)\s*</a>", re.S)
INPUT_RE = re.compile(r"<(?:input|select|textarea|Input|Select|Textarea)\b[^>]*?\bname=['\"{]+([\w\-\[\].]+)", re.S)
LABEL_RE = re.compile(r"<(?:label|Label)\b[^>]*>\s*([^<{]{2,60}?)\s*<", re.S)
BUTTON_RE = re.compile(r"<(?:button|Button)\b[^>]*>\s*([^<{]{2,40}?)\s*</", re.S)
PERM_PATTERNS = [
    re.compile(r"@can\(\s*['\"]([^'\"]+)['\"]"),
    re.compile(r"middleware\([^)]*can:([\w.\-]+)"),
    re.compile(r"Gate::define\(\s*['\"]([^'\"]+)['\"]"),
    re.compile(r"\b(?:hasRole|hasPermission|can|authorize)\(\s*['\"]([\w.\-:]+)['\"]"),
    re.compile(r"@(?:permission_required|login_required)\(\s*['\"]?([\w.\-]*)"),
]


def _walk(root: Path):
    count = 0
    for dirpath, dirnames, filenames in os.walk(root):
        rel_dir = Path(dirpath).relative_to(root).as_posix()
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS and f"{rel_dir}/{d}".lstrip("./") not in SKIP_DIRS
                       and not d.startswith(".")]
        for name in filenames:
            path = Path(dirpath) / name
            if path.suffix in CODE_EXT:
                count += 1
                if count > MAX_FILES:
                    return
                yield path


def _file_route(rel: str) -> tuple[str, str] | None:
    """Next.js / Nuxt / SvelteKit file-system routes."""
    m = re.match(r"^(?:src/)?app/(.*?)(?:/)?page\.(tsx|jsx|ts|js|mdx)$", rel)
    if m:
        kind = "nextjs-app"
    else:
        m = re.match(r"^(?:src/)?pages/(.*?)\.(tsx|jsx|ts|js|vue)$", rel)
        kind = "pages"
        if not m or m.group(1).startswith(("_", "api/")):
            m2 = re.match(r"^(?:src/)?routes/(.*?)/?\+page\.svelte$", rel)
            if not m2:
                return None
            m, kind = m2, "sveltekit"
    parts = [p for p in m.group(1).split("/") if p and not (p.startswith("(") and p.endswith(")"))]
    if parts and parts[-1] == "index":
        parts = parts[:-1]
    return kind, "/" + "/".join(parts)


def scan_code(root: str | Path) -> dict:
    root = Path(root).expanduser().resolve()
    if not root.is_dir():
        die(f"pasta não encontrada: {root}")
    routes, links, forms, perms, frameworks = [], [], [], set(), set()
    seen_routes = set()
    for path in _walk(root):
        rel = path.relative_to(root).as_posix()
        fr = _file_route(rel)
        if fr and (fr[0], fr[1]) not in seen_routes:
            seen_routes.add(fr)
            frameworks.add(fr[0])
            routes.append({"framework": fr[0], "metodo": "GET", "caminho": fr[1], "nome": None, "arquivo": rel, "linha": 1})
        try:
            text = path.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        if len(text) > 400_000:
            continue
        for fw, pattern, fields in ROUTE_PATTERNS:
            if fw == "django" and not rel.endswith("urls.py"):
                continue
            if fw == "rails" and not rel.endswith("routes.rb"):
                continue
            if fw == "router" and not re.search(r"(router|routes)", rel, re.I):
                continue
            if fw == "laravel" and not rel.startswith("routes/"):
                continue
            for m in pattern.finditer(text):
                groups = dict(zip(fields, m.groups()))
                line = text.count("\n", 0, m.start()) + 1
                tail = text[m.end():m.end() + 200]
                name = NAME_RE.search(tail.split(";")[0]) if fw == "laravel" else None
                caminho = groups["caminho"]
                if fw in ("django", "rails") and not caminho.startswith("/"):
                    caminho = "/" + caminho
                key = (fw, groups.get("metodo", "GET").upper(), caminho)
                if key in seen_routes:
                    continue
                seen_routes.add(key)
                frameworks.add({"router": "vue/js-router"}.get(fw, fw))
                routes.append({"framework": fw, "metodo": groups.get("metodo", "GET").upper(), "caminho": caminho,
                               "nome": name.group(1) if name else None, "arquivo": rel, "linha": line})
        for m in [*LINK_RE.finditer(text), *BLADE_LINK_RE.finditer(text)]:
            label = " ".join(m.group(2).split())
            if label and not label.startswith(("http", "{")):
                links.append({"texto": label, "destino": m.group(1), "arquivo": rel})
        fields = sorted(set(INPUT_RE.findall(text)))
        if fields:
            forms.append({"arquivo": rel, "campos": fields,
                          "rotulos": sorted({" ".join(x.split()) for x in LABEL_RE.findall(text)})[:30],
                          "botoes": sorted({" ".join(x.split()) for x in BUTTON_RE.findall(text)})[:20],
                          "dados_pessoais": [f for f in fields if PII_HINT.search(f)]})
        for pattern in PERM_PATTERNS:
            perms.update(x for x in pattern.findall(text) if x)
    dedup_links = list({(lk["texto"], lk["destino"]): lk for lk in links}.values())
    return {"schema": CODIGO_SCHEMA, "raiz": str(root), "frameworks": sorted(frameworks),
            "rotas": sorted(routes, key=lambda r: (r["caminho"], r["metodo"]))[:800],
            "links_menu": dedup_links[:400], "formularios": forms[:300], "permissoes": sorted(perms)[:200]}


def normalize_route(path: str) -> str:
    path = re.sub(r"https?://[^/]+", "", path.split("?")[0].split("#")[0]).rstrip("/") or "/"
    path = re.sub(r"\{[^}]+\}|:\w+|\[[^\]]+\]|<[^>]+>|\d+", "*", path)
    return path if path.startswith("/") else "/" + path


def coverage(code: dict, visited: list[str]) -> dict:
    seen = {normalize_route(u) for u in visited if u.strip()}
    pages = [r for r in code["rotas"] if r["metodo"] in ("GET", "VIEW", "RESOURCE") and "api" not in r["caminho"].split("/")[:2]]
    reached, missing = [], []
    for r in pages:
        (reached if normalize_route(r["caminho"]) in seen else missing).append(r["caminho"])
    return {"rotas_de_tela": len(pages), "alcancadas": sorted(set(reached)), "nao_alcancadas": sorted(set(missing)),
            "visitadas_fora_do_codigo": sorted(seen - {normalize_route(r["caminho"]) for r in pages})}


# ============================================================================ validation

def validate_roadmap(doc: dict) -> tuple[list[str], list[str]]:
    errors = []
    if doc.get("schema") != ROADMAP_SCHEMA:
        errors.append(f"schema deve ser {ROADMAP_SCHEMA}")
    videos = doc.get("videos") or []
    ids = [v.get("id") for v in videos]
    series = {s.get("id") for s in doc.get("series") or []}
    if len(ids) != len(set(ids)):
        errors.append("ids de vídeo repetidos")
    for v in videos:
        where = v.get("id", "?")
        for field in ("id", "titulo", "objetivo", "publico", "prioridade", "tipo", "duracao_alvo_s", "formato"):
            if not v.get(field):
                errors.append(f"{where}: falta '{field}'")
        if v.get("prioridade") not in ("P1", "P2", "P3"):
            errors.append(f"{where}: prioridade P1, P2 ou P3")
        if v.get("tipo") not in ("tutorial", "explicativo", "onboarding", "novidade", "demo"):
            errors.append(f"{where}: tipo tutorial, explicativo, onboarding, novidade ou demo")
        if v.get("serie") and v["serie"] not in series:
            errors.append(f"{where}: série '{v['serie']}' não declarada")
        for dep in v.get("prerequisitos") or []:
            if dep not in ids:
                errors.append(f"{where}: pré-requisito '{dep}' não existe")
    order, pending = [], {v["id"]: set(v.get("prerequisitos") or []) for v in videos if v.get("id")}
    rank = {"P1": 0, "P2": 1, "P3": 2}
    by_id = {v["id"]: v for v in videos if v.get("id")}
    while pending:
        ready = sorted([i for i, deps in pending.items() if not deps - set(order)],
                       key=lambda i: (rank.get(by_id[i].get("prioridade"), 9), i))
        if not ready:
            errors.append("pré-requisitos em ciclo: " + ", ".join(sorted(pending)))
            break
        order.append(ready[0])
        pending.pop(ready[0])
    return errors, order


def _js_literal(token: str):
    """Value of a JS string, boolean or number literal (only the forms the locator grammar allows)."""
    if token in ("true", "false"):
        return token == "true"
    if token[0] not in "'\"":
        return float(token) if "." in token else int(token)
    escapes = {"n": "\n", "t": "\t", "r": "\r", "0": "\0"}
    return re.sub(r"\\(.)", lambda m: escapes.get(m.group(1), m.group(1)), token[1:-1])


def parse_locator(alvo: str) -> tuple[str, str, dict] | None:
    """`getByX('text', { key: value })` as (method, text, options), or None when it is not exactly that.

    The script never pastes the locator text into the recording code: it is parsed here and
    re-emitted from these values, so a locator cannot carry code.
    """
    m = LOCATOR_RE.match(alvo.strip())
    if not m or m.group(1) not in LOCATOR_METHODS:
        return None
    options = {}
    body = (m.group(3) or "").strip()
    pos = 0
    while pos < len(body):
        opt = LOCATOR_OPT_RE.match(body, pos)
        if not opt or opt.end() == pos or opt.group(1) not in LOCATOR_OPTIONS:
            return None
        options[opt.group(1)] = _js_literal(opt.group(2))
        pos = opt.end()
    return "getBy" + m.group(1), _js_literal(m.group(2)), options


def validate_locator(alvo: str) -> str | None:
    if alvo.startswith("getBy"):
        return None if parse_locator(alvo) else f"localizador inválido: {alvo}"
    if any(c in alvo for c in "`\n;") or not alvo.strip():
        return f"seletor inválido: {alvo!r}"
    return None


def validate_script(doc: dict) -> list[str]:
    errors = []
    if doc.get("schema") != ROTEIRO_SCHEMA:
        errors.append(f"schema deve ser {ROTEIRO_SCHEMA}")
    if not str(doc.get("url_base", "")).startswith(("http://", "https://", "file://")):
        errors.append("url_base deve começar com http://, https:// ou file://")
    for sel in doc.get("mascarar") or []:
        if any(c in sel for c in "{}`;\n"):
            errors.append(f"mascarar: seletor inválido {sel!r}")
    cenas = doc.get("cenas") or []
    if not cenas:
        errors.append("roteiro sem cenas")
    ids = [c.get("id") for c in cenas]
    if len(ids) != len(set(ids)):
        errors.append("ids de cena repetidos")
    masked_fill = set(doc.get("mascarar") or [])
    for c in cenas:
        where = c.get("id", "?")
        if not str(c.get("narracao", "")).strip():
            errors.append(f"{where}: narração vazia")
        for n, a in enumerate(c.get("acoes") or []):
            tipo = a.get("tipo")
            if tipo not in ACOES:
                errors.append(f"{where}.acoes[{n}]: tipo deve ser um de {sorted(ACOES)}")
                continue
            if tipo in ("clicar", "preencher", "passar", "selecionar", "destacar"):
                problem = validate_locator(str(a.get("alvo", "")))
                if problem:
                    errors.append(f"{where}.acoes[{n}]: {problem}")
            if tipo in ("ir", "preencher", "pressionar", "selecionar") and a.get("valor") in (None, ""):
                errors.append(f"{where}.acoes[{n}]: '{tipo}' precisa de valor")
            if tipo == "preencher" and PII_HINT.search(str(a.get("alvo", ""))) and not a.get("ficticio") \
                    and a.get("alvo") not in masked_fill:
                errors.append(f"{where}.acoes[{n}]: campo de dado pessoal: use dado fictício (\"ficticio\": true) "
                              "ou ponha o seletor em mascarar")
    return errors


# ============================================================================ narration

def duration(path: Path) -> float:
    out = subprocess.run([tool("ffprobe"), "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0",
                          str(path)], capture_output=True, text=True)
    try:
        return round(float(out.stdout.strip()), 3)
    except ValueError:
        die(f"não consegui medir a duração de {path}", 5)


def tts_python() -> str:
    py = Path.home() / ".pwdev" / "venvs" / "tts" / "bin" / "python"
    if not py.is_file():
        die("TTS local não instalado: rode a skill vtut-setup (cria ~/.pwdev/venvs/tts com kokoro-onnx).", 6)
    return str(py)


def narrate(script: dict, folder: Path, voice: str, speed: float, from_dir: str | None) -> dict:
    out_dir = folder / "narracao"
    out_dir.mkdir(parents=True, exist_ok=True)
    result = {"voz": voice if not from_dir else "arquivos", "cenas": []}
    for c in script["cenas"]:
        target = out_dir / f"{c['id']}.wav"
        if from_dir:
            src = next((p for p in Path(from_dir).expanduser().glob(f"{c['id']}.*")), None)
            if not src:
                die(f"falta o áudio da cena {c['id']} em {from_dir} (nome: {c['id']}.wav/.mp3/.m4a)")
            subprocess.run([tool("ffmpeg"), "-v", "error", "-y", "-i", str(src), "-ac", "1", "-ar", "24000", str(target)],
                           check=True)
        else:
            npx = shutil.which("npx") or die("npx não encontrado (Node 22+).", 6)
            env = {**os.environ, "HYPERFRAMES_PYTHON": tts_python(), "HYPERFRAMES_NO_TELEMETRY": "1",
                   "DO_NOT_TRACK": "1", "PATH": str(Path.home() / ".pwdev" / "bin") + os.pathsep + os.environ.get("PATH", "")}
            text_file = out_dir / f"{c['id']}.txt"
            text_file.write_text(c["narracao"].strip(), encoding="utf-8")
            run = subprocess.run([npx, "--yes", f"hyperframes@{HYPERFRAMES}", "tts", str(text_file), "--voice", voice,
                                  "--lang", "pt-br", "--speed", str(speed), "-o", str(target), "--json"],
                                 capture_output=True, text=True, env=env)
            if run.returncode != 0 or not target.is_file():
                die("a narração falhou: " + (run.stdout + run.stderr).strip()[-400:], 5)
        result["cenas"].append({"id": c["id"], "arquivo": str(target), "duracao": duration(target)})
    write_json(folder / "narracao.json", result)
    return result


# ============================================================================ recording script

def _js(value) -> str:
    return json.dumps(value, ensure_ascii=False)


def _locator(alvo: str) -> str:
    if not alvo.startswith("getBy"):
        return f"page.locator({_js(alvo)})"
    parsed = parse_locator(alvo)
    if parsed is None:
        raise ValueError(f"localizador inválido: {alvo}")
    method, text, options = parsed
    return f"page.{method}({_js(text)}" + (f", {_js(options)})" if options else ")")


def _url(base: str, value: str) -> str:
    if re.match(r"^(https?|file)://", value):
        return value
    return base.rstrip("/") + "/" + value.lstrip("/")


def build_js(script: dict, folder: Path, narration: dict | None) -> str:
    errors = validate_script(script)
    if errors:  # never generate code from a roteiro that did not pass validation
        raise ValueError("roteiro com problemas: " + "; ".join(errors))
    vw = int((script.get("viewport") or {}).get("largura", 1920))
    vh = int((script.get("viewport") or {}).get("altura", 1080))
    durations = {c["id"]: c["duracao"] for c in (narration or {}).get("cenas", [])}
    mask_css = " ".join(f"{s} {{ filter: blur(8px) !important; }}" for s in script.get("mascarar") or [])
    video = (folder / "gravacao.webm").resolve()
    shots = (folder / "capturas").resolve()
    lines = [
        "async page => {",
        "  // Gerado por tutorial.py a partir do roteiro: edite o roteiro, não este arquivo.",
        f"  const MASK = {_js(mask_css)};",
        "  const log = { cenas: [] };",
        "  const boxOf = async loc => { try { return await loc.first().boundingBox(); } catch (e) { return null; } };",
        "  const mark = async (loc, note) => {",
        "    const b = await boxOf(loc); if (!b) return null;",
        "    const label = note ? `<div style=\"position:absolute;top:${b.y + b.height + 10}px;left:${b.x}px;max-width:520px;"
        "padding:10px 16px;background:#111;color:#fff;border-radius:10px;font:600 22px sans-serif\">${note}</div>` : '';",
        "    await page.screencast.showOverlay(`<div style=\"position:absolute;top:${b.y - 6}px;left:${b.x - 6}px;"
        "width:${b.width + 12}px;height:${b.height + 12}px;border:4px solid #FF6A00;border-radius:10px\"></div>${label}`,"
        " { duration: 900 });",
        "    return b;",
        "  };",
        "  if (MASK) {",
        "    await page.addInitScript(css => { const add = () => { const s = document.createElement('style');"
        " s.textContent = css; (document.head || document.documentElement).appendChild(s); };"
        " if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', add); else add(); }, MASK);",
        "  }",
        f"  await page.setViewportSize({{ width: {vw}, height: {vh} }});",
        f"  await page.screencast.start({{ path: {_js(str(video))}, size: {{ width: {vw}, height: {vh} }} }});",
        "  const t0 = Date.now();",
        "  const now = () => (Date.now() - t0) / 1000;",
    ]
    for c in script["cenas"]:
        need = float(durations.get(c["id"], 0)) + FONT_PAUSE
        lines += [f"  // cena {_js(str(c['id']))}", "  {", "    const cena = { id: " + _js(c["id"]) + ", inicio: now(), acoes: [] };"]
        if c.get("capitulo"):
            cap = c["capitulo"]
            lines.append(f"    await page.screencast.showChapter({_js(cap.get('titulo', ''))}, "
                         f"{{ description: {_js(cap.get('descricao', ''))}, duration: 1600 }});")
            lines.append("    cena.narracao_inicio = now();")
        else:
            lines.append("    cena.narracao_inicio = cena.inicio;")
        for a in c.get("acoes") or []:
            tipo, alvo, valor = a["tipo"], a.get("alvo"), a.get("valor")
            pausa = int(a.get("pausa", 700))
            if tipo == "ir":
                lines.append(f"    await page.goto({_js(_url(script['url_base'], str(valor)))}); "
                             "await page.waitForLoadState('networkidle').catch(() => {});")
                lines.append("    cena.acoes.push({ tipo: 'ir', t: now() });")
            elif tipo in ("clicar", "preencher", "passar", "selecionar", "destacar"):
                loc = _locator(alvo)
                lines.append(f"    {{ const loc = {loc}; await loc.first().scrollIntoViewIfNeeded().catch(() => {{}});")
                lines.append(f"      const box = await mark(loc, {_js(html.escape(str(a.get('nota', ''))))}); const t = now();")
                if tipo == "clicar":
                    lines.append("      await loc.first().click();")
                elif tipo == "preencher":
                    lines.append(f"      await loc.first().click(); await loc.first().pressSequentially({_js(str(valor))}, {{ delay: 55 }});")
                elif tipo == "passar":
                    lines.append("      await loc.first().hover();")
                elif tipo == "selecionar":
                    lines.append(f"      await loc.first().selectOption({_js(str(valor))});")
                elif tipo == "destacar":
                    lines.append("      await page.waitForTimeout(900);")
                lines.append(f"      cena.acoes.push({{ tipo: {_js(tipo)}, alvo: {_js(alvo)}, t, box }}); }}")
            elif tipo == "pressionar":
                lines.append(f"    await page.keyboard.press({_js(str(valor))}); cena.acoes.push({{ tipo: 'pressionar', t: now() }});")
            elif tipo == "rolar":
                lines.append(f"    await page.mouse.wheel(0, {int(valor or 400)}); cena.acoes.push({{ tipo: 'rolar', t: now() }});")
            elif tipo == "esperar":
                lines.append(f"    await page.waitForTimeout({int(valor or 1000)});")
            if tipo != "esperar":
                lines.append(f"    await page.waitForTimeout({pausa});")
        shot = (shots / f"{c['id']}.png")
        lines += [
            f"    const falta = cena.narracao_inicio + {need:.3f} - now();",
            "    if (falta > 0) await page.waitForTimeout(Math.round(falta * 1000));",
            f"    await page.screenshot({{ path: {_js(str(shot))} }});",
            "    cena.fim = now(); log.cenas.push(cena);",
            "  }",
        ]
    lines += ["  log.duracao = now();", "  await page.screencast.stop();", "  return JSON.stringify(log);", "}"]
    return "\n".join(lines) + "\n"


def run_cli(args: list[str], session: str) -> str:
    cli = shutil.which("playwright-cli") or die("playwright-cli não encontrado (skill vtut-setup).", 6)
    proc = subprocess.run([cli, f"-s={session}", *args], capture_output=True, text=True)
    if proc.returncode != 0 or "### Error" in proc.stdout:
        die(f"playwright-cli {' '.join(args[:1])} falhou: " + (proc.stdout + proc.stderr).strip()[-600:], 5)
    return proc.stdout


def record(script: dict, folder: Path, session: str, state: str | None, keep: bool) -> dict:
    narration = json.loads((folder / "narracao.json").read_text(encoding="utf-8")) if (folder / "narracao.json").is_file() else None
    (folder / "capturas").mkdir(parents=True, exist_ok=True)
    js = folder / "gravar.js"
    js.write_text(build_js(script, folder, narration), encoding="utf-8")
    run_cli(["open"], session)
    try:
        if state:
            run_cli(["state-load", str(Path(state).expanduser())], session)
        out = run_cli(["--raw", "run-code", f"--filename={js}"], session)
    finally:
        if not keep:
            subprocess.run([shutil.which("playwright-cli") or "playwright-cli", f"-s={session}", "close"], capture_output=True)
    raw = out.strip().splitlines()[-1]
    data = json.loads(json.loads(raw) if raw.startswith('"') else raw)
    doc = {"schema": CENAS_SCHEMA, "video": str(folder / "gravacao.webm"), "duracao": data["duracao"],
           "viewport": script.get("viewport") or {"largura": 1920, "altura": 1080}, "cenas": data["cenas"],
           "narracao": bool(narration)}
    write_json(folder / "cenas.json", doc)
    return {"video": doc["video"], "duracao": round(doc["duracao"], 2), "cenas": len(doc["cenas"])}


# ============================================================================ assembly

def words_from_text(text: str, start: float, length: float) -> list[dict]:
    """Even spread by character count: only a fallback when no transcription is available."""
    words = text.split()
    total = sum(len(w) + 1 for w in words) or 1
    t, out = start, []
    for w in words:
        d = length * (len(w) + 1) / total
        out.append({"w": w, "inicio": round(t, 3), "fim": round(t + d * 0.92, 3), "p": 0.5})
        t += d
    return out


def assemble(folder: Path, edit: Path, formato: str, script: dict | None, transcribe: bool) -> dict:
    cenas = load(folder / "cenas.json")
    narration = load(folder / "narracao.json") if (folder / "narracao.json").is_file() else {"cenas": []}
    narr_by_id = {c["id"]: c for c in narration["cenas"]}
    edit.mkdir(parents=True, exist_ok=True)
    fmt = json.loads(subprocess.run([tool("pwdev-media"), "--json", "formatos", "mostrar", formato],
                                    capture_output=True, text=True).stdout or "{}")
    w, h = fmt.get("largura", 1920), fmt.get("altura", 1080)
    inputs, filters, mix = ["-i", str(cenas["video"])], [], []
    for n, c in enumerate(cenas["cenas"]):
        narr = narr_by_id.get(c["id"])
        if not narr:
            continue
        inputs += ["-i", narr["arquivo"]]
        delay = int(round(c.get("narracao_inicio", c["inicio"]) * 1000))
        filters.append(f"[{len(mix) + 1}:a]aresample=48000,adelay={delay}|{delay}[n{len(mix)}]")
        mix.append(f"[n{len(mix)}]")
    vf = (f"[0:v]scale={w}:{h}:force_original_aspect_ratio=decrease,pad={w}:{h}:(ow-iw)/2:(oh-ih)/2:color=white,"
          f"fps=30,format=yuv420p[v]")
    graph = ";".join([vf, *filters] + ([f"{''.join(mix)}amix=inputs={len(mix)}:normalize=0,loudnorm=I=-16:TP=-1.5[a]"]
                                       if mix else []))
    out = edit / "cut.mp4"
    cmd = [tool("ffmpeg"), "-v", "error", "-y", *inputs, "-filter_complex", graph, "-map", "[v]"]
    cmd += ["-map", "[a]", "-c:a", "aac", "-b:a", "192k"] if mix else ["-an"]
    cmd += ["-c:v", "libx264", "-preset", "veryfast", "-crf", "18", "-t", f"{cenas['duracao']:.3f}",
            "-movflags", "+faststart", str(out)]
    subprocess.run(cmd, check=True)
    total = duration(out)
    words, source = [], "texto"
    if transcribe and mix:
        trans = subprocess.run([tool("pwdev-media"), "--json", "video", "transcrever", str(out), "--edit", str(edit / "_narracao")],
                               capture_output=True, text=True)
        if trans.returncode == 0:
            words = json.loads((edit / "_narracao" / "transcricao.json").read_text(encoding="utf-8"))["palavras"]
            source = "transcricao"
    if not words and script:
        for c in cenas["cenas"]:
            narr = narr_by_id.get(c["id"])
            text = next((s["narracao"] for s in script["cenas"] if s["id"] == c["id"]), "")
            if narr and text:
                words += words_from_text(text, c.get("narracao_inicio", c["inicio"]), narr["duracao"])
    timeline = {"schema": "pwdev-corte/1", "fonte": str(out), "duracao": total,
                "segmentos": [{"src_inicio": 0.0, "src_fim": total, "dst_inicio": 0.0, "dst_fim": total}],
                "palavras": words, "origem_palavras": source}
    write_json(edit / "cut_timeline.json", timeline)
    subprocess.run([tool("pwdev-media"), "video", "legendas", str(edit)], capture_output=True, check=False)
    vw = cenas["viewport"].get("largura", 1920)
    vh = cenas["viewport"].get("altura", 1080)
    blocos, textos = [], []
    for c in cenas["cenas"]:
        clicks = [a for a in c["acoes"] if a.get("box") and a["tipo"] in ("clicar", "preencher", "selecionar", "destacar")]
        if clicks:
            b = clicks[0]["box"]
            ox = min(max((b["x"] + b["width"] / 2) / vw * 100, 10), 90)
            oy = min(max((b["y"] + b["height"] / 2) / vh * 100, 10), 90)
            start = max(clicks[0]["t"] - 0.4, c["inicio"])
            blocos.append({"inicio": round(start, 3), "fim": round(c["fim"], 3), "tipo": "tela_cheia", "zoom": 1.25,
                           "origem": f"{ox:.0f}% {oy:.0f}%"})
            blocos.append({"inicio": round(c["fim"], 3), "fim": round(min(c["fim"] + 0.5, total), 3),
                           "tipo": "tela_cheia", "zoom": 1.0})
    blocos = [b for b in blocos if b["fim"] - b["inicio"] > 0.05 and b["fim"] <= total + 0.05]
    # Tutorials run over light interfaces: captions on a dark band, low in the frame.
    write_json(folder / "sugestoes-projeto.json", {"blocos": blocos, "textos": textos, "formato": formato,
                                                   "legenda": {"ativa": True, "estilo": "caixa", "max_palavras": 6, "y": 0.88}})
    return {"cut": str(out), "duracao": total, "palavras": len(words), "origem_palavras": source,
            "zooms": sum(1 for b in blocos if b["zoom"] > 1)}


def check_tutorial(folder: Path, script: dict | None) -> dict:
    cenas = load(folder / "cenas.json")
    narration = load(folder / "narracao.json") if (folder / "narracao.json").is_file() else {"cenas": []}
    narr = {c["id"]: c["duracao"] for c in narration["cenas"]}
    problems, warnings = [], []
    for c in cenas["cenas"]:
        d = narr.get(c["id"])
        if d is None:
            warnings.append(f"{c['id']}: sem narração")
            continue
        end = c.get("narracao_inicio", c["inicio"]) + d
        if end > c["fim"] + 0.3:
            problems.append(f"{c['id']}: a narração ({d:.1f}s) passa do fim da cena em {end - c['fim']:.1f}s")
        for a in c["acoes"]:
            if a["t"] < c["inicio"] - 0.05:
                problems.append(f"{c['id']}: ação '{a['tipo']}' antes do início da cena")
        if c["fim"] - end > LONG_SILENCE:
            warnings.append(f"{c['id']}: {c['fim'] - end:.1f}s de tela sem fala depois da narração; "
                            "divida a narração ou descreva as ações enquanto acontecem")
    if script:
        ids = [c["id"] for c in script["cenas"]]
        if ids != [c["id"] for c in cenas["cenas"]]:
            problems.append("as cenas gravadas não batem com as do roteiro (regrave)")
        for c in script["cenas"]:
            for a in c.get("acoes") or []:
                if a.get("tipo") == "preencher" and PII_HINT.search(str(a.get("alvo", ""))) and not a.get("ficticio") \
                        and a.get("alvo") not in (script.get("mascarar") or []):
                    problems.append(f"{c['id']}: dado pessoal digitado sem máscara nem marca de fictício")
    missing_shots = [c["id"] for c in cenas["cenas"] if not (folder / "capturas" / f"{c['id']}.png").is_file()]
    if missing_shots:
        warnings.append("sem captura: " + ", ".join(missing_shots))
    return {"veredito": "PASSOU" if not problems else "REPROVOU", "problemas": problems, "avisos": warnings}


def markdown_tutorial(folder: Path, script: dict) -> str:
    lines = [f"# {script.get('titulo', 'Tutorial')}", ""]
    if script.get("resumo"):
        lines += [script["resumo"], ""]
    step = 0
    for c in script["cenas"]:
        if c.get("capitulo"):
            lines += [f"## {c['capitulo']['titulo']}", ""]
        step += 1
        lines += [f"**{step}.** {c['narracao'].strip()}", ""]
        shot = folder / "capturas" / f"{c['id']}.png"
        if shot.is_file():
            lines += [f"![{c['id']}](capturas/{c['id']}.png)", ""]
    return "\n".join(lines)


# ============================================================================ CLI

def main(argv: list[str]) -> int:
    p = argparse.ArgumentParser(prog="tutorial.py", description="pwdev-video-tutorial")
    sub = p.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("codigo")
    s.add_argument("raiz")
    s.add_argument("--saida")
    s = sub.add_parser("cobertura")
    s.add_argument("codigo")
    s.add_argument("--visitadas", required=True)
    s = sub.add_parser("validar")
    s.add_argument("arquivo")
    s = sub.add_parser("narrar")
    s.add_argument("roteiro")
    s.add_argument("--pasta", required=True)
    s.add_argument("--voz", default="pf_dora")
    s.add_argument("--velocidade", type=float, default=1.0)
    s.add_argument("--de-arquivos")
    s = sub.add_parser("script")
    s.add_argument("roteiro")
    s.add_argument("--pasta", required=True)
    s = sub.add_parser("gravar")
    s.add_argument("roteiro")
    s.add_argument("--pasta", required=True)
    s.add_argument("--sessao", default="pwdev-tutorial")
    s.add_argument("--estado")
    s.add_argument("--manter", action="store_true")
    s = sub.add_parser("montar")
    s.add_argument("pasta")
    s.add_argument("--edit", required=True)
    s.add_argument("--formato", default="youtube-16x9")
    s.add_argument("--roteiro")
    s.add_argument("--sem-transcricao", action="store_true")
    s = sub.add_parser("conferir")
    s.add_argument("pasta")
    s.add_argument("--roteiro")
    s = sub.add_parser("texto")
    s.add_argument("pasta")
    s.add_argument("--roteiro", required=True)
    s.add_argument("--saida")
    a = p.parse_args(argv)

    if a.cmd == "codigo":
        doc = scan_code(a.raiz)
        out = Path(a.saida).expanduser() if a.saida else None
        if out:
            write_json(out, doc)
        print(json.dumps({"frameworks": doc["frameworks"], "rotas": len(doc["rotas"]), "links_menu": len(doc["links_menu"]),
                          "formularios": len(doc["formularios"]), "permissoes": len(doc["permissoes"]),
                          "arquivo": str(out) if out else None} if out else doc, ensure_ascii=False, indent=2))
        return 0
    if a.cmd == "cobertura":
        visited = Path(a.visitadas).expanduser().read_text(encoding="utf-8").splitlines()
        print(json.dumps(coverage(load(a.codigo), visited), ensure_ascii=False, indent=2))
        return 0
    if a.cmd == "validar":
        doc = load(a.arquivo)
        if doc.get("schema") == ROADMAP_SCHEMA:
            errors, order = validate_roadmap(doc)
            print(json.dumps({"erros": errors, "ordem": order}, ensure_ascii=False, indent=2))
        else:
            errors = validate_script(doc)
            print(json.dumps({"erros": errors}, ensure_ascii=False, indent=2))
        return 1 if errors else 0
    if a.cmd in ("narrar", "script", "gravar", "texto"):
        script = load(a.roteiro)
        errors = validate_script(script)
        if errors:
            die("roteiro com problemas:\n- " + "\n- ".join(errors), 1)
    if a.cmd == "narrar":
        if not a.de_arquivos and a.voz not in TTS_VOICES:
            die(f"voz local deve ser uma de {sorted(TTS_VOICES)} (ou use --de-arquivos)")
        r = narrate(script, Path(a.pasta).expanduser(), a.voz, a.velocidade, a.de_arquivos)
        print(json.dumps({"cenas": len(r["cenas"]), "total_s": round(sum(c["duracao"] for c in r["cenas"]), 2),
                          "voz": r["voz"]}, ensure_ascii=False, indent=2))
        return 0
    if a.cmd == "script":
        folder = Path(a.pasta).expanduser()
        narration = load(folder / "narracao.json") if (folder / "narracao.json").is_file() else None
        out = folder / "gravar.js"
        folder.mkdir(parents=True, exist_ok=True)
        out.write_text(build_js(script, folder, narration), encoding="utf-8")
        print(out)
        return 0
    if a.cmd == "gravar":
        print(json.dumps(record(script, Path(a.pasta).expanduser(), a.sessao, a.estado, a.manter), ensure_ascii=False, indent=2))
        return 0
    if a.cmd == "montar":
        script = load(a.roteiro) if a.roteiro else None
        r = assemble(Path(a.pasta).expanduser(), Path(a.edit).expanduser(), a.formato, script, not a.sem_transcricao)
        print(json.dumps(r, ensure_ascii=False, indent=2))
        return 0
    if a.cmd == "conferir":
        r = check_tutorial(Path(a.pasta).expanduser(), load(a.roteiro) if a.roteiro else None)
        print(json.dumps(r, ensure_ascii=False, indent=2))
        return 0 if r["veredito"] == "PASSOU" else 1
    if a.cmd == "texto":
        text = markdown_tutorial(Path(a.pasta).expanduser(), script)
        out = Path(a.saida).expanduser() if a.saida else Path(a.pasta).expanduser() / "tutorial.md"
        out.write_text(text, encoding="utf-8")
        print(out)
        return 0
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
