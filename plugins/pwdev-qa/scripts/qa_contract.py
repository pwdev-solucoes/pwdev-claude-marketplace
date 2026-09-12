"""Load and validate PWDEV QA report manifests (schema version 1)."""

from __future__ import annotations

import copy
import json
import re
import stat
from datetime import datetime
from pathlib import Path, PurePosixPath, PureWindowsPath
from typing import Any, Dict, Iterable, List, Optional, Set, Tuple


MAX_MANIFEST_BYTES = 5 * 1024 * 1024
MAX_CRITERIA = 1000
MAX_EVIDENCE = 1000
MAX_EVIDENCE_BYTES = 10 * 1024 * 1024
MAX_TOTAL_EVIDENCE_BYTES = 100 * 1024 * 1024

_RUN_ID = re.compile(r"^[a-z0-9][a-z0-9-]{0,63}$")
_SHA256 = re.compile(r"^[0-9a-f]{64}$")
_TIMESTAMP = re.compile(
    r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+-]\d{2}:\d{2})$"
)
_CASE_STATUSES = {"PASS", "FAIL", "BLOCKED", "NOT_RUN", "NOT_APPLICABLE"}
_MEDIA_TYPES = {"text/plain", "application/json", "image/png", "image/jpeg"}
_SANITIZATION_STATUSES = {"synthetic", "reviewed", "pending"}
_DEFECT_STATUSES = {"open", "resolved", "out_of_scope"}


class ValidationError(ValueError):
    """Raised when a report manifest is malformed or violates the v1 contract."""


def _fail(path: str, message: str) -> None:
    raise ValidationError(f"{path}: {message}")


def _object(value: Any, path: str) -> Dict[str, Any]:
    if type(value) is not dict:
        _fail(path, "expected object")
    return value


def _array(value: Any, path: str) -> List[Any]:
    if type(value) is not list:
        _fail(path, "expected array")
    return value


def _string(value: Any, path: str, *, nonempty: bool = True) -> str:
    if type(value) is not str:
        _fail(path, "expected string")
    if nonempty and not value:
        _fail(path, "must not be empty")
    return value


def _boolean(value: Any, path: str) -> bool:
    if type(value) is not bool:
        _fail(path, "expected boolean")
    return value


def _integer(
    value: Any, path: str, *, minimum: Optional[int] = None, nullable: bool = False
) -> Optional[int]:
    if nullable and value is None:
        return None
    if type(value) is not int:
        _fail(path, "expected integer (boolean is not an integer)")
    if minimum is not None and value < minimum:
        _fail(path, f"must be at least {minimum}")
    return value


def _required(value: Dict[str, Any], path: str, names: Iterable[str]) -> None:
    for name in names:
        if name not in value:
            _fail(path, f"missing required field {name!r}")


def _enum(value: Any, path: str, choices: Set[str]) -> str:
    result = _string(value, path)
    if result not in choices:
        _fail(path, f"unknown value {result!r}; expected one of {sorted(choices)}")
    return result


def _timestamp(value: Any, path: str) -> str:
    if type(value) is not str:
        _fail(path, "invalid ISO-8601 timestamp with timezone")
    result = value
    if not _TIMESTAMP.fullmatch(result):
        _fail(path, "invalid ISO-8601 timestamp with timezone")
    try:
        parsed = datetime.fromisoformat(result[:-1] + "+00:00" if result.endswith("Z") else result)
    except ValueError as error:
        raise ValidationError(f"{path}: invalid ISO-8601 timestamp with timezone") from error
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        _fail(path, "invalid ISO-8601 timestamp with timezone")
    return result


def _sha256(value: Any, path: str) -> str:
    result = _string(value, path)
    if not _SHA256.fullmatch(result):
        _fail(path, "expected lowercase SHA-256 digest")
    return result


def _relative_path(value: Any, path: str) -> str:
    result = _string(value, path)
    if "\x00" in result or "\\" in result:
        _fail(path, "path must be a normalized repository-relative POSIX path")
    posix = PurePosixPath(result)
    if (
        posix.is_absolute()
        or PureWindowsPath(result).is_absolute()
        or any(part in ("", ".", "..") for part in result.split("/"))
        or posix.as_posix() != result
    ):
        _fail(path, "path must be normalized, repository-relative, and traversal-free")
    return result


def _nullable_id(value: Any, path: str) -> Optional[str]:
    if value is None:
        return None
    return _string(value, path)


def _string_list(value: Any, path: str) -> List[str]:
    result = _array(value, path)
    seen: Set[str] = set()
    for index, item in enumerate(result):
        identifier = _string(item, f"{path}[{index}]")
        if identifier in seen:
            _fail(path, f"duplicate reference {identifier!r}")
        seen.add(identifier)
    return result


