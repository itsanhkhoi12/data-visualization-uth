from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Any, Sequence

from statistics.robust_stats import quantile_of

METHOD_VERSION = "histogram_bins.v1"
MIN_BIN_COUNT = 5
MAX_BIN_COUNT = 60
FALLBACK_BIN_COUNTS = (10, 20, 30, 40, 50, 60)


@dataclass(frozen=True)
class BinPolicy:
    bin_count: int
    method: str
    edges: tuple[float, ...]
    counts: tuple[int, ...]
    included_n: int
    excluded_n: int
    degenerate: bool
    reason: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "bin_count": self.bin_count,
            "method": self.method,
            "edges": list(self.edges),
            "counts": list(self.counts),
            "included_n": self.included_n,
            "excluded_n": self.excluded_n,
            "degenerate": self.degenerate,
            "reason": self.reason,
        }

    @property
    def labels(self) -> tuple[str, ...]:
        if self.degenerate:
            return tuple(f"{edge:.6g}" for edge in self.edges[: len(self.counts)])
        return tuple(
            f"{self.edges[index]:.6g}–{self.edges[index + 1]:.6g}"
            for index in range(len(self.counts))
        )


def freedman_diaconis_width(values: Sequence[float]) -> float | None:
    count = len(values)
    if count < 2:
        return None
    ordered = sorted(float(value) for value in values)
    iqr = quantile_of(ordered, 0.75) - quantile_of(ordered, 0.25)
    if iqr <= 0:
        return None
    width = 2.0 * iqr * (count ** (-1.0 / 3.0))
    return width if width > 0 else None


def scott_width(values: Sequence[float]) -> float | None:
    count = len(values)
    if count < 2:
        return None
    ordered = sorted(float(value) for value in values)
    mean = sum(ordered) / count
    variance = sum((value - mean) ** 2 for value in ordered) / (count - 1)
    if variance <= 0:
        return None
    sigma = math.sqrt(variance)
    width = 3.49 * sigma * (count ** (-1.0 / 3.0))
    return width if width > 0 else None


def sturges_width(values: Sequence[float]) -> float | None:
    count = len(values)
    if count < 1:
        return None
    minimum = min(float(value) for value in values)
    maximum = max(float(value) for value in values)
    if maximum <= minimum:
        return None
    bins = max(1, int(math.ceil(math.log2(count) + 1)))
    return (maximum - minimum) / bins


def choose_bin_count(values: Sequence[float]) -> tuple[int, str]:
    count = len(values)
    if count < 2:
        return 1, "single_observation"
    minimum = min(float(value) for value in values)
    maximum = max(float(value) for value in values)
    if maximum <= minimum:
        return 1, "constant_series"
    for width_fn, label in (
        (freedman_diaconis_width, "freedman_diaconis"),
        (scott_width, "scott"),
        (sturges_width, "sturges"),
    ):
        width = width_fn(values)
        if width is None or width <= 0:
            continue
        candidate = int((maximum - minimum) / width)
        if MIN_BIN_COUNT <= candidate <= MAX_BIN_COUNT:
            return candidate, label
    return FALLBACK_BIN_COUNTS[1], "fallback_equal_width"


def build_bins(values: Sequence[float], bin_count: int | None = None) -> BinPolicy:
    parsed = [float(value) for value in values]
    if not parsed:
        return BinPolicy(
            bin_count=0,
            method="no_values",
            edges=(),
            counts=(),
            included_n=0,
            excluded_n=0,
            degenerate=True,
            reason="no_numeric_values",
        )
    minimum = min(parsed)
    maximum = max(parsed)
    if minimum == maximum:
        return BinPolicy(
            bin_count=1,
            method="constant_series",
            edges=(minimum, maximum),
            counts=(len(parsed),),
            included_n=len(parsed),
            excluded_n=0,
            degenerate=True,
            reason="all_observations_share_one_value",
        )
    if bin_count is None:
        resolved_count, method = choose_bin_count(parsed)
    else:
        resolved_count = max(1, int(bin_count))
        method = "explicit_bin_count"
    width = (maximum - minimum) / resolved_count
    counts = [0] * resolved_count
    for value in parsed:
        index = int((value - minimum) / width)
        if index >= resolved_count:
            index = resolved_count - 1
        if index < 0:
            index = 0
        counts[index] += 1
    edges = tuple(minimum + index * width for index in range(resolved_count + 1))
    return BinPolicy(
        bin_count=resolved_count,
        method=method,
        edges=edges,
        counts=tuple(counts),
        included_n=len(parsed),
        excluded_n=0,
        degenerate=False,
        reason="",
    )


def ecdf_series(values: Sequence[float]) -> tuple[list[float], list[float]]:
    ordered = sorted(float(value) for value in values)
    count = len(ordered)
    xs: list[float] = []
    ys: list[float] = []
    for index, value in enumerate(ordered, start=1):
        xs.append(value)
        ys.append(index / count if count else 0.0)
    return xs, ys


def kde_series(
    values: Sequence[float], bandwidth: float | None = None, grid_size: int = 200
) -> tuple[list[float], list[float], float]:
    parsed = [float(value) for value in values]
    if len(parsed) < 3:
        return [], [], 0.0
    ordered = sorted(parsed)
    count = len(ordered)
    mean = sum(ordered) / count
    variance = sum((value - mean) ** 2 for value in ordered) / (count - 1)
    sigma = math.sqrt(variance)
    if bandwidth is None:
        if sigma <= 0:
            return [], [], 0.0
        bandwidth = 1.06 * sigma * count ** (-0.2)
    if bandwidth <= 0:
        return [], [], 0.0
    lower = ordered[0] - 3.0 * bandwidth
    upper = ordered[-1] + 3.0 * bandwidth
    step = (upper - lower) / max(grid_size - 1, 1)
    xs: list[float] = []
    ys: list[float] = []
    normalization = 1.0 / (count * bandwidth * math.sqrt(2.0 * math.pi))
    for index in range(grid_size):
        position = lower + index * step
        density = sum(
            math.exp(-0.5 * ((position - value) / bandwidth) ** 2)
            for value in ordered
        )
        xs.append(position)
        ys.append(density * normalization)
    return xs, ys, bandwidth
