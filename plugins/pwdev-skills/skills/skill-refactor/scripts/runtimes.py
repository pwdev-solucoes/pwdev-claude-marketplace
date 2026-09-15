#!/usr/bin/env python3
"""Headless adapters for Claude Code, Codex CLI, Hermes Agent and OpenCode.

Each adapter turns one prompt into one run inside an isolated workspace and returns
the same record shape: exit code, wall-clock duration, the usage the runtime itself
reported, the cost when the runtime reports or a pricing table allows it, and the
model the runtime says it used. Nothing here interprets the answer; ``grade.py`` does.

The vectors reuse what this marketplace already runs in its fleets
(``plugins/*/scripts/*engine-*``) and the process handling of the former
``sdd_runtime_smoke.py``: process-group timeouts, secret redaction, a snapshot of
protected paths before and after every run so an escaped write fails the run.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import shutil
import signal
import subprocess
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence

RUNTIMES = ("claude", "codex", "hermes", "opencode")
STATUSES = ("PASS", "FAIL", "BLOCKED", "NOT_RUN")
DEFAULT_TIMEOUT = 300.0
MODEL_ERROR = re.compile(r"(?i)(unknown|invalid|unsupported|not found|does not exist|no such).{0,40}model|model.{0,60}(unknown|invalid|unsupported|not found|does not exist|not available)")
PROVIDER_UNAVAILABLE = re.compile(r"(?i)(service temporarily overloaded|overloaded|temporarily unavailable|service unavailable|"
                                  r"bad gateway|upstream error|\[50[234]\]|cannot connect to api|socket connection was closed|"
                                  r"connection reset|ECONNRESET|ECONNREFUSED|fetch failed)[^\n]{0,160}")
QUOTA_ERROR = re.compile(r"(?i)(hit your usage limit|usage limit|rate limit(ed)?|quota (exceeded|exhausted)|insufficient (credits|quota)|"
                         r"purchase more credits|billing hard limit|429 too many requests)[^\n]{0,160}")


def _first_match(pattern: "re.Pattern[str]", text: str) -> str:
    match = pattern.search(text)
    return match.group(0).strip() if match else ""


ERROR_EVENT = re.compile(r'"type"\s*:\s*"error"[^\n]*')


def _diagnose(stdout: str, stderr: str) -> Tuple[Optional[str], str]:
    """What the runtime itself said went wrong: quota, provider outage or rejected model.

    stderr and error events are read first; the rest of stdout only when they say nothing.
    The agent's answer can quote documentation about quotas and outages (observed 2026-09-14),
    and a quote must never outrank the runtime's own message.
    """
    events = "\n".join(m.group(0) for m in ERROR_EVENT.finditer(stdout))
    for text in (stderr + "\n" + events, stdout):
        for kind, pattern in (("quota", QUOTA_ERROR), ("unavailable", PROVIDER_UNAVAILABLE), ("model", MODEL_ERROR)):
            match = pattern.search(text)
            if match:
                return kind, match.group(0).strip()
    return None, ""


class RuntimeBlocked(RuntimeError):
    """A prerequisite is missing; the run did not happen and proves nothing."""


@dataclass
class RunRequest:
    prompt: str
    workspace: Path
    run_dir: Path
    skill_dir: Optional[Path] = None
    skill_name: Optional[str] = None
    model: Optional[str] = None
    provider: Optional[str] = None
    timeout: float = DEFAULT_TIMEOUT
    executable: Optional[str] = None
    budget_usd: Optional[float] = None
    effort: Optional[str] = None  # None = the runtime's configured default, recorded as such
    # The user's own skills and plugins load into every arm and blur the comparison. Claude Code
    # can switch a listed plugin off per session (--settings enabledPlugins); OpenCode can only be
    # isolated by a fresh HOME, which works for models that need no stored credentials.
    disable_claude_plugins: Sequence[str] = ()
    isolate_user_skills: bool = False
    hermes_automation_acknowledged: bool = False
    protected_paths: List[Path] = field(default_factory=list)
    pricing: Dict[str, Dict[str, float]] = field(default_factory=dict)
    # CLAUDE_EFFORT is configuration, not a credential: without it a "default" Claude run silently
    # differs from the one the user gets in their own shell (observed 2026-09-13).
    env_passthrough: Sequence[str] = ("PATH", "HOME", "USER", "TMPDIR", "LANG", "LC_ALL", "TERM", "CLAUDE_EFFORT",
                                      "XDG_CONFIG_HOME", "XDG_DATA_HOME", "XDG_CACHE_HOME")


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def sanitize(value: str) -> str:
    value = re.sub(r"(?i)\b(token|password|secret|api[_-]?key)\s*[=:]\s*[^\s]+", r"\1=[REDACTED]", value)
    value = re.sub(r"(?i)\bAuthorization:\s*Bearer\s+[^\s]+", "Authorization: Bearer [REDACTED]", value)
    return re.sub(r"/(?:Users|home)/[^/\s]+", "/[USER]", value)


def sha256_path(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def snapshot(root: Path) -> Dict[str, Any]:
    """Content and mode of every entry under root; symlinks by target, never followed."""
    result: Dict[str, Any] = {}
    root = Path(root)
    if not root.exists():
        return result
    for path in sorted(root.rglob("*")):
        rel = path.relative_to(root).as_posix()
        # Bytecode caches are written by the interpreter running the harness, not by the run.
        if "__pycache__" in path.parts or path.suffix == ".pyc":
            continue
        if path.is_symlink():
            result[rel] = ["symlink", os.readlink(path)]
        elif path.is_dir():
            result[rel] = ["directory", path.stat().st_mode & 0o777]
        elif path.is_file():
            result[rel] = [sha256_path(path), path.stat().st_mode & 0o777]
    return result


def run_process(command: Sequence[str], cwd: Path, env: Dict[str, str], timeout: float) -> Dict[str, Any]:
    started = time.monotonic()
    process = subprocess.Popen(list(command), cwd=str(cwd), env=env, text=True,
                               stdout=subprocess.PIPE, stderr=subprocess.PIPE, start_new_session=True)
    try:
        stdout, stderr = process.communicate(timeout=timeout)
        timed_out = False
    except subprocess.TimeoutExpired:
        os.killpg(process.pid, signal.SIGTERM)
        try:
            stdout, stderr = process.communicate(timeout=2)
        except subprocess.TimeoutExpired:
            os.killpg(process.pid, signal.SIGKILL)
            stdout, stderr = process.communicate()
        timed_out = True
    return {"exit_code": None if timed_out else process.returncode, "timed_out": timed_out,
            "duration_seconds": round(time.monotonic() - started, 3), "stdout": stdout, "stderr": stderr}


def runtime_version(runtime: str, executable: Optional[str] = None) -> Optional[str]:
    binary = executable or runtime
    if not shutil.which(binary):
        return None
    try:
        completed = subprocess.run([binary, "--version"], capture_output=True, text=True, timeout=15)
    except (OSError, subprocess.TimeoutExpired):
        return None
    text = (completed.stdout or completed.stderr).strip().splitlines()
    return text[0] if text else None


# --- workspace preparation -------------------------------------------------------------

def _copy_skill(request: RunRequest, destination: Path) -> Path:
    if request.skill_dir is None:
        raise RuntimeBlocked("a skill_dir is required to expose the skill to the runtime")
    name = request.skill_name or Path(request.skill_dir).name
    target = destination / name
    shutil.copytree(request.skill_dir, target, symlinks=False,
                    ignore=shutil.ignore_patterns("__pycache__", "*.pyc", "benchmarks", ".git"))
    return target


PLUGIN_IGNORE = shutil.ignore_patterns("__pycache__", "*.pyc", "benchmarks", "evals", ".git")


def is_plugin_root(path: Optional[Path]) -> bool:
    """A whole plugin (manifest + skills/) rather than one skill folder."""
    return path is not None and (Path(path) / ".claude-plugin" / "plugin.json").is_file() and (Path(path) / "skills").is_dir()


def plugin_skills(root: Path) -> List[Path]:
    return sorted(p.parent for p in (root / "skills").glob("*/SKILL.md"))


def _copy_plugin(request: RunRequest, destination: Path) -> Path:
    """Copy a plugin root whole, so `../../references` and `../../scripts` keep resolving."""
    if request.skill_dir is None:
        raise RuntimeBlocked("a skill_dir is required to expose the plugin to the runtime")
    if any(p.is_symlink() for p in Path(request.skill_dir).rglob("*")):
        raise RuntimeBlocked("plugin tree contains symlinks; refusing to copy it into a workspace")
    shutil.copytree(request.skill_dir, destination, symlinks=False, ignore=PLUGIN_IGNORE)
    return destination


def _claude_settings(request: RunRequest, prepared: Dict[str, Any]) -> None:
    """A per-session settings file that switches the user's installed copies of the measured plugin off."""
    if not request.disable_claude_plugins:
        return
    path = request.run_dir / "settings.json"
    path.write_text(json.dumps({"enabledPlugins": {name: False for name in request.disable_claude_plugins}}, indent=2) + "\n",
                    encoding="utf-8")
    prepared["settings_path"] = str(path)


