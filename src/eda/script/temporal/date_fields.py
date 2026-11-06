from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime
from typing import Any, Sequence

from schema.type_inference import is_blank, parse_date, parse_datetime

DATE_ROLE_TOKENS = {
    "order": ("ngày đặt", "ngay dat", "ngày đơn", "date order", "ngày tạo", "thời gian tạo"),
    "payment": ("ngày trả", "ngay tra", "thời gian trả", "ngày thu", "payment date"),
    "delivery": ("ngày giao", "ngay giao", "delivery date"),
    "return": ("ngày trả hàng", "ngay tra hang", "return date"),
    "expiry": ("hạn sử dụng", "han su dung", "hạn dùng", "expiry"),
    "created": ("ngày đăng ký", "ngay dang ky", "created"),
}


@dataclass(frozen=True)
class DateFieldProfile:
    source_id: str
    split: str
    business_id: str
    object_name: str
    column: str
    event_role: str
    total_n: int
    valid_n: int
    parse_failure_n: int
    min_date: str | None
    max_date: str | None
    distinct_dates: int
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
            "total_n": self.total_n,
            "valid_n": self.valid_n,
            "parse_failure_n": self.parse_failure_n,
            "min_date": self.min_date,
            "max_date": self.max_date,
            "distinct_dates": self.distinct_dates,
            "status": self.status,
            "notes": list(self.notes),
        }


def detect_event_role(column: str) -> str:
    lowered = column.lower()
    for role, tokens in DATE_ROLE_TOKENS.items():
        for token in tokens:
            if token in lowered:
                return role
    return "unknown"


def profile_date_fields(
    source_id: str,
    split: str,
    business_id: str,
    object_name: str,
    rows: Sequence[dict[str, Any]],
    date_columns: Sequence[str],
    total_n: int,
) -> tuple[DateFieldProfile, ...]:
    profiles: list[DateFieldProfile] = []
    for column in date_columns:
        valid: list[date] = []
        failures = 0
        for row in rows:
            value = row.get(column)
            if is_blank(value):
                continue
            parsed = parse_date(value) or _datetime_to_date(parse_datetime(value))
            if parsed is None:
                failures += 1
                continue
            valid.append(parsed)
        notes: list[str] = []
        status = "PASS"
        if not valid:
            status = "BLOCKED"
            notes.append("no_parseable_dates")
        elif failures:
            status = "PARTIAL"
            notes.append("parse_failures_present")
        profiles.append(
            DateFieldProfile(
                source_id=source_id,
                split=split,
                business_id=business_id,
                object_name=object_name,
                column=column,
                event_role=detect_event_role(column),
                total_n=total_n,
                valid_n=len(valid),
                parse_failure_n=failures,
                min_date=min(valid).isoformat() if valid else None,
                max_date=max(valid).isoformat() if valid else None,
                distinct_dates=len(set(valid)),
                status=status,
                notes=tuple(notes),
            )
        )
    return tuple(profiles)


def _datetime_to_date(value: datetime | None) -> date | None:
    if value is None:
        return None
    return value.date()


def month_key(value: date) -> str:
    return f"{value.year:04d}-{value.month:02d}"


def missing_periods(
    observed: Sequence[date], start: date, end: date
) -> tuple[str, ...]:
    if not observed:
        return ()
    months = {month_key(value) for value in observed}
    cursor = date(start.year, start.month, 1)
    gaps: list[str] = []
    while cursor <= end:
        key = month_key(cursor)
        if key not in months:
            gaps.append(key)
        if cursor.month == 12:
            cursor = date(cursor.year + 1, 1, 1)
        else:
            cursor = date(cursor.year, cursor.month + 1, 1)
    return tuple(gaps)
