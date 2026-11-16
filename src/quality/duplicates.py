from __future__ import annotations

import hashlib
from dataclasses import dataclass
from typing import Any, Sequence

from readers.table_reader import LoadedTable
from schema.type_inference import is_blank


@dataclass(frozen=True)
class DuplicateEntry:
    source_id: str
    split: str
    business_id: str
    object_name: str
    key_columns: tuple[str, ...]
    duplicate_class: str
    n_duplicate_rows: int
    n_distinct_keys: int
    total_n: int
    explanation: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "source_id": self.source_id,
            "split": self.split,
            "business_id": self.business_id,
            "object_name": self.object_name,
            "key_columns": list(self.key_columns),
            "duplicate_class": self.duplicate_class,
            "n_duplicate_rows": self.n_duplicate_rows,
            "n_distinct_keys": self.n_distinct_keys,
            "total_n": self.total_n,
            "explanation": self.explanation,
        }


def _row_fingerprint(row: dict[str, Any], columns: Sequence[str]) -> str:
    payload = "\x1f".join(str(row.get(column, "")).strip() for column in columns)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def profile_duplicates(
    table: LoadedTable, key_columns: Sequence[str] | None = None
) -> tuple[DuplicateEntry, ...]:
    columns = [name for name in table.header if name]
    if not columns or not table.rows:
        return ()
    entries: list[DuplicateEntry] = []
    fingerprint_counts: dict[str, int] = {}
    for row in table.rows:
        fingerprint_counts[_row_fingerprint(row, columns)] = (
            fingerprint_counts.get(_row_fingerprint(row, columns), 0) + 1
        )
    exact_duplicate_rows = sum(count - 1 for count in fingerprint_counts.values() if count > 1)
    entries.append(
        DuplicateEntry(
            source_id=table.source_id,
            split=table.split,
            business_id=table.business_id,
            object_name=table.object_name,
            key_columns=(),
            duplicate_class="exact_row",
            n_duplicate_rows=exact_duplicate_rows,
            n_distinct_keys=len(fingerprint_counts),
            total_n=len(table.rows),
            explanation=(
                "identical full-row values may represent legitimate repeated events "
                "at order-line grain; not auto-removed"
            ),
        )
    )
    if key_columns:
        key_counts: dict[tuple[str, ...], int] = {}
        for row in table.rows:
            parts: list[str] = []
            missing = False
            for column in key_columns:
                value = row.get(column)
                if is_blank(value):
                    missing = True
                    break
                parts.append(str(value).strip())
            if missing:
                continue
            key = tuple(parts)
            key_counts[key] = key_counts.get(key, 0) + 1
        duplicated = sum(count - 1 for count in key_counts.values() if count > 1)
        entries.append(
            DuplicateEntry(
                source_id=table.source_id,
                split=table.split,
                business_id=table.business_id,
                object_name=table.object_name,
                key_columns=tuple(key_columns),
                duplicate_class="business_key",
                n_duplicate_rows=duplicated,
                n_distinct_keys=len(key_counts),
                total_n=len(table.rows),
                explanation=(
                    "rows sharing the candidate business key; duplicates are valid "
                    "when the grain is line-item and invalid when the grain is order"
                ),
            )
        )
    return tuple(entries)