def _isolated_home(request: RunRequest, prepared: Dict[str, Any]) -> None:
    """OpenCode reads ~/.config/opencode, ~/.claude and ~/.agents skills: a fresh HOME hides them all."""
    if not request.isolate_user_skills:
        return
    home = request.run_dir / "home"
    (home / ".config").mkdir(parents=True, exist_ok=True)
    prepared.setdefault("env", {}).update({"HOME": str(home), "XDG_CONFIG_HOME": str(home / ".config")})


def _agents_md_for(skills: List[Tuple[str, str]]) -> str:
    """AGENTS.md naming every skill file the runtime may follow (Codex and Hermes have no plugin)."""
    lines = ["# Workspace instructions", "",
             "Skills are available in this workspace. Read a skill's `description` first and follow the",
             "skill when the task matches it; otherwise ignore it. Do not modify the skill folders.", ""]
    lines += [f"- `{rel}/SKILL.md`" for _, rel in skills]
    return "\n".join(lines) + "\n"


def prepare(runtime: str, request: RunRequest) -> Dict[str, Any]:
    """Expose the skill the way each runtime discovers skills, without touching user config.

    `skill_dir` may be one skill folder or a whole plugin root (manifest + skills/): a plugin is
    copied whole, so relative references and scripts keep working, and every skill in it is exposed.
    """
    request.run_dir.mkdir(parents=True, exist_ok=True)
    request.workspace.mkdir(parents=True, exist_ok=True)
    prepared: Dict[str, Any] = {"runtime": runtime}
    if is_plugin_root(request.skill_dir):
        return _prepare_plugin(runtime, request, prepared)
    if runtime == "claude":
        _claude_settings(request, prepared)
        if request.skill_dir is None:
            # A no-skill run loads no plugin at all: the control arm sees only the workspace.
            return prepared
        plugin_dir = request.run_dir / "plugin"
        (plugin_dir / ".claude-plugin").mkdir(parents=True, exist_ok=True)
        name = request.skill_name or Path(request.skill_dir).name
        (plugin_dir / ".claude-plugin" / "plugin.json").write_text(json.dumps({
            "name": f"bench-{name}", "version": "0.0.0",
            "description": "Temporary plugin generated by skill-refactor bench; exposes one skill.",
        }, indent=2) + "\n", encoding="utf-8")
        prepared["skill_path"] = str(_copy_skill(request, plugin_dir / "skills"))
        prepared["plugin_dir"] = str(plugin_dir)
    elif runtime == "codex":
        if request.skill_dir is not None:
            skill_path = _copy_skill(request, request.workspace / "skills")
            prepared["skill_path"] = str(skill_path)
            rel = skill_path.relative_to(request.workspace).as_posix()
            (request.workspace / "AGENTS.md").write_text(
                "# Workspace instructions\n\n"
                f"A skill is available at `{rel}/SKILL.md`. Read its `description` first and follow the\n"
                "skill when the task matches it; otherwise ignore it. Do not modify the skill folder.\n",
                encoding="utf-8")
        prepared["last_message_path"] = str(request.run_dir / "last-message.txt")
    elif runtime == "hermes":
        if not request.hermes_automation_acknowledged:
            raise RuntimeBlocked("hermes -z bypasses approvals; pass hermes_automation_acknowledged=True "
                                 "only inside an isolated workspace")
        if request.skill_dir is not None:
            # `--skills` only accepts names Hermes already knows (profile, hub or a *trusted*
            # project), and trusting the workspace would edit the user's Hermes config. So the
            # skill is exposed the way Codex gets it: AGENTS.md, injected from the cwd on every
            # turn, names the file and the agent reaches it with its own file tools. This
            # measures execution with the skill available, not native catalogue discovery.
            skill_path = _copy_skill(request, request.workspace / "skills")
            prepared["skill_path"] = str(skill_path)
            rel = skill_path.relative_to(request.workspace).as_posix()
            (request.workspace / "AGENTS.md").write_text(
                "# Workspace instructions\n\n"
                f"A skill is available at `{rel}/SKILL.md`. Read its `description` first and follow the\n"
                "skill when the task matches it; otherwise ignore it. Do not modify the skill folder.\n",
                encoding="utf-8")
        # Hermes' shell and file tools anchor on $TERMINAL_CWD, not on the process cwd or `--in`
        # (observed 2026-09-13: without it the agent worked from the user's home directory).
        prepared["env"] = {"TERMINAL_CWD": str(request.workspace.resolve())}
        prepared["usage_path"] = str(request.run_dir / "usage.json")
    elif runtime == "opencode":
        _isolated_home(request, prepared)
        if request.skill_dir is not None:
            # Native discovery: OpenCode loads `.opencode/skills/<name>/SKILL.md` walking up from the
            # working directory to the git worktree root, and exposes each skill to its `skill` tool.
            # A git repository at the workspace bounds that walk, so nothing above the workspace is
            # picked up; global skills in the user's profile still load, as they do for every runtime.
            prepared["skill_path"] = str(_copy_skill(request, request.workspace / ".opencode" / "skills"))
        if not (request.workspace / ".git").exists():
            subprocess.run(["git", "init", "-q", str(request.workspace)], capture_output=True, check=False)
    else:
        raise ValueError(f"unknown runtime: {runtime}")
    return prepared


