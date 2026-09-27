#!/usr/bin/env python3
"""pwdev-feat codebase evidence scan — deterministic and read-only.

Observes languages, manifests, frameworks, declared commands (never executed),
style tooling, testing setup, CI, containers, migrations, modules, sensitive
areas and the project instructions files. Secret-looking paths are skipped
before any file is opened. Stdlib only (Python >= 3.9).

Usage:
  feat_map.py [--repo-root DIR]              print the evidence JSON
  feat_map.py [--repo-root DIR] --write      also publish .planning/feat/context/codebase.json
  feat_map.py [--repo-root DIR] --staleness  print only the staleness record
"""
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any

SCHEMA = "pwdev-feat.codebase"
SCHEMA_VERSION = "1"
CONTEXT_DIR = Path(".planning/feat/context")

SKIP_DIRS = {
    ".git", ".hg", ".svn", "node_modules", "vendor", "target", "__pycache__", ".venv", "venv",
    "dist", "build", ".tox", ".mypy_cache", ".pytest_cache", ".worktrees", ".next", ".nuxt",
    ".output", "coverage", ".gradle", ".idea", ".vscode", ".planning", ".turbo", ".cache",
}
SKIP_PATHS = {"storage", "bootstrap/cache", "public/build", "public/hot"}
SECRET_PARTS = {"credentials", "credential", "secret", "secrets", "private-key", "private_key", "apikey", "api-key"}
SECRET_SUFFIXES = (".pem", ".key", ".p12", ".pfx", ".crt", ".cer", ".keystore", ".jks")
SECRET_NAMES = {".npmrc", ".pypirc", ".netrc", ".git-credentials", ".dockercfg", ".htpasswd",
                "id_rsa", "id_dsa", "id_ecdsa", "id_ed25519", "auth.json"}
SAFE_ENV = {".env.example", ".env.sample", ".env.template", ".env.dist"}

LANGUAGES = {
    ".py": "Python", ".js": "JavaScript", ".mjs": "JavaScript", ".cjs": "JavaScript", ".jsx": "JavaScript",
    ".ts": "TypeScript", ".tsx": "TypeScript", ".vue": "Vue", ".svelte": "Svelte", ".go": "Go",
    ".rs": "Rust", ".java": "Java", ".kt": "Kotlin", ".rb": "Ruby", ".php": "PHP", ".swift": "Swift",
    ".c": "C", ".h": "C/C++", ".cpp": "C++", ".cs": "C#", ".sh": "Shell", ".dart": "Dart",
    ".ex": "Elixir", ".exs": "Elixir", ".sql": "SQL",
}
MANIFESTS = {
    "package.json", "pyproject.toml", "requirements.txt", "Pipfile", "setup.py", "Cargo.toml", "go.mod",
    "composer.json", "Gemfile", "pom.xml", "build.gradle", "build.gradle.kts", "mix.exs", "pubspec.yaml",
    "Makefile", "justfile", "Taskfile.yml",
}
STYLE_CONFIGS = re.compile(
    r"^(\.editorconfig|\.prettierrc.*|prettier\.config\..*|\.eslintrc.*|eslint\.config\..*|biome\.jsonc?|"
    r"tsconfig(\..*)?\.json|phpcs\.xml(\.dist)?|phpstan\.neon(\.dist)?|pint\.json|\.php-cs-fixer.*\.php|"
    r"ruff\.toml|\.ruff\.toml|\.flake8|setup\.cfg|\.rubocop\.yml|\.golangci\.ya?ml|rustfmt\.toml|\.stylelintrc.*)$"
)
TEST_CONFIGS = {
    "vitest": re.compile(r"^vitest\.config\..*$"), "jest": re.compile(r"^jest\.config\..*$"),
    "phpunit": re.compile(r"^phpunit\.xml(\.dist)?$"), "pest": re.compile(r"^Pest\.php$"),
    "pytest": re.compile(r"^(pytest\.ini|conftest\.py)$"), "playwright": re.compile(r"^playwright\.config\..*$"),
    "cypress": re.compile(r"^cypress\.config\..*$"), "karma": re.compile(r"^karma\.conf\..*$"),
}
TEST_FILE = re.compile(r"(\.test\.|\.spec\.|_test\.go$|Test\.php$|^test_.*\.py$|_test\.py$|_spec\.rb$)")
TEST_DIRS = {"tests", "test", "__tests__", "spec", "e2e", "cypress"}
SENSITIVE_AREAS = re.compile(r"(auth|login|password|payment|billing|checkout|stripe|webhook|token|permission|policy|admin|oauth|sso|crypt)", re.I)
FRAMEWORK_DEPS = {
    "laravel/framework": "Laravel", "symfony/framework-bundle": "Symfony", "vue": "Vue", "nuxt": "Nuxt",
    "react": "React", "next": "Next.js", "@angular/core": "Angular", "svelte": "Svelte", "express": "Express",
    "@nestjs/core": "NestJS", "fastify": "Fastify", "vite": "Vite", "tailwindcss": "Tailwind CSS",
    "primevue": "PrimeVue", "reka-ui": "Reka UI", "@inertiajs/vue3": "Inertia", "django": "Django",
    "fastapi": "FastAPI", "flask": "Flask", "rails": "Rails", "gin-gonic/gin": "Gin",
    "@playwright/test": "Playwright Test", "vitest": "Vitest", "jest": "Jest", "pestphp/pest": "Pest",
    "phpunit/phpunit": "PHPUnit", "pytest": "pytest", "prisma": "Prisma", "typeorm": "TypeORM",
    "sequelize": "Sequelize", "sqlalchemy": "SQLAlchemy",
}
INSTRUCTION_FILES = ("AGENTS.md", "CLAUDE.md")


