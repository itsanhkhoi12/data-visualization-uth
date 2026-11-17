from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Any, Sequence

METHOD_VERSION = "categorical_association.v1"
MIN_CROSSTAB_N = 5


@dataclass(frozen=True)
class CrosstabAssociation:
    field_x: str
    field_y: str
    x_labels: tuple[str, ...]
    y_labels: tuple[str, ...]
    counts: tuple[tuple[int, ...], ...]
    row_totals: tuple[int, ...]
    column_totals: tuple[int, ...]
    total_n: int
    cramers_v: float | None
    chi_square: float | None
    min_expected_count: float | None
    status: str
    reason: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "field_x": self.field_x,
            "field_y": self.field_y,
            "x_labels": list(self.x_labels),
            "y_labels": list(self.y_labels),
            "counts": [list(row) for row in self.counts],
            "row_totals": list(self.row_totals),
            "column_totals": list(self.column_totals),
            "total_n": self.total_n,
            "cramers_v": self.cramers_v,
            "chi_square": self.chi_square,
            "min_expected_count": self.min_expected_count,
            "status": self.status,
            "reason": self.reason,
        }


def build_crosstab(
    rows: Sequence[dict[str, Any]], field_x: str, field_y: str
) -> tuple[tuple[str, ...], tuple[str, ...], tuple[tuple[int, ...], ...]]:
    x_labels: list[str] = []
    y_labels: list[str] = []
    x_index: dict[str, int] = {}
    y_index: dict[str, int] = {}
    counts: list[list[int]] = []
    for row in rows:
        raw_x = row.get(field_x)
        raw_y = row.get(field_y)
        if raw_x is None or raw_y is None:
            continue
        label_x = str(raw_x).strip()
        label_y = str(raw_y).strip()
        if not label_x or not label_y:
            continue
        if label_x not in x_index:
            x_index[label_x] = len(x_labels)
            x_labels.append(label_x)
            counts.append([0])
        if label_y not in y_index:
            y_index[label_y] = len(y_labels)
            for existing in counts:
                existing.append(0)
        counts[x_index[label_x]][y_index[label_y]] += 1
    return (
        tuple(x_labels),
        tuple(y_labels),
        tuple(tuple(row) for row in counts),
    )


def cramers_v_with_details(
    x_labels: Sequence[str],
    y_labels: Sequence[str],
    counts: Sequence[Sequence[int]],
) -> tuple[float | None, float | None, float | None]:
    total = sum(sum(row) for row in counts)
    if total == 0:
        return None, None, None
    row_totals = [sum(row) for row in counts]
    column_totals = [
        sum(counts[index][column] for index in range(len(counts)))
        for column in range(len(y_labels))
    ]
    chi_square = 0.0
    min_expected = None
    for index_x in range(len(x_labels)):
        for index_y in range(len(y_labels)):
            expected = row_totals[index_x] * column_totals[index_y] / total
            if expected <= 0:
                continue
            min_expected = (
                expected if min_expected is None else min(min_expected, expected)
            )
            chi_square += (counts[index_x][index_y] - expected) ** 2 / expected
    denominator = total * min(len(x_labels) - 1, len(y_labels) - 1)
    if denominator <= 0:
        return None, chi_square, min_expected
    return math.sqrt(chi_square / denominator), chi_square, min_expected


def crosstab_association(
    rows: Sequence[dict[str, Any]], field_x: str, field_y: str
) -> CrosstabAssociation:
    x_labels, y_labels, counts = build_crosstab(rows, field_x, field_y)
    total = sum(sum(row) for row in counts)
    row_totals = tuple(sum(row) for row in counts)
    column_totals = tuple(
        sum(counts[index][column] for index in range(len(counts)))
        for column in range(len(y_labels))
    )
    if len(x_labels) < 2 or len(y_labels) < 2:
        return CrosstabAssociation(
            field_x=field_x,
            field_y=field_y,
            x_labels=x_labels,
            y_labels=y_labels,
            counts=counts,
            row_totals=row_totals,
            column_totals=column_totals,
            total_n=total,
            cramers_v=None,
            chi_square=None,
            min_expected_count=None,
            status="NOT_APPLICABLE",
            reason="crosstab_requires_at_least_two_levels_per_axis",
        )
    if total < MIN_CROSSTAB_N:
        return CrosstabAssociation(
            field_x=field_x,
            field_y=field_y,
            x_labels=x_labels,
            y_labels=y_labels,
            counts=counts,
            row_totals=row_totals,
            column_totals=column_totals,
            total_n=total,
            cramers_v=None,
            chi_square=None,
            min_expected_count=None,
            status="BLOCKED",
            reason="insufficient_crosstab_observations",
        )
    cramers_v, chi_square, min_expected = cramers_v_with_details(
        x_labels, y_labels, counts
    )
    status = "PASS"
    reason = "association_only_no_causal_claim"
    if min_expected is not None and min_expected < 5:
        status = "PARTIAL"
        reason = "small_expected_cell_counts_reduce_reliability"
    return CrosstabAssociation(
        field_x=field_x,
        field_y=field_y,
        x_labels=x_labels,
        y_labels=y_labels,
        counts=counts,
        row_totals=row_totals,
        column_totals=column_totals,
        total_n=total,
        cramers_v=round(cramers_v, 6) if cramers_v is not None else None,
        chi_square=round(chi_square, 6) if chi_square is not None else None,
        min_expected_count=(
            round(min_expected, 6) if min_expected is not None else None
        ),
        status=status,
        reason=reason,
    )


def crosstab_row_shares(
    x_labels: Sequence[str],
    y_labels: Sequence[str],
    counts: Sequence[Sequence[int]],
) -> tuple[tuple[float, ...], ...]:
    shares: list[tuple[float, ...]] = []
    for row in counts:
        total = sum(row)
        if total <= 0:
            shares.append(tuple(0.0 for _ in row))
            continue
        shares.append(tuple(value / total for value in row))
    return tuple(shares)
