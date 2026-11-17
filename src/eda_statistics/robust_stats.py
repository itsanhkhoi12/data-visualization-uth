from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Any, Sequence

METHOD_VERSION = "robust_stats.v1"
QUANTILE_LEVELS: tuple[float, ...] = (
    0.01,
    0.05,
    0.10,
    0.25,
    0.50,
    0.75,
    0.90,
    0.95,
    0.99,
)
ROBUST_Z_CONSTANT = 0.6745
IQR_MULTIPLIER = 1.5


@dataclass(frozen=True)
class RobustDispersion:
    n_valid: int
    n_total: int
    n_missing: int
    n_zero: int
    n_negative: int
    minimum: float
    maximum: float
    mean: float
    median: float
    variance: float
    std: float
    q01: float
    q05: float
    q25: float
    q50: float
    q75: float
    q95: float
    q99: float
    iqr: float
    mad: float
    normalized_mad: float
    skewness: float | None
    kurtosis: float | None
    zero_ratio: float
    negative_ratio: float
    coefficient_of_variation: float | None
    iqr_lower_fence: float | None
    iqr_upper_fence: float | None
    outlier_lower_n: int
    outlier_upper_n: int
    outlier_ratio: float
    robust_z_upper_n: int
    degenerate_iqr: bool
    method: str
    method_version: str
    warnings: tuple[str, ...] = ()

    def to_dict(self) -> dict[str, Any]:
        return {
            "n_valid": self.n_valid,
            "n_total": self.n_total,
            "n_missing": self.n_missing,
            "n_zero": self.n_zero,
            "n_negative": self.n_negative,
            "minimum": self.minimum,
            "maximum": self.maximum,
            "mean": self.mean,
            "median": self.median,
            "variance": self.variance,
            "std": self.std,
            "q01": self.q01,
            "q05": self.q05,
            "q25": self.q25,
            "q50": self.q50,
            "q75": self.q75,
            "q95": self.q95,
            "q99": self.q99,
            "iqr": self.iqr,
            "mad": self.mad,
            "normalized_mad": self.normalized_mad,
            "skewness": self.skewness,
            "kurtosis": self.kurtosis,
            "zero_ratio": self.zero_ratio,
            "negative_ratio": self.negative_ratio,
            "coefficient_of_variation": self.coefficient_of_variation,
            "iqr_lower_fence": self.iqr_lower_fence,
            "iqr_upper_fence": self.iqr_upper_fence,
            "outlier_lower_n": self.outlier_lower_n,
            "outlier_upper_n": self.outlier_upper_n,
            "outlier_ratio": self.outlier_ratio,
            "robust_z_upper_n": self.robust_z_upper_n,
            "degenerate_iqr": self.degenerate_iqr,
            "method": self.method,
            "method_version": self.method_version,
            "warnings": list(self.warnings),
        }


def median_of(sorted_values: Sequence[float]) -> float:
    count = len(sorted_values)
    if count == 0:
        return math.nan
    middle = count // 2
    if count % 2:
        return sorted_values[middle]
    return (sorted_values[middle - 1] + sorted_values[middle]) / 2.0


def quantile_of(sorted_values: Sequence[float], probability: float) -> float:
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


def median_absolute_deviation(sorted_values: Sequence[float]) -> float:
    if not sorted_values:
        return 0.0
    median = median_of(sorted_values)
    deviations = sorted(abs(value - median) for value in sorted_values)
    return median_of(deviations)


def sample_skewness(values: Sequence[float]) -> float | None:
    count = len(values)
    if count < 3:
        return None
    mean = sum(values) / count
    variance = sum((value - mean) ** 2 for value in values) / (count - 1)
    if variance <= 0:
        return None
    sigma = math.sqrt(variance)
    return (
        sum(((value - mean) / sigma) ** 3 for value in values)
        * count
        / ((count - 1) * (count - 2))
    )


def sample_kurtosis(values: Sequence[float]) -> float | None:
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


