#!/usr/bin/env python3
"""Discover which agent runtimes are usable here and which models each one can run.

Read-only. For Claude Code, Codex CLI, Hermes Agent and OpenCode it reports whether the
binary is installed, its version, whether it is signed in, the model and effort it uses by
default (and where each value came from), and the models it can run with their effort
levels, context and price when the runtime exposes them.

Every model list carries its source, because the runtimes expose very different things:
Codex and OpenCode print a real catalogue, Hermes keeps a per-provider cache, and Claude
Code has no listing command at all — its list is the aliases its own help documents plus
the extra options it has cached. Nothing is invented to fill a gap; an unknown stays
unknown. No credential, e-mail, organization id or key fragment is ever recorded.

Usage:
    discover.py [--runtimes claude,codex,hermes,opencode] [--json] [--limit 12]
"""
from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

sys.path.insert(0, str(Path(__file__).resolve().parent))
import runtimes as rt  # noqa: E402

TIMEOUT = 60


def _run(command: List[str], timeout: float = TIMEOUT, env: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
    if not shutil.which(command[0]):
        return {"exit_code": None, "stdout": "", "stderr": f"{command[0]} not found"}
    try:
        done = subprocess.run(command, capture_output=True, text=True, timeout=timeout, stdin=subprocess.DEVNULL, env=env)
        return {"exit_code": done.returncode, "stdout": done.stdout, "stderr": done.stderr}
    except (OSError, subprocess.TimeoutExpired) as exc:
        return {"exit_code": None, "stdout": "", "stderr": str(exc)}


def _json_after_prefix(text: str) -> Any:
    starts = [i for i in (text.find("{"), text.find("[")) if i != -1]
    if not starts:
        return None
    try:
        return json.loads(text[min(starts):])
    except json.JSONDecodeError:
        return None


def _base(runtime: str) -> Dict[str, Any]:
    path = shutil.which(runtime)
    return {"runtime": runtime, "installed": bool(path), "path": rt.sanitize(path) if path else None,
            "version": rt.runtime_version(runtime) if path else None, "auth": None, "default": None,
            "models": [], "models_source": None, "usable": False, "notes": []}


def _defaults(runtime: str) -> Dict[str, Any]:
    request = rt.RunRequest(prompt="", workspace=Path("."), run_dir=Path("."))
    env = {k: os.environ[k] for k in request.env_passthrough if k in os.environ}
    return rt.effective_settings(runtime, request, env)


# --- Claude Code ---------------------------------------------------------------------

def discover_claude() -> Dict[str, Any]:
    info = _base("claude")
    if not info["installed"]:
        return info
    status = _json_after_prefix(_run(["claude", "auth", "status"])["stdout"]) or {}
    # Deliberately drops email, orgId, orgName and directories.
    info["auth"] = {k: status.get(k) for k in ("loggedIn", "authMethod", "apiProvider", "subscriptionType") if k in status}
    info["default"] = _defaults("claude")
    help_text = _run(["claude", "--help"])["stdout"]
    efforts = re.search(r"--effort <level>[^(]*\(([^)]+)\)", help_text, re.S)
    effort_levels = [e.strip() for e in efforts.group(1).split(",")] if efforts else []
    aliases = sorted(set(re.findall(r"'(sonnet|opus|haiku|fable)'", help_text)))
    models: List[Dict[str, Any]] = [{"id": alias, "kind": "alias (latest of the family)", "efforts": effort_levels,
                                     "source": "claude --help"} for alias in aliases]
    try:
        cache = json.loads(rt._read(Path.home() / ".claude.json") or "{}").get("additionalModelOptionsCache") or []
    except json.JSONDecodeError:
        cache = []
    for option in cache:
        if isinstance(option, dict) and option.get("value"):
            models.append({"id": option["value"], "label": option.get("label"), "description": option.get("description"),
                           "efforts": effort_levels, "source": "~/.claude.json additionalModelOptionsCache"})
    info["models"] = models
    info["models_source"] = ("Claude Code has no model-listing command: aliases documented by `claude --help` plus the "
                             "additional options it cached. Full ids such as claude-sonnet-5 are also accepted by --model.")
    info["effort_levels"] = effort_levels
    info["usable"] = bool(info["auth"].get("loggedIn"))
    if not info["usable"]:
        info["notes"].append("not signed in: run `claude auth login`")
    return info


# --- Codex CLI -------------------------------------------------------------------------

def discover_codex(pricing: Dict[str, Dict[str, float]]) -> Dict[str, Any]:
    info = _base("codex")
    if not info["installed"]:
        return info
    login = _run(["codex", "login", "status"])
    line = (login["stdout"] or login["stderr"]).strip().splitlines()
    info["auth"] = {"loggedIn": login["exit_code"] == 0 and bool(line) and "not logged" not in line[0].lower(),
                    "method": line[0] if line else None}
    info["default"] = _defaults("codex")
    catalogue = _json_after_prefix(_run(["codex", "debug", "models"])["stdout"]) or {}
    for model in catalogue.get("models") or []:
        if model.get("visibility") != "list":
            continue  # hidden and internal entries are not offered to users
        slug = model.get("slug")
        info["models"].append({
            "id": slug, "label": model.get("display_name"),
            "default_effort": model.get("default_reasoning_level"),
            "efforts": [level.get("effort") for level in model.get("supported_reasoning_levels") or [] if level.get("effort")],
            "context": model.get("context_window"), "supported_in_api": model.get("supported_in_api"),
            "price_per_mtok": pricing.get(slug), "priority": model.get("priority"), "source": "codex debug models"})
    info["models"].sort(key=lambda m: (m.get("priority") is None, m.get("priority")))
    info["models_source"] = "codex debug models (visibility=list)"
    configured = info["default"].get("model_effective")
    match = next((m for m in info["models"] if m["id"] == configured), None)
    if match and not info["default"].get("effort_source", "").startswith("~/.codex"):
        info["default"].update(effort_effective=match["default_effort"], effort_source="model default_reasoning_level (codex debug models)")
    info["usable"] = bool(info["auth"]["loggedIn"])
    if info["usable"]:
        info["notes"].append("a ChatGPT-plan login is not billed per token; costs are API-price equivalents")
    return info


# --- Hermes Agent ----------------------------------------------------------------------

def discover_hermes() -> Dict[str, Any]:
    info = _base("hermes")
    if not info["installed"]:
        return info
    status = _run(["hermes", "status"], timeout=90)["stdout"]
    model = re.search(r"^\s*Model:\s*(\S+)", status, re.M)
    provider = re.search(r"^\s*Provider:\s*(.+)$", status, re.M)
    # Provider names only; the masked key fragment Hermes prints is never kept.
    ready = sorted({m.group(1).strip() for m in re.finditer(r"^\s{2}([A-Za-z][\w ./-]*?)\s+✓", status, re.M)})
    info["auth"] = {"providers_ready": ready, "loggedIn": bool(ready)}
    info["default"] = _defaults("hermes")
    if model and not info["default"].get("model_effective"):
        info["default"].update(model_effective=model.group(1), model_source="hermes status")
    active = (info["default"].get("provider_effective") or (provider.group(1).strip() if provider else "")).lower().replace(" ", "")
    try:
        cache = json.loads(rt._read(Path.home() / ".hermes" / "provider_models_cache.json") or "{}")
    except json.JSONDecodeError:
        cache = {}
    for name, entry in cache.items():
        if active and name.lower().replace(" ", "") != active:
            continue
        for item in (entry or {}).get("models") or []:
            model_id = item if isinstance(item, str) else (item.get("id") if isinstance(item, dict) else None)
            if model_id:
                info["models"].append({"id": model_id, "provider": name, "source": "~/.hermes/provider_models_cache.json"})
    info["models_source"] = (f"~/.hermes/provider_models_cache.json for the configured provider ({active or 'unknown'}); "
                             "refresh with `hermes model --refresh`")
    effort_levels = re.search(r"--reasoning LEVEL.*?:\s*([a-z, ]+(?:, or [a-z]+)?)", _run(["hermes", "--help"])["stdout"], re.S)
    info["effort_levels"] = [e.strip() for e in re.split(r",|\bor\b", effort_levels.group(1)) if e.strip()] if effort_levels else []
    info["usable"] = bool(ready)
    info["notes"].append("headless runs bypass approvals: bench.py requires --acknowledge-hermes-automation")
    return info


# --- OpenCode ------------------------------------------------------------------------

def discover_opencode() -> Dict[str, Any]:
    info = _base("opencode")
    if not info["installed"]:
        return info
    creds = _run(["opencode", "providers", "list"])["stdout"]
    count = re.search(r"(\d+)\s+credentials?", re.sub(r"\x1b\[[0-9;]*m", "", creds))
    info["auth"] = {"credentials": int(count.group(1)) if count else None}
    info["default"] = _defaults("opencode")
    verbose = _run(["opencode", "models", "--verbose"], timeout=120)["stdout"]
    blocks = re.split(r"^([\w.-]+/[^\s{]+)\s*$", verbose, flags=re.M)
    for i in range(1, len(blocks) - 1, 2):
        try:
            data = json.loads(blocks[i + 1])
        except json.JSONDecodeError:
            continue
        cost = data.get("cost") or {}
        info["models"].append({
            "id": blocks[i].strip(), "label": data.get("name"), "status": data.get("status"),
            "efforts": sorted((data.get("variants") or {}).keys()),
            "context": (data.get("limit") or {}).get("context"), "output": (data.get("limit") or {}).get("output"),
            "reasoning": (data.get("capabilities") or {}).get("reasoning"),
            "price_per_mtok": {"input": cost.get("input"), "output": cost.get("output")} if cost else None,
            "free": cost.get("input") == 0 and cost.get("output") == 0, "released": data.get("release_date"),
            "source": "opencode models --verbose"})
    info["models_source"] = "opencode models --verbose (only providers with credentials, plus the free Zen tier)"
    info["usable"] = bool(info["models"])
    if any(m.get("free") for m in info["models"]):
        info["notes"].append("free Zen models may retain or train on prompts (opencode.ai/docs/zen); do not send unpublished or confidential content")
    if info["auth"]["credentials"] == 0:
        info["notes"].append("no provider credentials: add one with `opencode providers login` to run paid models")
    return info


def discover(runtimes: List[str], pricing: Dict[str, Dict[str, float]]) -> Dict[str, Any]:
    probes = {"claude": discover_claude, "codex": lambda: discover_codex(pricing),
              "hermes": discover_hermes, "opencode": discover_opencode}
    found = {name: probes[name]() for name in runtimes if name in probes}
    return {"schema_version": 1, "generated_at": rt.utc_now(), "runtimes": found,
            "usable": [name for name, item in found.items() if item["usable"]]}


def render_markdown(report: Dict[str, Any], limit: int) -> str:
    lines = ["# Runtimes and models available", "",
             "| Runtime | Installed | Version | Signed in | Default model | Default effort | Models |",
             "|---|---|---|---|---|---|---:|"]
    for name, item in report["runtimes"].items():
        default = item.get("default") or {}
        auth = item.get("auth") or {}
        if "loggedIn" in auth:
            signed = "yes" if auth["loggedIn"] else "no"
        elif "credentials" in auth:
            signed = f"{auth['credentials']} credentials" if auth.get("credentials") else ("free tier only" if item["usable"] else "no")
        else:
            signed = "—"
        lines.append(f"| {name} | {'yes' if item['installed'] else 'no'} | {item.get('version') or '—'} | "
                     f"{signed} | {default.get('model_effective') or 'built-in'} | "
                     f"{default.get('effort_effective') or 'built-in'} | {len(item['models'])} |")
    for name, item in report["runtimes"].items():
        if not item["installed"]:
            continue
        lines += ["", f"## {name}", "", f"Source: {item.get('models_source') or '—'}", ""]
        for note in item.get("notes") or []:
            lines.append(f"- {note}")
        if item["models"]:
            lines += ["", "| Model | Efforts | Default effort | Context | Price in/out per MTok |", "|---|---|---|---:|---|"]
            for model in item["models"][:limit]:
                price = model.get("price_per_mtok")
                price_text = "free" if model.get("free") else (f"{price.get('input')} / {price.get('output')}" if price else "—")
                lines.append(f"| `{model['id']}` | {', '.join(model.get('efforts') or []) or '—'} | "
                             f"{model.get('default_effort') or '—'} | {model.get('context') or '—'} | {price_text} |")
            if len(item["models"]) > limit:
                lines.append(f"| … {len(item['models']) - limit} more (use --json) | | | | |")
    lines += ["", f"Usable now: {', '.join(report['usable']) or 'none'}"]
    return "\n".join(lines)


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--runtimes", default=",".join(rt.RUNTIMES))
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--limit", type=int, default=12, help="models per runtime in the Markdown view")
    parser.add_argument("--cases", type=Path, default=Path(__file__).resolve().parents[1] / "evals" / "evals.json",
                        help="evals.json whose matrix.pricing prices Codex models")
    args = parser.parse_args(argv)
    try:
        pricing = json.loads(args.cases.read_text(encoding="utf-8")).get("matrix", {}).get("pricing", {})
    except (OSError, json.JSONDecodeError):
        pricing = {}
    report = discover([r.strip() for r in args.runtimes.split(",") if r.strip()], pricing)
    report = json.loads(rt.sanitize(json.dumps(report, ensure_ascii=False)))
    print(json.dumps(report, indent=2, ensure_ascii=False) if args.json else render_markdown(report, args.limit))
    return 0


if __name__ == "__main__":
    sys.exit(main())
