"""ffmpeg/ffprobe: find them, install them without sudo, and run them.

Installation uses the public `static-ffmpeg` package (MIT) through `uv run --with`, so nothing is
added to any Python environment, and links the binaries into ~/.pwdev/bin.
"""
from __future__ import annotations

import json
import os
import shutil
import subprocess
from pathlib import Path


class MissingTool(RuntimeError):
    pass


def bin_dir() -> Path:
    path = Path(os.environ.get("PWDEV_BIN") or Path.home() / ".pwdev" / "bin").expanduser()
    return path


def find(tool: str) -> str | None:
    local = bin_dir() / tool
    if local.is_file() and os.access(local, os.X_OK):
        return str(local)
    return shutil.which(tool)


def need(tool: str) -> str:
    path = find(tool)
    if not path:
        raise MissingTool(f"{tool} não encontrado. Instale com `pwdev-media video ffmpeg --instalar` "
                          "(sem sudo, uns 30 segundos).")
    return path


INSTALL_SCRIPT = (
    "import json; from static_ffmpeg import run; "
    "a, b = run.get_or_fetch_platform_executables_else_raise(); print(json.dumps([a, b]))"
)


def install() -> dict:
    uv = shutil.which("uv")
    if not uv:
        fallback = Path.home() / ".local" / "bin" / "uv"
        if not fallback.exists():
            raise MissingTool("uv não encontrado; instale o uv primeiro (veja o media-setup)")
        uv = str(fallback)
    result = subprocess.run([uv, "run", "--no-project", "--with", "static-ffmpeg", "python", "-c", INSTALL_SCRIPT],
                            capture_output=True, text=True, timeout=900)
    if result.returncode != 0:
        raise MissingTool("o download do ffmpeg falhou: " + result.stderr.strip()[-400:])
    ffmpeg, ffprobe = json.loads(result.stdout.strip().splitlines()[-1])
    target = bin_dir()
    target.mkdir(parents=True, exist_ok=True)
    for name, src in (("ffmpeg", ffmpeg), ("ffprobe", ffprobe)):
        # Copy, not link: the source lives in uv's cache, which `uv cache clean` may remove.
        dest = target / name
        if dest.is_symlink() or dest.exists():
            dest.unlink()
        shutil.copy2(src, dest)
        dest.chmod(0o755)
    return {"ffmpeg": str(target / "ffmpeg"), "ffprobe": str(target / "ffprobe"), "pasta": str(target),
            "no_path": str(target) in os.environ.get("PATH", "").split(os.pathsep)}


def run(args: list[str], timeout: float = 3600) -> subprocess.CompletedProcess:
    tool = need(args[0])
    result = subprocess.run([tool, *args[1:]], capture_output=True, timeout=timeout)
    if result.returncode != 0:
        tail = result.stderr.decode("utf-8", "replace").strip()[-600:]
        raise RuntimeError(f"{args[0]} falhou: {tail}")
    return result


def probe(path: str | Path) -> dict:
    out = run(["ffprobe", "-v", "error", "-print_format", "json", "-show_format", "-show_streams", str(path)])
    data = json.loads(out.stdout)
    video = next((s for s in data.get("streams", []) if s.get("codec_type") == "video"), None)
    audio = next((s for s in data.get("streams", []) if s.get("codec_type") == "audio"), None)
    info = {"arquivo": str(path), "duracao": float(data["format"].get("duration", 0.0)),
            "video": None, "audio": None}
    if video:
        num, _, den = (video.get("avg_frame_rate") or "0/1").partition("/")
        fps = float(num) / float(den or 1) if float(den or 1) else 0.0
        rotation = 0
        for side in video.get("side_data_list", []) or []:
            rotation = int(side.get("rotation", rotation) or 0)
        w, h = int(video["width"]), int(video["height"])
        if abs(rotation) in (90, 270):
            w, h = h, w
        info["video"] = {"largura": w, "altura": h, "fps": round(fps, 3), "codec": video.get("codec_name")}
    if audio:
        info["audio"] = {"taxa": int(audio.get("sample_rate", 0)), "canais": int(audio.get("channels", 0)),
                         "codec": audio.get("codec_name")}
    return info
