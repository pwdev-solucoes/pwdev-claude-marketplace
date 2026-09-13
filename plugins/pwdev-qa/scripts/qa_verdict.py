"""Build the single public PWDEV QA report model used by renderers."""

from __future__ import annotations

import copy
from typing import Any, Dict, Iterable, List, Optional, Set, Tuple

from qa_evidence import EvidenceError, _json_contains_credential

_CASE_RESULTS = {"PASS", "FAIL", "BLOCKED", "NOT_RUN", "NOT_APPLICABLE"}


def _pick(source: Dict[str, Any], names: Iterable[str]) -> Dict[str, Any]:
    return {name: copy.deepcopy(source[name]) for name in names}


def _public_manifest(manifest: Dict[str, Any]) -> Dict[str, Any]:
    """Allowlist the normalized contract; extensions are never auto-published."""

    contract = _pick(manifest["contract"], ("path", "sha256"))
    contract["criteria_review"] = _pick(
        manifest["contract"]["criteria_review"], ("actor", "at", "complete")
    )
    criteria = []
    for item in manifest["criteria"]:
        public = _pick(
            item,
            ("id", "text", "applicable", "applicability_reason", "case_ids"),
        )
        public["assessment"] = _pick(
            item["assessment"], ("actor", "at", "expected", "observed")
        )
        criteria.append(public)
    cases = [
        _pick(
            item,
            (
                "id",
                "case_id",
                "criterion_ids",
                "status",
                "required",
                "expected",
                "observed",
                "command",
                "exit_code",
                "evidence_ids",
                "attempt",
                "supersedes",
            ),
        )
        for item in manifest["cases"]
    ]
    defects = [
        _pick(
            item,
            (
                "id",
                "summary",
                "in_scope",
                "status",
                "severity",
                "criterion_ids",
                "evidence_ids",
                "supersedes",
                "retest_attempt_id",
            ),
        )
        for item in manifest["defects"]
    ]
    return {
        "schema_version": manifest["schema_version"],
        "run_id": manifest["run_id"],
        "project": manifest["project"],
        "target": _pick(manifest["target"], ("id", "kind")),
        "executed_at": manifest["executed_at"],
        "contract": contract,
        "criteria": criteria,
        "cases": cases,
        "defects": defects,
    }


def _terminal_records(
    records: List[Dict[str, Any]],
    *,
    logical_key: Optional[str],
    label: str,
    diagnostic,
) -> Tuple[List[Dict[str, Any]], bool]:
    """Return declared terminals and diagnose cycles/branches defensively."""

    by_id = {item["id"]: item for item in records}
    children: Dict[str, List[str]] = {}
    invalid = False
    for item in records:
        predecessor = item.get("supersedes")
        if predecessor is None:
            continue
        if predecessor not in by_id:
            diagnostic(f"{label} {item['id']}: supersedes unknown record {predecessor}")
            invalid = True
            continue
        children.setdefault(predecessor, []).append(item["id"])
        if len(children[predecessor]) > 1:
            diagnostic(f"{label} history branches at {predecessor}")
            invalid = True

    for item in records:
        seen: Set[str] = set()
        current: Optional[str] = item["id"]
        while current is not None and current in by_id:
            if current in seen:
                diagnostic(f"{label} history contains a cycle at {current}")
                invalid = True
                break
            seen.add(current)
            current = by_id[current].get("supersedes")

    if logical_key is None:
        terminals = [item for item in records if item["id"] not in children]
        return terminals, invalid

    grouped: Dict[str, List[Dict[str, Any]]] = {}
    for item in records:
        grouped.setdefault(item[logical_key], []).append(item)
    terminals = []
    for logical_id, group in grouped.items():
        candidates = [item for item in group if item["id"] not in children]
        if len(candidates) != 1:
            diagnostic(
                f"{label} {logical_id}: expected one terminal attempt, found {len(candidates)}"
            )
            invalid = True
        else:
            terminals.append(candidates[0])
    return terminals, invalid


def _public_verified(record: Dict[str, Any]) -> Dict[str, Any]:
    public = _pick(
        record,
        (
            "id",
            "target_id",
            "contract",
            "status",
            "copy_allowed",
            "requires_copy_revalidation",
            "path",
            "sha256",
            "media_type",
            "size_bytes",
            "diagnostic",
        ),
    )
    public["contract"] = _pick(record["contract"], ("path", "sha256"))
    return public


