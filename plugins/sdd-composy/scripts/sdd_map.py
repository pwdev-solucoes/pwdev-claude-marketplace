#!/usr/bin/env python3
"""Build a deterministic, read-only evidence inventory for a repository.

The mapper deliberately describes observations (files, manifests, commands and
directory boundaries).  It does not attempt to infer architecture or execute
commands discovered in manifests.
"""

from __future__ import annotations

import argparse
import datetime as _dt
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile
from typing import Any, Iterable
from sdd_language import resolve_language


OKF_VERSION = "0.2"
DEFAULT_CONTEXT = ".planning/sdd-composy/context"

# These names are excluded before opening a file.  The list intentionally errs
# on the side of omission: a map is useful without secret material.
_SECRET_PARTS = {
    ".env", "credentials", "credential", "secret", "secrets", "token",
    "tokens", "private-key", "private_key", "apikey", "api-key", "password",
    "certificate", "certificates",
}
_SECRET_SUFFIXES = {".pem", ".key", ".p12", ".pfx", ".crt", ".cer"}
_SKIP_DIRS = {".git", ".hg", ".svn", "node_modules", "vendor", "target",
              "__pycache__", ".venv", "venv", "dist", "build", ".tox",
              ".mypy_cache", ".pytest_cache", ".worktrees"}
_LANGUAGE_SUFFIXES = {
    ".py": "Python", ".js": "JavaScript", ".jsx": "JavaScript",
    ".ts": "TypeScript", ".tsx": "TypeScript", ".go": "Go",
    ".rs": "Rust", ".java": "Java", ".kt": "Kotlin", ".rb": "Ruby",
    ".php": "PHP", ".swift": "Swift", ".c": "C", ".h": "C/C++",
    ".cpp": "C++", ".cs": "C#", ".sh": "Shell", ".vue": "Vue",
}
_MANIFESTS = {
    "package.json", "pyproject.toml", "requirements.txt", "Pipfile",
    "Cargo.toml", "go.mod", "composer.json", "Gemfile", "pom.xml",
    "build.gradle", "Makefile", "justfile", "Taskfile.yml",
}


def _safe_relative(path: Path, root: Path) -> str:
    # Keep this lexical. Resolving a repository symlink can point outside the
    # repository and must never turn a harmless inventory entry into a crash.
    return path.relative_to(root).as_posix()


def _sensitive(relative: str) -> bool:
    path = Path(relative)
    lowered = [part.lower() for part in path.parts]
    name = path.name.lower()
    if any(part in _SECRET_PARTS or part.startswith(".env") for part in lowered):
        return True
    if name.endswith(tuple(_SECRET_SUFFIXES)):
        return True
    if ("fleet" in lowered or ".planning" in lowered) and ("env" in name or name.startswith(".env")):
        return True
    return False


def _files(root: Path, excluded_dir: Path | None = None) -> list[tuple[str, Path]]:
    result: list[tuple[str, Path]] = []
    for current, dirs, names in os.walk(root):
        current_path = Path(current)
        dirs[:] = sorted(
            d for d in dirs
            if d not in _SKIP_DIRS
            and (excluded_dir is None or current_path / d != excluded_dir)
            and not (current_path / d).is_symlink()
            and not _sensitive(_safe_relative(current_path / d, root))
        )
        for name in sorted(names):
            path = current_path / name
            relative = _safe_relative(path, root)
            if not _sensitive(relative) and not path.is_symlink():
                result.append((relative, path))
    return result


def _read_text(path: Path, limit: int = 250_000) -> str | None:
    try:
        if path.stat().st_size > limit:
            return None
        return path.read_text(encoding="utf-8", errors="replace")
    except (OSError, UnicodeError):
        return None


def _git_commit(root: Path) -> str:
    try:
        proc = subprocess.run(["git", "rev-parse", "HEAD"], cwd=root,
                              text=True, capture_output=True, check=True, timeout=5)
        value = proc.stdout.strip()
        return value if re.fullmatch(r"[0-9a-f]{40}", value) else "UNKNOWN"
    except (OSError, subprocess.SubprocessError):
        return "UNKNOWN"


