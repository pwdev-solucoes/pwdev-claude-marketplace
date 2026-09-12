"""Confine, verify, and sanitize PWDEV QA evidence attachments."""

from __future__ import annotations

import hashlib
import json
import os
import re
import stat
import struct
from pathlib import Path, PurePosixPath, PureWindowsPath
from typing import Any, Dict, List, Optional, Tuple


MAX_EVIDENCE_BYTES = 10 * 1024 * 1024
MAX_TOTAL_EVIDENCE_BYTES = 100 * 1024 * 1024
MAX_IMAGE_PIXELS = 20_000_000

_PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"
_JPEG_SIGNATURE = b"\xff\xd8\xff"
_CREDENTIAL_PATTERNS = (
    re.compile(r"(?i)authorization\s*:\s*(?:bearer|basic)\s+\S+"),
    re.compile(
        r"(?i)(?:api[_-]?key|access[_-]?token|auth[_-]?token|password|passwd|secret)"
        r"[\"']?\s*[:=]\s*[\"']?[^\s\"',}]{8,}"
    ),
    re.compile(r"AKIA[0-9A-Z]{16}"),
    re.compile(r"gh[pousr]_[A-Za-z0-9]{20,}"),
    re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
)
_SENSITIVE_NAMES = {".env", "id_rsa", "id_dsa", "id_ecdsa", "id_ed25519"}


class EvidenceError(ValueError):
    """Raised when evidence violates a safety boundary and export must stop."""


def _error(identifier: str, message: str) -> None:
    raise EvidenceError(f"evidence {identifier!r}: {message}")


def _public_base(item: Dict[str, Any], manifest: Dict[str, Any]) -> Dict[str, Any]:
    contract = manifest["contract"]
    return {
        "id": item["id"],
        "target_id": item["target_id"],
        "contract": {"path": contract["path"], "sha256": contract["sha256"]},
    }


def _blocked(
    item: Dict[str, Any], manifest: Dict[str, Any], diagnostic: str
) -> Dict[str, Any]:
    result = _public_base(item, manifest)
    result.update(status="BLOCKED", copy_allowed=False, diagnostic=diagnostic)
    return result


def _verified(
    item: Dict[str, Any], manifest: Dict[str, Any], actual_size: int
) -> Dict[str, Any]:
    result = _public_base(item, manifest)
    result.update(
        status="VERIFIED",
        copy_allowed=True,
        path=item["path"],
        sha256=item["sha256"],
        media_type=item["media_type"],
        size_bytes=actual_size,
        diagnostic=None,
    )
    return result


def _safe_parts(identifier: str, value: Any) -> Tuple[str, ...]:
    if type(value) is not str or not value or "\x00" in value or "\\" in value:
        _error(identifier, "path is not confined to the project root")
    path = PurePosixPath(value)
    parts = tuple(value.split("/"))
    if (
        path.is_absolute()
        or PureWindowsPath(value).is_absolute()
        or any(part in ("", ".", "..") for part in parts)
        or path.as_posix() != value
    ):
        _error(identifier, "path is not confined to the project root")
    return parts


def _reject_sensitive_path(identifier: str, parts: Tuple[str, ...]) -> None:
    for part in parts:
        lowered = part.lower()
        if (
            lowered in _SENSITIVE_NAMES
            or lowered.startswith(".env.")
            or lowered in {"credentials.json", "secrets.json"}
            or lowered.endswith((".pem", ".key", ".p12", ".pfx"))
        ):
            _error(identifier, "sensitive path is not eligible as evidence")


def _inspect_path(
    root: Path, parts: Tuple[str, ...], identifier: str
) -> Tuple[Optional[Path], Optional[os.stat_result]]:
    current = root
    for index, part in enumerate(parts):
        current = current / part
        try:
            metadata = current.lstat()
        except FileNotFoundError:
            return None, None
        except OSError as error:
            raise EvidenceError(f"evidence {identifier!r}: path cannot be inspected") from error
        if stat.S_ISLNK(metadata.st_mode):
            _error(identifier, "symlink in evidence path is forbidden")
        if index < len(parts) - 1 and not stat.S_ISDIR(metadata.st_mode):
            _error(identifier, "evidence parent must be a local directory")
    if not stat.S_ISREG(metadata.st_mode):
        _error(identifier, "evidence must be a regular local file")
    return current, metadata


def _read_regular(path: Path, metadata: os.stat_result, identifier: str) -> bytes:
    flags = os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0)
    try:
        descriptor = os.open(str(path), flags)
    except OSError as error:
        raise EvidenceError(f"evidence {identifier!r}: regular file cannot be opened safely") from error
    try:
        opened = os.fstat(descriptor)
        if (
            not stat.S_ISREG(opened.st_mode)
            or opened.st_dev != metadata.st_dev
            or opened.st_ino != metadata.st_ino
        ):
            _error(identifier, "evidence changed during safe inspection")
        chunks: List[bytes] = []
        observed = 0
        while True:
            chunk = os.read(descriptor, 1024 * 1024)
            if not chunk:
                break
            observed += len(chunk)
            if observed > MAX_EVIDENCE_BYTES:
                _error(identifier, "actual evidence exceeds the 10 MiB limit")
            chunks.append(chunk)
        raw = b"".join(chunks)
        final = os.fstat(descriptor)
        if final.st_size != metadata.st_size or len(raw) != final.st_size:
            _error(identifier, "evidence changed during safe inspection")
        return raw
    finally:
        os.close(descriptor)


def _png_dimensions(raw: bytes, identifier: str) -> Tuple[int, int]:
    if len(raw) < 24 or raw[:8] != _PNG_SIGNATURE or raw[12:16] != b"IHDR":
        _error(identifier, "actual media type does not match image/png")
    width, height = struct.unpack(">II", raw[16:24])
    if width == 0 or height == 0:
        _error(identifier, "image dimensions are invalid")
    return width, height