def compute_robust_dispersion(
    values: Sequence[float], total_n: int | None = None
) -> RobustDispersion | None:
    parsed = [float(value) for value in values]
    if not parsed:
        return None
    total = total_n if total_n is not None else len(parsed)
    ordered = sorted(parsed)
    count = len(ordered)
    mean = sum(ordered) / count
    variance = (
        sum((value - mean) ** 2 for value in ordered) / (count - 1) if count > 1 else 0.0
    )
    std = math.sqrt(variance)
    median = median_of(ordered)
    q25 = quantile_of(ordered, 0.25)
    q75 = quantile_of(ordered, 0.75)
    iqr = q75 - q25
    mad = median_absolute_deviation(ordered)
    normalized_mad = mad * 1.4826
    zero_count = sum(1 for value in ordered if value == 0)
    negative_count = sum(1 for value in ordered if value < 0)
    degenerate = iqr <= 0
    lower_fence = q25 - IQR_MULTIPLIER * iqr
    upper_fence = q75 + IQR_MULTIPLIER * iqr
    lower_outliers = sum(1 for value in ordered if value < lower_fence)
    upper_outliers = sum(1 for value in ordered if value > upper_fence)
    outlier_total = lower_outliers + upper_outliers
    robust_z_count = 0
    if mad > 0:
        robust_z_count = sum(
            1
            for value in ordered
            if abs(ROBUST_Z_CONSTANT * (value - median) / mad) > 3.5
        )
    warnings: list[str] = []
    if count < 30:
        warnings.append("small_sample_for_shape_statistics")
    if degenerate:
        warnings.append("degenerate_iqr_zero_spread")
    if zero_count / count > 0.3:
        warnings.append("high_zero_inflation")
    if std == 0:
        warnings.append("constant_field")
    coefficient = None
    if abs(mean) > 1e-12:
        coefficient = std / abs(mean)
    return RobustDispersion(
        n_valid=count,
        n_total=total,
        n_missing=max(0, total - count),
        n_zero=zero_count,
        n_negative=negative_count,
        minimum=ordered[0],
        maximum=ordered[-1],
        mean=mean,
        median=median,
        variance=variance,
        std=std,
        q01=quantile_of(ordered, 0.01),
        q05=quantile_of(ordered, 0.05),
        q25=q25,
        q50=median,
        q75=q75,
        q95=quantile_of(ordered, 0.95),
        q99=quantile_of(ordered, 0.99),
        iqr=iqr,
        mad=mad,
        normalized_mad=normalized_mad,
        skewness=sample_skewness(ordered),
        kurtosis=sample_kurtosis(ordered),
        zero_ratio=zero_count / count,
        negative_ratio=negative_count / count,
        coefficient_of_variation=coefficient,
        iqr_lower_fence=lower_fence,
        iqr_upper_fence=upper_fence,
        outlier_lower_n=lower_outliers,
        outlier_upper_n=upper_outliers,
        outlier_ratio=outlier_total / count,
        robust_z_upper_n=robust_z_count,
        degenerate_iqr=degenerate,
        method="descriptive_full_population_robust",
        method_version=METHOD_VERSION,
        warnings=tuple(warnings),
    )


def quantile_profile(values: Sequence[float]) -> list[dict[str, Any]]:
    ordered = sorted(float(value) for value in values)
    return [
        {
            "percentile": round(level * 100.0, 4),
            "value": quantile_of(ordered, level),
        }
        for level in QUANTILE_LEVELS
    ]


def iqr_outlier_masks(
    values: Sequence[float], multiplier: float = IQR_MULTIPLIER
) -> tuple[float, float, list[bool], bool]:
    ordered = sorted(float(value) for value in values)
    if not ordered:
        return math.nan, math.nan, [], True
    q25 = quantile_of(ordered, 0.25)
    q75 = quantile_of(ordered, 0.75)
    iqr = q75 - q25
    if iqr <= 0:
        return q25, q75, [False] * len(ordered), True
    lower = q25 - multiplier * iqr
    upper = q75 + multiplier * iqr
    return lower, upper, [value < lower or value > upper for value in ordered], False


def robust_z_scores(
    values: Sequence[float], median: float, mad: float, threshold: float = 3.5
) -> list[float]:
    if mad <= 0:
        return [0.0] * len(values)
    return [
        ROBUST_Z_CONSTANT * (float(value) - median) / mad for value in values
    ]


def is_positive_only(values: Sequence[float]) -> bool:
    return all(float(value) > 0 for value in values) if values else False