def sensitive(relative: str) -> bool:
    path = Path(relative)
    name = path.name.lower()
    if name in SAFE_ENV:
        return False
    lowered = [p.lower() for p in path.parts]
    if any(p.startswith(".env") for p in lowered):
        return True
    if any(p in SECRET_PARTS for p in lowered):
        return True
    if name.endswith(SECRET_SUFFIXES) or name in SECRET_NAMES:
        return True
    return name.split(".", 1)[0] in {"credentials", "secrets", "service-account", "service_account"}


def walk(root: Path) -> tuple[list[str], int]:
    files: list[str] = []
    excluded = 0
    for current, dirs, names in os.walk(root):
        cur = Path(current)
        keep = []
        for d in sorted(dirs):
            rel = (cur / d).relative_to(root).as_posix()
            if d in SKIP_DIRS or rel in SKIP_PATHS or (cur / d).is_symlink():
                continue
            if sensitive(rel):
                excluded += 1
                continue
            keep.append(d)
        dirs[:] = keep
        for name in sorted(names):
            path = cur / name
            rel = path.relative_to(root).as_posix()
            if path.is_symlink():
                continue
            if sensitive(rel):
                excluded += 1
                continue
            files.append(rel)
    return sorted(files), excluded


def read_text(path: Path, limit: int = 300_000) -> str:
    try:
        if path.stat().st_size > limit:
            return ""
        return path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return ""


def git(root: Path, *args: str) -> str:
    try:
        proc = subprocess.run(["git", *args], cwd=root, text=True, capture_output=True, timeout=10)
        return proc.stdout.strip() if proc.returncode == 0 else ""
    except (OSError, subprocess.SubprocessError):
        return ""


