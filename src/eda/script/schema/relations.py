from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Sequence

from common.contracts import RelationEvidence
from common.enums import RelationStatus
from readers.table_reader import LoadedTable
from schema.type_inference import is_blank

KEY_NAME_TOKENS = (
    "mã hóa đơn",
    "mã hoá đơn",
    "ma hoa don",
    "mã chứng từ",
    "ma chung tu",
    "bill",
    "mã đơn",
    "ma don",
    "mã đơn hàng",
    "ma don hang",
    "mã phiếu",
    "ma phieu",
    "mã nhập hàng",
    "ma nhap hang",
    "mã hàng",
    "ma hang",
    "mã khách",
    "ma khach",
    "mã kh",
    "mã gd",
    "mã giao dịch",
    "id",
    "mã lô",
    "ma lo",
    "số phiếu",
    "so phieu",
)


@dataclass(frozen=True)
class RelationCandidate:
    left_source: str
    right_source: str
    join_keys: tuple[str, ...]
    left_object: str
    right_object: str

    def relation_id(self, split: str, business_id: str) -> str:
        key_part = "_".join(self.join_keys)
        return f"{split}.{business_id}.{self.left_object}__{key_part}__{self.right_object}"


def _normalized_name(name: str) -> str:
    return name.strip().lower()


def propose_key_pairs(
    left: LoadedTable, right: LoadedTable
) -> list[tuple[str, ...]]:
    left_columns = {_normalized_name(name): name for name in left.header if name}
    right_columns = {_normalized_name(name): name for name in right.header if name}
    pairs: list[tuple[str, ...]] = []
    for left_key, left_name in left_columns.items():
        for right_key, right_name in right_columns.items():
            if left_key != right_key:
                continue
            pairs.append((left_name, right_name))
    if not pairs:
        for token in KEY_NAME_TOKENS:
            for left_key, left_name in left_columns.items():
                if token not in left_key:
                    continue
                for right_key, right_name in right_columns.items():
                    if token not in right_key:
                        continue
                    pairs.append((left_name, right_name))
                break
    return pairs


def _key_set(table: LoadedTable, columns: Sequence[str]) -> tuple[set[tuple[str, ...]], int]:
    values: set[tuple[str, ...]] = set()
    null_count = 0
    for row in table.rows:
        parts: list[str] = []
        missing = False
        for column in columns:
            value = row.get(column)
            if is_blank(value):
                missing = True
                break
            parts.append(str(value).strip())
        if missing:
            null_count += 1
            continue
        values.add(tuple(parts))
    return values, null_count


def profile_relation(
    left: LoadedTable,
    right: LoadedTable,
    join_keys: tuple[str, ...],
    split: str,
    business_id: str,
    measure_column: str | None = None,
) -> RelationEvidence:
    left_values, left_nulls = _key_set(left, join_keys)
    right_values, right_nulls = _key_set(right, join_keys)
    matched = left_values & right_values
    unmatched_left = left_values - right_values
    unmatched_right = right_values - left_values
    left_duplicate = max(0, len(left.rows) - len(left_values) - left_nulls)
    right_duplicate = max(0, len(right.rows) - len(right_values) - right_nulls)
    fanout = round(len(right.rows) / len(left.rows), 4) if left.rows else 0.0
    evidence: list[str] = []
    risk: str | None = None
    status = RelationStatus.CANDIDATE.value
    if not matched:
        status = RelationStatus.REJECTED.value
        risk = "no_key_overlap"
    elif left_duplicate or right_duplicate:
        status = RelationStatus.CANDIDATE.value
        risk = "duplicate_keys_may_cause_fanout"
    elif unmatched_left or unmatched_right:
        status = RelationStatus.CANDIDATE.value
        risk = "unmatched_keys_present"
    else:
        status = RelationStatus.APPROVED.value
    if measure_column and measure_column in right.header:
        left_sum = _sum_numeric(left, measure_column)
        right_sum = _sum_numeric(right, measure_column)
        evidence.append(
            f"measure_sum_left={left_sum};measure_sum_right={right_sum};"
            f"row_ratio={fanout}"
        )
    else:
        evidence.append(f"row_ratio_right_over_left={fanout}")
    invariant = (
        "aggregate of joined rows must equal aggregate of right table when left key is unique"
    )
    return RelationEvidence(
        relation_id=RelationCandidate(
            left_source=left.source_id,
            right_source=right.source_id,
            join_keys=join_keys,
            left_object=left.object_name,
            right_object=right.object_name,
        ).relation_id(split, business_id),
        split=split,
        business_id=business_id,
        left_source=left.source_id,
        right_source=right.source_id,
        join_keys=join_keys,
        left_grain=f"one row per {left.object_name}",
        right_grain=f"one row per {right.object_name}",
        status=status,
        left_rows=len(left.rows),
        right_rows=len(right.rows),
        matched_rows=len(matched),
        unmatched_left_rows=len(unmatched_left),
        unmatched_right_rows=len(unmatched_right),
        key_null_left=left_nulls,
        key_null_right=right_nulls,
        duplicate_key_left=left_duplicate,
        duplicate_key_right=right_duplicate,
        fanout_factor=fanout,
        expected_invariant=invariant,
        evidence=tuple(evidence),
        risk=risk,
    )


def _sum_numeric(table: LoadedTable, column: str) -> float:
    from schema.type_inference import parse_number

    total = 0.0
    for row in table.rows:
        value = parse_number(row.get(column))
        if value is not None:
            total += value
    return round(total, 4)


def approve_relation(evidence: RelationEvidence) -> RelationEvidence:
    if evidence.status != RelationStatus.APPROVED.value:
        return evidence
    from dataclasses import replace

    return replace(evidence, status=RelationStatus.APPROVED.value)
