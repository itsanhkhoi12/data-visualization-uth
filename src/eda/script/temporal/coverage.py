from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import Any, Sequence

from temporal.date_fields import DateFieldProfile, missing_periods, month_key


@dataclass(frozen=True)
class TemporalCoverage:
    source_id: str
    split: str
    business_id: str
    object_name: str
    column: str
    event_role: str
    min_date: str | None
    max_date: str | None
    active_days: int
    span_days: int
    coverage_ratio: float
    missing_months: tuple[str, ...]
    daily_counts: dict[str, int]
    weekday_counts: dict[str, int]
    status: str
    notes: tuple[str, ...] = ()

    def to_dict(self) -> dict[str, Any]:
        return {
            "source_id": self.source_id,
            "split": self.split,
            "business_id": self.business_id,
            "object_name": self.object_name,
            "column": self.column,
            "event_role": self.event_role,
            "min_date": self.min_date,
            "max_date": self.max_date,
            "active_days": self.active_days,
            "span_days": self.span_days,
            "coverage_ratio": self.coverage_ratio,
            "missing_months": list(self.missing_months),
            "weekday_counts": dict(self.weekday_counts),
            "status": self.status,
            "notes": list(self.notes),
        }


def profile_time_coverage(
    profile: DateFieldProfile,
    daily_counts: dict[str, int],
    weekday_counts: dict[str, int],
    calendar_start: date | None = None,
    calendar_end: date | None = None,
) -> TemporalCoverage:
    notes: list[str] = []
    if profile.min_date is None or profile.max_date is None:
        return TemporalCoverage(
            source_id=profile.source_id,
            split=profile.split,
            business_id=profile.business_id,
            object_name=profile.object_name,
            column=profile.column,
            event_role=profile.event_role,
            min_date=None,
            max_date=None,
            active_days=0,
            span_days=0,
            coverage_ratio=0.0,
            missing_months=(),
            daily_counts={},
            weekday_counts={},
            status="BLOCKED",
            notes=("no_valid_date_range",),
        )
    start = date.fromisoformat(profile.min_date)
    end = date.fromisoformat(profile.max_date)
    span_days = (end - start).days + 1
    coverage_ratio = round(len(daily_counts) / span_days, 6) if span_days > 0 else 0.0
    gaps = missing_periods(
        [date.fromisoformat(key) for key in daily_counts], start, end
    )
    if gaps:
        notes.append("months_without_observed_events")
    if calendar_start and start < calendar_start:
        notes.append("events_before_calendar_coverage")
    if calendar_end and end > calendar_end:
        notes.append("events_after_calendar_coverage")
    return TemporalCoverage(
        source_id=profile.source_id,
        split=profile.split,
        business_id=profile.business_id,
        object_name=profile.object_name,
        column=profile.column,
        event_role=profile.event_role,
        min_date=profile.min_date,
        max_date=profile.max_date,
        active_days=len(daily_counts),
        span_days=span_days,
        coverage_ratio=coverage_ratio,
        missing_months=gaps,
        daily_counts=daily_counts,
        weekday_counts=weekday_counts,
        status="PASS" if not gaps else "PARTIAL",
        notes=tuple(notes),
    )


def daily_counts_from_dates(dates: Sequence[date]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for value in dates:
        key = value.isoformat()
        counts[key] = counts.get(key, 0) + 1
    return counts


def weekday_counts_from_dates(dates: Sequence[date]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for value in dates:
        key = str(value.isoweekday())
        counts[key] = counts.get(key, 0) + 1
    return counts


def monthly_counts_from_dates(dates: Sequence[date]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for value in dates:
        key = month_key(value)
        counts[key] = counts.get(key, 0) + 1
    return counts