def _prepare_plugin(runtime: str, request: RunRequest, prepared: Dict[str, Any]) -> Dict[str, Any]:
    root = Path(request.skill_dir)
    names = [p.name for p in plugin_skills(root)]
    prepared["plugin_skills"] = names
    if runtime == "claude":
        _claude_settings(request, prepared)
        # The plugin as the user would install it: its own manifest, hooks and skills.
        plugin_dir = _copy_plugin(request, request.run_dir / "plugin")
        prepared["plugin_dir"] = str(plugin_dir)
        prepared["skill_path"] = str(plugin_dir / "skills")
    elif runtime in ("codex", "hermes"):
        if runtime == "hermes" and not request.hermes_automation_acknowledged:
            raise RuntimeBlocked("hermes -z bypasses approvals; pass hermes_automation_acknowledged=True "
                                 "only inside an isolated workspace")
        copied = _copy_plugin(request, request.workspace / "plugin")
        prepared["skill_path"] = str(copied / "skills")
        (request.workspace / "AGENTS.md").write_text(
            _agents_md_for([(n, f"plugin/skills/{n}") for n in names]), encoding="utf-8")
        if runtime == "hermes":
            prepared["env"] = {"TERMINAL_CWD": str(request.workspace.resolve())}
            prepared["usage_path"] = str(request.run_dir / "usage.json")
        else:
            prepared["last_message_path"] = str(request.run_dir / "last-message.txt")
    elif runtime == "opencode":
        # OpenCode reads .opencode/skills/<name>/SKILL.md; the plugin's siblings go next to
        # skills/ so `../../references` resolves from inside .opencode/.
        # Only what skills link to. OpenCode parses .opencode/agents/ and .opencode/commands/ as
        # its own configuration (different frontmatter), and a plugin's copies make it refuse to start.
        _isolated_home(request, prepared)
        target = request.workspace / ".opencode"
        target.mkdir(parents=True, exist_ok=True)
        for name in ("skills", "references", "scripts", "templates", "assets"):
            child = root / name
            if child.is_dir():
                shutil.copytree(child, target / name, symlinks=False, ignore=PLUGIN_IGNORE, dirs_exist_ok=True)
        prepared["skill_path"] = str(target / "skills")
        if not (request.workspace / ".git").exists():
            subprocess.run(["git", "init", "-q", str(request.workspace)], capture_output=True, check=False)
    else:
        raise ValueError(f"unknown runtime: {runtime}")
    return prepared


