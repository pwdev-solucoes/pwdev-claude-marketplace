"""Create a reproducible, deliberately failing PWDEV QA report demonstration."""

from __future__ import annotations

import argparse
import hashlib
import json
import struct
import zlib
from pathlib import Path
from typing import Any, Dict, List, Optional

from qa_report import generate_report


RUN_ID = "qa-report-demo"
EXECUTED_AT = "2026-09-12T20:00:00Z"
REVIEWED_AT = "2026-09-12T19:55:00Z"
SECRET_VALUE = "qa-secret-value-123456789"


def _sha256(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def _png_fixture(width: int = 96, height: int = 54) -> bytes:
    def chunk(kind: bytes, payload: bytes) -> bytes:
        return (
            struct.pack(">I", len(payload))
            + kind
            + payload
            + struct.pack(">I", zlib.crc32(kind + payload) & 0xFFFFFFFF)
        )

    header = struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0)
    rows = b"".join(
        b"\x00" + bytes((28, 104, 180)) * width for _ in range(height)
    )
    return (
        b"\x89PNG\r\n\x1a\n"
        + chunk(b"IHDR", header)
        + chunk(b"IDAT", zlib.compress(rows))
        + chunk(b"IEND", b"")
    )


def _criterion_text(index: int) -> str:
    tokens: List[str] = []
    word = 0
    while len(" ".join(tokens)) < 2000:
        tokens.append(f"c{index:03d}w{word:04d}á")
        word += 1
    return " ".join(tokens)[:2000]


def _manifest(contract_raw: bytes, evidence: Dict[str, bytes]) -> Dict[str, Any]:
    criteria = []
    cases = []
    for index in range(100):
        criterion_id = f"CA-{index:03d}"
        case_id = f"visual-case-{index:03d}"
        expected = f"Critério esperado íntegro {index:03d} — ação concluída"
        observed = f"Critério observado íntegro {index:03d} — ação concluída"
        criteria.append(
            {
                "id": criterion_id,
                "text": _criterion_text(index),
                "applicable": True,
                "applicability_reason": "Fixture visual e teste de paridade",
                "assessment": {
                    "actor": "qa-demo",
                    "at": EXECUTED_AT,
                    "expected": expected,
                    "observed": observed,
                },
                "case_ids": [case_id],
            }
        )
        cases.append(
            {
                "id": f"attempt-{index:03d}-1",
                "case_id": case_id,
                "criterion_ids": [criterion_id],
                "status": "PASS",
                "required": True,
                "expected": f"Caso esperado íntegro {index:03d} — saída preservada",
                "observed": f"Caso observado íntegro {index:03d} — saída preservada",
                "command": "python3 -m unittest tests.test_qa_reports_e2e",
                "exit_code": 0,
                "evidence_ids": ["ev-safe"],
                "attempt": 1,
                "supersedes": None,
            }
        )

    evidence_records = []
    definitions = (
        ("ev-safe", "artifacts/safe-result.txt", "text/plain", "synthetic"),
        ("ev-secret", "artifacts/credential-log.txt", "text/plain", "synthetic"),
        ("ev-pending-image", "artifacts/pending-image.png", "image/png", "pending"),
    )
    for identifier, path, media_type, status in definitions:
        raw = evidence[path]
        evidence_records.append(
            {
                "id": identifier,
                "path": path,
                "sha256": _sha256(raw),
                "media_type": media_type,
                "size_bytes": len(raw),
                "target_id": "qa-demo-target",
                "sanitization": {
                    "status": status,
                    "actor": "qa-demo",
                    "at": REVIEWED_AT,
                },
            }
        )

    return {
        "schema_version": 1,
        "run_id": RUN_ID,
        "project": "PWDEV QA — fixture integrada",
        "target": {"id": "qa-demo-target", "kind": "web"},
        "executed_at": EXECUTED_AT,
        "contract": {
            "path": "contract.txt",
            "sha256": _sha256(contract_raw),
            "criteria_review": {
                "actor": "qa-demo",
                "at": REVIEWED_AT,
                "complete": True,
            },
        },
        "criteria": criteria,
        "cases": cases,
        "evidence": evidence_records,
        "defects": [
            {
                "id": "BUG-OPEN-UNMAPPED",
                "summary": "Falha comprovada vigente sem critério associado",
                "in_scope": True,
                "status": "open",
                "severity": "high",
                "criterion_ids": [],
                "evidence_ids": ["ev-safe"],
                "supersedes": None,
                "retest_attempt_id": None,
            }
        ],
    }


def create_demo(output_dir: Path) -> dict:
    """Create all demo inputs and its report below one new explicit directory."""

    destination = Path(output_dir)
    destination.mkdir(parents=True, exist_ok=False)
    artifacts = destination / "artifacts"
    artifacts.mkdir()

    contract_raw = (
        "Contrato sintético reproduzível para inspecionar paridade HTML/PDF.\n"
    ).encode("utf-8")
    evidence = {
        "artifacts/safe-result.txt": (
            "Resultado sintético revisado: execução reproduzível concluída.\n"
        ).encode("utf-8"),
        "artifacts/credential-log.txt": (
            f"auth_token={SECRET_VALUE}\n"
        ).encode("utf-8"),
        "artifacts/pending-image.png": _png_fixture(),
    }
    (destination / "contract.txt").write_bytes(contract_raw)
    for relative, raw in evidence.items():
        (destination / relative).write_bytes(raw)

    manifest = _manifest(contract_raw, evidence)
    manifest_path = destination / "demo-manifest.json"
    manifest_path.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    return generate_report(manifest_path, destination)


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(prog="qa_demo.py")
    parser.add_argument("--output-dir", required=True, type=Path)
    arguments = parser.parse_args(argv)
    try:
        result = create_demo(arguments.output_dir)
    except FileExistsError:
        parser.error("--output-dir must identify a directory that does not exist")
    print(json.dumps(result, ensure_ascii=False))
    return 0 if result["export_status"] == "complete" else 3


if __name__ == "__main__":
    raise SystemExit(main())