def _unique_ids(items: List[Any], path: str) -> Set[str]:
    seen: Set[str] = set()
    for index, item in enumerate(items):
        record = _object(item, f"{path}[{index}]")
        identifier = _string(record.get("id"), f"{path}[{index}].id")
        if identifier in seen:
            _fail(path, f"duplicate id {identifier!r}")
        seen.add(identifier)
    return seen


def _validate_review(value: Any, path: str, *, include_complete: bool) -> None:
    review = _object(value, path)
    names = ["actor", "at"]
    if include_complete:
        names.append("complete")
    _required(review, path, names)
    _string(review["actor"], f"{path}.actor")
    _timestamp(review["at"], f"{path}.at")
    if include_complete:
        _boolean(review["complete"], f"{path}.complete")


def _validate_criteria(items: List[Any]) -> None:
    if len(items) > MAX_CRITERIA:
        _fail("criteria", f"at most {MAX_CRITERIA} records are allowed")
    _unique_ids(items, "criteria")
    required = (
        "id",
        "text",
        "applicable",
        "applicability_reason",
        "assessment",
        "case_ids",
    )
    for index, value in enumerate(items):
        path = f"criteria[{index}]"
        item = _object(value, path)
        _required(item, path, required)
        _string(item["text"], f"{path}.text")
        _boolean(item["applicable"], f"{path}.applicable")
        reason = _string(
            item["applicability_reason"], f"{path}.applicability_reason", nonempty=False
        )
        if not item["applicable"] and not reason:
            _fail(f"{path}.applicability_reason", "non-applicable criterion requires a reason")
        assessment = _object(item["assessment"], f"{path}.assessment")
        _required(assessment, f"{path}.assessment", ("actor", "at", "expected", "observed"))
        _string(assessment["actor"], f"{path}.assessment.actor")
        _timestamp(assessment["at"], f"{path}.assessment.at")
        _string(assessment["expected"], f"{path}.assessment.expected", nonempty=False)
        _string(assessment["observed"], f"{path}.assessment.observed", nonempty=False)
        _string_list(item["case_ids"], f"{path}.case_ids")


def _validate_cases(items: List[Any]) -> None:
    _unique_ids(items, "cases")
    required = (
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
    )
    attempts: Set[Tuple[str, int]] = set()
    last_attempt: Dict[str, int] = {}
    for index, value in enumerate(items):
        path = f"cases[{index}]"
        item = _object(value, path)
        _required(item, path, required)
        case_id = _string(item["case_id"], f"{path}.case_id")
        _string_list(item["criterion_ids"], f"{path}.criterion_ids")
        _enum(item["status"], f"{path}.status", _CASE_STATUSES)
        _boolean(item["required"], f"{path}.required")
        _string(item["expected"], f"{path}.expected", nonempty=False)
        _string(item["observed"], f"{path}.observed", nonempty=False)
        _string(item["command"], f"{path}.command", nonempty=False)
        _integer(item["exit_code"], f"{path}.exit_code", nullable=True)
        _string_list(item["evidence_ids"], f"{path}.evidence_ids")
        attempt = _integer(item["attempt"], f"{path}.attempt", minimum=1)
        assert attempt is not None
        if (case_id, attempt) in attempts:
            _fail(path, f"duplicate attempt {attempt} for case_id {case_id!r}")
        attempts.add((case_id, attempt))
        if case_id in last_attempt and attempt <= last_attempt[case_id]:
            _fail(f"{path}.attempt", "attempts must be increasing by case_id")
        last_attempt[case_id] = attempt
        _nullable_id(item["supersedes"], f"{path}.supersedes")


def _validate_evidence(items: List[Any]) -> None:
    if len(items) > MAX_EVIDENCE:
        _fail("evidence", f"at most {MAX_EVIDENCE} records are allowed")
    _unique_ids(items, "evidence")
    required = (
        "id",
        "path",
        "sha256",
        "media_type",
        "size_bytes",
        "target_id",
        "sanitization",
    )
    total_size = 0
    for index, value in enumerate(items):
        path = f"evidence[{index}]"
        item = _object(value, path)
        _required(item, path, required)
        _relative_path(item["path"], f"{path}.path")
        _sha256(item["sha256"], f"{path}.sha256")
        _enum(item["media_type"], f"{path}.media_type", _MEDIA_TYPES)
        size = _integer(item["size_bytes"], f"{path}.size_bytes", minimum=0)
        assert size is not None
        if size > MAX_EVIDENCE_BYTES:
            _fail(f"{path}.size_bytes", "declared evidence exceeds the 10 MiB limit")
        total_size += size
        _string(item["target_id"], f"{path}.target_id")
        sanitization = _object(item["sanitization"], f"{path}.sanitization")
        _required(sanitization, f"{path}.sanitization", ("status", "actor", "at"))
        _enum(
            sanitization["status"],
            f"{path}.sanitization.status",
            _SANITIZATION_STATUSES,
        )
        _string(sanitization["actor"], f"{path}.sanitization.actor")
        _timestamp(sanitization["at"], f"{path}.sanitization.at")
    if total_size > MAX_TOTAL_EVIDENCE_BYTES:
        _fail("evidence", "declared evidence exceeds the 100 MiB aggregate limit")