# --- command vectors ---------------------------------------------------------------

def build_command(runtime: str, request: RunRequest, prepared: Dict[str, Any]) -> List[str]:
    exe = request.executable or runtime
    if runtime == "claude":
        command = [exe, "-p", request.prompt, "--output-format", "json", "--no-session-persistence",
                   "--dangerously-skip-permissions", "--add-dir", str(request.workspace)]
        if "plugin_dir" in prepared:
            command += ["--plugin-dir", prepared["plugin_dir"]]
        if "settings_path" in prepared:
            command += ["--settings", prepared["settings_path"]]
        if request.model:
            command += ["--model", request.model]
        if request.effort:
            command += ["--effort", request.effort]
        if request.budget_usd is not None:
            command += ["--max-budget-usd", f"{request.budget_usd:.4f}"]
        return command
    if runtime == "codex":
        command = [exe, "exec", "--json", "--ephemeral", "--skip-git-repo-check",
                   "--dangerously-bypass-approvals-and-sandbox", "--cd", str(request.workspace),
                   "--output-last-message", prepared["last_message_path"]]
        if request.model:
            command += ["-m", request.model]
        if request.effort:
            command += ["-c", f'model_reasoning_effort="{request.effort}"']
        return command + [request.prompt]
    if runtime == "hermes":
        command = [exe, "-z", request.prompt, "--in", str(request.workspace), "--no-restore-cwd",
                   "--usage-file", prepared["usage_path"], "--yolo", "--accept-hooks"]
        if "skill_name" in prepared:
            command += ["--skills", prepared["skill_name"]]
        if request.model:
            command += ["-m", request.model]
        if request.provider:
            command += ["--provider", request.provider]
        if request.effort:
            command += ["--reasoning", request.effort]
        return command
    if runtime == "opencode":
        command = [exe, "run", "--format", "json", "--dir", str(request.workspace), "--dangerously-skip-permissions"]
        if request.model:
            command += ["-m", request.model]
        if request.effort:
            command += ["--variant", request.effort]
        return command + [request.prompt]
    raise ValueError(f"unknown runtime: {runtime}")


# --- result parsing --------------------------------------------------------------------

def _int(value: Any) -> Optional[int]:
    return int(value) if isinstance(value, (int, float)) and not isinstance(value, bool) else None


def normalize_usage(raw: Optional[Dict[str, Any]], *, input_includes_cache: bool = False) -> Optional[Dict[str, Optional[int]]]:
    """One usage shape for every runtime.

    Providers disagree on what ``input_tokens`` means. Anthropic reports it *net* of cache
    (``cache_read_input_tokens`` and ``cache_creation_input_tokens`` are separate); OpenAI reports
    it *including* ``cached_input_tokens``, and ``output_tokens`` including reasoning. Normalized:
    ``input_tokens`` is always the fresh, uncached part, so the three buckets add up to
    ``context_tokens`` — the accumulated input the model actually processed — on every runtime.
    """
    if not isinstance(raw, dict):
        return None
    pick = lambda *keys: next((_int(raw[k]) for k in keys if k in raw), None)  # noqa: E731
    usage = {
        "input_tokens": pick("input_tokens", "prompt_tokens", "input"),
        "output_tokens": pick("output_tokens", "completion_tokens", "output"),
        "cache_read_tokens": pick("cache_read_input_tokens", "cached_input_tokens", "cache_read_tokens", "cached_tokens"),
        "cache_write_tokens": pick("cache_creation_input_tokens", "cache_write_input_tokens", "cache_write_tokens"),
        "reasoning_tokens": pick("reasoning_output_tokens", "reasoning_tokens")
                            if any(k in raw for k in ("reasoning_output_tokens", "reasoning_tokens"))
                            else _int((raw.get("output_tokens_details") or {}).get("thinking_tokens")),
        "total_tokens": pick("total_tokens"),
    }
    if input_includes_cache and usage["input_tokens"] is not None:
        usage["input_tokens"] = max(0, usage["input_tokens"] - (usage["cache_read_tokens"] or 0) - (usage["cache_write_tokens"] or 0))
    if usage["input_tokens"] is not None:
        usage["context_tokens"] = usage["input_tokens"] + (usage["cache_read_tokens"] or 0) + (usage["cache_write_tokens"] or 0)
    else:
        usage["context_tokens"] = None
    if usage["total_tokens"] is None and usage["context_tokens"] is not None and usage["output_tokens"] is not None:
        usage["total_tokens"] = usage["context_tokens"] + usage["output_tokens"]
    return usage


