"""Minimal HTTP client (stdlib) shared by providers and discovery.

Every provider goes through `request`, so the tests replace this single function to run
without network. A response that does not match the documented contract raises
`ContractError` with the field that was missing: fail loudly, never guess.
"""
from __future__ import annotations

import json
import urllib.error
import urllib.request
from dataclasses import dataclass

USER_AGENT = "pwdev-media/0.1"


class HttpError(RuntimeError):
    def __init__(self, status: int, url: str, body: str):
        super().__init__(f"HTTP {status} em {url}: {body[:300]}")
        self.status = status
        self.url = url
        self.body = body


class ContractError(RuntimeError):
    """The API answered, but not in the shape its documentation promises."""


@dataclass
class Response:
    status: int
    headers: dict
    body: bytes

    def json(self):
        try:
            return json.loads(self.body.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise ContractError(f"resposta não é JSON: {self.body[:200]!r}") from exc


def request(method: str, url: str, headers: dict | None = None, payload=None,
            timeout: float = 120.0) -> Response:
    data = None
    hdrs = {"User-Agent": USER_AGENT, **(headers or {})}
    if payload is not None:
        data = json.dumps(payload).encode("utf-8")
        hdrs.setdefault("Content-Type", "application/json")
    req = urllib.request.Request(url, data=data, headers=hdrs, method=method)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return Response(resp.status, dict(resp.headers), resp.read())
    except urllib.error.HTTPError as exc:
        raise HttpError(exc.code, url, exc.read().decode("utf-8", "replace")) from exc


def require(data: dict, *keys: str, where: str):
    """Return data[k1][k2]... or raise ContractError naming the missing field."""
    current = data
    path = []
    for key in keys:
        path.append(str(key))
        try:
            current = current[key]
        except (KeyError, IndexError, TypeError):
            raise ContractError(f"{where}: campo '{'.'.join(path)}' ausente na resposta — "
                                "o contrato da API pode ter mudado") from None
    return current
