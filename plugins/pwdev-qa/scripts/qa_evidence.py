"""Confine, verify, and sanitize PWDEV QA evidence attachments."""

from __future__ import annotations

import hashlib
import json
import os
import re
import stat
import struct
import zlib
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
_CREDENTIAL_KEYS = re.compile(
    r"(?i)^(?:api[_-]?key|access[_-]?token|auth[_-]?token|password|passwd|secret)$"
)
_SUPPORTS_SECURE_TRAVERSAL = (
    hasattr(os, "O_NOFOLLOW")
    and os.open in os.supports_dir_fd
    and os.stat in os.supports_dir_fd
    and os.stat in os.supports_follow_symlinks
)


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
        requires_copy_revalidation=True,
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


def _open_evidence(
    root_descriptor: int, parts: Tuple[str, ...], identifier: str
) -> Tuple[Optional[int], Optional[os.stat_result]]:
    current_descriptor = os.dup(root_descriptor)
    directory_flags = (
        os.O_RDONLY | getattr(os, "O_DIRECTORY", 0) | getattr(os, "O_NOFOLLOW", 0)
    )
    try:
        for part in parts[:-1]:
            try:
                metadata = os.stat(part, dir_fd=current_descriptor, follow_symlinks=False)
            except FileNotFoundError:
                return None, None
            except OSError as error:
                raise EvidenceError(
                    f"evidence {identifier!r}: path cannot be inspected"
                ) from error
            if stat.S_ISLNK(metadata.st_mode):
                _error(identifier, "symlink in evidence path is forbidden")
            if not stat.S_ISDIR(metadata.st_mode):
                _error(identifier, "evidence parent must be a local directory")
            try:
                next_descriptor = os.open(
                    part, directory_flags, dir_fd=current_descriptor
                )
            except OSError as error:
                raise EvidenceError(
                    f"evidence {identifier!r}: parent directory cannot be opened safely"
                ) from error
            opened = os.fstat(next_descriptor)
            if opened.st_dev != metadata.st_dev or opened.st_ino != metadata.st_ino:
                os.close(next_descriptor)
                _error(identifier, "evidence path changed during safe traversal")
            os.close(current_descriptor)
            current_descriptor = next_descriptor

        filename = parts[-1]
        try:
            metadata = os.stat(filename, dir_fd=current_descriptor, follow_symlinks=False)
        except FileNotFoundError:
            return None, None
        except OSError as error:
            raise EvidenceError(f"evidence {identifier!r}: path cannot be inspected") from error
        if stat.S_ISLNK(metadata.st_mode):
            _error(identifier, "symlink in evidence path is forbidden")
        if not stat.S_ISREG(metadata.st_mode):
            _error(identifier, "evidence must be a regular local file")
        try:
            descriptor = os.open(
                filename,
                os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0),
                dir_fd=current_descriptor,
            )
        except OSError as error:
            raise EvidenceError(
                f"evidence {identifier!r}: regular file cannot be opened safely"
            ) from error
        opened = os.fstat(descriptor)
        if (
            not stat.S_ISREG(opened.st_mode)
            or opened.st_dev != metadata.st_dev
            or opened.st_ino != metadata.st_ino
        ):
            os.close(descriptor)
            _error(identifier, "evidence changed during safe inspection")
        return descriptor, opened
    finally:
        os.close(current_descriptor)


