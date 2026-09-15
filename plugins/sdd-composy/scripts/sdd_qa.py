"""Deterministic, runtime-neutral QA gate for SDD Composy."""
from datetime import datetime, timezone
from hashlib import sha256
from pathlib import Path
import json
import os
import tempfile
from sdd_language import resolve_language


def _origin(data):
    origin = {}
    for key, value in (("task_id", data.get("task_id") or (data.get("task") or {}).get("id")),
                       ("source", data.get("source") or (data.get("provenance") or {}).get("source")),
                       ("result_id", data.get("result_id"))):
        if isinstance(value, str) and value.strip():
            origin[key] = value.strip().replace("token=", "token=[redacted]")
    coverage = []
    for item in data.get("acceptance") or []:
        if not isinstance(item, dict):
            continue
        entry = {}
        for key, aliases in (("ca", ("id", "criterion_id")), ("story", ("story_id", "story")), ("result", ("result_id",))):
            value = next((item.get(alias) for alias in aliases if isinstance(item.get(alias), str) and item.get(alias).strip()), None)
            if value:
                entry[key] = value.strip().replace("token=", "token=[redacted]")
        if entry:
            coverage.append(entry)
    if coverage:
        origin["coverage"] = coverage
    return origin


def _now():
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _not_applicable(value):
    """A level may be skipped only with an explicit, non-empty justification."""
    return (isinstance(value, dict) and value.get("status") == "NOT_APPLICABLE"
            and isinstance(value.get("justification"), str) and bool(value["justification"].strip()))


def _passed(value):
    return value == "passed" or (isinstance(value, dict) and value.get("status") == "passed")


def _reject(reason, detail, *, origin=None, report_path=None, allowed_root=None, generated_by="sdd-composy", verified_by="sdd-composy", generated_at=None):
    result = {"status": "REJECTED", "transition": "rejected", "reason": reason,
            "blocker": str(detail).replace("token=", "token=[redacted]"),
            "next_action": "resolve the QA blocker and rerun the quality gate"}
    result["origin"] = origin or {}
    result["report"] = {"type":"QA_REPORT", "okf_version":"0.2", "title":"SDD Composy quality assurance report",
        "sources":[{"resource":"qa_required task"}], "generated":{"by":generated_by,"at":generated_at or _now()},
        "verified":[],
        "lifecycle":{"status":"REJECTED","human_approval":"PENDING"}, "approval_event":{}, "transition":"rejected",
        "blockers":[{"reason":reason,"detail":result["blocker"]}], "next_action":result["next_action"],
        "coverage":[], "results":{}, "environment":{}, "regression":{}, "evidence":[], "origin": result["origin"]}
    if report_path: _persist(result["report"], report_path, allowed_root)
    return result

def _persist(report, path, allowed_root):
    path = Path(path)
    if path.exists() and path.is_symlink(): raise ValueError("report path cannot be symlink")
    root = Path(allowed_root).resolve(); target = path if path.is_absolute() else root / path
    if not target.resolve().is_relative_to(root): raise ValueError("report path escapes allowed root")
    if any(parent.is_symlink() for parent in target.parents if parent.exists()): raise ValueError("report parent cannot be symlink")
    target.parent.mkdir(parents=True, exist_ok=True)
    front = "---\ntype: QA_REPORT\nokf_version: \"0.2\"\n" + f"title: {json.dumps(report['title'])}\n"
    for key in ("sources", "generated", "verified", "lifecycle", "approval_event", "transition", "blockers", "next_action", "coverage", "results", "environment", "regression", "evidence", "origin"):
        front += f"{key}: {json.dumps(report.get(key), sort_keys=True)}\n"
    front += "---\n"
    fd, tmp = tempfile.mkstemp(prefix=".qa-", dir=str(target.parent), text=True)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as fh: fh.write(front + json.dumps(report, sort_keys=True, indent=2) + "\n")
        os.replace(tmp, target)
    finally:
        if os.path.exists(tmp): os.unlink(tmp)