def cost_from_pricing(model: Optional[str], usage: Optional[Dict[str, Optional[int]]],
                      pricing: Dict[str, Dict[str, float]]) -> Optional[float]:
    """USD from a per-million-token price table {model: {input, output, cached_input?}}."""
    if not model or not usage or model not in pricing:
        return None
    price = pricing[model]
    # input_tokens is already the uncached part (see normalize_usage), so nothing is billed twice.
    inp, out = usage.get("input_tokens") or 0, usage.get("output_tokens") or 0
    cached = usage.get("cache_read_tokens") or 0
    cached_price = price.get("cached_input", price["input"])
    return round((inp * price["input"] + out * price["output"] + cached * cached_price) / 1_000_000, 6)


def parse_output(runtime: str, request: RunRequest, prepared: Dict[str, Any], stdout: str) -> Dict[str, Any]:
    parsed: Dict[str, Any] = {"result_text": None, "usage": None, "cost_usd": None, "cost_source": None,
                              "model_observed": None, "usage_source": None, "envelope_ok": None}
    if runtime == "claude":
        envelope = None
        for candidate in (stdout.strip(), *reversed(stdout.strip().splitlines())):
            try:
                value = json.loads(candidate)
            except (json.JSONDecodeError, ValueError):
                continue
            if isinstance(value, dict) and value.get("type") == "result":
                envelope = value
                break
        if envelope is None:
            # A run stopped mid-turn (budget cap, interruption) emits a non-result envelope that
            # still carries what it spent. Take the cost and usage; the verdict stays a failure.
            for candidate in reversed(stdout.strip().splitlines() or [stdout.strip()]):
                try:
                    value = json.loads(candidate)
                except (json.JSONDecodeError, ValueError):
                    continue
                if isinstance(value, dict) and ("usage" in value or "total_cost_usd" in value):
                    parsed["usage"] = normalize_usage(value.get("usage"))
                    parsed["usage_source"] = "claude:partial envelope"
                    if isinstance(value.get("total_cost_usd"), (int, float)):
                        parsed["cost_usd"], parsed["cost_source"] = round(float(value["total_cost_usd"]), 6), "runtime"
                    parsed["extra"] = {"stop_reason": value.get("stop_reason"), "session_id": value.get("session_id")}
                    break
            parsed["envelope_ok"] = False
            return parsed
        parsed["envelope_ok"] = envelope.get("is_error") is False and envelope.get("subtype") == "success"
        parsed["result_text"] = envelope.get("result") if isinstance(envelope.get("result"), str) else json.dumps(envelope.get("result"))
        parsed["usage"] = normalize_usage(envelope.get("usage"))
        parsed["usage_source"] = "claude:result.usage"
        if isinstance(envelope.get("total_cost_usd"), (int, float)):
            parsed["cost_usd"], parsed["cost_source"] = round(float(envelope["total_cost_usd"]), 6), "runtime"
        model_usage = envelope.get("modelUsage")
        if isinstance(model_usage, dict) and model_usage:
            # Claude Code also calls a small helper model; the model that did the task is the one that spent most.
            spend = {name: (u.get("costUSD") or 0) if isinstance(u, dict) else 0 for name, u in model_usage.items()}
            parsed["model_observed"] = max(spend, key=spend.get)
            parsed["models_involved"] = sorted(model_usage)
        parsed["extra"] = {k: envelope.get(k) for k in ("duration_ms", "duration_api_ms", "num_turns", "session_id")}
        return parsed
    if runtime == "codex":
        events = []
        for line in stdout.splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                events.append(json.loads(line))
            except json.JSONDecodeError:
                continue
        usage = next((e.get("usage") for e in reversed(events) if isinstance(e, dict) and e.get("type") == "turn.completed"), None)
        parsed["usage"] = normalize_usage(usage, input_includes_cache=True)
        parsed["usage_source"] = "codex:turn.completed.usage" if usage else None
        model = next((e.get("model") for e in events if isinstance(e, dict) and isinstance(e.get("model"), str)), None)
        parsed["model_observed"] = model
        last = Path(prepared["last_message_path"])
        parsed["result_text"] = last.read_text(encoding="utf-8") if last.is_file() else None
        parsed["envelope_ok"] = bool(events) and parsed["result_text"] is not None
        parsed["events_count"] = len(events)
        cost = cost_from_pricing(request.model or _configured_model("codex", request), parsed["usage"], request.pricing)
        if cost is not None:
            parsed["cost_usd"], parsed["cost_source"] = cost, "pricing_table"
        return parsed
    if runtime == "hermes":
        parsed["result_text"] = stdout
        usage_path = Path(prepared["usage_path"])
        if usage_path.is_file():
            try:
                report = json.loads(usage_path.read_text(encoding="utf-8"))
            except json.JSONDecodeError:
                report = None
            if isinstance(report, dict):
                raw = report.get("usage") if isinstance(report.get("usage"), dict) else report
                parsed["usage"] = normalize_usage(raw)
                parsed["usage_source"] = "hermes:--usage-file"
                for key in ("estimated_cost", "estimated_cost_usd", "cost", "cost_usd"):
                    if isinstance(report.get(key), (int, float)):
                        parsed["cost_usd"], parsed["cost_source"] = round(float(report[key]), 6), "estimated"
                        break
                parsed["model_observed"] = report.get("model") if isinstance(report.get("model"), str) else None
                parsed["extra"] = {"api_calls": report.get("api_calls")}
        parsed["envelope_ok"] = bool(stdout.strip())
        return parsed
    if runtime == "opencode":
        events = []
        for line in stdout.splitlines():
            try:
                value = json.loads(line)
            except (json.JSONDecodeError, ValueError):
                continue
            if isinstance(value, dict):
                events.append(value)
        steps = [e.get("part") or {} for e in events if e.get("type") == "step_finish"]
        # One step_finish per model call; the run's usage is their sum. `input` excludes cache
        # (observed: total = input + output + cache.read), as Claude's does.
        if steps:
            sums = {"input_tokens": 0, "output_tokens": 0, "reasoning_tokens": 0, "cache_read_input_tokens": 0,
                    "cache_creation_input_tokens": 0}
            for step in steps:
                tokens = step.get("tokens") or {}
                cache = tokens.get("cache") or {}
                sums["input_tokens"] += _int(tokens.get("input")) or 0
                sums["output_tokens"] += _int(tokens.get("output")) or 0
                sums["reasoning_tokens"] += _int(tokens.get("reasoning")) or 0
                sums["cache_read_input_tokens"] += _int(cache.get("read")) or 0
                sums["cache_creation_input_tokens"] += _int(cache.get("write")) or 0
            parsed["usage"] = normalize_usage(sums)
            parsed["usage_source"] = "opencode:sum(step_finish.part.tokens)"
            costs = [s.get("cost") for s in steps if isinstance(s.get("cost"), (int, float))]
            if costs:
                parsed["cost_usd"], parsed["cost_source"] = round(float(sum(costs)), 6), "runtime"
        texts = [(e.get("part") or {}).get("text") for e in events if e.get("type") == "text"]
        parsed["result_text"] = "\n".join(t for t in texts if isinstance(t, str) and t.strip()) or None
        errors = [e for e in events if e.get("type") == "error"]
        tools = [(e.get("part") or {}).get("tool") for e in events if e.get("type") == "tool_use"]
        session = next((e.get("sessionID") for e in events if e.get("sessionID")), None)
        parsed["extra"] = {"session_id": session, "steps": len(steps), "tools_used": tools,
                           "skill_loaded": any(t == "skill" for t in tools),
                           "errors": [json.dumps(e)[:300] for e in errors][:3]}
        parsed["envelope_ok"] = bool(steps) and not errors and parsed["result_text"] is not None
        # The events do not name the model; the stored session does.
        if session:
            info = _opencode_session_model(request.executable or "opencode", session, request.run_dir / "session-export.json")
            parsed["model_observed"] = info.get("model")
            parsed["effort_observed"] = info.get("variant")
        return parsed
    raise ValueError(f"unknown runtime: {runtime}")