def _validate_defects(items: List[Any]) -> None:
    _unique_ids(items, "defects")
    required = (
        "id",
        "summary",
        "in_scope",
        "status",
        "severity",
        "criterion_ids",
        "evidence_ids",
        "supersedes",
        "retest_attempt_id",
    )
    for index, value in enumerate(items):
        path = f"defects[{index}]"
        item = _object(value, path)
        _required(item, path, required)
        _string(item["summary"], f"{path}.summary")
        _boolean(item["in_scope"], f"{path}.in_scope")
        status_value = _enum(item["status"], f"{path}.status", _DEFECT_STATUSES)
        _string(item["severity"], f"{path}.severity")
        _string_list(item["criterion_ids"], f"{path}.criterion_ids")
        _string_list(item["evidence_ids"], f"{path}.evidence_ids")
        _nullable_id(item["supersedes"], f"{path}.supersedes")
        retest = _nullable_id(item["retest_attempt_id"], f"{path}.retest_attempt_id")
        if status_value == "resolved" and retest is None:
            _fail(f"{path}.retest_attempt_id", "resolved defect requires a retest_attempt_id")


def _require_references(values: Iterable[str], known: Set[str], path: str, kind: str) -> None:
    for value in values:
        if value not in known:
            _fail(path, f"unresolved {kind} reference {value!r}")


def _validate_references(data: Dict[str, Any]) -> None:
    criteria_ids = {item["id"] for item in data["criteria"]}
    case_attempt_ids = {item["id"] for item in data["cases"]}
    logical_case_ids = {item["case_id"] for item in data["cases"]}
    evidence_ids = {item["id"] for item in data["evidence"]}
    defect_ids = {item["id"] for item in data["defects"]}
    target_id = data["target"]["id"]

    for index, item in enumerate(data["criteria"]):
        _require_references(item["case_ids"], logical_case_ids, f"criteria[{index}].case_ids", "logical case")
    for index, item in enumerate(data["cases"]):
        _require_references(item["criterion_ids"], criteria_ids, f"cases[{index}].criterion_ids", "criterion")
        _require_references(item["evidence_ids"], evidence_ids, f"cases[{index}].evidence_ids", "evidence")
    for index, item in enumerate(data["evidence"]):
        if item["target_id"] != target_id:
            _fail(f"evidence[{index}].target_id", f"unresolved target reference {item['target_id']!r}")
    for index, item in enumerate(data["defects"]):
        _require_references(item["criterion_ids"], criteria_ids, f"defects[{index}].criterion_ids", "criterion")
        _require_references(item["evidence_ids"], evidence_ids, f"defects[{index}].evidence_ids", "evidence")
        if item["supersedes"] is not None:
            _require_references((item["supersedes"],), defect_ids, f"defects[{index}].supersedes", "defect")
            if item["supersedes"] == item["id"]:
                _fail(f"defects[{index}].supersedes", "a defect cannot supersede itself")
        if item["retest_attempt_id"] is not None:
            _require_references(
                (item["retest_attempt_id"],),
                case_attempt_ids,
                f"defects[{index}].retest_attempt_id",
                "retest attempt",
            )


def _validate_case_chains(items: List[Dict[str, Any]]) -> None:
    by_id = {item["id"]: item for item in items}
    children: Dict[str, str] = {}
    for index, item in enumerate(items):
        predecessor_id = item["supersedes"]
        if predecessor_id is None:
            continue
        if predecessor_id not in by_id:
            _fail(f"cases[{index}].supersedes", f"unresolved attempt reference {predecessor_id!r}")
        predecessor = by_id[predecessor_id]
        if predecessor["case_id"] != item["case_id"]:
            _fail(f"cases[{index}].supersedes", "superseded attempt must have the same case_id")
        if predecessor["attempt"] >= item["attempt"]:
            _fail(f"cases[{index}].supersedes", "superseded attempt must be prior")
        if predecessor_id in children:
            _fail(f"cases[{index}].supersedes", "retest chain cannot branch")
        children[predecessor_id] = item["id"]
    by_case: Dict[str, List[Dict[str, Any]]] = {}
    for item in items:
        by_case.setdefault(item["case_id"], []).append(item)
    for case_id, attempts in by_case.items():
        if attempts[0]["supersedes"] is not None:
            _fail("cases", f"retest chain for case_id {case_id!r} has no initial attempt")
        for previous, current in zip(attempts, attempts[1:]):
            if current["supersedes"] != previous["id"]:
                _fail("cases", f"retest chain for case_id {case_id!r} is disconnected")


