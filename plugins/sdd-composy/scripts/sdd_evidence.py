#!/usr/bin/env python3
"""Fail-closed evidence manifest, HTML renderer, and optional PDF exporter."""
from __future__ import annotations
import argparse, base64, hashlib, html, json, os, re, shutil, signal, subprocess, tempfile, time
import datetime as dt
from pathlib import Path
from sdd_language import resolve_language


def _atomic_output(root, output, content):
    raw_root = Path(root).absolute()
    root = _evidence_root(root)
    out = Path(output).absolute()
    try:
        relative = out.relative_to(raw_root)
    except ValueError as exc:
        try:
            relative = out.relative_to(root)
        except ValueError:
            raise ValueError('output destination escapes root') from exc
    out = _safe(root, relative.as_posix())
    out.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix='.evidence-', dir=out.parent)
    try:
        with os.fdopen(fd, 'w', encoding='utf-8') as stream:
            stream.write(content)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, out)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)
    return Path(output)

RESULTS = {"passed", "failed", "not_applicable"}
TYPES = {"test_output", "screenshot", "log", "report"}
ID_RULES = {"prd_slug": r"^[a-z0-9]+(?:-[a-z0-9]+)*$", "task_id": r"^TASK-[0-9]{3,}$",
            "requirement_id": r"^RF-[0-9]{3,}$", "story_id": r"^US-[0-9]{3,}$",
            "scenario_id": r"^SC-[0-9]{3,}$", "criterion_id": r"^CA-[0-9]{3,}$",
            "test_id": r"^TEST-[0-9]{3,}$"}
RFC3339 = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+-]\d{2}:\d{2})$")
SHA256 = re.compile(r"^[a-f0-9]{64}$")

def _evidence_root(root):
    """Return a confined root without following caller-controlled symlinks."""
    raw = Path(root).absolute()
    current = Path(raw.anchor)
    started = False
    for part in raw.parts[1:]:
        current /= part
        # macOS commonly exposes /var as a compatibility symlink.  Permit
        # leading platform aliases, but reject any link inside the supplied
        # evidence-root path (including the root itself).
        if current.is_symlink():
            if started:
                raise ValueError("evidence root must not contain symlink components")
            continue
        started = True
    resolved = raw.resolve()
    if not resolved.is_dir():
        raise ValueError("evidence root must be a regular directory")
    return resolved

def _safe(root, rel):
    if not isinstance(rel, str) or not rel or "\\" in rel:
        raise ValueError("evidence path must be a confined relative path")
    p = Path(rel)
    if p.is_absolute() or any(x in ("", ".", "..") for x in p.parts):
        raise ValueError("evidence path escapes root")
    root = _evidence_root(root)
    current = root
    for part in p.parts[:-1]:
        current = current / part
        if current.is_symlink():
            raise ValueError("evidence path contains symlink component")
    candidate = root.joinpath(*p.parts)
    if candidate.is_symlink() or (candidate.exists() and not candidate.is_file()):
        raise ValueError("evidence path must be a regular non-symlink file")
    # resolve parent chains too, preventing links to files outside root
    if not str(candidate.resolve()).startswith(str(root) + os.sep):
        raise ValueError("evidence path escapes root")
    return candidate

def _validate(meta):
    if not isinstance(meta, dict): raise ValueError("manifest must be an object")
    if meta.get("schema_version", "1") != "1": raise ValueError("unsupported schema_version")
    for key in ("prd_slug", "task_id"):
        pattern = ID_RULES[key]
        if not isinstance(meta.get(key), str) or not re.match(pattern, meta[key]):
            raise ValueError(f"invalid {key}")
    if not isinstance(meta.get("generated_at"), str) or not RFC3339.fullmatch(meta["generated_at"]):
        raise ValueError("generated_at must be an RFC3339 date-time with offset")
    if not isinstance(meta.get("entries"), list) or not meta["entries"]:
        raise ValueError("entries must be non-empty")
    for i, e in enumerate(meta["entries"]):
        if not isinstance(e, dict): raise ValueError(f"entry {i} must be an object")
        for key in ("requirement_id", "story_id", "scenario_id", "criterion_id", "test_id"):
            if not isinstance(e.get(key), str) or not re.match(ID_RULES[key], e[key]): raise ValueError(f"invalid {key}")
        if e.get("result") not in RESULTS: raise ValueError("unknown result")
        if e.get("evidence_type") not in TYPES: raise ValueError("unknown evidence type")
        if not isinstance(e.get("path"), str) or not re.match(r"^[^/]+(?:/[^/]+)*$", e["path"]) or any(part in ("", ".", "..") for part in e["path"].split("/")) or "\\" in e["path"]:
            raise ValueError("invalid evidence path")
        if "sha256" in e and (not isinstance(e["sha256"], str) or not SHA256.fullmatch(e["sha256"])): raise ValueError("invalid sha256")
    return meta