def build_report(
    manifest: dict,
    evidence: list[dict],
    contract_diagnostics: Optional[List[str]] = None,
) -> dict:
    """Consolidate a normalized manifest and evidence inspections deterministically.

    Stored commands remain inert strings. The returned dictionary is an allowlisted public
    projection and is the only model renderers need; renderers must not recalculate results.
    """

    diagnostics: List[str] = []

    def diagnostic(message: str) -> None:
        if message not in diagnostics:
            diagnostics.append(message)

    for message in contract_diagnostics or []:
        diagnostic(message)

    public = _public_manifest(manifest)
    expected_evidence = {item["id"]: item for item in manifest["evidence"]}
    inspection_groups: Dict[str, List[Dict[str, Any]]] = {}
    for record in evidence:
        identifier = record.get("id")
        if identifier not in expected_evidence:
            diagnostic(f"unexpected inspection for evidence {identifier!r}")
            continue
        inspection_groups.setdefault(identifier, []).append(record)

    verified_by_id: Dict[str, Dict[str, Any]] = {}
    blocked_evidence = 0
    for item in manifest["evidence"]:
        identifier = item["id"]
        records = inspection_groups.get(identifier, [])
        if len(records) != 1:
            blocked_evidence += 1
            if not records:
                diagnostic(f"evidence {identifier}: inspection is missing")
            else:
                diagnostic(f"evidence {identifier}: duplicate inspections")
            continue
        record = records[0]
        contract = record.get("contract")
        verified = (
            record.get("status") == "VERIFIED"
            and record.get("copy_allowed") is True
            and record.get("requires_copy_revalidation") is True
            and record.get("target_id") == manifest["target"]["id"]
            and isinstance(contract, dict)
            and contract.get("path") == manifest["contract"]["path"]
            and contract.get("sha256") == manifest["contract"]["sha256"]
            and all(
                record.get(name) == item[name]
                for name in ("path", "sha256", "media_type", "size_bytes")
            )
        )
        if verified:
            verified_by_id[identifier] = _public_verified(record)
        else:
            blocked_evidence += 1
            message = record.get("diagnostic")
            diagnostic(
                message
                if isinstance(message, str) and message
                else f"evidence {identifier}: inspection is blocked or inconsistent"
            )

    if len(evidence) != len(manifest["evidence"]):
        # Missing, duplicate, and unexpected records are already identified above. This
        # condition also guarantees an unexpected record cannot coexist with global PASS.
        diagnostic("evidence inspection inventory does not match the manifest")

    terminal_cases, invalid_case_history = _terminal_records(
        manifest["cases"],
        logical_key="case_id",
        label="case",
        diagnostic=diagnostic,
    )
    terminal_by_logical = {item["case_id"]: item for item in terminal_cases}
    terminal_by_attempt = {item["id"]: item for item in terminal_cases}
    criteria_by_id = {item["id"]: item for item in manifest["criteria"]}

    def all_evidence_verified(item: Dict[str, Any]) -> bool:
        references = item.get("evidence_ids", [])
        return bool(references) and all(ref in verified_by_id for ref in references)

    def any_evidence_verified(item: Dict[str, Any]) -> bool:
        return any(ref in verified_by_id for ref in item.get("evidence_ids", []))

    def valid_not_applicable(case: Dict[str, Any]) -> bool:
        criterion_ids = case.get("criterion_ids", [])
        if not criterion_ids:
            return False
        related = [criteria_by_id.get(identifier) for identifier in criterion_ids]
        return all(
            criterion is not None
            and not criterion["applicable"]
            and bool(criterion["applicability_reason"])
            and case["case_id"] in criterion["case_ids"]
            for criterion in related
        )

    proven_case_failure = False
    pending = bool(diagnostics) or invalid_case_history or blocked_evidence > 0
    for case in terminal_cases:
        status = case.get("status")
        substantive_case = bool(case.get("expected", "").strip()) and bool(
            case.get("observed", "").strip()
        )
        if (
            case.get("required")
            and status not in ("NOT_RUN", "NOT_APPLICABLE")
            and not substantive_case
        ):
            diagnostic(
                f"case {case['id']}: executed required case lacks expected or observed content"
            )
            pending = True
        if status not in _CASE_RESULTS:
            diagnostic(f"case {case['id']}: unknown terminal status {status!r}")
            pending = True
        elif status == "FAIL":
            if any_evidence_verified(case):
                proven_case_failure = True
                diagnostic(f"case {case['id']}: proven current failure")
            else:
                diagnostic(f"case {case['id']}: FAIL lacks verified evidence")
                pending = True
        elif status == "NOT_APPLICABLE" and valid_not_applicable(case):
            continue
        elif status != "PASS":
            diagnostic(f"case {case['id']}: terminal status {status}")
            pending = True
        elif case.get("required") and not all_evidence_verified(case):
            diagnostic(f"case {case['id']}: PASS lacks complete verified evidence")
            pending = True

    applicable_count = sum(bool(item["applicable"]) for item in manifest["criteria"])
    required_terminal_count = sum(bool(item.get("required")) for item in terminal_cases)
    if not manifest["criteria"]:
        diagnostic("no criteria")
        pending = True
    if applicable_count == 0:
        diagnostic("no applicable criteria")
        pending = True
    if required_terminal_count == 0:
        diagnostic("no required cases")
        pending = True
    if not manifest["contract"]["criteria_review"]["complete"]:
        diagnostic("criteria transcription completeness is not confirmed")
        pending = True

    criterion_results: List[Dict[str, str]] = []
    for criterion in manifest["criteria"]:
        identifier = criterion["id"]
        if not criterion["applicable"]:
            result = "NOT_APPLICABLE"
        else:
            assessment = criterion["assessment"]
            substantive_assessment = bool(assessment["expected"].strip()) and bool(
                assessment["observed"].strip()
            )
            required_cases = []
            missing_cases = []
            non_reciprocal = []
            for case_id in criterion["case_ids"]:
                case = terminal_by_logical.get(case_id)
                if case is None:
                    missing_cases.append(case_id)
                elif identifier not in case.get("criterion_ids", []):
                    non_reciprocal.append(case_id)
                elif case.get("required"):
                    required_cases.append(case)
            non_reciprocal.extend(
                case["case_id"]
                for case in terminal_cases
                if identifier in case.get("criterion_ids", [])
                and case["case_id"] not in criterion["case_ids"]
            )
            proven_failures = [
                case
                for case in required_cases
                if case.get("status") == "FAIL" and any_evidence_verified(case)
            ]
            if not substantive_assessment:
                result = "BLOCKED"
                diagnostic(f"criterion {identifier}: substantive assessment is incomplete")
                pending = True
            elif proven_failures:
                result = "FAIL"
            elif non_reciprocal:
                result = "BLOCKED"
                diagnostic(f"criterion {identifier}: non-reciprocal case links")
                pending = True
            elif missing_cases or not required_cases:
                result = "BLOCKED"
                diagnostic(f"criterion {identifier}: no complete required case set")
                pending = True
            elif any(case.get("status") == "NOT_APPLICABLE" for case in required_cases):
                result = "BLOCKED"
                diagnostic(f"criterion {identifier}: invalid NOT_APPLICABLE waiver")
                pending = True
            elif any(case.get("status") == "BLOCKED" for case in required_cases):
                result = "BLOCKED"
                pending = True
            elif any(case.get("status") == "NOT_RUN" for case in required_cases):
                result = "NOT_RUN"
                pending = True
            elif any(case.get("status") == "FAIL" for case in required_cases):
                result = "BLOCKED"
                pending = True
            elif all(
                case.get("status") == "PASS" and all_evidence_verified(case)
                for case in required_cases
            ):
                result = "PASS"
            else:
                result = "BLOCKED"
                pending = True
        criterion_results.append({"id": identifier, "result": result})

    terminal_defects, invalid_defect_history = _terminal_records(
        manifest["defects"],
        logical_key=None,
        label="defect",
        diagnostic=diagnostic,
    )
    pending = pending or invalid_defect_history
    proven_defect_failure = False
    current_in_scope = 0
    out_of_scope = 0
    for defect in terminal_defects:
        scope_is_consistent = defect["in_scope"] == (defect["status"] != "out_of_scope")
        if not scope_is_consistent:
            diagnostic(f"defect {defect['id']}: contradictory scope markers")
            pending = True
            continue
        if not defect["in_scope"]:
            out_of_scope += 1
            continue
        closed = False
        if defect["status"] == "resolved":
            retest = terminal_by_attempt.get(defect["retest_attempt_id"])
            closed = bool(
                retest
                and retest.get("status") == "PASS"
                and all_evidence_verified(retest)
            )
        if closed:
            continue
        current_in_scope += 1
        if any_evidence_verified(defect):
            proven_defect_failure = True
            diagnostic(f"defect {defect['id']}: proven current in-scope failure")
        else:
            diagnostic(f"defect {defect['id']}: current state lacks verified evidence")
            pending = True

    result_values = [item["result"] for item in criterion_results]
    if proven_case_failure or proven_defect_failure:
        verdict = "FAIL"
    elif (
        pending
        or any(
            result not in ("PASS", "NOT_APPLICABLE") for result in result_values
        )
        or any(
            item["applicable"] and result["result"] != "PASS"
            for item, result in zip(manifest["criteria"], criterion_results)
        )
        or current_in_scope
    ):
        verdict = "BLOCKED"
    else:
        verdict = "PASS"

    counts = {
        "criteria_total": len(manifest["criteria"]),
        "criteria_applicable": applicable_count,
        "criteria_pass": result_values.count("PASS"),
        "criteria_fail": result_values.count("FAIL"),
        "criteria_blocked": result_values.count("BLOCKED"),
        "criteria_not_run": result_values.count("NOT_RUN"),
        "criteria_not_applicable": result_values.count("NOT_APPLICABLE"),
        "cases_total": len(manifest["cases"]),
        "cases_terminal": len(terminal_cases),
        "defects_total": len(manifest["defects"]),
        "defects_current_in_scope": current_in_scope,
        "defects_out_of_scope": out_of_scope,
        "evidence_verified": len(verified_by_id),
        "evidence_blocked": blocked_evidence,
    }
    public.update(
        criterion_results=criterion_results,
        verdict=verdict,
        counts=counts,
        diagnostics=diagnostics,
        verified_evidence=[
            verified_by_id[item["id"]]
            for item in manifest["evidence"]
            if item["id"] in verified_by_id
        ],
    )
    if _json_contains_credential(public):
        raise EvidenceError(
            "public report contains credential-like data; publication refused"
        )
    return public
