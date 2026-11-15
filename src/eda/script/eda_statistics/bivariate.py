from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Any, Sequence

from common.enums import Status
from schema.type_inference import parse_number


@dataclass(frozen=True)
class PairResult:
    source_id: str
    split: str
    business_id: str
    field_x: str
    field_y: str
    method: str
    n_complete_pairs: int
    n_dropped: int
    pearson_r: float | None
    spearman_rho: float | None
    p_value: float | None
    status: Status
    notes: tuple[str, ...] = ()

    def to_dict(self) -> dict[str, Any]:
        return {
            "source_id": self.source_id,
            "split": self.split,
            "business_id": self.business_id,
            "field_x": self.field_x,
            "field_y": self.field_y,
            "method": self.method,
            "n_complete_pairs": self.n_complete_pairs,
            "n_dropped": self.n_dropped,
            "pearson_r": self.pearson_r,
            "spearman_rho": self.spearman_rho,
            "p_value": self.p_value,
            "status": self.status.value,
            "notes": list(self.notes),
        }


def _mean(values: Sequence[float]) -> float:
    return sum(values) / len(values)


def _ranks(values: Sequence[float]) -> list[float]:
    order = sorted(range(len(values)), key=lambda index: values[index])
    ranks = [0.0] * len(values)
    index = 0
    while index < len(order):
        end = index
        while end + 1 < len(order) and values[order[end + 1]] == values[order[index]]:
            end += 1
        average = (index + end) / 2.0 + 1.0
        for position in range(index, end + 1):
            ranks[order[position]] = average
        index = end + 1
    return ranks


def pearson(xs: Sequence[float], ys: Sequence[float]) -> float | None:
    count = len(xs)
    if count < 3:
        return None
    mean_x = _mean(xs)
    mean_y = _mean(ys)
    numerator = sum((x - mean_x) * (y - mean_y) for x, y in zip(xs, ys))
    sum_x = math.sqrt(sum((x - mean_x) ** 2 for x in xs))
    sum_y = math.sqrt(sum((y - mean_y) ** 2 for y in ys))
    if sum_x == 0 or sum_y == 0:
        return None
    return numerator / (sum_x * sum_y)


def spearman(xs: Sequence[float], ys: Sequence[float]) -> float | None:
    if len(xs) < 3:
        return None
    return pearson(_ranks(xs), _ranks(ys))


def pearson_p_value(r: float, n: int) -> float | None:
    if n < 3 or abs(r) >= 1.0:
        return None
    t_statistic = r * math.sqrt((n - 2) / (1 - r * r))
    degrees = n - 2
    x = degrees / (degrees + t_statistic * t_statistic)
    return _student_t_cdf_complement(t_statistic, degrees, x)


def _student_t_cdf_complement(
    t_statistic: float, degrees: int, x: float
) -> float:
    return 0.5 * _regularized_beta(x, degrees / 2.0, 0.5)


def _regularized_beta(x: float, a: float, b: float) -> float:
    if x <= 0:
        return 0.0
    if x >= 1:
        return 1.0
    front = math.exp(
        math.lgamma(a + b)
        - math.lgamma(a)
        - math.lgamma(b)
        + a * math.log(x)
        + b * math.log(1 - x)
    )
    if x < (a + 1) / (a + b + 2):
        return front * _beta_continued_fraction(x, a, b) / a
    return 1.0 - math.exp(
        math.lgamma(a + b)
        - math.lgamma(a)
        - math.lgamma(b)
        + b * math.log(1 - x)
        + a * math.log(x)
    ) * _beta_continued_fraction(1 - x, b, a) / b


def _beta_continued_fraction(x: float, a: float, b: float) -> float:
    max_iterations = 200
    epsilon = 3.0e-12
    tiny = 1.0e-30
    qab = a + b
    qap = a + 1.0
    qam = a - 1.0
    c = 1.0
    d = 1.0 - qab * x / qap
    if abs(d) < tiny:
        d = tiny
    d = 1.0 / d
    result = d
    for iteration in range(1, max_iterations + 1):
        m2 = 2 * iteration
        numerator = iteration * (b - iteration) * x / ((qam + m2) * (a + m2))
        d = 1.0 + numerator * d
        if abs(d) < tiny:
            d = tiny
        c = 1.0 + numerator / c
        if abs(c) < tiny:
            c = tiny
        d = 1.0 / d
        result *= d * c
        numerator = -(a + iteration) * (qab + iteration) * x / (
            (a + m2) * (qap + m2)
        )
        d = 1.0 + numerator * d
        if abs(d) < tiny:
            d = tiny
        c = 1.0 + numerator / c
        if abs(c) < tiny:
            c = tiny
        d = 1.0 / d
        delta = d * c
        result *= delta
        if abs(delta - 1.0) < epsilon:
            break
    return result


