from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping, Sequence

from common.contracts import ColumnProfile
from common.enums import Status
from readers.table_reader import LoadedTable
from schema.type_inference import (
    infer_physical_type,
    infer_semantic_type,
    is_blank,
    parse_date,
    parse_number,
)


@dataclass(frozen=True)
class ColumnRegistryEntry:
    source_id: str
    split: str
    business_id: str
    object_name: str
    column: str
    position: int
    physical_type: str
    semantic_type: str
    unit: str | None
    non_null_n: int
    null_n: int
    distinct_n: int
    parse_failure_n: int
    confidence: float
    sample_values: tuple[str, ...]
    status: Status

    def to_dict(self) -> dict[str, Any]:
        return {
            "source_id": self.source_id,
            "split": self.split,
            "business_id": self.business_id,
            "object_name": self.object_name,
            "column": self.column,
            "position": self.position,
            "physical_type": self.physical_type,
            "semantic_type": self.semantic_type,
            "unit": self.unit,
            "non_null_n": self.non_null_n,
            "null_n": self.null_n,
            "distinct_n": self.distinct_n,
            "parse_failure_n": self.parse_failure_n,
            "confidence": self.confidence,
            "sample_values": list(self.sample_values),
            "status": self.status.value,
        }


UNIT_HINTS = {
    "tiền": "VND",
    "tien": "VND",
    "giá": "VND",
    "gia": "VND",
    "doanh thu": "VND",
    "tong tien": "VND",
    "thanh tien": "VND",
    "con no": "VND",
    "còn nợ": "VND",
    "số lượng": "count",
    "so luong": "count",
    "sl": "count",
    "hạn sử dụng": "date",
    "han su dung": "date",
}


def detect_unit(column: str) -> str | None:
    lowered = column.lower()
    for token, unit in UNIT_HINTS.items():
        if token in lowered:
            return unit
    return None


def _distinct_count(values: Sequence[Any]) -> int:
    seen: set[str] = set()
    for value in values:
        if is_blank(value):
            continue
        seen.add(str(value).strip())
    return len(seen)


def build_column_registry(
    table: LoadedTable, sample_limit: int = 5000
) -> tuple[ColumnRegistryEntry, ...]:
    entries: list[ColumnRegistryEntry] = []
    columns = [name for name in table.header if name]
    sample_rows = table.rows[:sample_limit]
    for position, column in enumerate(columns):
        values = [row.get(column) for row in sample_rows]
        physical = infer_physical_type(values)
        candidate = infer_semantic_type(column, values, physical)
        text_values: list[str | None] = []
        for value in values:
            if value is None:
                text_values.append(None)
                continue
            if isinstance(value, str):
                stripped = value.strip()
                text_values.append(stripped if stripped else None)
                continue
            text_values.append(str(value).strip())
        null_n = sum(1 for value in text_values if value is None)
        non_null_n = len(text_values) - null_n
        parse_failures = 0
        if candidate.semantic_type.value in {"measure", "amount", "quantity"}:
            parse_failures = sum(
                1
                for value in values
                if not is_blank(value) and parse_number(value) is None
            )
        elif candidate.semantic_type.value == "date":
            parse_failures = sum(
                1
                for value in values
                if not is_blank(value) and parse_date(value) is None
            )
        samples: list[str] = []
        for value in text_values:
            if value is None:
                continue
            if value not in samples:
                samples.append(value)
            if len(samples) >= 5:
                break
        entries.append(
            ColumnRegistryEntry(
                source_id=table.source_id,
                split=table.split,
                business_id=table.business_id,
                object_name=table.object_name,
                column=column,
                position=position,
                physical_type=candidate.physical_type.value,
                semantic_type=candidate.semantic_type.value,
                unit=detect_unit(column),
                non_null_n=non_null_n,
                null_n=null_n,
                distinct_n=_distinct_count(values),
                parse_failure_n=parse_failures,
                confidence=candidate.confidence,
                sample_values=tuple(samples),
                status=Status.PASS,
            )
        )
    return tuple(entries)


def column_profiles(entries: Sequence[ColumnRegistryEntry]) -> tuple[ColumnProfile, ...]:
    return tuple(
        ColumnProfile(
            source_id=entry.source_id,
            split=entry.split,
            business_id=entry.business_id,
            column=entry.column,
            physical_type=entry.physical_type,
            semantic_type=entry.semantic_type,
            unit=entry.unit,
            non_null_n=entry.non_null_n,
            null_n=entry.null_n,
            distinct_n=entry.distinct_n,
            parse_failure_n=entry.parse_failure_n,
            confidence=entry.confidence,
            sample_values=entry.sample_values,
            status=entry.status,
        )
        for entry in entries
    )


def columns_by_semantic(
    entries: Sequence[ColumnRegistryEntry], semantic_type: str
) -> tuple[ColumnRegistryEntry, ...]:
    return tuple(
        entry for entry in entries if entry.semantic_type == semantic_type
    )


def columns_by_role(
    entries: Sequence[ColumnRegistryEntry], roles: Mapping[str, str]
) -> dict[str, ColumnRegistryEntry]:
    result: dict[str, ColumnRegistryEntry] = {}
    lowered = {entry.column.lower(): entry for entry in entries}
    for role, needle in roles.items():
        for column_lower, entry in lowered.items():
            if needle.lower() in column_lower:
                result[role] = entry
                break
    return result