def _validate_defect_chains(items: List[Dict[str, Any]]) -> None:
    by_id = {item["id"]: item for item in items}
    children: Set[str] = set()
    for index, item in enumerate(items):
        current = item["supersedes"]
        if current is not None:
            if current in children:
                _fail(f"defects[{index}].supersedes", "defect history cannot branch")
            children.add(current)
        visited = {item["id"]}
        while current is not None:
            if current in visited:
                _fail(f"defects[{index}].supersedes", "defect history contains a cycle")
            visited.add(current)
            current = by_id[current]["supersedes"]


def validate_manifest(data: dict) -> dict:
    """Validate *data* as a v1 manifest and return an independent normalized copy.

    Unknown fields are retained in that copy. This function does not create a public
    projection, so extensions remain data only and are not implicitly published.
    """

    manifest = _object(data, "manifest")
    required = (
        "schema_version",
        "run_id",
        "project",
        "target",
        "executed_at",
        "contract",
        "criteria",
        "cases",
        "evidence",
        "defects",
    )
    _required(manifest, "manifest", required)
    version = _integer(manifest["schema_version"], "schema_version")
    if version != 1:
        _fail("schema_version", "only schema_version=1 is supported")
    run_id = _string(manifest["run_id"], "run_id")
    if not _RUN_ID.fullmatch(run_id):
        _fail("run_id", "must match ^[a-z0-9][a-z0-9-]{0,63}$")
    _string(manifest["project"], "project")
    target = _object(manifest["target"], "target")
    _required(target, "target", ("id", "kind"))
    _string(target["id"], "target.id")
    _string(target["kind"], "target.kind")
    _timestamp(manifest["executed_at"], "executed_at")

    contract = _object(manifest["contract"], "contract")
    _required(contract, "contract", ("path", "sha256", "criteria_review"))
    _relative_path(contract["path"], "contract.path")
    _sha256(contract["sha256"], "contract.sha256")
    _validate_review(contract["criteria_review"], "contract.criteria_review", include_complete=True)

    criteria = _array(manifest["criteria"], "criteria")
    cases = _array(manifest["cases"], "cases")
    evidence = _array(manifest["evidence"], "evidence")
    defects = _array(manifest["defects"], "defects")
    _validate_criteria(criteria)
    _validate_cases(cases)
    _validate_evidence(evidence)
    _validate_defects(defects)
    _validate_references(manifest)
    _validate_case_chains(cases)
    _validate_defect_chains(defects)
    return copy.deepcopy(manifest)


def load_manifest(path: Path) -> dict:
    """Read and validate a UTF-8 JSON manifest without truncating oversized input."""

    candidate = Path(path)
    try:
        metadata = candidate.lstat()
    except OSError as error:
        raise ValidationError(f"manifest file cannot be inspected: {error}") from error
    if stat.S_ISLNK(metadata.st_mode) or not stat.S_ISREG(metadata.st_mode):
        raise ValidationError("manifest path must be a regular file, not a symlink")
    if metadata.st_size > MAX_MANIFEST_BYTES:
        raise ValidationError("manifest exceeds the 5 MiB limit")
    try:
        raw = candidate.read_bytes()
    except OSError as error:
        raise ValidationError(f"manifest file cannot be read: {error}") from error
    if len(raw) > MAX_MANIFEST_BYTES:
        raise ValidationError("manifest exceeds the 5 MiB limit")
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError as error:
        raise ValidationError("manifest is not valid UTF-8") from error
    def reject_duplicate_fields(pairs: List[Tuple[str, Any]]) -> Dict[str, Any]:
        result: Dict[str, Any] = {}
        for name, value in pairs:
            if name in result:
                raise ValidationError(f"manifest JSON contains duplicate field {name!r}")
            result[name] = value
        return result

    def reject_constant(value: str) -> None:
        raise ValidationError(f"manifest JSON contains invalid number {value!r}")

    try:
        data = json.loads(
            text,
            object_pairs_hook=reject_duplicate_fields,
            parse_constant=reject_constant,
        )
    except json.JSONDecodeError as error:
        raise ValidationError(f"manifest is not valid JSON: {error.msg}") from error
    return validate_manifest(data)
