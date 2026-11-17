from __future__ import annotations

import unicodedata
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Sequence

from common.enums import Status
from readers.markdown_reader import MarkdownDocument, parse_markdown


@dataclass(frozen=True)
class BusinessSourceEntry:
    logical_path: str
    source_type: str
    size_bytes: int
    content_hash: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "logical_path": self.logical_path,
            "source_type": self.source_type,
            "size_bytes": self.size_bytes,
            "content_hash": self.content_hash,
        }


@dataclass(frozen=True)
class BusinessProfile:
    business_id: str
    split: str
    source_count: int
    sources: tuple[BusinessSourceEntry, ...]
    readme_present: bool
    readme_title: str
    readme_line_count: int
    readme_hash: str
    documented_files: tuple[str, ...]
    documented_conventions: tuple[str, ...]
    domain_evidence: str | None
    status: Status
    notes: tuple[str, ...] = ()

    def to_dict(self) -> dict[str, Any]:
        return {
            "business_id": self.business_id,
            "split": self.split,
            "source_count": self.source_count,
            "sources": [source.to_dict() for source in self.sources],
            "readme_present": self.readme_present,
            "readme_title": self.readme_title,
            "readme_line_count": self.readme_line_count,
            "readme_hash": self.readme_hash,
            "documented_files": list(self.documented_files),
            "documented_conventions": list(self.documented_conventions),
            "domain_evidence": self.domain_evidence,
            "status": self.status.value,
            "notes": list(self.notes),
        }


def _extract_documented_files(document: MarkdownDocument) -> tuple[str, ...]:
    files: list[str] = []
    for block in document.blocks:
        for line in block.body:
            stripped = line.strip()
            if stripped.startswith("- `") and stripped.endswith("`"):
                inner = stripped[3:-1]
                if "(" in inner:
                    inner = inner.split("(")[0].strip()
                if inner:
                    files.append(inner)
    return tuple(dict.fromkeys(files))


def _extract_conventions(document: MarkdownDocument) -> tuple[str, ...]:
    conventions: list[str] = []
    for block in document.blocks:
        for line in block.body:
            stripped = line.strip()
            if stripped.startswith("- ") and "**" in stripped:
                conventions.append(stripped[2:].strip())
    return tuple(conventions)


def _strip_marks(text: str) -> str:
    text = text.replace("đ", "d").replace("Đ", "D")
    decomposed = unicodedata.normalize("NFD", text)
    return "".join(ch for ch in decomposed if not unicodedata.combining(ch))


def _normalize(text: str) -> str:
    lowered = _strip_marks(text.lower())
    return " ".join(lowered.split())


DOMAIN_VOCABULARY: tuple[tuple[str, tuple[str, ...], int], ...] = (
    (
        "pharmacy",
        ("thuoc", "han su dung", "lo ", "hoat chat", "ke don"),
        2,
    ),
    (
        "cafe_restaurant",
        ("mon ", "topping", "ca sang", "ca chieu", "quay"),
        2,
    ),
    ("materials", ("thung", "tan ", "xi mang", "vat lieu"), 2),
    (
        "phone_retail",
        ("may cu", "thu may cu", "tra gop", "bao hanh", "imei"),
        2,
    ),
    ("motor_repair", ("bien so", "sua xe", "luot xe", "tho"), 2),
    ("mother_baby", ("bim", "sua ", "size", "voucher", "thanh vien"), 2),
    (
        "retail_grocery",
        (
            "grocery",
            "quy doi don vi",
            "don vi quy doi",
            "gia von",
            "ton cuoi ky",
        ),
        2,
    ),
    (
        "retail_pos",
        (
            "ban hang",
            "hoa don",
            "mat hang",
            "hang hoa",
            "ton kho",
            "gia ban",
            "gia von",
            "cong no",
            "khach hang",
            "so luong",
            "don vi",
            "don hang",
        ),
        3,
    ),
)


def detect_domain_evidence(document: MarkdownDocument) -> str | None:
    text = "\n".join(
        [block.heading_text for block in document.blocks]
        + [line for block in document.blocks for line in block.body]
    )
    normalized = _normalize(text)
    for domain, tokens, threshold in DOMAIN_VOCABULARY:
        hits = sum(1 for token in tokens if token in normalized)
        if hits >= threshold:
            return domain
    return None


def build_business_profile(
    business_id: str,
    split: str,
    sources: Sequence[BusinessSourceEntry],
    readme_path: Path | None,
    readme_hash: str,
) -> BusinessProfile:
    notes: list[str] = []
    documented_files: tuple[str, ...] = ()
    documented_conventions: tuple[str, ...] = ()
    readme_title = ""
    readme_lines = 0
    domain_evidence: str | None = None
    readme_present = readme_path is not None and readme_path.exists()
    if readme_present and readme_path is not None:
        document = parse_markdown(readme_path)
        readme_title = document.title
        readme_lines = document.line_count
        documented_files = _extract_documented_files(document)
        documented_conventions = _extract_conventions(document)
        domain_evidence = detect_domain_evidence(document)
    else:
        notes.append("readme_missing_domain_cannot_be_inferred_from_filename")
    status = Status.PASS if readme_present else Status.PARTIAL
    if not sources:
        if readme_present:
            status = Status.BLOCKED
            notes.append("no_business_data_sources")
        else:
            notes.append("no_business_data_sources_documented_scope_unknown")
    return BusinessProfile(
        business_id=business_id,
        split=split,
        source_count=len(sources),
        sources=tuple(sources),
        readme_present=readme_present,
        readme_title=readme_title,
        readme_line_count=readme_lines,
        readme_hash=readme_hash,
        documented_files=documented_files,
        documented_conventions=documented_conventions,
        domain_evidence=domain_evidence,
        status=status,
        notes=tuple(notes),
    )
