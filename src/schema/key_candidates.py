from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Sequence

from readers.table_reader import LoadedTable
from schema.type_inference import is_blank


@dataclass(frozen=True)
class KeyCandidate:
    source_id: str
    split: str
    business_id: str
    object_name: str
    key_columns: tuple[str, ...]
    total_n: int
    non_null_n: int
    distinct_n: int
    duplicate_value_n: int
    null_count: int
    is_unique: bool
    is_not_null: bool
    confidence: float
    status: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "source_id": self.source_id,
            "split": self.split,
            "business_id": self.business_id,
            "object_name": self.object_name,
            "key_columns": list(self.key_columns),
            "total_n": self.total_n,
            "non_null_n": self.non_null_n,
            "distinct_n": self.distinct_n,
            "duplicate_value_n": self.duplicate_value_n,
            "null_count": self.null_count,
            "is_unique": self.is_unique,
            "is_not_null": self.is_not_null,
            "confidence": self.confidence,
            "status": self.status,
        }


def _key_values(row: dict[str, Any], columns: Sequence[str]) -> tuple[str, ...]:
    values: list[str] = []
    for column in columns:
        value = row.get(column)
        if is_blank(value):
            return ()
        values.append(str(value).strip())
    return tuple(values)


def find_candidate_keys(
    table: LoadedTable, max_combinations: int = 6
) -> tuple[KeyCandidate, ...]:
    columns = [name for name in table.header if name]
    if not columns or not table.rows:
        return ()
    single_columns = columns[: min(len(columns), max_combinations * 3)]
    if not single_columns:
        return ()
    normalized: dict[str, list[str | None]] = {}
    for column in single_columns:
        values: list[str | None] = []
        for row in table.rows:
            value = row.get(column)
            values.append(None if is_blank(value) else str(value).strip())
        normalized[column] = values
    candidates: list[KeyCandidate] = []
    for column in single_columns:
        candidates.append(
            _evaluate_key(
                table, (column,), normalized[column]
            )
        )
    for first_index, first in enumerate(single_columns):
        for second in single_columns[first_index + 1 :]:
            candidates.append(
                _evaluate_key(
                    table,
                    (first, second),
                    normalized[first],
                    normalized[second],
                )
            )
    ranked = sorted(
        candidates,
        key=lambda item: (-item.confidence, item.duplicate_value_n, len(item.key_columns)),
    )
    return tuple(ranked)


def _evaluate_key(
    table: LoadedTable,
    columns: tuple[str, ...],
    *normalized_values: list[str | None],
) -> KeyCandidate:
    total = len(table.rows)
    null_count = 0
    counts: dict[tuple[str, ...], int] = {}
    if len(columns) == 1:
        for value in normalized_values[0]:
            if value is None:
                null_count += 1
                continue
            key = (value,)
            counts[key] = counts.get(key, 0) + 1
    else:
        for first, second in zip(normalized_values[0], normalized_values[1]):
            if first is None or second is None:
                null_count += 1
                continue
            key = (first, second)
            counts[key] = counts.get(key, 0) + 1
    distinct = len(counts)
    non_null = total - null_count
    duplicates = sum(count - 1 for count in counts.values() if count > 1)
    is_unique = total > 0 and distinct == total and null_count == 0
    is_not_null = total > 0 and null_count == 0
    if is_unique:
        confidence = 1.0
    elif is_not_null and distinct == total:
        confidence = 0.95
    else:
        coverage = non_null / total if total else 0.0
        uniqueness = distinct / non_null if non_null else 0.0
        confidence = round(coverage * uniqueness * 0.9, 4)
    if is_unique:
        status = "UNIQUE_CANDIDATE"
    elif is_not_null:
        status = "CANDIDATE"
    else:
        status = "REJECTED"
    return KeyCandidate(
        source_id=table.source_id,
        split=table.split,
        business_id=table.business_id,
        object_name=table.object_name,
        key_columns=columns,
        total_n=total,
        non_null_n=non_null,
        distinct_n=distinct,
        duplicate_value_n=duplicates,
        null_count=null_count,
        is_unique=is_unique,
        is_not_null=is_not_null,
        confidence=confidence,
        status=status,
    )


def best_key_candidate(candidates: Sequence[KeyCandidate]) -> KeyCandidate | None:
    for candidate in candidates:
        if candidate.is_unique:
            return candidate
    return None
