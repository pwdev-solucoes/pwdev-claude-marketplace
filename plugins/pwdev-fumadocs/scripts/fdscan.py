#!/usr/bin/env python3
"""Deterministic, read-only scan of a project for Fumadocs work.

Reports what an agent would otherwise guess: the React framework, package manager, Fumadocs
packages and versions, the content source (Fumadocs MDX Macro API, Config API or another),
the loader's ``baseUrl`` and content directories, which features are already wired (search,
llms.txt, MCP, OG images, OpenAPI, i18n, static export) and a list of known pitfalls found in
the files themselves. Nothing is written and nothing is installed.

    python3 fdscan.py                 # scan the current directory, JSON on stdout
    python3 fdscan.py path/to/app     # scan another directory
    python3 fdscan.py --format text   # human-readable summary

Standard library only. Exit code 0 on a completed scan (findings included), 2 on bad usage.
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
from typing import Dict, Iterable, List, Optional, Tuple

SCHEMA = "pwdev-fdscan/1"
SKIP_DIRS = {
    "node_modules", ".git", ".next", ".source", ".output", ".vercel", ".turbo", ".cache",
    ".react-router", ".tanstack", ".waku", ".astro", "dist", "build", "out", "coverage",
}
CODE_EXT = {".ts", ".tsx", ".js", ".jsx", ".mjs", ".cjs", ".mts", ".cts", ".astro", ".css"}
CONTENT_EXT = {".md", ".mdx"}
MAX_FILE_BYTES = 512 * 1024
MAX_FILES = 20000

FRAMEWORKS = (  # first match wins: meta-frameworks before the router they build on
    ("next", ("next",)),
    ("tanstack-start", ("@tanstack/react-start", "@tanstack/start")),
    ("react-router", ("@react-router/dev", "react-router")),
    ("waku", ("waku",)),
    ("astro", ("astro",)),
)
VITE_FRAMEWORKS = {"tanstack-start", "react-router", "waku", "astro"}
FUMADOCS_PACKAGES = (
    "fumadocs-core", "fumadocs-ui", "fumadocs-mdx", "@fumadocs/cli", "fumadocs-openapi",
    "fumadocs-typescript", "fumadocs-twoslash", "fumadocs-docgen", "@fumadocs/mdx-remote",
    "@fumadocs/base-ui", "@fumadocs/content-collections", "@fumadocs/story",
)
DOCS = "https://www.fumadocs.dev"

FEATURES = {  # feature -> patterns that prove it is wired in code
    "search": (r"fumadocs-core/search/server", r"fumadocs-core/search/client", r"fumadocs-core/search/algolia"),
    "llms": (r"llms\.txt", r"llms-full", r"\bllms\(\s*source", r"getLLMText"),
    "mcp": (r"fumadocs-core/mcp",),
    "og": (r"next/og", r"ImageResponse", r"fumadocs-ui/og", r"@takumi-rs"),
    "openapi": (r"fumadocs-openapi",),
    "i18n": (r"fumadocs-core/i18n",),
    "ai": (r"@ai-sdk/", r"from ['\"]ai['\"]"),
    "feedback": (r"components/feedback", r"<Feedback\b"),
    "typescript": (r"fumadocs-typescript",),
    "twoslash": (r"fumadocs-twoslash",),
}
ROUTE_FEATURES = {  # feature -> route file paths that prove it is wired
    "llms": r"(^|/)(llms[^/]*|api\.llms[^/]*)(/|\.|$)",
    "mcp": r"(^|/)(api/mcp|api\.mcp)(/|\.|$)",
    "og": r"(^|/)og(/|\.)",
}


def read(path: Path) -> str:
    try:
        if path.stat().st_size > MAX_FILE_BYTES:
            return ""
        return path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return ""


def walk(root: Path) -> Iterable[Path]:
    count = 0
    for current, dirs, files in os.walk(root):
        dirs[:] = sorted(d for d in dirs if d not in SKIP_DIRS and not d.startswith("."))
        for name in sorted(files):
            count += 1
            if count > MAX_FILES:
                return
            yield Path(current) / name


def major(version: Optional[str]) -> Optional[int]:
    if not version:
        return None
    found = re.search(r"(\d+)", version)
    return int(found.group(1)) if found else None


def load_package(root: Path) -> Tuple[dict, Dict[str, str]]:
    path = root / "package.json"
    if not path.is_file():
        return {}, {}
    try:
        data = json.loads(read(path) or "{}")
    except json.JSONDecodeError:
        return {"_invalid": True}, {}
    deps: Dict[str, str] = {}
    for key in ("dependencies", "devDependencies", "peerDependencies", "optionalDependencies"):
        deps.update({k: str(v) for k, v in (data.get(key) or {}).items()})
    return data, deps


def installed_version(root: Path, name: str) -> Optional[str]:
    manifest = root / "node_modules" / name / "package.json"
    if not manifest.is_file():
        return None
    try:
        return json.loads(read(manifest) or "{}").get("version")
    except json.JSONDecodeError:
        return None


def package_manager(root: Path, pkg: dict) -> str:
    declared = str(pkg.get("packageManager") or "")
    if declared:
        return declared.split("@")[0]
    for lock, name in (("pnpm-lock.yaml", "pnpm"), ("bun.lock", "bun"), ("bun.lockb", "bun"),
                       ("yarn.lock", "yarn"), ("package-lock.json", "npm")):
        if (root / lock).is_file():
            return name
    return "npm"


def node_version() -> Optional[str]:
    if not shutil.which("node"):
        return None
    try:
        out = subprocess.run(["node", "--version"], capture_output=True, text=True, timeout=10)
    except (OSError, subprocess.SubprocessError):
        return None
    return out.stdout.strip().lstrip("v") or None


def gitignored(root: Path, entry: str) -> bool:
    text = read(root / ".gitignore")
    wanted = entry.strip("/")
    return any(line.strip().strip("/") == wanted for line in text.splitlines())


def rel(root: Path, path: Path) -> str:
    return path.relative_to(root).as_posix()


def resolve_value(code: Dict[str, str], value: str) -> Optional[str]:
    """A quoted literal, or the literal an exported constant of that name is bound to."""
    if value[0] in "'\"`":
        return value[1:-1]
    for text in code.values():
        found = re.search(rf"\bconst\s+{re.escape(value)}\s*(?::[^=]+)?=\s*['\"`]([^'\"`]+)['\"`]", text)
        if found:
            return found.group(1)
    return None


def frontmatter(text: str) -> Optional[str]:
    match = re.match(r"^---\r?\n(.*?)\r?\n---", text, re.S)
    return match.group(1) if match else None


def scan(root: Path, check_node: bool = True) -> dict:
    pkg, deps = load_package(root)
    framework = next((name for name, markers in FRAMEWORKS if any(m in deps for m in markers)), None)

    code: Dict[str, str] = {}
    content: List[Path] = []
    metas: List[Path] = []
    for path in walk(root):
        if path.suffix in CODE_EXT:
            code[rel(root, path)] = read(path)
        elif path.suffix in CONTENT_EXT:
            content.append(path)
        elif path.name.startswith("meta.") and path.suffix in {".json", ".yaml", ".yml"}:
            metas.append(path)

    def files_matching(pattern: str) -> List[str]:
        regex = re.compile(pattern)
        return sorted(p for p, text in code.items() if regex.search(text))

    loaders = files_matching(r"fumadocs-core/source['\"]")
    base_urls = sorted({resolve_value(code, value) for p in loaders
                        for value in re.findall(r"baseUrl\s*:\s*(['\"`][^'\"`]+['\"`]|[A-Za-z_$][\w$]*)", code[p])} - {None})
    source_config = next((p for p in ("source.config.ts", "source.config.mts", "source.config.js")
                          if (root / p).is_file()), None)
    macro_files = files_matching(r"fumadocs-mdx/macro")
    config_text = read(root / source_config) if source_config else ""
    dir_texts = [config_text] + [code[p] for p in macro_files]
    content_dirs = sorted({d for t in dir_texts for d in re.findall(r"\bdir\s*:\s*['\"`]([^'\"`]+)", t)})

    if "fumadocs-mdx" in deps:
        mode = "macro" if macro_files else ("config" if source_config else "unknown")
        content_source = {"kind": "fumadocs-mdx", "mode": mode}
    elif "@fumadocs/content-collections" in deps or "@content-collections/core" in deps:
        content_source = {"kind": "content-collections"}
    elif "@fumadocs/mdx-remote" in deps:
        content_source = {"kind": "mdx-remote"}
    elif loaders:
        content_source = {"kind": "custom"}
    else:
        content_source = {"kind": None}

    packages = {}
    for name in FUMADOCS_PACKAGES:
        if name in deps or installed_version(root, name):
            packages[name] = {"declared": deps.get(name), "installed": installed_version(root, name)}

    features = {name: files_matching("|".join(patterns)) for name, patterns in FEATURES.items()}
    for name, pattern in ROUTE_FEATURES.items():
        routes = [p for p in code if re.search(pattern, p)]
        features[name] = sorted(set(features.get(name, [])) | set(routes))
    features = {name: found for name, found in features.items() if found}
    config_files = [p for p in code if re.fullmatch(r"(next|vite|waku|astro)\.config\.[mc]?[jt]s", p)
                    or re.fullmatch(r"app\.config\.[jt]s", p)]
    static_export = any(re.search(r"output\s*:\s*['\"]export['\"]", code[p]) for p in config_files) or any(
        re.search(r"ssr\s*:\s*false", code[p]) for p in code if re.fullmatch(r"react-router\.config\.[jt]s", p))
    if static_export:
        features["static-export"] = sorted(config_files)

    i18n_parser = None
    for p in features.get("i18n", []):
        found = re.search(r"parser\s*:\s*['\"](dot|dir|none)['\"]", code[p])
        if found:
            i18n_parser = found.group(1)

    pages = [p for p in content if not any(part in SKIP_DIRS for part in p.parts)]
    content_pages = [p for p in pages if any(rel(root, p).startswith(d.strip("./").rstrip("/") + "/")
                                             for d in content_dirs)] if content_dirs else []
    untitled = []
    for page in content_pages:
        head = frontmatter(read(page))
        if head is None or not re.search(r"^title\s*:", head, re.M):
            untitled.append(rel(root, page))

    node = node_version() if check_node else None
    codegen = source_config if content_source.get("mode") == "config" else None
    findings = find_pitfalls(root, framework, deps, packages, code, codegen, untitled, node,
                             bool(loaders), config_files)

    return {
        "schema": SCHEMA,
        "root": str(root),
        "package_json": bool(pkg) and not pkg.get("_invalid"),
        "framework": framework,
        "bundler": "vite" if framework in VITE_FRAMEWORKS else ("next" if framework == "next" else None),
        "package_manager": package_manager(root, pkg) if pkg else None,
        "node": node,
        "react": deps.get("react"),
        "tailwindcss": deps.get("tailwindcss"),
        "fumadocs": packages,
        "installed": bool(packages),
        "content_source": content_source,
        "source_config": source_config,
        "loader_files": loaders,
        "base_urls": base_urls,
        "content_dirs": content_dirs,
        "content": {"pages": len(content_pages), "meta_files": len(metas), "untitled": untitled[:20]},
        "i18n_parser": i18n_parser,
        "features": features,
        "config_files": sorted(config_files),
        "findings": findings,
    }


def find_pitfalls(root, framework, deps, packages, code, codegen_config, untitled, node,
                  has_loader, config_files) -> List[dict]:
    out: List[dict] = []

    def add(fid, severity, message, doc, where=None):
        item = {"id": fid, "severity": severity, "message": message, "doc": f"{DOCS}{doc}"}
        if where:
            item["files"] = where
        out.append(item)

    if not packages:
        return out
    if node and (major(node) or 0) < 22:
        add("FD001", "error", f"Node.js {node}: Fumadocs requires Node.js 22 or newer.", "/docs")
    tw = major(deps.get("tailwindcss"))
    if "fumadocs-ui" in packages and tw is not None and tw < 4:
        add("FD002", "error", f"tailwindcss {deps['tailwindcss']}: Fumadocs UI needs Tailwind CSS 4.",
            "/docs/manual-installation")
    if "fumadocs-ui" in packages:
        if not any("fumadocs-ui/css/" in t for t in code.values()):
            add("FD003", "error", "fumadocs-ui is installed but no stylesheet imports "
                "'fumadocs-ui/css/<theme>.css' and 'fumadocs-ui/css/preset.css'.", "/docs/ui/theme")
        providers = [p for p, t in code.items() if "RootProvider" in t and "<html" in t]
        missing = [p for p in providers if "suppressHydrationWarning" not in code[p]]
        if missing:
            add("FD004", "warn", "<html> wraps RootProvider without suppressHydrationWarning "
                "(theme switch causes hydration warnings).", "/docs/ui/layouts/root-provider", missing)
        if not any("RootProvider" in t for t in code.values()):
            add("FD005", "warn", "fumadocs-ui is installed but RootProvider is never rendered.",
                "/docs/ui/layouts/root-provider")
    versions = {name: major(info.get("installed") or info.get("declared"))
                for name, info in packages.items() if name in ("fumadocs-core", "fumadocs-ui")}
    if len(set(v for v in versions.values() if v is not None)) > 1:
        add("FD006", "warn", f"fumadocs-core and fumadocs-ui majors differ ({versions}); upgrade them together.",
            "/docs")
    if framework == "next" and "fumadocs-mdx" in packages:
        cjs = [p for p in config_files if re.fullmatch(r"next\.config\.(c?js)", p)]
        if cjs:
            add("FD007", "warn", "Fumadocs MDX is ESM-only: prefer next.config.mjs (or a TS config with "
                "the native Node.js TypeScript resolver).", "/docs/mdx/next", cjs)
        configured = [p for p in config_files if p.startswith("next.config") and "createMDX" in code[p]]
        if not configured:
            add("FD008", "error", "Next.js config does not wrap the config with createMDX() from "
                "'fumadocs-mdx/next'.", "/docs/mdx/next")
    if framework in VITE_FRAMEWORKS and "fumadocs-mdx" in packages:
        vite = [p for p in config_files if re.match(r"(vite|waku|app)\.config", p)]
        if vite and not any("fumadocsMdx" in code[p] for p in vite):
            add("FD009", "error", "Vite config does not register fumadocsMdx() from 'fumadocs-mdx/vite'.",
                "/docs/mdx/vite", vite)
    if codegen_config and not gitignored(root, ".source"):
        add("FD011", "warn", "source.config.ts generates .source/ — add '.source' to .gitignore.",
            "/docs/mdx/collections")
    if "fumadocs-mdx" in packages and not has_loader:
        add("FD012", "warn", "fumadocs-mdx is installed but no file calls loader() from "
            "'fumadocs-core/source'.", "/docs/headless/source-api")
    if untitled:
        add("FD013", "warn", f"{len(untitled)} content page(s) without a 'title' in frontmatter "
            "(required by the default page schema).", "/docs/page-conventions", untitled[:20])
    return out


def as_text(report: dict) -> str:
    fd = report["fumadocs"]
    lines = [
        f"FRAMEWORK: {report['framework'] or 'não detectado'} · PM: {report['package_manager'] or '-'} · "
        f"Node: {report['node'] or '-'} · Tailwind: {report['tailwindcss'] or '-'}",
        "FUMADOCS: " + (", ".join(f"{k}@{v['installed'] or v['declared']}" for k, v in fd.items()) or "não instalado"),
        f"CONTEÚDO: {report['content_source'].get('kind') or '-'} {report['content_source'].get('mode') or ''}".rstrip()
        + f" · baseUrl: {', '.join(report['base_urls']) or '-'} · dirs: {', '.join(report['content_dirs']) or '-'}"
        + f" · {report['content']['pages']} páginas, {report['content']['meta_files']} meta",
        "FEATURES: " + (", ".join(sorted(report["features"])) or "nenhuma"),
    ]
    if report["findings"]:
        lines.append("ACHADOS:")
        for f in report["findings"]:
            where = f" [{', '.join(f['files'][:3])}]" if f.get("files") else ""
            lines.append(f"  {f['id']} {f['severity'].upper():5} {f['message']}{where}\n        → {f['doc']}")
    else:
        lines.append("ACHADOS: nenhum")
    return "\n".join(lines)


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("path", nargs="?", default=".")
    parser.add_argument("--format", choices=("json", "text"), default="json")
    parser.add_argument("--no-node", action="store_true", help="do not run `node --version`")
    args = parser.parse_args(argv)
    root = Path(args.path).resolve()
    if not root.is_dir():
        print(f"fdscan: {root} is not a directory", file=sys.stderr)
        return 2
    report = scan(root, check_node=not args.no_node)
    print(as_text(report) if args.format == "text" else json.dumps(report, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