def _opencode_session_model(executable: str, session_id: str, path: Path) -> Dict[str, Optional[str]]:
    # Written to a file, not a pipe: piped, `opencode export` stops at 64 KiB mid-string
    # (observed 2026-09-13 on 1.17.11), and the model is recorded near the end of the session.
    try:
        with path.open("w", encoding="utf-8") as handle:
            subprocess.run([executable, "export", session_id], stdout=handle, stderr=subprocess.DEVNULL, timeout=120)
        exported = path.read_text(encoding="utf-8")
    except (OSError, subprocess.TimeoutExpired):
        return {}
    start = exported.find("{")
    try:
        data = json.loads(exported[start:]) if start >= 0 else {}
    except json.JSONDecodeError:
        return {}
    model = variant = None
    for message in data.get("messages") or []:
        info = message.get("info") or {}
        if info.get("modelID"):
            model = f'{info.get("providerID")}/{info["modelID"]}' if info.get("providerID") else info["modelID"]
    session_model = (data.get("info") or {}).get("model") or {}
    variant = session_model.get("variant")
    return {"model": model, "variant": variant}


# --- effective settings ----------------------------------------------------------------

def _configured_model(runtime: str, request: "RunRequest") -> Optional[str]:
    env = {k: os.environ[k] for k in request.env_passthrough if k in os.environ}
    return effective_settings(runtime, request, env).get("model_effective")

