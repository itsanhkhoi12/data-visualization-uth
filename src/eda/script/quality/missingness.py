from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Sequence

from readers.table_reader import LoadedTable
from schema.type_inference import is_blank, parse_date, parse_number


@dataclass(frozen=True)
class MissingnessEntry:
    source_id: str
    split: str
    business_id: str
    object_name: str
    column: str
    n_total: int
    n_missing: int
    missing_ratio: float
    null_kind: str
    co_missing_with: tuple[str, ...]

    def to_dict(self) -> dict[str, Any]:
        return {
            "source_id": self.source_id,
            "split": self.split,
            "business_id": self.business_id,
            "object_name": self.object_name,
            "column": self.column,
            "n_total": self.n_total,
            "n_missing": self.n_missing,
            "missing_ratio": self.missing_ratio,
            "null_kind": self.null_kind,
            "co_missing_with": list(self.co_missing_with),
        }


STRUCTURAL_HINTS = ("mã khách", "ma khach", "khách lẻ", "khach le", "mã kh", "note", "ghi chú")


def classify_null_kind(column: str, semantic_type: str) -> str:
    lowered = column.lower()
    for token in STRUCTURAL_HINTS:
        if token in lowered:
            return "structural_missing"
    if semantic_type in {"identifier", "measure", "amount", "quantity"}:
        return "unknown"
    return "blank_or_not_applicable"


def profile_missingness(
    table: LoadedTable, semantic_by_column: dict[str, str] | None = None
) -> tuple[MissingnessEntry, ...]:
    semantic_by_column = semantic_by_column or {}
    columns = [name for name in table.header if name]
    total = len(table.rows)
    if total == 0:
        return ()
    missing_matrix: dict[str, set[int]] = {column: set() for column in columns}
    for index, row in enumerate(table.rows):
        for column in columns:
            if is_blank(row.get(column)):
                missing_matrix[column].add(index)
    entries: list[MissingnessEntry] = []
    for column in columns:
        missing_indexes = missing_matrix[column]
        count = len(missing_indexes)
        if count == 0:
            continue
        co_missing: list[str] = []
        for other in columns:
            if other == column:
                continue
            other_indexes = missing_matrix[other]
            if not other_indexes:
                continue
            overlap = len(missing_indexes & other_indexes)
            if overlap / count >= 0.8:
                co_missing.append(other)
        entries.append(
            MissingnessEntry(
                source_id=table.source_id,
                split=table.split,
                business_id=table.business_id,
                object_name=table.object_name,
                column=column,
                n_total=total,
                n_missing=count,
                missing_ratio=round(count / total, 6),
                null_kind=classify_null_kind(column, semantic_by_column.get(column, "")),
                co_missing_with=tuple(co_missing[:8]),
            )
        )
    return tuple(entries)


def parse_failure_rate(
    table: LoadedTable, column: str, semantic_type: str
) -> tuple[int, int]:
    total = 0
    failures = 0
    for row in table.rows:
        value = row.get(column)
        if is_blank(value):
            continue
        total += 1
        if semantic_type in {"measure", "amount", "quantity"}:
            if parse_number(value) is None:
                failures += 1
        elif semantic_type == "date":
            if parse_date(value) is None:
                failures += 1
    return failures, total
