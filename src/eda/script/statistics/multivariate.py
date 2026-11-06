from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Sequence

from common.enums import Status
from schema.type_inference import parse_number
from statistics.bivariate import pearson, spearman


@dataclass(frozen=True)
class MultivariateResult:
    source_id: str
    split: str
    business_id: str
    fields: tuple[str, ...]
    method: str
    matrix: tuple[tuple[float | None, ...], ...]
    status: Status
    notes: tuple[str, ...] = ()

    def to_dict(self) -> dict[str, Any]:
        return {
            "source_id": self.source_id,
            "split": self.split,
            "business_id": self.business_id,
            "fields": list(self.fields),
            "method": self.method,
            "matrix": [list(row) for row in self.matrix],
            "status": self.status.value,
            "notes": list(self.notes),
        }


def profile_multivariate(
    source_id: str,
    split: str,
    business_id: str,
    fields: Sequence[str],
    rows: Sequence[dict[str, Any]],
    method: str = "pearson_correlation_matrix",
) -> MultivariateResult:
    usable = list(fields)
    if len(usable) < 2:
        return MultivariateResult(
            source_id=source_id,
            split=split,
            business_id=business_id,
            fields=tuple(usable),
            method=method,
            matrix=(),
            status=Status.NOT_APPLICABLE,
            notes=("fewer_than_two_measure_fields",),
        )
    complete_rows: list[list[float]] = []
    for row in rows:
        values: list[float] = []
        for field in usable:
            number = parse_number(row.get(field))
            if number is None:
                break
            values.append(number)
        else:
            complete_rows.append(values)
    if len(complete_rows) < 3:
        return MultivariateResult(
            source_id=source_id,
            split=split,
            business_id=business_id,
            fields=tuple(usable),
            method=method,
            matrix=(),
            status=Status.BLOCKED,
            notes=("insufficient_complete_cases",),
        )
    notes: list[str] = []
    columns = list(zip(*complete_rows))
    constant_fields = [
        field for field, column in zip(usable, columns) if len(set(column)) <= 1
    ]
    if constant_fields:
        notes.append(f"constant_fields_excluded:{','.join(constant_fields)}")
    matrix: list[tuple[float | None, ...]] = []
    for index_x, column_x in enumerate(columns):
        row_values: list[float | None] = []
        for index_y, column_y in enumerate(columns):
            if index_x == index_y:
                row_values.append(1.0)
                continue
            if len(set(column_x)) <= 1 or len(set(column_y)) <= 1:
                row_values.append(None)
                continue
            row_values.append(
                round(pearson(list(column_x), list(column_y)) or 0.0, 6)
            )
        matrix.append(tuple(row_values))
    return MultivariateResult(
        source_id=source_id,
        split=split,
        business_id=business_id,
        fields=tuple(usable),
        method=method,
        matrix=tuple(matrix),
        status=Status.PASS,
        notes=tuple(notes),
    )


def spearman_matrix(
    source_id: str,
    split: str,
    business_id: str,
    fields: Sequence[str],
    rows: Sequence[dict[str, Any]],
) -> MultivariateResult:
    usable = list(fields)
    if len(usable) < 2:
        return MultivariateResult(
            source_id=source_id,
            split=split,
            business_id=business_id,
            fields=tuple(usable),
            method="spearman_correlation_matrix",
            matrix=(),
            status=Status.NOT_APPLICABLE,
            notes=("fewer_than_two_measure_fields",),
        )
    complete_rows: list[list[float]] = []
    for row in rows:
        values: list[float] = []
        for field in usable:
            number = parse_number(row.get(field))
            if number is None:
                break
            values.append(number)
        else:
            complete_rows.append(values)
    if len(complete_rows) < 3:
        return MultivariateResult(
            source_id=source_id,
            split=split,
            business_id=business_id,
            fields=tuple(usable),
            method="spearman_correlation_matrix",
            matrix=(),
            status=Status.BLOCKED,
            notes=("insufficient_complete_cases",),
        )
    columns = list(zip(*complete_rows))
    matrix: list[tuple[float | None, ...]] = []
    for index_x, column_x in enumerate(columns):
        row_values: list[float | None] = []
        for index_y, column_y in enumerate(columns):
            if index_x == index_y:
                row_values.append(1.0)
                continue
            if len(set(column_x)) <= 1 or len(set(column_y)) <= 1:
                row_values.append(None)
                continue
            row_values.append(
                round(spearman(list(column_x), list(column_y)) or 0.0, 6)
            )
        matrix.append(tuple(row_values))
    return MultivariateResult(
        source_id=source_id,
        split=split,
        business_id=business_id,
        fields=tuple(usable),
        method="spearman_correlation_matrix",
        matrix=tuple(matrix),
        status=Status.PASS,
        notes=("association_only_no_causal_claim",),
    )