def _read(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except OSError:
        return ""


def effective_settings(runtime: str, request: RunRequest, env: Dict[str, str]) -> Dict[str, Any]:
    """Which model and effort the run actually used, and where each value came from.

    An explicit request wins. Otherwise the value comes from the runtime's own configuration
    in the environment the child received; when neither exists the runtime applies a built-in
    default it does not report, and the record says exactly that instead of guessing.
    """
    home = Path(env.get("HOME", str(Path.home())))
    out: Dict[str, Any] = {"model_effective": request.model, "model_source": "request" if request.model else None,
                           "effort_effective": request.effort, "effort_source": "request" if request.effort else None}
    if runtime == "claude":
        settings = {}
        try:
            settings = json.loads(_read(home / ".claude" / "settings.json") or "{}")
        except json.JSONDecodeError:
            pass
        if not request.model and settings.get("model"):
            out.update(model_effective=settings["model"], model_source="~/.claude/settings.json model (alias)")
        if not request.effort:
            if env.get("CLAUDE_EFFORT"):
                out.update(effort_effective=env["CLAUDE_EFFORT"], effort_source="env CLAUDE_EFFORT")
            elif settings.get("effortLevel"):
                out.update(effort_effective=settings["effortLevel"], effort_source="~/.claude/settings.json effortLevel")
    elif runtime == "codex":
        text = _read(home / ".codex" / "config.toml")
        top = text.split("\n[", 1)[0]  # only top-level keys; profiles are not selected by this harness
        model = re.search(r'^\s*model\s*=\s*"([^"]+)"', top, re.M)
        effort = re.search(r'^\s*model_reasoning_effort\s*=\s*"([^"]+)"', top, re.M)
        if not request.model and model:
            out.update(model_effective=model.group(1), model_source="~/.codex/config.toml model")
        if not request.effort and effort:
            out.update(effort_effective=effort.group(1), effort_source="~/.codex/config.toml model_reasoning_effort")
    elif runtime == "hermes":
        text = _read(home / ".hermes" / "config.yaml")
        def section_value(section: str, key: str) -> Optional[str]:
            block = re.search(rf"^{section}:\n((?:[ \t]+.*\n?)+)", text, re.M)
            hit = block and re.search(rf"^[ \t]{{2}}{key}:\s*([^\s#]+)", block.group(1), re.M)
            return hit.group(1).strip("'\"") if hit else None
        if not request.model and section_value("model", "default"):
            out.update(model_effective=section_value("model", "default"), model_source="~/.hermes/config.yaml model.default")
        if not request.provider and section_value("model", "provider"):
            out["provider_effective"] = section_value("model", "provider")
        if not request.effort and section_value("agent", "reasoning_effort"):
            out.update(effort_effective=section_value("agent", "reasoning_effort"), effort_source="~/.hermes/config.yaml agent.reasoning_effort")
    elif runtime == "opencode":
        for name in ("opencode.json", "opencode.jsonc"):
            text = _read(home / ".config" / "opencode" / name)
            model = re.search(r'^\s*"model"\s*:\s*"([^"]+)"', text, re.M)
            if not request.model and model:
                out.update(model_effective=model.group(1), model_source=f"~/.config/opencode/{name} model")
                break
    if out["effort_effective"] is None:
        out["effort_source"] = "runtime built-in default (not reported by the runtime)"
    if out["model_effective"] is None:
        out["model_source"] = "runtime built-in default (not reported by the runtime)"
    return out


# --- the run ------------------------------------------------------------------------

def classify(*, exit_code: Optional[int], timed_out: bool, timeout: float, stdout: str, stderr: str, envelope_ok: bool,
             cost_usd: Any, budget_usd: Optional[float], protected_changed: bool) -> Tuple[str, Optional[str]]:
    """Status and reason of one run from what the process left behind.

    Pure, so a finished round can be re-classified offline (bench.py --regrade) after a rule
    changes. Quota, overload and model errors count only when the run actually failed — a
    non-zero exit or a broken envelope. A clean run whose *answer* quotes "rate limit" is a
    pass (observed 2026-09-14: two Codex runs that read references/runtimes.md were lost to it).
    """
    failed = timed_out or exit_code != 0 or not envelope_ok
    kind, message = _diagnose(stdout, stderr) if failed else (None, "")
    budget_hit = budget_usd is not None and isinstance(cost_usd, (int, float)) and cost_usd >= budget_usd
    if timed_out:
        status, reason = "BLOCKED", f"timeout after {timeout:.0f}s"
    elif kind == "quota":
        # The provider refused to serve: no evidence about the skill either way.
        status, reason = "NOT_RUN", "runtime quota or usage limit: " + sanitize(message)
    elif not envelope_ok and kind == "unavailable":
        # The provider failed to serve (5xx, overload, dropped connection): no evidence either way.
        status, reason = "NOT_RUN", "provider unavailable: " + sanitize(message)
    elif exit_code != 0 and budget_hit:
        # The per-run cap stopped the model mid-task: it says nothing about the skill.
        status, reason = "NOT_RUN", f"per-run budget of US$ {budget_usd:.4f} reached (spent {cost_usd:.4f})"
    elif exit_code != 0 and kind == "model":
        status, reason = "NOT_RUN", "runtime rejected the model: " + sanitize((stderr.strip() or message)[:300])
    elif exit_code != 0:
        status, reason = "FAIL", f"exit {exit_code}: " + sanitize(stderr.strip()[:300])
    else:
        status = "PASS" if envelope_ok else "FAIL"
        reason = None if envelope_ok else "runtime envelope missing or reported an error"
    if protected_changed:
        status, reason = "FAIL", "a protected path changed during the run"
    return status, reason


def run(runtime: str, request: RunRequest) -> Dict[str, Any]:
    if runtime not in RUNTIMES:
        raise ValueError(f"unknown runtime: {runtime}")
    started_at = utc_now()
    record: Dict[str, Any] = {
        "schema_version": 1, "runtime": runtime, "version": runtime_version(runtime, request.executable),
        "model_requested": request.model, "model_observed": None, "provider": request.provider,
        "effort_requested": request.effort,
        "status": "NOT_RUN", "reason": None, "exit_code": None, "started_at": started_at, "ended_at": None,
        "duration_seconds": None, "usage": None, "usage_source": None, "cost_usd": None, "cost_source": None,
        "command": None, "workspace": sanitize(str(request.workspace)), "protected_changed": False,
        "stdout_path": None, "stderr_path": None,
    }
    try:
        prepared = prepare(runtime, request)
    except RuntimeBlocked as exc:
        record.update(status="BLOCKED", reason=str(exc), ended_at=utc_now())
        return record
    command = build_command(runtime, request, prepared)
    record["command"] = [sanitize(part) for part in command]
    if not shutil.which(command[0]):
        record.update(status="NOT_RUN", reason=f"executable not found: {command[0]}", ended_at=utc_now())
        return record
    before = {str(p): snapshot(p) for p in request.protected_paths}
    env = {k: os.environ[k] for k in request.env_passthrough if k in os.environ}
    env.setdefault("LC_ALL", "C")
    env.pop("CLAUDECODE", None)
    env.update(prepared.get("env", {}))
    record["env_overrides"] = sorted(prepared.get("env", {}))
    record.update(effective_settings(runtime, request, env))
    outcome = run_process(command, request.workspace, env, request.timeout)
    after = {str(p): snapshot(p) for p in request.protected_paths}
    record["protected_changed"] = before != after
    record["protected_diff"] = sorted(
        f"{sanitize(root)}/{key}" for root in before
        for key in set(before[root]) | set(after.get(root, {}))
        if before[root].get(key) != after.get(root, {}).get(key))[:20]
    record["stdout_path"] = str(request.run_dir / "stdout.txt")
    record["stderr_path"] = str(request.run_dir / "stderr.txt")
    Path(record["stdout_path"]).write_text(sanitize(outcome["stdout"]), encoding="utf-8")
    Path(record["stderr_path"]).write_text(sanitize(outcome["stderr"]), encoding="utf-8")
    record.update(exit_code=outcome["exit_code"], duration_seconds=outcome["duration_seconds"], ended_at=utc_now())

    combined = outcome["stderr"] + "\n" + outcome["stdout"]
    # Parse first, always. A failed run still spent tokens and money, and the protocol puts
    # failures, retries and fallback in the numerator of cost per success.
    try:
        parsed = parse_output(runtime, request, prepared, outcome["stdout"])
    except Exception as exc:  # a malformed envelope must not hide the exit code
        parsed = {"result_text": None, "usage": None, "cost_usd": None, "cost_source": None,
                  "model_observed": None, "usage_source": None, "envelope_ok": False, "parse_error": str(exc)}
    record.update({k: parsed.get(k) for k in ("usage", "usage_source", "cost_usd", "cost_source", "model_observed")})
    if parsed.get("effort_observed"):
        record["effort_observed"] = parsed["effort_observed"]
    record["extra"] = parsed.get("extra")
    if parsed.get("models_involved"):
        record["models_involved"] = parsed["models_involved"]
    if parsed.get("result_text"):
        record["result_path"] = str(request.run_dir / "result.txt")
        Path(record["result_path"]).write_text(sanitize(parsed["result_text"]), encoding="utf-8")

    record["envelope_ok"] = bool(parsed.get("envelope_ok"))
    record["timed_out"] = bool(outcome["timed_out"])
    status, reason = classify(exit_code=outcome["exit_code"], timed_out=outcome["timed_out"], timeout=request.timeout,
                              stdout=outcome["stdout"], stderr=outcome["stderr"], envelope_ok=record["envelope_ok"],
                              cost_usd=record.get("cost_usd"), budget_usd=request.budget_usd,
                              protected_changed=record["protected_changed"])
    record.update(status=status, reason=reason)
    (request.run_dir / "record.json").write_text(json.dumps(record, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return record
