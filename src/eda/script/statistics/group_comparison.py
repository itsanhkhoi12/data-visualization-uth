from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Sequence

from statistics.robust_stats import median_of, quantile_of

METHOD_VERSION = "group_comparison.v1"
MIN_GROUP_N = 5


@dataclass(frozen=True)
class GroupSummary:
    group: str
    n: int
    minimum: float
    maximum: float
    mean: float
    median: float
    q25: float
    q75: float
    iqr: float
    std: float
    zero_count: int
    negative_count: int

    def to_dict(self) -> dict[str, Any]:
        return {
            "group": self.group,
            "n": self.n,
            "minimum": self.minimum,
            "maximum": self.maximum,
            "mean": self.mean,
            "median": self.median,
            "q25": self.q25,
            "q75": self.q75,
            "iqr": self.iqr,
            "std": self.std,
            "zero_count": self.zero_count,
            "negative_count": self.negative_count,
        }


@dataclass(frozen=True)
class GroupComparison:
    group_field: str
    value_field: str
    groups: tuple[GroupSummary, ...]
    total_n: int
    dropped_n: int
    excluded_small_groups: tuple[str, ...]
    method: str
    method_version: str
    notes: tuple[str, ...] = ()

    def to_dict(self) -> dict[str, Any]:
        return {
            "group_field": self.group_field,
            "value_field": self.value_field,
            "groups": [group.to_dict() for group in self.groups],
            "total_n": self.total_n,
            "dropped_n": self.dropped_n,
            "excluded_small_groups": list(self.excluded_small_groups),
            "method": self.method,
            "method_version": self.method_version,
            "notes": list(self.notes),
        }


def group_value_buckets(
    rows: Sequence[dict[str, Any]],
    group_field: str,
    value_field: str,
    parse: Any,
    min_group_n: int = MIN_GROUP_N,
    max_groups: int = 12,
) -> tuple[tuple[str, ...], tuple[tuple[float, ...], ...], int, int]:
    buckets: dict[str, list[float]] = {}
    dropped = 0
    for row in rows:
        raw_group = row.get(group_field)
        if raw_group is None or not str(raw_group).strip():
            dropped += 1
            continue
        number = parse(row.get(value_field))
        if number is None:
            dropped += 1
            continue
        buckets.setdefault(str(raw_group).strip(), []).append(float(number))
    eligible = sorted(
        group for group in buckets if len(buckets[group]) >= min_group_n
    )[:max_groups]
    labels = tuple(eligible)
    values = tuple(tuple(buckets[group]) for group in eligible)
    total_n = sum(len(bucket) for bucket in buckets.values())
    return labels, values, total_n, dropped


def compare_groups(
    rows: Sequence[dict[str, Any]],
    group_field: str,
    value_field: str,
    parse: Any,
    min_group_n: int = MIN_GROUP_N,
    max_groups: int = 12,
) -> GroupComparison:
    buckets: dict[str, list[float]] = {}
    dropped = 0
    for row in rows:
        raw_group = row.get(group_field)
        if raw_group is None or not str(raw_group).strip():
            dropped += 1
            continue
        number = parse(row.get(value_field))
        if number is None:
            dropped += 1
            continue
        buckets.setdefault(str(raw_group).strip(), []).append(float(number))
    notes: list[str] = []
    excluded: list[str] = []
    summaries: list[GroupSummary] = []
    for group in sorted(buckets):
        values = buckets[group]
        if len(values) < min_group_n:
            excluded.append(group)
            continue
        summaries.append(_summarize(group, values))
    if excluded:
        notes.append(f"groups_below_minimum_n_excluded:{len(excluded)}")
    if len(summaries) > max_groups:
        notes.append(f"groups_truncated_to_{max_groups}")
        summaries = summaries[:max_groups]
    return GroupComparison(
        group_field=group_field,
        value_field=value_field,
        groups=tuple(summaries),
        total_n=sum(len(bucket) for bucket in buckets.values()),
        dropped_n=dropped,
        excluded_small_groups=tuple(excluded),
        method="group_quantile_summary_full_population",
        method_version=METHOD_VERSION,
        notes=tuple(notes),
    )


def _summarize(group: str, values: Sequence[float]) -> GroupSummary:
    ordered = sorted(values)
    count = len(ordered)
    mean = sum(ordered) / count
    variance = sum((value - mean) ** 2 for value in ordered) / (count - 1)
    q25 = quantile_of(ordered, 0.25)
    q75 = quantile_of(ordered, 0.75)
    return GroupSummary(
        group=group,
        n=count,
        minimum=ordered[0],
        maximum=ordered[-1],
        mean=round(mean, 6),
        median=round(median_of(ordered), 6),
        q25=round(q25, 6),
        q75=round(q75, 6),
        iqr=round(q75 - q25, 6),
        std=round(variance**0.5, 6),
        zero_count=sum(1 for value in ordered if value == 0),
        negative_count=sum(1 for value in ordered if value < 0),
    )
