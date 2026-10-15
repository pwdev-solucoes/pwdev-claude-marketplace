#!/usr/bin/env python3
"""pwdev-video-remotion · project builder (standard library only).

Reads projeto.json (schema pwdev-projeto-video/1, shared with pwdev-video-hyperframes), asks the
pwdev-media core for the resolved render plan, copies media into public/ and writes
src/dados.json and src/cenas.generated.ts. The React code in src/ renders it.

    python3 build.py novo <pasta-do-projeto> --edit <pasta-edit> [--formato reels-9x16] [--nome x]
    python3 build.py instalar               # npm install (versões fixas do package.json)
    python3 build.py montar                 # dados.json from projeto.json (respects "amostra")
    python3 build.py amostra <inicio> <fim> # only that stretch (seconds on the cut)
    python3 build.py completo               # clear the sample
    python3 build.py checar                 # TypeScript + composition listing
    python3 build.py quadro <segundo>       # PNG of one frame in renders/quadros/
    python3 build.py estudio [--parar|--status]
    python3 build.py rm <args...>           # pinned Remotion CLI in this project
    python3 build.py render [--max-silencio s] [--qualidade rascunho|padrao|alta]

Times come from the measured cut; nothing here estimates a time.
"""
from __future__ import annotations

import json
import os
import re
import shutil
import signal
import subprocess
import sys
from pathlib import Path

REMOTION = "4.0.535"   # pinned in package.json too: the same project re-renders identically
HERE = Path(__file__).resolve().parent
COMPOSITION = "Principal"
ENTRY = "src/index.ts"
STUDIO_PORT = "3123"
TEMPLATE_FILES = ("build.py", "package.json", "tsconfig.json", "remotion.config.ts", "src", "public/fonts",
                  "compositions")
CRF = {"rascunho": "28", "padrao": "18", "alta": "14"}


# ---------------------------------------------------------------------------- helpers

def die(msg: str, code: int = 2) -> None:
    print(msg, file=sys.stderr)
    sys.exit(code)


def media_cli() -> str:
    found = shutil.which("pwdev-media") or str(Path.home() / ".local" / "bin" / "pwdev-media")
    if not Path(found).exists():
        die("pwdev-media não encontrado: instale o núcleo (pwdev-media, skill media-setup).", 6)
    return found


def media(*args: str) -> dict:
    result = subprocess.run([media_cli(), "--json", *args], capture_output=True, text=True)
    if result.returncode not in (0, 1):
        die(result.stderr.strip() or result.stdout.strip(), result.returncode)
    return json.loads(result.stdout)


def npx() -> str:
    return shutil.which("npx") or die("npx não encontrado: instale o Node 20+ (skill vrm-setup).", 6)


def remotion(args: list[str], check: bool = True, **kwargs) -> int:
    if not (HERE / "node_modules" / "remotion").is_dir():
        die("dependências não instaladas: rode `python3 build.py instalar`.", 6)
    code = subprocess.run([npx(), "--no-install", "remotion", *args], cwd=HERE, **kwargs).returncode
    if check and code != 0:
        sys.exit(code)
    return code


def load_project() -> dict:
    path = HERE / "projeto.json"
    if not path.is_file():
        die("projeto.json não existe: crie o projeto com `build.py novo`.")
    return json.loads(path.read_text(encoding="utf-8"))


