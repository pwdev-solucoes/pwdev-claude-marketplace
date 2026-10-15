"""Optional monthly schedule for `pwdev-media catalogo atualizar`.

macOS: a LaunchAgent (day 1, 09:00). Elsewhere: the crontab / Task Scheduler line is printed
for the person to add. Nothing is installed without `instalar=True`.
"""
from __future__ import annotations

import platform
import shutil
import subprocess
from pathlib import Path

LABEL = "br.com.pwdev.media.catalogo"


def command() -> list[str]:
    exe = shutil.which("pwdev-media") or "pwdev-media"
    return [exe, "catalogo", "atualizar"]


def plist() -> str:
    args = "".join(f"<string>{a}</string>" for a in command())
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0"><dict>
  <key>Label</key><string>{LABEL}</string>
  <key>ProgramArguments</key><array>{args}</array>
  <key>StartCalendarInterval</key><dict><key>Day</key><integer>1</integer><key>Hour</key><integer>9</integer></dict>
  <key>StandardOutPath</key><string>/tmp/{LABEL}.log</string>
  <key>StandardErrorPath</key><string>/tmp/{LABEL}.log</string>
</dict></plist>
"""


def plan() -> dict:
    system = platform.system()
    cmd = " ".join(command())
    if system == "Darwin":
        path = Path.home() / "Library" / "LaunchAgents" / f"{LABEL}.plist"
        return {"sistema": "macOS", "arquivo": str(path), "conteudo": plist()}
    if system == "Windows":
        return {"sistema": "Windows",
                "comando": f'schtasks /Create /SC MONTHLY /D 1 /ST 09:00 /TN "pwdev-media catalogo" /TR "{cmd}"'}
    return {"sistema": system, "comando": f'(crontab -l; echo "0 9 1 * * {cmd}") | crontab -'}


def install() -> str:
    info = plan()
    if info["sistema"] != "macOS":
        return f"Rode este comando para agendar: {info['comando']}"
    path = Path(info["arquivo"])
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(info["conteudo"], encoding="utf-8")
    subprocess.run(["launchctl", "unload", str(path)], capture_output=True)
    subprocess.run(["launchctl", "load", str(path)], check=True, capture_output=True)
    return f"Agendado: todo dia 1, às 09:00 ({path})."


def uninstall() -> str:
    path = Path.home() / "Library" / "LaunchAgents" / f"{LABEL}.plist"
    if not path.is_file():
        return "Não havia agendamento do pwdev-media."
    subprocess.run(["launchctl", "unload", str(path)], capture_output=True)
    path.unlink()
    return "Agendamento removido."