def _manifest_commands(relative: str, path: Path) -> list[dict[str, str]]:
    commands: list[dict[str, str]] = []
    name = path.name
    if name == "package.json":
        try:
            data = json.loads(_read_text(path) or "{}")
            for script, value in sorted((data.get("scripts") or {}).items()):
                if isinstance(value, str):
                    commands.append({"name": script, "command": f"npm run {script}", "source": relative})
        except (json.JSONDecodeError, TypeError, OSError):
            pass
    elif name == "pyproject.toml":
        try:
            text = _read_text(path) or ""
            try:
                import tomllib
                data = tomllib.loads(text)
            except ImportError:  # Python 3.10: retain stdlib-only operation.
                data = {}
            project = data.get("project", {})
            for script in sorted((project.get("scripts") or {})):
                commands.append({"name": script, "command": f"python -m {script}", "source": relative})
            tool = data.get("tool", {})
            pytest = tool.get("pytest", {})
            pytest_config = pytest or tool.get("pytest", {}).get("ini_options", {})
            if pytest_config or "pytest" in tool or re.search(r"(?m)^\[tool\.pytest(?:\.|\])", text):
                commands.append({"name": "test", "command": "pytest", "source": relative})
        except (ValueError, OSError):
            pass
    elif name in {"Makefile", "justfile"}:
        text = _read_text(path) or ""
        for target in sorted(set(re.findall(r"(?m)^([A-Za-z][A-Za-z0-9_.-]*):", text))):
            commands.append({"name": target, "command": f"make {target}" if name == "Makefile" else f"just {target}", "source": relative})
    elif name == "Taskfile.yml":
        text = _read_text(path) or ""
        for target in sorted(set(re.findall(r"(?m)^  ([A-Za-z][A-Za-z0-9_.-]*):", text))):
            commands.append({"name": target, "command": f"task {target}", "source": relative})
    elif name == "Cargo.toml":
        commands.extend([
            {"name": "build", "command": "cargo build", "source": relative},
            {"name": "test", "command": "cargo test", "source": relative},
        ])
    elif name == "go.mod":
        commands.append({"name": "test", "command": "go test ./...", "source": relative})
    elif name == "requirements.txt":
        commands.append({"name": "install", "command": "python -m pip install -r requirements.txt", "source": relative})
    elif name == "composer.json":
        commands.append({"name": "test", "command": "composer test", "source": relative})
    return commands


def _inventory(root: Path, excluded_dir: Path | None = None) -> dict[str, Any]:
    entries = _files(root, excluded_dir)
    manifests = [{"path": rel, "name": Path(rel).name} for rel, _ in entries if Path(rel).name in _MANIFESTS]
    languages: dict[str, int] = {}
    for relative, _ in entries:
        language = _LANGUAGE_SUFFIXES.get(Path(relative).suffix.lower())
        if language:
            languages[language] = languages.get(language, 0) + 1
    commands: list[dict[str, str]] = []
    for relative, path in entries:
        if Path(relative).name in _MANIFESTS:
            commands.extend(_manifest_commands(relative, path))
    commands = sorted(commands, key=lambda x: (x["command"], x["source"], x["name"]))

    top_dirs = sorted({parts[0] for relative, _ in entries if len(parts := Path(relative).parts) > 1 and parts[0] not in _SKIP_DIRS})
    modules = [{"path": name, "evidence": "top-level directory containing readable files"} for name in top_dirs]
    domain_terms: dict[str, list[str]] = {}
    for relative, _ in entries:
        parts = Path(relative).parts
        for term in parts[:-1]:
            normalized = re.sub(r"[-_]+", " ", term).strip().lower()
            if normalized and normalized not in _SKIP_DIRS and len(normalized) > 2:
                domain_terms.setdefault(normalized, []).append(relative)
    domain = [{"term": term, "evidence": sorted(paths)[:20], "confidence": "low"}
              for term, paths in sorted(domain_terms.items()) if len(paths) >= 1][:50]
    boundaries = [{"path": name, "evidence": "observed top-level directory boundary", "confidence": "low"}
                  for name in top_dirs]
    return {
        "languages": [{"name": name, "file_count": languages[name]} for name in sorted(languages)],
        "manifests": manifests,
        "commands": commands,
        "modules": modules,
        "boundaries": boundaries,
        "domain_evidence": domain,
        "files_observed": len(entries),
        "excluded_policy": "secret and environment-like paths are excluded before reading",
    }