def save_project(proj: dict) -> None:
    (HERE / "projeto.json").write_text(json.dumps(proj, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def safe_name(name: str) -> str:
    stem, dot, ext = name.rpartition(".")
    clean = re.sub(r"[^a-z0-9_-]+", "-", (stem or ext).lower()).strip("-") or "arquivo"
    return f"{clean}.{re.sub(r'[^a-z0-9]+', '', ext.lower())}" if dot else clean


def publish(src: str, dest_rel: str) -> str:
    """Copy a media file into public/ (only when it changed) and return its public-relative path."""
    source, dest = Path(src).expanduser(), HERE / "public" / dest_rel
    if not source.is_file():
        die(f"arquivo não encontrado: {source}", 2)
    dest.parent.mkdir(parents=True, exist_ok=True)
    if not dest.exists() or dest.stat().st_size != source.stat().st_size or dest.stat().st_mtime < source.stat().st_mtime:
        shutil.copy2(source, dest)
    return dest_rel


# ---------------------------------------------------------------------------- build

def scenes_module(plan: dict) -> str:
    srcs = sorted({c["src"] for c in plan["cenas"]})
    lines = ["// Gerado por build.py a partir de projeto.json (\"cenas\"). Não edite à mão.",
             "import type {CenaComponent} from './tipos';"]
    for n, src in enumerate(srcs):
        if not src.endswith(".tsx"):
            die(f"cena {src}: no Remotion as cenas são .tsx (cenas .html são do HyperFrames).", 1)
        if not (HERE / src).is_file():
            die(f"cena {src} não existe em compositions/.", 1)
        lines.append(f"import Cena{n} from '../{src[:-4]}';")
    lines += ["", "export const CENAS: Record<string, CenaComponent> = {"]
    lines += [f"  {json.dumps(src)}: Cena{n}," for n, src in enumerate(srcs)]
    lines.append("};")
    return "\n".join(lines) + "\n"


def build(proj: dict) -> dict:
    plan = media("video", "plano-render", str(HERE / "projeto.json"))
    plan["video"]["arquivo"] = publish(plan["video"]["arquivo"], "cut.mp4")
    if plan["audio"]["trilha"]:
        t = plan["audio"]["trilha"]
        t["arquivo"] = publish(t["arquivo"], f"audio/{safe_name(Path(t['arquivo']).name)}")
    for e in plan["audio"]["efeitos"]:
        e["arquivo"] = publish(e["arquivo"], f"audio/{safe_name(Path(e['arquivo']).name)}")
    module = scenes_module(plan)
    (HERE / "src" / "cenas.generated.ts").write_text(module, encoding="utf-8")
    (HERE / "src" / "dados.json").write_text(json.dumps(plan, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    return {"dados": str(HERE / "src" / "dados.json"), "duracao": plan["duracao"], "amostra": plan["amostra"],
            "legendas": len(plan["cues"]), "textos": len(plan["textos"]), "cenas": len(plan["cenas"])}


# ---------------------------------------------------------------------------- commands

def cmd_novo(argv: list[str]) -> None:
    import argparse
    p = argparse.ArgumentParser(prog="build.py novo")
    p.add_argument("destino")
    p.add_argument("--edit", required=True)
    p.add_argument("--formato", default="reels-9x16")
    p.add_argument("--nome")
    a = p.parse_args(argv)
    dest = Path(a.destino).expanduser().resolve()
    if (dest / "projeto.json").exists():
        die(f"{dest} já é um projeto: reabra com `python3 {dest / 'build.py'} estudio`.")
    edit = Path(a.edit).expanduser().resolve()
    if dest == edit or edit in dest.parents:
        die("o projeto fica ao lado da pasta edit, não dentro dela.")
    dest.mkdir(parents=True, exist_ok=True)
    for rel in TEMPLATE_FILES:
        src, out = HERE / rel, dest / rel
        out.parent.mkdir(parents=True, exist_ok=True)
        if src.is_dir():
            shutil.copytree(src, out, dirs_exist_ok=True, ignore=shutil.ignore_patterns("node_modules"))
        else:
            shutil.copy2(src, out)
    (dest / "renders").mkdir(exist_ok=True)
    nome = a.nome or dest.name
    result = subprocess.run([media_cli(), "--json", "video", "projeto", str(dest / "projeto.json"), "--novo",
                             "--edit", str(edit), "--formato", a.formato, "--nome", nome], capture_output=True, text=True)
    if result.returncode not in (0, 1):
        die(result.stderr.strip())
    print(f"Projeto criado em {dest}. Próximos passos: python3 '{dest / 'build.py'}' instalar, depois montar.")


def cmd_instalar() -> None:
    npm = shutil.which("npm") or die("npm não encontrado: instale o Node 20+ (skill vrm-setup).", 6)
    code = subprocess.run([npm, "install", "--no-audit", "--no-fund", "--save-exact"], cwd=HERE).returncode
    sys.exit(code)


def cmd_checar() -> None:
    build(load_project())
    code = subprocess.run([npx(), "--no-install", "tsc", "--noEmit"], cwd=HERE).returncode
    if code != 0:
        die("TypeScript reprovou: corrija as cenas em compositions/ ou o src/.", 1)
    remotion(["compositions", ENTRY])
    print("Projeto confere: TypeScript ok e composição Principal encontrada.")


def cmd_quadro(argv: list[str]) -> None:
    if len(argv) != 1:
        die("uso: build.py quadro <segundo>")
    plan = json.loads((HERE / "src" / "dados.json").read_text(encoding="utf-8"))
    frame = min(int(round(float(argv[0]) * plan["fps"])), max(int(round(plan["duracao"] * plan["fps"])) - 1, 0))
    out = HERE / "renders" / "quadros" / f"quadro-{frame:05d}.png"
    out.parent.mkdir(parents=True, exist_ok=True)
    remotion(["still", ENTRY, COMPOSITION, str(out), f"--frame={frame}"])
    print(out)


def studio_pid() -> Path:
    return HERE / ".pwdev" / "estudio.pid"


def cmd_estudio(argv: list[str]) -> None:
    pid_file = studio_pid()
    running = None
    if pid_file.is_file():
        running = int(pid_file.read_text())
        try:
            os.kill(running, 0)
        except OSError:
            running = None
    if "--status" in argv:
        print(f"Estúdio no ar em http://localhost:{STUDIO_PORT} (pid {running})" if running else "Estúdio parado.")
        return
    if "--parar" in argv:
        if running:
            os.killpg(os.getpgid(running), signal.SIGTERM) if hasattr(os, "killpg") else os.kill(running, signal.SIGTERM)
        pid_file.unlink(missing_ok=True)
        print("Estúdio parado.")
        return
    build(load_project())
    if running:
        print(f"Estúdio já no ar em http://localhost:{STUDIO_PORT}: ele recarrega sozinho.")
        return
    if not (HERE / "node_modules" / "remotion").is_dir():
        die("dependências não instaladas: rode `python3 build.py instalar`.", 6)
    pid_file.parent.mkdir(exist_ok=True)
    log = open(HERE / ".pwdev" / "estudio.log", "ab")
    proc = subprocess.Popen([npx(), "--no-install", "remotion", "studio", ENTRY, "--port", STUDIO_PORT, "--no-open"],
                            cwd=HERE, stdout=log, stderr=log, start_new_session=True)
    pid_file.write_text(str(proc.pid))
    print(f"Estúdio abrindo em http://localhost:{STUDIO_PORT} (pare com `build.py estudio --parar`).")


def cmd_render(argv: list[str]) -> None:
    quality = argv[argv.index("--qualidade") + 1] if "--qualidade" in argv else "padrao"
    if quality not in CRF:
        die(f"qualidade deve ser uma de {sorted(CRF)}")
    proj = load_project()
    info = build(proj)
    name = proj["nome"] + ("-amostra" if info["amostra"] else "")
    out = HERE / "renders" / f"{name}.mp4"
    remotion(["render", ENTRY, COMPOSITION, str(out), "--codec=h264", f"--crf={CRF[quality]}"])
    args = ["video", "portao", str(out)]
    if "--max-silencio" in argv:  # tutorials: pauses while the screen loads are expected
        args += ["--max-silencio", argv[argv.index("--max-silencio") + 1]]
    if not info["amostra"]:
        args += ["--edit", proj["edit"]]
    gate = media(*args)
    print(json.dumps({"arquivo": str(out), "veredito": gate["veredito"], "problemas": gate["problemas"],
                      "avisos": gate["avisos"]}, ensure_ascii=False, indent=2))
    sys.exit(0 if gate["veredito"] == "PASSOU" else 1)


def main(argv: list[str]) -> None:
    if not argv:
        die(__doc__)
    cmd, rest = argv[0], argv[1:]
    if cmd == "novo":
        cmd_novo(rest)
    elif cmd == "instalar":
        cmd_instalar()
    elif cmd == "montar":
        print(json.dumps(build(load_project()), ensure_ascii=False, indent=2))
    elif cmd == "amostra":
        if len(rest) != 2:
            die("uso: build.py amostra <inicio> <fim>")
        a, b = float(rest[0]), float(rest[1])
        if not 0 < b - a <= 30:
            die("a amostra tem de 8 a 15 s (máximo 30).")
        proj = load_project()
        proj["amostra"] = {"inicio": a, "fim": b}
        save_project(proj)
        print(json.dumps(build(proj), ensure_ascii=False, indent=2))
    elif cmd == "completo":
        proj = load_project()
        proj["amostra"] = None
        save_project(proj)
        print(json.dumps(build(proj), ensure_ascii=False, indent=2))
    elif cmd == "checar":
        cmd_checar()
    elif cmd == "quadro":
        cmd_quadro(rest)
    elif cmd == "estudio":
        cmd_estudio(rest)
    elif cmd == "rm":
        sys.exit(remotion(rest, check=False))
    elif cmd == "render":
        cmd_render(rest)
    else:
        die(__doc__)


if __name__ == "__main__":
    main(sys.argv[1:])