def _jpeg_dimensions(raw: bytes, identifier: str) -> Tuple[int, int]:
    if len(raw) < 4 or not raw.startswith(_JPEG_SIGNATURE):
        _error(identifier, "actual media type does not match image/jpeg")
    offset = 2
    while offset < len(raw):
        if raw[offset] != 0xFF:
            offset += 1
            continue
        while offset < len(raw) and raw[offset] == 0xFF:
            offset += 1
        if offset >= len(raw):
            break
        marker = raw[offset]
        offset += 1
        if marker in (0xD8, 0xD9) or 0xD0 <= marker <= 0xD7:
            continue
        if offset + 2 > len(raw):
            break
        segment_length = struct.unpack(">H", raw[offset : offset + 2])[0]
        if segment_length < 2 or offset + segment_length > len(raw):
            break
        if marker in {
            0xC0,
            0xC1,
            0xC2,
            0xC3,
            0xC5,
            0xC6,
            0xC7,
            0xC9,
            0xCA,
            0xCB,
            0xCD,
            0xCE,
            0xCF,
        }:
            if segment_length < 7:
                break
            height, width = struct.unpack(">HH", raw[offset + 3 : offset + 7])
            if width == 0 or height == 0:
                break
            return width, height
        offset += segment_length
    _error(identifier, "image/jpeg dimensions cannot be verified")
    raise AssertionError("unreachable")


def _text(raw: bytes, identifier: str, media_type: str) -> str:
    if raw.startswith((_PNG_SIGNATURE, _JPEG_SIGNATURE)) or b"\x00" in raw:
        _error(identifier, f"actual media type does not match {media_type}")
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError as error:
        raise EvidenceError(
            f"evidence {identifier!r}: actual media type does not match {media_type}"
        ) from error
    stripped = text.lstrip()
    if media_type == "text/plain" and stripped.startswith(("{", "[")):
        try:
            json.loads(text)
        except (json.JSONDecodeError, RecursionError):
            pass
        else:
            _error(identifier, "actual media type does not match text/plain")
    if media_type == "application/json":
        try:
            json.loads(text)
        except (json.JSONDecodeError, RecursionError) as error:
            raise EvidenceError(
                f"evidence {identifier!r}: actual media type does not match application/json"
            ) from error
    return text


def _verify_media(raw: bytes, identifier: str, media_type: str) -> Optional[str]:
    if media_type == "image/png":
        width, height = _png_dimensions(raw, identifier)
    elif media_type == "image/jpeg":
        width, height = _jpeg_dimensions(raw, identifier)
    elif media_type in ("text/plain", "application/json"):
        return _text(raw, identifier, media_type)
    else:
        _error(identifier, "media type is not accepted")
    if width * height > MAX_IMAGE_PIXELS:
        _error(identifier, "image exceeds the 20 megapixels limit")
    return None


def _contains_credential(text: Optional[str]) -> bool:
    return text is not None and any(pattern.search(text) for pattern in _CREDENTIAL_PATTERNS)


def inspect_evidence(root: Path, manifest: dict) -> list[dict]:
    """Return a safe public projection after revalidating every evidence file.

    Unsafe paths, formats, and limits raise :class:`EvidenceError`, which tells the
    caller not to export. Missing, changed, target-incompatible, credential-bearing,
    or pending-review attachments return sanitized ``BLOCKED`` diagnostics and are
    never marked copyable.
    """

    project_root = Path(root)
    try:
        root_metadata = project_root.lstat()
    except OSError as error:
        raise EvidenceError("project root cannot be inspected") from error
    if stat.S_ISLNK(root_metadata.st_mode) or not stat.S_ISDIR(root_metadata.st_mode):
        raise EvidenceError("project root must be a regular local directory, not a symlink")

    records: List[Dict[str, Any]] = []
    actual_total = 0
    for item in manifest["evidence"]:
        identifier = item["id"]
        parts = _safe_parts(identifier, item["path"])
        _reject_sensitive_path(identifier, parts)
        candidate, metadata = _inspect_path(project_root, parts, identifier)
        if candidate is None or metadata is None:
            records.append(_blocked(item, manifest, "evidence file is missing"))
            continue

        if metadata.st_size > MAX_EVIDENCE_BYTES:
            _error(identifier, "actual evidence exceeds the 10 MiB limit")

        raw = _read_regular(candidate, metadata, identifier)
        actual_size = len(raw)
        actual_total += actual_size
        if actual_total > MAX_TOTAL_EVIDENCE_BYTES:
            _error(identifier, "actual evidence exceeds the 100 MiB aggregate limit")
        text = _verify_media(raw, identifier, item["media_type"])
        actual_hash = hashlib.sha256(raw).hexdigest()

        if item["target_id"] != manifest["target"]["id"]:
            records.append(_blocked(item, manifest, "evidence target is incompatible"))
        elif actual_size != item["size_bytes"]:
            records.append(_blocked(item, manifest, "evidence size changed"))
        elif actual_hash != item["sha256"]:
            records.append(_blocked(item, manifest, "evidence digest changed"))
        elif _contains_credential(text):
            records.append(
                _blocked(item, manifest, "credential-like data detected; attachment withheld")
            )
        elif item["sanitization"]["status"] == "pending":
            records.append(_blocked(item, manifest, "sanitization review is pending"))
        elif item["media_type"].startswith("image/") and item["sanitization"]["status"] != "reviewed":
            records.append(_blocked(item, manifest, "recorded visual sanitization review is required"))
        else:
            records.append(_verified(item, manifest, actual_size))
    return records