def _validated_context(root: Path, output_dir: Path | None = None) -> tuple[Path, Path]:
    """Resolve the repository and context once, refusing external output paths."""
    lexical_root = Path(os.path.abspath(root))
    if not lexical_root.is_dir():
        raise ValueError(f"repository root is not a directory: {lexical_root}")
    context = output_dir or lexical_root / DEFAULT_CONTEXT
    if not context.is_absolute():
        context = lexical_root / context
    context = Path(os.path.abspath(context))
    try:
        relative = context.relative_to(lexical_root)
    except ValueError as exc:
        raise ValueError("output directory must be inside repository root") from exc
    current = lexical_root
    for part in relative.parts:
        current = current / part
        if current.is_symlink():
            raise ValueError(f"output directory has symlink ancestor: {current}")
    root = lexical_root.resolve()
    context = root.joinpath(*relative.parts)
    return root, context


def _reject_symlink_path(path: Path, root: Path) -> None:
    """Reject a controlled destination or any of its repository ancestors."""
    current = root
    for part in path.relative_to(root).parts:
        current = current / part
        if current.is_symlink():
            raise ValueError(f"controlled path has symlink ancestor: {current}")


def build_map(root: Path, output_dir: Path | None = None) -> dict[str, Any]:
    root, context = _validated_context(root, output_dir)
    source_commit = _git_commit(root)
    inventory = _inventory(root, context)
    previous_path = context / "codebase.json"
    _reject_symlink_path(previous_path, root)
    previous_commit = None
    if previous_path.is_file() and not _sensitive(_safe_relative(previous_path, root)):
        try:
            previous = json.loads(previous_path.read_text(encoding="utf-8"))
            previous_commit = previous.get("source_commit")
        except (OSError, json.JSONDecodeError):
            previous_commit = None
    stale = bool(previous_commit and previous_commit != source_commit and source_commit != "UNKNOWN")
    return {
        "schema": "sdd-composy.codebase",
        "schema_version": "0.2",
        "okf_version": OKF_VERSION,
        "repository": str(root),
        "source_commit": source_commit,
        "mapped_commit": source_commit,
        "staleness": {"stale": stale, "previous_commit": previous_commit, "reason": "repository commit changed" if stale else None},
        "observation_only": True,
        "confidence": "medium" if inventory["manifests"] or inventory["languages"] else "low",
        **inventory,
    }


def _timestamp() -> str:
    return _dt.datetime.now(_dt.timezone.utc).replace(microsecond=0).isoformat()


def _okf_doc(doc_type: str, title: str, body: str, source_commit: str) -> str:
    return (f"---\ntype: {doc_type}\nokf_version: \"{OKF_VERSION}\"\n"
            f"generated_by: sdd-map\ngenerated_at: {_timestamp()}\n"
            f"source_commit: {source_commit}\n---\n\n# {title}\n\n{body.rstrip()}\n")


def _atomic_write_text(path: Path, content: str) -> None:
    """Publish one document through a same-directory temporary file."""
    descriptor, temporary = tempfile.mkstemp(
        prefix=f".{path.name}.", suffix=".tmp", dir=path.parent
    )
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
            handle.write(content)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
    except BaseException:
        try:
            os.unlink(temporary)
        except OSError:
            pass
        raise