def _read_regular(descriptor: int, metadata: os.stat_result, identifier: str) -> bytes:
    try:
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
    if len(raw) < 45 or raw[:8] != _PNG_SIGNATURE:
        _error(identifier, "actual media type does not match image/png")
    offset = 8
    dimensions: Optional[Tuple[int, int]] = None
    image_layout: Optional[Tuple[int, int, int]] = None
    compressed: List[bytes] = []
    saw_end = False
    saw_palette = False
    idat_finished = False
    while offset < len(raw):
        if offset + 12 > len(raw):
            _error(identifier, "PNG structure is truncated")
        length = struct.unpack(">I", raw[offset : offset + 4])[0]
        kind = raw[offset + 4 : offset + 8]
        data_start = offset + 8
        data_end = data_start + length
        chunk_end = data_end + 4
        if chunk_end > len(raw):
            _error(identifier, "PNG structure is truncated")
        expected_crc = struct.unpack(">I", raw[data_end:chunk_end])[0]
        actual_crc = zlib.crc32(kind + raw[data_start:data_end]) & 0xFFFFFFFF
        if expected_crc != actual_crc:
            _error(identifier, "PNG chunk checksum is invalid")
        if len(kind) != 4 or not all(
            ord("A") <= byte <= ord("Z") or ord("a") <= byte <= ord("z")
            for byte in kind
        ):
            _error(identifier, "PNG chunk type is invalid")
        if dimensions is None:
            if kind != b"IHDR" or length != 13:
                _error(identifier, "PNG IHDR is invalid")
            width, height, bit_depth, color_type, compression, filtering, interlace = struct.unpack(
                ">IIBBBBB", raw[data_start:data_end]
            )
            if (
                width == 0
                or height == 0
                or compression != 0
                or filtering != 0
                or interlace not in (0, 1)
                or (color_type, bit_depth)
                not in {
                    (0, 1), (0, 2), (0, 4), (0, 8), (0, 16),
                    (2, 8), (2, 16), (3, 1), (3, 2), (3, 4), (3, 8),
                    (4, 8), (4, 16), (6, 8), (6, 16),
                }
            ):
                _error(identifier, "PNG IHDR is invalid")
            dimensions = (width, height)
            image_layout = (bit_depth, color_type, interlace)
        elif kind == b"IHDR":
            _error(identifier, "PNG contains multiple IHDR chunks")
        elif kind == b"PLTE":
            if compressed or length == 0 or length % 3 != 0 or length > 768:
                _error(identifier, "PNG palette is invalid")
            saw_palette = True
        elif kind not in {b"IDAT", b"IEND"} and kind[0] & 0x20 == 0:
            _error(identifier, "PNG contains an unsupported critical chunk")
        if kind == b"IDAT":
            if idat_finished:
                _error(identifier, "PNG IDAT chunks must be consecutive")
            compressed.append(raw[data_start:data_end])
        elif compressed:
            idat_finished = True
        if kind == b"IEND":
            if length != 0 or chunk_end != len(raw):
                _error(identifier, "PNG IEND is invalid")
            saw_end = True
            offset = chunk_end
            break
        offset = chunk_end
    if dimensions is None or not compressed or not saw_end or offset != len(raw):
        _error(identifier, "PNG structure is incomplete")
    assert image_layout is not None
    width, height = dimensions
    if width * height > MAX_IMAGE_PIXELS:
        _error(identifier, "image exceeds the 20 megapixels limit")
    bit_depth, color_type, interlace = image_layout
    if color_type == 3 and not saw_palette:
        _error(identifier, "PNG indexed image is missing its palette")
    if color_type in (0, 4) and saw_palette:
        _error(identifier, "PNG color type does not permit a palette")
    channels = {0: 1, 2: 3, 3: 1, 4: 2, 6: 4}[color_type]
    if interlace == 0:
        passes = ((width, height),)
    else:
        adam7 = (
            (0, 0, 8, 8),
            (4, 0, 8, 8),
            (0, 4, 4, 8),
            (2, 0, 4, 4),
            (0, 2, 2, 4),
            (1, 0, 2, 2),
            (0, 1, 1, 2),
        )
        passes = tuple(
            (
                (width - start_x + step_x - 1) // step_x,
                (height - start_y + step_y - 1) // step_y,
            )
            for start_x, start_y, step_x, step_y in adam7
            if width > start_x and height > start_y
        )
    pass_rows = tuple(
        (((pass_width * channels * bit_depth + 7) // 8), pass_height)
        for pass_width, pass_height in passes
    )
    exact_size = sum(pass_height * (row_bytes + 1) for row_bytes, pass_height in pass_rows)
    try:
        inflater = zlib.decompressobj()
        decoded = inflater.decompress(b"".join(compressed), exact_size + 1)
    except zlib.error as error:
        raise EvidenceError(f"evidence {identifier!r}: PNG image data is invalid") from error
    if (
        len(decoded) != exact_size
        or not inflater.eof
        or bool(inflater.unused_data)
    ):
        _error(identifier, "PNG image data is inconsistent with its dimensions")
    row_start = 0
    for row_bytes, pass_height in pass_rows:
        for _ in range(pass_height):
            if decoded[row_start] > 4:
                _error(identifier, "PNG row filter is invalid")
            row_start += row_bytes + 1
    return dimensions


def _jpeg_dimensions(raw: bytes, identifier: str) -> Tuple[int, int]:
    if len(raw) < 4 or not raw.startswith(_JPEG_SIGNATURE):
        _error(identifier, "actual media type does not match image/jpeg")
    offset = 2
    dimensions: Optional[Tuple[int, int]] = None
    saw_scan = False
    while offset < len(raw):
        if raw[offset] != 0xFF:
            _error(identifier, "JPEG marker structure is invalid")
        while offset < len(raw) and raw[offset] == 0xFF:
            offset += 1
        if offset >= len(raw):
            break
        marker = raw[offset]
        offset += 1
        if marker == 0xD9:
            if not saw_scan or dimensions is None or offset != len(raw):
                _error(identifier, "JPEG structure is incomplete")
            return dimensions
        if marker == 0xD8 or marker == 0x00 or 0xD0 <= marker <= 0xD7:
            _error(identifier, "JPEG marker structure is invalid")
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
            if dimensions is not None or segment_length < 8:
                break
            component_count = raw[offset + 7]
            if component_count == 0 or segment_length != 8 + 3 * component_count:
                break
            height, width = struct.unpack(">HH", raw[offset + 3 : offset + 7])
            if width == 0 or height == 0:
                break
            dimensions = (width, height)
        offset += segment_length
        if marker == 0xDA:
            component_count = raw[offset - segment_length + 2]
            if (
                dimensions is None
                or component_count == 0
                or segment_length != 6 + 2 * component_count
            ):
                _error(identifier, "JPEG scan header is invalid")
            saw_scan = True
            scan_start = offset
            while offset < len(raw):
                marker_start = raw.find(b"\xff", offset)
                if marker_start < 0 or marker_start + 1 >= len(raw):
                    _error(identifier, "JPEG scan is truncated")
                next_byte = raw[marker_start + 1]
                if next_byte == 0x00 or 0xD0 <= next_byte <= 0xD7:
                    offset = marker_start + 2
                    continue
                if marker_start == scan_start:
                    _error(identifier, "JPEG scan contains no image data")
                offset = marker_start
                break
    _error(identifier, "JPEG structure is incomplete")
    raise AssertionError("unreachable")


def _known_credential_text(text: str) -> bool:
    return any(pattern.search(text) for pattern in _CREDENTIAL_PATTERNS)


def _json_contains_credential(value: Any) -> bool:
    if isinstance(value, dict):
        for key, child in value.items():
            if _known_credential_text(key):
                return True
            if _CREDENTIAL_KEYS.fullmatch(key) and isinstance(child, str) and bool(child):
                return True
            if _json_contains_credential(child):
                return True
        return False
    if isinstance(value, list):
        return any(_json_contains_credential(item) for item in value)
    return isinstance(value, str) and _known_credential_text(value)


def _text_has_credential(raw: bytes, identifier: str, media_type: str) -> bool:
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
            parsed = json.loads(text)
        except (json.JSONDecodeError, RecursionError) as error:
            raise EvidenceError(
                f"evidence {identifier!r}: actual media type does not match application/json"
            ) from error
        return _json_contains_credential(parsed) or _known_credential_text(text)
    return _known_credential_text(text)


def _verify_media(raw: bytes, identifier: str, media_type: str) -> bool:
    if media_type == "image/png":
        width, height = _png_dimensions(raw, identifier)
    elif media_type == "image/jpeg":
        width, height = _jpeg_dimensions(raw, identifier)
    elif media_type in ("text/plain", "application/json"):
        return _text_has_credential(raw, identifier, media_type)
    else:
        _error(identifier, "media type is not accepted")
    if width * height > MAX_IMAGE_PIXELS:
        _error(identifier, "image exceeds the 20 megapixels limit")
    return False


def inspect_evidence(root: Path, manifest: dict) -> list[dict]:
    """Return a safe public projection after revalidating every evidence file.

    Unsafe paths, formats, and limits raise :class:`EvidenceError`, which tells the
    caller not to export. Missing, changed, target-incompatible, credential-bearing,
    or pending-review attachments return sanitized ``BLOCKED`` diagnostics and are
    never marked copyable.
    """

    project_root = Path(root)
    if not _SUPPORTS_SECURE_TRAVERSAL:
        raise EvidenceError("secure descriptor-relative evidence traversal is unavailable")
    try:
        root_metadata = project_root.lstat()
    except OSError as error:
        raise EvidenceError("project root cannot be inspected") from error
    if stat.S_ISLNK(root_metadata.st_mode) or not stat.S_ISDIR(root_metadata.st_mode):
        raise EvidenceError("project root must be a regular local directory, not a symlink")

    root_flags = os.O_RDONLY | getattr(os, "O_DIRECTORY", 0) | getattr(os, "O_NOFOLLOW", 0)
    try:
        root_descriptor = os.open(str(project_root), root_flags)
    except OSError as error:
        raise EvidenceError("project root cannot be opened safely") from error
    opened_root = os.fstat(root_descriptor)
    if opened_root.st_dev != root_metadata.st_dev or opened_root.st_ino != root_metadata.st_ino:
        os.close(root_descriptor)
        raise EvidenceError("project root changed during safe inspection")

    records: List[Dict[str, Any]] = []
    actual_total = 0
    try:
        for item in manifest["evidence"]:
            identifier = item["id"]
            parts = _safe_parts(identifier, item["path"])
            _reject_sensitive_path(identifier, parts)
            descriptor, metadata = _open_evidence(root_descriptor, parts, identifier)
            if descriptor is None or metadata is None:
                records.append(_blocked(item, manifest, "evidence file is missing"))
                continue

            if metadata.st_size > MAX_EVIDENCE_BYTES:
                os.close(descriptor)
                _error(identifier, "actual evidence exceeds the 10 MiB limit")

            raw = _read_regular(descriptor, metadata, identifier)
            actual_size = len(raw)
            actual_total += actual_size
            if actual_total > MAX_TOTAL_EVIDENCE_BYTES:
                _error(identifier, "actual evidence exceeds the 100 MiB aggregate limit")
            contains_credential = _verify_media(raw, identifier, item["media_type"])
            actual_hash = hashlib.sha256(raw).hexdigest()

            if item["target_id"] != manifest["target"]["id"]:
                records.append(_blocked(item, manifest, "evidence target is incompatible"))
            elif actual_size != item["size_bytes"]:
                records.append(_blocked(item, manifest, "evidence size changed"))
            elif actual_hash != item["sha256"]:
                records.append(_blocked(item, manifest, "evidence digest changed"))
            elif contains_credential:
                records.append(
                    _blocked(item, manifest, "credential-like data detected; attachment withheld")
                )
            elif item["sanitization"]["status"] == "pending":
                records.append(_blocked(item, manifest, "sanitization review is pending"))
            elif item["media_type"].startswith("image/") and item["sanitization"]["status"] != "reviewed":
                records.append(
                    _blocked(item, manifest, "recorded visual sanitization review is required")
                )
            else:
                records.append(_verified(item, manifest, actual_size))
    finally:
        os.close(root_descriptor)
    return records
