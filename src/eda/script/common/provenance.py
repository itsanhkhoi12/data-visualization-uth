from __future__ import annotations

import hashlib
from pathlib import Path

from common.contracts import EvidenceRef
from common.enums import EvidenceStatus

CHUNK_SIZE = 1 << 20


def fingerprint_bytes(payload: bytes) -> str:
    digest = hashlib.sha256()
    digest.update(payload)
    return f"sha256:{digest.hexdigest()}"


def fingerprint_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        while True:
            chunk = handle.read(CHUNK_SIZE)
            if not chunk:
                break
            digest.update(chunk)
    return f"sha256:{digest.hexdigest()}"


def fingerprint_text(text: str) -> str:
    return fingerprint_bytes(text.encode("utf-8"))


def fingerprint_mapping(payload: dict[str, object]) -> str:
    import json

    canonical = json.dumps(payload, sort_keys=True, ensure_ascii=False, default=str)
    return fingerprint_text(canonical)


def create_evidence(
    evidence_id: str,
    split: str,
    business_id: str,
    source_id: str,
    source_hash: str,
    method: str,
    method_version: str,
    locator: str,
    detail: str,
    status: EvidenceStatus = EvidenceStatus.DATA_VERIFIED,
) -> EvidenceRef:
    return EvidenceRef(
        evidence_id=evidence_id,
        split=split,
        business_id=business_id,
        source_id=source_id,
        source_hash=source_hash,
        method=method,
        method_version=method_version,
        locator=locator,
        detail=detail,
        status=status,
    )
