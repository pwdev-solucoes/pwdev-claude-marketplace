#!/usr/bin/env python3
"""Fail-closed evidence manifest, HTML renderer, and optional PDF exporter."""
from __future__ import annotations
import argparse, hashlib, html, json, os, re
import datetime as dt
from pathlib import Path

RESULTS = {"passed", "failed", "not_applicable"}
TYPES = {"test_output", "screenshot", "log", "report"}
ID_RULES = {"prd_slug": r"^[a-z0-9]+(?:-[a-z0-9]+)*$", "task_id": r"^TASK-[0-9]{3,}$",
            "requirement_id": r"^RF-[0-9]{3,}$", "story_id": r"^US-[0-9]{3,}$",
            "scenario_id": r"^SC-[0-9]{3,}$", "criterion_id": r"^CA-[0-9]{3,}$",
            "test_id": r"^TEST-[0-9]{3,}$"}
RFC3339 = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?Z$")

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
    if candidate.exists() and (candidate.is_symlink() or not candidate.is_file()):
        raise ValueError("evidence path must be a regular non-symlink file")
    # resolve parent chains too, preventing links to files outside root
    if not str(candidate.resolve()).startswith(str(root) + os.sep):
        raise ValueError("evidence path escapes root")
    return candidate

def _validate(meta):
    if not isinstance(meta, dict): raise ValueError("manifest must be an object")
    for key in ("prd_slug", "task_id"):
        pattern = ID_RULES[key]
        if not isinstance(meta.get(key), str) or not re.match(pattern, meta[key]):
            raise ValueError(f"invalid {key}")
    if not isinstance(meta.get("generated_at"), str) or not RFC3339.fullmatch(meta["generated_at"]):
        raise ValueError("generated_at must be RFC3339 UTC date-time")
    if not isinstance(meta.get("entries"), list) or not meta["entries"]:
        raise ValueError("entries must be non-empty")
    for i, e in enumerate(meta["entries"]):
        if not isinstance(e, dict): raise ValueError(f"entry {i} must be an object")
        for key in ("requirement_id", "story_id", "scenario_id", "criterion_id", "test_id"):
            if not isinstance(e.get(key), str) or not re.match(ID_RULES[key], e[key]): raise ValueError(f"invalid {key}")
        if e.get("result") not in RESULTS: raise ValueError("unknown result")
        if e.get("evidence_type") not in TYPES: raise ValueError("unknown evidence type")
        if not isinstance(e.get("path"), str) or not re.match(r"^[^/]+(?:/[^/]+)*$", e["path"]): raise ValueError("invalid evidence path")
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
        out = Path(manifest_path)
        if out.is_symlink(): raise ValueError("manifest destination cannot be symlink")
        if not str(out.resolve()).startswith(str(root.resolve()) + os.sep): raise ValueError("manifest destination escapes root")
        out.parent.mkdir(parents=True, exist_ok=True)
        tmp = out.with_name(out.name + ".tmp")
        tmp.write_text(json.dumps(meta, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        tmp.replace(out)
    return meta

def verify(manifest, evidence_root):
    """Verify schema, paths, hashes, and return a deterministic result."""
    meta = json.loads(Path(manifest).read_text(encoding="utf-8")) if isinstance(manifest, (str, Path)) else manifest
    try: _validate(meta)
    except (ValueError, TypeError) as exc: return {"ok": False, "errors": [str(exc)]}
    errors = []
    for e in meta["entries"]:
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

def render_html(manifest, evidence_root=None):
    meta = _validate(manifest)
    rows = []
    for e in meta["entries"]:
        rows.append("<tr>" + "".join(f"<td>{html.escape(str(e.get(k, '')))}</td>" for k in ("criterion_id", "test_id", "result", "evidence_type", "path", "sha256")) + "</tr>")
    return "<!doctype html><meta charset='utf-8'><title>Evidence report</title><h1>Evidence report</h1><table><thead><tr><th>Criterion</th><th>Test</th><th>Result</th><th>Type</th><th>Path</th><th>SHA-256</th></tr></thead><tbody>" + "".join(rows) + "</tbody></table>"

def export(manifest, output, evidence_root=None, pdf=False):
    """Write escaped HTML; PDF is optional and fails if expected images cannot load."""
    out = Path(output)
    if pdf:
        for e in _validate(manifest)["entries"]:
            if e["evidence_type"] == "screenshot":
                if evidence_root is None or not _safe(evidence_root, e["path"]).exists(): raise ValueError("expected image did not load")
        raise RuntimeError("PDF export unavailable without a verified PDF backend")
    if out.is_symlink(): raise ValueError("output destination cannot be symlink")
    if evidence_root is not None and not str(out.resolve()).startswith(str(Path(evidence_root).resolve()) + os.sep): raise ValueError("output destination escapes root")
    out.parent.mkdir(parents=True, exist_ok=True); out.write_text(render_html(manifest, evidence_root), encoding="utf-8")
    return out

def main():
    p=argparse.ArgumentParser(); sub=p.add_subparsers(dest="cmd", required=True)
    b=sub.add_parser("build"); b.add_argument("input"); b.add_argument("root"); b.add_argument("manifest"); b.add_argument("--generated-at")
    v=sub.add_parser("verify"); v.add_argument("manifest"); v.add_argument("root")
    e=sub.add_parser("export"); e.add_argument("manifest"); e.add_argument("root"); e.add_argument("output"); e.add_argument("--pdf", action="store_true")
    d=sub.add_parser("discover"); d.add_argument("root")
    a=p.parse_args()
    try:
        if a.cmd == "build":
            result=build(json.loads(Path(a.input).read_text(encoding="utf-8")), a.root, a.manifest, generated_at=a.generated_at)
        elif a.cmd == "verify": result=verify(a.manifest,a.root)
        elif a.cmd == "export": result={"output": str(export(json.loads(Path(a.manifest).read_text(encoding="utf-8")), a.output, a.root, a.pdf))}
        else: result=discover(a.root)
    except (OSError, ValueError, RuntimeError, json.JSONDecodeError) as exc:
        print(json.dumps({"ok":False,"errors":[str(exc)]},ensure_ascii=False)); raise SystemExit(1)
    print(json.dumps(result,ensure_ascii=False,sort_keys=True)); raise SystemExit(0 if result.get("ok", True) else 1)
if __name__ == "__main__": main()
