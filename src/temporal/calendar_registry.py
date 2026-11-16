from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Sequence

from readers.csv_reader import read_all_csv_rows

REQUIRED_CALENDAR_COLUMNS = (
    "date",
    "weekday",
    "lunar_day",
    "lunar_month",
    "lunar_year",
    "lunar_leap",
    "holiday",
)


@dataclass(frozen=True)
class CalendarRegistry:
    split: str
    path: Path
    row_count: int
    min_date: str
    max_date: str
    columns: tuple[str, ...]
    missing_columns: tuple[str, ...]
    duplicate_date_count: int
    weekday_distribution: dict[str, int]
    leap_month_days: int
    tet_windows: tuple[tuple[str, str], ...]
    status: str
    warnings: tuple[str, ...]

    def to_dict(self) -> dict[str, Any]:
        return {
            "split": self.split,
            "path": str(self.path),
            "row_count": self.row_count,
            "min_date": self.min_date,
            "max_date": self.max_date,
            "columns": list(self.columns),
            "missing_columns": list(self.missing_columns),
            "duplicate_date_count": self.duplicate_date_count,
            "weekday_distribution": dict(self.weekday_distribution),
            "leap_month_days": self.leap_month_days,
            "tet_windows": [list(window) for window in self.tet_windows],
            "status": self.status,
            "warnings": list(self.warnings),
        }

    def date_index(self) -> dict[str, dict[str, Any]]:
        header, rows = read_all_csv_rows(self.path)
        del header
        return {row["date"]: row for row in rows}


def validate_calendar(path: Path, split: str) -> CalendarRegistry:
    header, rows = read_all_csv_rows(path)
    columns = tuple(header)
    missing = tuple(name for name in REQUIRED_CALENDAR_COLUMNS if name not in columns)
    warnings: list[str] = []
    dates = [row.get("date", "") for row in rows]
    duplicate_dates = len(dates) - len(set(dates))
    if duplicate_dates:
        warnings.append("duplicate_calendar_dates")
    if missing:
        warnings.append("missing_calendar_columns")
    weekday_distribution: dict[str, int] = {}
    for row in rows:
        weekday = row.get("weekday", "")
        weekday_distribution[weekday] = weekday_distribution.get(weekday, 0) + 1
    leap_month_days = sum(
        1 for row in rows if str(row.get("lunar_leap", "")).strip().lower() == "true"
    )
    tet_windows = _find_tet_windows(rows)
    status = "PASS" if not missing and not duplicate_dates else "PARTIAL"
    return CalendarRegistry(
        split=split,
        path=path,
        row_count=len(rows),
        min_date=min(dates) if dates else "",
        max_date=max(dates) if dates else "",
        columns=columns,
        missing_columns=missing,
        duplicate_date_count=duplicate_dates,
        weekday_distribution=weekday_distribution,
        leap_month_days=leap_month_days,
        tet_windows=tet_windows,
        status=status,
        warnings=tuple(warnings),
    )


def _find_tet_windows(rows: Sequence[dict[str, Any]]) -> tuple[tuple[str, str], ...]:
    starts: dict[int, str] = {}
    ends: dict[int, str] = {}
    for row in rows:
        try:
            lunar_month = int(row.get("lunar_month", "") or 0)
            lunar_day = int(row.get("lunar_day", "") or 0)
            lunar_year = int(row.get("lunar_year", "") or 0)
        except ValueError:
            continue
        is_leap = str(row.get("lunar_leap", "")).strip().lower() == "true"
        if is_leap:
            continue
        if lunar_month == 12 and lunar_day == 23:
            starts[lunar_year + 1] = row.get("date", "")
        if lunar_month == 1 and lunar_day == 10:
            ends[lunar_year] = row.get("date", "")
    windows: list[tuple[str, str]] = []
    for lunar_year in sorted(set(starts) & set(ends)):
        windows.append((starts[lunar_year], ends[lunar_year]))
    return tuple(windows)
