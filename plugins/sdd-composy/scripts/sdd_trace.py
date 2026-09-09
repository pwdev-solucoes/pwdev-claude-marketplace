#!/usr/bin/env python3
"""Fail-closed append-only semantic trace for SDD Composy."""
from __future__ import annotations
import argparse, datetime as dt, hashlib, json, os, re, tempfile
from pathlib import Path
from typing import Any

EVENT_TYPES = re.compile(r"^[a-z][a-z0-9]*(?:[._-][a-z0-9]+)+$")
ACTOR = re.compile(r"^[A-Za-z][A-Za-z0-9._-]*:[A-Za-z0-9][A-Za-z0-9._-]*$")
STAGES = {"INIT", "MAP", "PRD", "STORIES", "TECHSPEC", "TASKS", "EXECUTE", "QA", "EVIDENCE", "REVIEW", "VERIFY", "COMPLETE"}
FORBIDDEN = {"prompt", "output", "outputs", "environment", "env", "secret", "secrets", "model", "private_path", "private_paths"}

def _root(root: Path | str) -> Path:
    raw = Path(root).absolute()
    if raw.is_symlink() or not raw.is_dir(): raise ValueError("repository root must be a regular directory")
    current = Path(raw.anchor); started = False
    for part in raw.parts[1:]:
        current /= part
        if current.is_symlink():
            if started: raise ValueError("repository root must not contain symlink components")
            continue
        started = True
    return raw

def _target(root: Path | str, *, create: bool = False) -> Path:
    """Resolve trace below a repository root (never an operational root)."""
    base = _root(root)
    operational = base / ".planning" / "sdd-composy"
    for controlled in (base / ".planning", operational):
        if controlled.is_symlink() or (controlled.exists() and not controlled.is_dir()):
            raise ValueError("operational trace ancestor must be regular")
    trace = operational / "trace"
    if trace.is_symlink() or (trace.exists() and not trace.is_dir()): raise ValueError("trace directory must be regular")
    if create:
        trace.mkdir(mode=0o700, parents=True, exist_ok=True)
        os.chmod(trace, 0o700)
    path = trace / "events.jsonl"
    if path.is_symlink() or (path.exists() and not path.is_file()): raise ValueError("trace target must be regular")
    return path

def _check_forbidden(value: Any) -> None:
    if isinstance(value, dict):
        for key, child in value.items():
            if str(key).lower() in FORBIDDEN: raise ValueError(f"prohibited trace key: {key}")
            _check_forbidden(child)
    elif isinstance(value, list):
        for child in value: _check_forbidden(child)

def _validate_event(event: dict[str, Any]) -> None:
    if not isinstance(event, dict): raise ValueError("event must be an object")
    for key in ("actor_id", "type", "stage"):
        if not isinstance(event.get(key), str): raise ValueError(f"missing {key}")
    if not ACTOR.fullmatch(event["actor_id"]): raise ValueError("invalid actor_id")
    if not EVENT_TYPES.fullmatch(event["type"]): raise ValueError("invalid event type")
    if event["stage"] not in STAGES: raise ValueError("invalid stage")
    if event.get("task_id") is not None and (not isinstance(event["task_id"], str) or not re.fullmatch(r"TASK-[0-9]{3,}", event["task_id"])): raise ValueError("invalid task_id")
    if not isinstance(event.get("data", {}), dict): raise ValueError("data must be an object")
    _check_forbidden(event)

def _read(path: Path) -> list[dict[str, Any]]:
    if not path.exists(): return []
    rows = []
    for line_no, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        try: item = json.loads(line)
        except json.JSONDecodeError as exc: raise ValueError(f"invalid JSONL at line {line_no}") from exc
        if not isinstance(item, dict): raise ValueError(f"invalid event at line {line_no}")
        rows.append(item)
    return rows

def _iso(now: str | None) -> str:
    return now or dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")