def manifest_facts(root: Path, rel: str) -> tuple[list[dict], list[str]]:
    """Return (commands, dependency names) declared by one manifest. Nothing is executed."""
    path, name = root / rel, Path(rel).name
    text = read_text(path)
    commands: list[dict] = []
    deps: list[str] = []
    if name == "package.json":
        try:
            data = json.loads(text or "{}")
        except json.JSONDecodeError:
            data = {}
        runner = "pnpm" if (root / Path(rel).parent / "pnpm-lock.yaml").exists() else \
            "yarn" if (root / Path(rel).parent / "yarn.lock").exists() else "npm run"
        for script, value in sorted((data.get("scripts") or {}).items()):
            if isinstance(value, str):
                commands.append({"name": script, "command": f"{runner} {script}", "declared": value, "source": rel})
        for key in ("dependencies", "devDependencies", "peerDependencies"):
            deps += sorted((data.get(key) or {}).keys())
    elif name == "composer.json":
        try:
            data = json.loads(text or "{}")
        except json.JSONDecodeError:
            data = {}
        for script, value in sorted((data.get("scripts") or {}).items()):
            commands.append({"name": script, "command": f"composer {script}",
                             "declared": value if isinstance(value, str) else " && ".join(map(str, value)),
                             "source": rel})
        for key in ("require", "require-dev"):
            deps += sorted((data.get(key) or {}).keys())
        if (root / Path(rel).parent / "artisan").exists():
            commands.append({"name": "test", "command": "php artisan test", "declared": "artisan", "source": rel})
    elif name == "pyproject.toml":
        deps += re.findall(r'(?m)^\s*"?([A-Za-z0-9_.-]+)(?:\[.*?\])?\s*[<>=~!;"]', text)
        if re.search(r"(?m)^\[tool\.pytest", text):
            commands.append({"name": "test", "command": "pytest", "declared": "[tool.pytest]", "source": rel})
        if re.search(r"(?m)^\[tool\.ruff", text):
            commands.append({"name": "lint", "command": "ruff check .", "declared": "[tool.ruff]", "source": rel})
    elif name == "requirements.txt":
        deps += re.findall(r"(?m)^([A-Za-z0-9_.-]+)", text)
    elif name in ("Makefile", "justfile"):
        for target in sorted(set(re.findall(r"(?m)^([A-Za-z][A-Za-z0-9_.-]*)[ \t]*:(?![:=])", text))):
            commands.append({"name": target, "command": f"{'make' if name == 'Makefile' else 'just'} {target}",
                             "declared": "target", "source": rel})
    elif name == "Taskfile.yml":
        for target in sorted(set(re.findall(r"(?m)^  ([A-Za-z][A-Za-z0-9_.-]*):", text))):
            commands.append({"name": target, "command": f"task {target}", "declared": "task", "source": rel})
    elif name == "go.mod":
        commands.append({"name": "test", "command": "go test ./...", "declared": "go.mod", "source": rel})
        deps += re.findall(r"(?m)^\s*([a-z0-9.-]+\.[a-z]+/[^\s]+)\s+v", text)
    elif name == "Cargo.toml":
        commands += [{"name": "test", "command": "cargo test", "declared": "Cargo.toml", "source": rel},
                     {"name": "lint", "command": "cargo clippy", "declared": "Cargo.toml", "source": rel}]
    elif name == "Gemfile":
        deps += re.findall(r"""(?m)^\s*gem\s+['"]([^'"]+)""", text)
    return commands, deps


def build(root: Path) -> dict[str, Any]:
    files, excluded = walk(root)
    languages: dict[str, int] = {}
    for rel in files:
        lang = LANGUAGES.get(Path(rel).suffix.lower())
        if lang:
            languages[lang] = languages.get(lang, 0) + 1

    manifests = [rel for rel in files if Path(rel).name in MANIFESTS]
    commands: list[dict] = []
    deps: set[str] = set()
    for rel in manifests:
        c, d = manifest_facts(root, rel)
        commands += c
        deps.update(x.lower() for x in d)
    frameworks = sorted({label for dep, label in FRAMEWORK_DEPS.items() if dep.lower() in deps})

    names = {rel: Path(rel).name for rel in files}
    style = sorted(rel for rel, n in names.items() if STYLE_CONFIGS.match(n))
    test_frameworks = sorted({fw for rel, n in names.items() for fw, rx in TEST_CONFIGS.items() if rx.match(n)})
    test_files = [rel for rel, n in names.items() if TEST_FILE.search(n)]
    test_dirs = sorted({Path(rel).parts[0] for rel in test_files if Path(rel).parts[0] in TEST_DIRS} |
                       {p for p in TEST_DIRS if (root / p).is_dir() and p not in SKIP_DIRS})
    e2e = sorted({fw for fw in ("playwright", "cypress") if fw in test_frameworks} |
                 ({"playwright"} if "@playwright/test" in deps else set()))
    scenarios = sorted(rel for rel in files if rel.endswith(".scenario.json"))

    ci = sorted(rel for rel in files if rel.startswith(".github/workflows/") or rel in
                (".gitlab-ci.yml", "bitbucket-pipelines.yml", "azure-pipelines.yml", ".circleci/config.yml", "Jenkinsfile"))
    containers = sorted(rel for rel, n in names.items() if n == "Dockerfile" or n.startswith("Dockerfile.")
                        or re.match(r"^(docker-)?compose(\..*)?\.ya?ml$", n))
    migrations = sorted({str(Path(rel).parent) for rel in files
                         if re.search(r"(^|/)(migrations|migrate|alembic/versions|db/migrate)/", rel)})

    modules: dict[str, int] = {}
    for rel in files:
        parts = Path(rel).parts
        if len(parts) > 1 and LANGUAGES.get(Path(rel).suffix.lower()) and parts[0] not in TEST_DIRS:
            key = "/".join(parts[:2]) if parts[0] in ("src", "app", "lib", "packages", "apps", "internal", "cmd", "resources") and len(parts) > 2 else parts[0]
            modules[key] = modules.get(key, 0) + 1
    sensitive_areas = sorted({str(Path(rel).parent) if Path(rel).parent != Path(".") else rel
                              for rel in files if LANGUAGES.get(Path(rel).suffix.lower()) and SENSITIVE_AREAS.search(rel)})

    commit = git(root, "rev-parse", "HEAD")
    recent = git(root, "log", "--format=%s", "-20").splitlines()
    conventional = sum(bool(re.match(r"^(feat|fix|chore|docs|refactor|test|style|perf|build|ci|revert)(\(.+\))?!?:", s)) for s in recent)

    return {
        "schema": SCHEMA,
        "schema_version": SCHEMA_VERSION,
        "source_commit": commit or "UNKNOWN",
        "observation_only": True,
        "files_observed": len(files),
        "excluded_sensitive": excluded,
        "languages": [{"name": k, "files": languages[k]} for k in sorted(languages, key=lambda k: (-languages[k], k))],
        "manifests": manifests,
        "frameworks": frameworks,
        "commands": sorted(commands, key=lambda c: (c["source"], c["name"])),
        "style_configs": style,
        "testing": {
            "frameworks": test_frameworks,
            "e2e": e2e,
            "test_dirs": test_dirs,
            "test_files": len(test_files),
            "e2e_scenarios": scenarios,
        },
        "ci": ci,
        "containers": containers,
        "migrations": migrations,
        "modules": [{"path": k, "files": modules[k]} for k in sorted(modules)],
        "sensitive_areas": sensitive_areas[:60],
        "instructions_files": [n for n in INSTRUCTION_FILES if (root / n).is_file()],
        "git": {"recent_commits": len(recent), "conventional_commits": conventional},
    }


