from __future__ import annotations

import struct
import zipfile
from dataclasses import dataclass
from pathlib import Path

from common.errors import CorruptArchiveError

EOCD_SIGNATURE = b"PK\x05\x06"
CENTRAL_DIRECTORY_SIGNATURE = b"PK\x01\x02"
EOCD_FIXED_SIZE = 22
CENTRAL_DIRECTORY_HEADER_SIZE = 46
MAX_COMMENT_SIZE = 65535


@dataclass(frozen=True)
class ZipMember:
    member_name: str
    normalized_name: str
    compress_size: int
    file_size: int
    crc: str
    is_directory: bool
    compressed_ratio: float

    def to_dict(self) -> dict[str, object]:
        return {
            "member_name": self.member_name,
            "normalized_name": self.normalized_name,
            "compress_size": self.compress_size,
            "file_size": self.file_size,
            "crc": self.crc,
            "is_directory": self.is_directory,
            "compressed_ratio": self.compressed_ratio,
        }


@dataclass(frozen=True)
class ArchiveVerification:
    archive_path: Path
    member_count: int
    file_member_count: int
    duplicate_normalized_names: tuple[str, ...]
    unsafe_members: tuple[str, ...]
    total_uncompressed_bytes: int
    total_compressed_bytes: int
    integrity_error: str | None
    status: str

    def to_dict(self) -> dict[str, object]:
        return {
            "archive_path": str(self.archive_path),
            "member_count": self.member_count,
            "file_member_count": self.file_member_count,
            "duplicate_normalized_names": list(self.duplicate_normalized_names),
            "unsafe_members": list(self.unsafe_members),
            "total_uncompressed_bytes": self.total_uncompressed_bytes,
            "total_compressed_bytes": self.total_compressed_bytes,
            "integrity_error": self.integrity_error,
            "status": self.status,
        }


def normalize_member_name(name: str) -> str:
    normalized = name.replace("\\", "/")
    while normalized.startswith("./"):
        normalized = normalized[2:]
    return normalized


def is_unsafe_member(name: str) -> bool:
    raw = name.replace("\\", "/")
    if raw.startswith("/"):
        return True
    normalized = normalize_member_name(name)
    if not normalized:
        return True
    if normalized.startswith("/") or ":" in normalized.split("/")[0]:
        return True
    parts = normalized.split("/")
    if ".." in parts:
        return True
    return False


def _locate_end_of_central_directory(payload: bytes) -> int:
    search_start = max(0, len(payload) - EOCD_FIXED_SIZE - MAX_COMMENT_SIZE)
    position = payload.rfind(EOCD_SIGNATURE, search_start)
    if position < 0:
        raise CorruptArchiveError("end_of_central_directory_not_found")
    return position


def assert_central_directory_intact(archive_path: Path) -> None:
    payload = archive_path.read_bytes()
    if len(payload) < EOCD_FIXED_SIZE:
        raise CorruptArchiveError("archive_truncated")
    eocd_offset = _locate_end_of_central_directory(payload)
    (
        entry_count,
        directory_size,
        directory_offset,
    ) = struct.unpack("<HII", payload[eocd_offset + 10 : eocd_offset + 20])
    if directory_size == 0 and entry_count == 0:
        return
    if directory_offset + directory_size > len(payload):
        raise CorruptArchiveError(
            "central_directory_out_of_bounds:"
            f"offset={directory_offset},size={directory_size},length={len(payload)}"
        )
    if payload[directory_offset : directory_offset + 4] != CENTRAL_DIRECTORY_SIGNATURE:
        raise CorruptArchiveError(
            f"central_directory_signature_missing_at:{directory_offset}"
        )
    position = directory_offset
    for _ in range(entry_count):
        if payload[position : position + 4] != CENTRAL_DIRECTORY_SIGNATURE:
            raise CorruptArchiveError(
                f"central_directory_entry_signature_missing_at:{position}"
            )
        (
            file_name_length,
            extra_field_length,
            comment_length,
        ) = struct.unpack("<HHH", payload[position + 28 : position + 34])
        position += (
            CENTRAL_DIRECTORY_HEADER_SIZE + file_name_length + extra_field_length + comment_length
        )
        if position > len(payload):
            raise CorruptArchiveError("central_directory_entry_truncated")
    if position != directory_offset + directory_size:
        raise CorruptArchiveError(
            "central_directory_size_mismatch:"
            f"expected={directory_offset + directory_size},actual={position}"
        )


def list_zip_members(archive_path: Path) -> list[ZipMember]:
    members: list[ZipMember] = []
    with zipfile.ZipFile(archive_path) as archive:
        for info in archive.infolist():
            ratio = (
                info.compress_size / info.file_size if info.file_size else 0.0
            )
            members.append(
                ZipMember(
                    member_name=info.filename,
                    normalized_name=normalize_member_name(info.filename),
                    compress_size=info.compress_size,
                    file_size=info.file_size,
                    crc=f"{info.CRC:08x}",
                    is_directory=info.is_dir(),
                    compressed_ratio=round(ratio, 6),
                )
            )
    return members


def verify_archive(archive_path: Path) -> ArchiveVerification:
    assert_central_directory_intact(archive_path)
    with zipfile.ZipFile(archive_path) as archive:
        members = archive.infolist()
        names = [normalize_member_name(info.filename) for info in members]
        seen: dict[str, int] = {}
        for name in names:
            seen[name] = seen.get(name, 0) + 1
        duplicates = tuple(sorted(name for name, count in seen.items() if count > 1))
        unsafe = tuple(
            sorted({info.filename for info in members if is_unsafe_member(info.filename)})
        )
        file_members = [info for info in members if not info.is_dir()]
        total_uncompressed = sum(info.file_size for info in file_members)
        total_compressed = sum(info.compress_size for info in file_members)
        integrity_error: str | None = None
        try:
            bad = archive.testzip()
            if bad is not None:
                integrity_error = f"crc_failure:{bad}"
        except (zipfile.BadZipFile, OSError) as error:
            integrity_error = f"{type(error).__name__}:{error}"
        status = "PASS"
        if integrity_error or unsafe or duplicates:
            status = "FAIL"
        return ArchiveVerification(
            archive_path=archive_path,
            member_count=len(members),
            file_member_count=len(file_members),
            duplicate_normalized_names=duplicates,
            unsafe_members=unsafe,
            total_uncompressed_bytes=total_uncompressed,
            total_compressed_bytes=total_compressed,
            integrity_error=integrity_error,
            status=status,
        )