def write_map(root: Path, data: dict[str, Any], output_dir: Path | None = None) -> Path:
    root, context = _validated_context(root, output_dir)
    resolved = resolve_language(root)
    if 'language' not in resolved:
        return resolved
    codebase = context / "codebase.json"
    for name in ("codebase.json", "project.md", "stack.md", "domain.md", "pitfalls.md"):
        _reject_symlink_path(context / name, root)
    context.mkdir(parents=True, exist_ok=True)
    serialized = json.dumps(data, indent=2, sort_keys=True) + "\n"
    languages = ", ".join(f'{x["name"]} ({x["file_count"]})' for x in data["languages"]) or "none observed"
    commands = "\n".join(f'- `{x["command"]}` (from `{x["source"]}`)' for x in data["commands"]) or "- none observed"
    documents = {
        "project.md": _okf_doc("context-project", "Project context", f"Repository: `{data['repository']}`.\n\nThis is a read-only inventory; it records evidence and does not assert architecture.\n", data["source_commit"]),
        "stack.md": _okf_doc("context-stack", "Observed stack", f"Languages: {languages}.\n\nCommands observed in manifests (not executed):\n{commands}\n", data["source_commit"]),
    }
    domain = "\n".join(f'- `{x["term"]}` — {", ".join(x["evidence"][:5])}' for x in data["domain_evidence"]) or "- no domain terms observed"
    documents.update({
        "domain.md": _okf_doc("context-domain", "Domain evidence", f"Terms are file-path evidence only; confidence is deliberately low.\n\n{domain}\n", data["source_commit"]),
        "pitfalls.md": _okf_doc("context-pitfalls", "Observed map caveats", "The map is bounded by readable, non-secret files and must be refreshed when the source commit changes.\n", data["source_commit"]),
    })
    if resolved['language'] == 'pt-BR':
        replacements = {
            'Project context': 'Contexto do projeto', 'Repository:': 'Repositório:',
            'This is a read-only inventory; it records evidence and does not assert architecture.': 'Este inventário somente leitura registra evidências e não define a arquitetura.',
            'Observed stack': 'Stack observada', 'Languages:': 'Linguagens:',
            'Commands observed in manifests (not executed):': 'Comandos observados nos manifestos (não executados):',
            '(from ': '(origem ', 'none observed': 'nenhum observado',
            'Domain evidence': 'Evidências de domínio', 'no domain terms observed': 'nenhum termo de domínio observado',
            'Terms are file-path evidence only; confidence is deliberately low.': 'Os termos são apenas evidências dos caminhos de arquivos; a confiança é deliberadamente baixa.',
            'Observed map caveats': 'Limitações do mapa observado',
            'The map is bounded by readable, non-secret files and must be refreshed when the source commit changes.': 'O mapa abrange arquivos legíveis e sem segredos e deve ser atualizado quando o commit de origem mudar.',
        }
        for name, content in documents.items():
            for source, target in replacements.items():
                content = content.replace(source, target)
            documents[name] = content
    publications = {codebase: serialized}
    publications.update({context / name: content for name, content in documents.items()})
    temporaries: dict[Path, str] = {}
    previous = {path: path.read_bytes() if path.is_file() else None for path in publications}
    published: list[Path] = []
    try:
        for path, content in publications.items():
            descriptor, temporary = tempfile.mkstemp(
                prefix=f".{path.name}.", suffix=".tmp", dir=context
            )
            temporaries[path] = temporary
            with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
                handle.write(content)
                handle.flush()
                os.fsync(handle.fileno())
        for path, temporary in temporaries.items():
            os.replace(temporary, path)
            published.append(path)
    except BaseException:
        for path in reversed(published):
            old = previous[path]
            if old is None:
                try:
                    path.unlink()
                except FileNotFoundError:
                    pass
            else:
                descriptor, rollback = tempfile.mkstemp(
                    prefix=f".{path.name}.", suffix=".tmp", dir=context
                )
                with os.fdopen(descriptor, "wb") as handle:
                    handle.write(old)
                    handle.flush()
                    os.fsync(handle.fileno())
                os.replace(rollback, path)
        raise
    finally:
        for temporary in temporaries.values():
            try:
                os.unlink(temporary)
            except FileNotFoundError:
                pass
    return codebase


def main(argv: Iterable[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=Path.cwd())
    parser.add_argument("--output-dir", type=Path)
    parser.add_argument("--write", action="store_true", help="write context documents and codebase.json")
    args = parser.parse_args(argv)
    try:
        root = args.repo_root.resolve()
        resolved = resolve_language(root)
        if 'language' not in resolved:
            print(json.dumps(resolved, sort_keys=True))
            return 2
        data = build_map(root, args.output_dir)
        if args.write:
            write_map(root, data, args.output_dir)
        print(json.dumps(data, indent=2, sort_keys=True))
        return 0
    except (OSError, ValueError) as exc:
        print(f"sdd-map: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