def staleness(root: Path, current_commit: str) -> dict[str, Any]:
    path = root / CONTEXT_DIR / "codebase.json"
    if not path.is_file():
        return {"exists": False, "stale": True, "previous_commit": None, "current_commit": current_commit,
                "reason": "no published map"}
    try:
        previous = json.loads(path.read_text(encoding="utf-8")).get("source_commit")
    except (OSError, json.JSONDecodeError, AttributeError):
        previous = None
    stale = previous is None or (current_commit not in ("", "UNKNOWN") and previous != current_commit)
    changed = []
    if stale and previous and previous != "UNKNOWN" and current_commit not in ("", "UNKNOWN"):
        changed = git(root, "diff", "--name-only", f"{previous}..{current_commit}").splitlines()
    return {"exists": True, "stale": stale, "previous_commit": previous, "current_commit": current_commit,
            "changed_files": len(changed), "reason": "commit changed" if stale else None}


def publish(root: Path, data: dict[str, Any]) -> Path:
    context = root / CONTEXT_DIR
    for parent in [root / ".planning", root / ".planning/feat", context]:
        if parent.is_symlink():
            raise ValueError(f"refusing to write through symlink {parent}")
    context.mkdir(parents=True, exist_ok=True)
    dest = context / "codebase.json"
    fd, tmp = tempfile.mkstemp(prefix=".codebase.", suffix=".tmp", dir=context)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            handle.write(json.dumps(data, indent=2, sort_keys=True) + "\n")
        os.replace(tmp, dest)
    finally:
        if os.path.exists(tmp):
            os.unlink(tmp)
    return dest


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--repo-root", type=Path, default=Path.cwd())
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--write", action="store_true", help="publish .planning/feat/context/codebase.json")
    group.add_argument("--staleness", action="store_true", help="print only the staleness record")
    args = parser.parse_args(argv)
    root = args.repo_root.resolve()
    if not root.is_dir():
        print(json.dumps({"ok": False, "error": f"not a directory: {root}"}))
        return 2
    if args.staleness:
        print(json.dumps(staleness(root, git(root, "rev-parse", "HEAD") or "UNKNOWN"), indent=2, sort_keys=True))
        return 0
    data = build(root)
    data["staleness"] = staleness(root, data["source_commit"])
    if args.write:
        try:
            data["published"] = str(publish(root, {**data, "staleness": {**data["staleness"], "stale": False}}).relative_to(root))
        except (OSError, ValueError) as exc:
            print(json.dumps({"ok": False, "error": str(exc)}))
            return 2
    print(json.dumps(data, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
