from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Any, Sequence

from common.contracts import NumericStats
from common.enums import Status
from schema.type_inference import parse_number

METHOD_VERSION = "numeric.v1"


@dataclass(frozen=True)
class NumericProfileRequest:
    source_id: str
    split: str
    business_id: str
    field: str
    unit: str | None
    values: Sequence[Any]
    total_n: int
    method: str = "descriptive_full_population"
    method_version: str = METHOD_VERSION


def _median(sorted_values: list[float]) -> float:
    count = len(sorted_values)
    middle = count // 2
    if count % 2:
        return sorted_values[middle]
    return (sorted_values[middle - 1] + sorted_values[middle]) / 2.0


def _quantile(sorted_values: list[float], probability: float) -> float:
    if not sorted_values:
        return math.nan
    if len(sorted_values) == 1:
        return sorted_values[0]
    position = probability * (len(sorted_values) - 1)
    lower = math.floor(position)
    upper = math.ceil(position)
    if lower == upper:
        return sorted_values[int(position)]
    weight = position - lower
    return sorted_values[lower] * (1 - weight) + sorted_values[upper] * weight


def _mad(sorted_values: list[float]) -> float:
    median = _median(sorted_values)
    deviations = sorted(abs(value - median) for value in sorted_values)
    return _median(deviations)


def _skewness(values: list[float]) -> float | None:
    count = len(values)
    if count < 3:
        return None
    mean = sum(values) / count
    variance = sum((value - mean) ** 2 for value in values) / (count - 1)
    if variance <= 0:
        return None
    sigma = math.sqrt(variance)
    return sum(((value - mean) / sigma) ** 3 for value in values) * (count / ((count - 1) * (count - 2)))


def _kurtosis(values: list[float]) -> float | None:
    count = len(values)
    if count < 4:
        return None
    mean = sum(values) / count
    variance = sum((value - mean) ** 2 for value in values) / (count - 1)
    if variance <= 0:
        return None
    sigma = math.sqrt(variance)
    fourth = sum(((value - mean) / sigma) ** 4 for value in values) * (
        count / ((count - 1) * (count - 2) * (count - 3))
    )
    return fourth - 3.0


def profile_numeric(request: NumericProfileRequest) -> NumericStats:
    parsed: list[float] = []
    missing = 0
    zero = 0
    for value in request.values:
        number = parse_number(value)
        if number is None:
            missing += 1
            continue
        parsed.append(number)
        if number == 0:
            zero += 1
    total = request.total_n if request.total_n else len(request.values)
    valid = len(parsed)
    warnings: list[str] = []
    if valid == 0:
        return NumericStats(
            source_id=request.source_id,
            split=request.split,
            business_id=request.business_id,
            field=request.field,
            unit=request.unit,
            n_total=total,
            n_valid=0,
            n_missing=missing,
            n_zero=0,
            mean=None,
            median=None,
            std=None,
            variance=None,
            minimum=None,
            maximum=None,
            q25=None,
            q75=None,
            iqr=None,
            mad=None,
            skewness=None,
            kurtosis=None,
            zero_ratio=0.0,
            method=request.method,
            method_version=request.method_version,
            status=Status.BLOCKED,
            warnings=("no_parseable_values",),
        )
    sorted_values = sorted(parsed)
    mean = sum(parsed) / valid
    variance = (
        sum((value - mean) ** 2 for value in parsed) / (valid - 1) if valid > 1 else 0.0
    )
    std = math.sqrt(variance)
    q25 = _quantile(sorted_values, 0.25)
    q75 = _quantile(sorted_values, 0.75)
    zero_ratio = round(zero / valid, 6)
    if valid < 30:
        warnings.append("small_sample_for_shape_statistics")
    if zero_ratio > 0.3:
        warnings.append("high_zero_inflation")
    if std == 0:
        warnings.append("constant_field")
    return NumericStats(
        source_id=request.source_id,
        split=request.split,
        business_id=request.business_id,
        field=request.field,
        unit=request.unit,
        n_total=total,
        n_valid=valid,
        n_missing=missing,
        n_zero=zero,
        mean=round(mean, 6),
        median=round(_median(sorted_values), 6),
        std=round(std, 6),
        variance=round(variance, 6),
        minimum=round(sorted_values[0], 6),
        maximum=round(sorted_values[-1], 6),
        q25=round(q25, 6),
        q75=round(q75, 6),
        iqr=round(q75 - q25, 6),
        mad=round(_mad(sorted_values), 6),
        skewness=round(_skewness(parsed), 6) if _skewness(parsed) is not None else None,
        kurtosis=round(_kurtosis(parsed), 6) if _kurtosis(parsed) is not None else None,
        zero_ratio=zero_ratio,
        method=request.method,
        method_version=request.method_version,
        status=Status.PASS,
        warnings=tuple(warnings),
    )


def empirical_cdf(values: Sequence[float]) -> tuple[list[float], list[float]]:
    sorted_values = sorted(values)
    count = len(sorted_values)
    xs: list[float] = []
    ys: list[float] = []
    for index, value in enumerate(sorted_values, start=1):
        xs.append(value)
        ys.append(round(index / count, 6) if count else 0.0)
    return xs, ys


def histogram_bins(values: Sequence[float], bin_count: int = 20) -> tuple[list[float], list[int]]:
    if not values:
        return [], []
    minimum = min(values)
    maximum = max(values)
    if minimum == maximum:
        return [minimum, minimum], [len(values)]
    width = (maximum - minimum) / bin_count
    counts = [0] * bin_count
    for value in values:
        index = int((value - minimum) / width)
        if index >= bin_count:
            index = bin_count - 1
        counts[index] += 1
    edges = [round(minimum + index * width, 6) for index in range(bin_count + 1)]
    return edges, counts


def iqr_fences(stats: NumericStats, multiplier: float = 1.5) -> tuple[float, float] | None:
    if stats.q25 is None or stats.q75 is None:
        return None
    spread = stats.q75 - stats.q25
    return stats.q25 - multiplier * spread, stats.q75 + multiplier * spread


def modified_z_scores(values: Sequence[float], median: float, mad: float) -> list[float]:
    if mad == 0:
        return [0.0] * len(values)
    return [round(0.6745 * (value - median) / mad, 6) for value in values]
