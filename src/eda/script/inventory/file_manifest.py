from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from common.contracts import SourceRecord
from common.enums import SourceType, Status
from common.paths import DatasetContext
from common.provenance import fingerprint_file

IGNORED_NAMES = {".DS_Store", "Thumbs.db"}
IGNORED_SUFFIXES = {".pyc"}
DOCUMENT_NAMES = {"README.md", "rulebook.md"}
DOCUMENT_SUFFIXES = {".md", ".jsonl", ".csv"}
BUSINESS_SUFFIXES = {".xlsx", ".csv", ".sqlite"}


@dataclass(frozen=True)
class FileManifest:
    split: str
    records: tuple[SourceRecord, ...]
    business_ids: tuple[str, ...]
    ignored_paths: tuple[str, ...]
    counts_by_type: dict[str, int]

    def to_dict(self) -> dict[str, object]:
        return {
            "split": self.split,
            "records": [record.to_dict() for record in self.records],
            "business_ids": list(self.business_ids),
            "ignored_paths": list(self.ignored_paths),
            "counts_by_type": dict(self.counts_by_type),
        }


def classify_source_type(path: Path) -> SourceType:
    suffix = path.suffix.lower()
    if suffix == ".csv":
        return SourceType.CSV
    if suffix == ".xlsx":
        return SourceType.XLSX
    if suffix in {".sqlite", ".db", ".sqlite3"}:
        return SourceType.SQLITE
    if suffix == ".jsonl":
        return SourceType.JSONL
    if suffix == ".md":
        return SourceType.MARKDOWN
    return SourceType.UNKNOWN


def is_ignored(path: Path) -> bool:
    if path.name in IGNORED_NAMES:
        return True
    if path.suffix.lower() in IGNORED_SUFFIXES:
        return True
    if path.name.startswith("."):
        return True
    return False


def build_file_manifest(
    context: DatasetContext, business_filter: tuple[str, ...] = ()
) -> FileManifest:
    records: list[SourceRecord] = []
    ignored: list[str] = []
    business_ids = [
        business_id
        for business_id in context.business_ids()
        if not business_filter or business_id in business_filter
    ]
    for business_id in business_ids:
        business_path = context.business_root_path(business_id)
        for path in sorted(business_path.rglob("*")):
            if not path.is_file():
                continue
            relative = path.relative_to(context.root).as_posix()
            if is_ignored(path):
                ignored.append(relative)
                continue
            source_type = classify_source_type(path)
            is_business_data = path.suffix.lower() in BUSINESS_SUFFIXES
            records.append(
                SourceRecord(
                    source_id=f"{context.split}:{business_id}:{relative}",
                    split=context.split,
                    business_id=business_id,
                    source_type=source_type.value,
                    logical_path=relative,
                    absolute_path=str(path.resolve()),
                    size_bytes=path.stat().st_size,
                    content_hash=fingerprint_file(path),
                    status=Status.PASS,
                    sheet_name=None,
                    table_name=None,
                    row_count=None,
                    column_count=None,
                    warnings=(),
                )
            )
            del is_business_data
    for path in sorted(context.root.glob("*")):
        if not path.is_file() or is_ignored(path):
            if path.is_file():
                ignored.append(path.relative_to(context.root).as_posix())
            continue
        relative = path.relative_to(context.root).as_posix()
        source_type = classify_source_type(path)
        records.append(
            SourceRecord(
                source_id=f"{context.split}:{relative}",
                split=context.split,
                business_id="__split__",
                source_type=source_type.value,
                logical_path=relative,
                absolute_path=str(path.resolve()),
                size_bytes=path.stat().st_size,
                content_hash=fingerprint_file(path),
                status=Status.PASS,
                sheet_name=None,
                table_name=None,
                row_count=None,
                column_count=None,
                warnings=(),
            )
        )
    counts: dict[str, int] = {}
    for record in records:
        counts[record.source_type] = counts.get(record.source_type, 0) + 1
    return FileManifest(
        split=context.split,
        records=tuple(records),
        business_ids=tuple(business_ids),
        ignored_paths=tuple(ignored),
        counts_by_type=counts,
    )


def dataset_document_sources(manifest: FileManifest) -> tuple[SourceRecord, ...]:
    return tuple(
        record
        for record in manifest.records
        if record.business_id == "__split__"
        or record.logical_path.endswith("README.md")
    )