def assess(data, *, evidence_root=None, report_path=None, allowed_root=None, generated_by="sdd-composy", verified_by="sdd-composy", title="SDD Composy quality assurance report", generated_at=None):
    """Assess a qa_required payload and return a guarded transition result.

    Unit tests are always required. Integration, E2E, accessibility, and responsiveness may be
    `{"status": "NOT_APPLICABLE", "justification": "..."}`; a browser is required only when E2E runs.
    """
    generated_at = generated_at or _now()
    if report_path and allowed_root is None: raise ValueError("allowed_root is required")
    language = 'en-US'
    if allowed_root is not None:
        resolved = resolve_language(allowed_root)
        if 'language' not in resolved:
            return resolved
        language = resolved['language']
    if language == 'pt-BR' and title == 'SDD Composy quality assurance report':
        title = 'Relatório de garantia de qualidade SDD Composy'
    origin = _origin(data)
    def fail(reason, detail):
        result = _reject(reason, detail, origin=origin, generated_by=generated_by, verified_by=verified_by, generated_at=generated_at)
        result['report']['title'] = title
        if language == 'pt-BR':
            result['next_action'] = 'resolver o bloqueio de QA e executar novamente a verificação de qualidade'
            result['report']['next_action'] = result['next_action']
        if report_path:
            _persist(result['report'], report_path, allowed_root)
        return result
    if data.get("state") != "qa_required":
        return fail("invalid_state", "task must be qa_required")
    acceptance = data.get("acceptance") or []
    ids = [x.get("id") for x in acceptance]
    if (not acceptance or len(ids) != len(set(ids)) or
            any(not x.get("id") or not x.get("story") or not x.get("tests") or
                any(not isinstance(t, str) or not t.strip() for t in x.get("tests", [])) for x in acceptance)):
        return fail("coverage_missing", "every CA requires an SC and executable test")
    results = data.get("results") or {}
    for name in ("unit", "integration", "e2e"):
        result = results.get(name) or {}
        if name != "unit" and _not_applicable(result):
            continue
        if not isinstance(result, dict) or result.get("status") != "passed" or not result.get("command") or not result.get("environment") or result.get("exit_code") != 0 or not result.get("evidence"):
            return fail(name + "_failed", name + " requires passed status, command, environment, exit code, and evidence, or NOT_APPLICABLE with a justification")
    if not _not_applicable(results.get("e2e")) and not (data.get("browser") or {}).get("available"):
        return fail("browser_unavailable", "E2E browser capability unavailable")
    for name in ("accessibility", "responsiveness"):
        if not _passed(data.get(name)) and not _not_applicable(data.get(name)):
            return fail(name + "_failed", name + " checks are not passed or justified as NOT_APPLICABLE")
    env = data.get("environment") or {}
    if not env.get("ready") or not env.get("runtime") or not env.get("versions"):
        return fail("environment_not_ready", "QA environment is not ready")
    if env.get("cleanup") != "cleaned":
        return fail("cleanup_failed", "run-owned services were not cleaned")
    if (data.get("regression") or {}).get("status") != "passed" or not (data.get("regression") or {}).get("evidence"):
        return fail("regression_failed", "regression evidence is required")
    evidence = data.get("evidence") or []
    if not evidence:
        return fail("evidence_missing", "evidence inventory is empty")
    root = Path(evidence_root) if evidence_root else None
    manifest = []
    for item in sorted(evidence, key=lambda x: x.get("path", "")):
        path = item.get("path", "")
        p = Path(path)
        if not path or p.is_absolute() or ".." in p.parts:
            return fail("evidence_path_invalid", "evidence path must be confined and relative")
        digest = item.get("sha256")
        target = root / p if root else None
        if not target or not target.exists() or not target.is_file():
            return fail("evidence_missing", "evidence file does not exist")
        if item.get("type") not in {"log", "screenshot", "video", "trace", "report"} or item.get("result") not in {"passed", "failed", "skipped"} or not item.get("summary") or not item.get("source"):
            return fail("evidence_invalid", "evidence requires known type, result, summary, and source")
        actual = sha256(target.read_bytes()).hexdigest()
        if digest and digest != actual:
            return fail("evidence_hash_mismatch", "evidence SHA-256 mismatch")
        digest = actual
        manifest.append({"path": path, "type": item["type"], "result": item["result"], "summary": item["summary"].replace("token=", "token=[redacted]"), "source": item["source"], "sha256": digest})
    if not data.get("human_approved"):
        return fail("human_approval_missing", "explicit human approval is required")
    coverage = [{"ca": x["id"], "story": x["story"], "tests": sorted(x["tests"])} for x in acceptance]
    report = {"type": "QA_REPORT", "okf_version": "0.2", "title": title,
              "sources": [{"resource": "qa_required task"}, {"resource": "approved CA/SC/test mappings"}],
              "generated": {"by": generated_by, "at": generated_at},
              "verified": [{"by": verified_by, "at": generated_at, "event": "qa-gate"}],
              "lifecycle": {"status": "APPROVED", "human_approval": "APPROVED"},
              "approval_event": {"by": verified_by, "event": "explicit-human-approval"},
              "coverage": coverage, "results": results, "accessibility": data["accessibility"],
              "responsiveness": data["responsiveness"], "environment": env,
              "regression": data["regression"], "evidence": manifest,
              "blockers": [], "next_action": "publish evidence dossier",
              "transition": "evidence_required"}
    if language == 'pt-BR':
        report['next_action'] = 'publicar dossiê de evidências'
    if report_path:
        _persist(report, report_path, allowed_root)
    return {"status": "APPROVED", "transition": "evidence_required", "coverage": coverage,
            "evidence": manifest, "reason": "qa_passed", "next_action": report['next_action'], "report": report}


def load_report(path):
    """Reload a persisted deterministic QA report."""
    text = Path(path).read_text(encoding="utf-8")
    parts = text.split("---\n", 2)
    if len(parts) != 3: raise ValueError("invalid OKF document")
    body = json.loads(parts[2]); front = {}
    for line in parts[1].splitlines():
        if ": " in line:
            key, value = line.split(": ", 1); front[key] = json.loads(value) if value.startswith(("{", "[", '"')) else value
    required = {"type", "okf_version", "title", "sources", "generated", "verified", "lifecycle", "approval_event", "transition", "blockers", "next_action", "coverage", "results", "environment", "regression", "evidence"}
    if not required <= set(front) or front["type"] != "QA_REPORT" or front["okf_version"] != "0.2": raise ValueError("invalid OKF frontmatter")
    if front["lifecycle"].get("status") not in {"APPROVED", "REJECTED", "DRAFT"}: raise ValueError("invalid lifecycle")
    for key in required - {"type", "okf_version"}:
        if front.get(key) != body.get(key): raise ValueError("frontmatter/body mismatch")
    return body