def build(data, evidence_root, manifest_path=None, generated_by="sdd-composy", generated_at=None):
    """Validate input, hash evidence files, and optionally atomically write manifest."""
    root = Path(evidence_root)
    meta = dict(data)
    meta.setdefault("schema_version", "1")
    meta.setdefault("generated_by", generated_by)
    meta.setdefault("generated_at", generated_at or dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"))
    if meta["schema_version"] != "1": raise ValueError("unsupported schema_version")
    entries = []
    for source in meta.get("entries", []):
        e = dict(source); path = _safe(root, e.get("path"))
        if not path.exists(): raise FileNotFoundError(e["path"])
        e["sha256"] = hashlib.sha256(path.read_bytes()).hexdigest()
        entries.append(e)
    meta["entries"] = sorted(entries, key=lambda x: (x["path"], x["criterion_id"], x["test_id"]))
    _validate(meta)
    if manifest_path:
        _atomic_output(root, manifest_path, json.dumps(meta, ensure_ascii=False, indent=2, sort_keys=True) + "\n")
    return meta

def verify(manifest, evidence_root):
    """Verify schema, paths, hashes, and return a deterministic result."""
    meta = json.loads(Path(manifest).read_text(encoding="utf-8")) if isinstance(manifest, (str, Path)) else manifest
    try: _validate(meta)
    except (ValueError, TypeError) as exc: return {"ok": False, "errors": [str(exc)]}
    errors = []
    for e in meta["entries"]:
        if "sha256" not in e: errors.append(f"missing sha256: {e['path']}"); continue
        try: path = _safe(evidence_root, e["path"])
        except ValueError as exc: errors.append(str(exc)); continue
        if not path.exists(): errors.append(f"missing: {e['path']}"); continue
        if hashlib.sha256(path.read_bytes()).hexdigest() != e.get("sha256"): errors.append(f"hash mismatch: {e['path']}")
    return {"ok": not errors, "errors": errors, "manifest": meta}

def discover(evidence_root):
    """Return deterministic, read-only inventory of regular evidence files."""
    root = _evidence_root(evidence_root)
    found = []
    for path in sorted(root.rglob("*")):
        if path.is_symlink():
            raise ValueError("evidence discovery rejects symlinks")
        if path.is_file():
            found.append(str(path.relative_to(root)))
    return {"root": str(root), "files": found}

IMAGE_TYPES = ((b"\x89PNG\r\n\x1a\n", "image/png"), (b"\xff\xd8\xff", "image/jpeg"),
               (b"GIF87a", "image/gif"), (b"GIF89a", "image/gif"))
PDF_BROWSERS = ("google-chrome", "google-chrome-stable", "chromium", "chromium-browser", "microsoft-edge",
                "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
                "/Applications/Chromium.app/Contents/MacOS/Chromium",
                "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge")

def _image_data_uri(evidence_root, relative):
    """Embed a screenshot so the report is self-contained; anything that is not an image fails."""
    raw = _safe(evidence_root, relative).read_bytes()
    mime = next((kind for magic, kind in IMAGE_TYPES if raw.startswith(magic)), None)
    if mime is None or (raw.startswith(IMAGE_TYPES[0][0]) and b"IEND" not in raw[-16:]):
        raise ValueError(f"expected image did not load: {relative}")
    return f"data:{mime};base64," + base64.b64encode(raw).decode("ascii")

def _pdf_browser():
    """A headless Chromium-family browser; SDD_PDF_BROWSER overrides discovery."""
    candidates = [os.environ["SDD_PDF_BROWSER"]] if os.environ.get("SDD_PDF_BROWSER") else list(PDF_BROWSERS)
    for candidate in candidates:
        found = shutil.which(candidate) if os.sep not in candidate else (candidate if os.access(candidate, os.X_OK) else None)
        if found: return found
    raise RuntimeError("PDF export unavailable: no PDF backend (a Chromium-family browser) was found; set SDD_PDF_BROWSER")

def _print_pdf(html_path, pdf_path, *, timeout=120):
    browser = _pdf_browser()
    with tempfile.TemporaryDirectory(prefix="sdd-pdf-") as profile:
        fd, temporary = tempfile.mkstemp(prefix=".evidence-", suffix=".pdf", dir=pdf_path.parent)
        os.close(fd)
        try:
            command = [browser, "--headless=new", "--disable-gpu", "--no-first-run", "--no-default-browser-check",
                       f"--user-data-dir={profile}", "--no-pdf-header-footer", f"--print-to-pdf={temporary}",
                       Path(html_path).absolute().as_uri()]
            # Chrome on macOS can keep helper processes (and inherited pipes) alive after printing,
            # so wait for a complete PDF instead of process exit, then stop the whole group.
            try:
                process = subprocess.Popen(command, stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL,
                                           stderr=subprocess.DEVNULL, start_new_session=True)
            except OSError as exc:
                raise RuntimeError(f"PDF backend failed: {exc}") from exc
            deadline = time.monotonic() + timeout
            data = b""
            try:
                while time.monotonic() < deadline:
                    data = Path(temporary).read_bytes() if Path(temporary).exists() else b""
                    if data.startswith(b"%PDF-") and data.rstrip().endswith(b"%%EOF"): break
                    if process.poll() is not None:
                        data = Path(temporary).read_bytes() if Path(temporary).exists() else b""
                        break
                    time.sleep(0.1)
            finally:
                if process.poll() is None:
                    try: os.killpg(process.pid, signal.SIGTERM)
                    except OSError: pass
                    try: process.wait(timeout=10)
                    except subprocess.TimeoutExpired:
                        try: os.killpg(process.pid, signal.SIGKILL)
                        except OSError: pass
            if not (data.startswith(b"%PDF-") and data.rstrip().endswith(b"%%EOF")):
                raise RuntimeError("PDF backend did not produce a complete PDF")
            os.replace(temporary, pdf_path)
        finally:
            if os.path.exists(temporary): os.unlink(temporary)
    return pdf_path

def render_html(manifest, evidence_root=None, *, language='en-US'):
    meta = _validate(manifest)
    if language not in {'pt-BR', 'en-US'}:
        raise ValueError('invalid language')
    title = 'Relatório de evidências' if language == 'pt-BR' else 'Evidence report'
    labels = ('Critério', 'Teste', 'Resultado', 'Tipo', 'Caminho', 'SHA-256') if language == 'pt-BR' else ('Criterion', 'Test', 'Result', 'Type', 'Path', 'SHA-256')
    rows = []
    for e in meta["entries"]:
        cells = "".join(f"<td>{html.escape(str(e.get(k, '')))}</td>" for k in ("criterion_id", "test_id", "result", "evidence_type", "path", "sha256"))
        if e["evidence_type"] == "screenshot" and evidence_root is not None:
            cells += f"<td><img alt='{html.escape(e['path'])}' src='{_image_data_uri(evidence_root, e['path'])}' style='max-width:320px'></td>"
        rows.append("<tr>" + cells + "</tr>")
    return f"<!doctype html><html lang='{language}'><meta charset='utf-8'><title>{title}</title><h1>{title}</h1><table><thead><tr>" + ''.join(f'<th>{label}</th>' for label in labels) + '</tr></thead><tbody>' + ''.join(rows) + '</tbody></table></html>'

def _bundle_layout(evidence_root):
    """For `<workspace>/tasks/prd-<slug>/evidences`, return (bundle, workspace); otherwise (root, root)."""
    root = Path(evidence_root).absolute()
    if root.name == "evidences" and root.parent.name.startswith("prd-") and root.parent.parent.name == "tasks":
        return root.parent, root.parent.parent.parent
    return root, root

def export(manifest, output, evidence_root=None, pdf=False, *, workspace_root=None):
    """Write escaped HTML into the PRD bundle; PDF is optional and fails if expected images cannot load."""
    out = Path(output)
    if evidence_root is None:
        raise ValueError('evidence_root is required')
    bundle, inferred_workspace = _bundle_layout(evidence_root)
    preference = resolve_language(workspace_root or inferred_workspace)
    if 'language' not in preference:
        raise ValueError('not_initialized: run_init')
    if pdf:
        _pdf_browser()  # fail before writing anything when no backend exists
    # Rendering embeds and checks every screenshot, so a missing or broken image fails here.
    written = _atomic_output(bundle, out, render_html(manifest, evidence_root, language=preference['language']))
    if pdf:
        pdf_path = _safe(bundle, Path(written).absolute().relative_to(Path(bundle).absolute()).with_suffix(".pdf").as_posix())
        _print_pdf(written, pdf_path)
    return written

def main():
    p=argparse.ArgumentParser(); sub=p.add_subparsers(dest="cmd", required=True)
    b=sub.add_parser("build"); b.add_argument("input"); b.add_argument("root"); b.add_argument("manifest"); b.add_argument("--generated-at")
    v=sub.add_parser("verify"); v.add_argument("manifest"); v.add_argument("root")
    e=sub.add_parser("export"); e.add_argument("manifest"); e.add_argument("root"); e.add_argument("output"); e.add_argument("--pdf", action="store_true")
    e.add_argument('--workspace-root', help='workspace initialized by sdd-init; inferred from tasks/prd-<slug>/evidences, otherwise the evidence root')
    d=sub.add_parser("discover"); d.add_argument("root")
    a=p.parse_args()
    try:
        if a.cmd == "build":
            result=build(json.loads(Path(a.input).read_text(encoding="utf-8")), a.root, a.manifest, generated_at=a.generated_at)
        elif a.cmd == "verify": result=verify(a.manifest,a.root)
        elif a.cmd == "export":
            written = export(json.loads(Path(a.manifest).read_text(encoding="utf-8")), a.output, a.root, a.pdf, workspace_root=a.workspace_root)
            result = {"output": str(written)}
            if a.pdf: result["pdf"] = str(Path(written).with_suffix(".pdf"))
        else: result=discover(a.root)
    except (OSError, ValueError, RuntimeError, json.JSONDecodeError) as exc:
        print(json.dumps({"ok":False,"errors":[str(exc)]},ensure_ascii=False)); raise SystemExit(1)
    print(json.dumps(result,ensure_ascii=False,sort_keys=True)); raise SystemExit(0 if result.get("ok", True) else 1)
if __name__ == "__main__": main()
