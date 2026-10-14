"""Where pwdev-media keeps its state: ~/.pwdev/media, or PWDEV_MEDIA_HOME (used by the tests)."""
from __future__ import annotations

import os
from pathlib import Path

DATA = Path(__file__).resolve().parent / "data"


def home() -> Path:
    base = os.environ.get("PWDEV_MEDIA_HOME")
    path = Path(base).expanduser() if base else Path.home() / ".pwdev" / "media"
    path.mkdir(parents=True, exist_ok=True)
    return path


def catalog_file() -> Path:
    return home() / "catalogo.json"


def ledger_file() -> Path:
    return home() / "ledger.jsonl"


def config_file() -> Path:
    return home() / "config.json"


def reports_dir() -> Path:
    path = home() / "relatorios"
    path.mkdir(parents=True, exist_ok=True)
    return path


def outputs_dir() -> Path:
    path = home() / "gerados"
    path.mkdir(parents=True, exist_ok=True)
    return path
