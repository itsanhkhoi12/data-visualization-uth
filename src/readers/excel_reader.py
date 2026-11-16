from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import openpyxl
from openpyxl.utils.datetime import from_excel


@dataclass(frozen=True)
class SheetInspection:
    path: Path
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
    warnings: tuple[str, ...]

    def to_dict(self) -> dict[str, object]:
        return {
            "path": str(self.path),
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
            "warnings": list(self.warnings),
        }


def detect_epoch(workbook: openpyxl.Workbook) -> str:
    return "1904" if getattr(workbook, "epoch", None) and workbook.epoch.year == 1904 else "1900"


def _header_confidence(header: tuple[str, ...]) -> float:
    if not header:
        return 0.0
    filled = sum(1 for cell in header if cell and cell.strip())
    distinct = len({cell.strip().lower() for cell in header if cell and cell.strip()})
    score = 0.6 * (filled / len(header)) + 0.4 * (distinct / max(filled, 1))
    return round(score, 4)


def inspect_workbook(path: Path) -> list[SheetInspection]:
    workbook = openpyxl.load_workbook(path, read_only=False, data_only=False)
    epoch = detect_epoch(workbook)
    results: list[SheetInspection] = []
    try:
        for worksheet in workbook.worksheets:
            merged_count = len(worksheet.merged_cells.ranges)
            header: tuple[str, ...] = ()
            data_rows = 0
            formula_cells = 0
            cached_missing = 0
            repeated = False
            row_index = 0
            for row in worksheet.iter_rows(values_only=False):
                row_index += 1
                if row_index == 1:
                    header = tuple(
                        "" if cell.value is None else str(cell.value).strip() for cell in row
                    )
                    continue
                values = [cell.value for cell in row]
                if all(value is None or str(value).strip() == "" for value in values):
                    continue
                data_rows += 1
                normalized = tuple("" if value is None else str(value).strip() for value in values)
                if header and normalized == header[: len(normalized)]:
                    repeated = True
                for cell in row:
                    if isinstance(cell.value, str) and cell.value.startswith("="):
                        formula_cells += 1
            warnings: list[str] = []
            if merged_count:
                warnings.append("merged_ranges_present")
            if formula_cells:
                warnings.append("formula_cells_present")
            if repeated:
                warnings.append("repeated_header_rows_present")
            results.append(
                SheetInspection(
                    path=path,
                    sheet_name=worksheet.title,
                    sheet_state=worksheet.sheet_state,
                    max_row=worksheet.max_row or 0,
                    max_column=worksheet.max_column or 0,
                    header=header,
                    data_row_count=data_rows,
                    merged_range_count=merged_count,
                    formula_cell_count=formula_cells,
                    cached_value_missing_count=cached_missing,
                    header_confidence=_header_confidence(header),
                    has_repeated_header=repeated,
                    epoch=epoch,
                    warnings=tuple(warnings),
                )
            )
    finally:
        workbook.close()
    return results


def inspect_workbook_fast(path: Path) -> list[SheetInspection]:
    from readers.xlsx_fast import inspect_workbook_fast as fast_inspect

    results: list[SheetInspection] = []
    for info in fast_inspect(path):
        header = info.header
        warnings: list[str] = []
        if info.merged_range_count:
            warnings.append("merged_ranges_present")
        if info.formula_cell_count:
            warnings.append("formula_cells_present")
        results.append(
            SheetInspection(
                path=path,
                sheet_name=info.sheet_name,
                sheet_state=info.sheet_state,
                max_row=info.row_count,
                max_column=info.max_column or len(header),
                header=header,
                data_row_count=max(info.row_count - 1, 0),
                merged_range_count=info.merged_range_count,
                formula_cell_count=info.formula_cell_count,
                cached_value_missing_count=0,
                header_confidence=_header_confidence(header),
                has_repeated_header=False,
                epoch=info.epoch,
                warnings=tuple(warnings),
            )
        )
    return results


def list_sheets(path: Path) -> list[tuple[str, str]]:
    workbook = openpyxl.load_workbook(path, read_only=True, data_only=True)
    try:
        return [(worksheet.title, worksheet.sheet_state) for worksheet in workbook.worksheets]
    finally:
        workbook.close()


def read_sheet_values(
    path: Path, sheet_name: str, max_rows: int | None = None
) -> list[tuple[object, ...]]:
    workbook = openpyxl.load_workbook(path, read_only=True, data_only=True)
    try:
        worksheet = workbook[sheet_name]
        values: list[tuple[object, ...]] = []
        for index, row in enumerate(worksheet.iter_rows(values_only=True)):
            if max_rows is not None and index >= max_rows:
                break
            values.append(tuple(row))
        return values
    finally:
        workbook.close()


def read_sheet_rows(
    path: Path, sheet_name: str, max_rows: int | None = None
) -> tuple[tuple[str, ...], list[dict[str, object]]]:
    from readers.xlsx_fast import read_sheet_rows_fast

    header, rows, _count = read_sheet_rows_fast(path, sheet_name, max_rows=max_rows)
    return header, list(rows)


def excel_serial_to_datetime(serial: int, epoch: str = "1900") -> object:
    return from_excel(serial, epoch=epoch)