def profile_bivariate(
    source_id: str,
    split: str,
    business_id: str,
    field_x: str,
    field_y: str,
    rows: Sequence[dict[str, Any]],
    grain_verified: bool = True,
) -> PairResult:
    xs: list[float] = []
    ys: list[float] = []
    dropped = 0
    for row in rows:
        x_value = parse_number(row.get(field_x))
        y_value = parse_number(row.get(field_y))
        if x_value is None or y_value is None:
            dropped += 1
            continue
        xs.append(x_value)
        ys.append(y_value)
    notes: list[str] = []
    if not grain_verified:
        notes.append("join_grain_not_verified_association_blocked")
        return PairResult(
            source_id=source_id,
            split=split,
            business_id=business_id,
            field_x=field_x,
            field_y=field_y,
            method="blocked_unverified_grain",
            n_complete_pairs=len(xs),
            n_dropped=dropped,
            pearson_r=None,
            spearman_rho=None,
            p_value=None,
            status=Status.BLOCKED,
            notes=tuple(notes),
        )
    if len(xs) < 3:
        notes.append("insufficient_pairs")
        return PairResult(
            source_id=source_id,
            split=split,
            business_id=business_id,
            field_x=field_x,
            field_y=field_y,
            method="insufficient_data",
            n_complete_pairs=len(xs),
            n_dropped=dropped,
            pearson_r=None,
            spearman_rho=None,
            p_value=None,
            status=Status.BLOCKED,
            notes=tuple(notes),
        )
    r_value = pearson(xs, ys)
    rho_value = spearman(xs, ys)
    p_value = pearson_p_value(r_value, len(xs)) if r_value is not None else None
    notes.append("association_only_no_causal_claim")
    return PairResult(
        source_id=source_id,
        split=split,
        business_id=business_id,
        field_x=field_x,
        field_y=field_y,
        method="pearson_spearman_full_population",
        n_complete_pairs=len(xs),
        n_dropped=dropped,
        pearson_r=round(r_value, 6) if r_value is not None else None,
        spearman_rho=round(rho_value, 6) if rho_value is not None else None,
        p_value=round(p_value, 6) if p_value is not None else None,
        status=Status.PASS,
        notes=tuple(notes),
    )


def contingency_table(
    rows: Sequence[dict[str, Any]], field_x: str, field_y: str
) -> tuple[list[str], list[str], list[list[int]]]:
    x_labels: list[str] = []
    y_labels: list[str] = []
    x_index: dict[str, int] = {}
    y_index: dict[str, int] = {}
    counts: list[list[int]] = []
    for row in rows:
        x_value = row.get(field_x)
        y_value = row.get(field_y)
        if x_value is None or y_value is None:
            continue
        x_label = str(x_value).strip()
        y_label = str(y_value).strip()
        if not x_label or not y_label:
            continue
        if x_label not in x_index:
            x_index[x_label] = len(x_labels)
            x_labels.append(x_label)
            counts.append([0] * 0)
        if y_label not in y_index:
            y_index[y_label] = len(y_labels)
            for existing in counts:
                existing.append(0)
        counts[x_index[x_label]][y_index[y_label]] += 1
    return x_labels, y_labels, counts


def cramers_v(
    x_labels: list[str], y_labels: list[str], counts: list[list[int]]
) -> float | None:
    total = sum(sum(row) for row in counts)
    if total == 0:
        return None
    row_totals = [sum(row) for row in counts]
    column_totals = [sum(counts[i][j] for i in range(len(counts))) for j in range(len(y_labels))]
    chi_square = 0.0
    for i in range(len(x_labels)):
        for j in range(len(y_labels)):
            expected = row_totals[i] * column_totals[j] / total
            if expected <= 0:
                continue
            chi_square += (counts[i][j] - expected) ** 2 / expected
    denominator = total * min(len(x_labels) - 1, len(y_labels) - 1)
    if denominator <= 0:
        return None
    return math.sqrt(chi_square / denominator)