def record(root: Path | str, event: dict[str, Any], *, enabled: bool = True, now: str | None = None) -> dict[str, Any] | None:
    if not enabled: return None
    _validate_event(event)
    path = _target(root, create=True)
    existing = _read(path)
    if existing:
        for n, item in enumerate(existing, 1):
            if item.get("sequence") != n: raise ValueError("trace sequence is invalid")
    entry = dict(event); entry.setdefault("task_id", None); entry.setdefault("data", {})
    entry.update(sequence=len(existing) + 1, id=f"EVT-{len(existing)+1:06d}", at=_iso(now))
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(entry, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n")
        handle.flush(); os.fsync(handle.fileno())
    os.chmod(path, 0o600)
    return entry

def events(root: Path | str) -> dict[str, Any]:
    rows = _read(_target(root))
    return {"schema_version": "1", "source_event_count": len(rows), "events": rows}

def verify(root: Path | str) -> dict[str, Any]:
    try:
        rows = _read(_target(root))
        for n, item in enumerate(rows, 1):
            if item.get("sequence") != n: raise ValueError("trace sequence is invalid")
            _validate_event(item)
        return {"ok": True, "errors": [], "source_event_count": len(rows)}
    except (OSError, UnicodeError, ValueError) as exc:
        return {"ok": False, "errors": [str(exc)]}

def summary(root: Path | str) -> dict[str, Any]:
    rows = _read(_target(root)); by_type: dict[str, int] = {}
    for item in rows: by_type[item.get("type", "invalid")] = by_type.get(item.get("type", "invalid"), 0) + 1
    return {"schema_version": "1", "source_event_count": len(rows), "by_type": dict(sorted(by_type.items()))}

def _projection_path(root: Path | str) -> Path:
    base = _root(root); trace = base / ".planning" / "sdd-composy" / "trace"
    for controlled in (base / ".planning", base / ".planning" / "sdd-composy"):
        if controlled.is_symlink() or (controlled.exists() and not controlled.is_dir()):
            raise ValueError("operational trace ancestor must be regular")
    if trace.is_symlink() or (trace.exists() and not trace.is_dir()):
        raise ValueError("trace directory must be regular")
    path = trace / "trace.json"
    # Check the directory entry itself first: exists() is false for broken links.
    if path.is_symlink():
        raise ValueError("trace projection target must be regular")
    if path.exists() and not path.is_file():
        raise ValueError("trace projection target must be regular")
    return path

def _graph_nodes(graph: dict[str, Any]) -> list[dict[str, Any]]:
    """Normalize the small graph contract while retaining caller metadata."""
    nodes: list[dict[str, Any]] = []
    if isinstance(graph.get("nodes"), list):
        nodes = [dict(n) for n in graph["nodes"] if isinstance(n, dict)]
    else:
        for key in ("requirements", "stories", "scenarios", "criteria", "tasks", "tests", "evidence", "manifests", "artifacts", "hashes", "verdicts"):
            for item in graph.get(key, []) if isinstance(graph.get(key), list) else []:
                if isinstance(item, dict): nodes.append(dict(item))
    seen: set[str] = set()
    for node in nodes:
        ident = node.get("id")
        if not isinstance(ident, str) or not ident: raise ValueError("graph node requires id")
        if ident in seen: raise ValueError(f"duplicate graph id: {ident}")
        seen.add(ident); node.setdefault("kind", ident.split("-")[0].lower())
    return sorted(nodes, key=lambda n: (str(n["id"]), json.dumps(n, sort_keys=True, ensure_ascii=False)))

def _graph_edges(graph: dict[str, Any], nodes: list[dict[str, Any]]) -> list[dict[str, str]]:
    edges = graph.get("links", graph.get("edges", []))
    if not isinstance(edges, list): raise ValueError("graph links must be a list")
    known = {n["id"] for n in nodes}; result = []
    for edge in edges:
        if not isinstance(edge, dict): raise ValueError("graph link must be an object")
        source, target = edge.get("from", edge.get("source")), edge.get("to", edge.get("target"))
        if not isinstance(source, str) or not isinstance(target, str): raise ValueError("graph link requires from and to")
        if source not in known or target not in known: raise ValueError(f"dangling graph id: {source if source not in known else target}")
        result.append({"from": source, "to": target, "type": str(edge.get("type", "relates_to"))})
    return sorted(result, key=lambda e: (e["from"], e["to"], e["type"]))

def build(root: Path | str, graph: dict[str, Any] | None = None, *, generated_at: str | None = None) -> dict[str, Any]:
    """Atomically publish a deterministic graph projection bound to events.jsonl."""
    base = _root(root); source = _read(_target(base));
    if graph is None:
        candidate = base / ".planning" / "sdd-composy" / "trace" / "graph.json"
        graph = json.loads(candidate.read_text(encoding="utf-8")) if candidate.exists() else {}
    if not isinstance(graph, dict): raise ValueError("graph must be an object")
    nodes = _graph_nodes(graph); links = _graph_edges(graph, nodes)
    payload = {"schema_version": "1", "source_event_count": len(source),
               "generated_at": generated_at or (max((e.get("at", "") for e in source), default="1970-01-01T00:00:00Z")),
               "nodes": nodes, "links": links, "events": source}
    payload["projection_hash"] = hashlib.sha256(json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()).hexdigest()
    out = _projection_path(base); out.parent.mkdir(mode=0o700, exist_ok=True); os.chmod(out.parent, 0o700)
    fd, name = tempfile.mkstemp(prefix=f".{out.name}.", suffix=".tmp", dir=str(out.parent), text=True)
    tmp = Path(name)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            handle.write(json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n")
            handle.flush(); os.fsync(handle.fileno())
        os.chmod(tmp, 0o600); os.replace(tmp, out); os.chmod(out, 0o600)
    except Exception:
        try: tmp.unlink()
        except OSError: pass
        raise
    return payload

def query(root: Path | str, node_id: str | None = None) -> dict[str, Any]:
    path = _projection_path(root)
    data = json.loads(path.read_text(encoding="utf-8"))
    if node_id is None: return data
    nodes = [n for n in data.get("nodes", []) if n.get("id") == node_id]
    links = [e for e in data.get("links", []) if e.get("from") == node_id or e.get("to") == node_id]
    return {"node": nodes[0] if nodes else None, "links": links}

def verify_projection(root: Path | str) -> dict[str, Any]:
    try:
        data = query(root); source = _read(_target(root))
        if data.get("source_event_count") != len(source): raise ValueError("source event count mismatch")
        if data.get("events") != source: raise ValueError("projection events mismatch")
        nodes = _graph_nodes({"nodes": data.get("nodes", [])})
        links = _graph_edges({"links": data.get("links", [])}, nodes)
        canonical = dict(data); claimed = canonical.pop("projection_hash", None)
        expected = hashlib.sha256(json.dumps(canonical, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()).hexdigest()
        if claimed != expected: raise ValueError("projection hash mismatch")
        if nodes != data.get("nodes", []) or links != data.get("links", []): raise ValueError("projection ordering is invalid")
        return {"ok": True, "errors": [], "source_event_count": len(source), "projection_hash": data.get("projection_hash")}
    except (OSError, UnicodeError, ValueError, json.JSONDecodeError) as exc:
        return {"ok": False, "errors": [str(exc)]}

if __name__ == "__main__":
    parser = argparse.ArgumentParser(); parser.add_argument("command", choices=("events", "summary", "verify", "build", "query", "verify-projection")); parser.add_argument("root"); parser.add_argument("node_id", nargs="?")
    args = parser.parse_args(); result = (build(args.root) if args.command == "build" else verify_projection(args.root) if args.command == "verify-projection" else query(args.root, args.node_id) if args.command == "query" else globals()[args.command](args.root)); print(json.dumps(result, ensure_ascii=False, sort_keys=True))
