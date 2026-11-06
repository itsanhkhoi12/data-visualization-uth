from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Any, Sequence

from common.enums import Status

METHOD_VERSION = "association_profile.v1"
MIN_PAIRS = 3


@dataclass(frozen=True)
class AssociationEntry:
    field_x: str
    field_y: str
    n_pairs: int
    n_dropped: int
    pearson_r: float | None
    spearman_rho: float | None
    kendall_tau_b: float | None
    p_value: float | None
    status: Status
    notes: tuple[str, ...] = ()

    def to_dict(self) -> dict[str, Any]:
        return {
            "field_x": self.field_x,
            "field_y": self.field_y,
            "n_pairs": self.n_pairs,
            "n_dropped": self.n_dropped,
            "pearson_r": self.pearson_r,
            "spearman_rho": self.spearman_rho,
            "kendall_tau_b": self.kendall_tau_b,
            "p_value": self.p_value,
            "status": self.status.value,
            "notes": list(self.notes),
        }


def kendall_tau_b(xs: Sequence[float], ys: Sequence[float]) -> float | None:
    count = len(xs)
    if count < 2:
        return None
    concordant = 0
    discordant = 0
    tied_x = 0
    tied_y = 0
    for i in range(count - 1):
        dx = xs[i + 1] - xs[i]
        for j in range(i + 2, count + 1):
            dy = ys[j - 1] - ys[i]
            if dx == 0 and dy == 0:
                tied_x += 1
                tied_y += 1
            elif dx == 0:
                tied_x += 1
            elif dy == 0:
                tied_y += 1
            elif (dx > 0) == (dy > 0):
                concordant += 1
            else:
                discordant += 1
    denominator = math.sqrt(
        (concordant + discordant + tied_x) * (concordant + discordant + tied_y)
    )
    if denominator == 0:
        return None
    return (concordant - discordant) / denominator


def pearson_from_ranks(ranks_x: Sequence[float], ranks_y: Sequence[float]) -> float | None:
    count = len(ranks_x)
    if count < 3:
        return None
    mean_x = sum(ranks_x) / count
    mean_y = sum(ranks_y) / count
    numerator = sum(
        (x - mean_x) * (y - mean_y) for x, y in zip(ranks_x, ranks_y)
    )
    sum_x = math.sqrt(sum((x - mean_x) ** 2 for x in ranks_x))
    sum_y = math.sqrt(sum((y - mean_y) ** 2 for y in ranks_y))
    if sum_x == 0 or sum_y == 0:
        return None
    return numerator / (sum_x * sum_y)


def association_entries(
    fields: Sequence[str],
    rows: Sequence[dict[str, Any]],
    parse: Any,
    grain_verified: bool = True,
    max_fields: int = 8,
) -> tuple[AssociationEntry, ...]:
    usable = list(fields)[:max_fields]
    if len(usable) < 2:
        return ()
    if not grain_verified:
        return tuple(
            AssociationEntry(
                field_x=usable[index],
                field_y=usable[other],
                n_pairs=0,
                n_dropped=0,
                pearson_r=None,
                spearman_rho=None,
                kendall_tau_b=None,
                p_value=None,
                status=Status.BLOCKED,
                notes=("join_grain_not_verified_association_blocked",),
            )
            for index in range(len(usable))
            for other in range(index + 1, len(usable))
        )
    columns: dict[str, list[float | None]] = {field: [] for field in usable}
    dropped = 0
    for row in rows:
        values: list[float | None] = []
        for field in usable:
            values.append(parse(row.get(field)))
        if any(value is None for value in values):
            dropped += 1
            continue
        for field, value in zip(usable, values):
            columns[field].append(float(value))
    complete = len(next(iter(columns.values()))) if columns else 0
    entries: list[AssociationEntry] = []
    if complete < MIN_PAIRS:
        for index in range(len(usable)):
            for other in range(index + 1, len(usable)):
                entries.append(
                    AssociationEntry(
                        field_x=usable[index],
                        field_y=usable[other],
                        n_pairs=complete,
                        n_dropped=dropped,
                        pearson_r=None,
                        spearman_rho=None,
                        kendall_tau_b=None,
                        p_value=None,
                        status=Status.BLOCKED,
                        notes=("insufficient_complete_pairs",),
                    )
                )
        return tuple(entries)
    from statistics.bivariate import pearson, spearman

    for index in range(len(usable)):
        for other in range(index + 1, len(usable)):
            xs = [float(value) for value in columns[usable[index]]]
            ys = [float(value) for value in columns[usable[other]]]
            pearson_r = pearson(xs, ys)
            spearman_rho = spearman(xs, ys)
            tau_b = kendall_tau_b(xs, ys)
            notes: list[str] = ["association_only_no_causal_claim"]
            status = Status.PASS
            if pearson_r is None or spearman_rho is None:
                status = Status.BLOCKED
                notes.append("constant_or_degenerate_column")
            entries.append(
                AssociationEntry(
                    field_x=usable[index],
                    field_y=usable[other],
                    n_pairs=complete,
                    n_dropped=dropped,
                    pearson_r=round(pearson_r, 6) if pearson_r is not None else None,
                    spearman_rho=(
                        round(spearman_rho, 6) if spearman_rho is not None else None
                    ),
                    kendall_tau_b=round(tau_b, 6) if tau_b is not None else None,
                    p_value=None,
                    status=status,
                    notes=tuple(notes),
                )
            )
    return tuple(entries)


def correlation_matrix(
    fields: Sequence[str],
    rows: Sequence[dict[str, Any]],
    parse: Any,
    method: str = "pearson",
) -> tuple[tuple[str, ...], tuple[tuple[float | None, ...], ...], tuple[str, ...]]:
    usable = list(fields)
    size = len(usable)
    matrix: list[tuple[float | None, ...]] = []
    notes: list[str] = []
    for index_x in range(size):
        row_values: list[float | None] = []
        for index_y in range(size):
            if index_x == index_y:
                row_values.append(1.0)
                continue
            entries = association_entries(
                [usable[index_x], usable[index_y]], rows, parse, max_fields=2
            )
            if not entries:
                row_values.append(None)
                continue
            entry = entries[0]
            if method == "spearman":
                row_values.append(entry.spearman_rho)
            elif method == "kendall":
                row_values.append(entry.kendall_tau_b)
            else:
                row_values.append(entry.pearson_r)
            for note in entry.notes:
                if note not in notes:
                    notes.append(note)
        matrix.append(tuple(row_values))
    return tuple(usable), tuple(matrix), tuple(notes)
