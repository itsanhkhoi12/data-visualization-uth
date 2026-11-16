from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from common.contracts import SourceRecord
from common.enums import Status
from readers.excel_reader import inspect_workbook_fast


@dataclass(frozen=True)
class SheetRegistryEntry:
    source_id: str
    split: str
    business_id: str
    workbook_path: str
    workbook_hash: str
    sheet_name: str
    sheet_state: str
    max_row: int
    max_column: int
    header: tuple[str, ...]
    data_row_count: int
    merged_range_count: int
    formula_cell_count: int
    cached_value_missing_count: int
    header_confidence: float
    has_repeated_header: bool
    epoch: str
    status: Status
    warnings: tuple[str, ...]

    def to_dict(self) -> dict[str, object]:
        return {
            "source_id": self.source_id,
            "split": self.split,
            "business_id": self.business_id,
            "workbook_path": self.workbook_path,
            "workbook_hash": self.workbook_hash,
            "sheet_name": self.sheet_name,
            "sheet_state": self.sheet_state,
            "max_row": self.max_row,
            "max_column": self.max_column,
            "header": list(self.header),
            "data_row_count": self.data_row_count,
            "merged_range_count": self.merged_range_count,
            "formula_cell_count": self.formula_cell_count,
            "cached_value_missing_count": self.cached_value_missing_count,
            "header_confidence": self.header_confidence,
            "has_repeated_header": self.has_repeated_header,
            "epoch": self.epoch,
            "status": self.status.value,
            "warnings": list(self.warnings),
        }


@dataclass(frozen=True)
class SheetRegistry:
    split: str
    entries: tuple[SheetRegistryEntry, ...]
    workbook_count: int
    error_paths: tuple[str, ...]

    def to_dict(self) -> dict[str, object]:
        return {
            "split": self.split,
            "entries": [entry.to_dict() for entry in self.entries],
            "workbook_count": self.workbook_count,
            "error_paths": list(self.error_paths),
        }


def build_sheet_registry(records: tuple[SourceRecord, ...], split: str) -> SheetRegistry:
    entries: list[SheetRegistryEntry] = []
    errors: list[str] = []
    workbook_count = 0
    for record in records:
        if record.source_type != "xlsx":
            continue
        workbook_count += 1
        path = Path(record.absolute_path)
        try:
            inspections = inspect_workbook_fast(path)
        except (OSError, ValueError) as error:
            errors.append(f"{record.logical_path}:{type(error).__name__}")
            continue
        for inspection in inspections:
            entries.append(
                SheetRegistryEntry(
                    source_id=f"{record.source_id}#sheet={inspection.sheet_name}",
                    split=split,
                    business_id=record.business_id,
                    workbook_path=record.logical_path,
                    workbook_hash=record.content_hash,
                    sheet_name=inspection.sheet_name,
                    sheet_state=inspection.sheet_state,
                    max_row=inspection.max_row,
                    max_column=inspection.max_column,
                    header=inspection.header,
                    data_row_count=inspection.data_row_count,
                    merged_range_count=inspection.merged_range_count,
                    formula_cell_count=inspection.formula_cell_count,
                    cached_value_missing_count=inspection.cached_value_missing_count,
                    header_confidence=inspection.header_confidence,
                    has_repeated_header=inspection.has_repeated_header,
                    epoch=inspection.epoch,
                    status=Status.PASS,
                    warnings=inspection.warnings,
                )
            )
    return SheetRegistry(
        split=split,
        entries=tuple(entries),
        workbook_count=workbook_count,
        error_paths=tuple(errors),
    )
