from __future__ import annotations

from datetime import date
from pathlib import Path

from rulebook.rule_registry import compile_rule_registry
from temporal.calendar_registry import validate_calendar
from temporal.coverage import (
    daily_counts_from_dates,
    profile_time_coverage,
    weekday_counts_from_dates,
)
from temporal.date_fields import detect_event_role, missing_periods, profile_date_fields


def _rulebook(path: Path, body: str) -> None:
    path.write_text(body, encoding="utf-8")


def test_rule_registry_ids_are_split_scoped(tmp_path: Path) -> None:
    path = tmp_path / "rulebook.md"
    _rulebook(
        path,
        "# Rules\n\n## Revenue\n\n| Rule | Description |\n|---|---|\n"
        "| R-01 | Revenue sums line totals |\n",
    )
    registry = compile_rule_registry(path, "public_test", "hash")
    assert registry.rules[0].rule_id.startswith("public_test.")
    assert registry.rule_by_id(registry.rules[0].rule_id) is not None


def _calendar(path: Path) -> Path:
    lines = ["date,weekday,lunar_day,lunar_month,lunar_year,lunar_leap,holiday"]
    for offset in range(0, 60):
        current = date(2025, 1, 1).toordinal() + offset
        converted = date.fromordinal(current)
        lines.append(
            f"{converted.isoformat()},2,1,1,2025,false,false"
        )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return path


def test_t034_calendar_registry_validates(tmp_path: Path) -> None:
    path = _calendar(tmp_path / "calendar.csv")
    registry = validate_calendar(path, "public_test")
    assert registry.row_count == 60
    assert registry.min_date == "2025-01-01"
    assert registry.status in {"PASS", "PARTIAL"}


def test_t033_missing_months_are_detected() -> None:
    observed = [date(2025, 1, 5), date(2025, 4, 5)]
    gaps = missing_periods(observed, date(2025, 1, 1), date(2025, 4, 30))
    assert "2025-02" in gaps
    assert "2025-03" in gaps
    assert "2025-01" not in gaps


def test_event_role_detection() -> None:
    assert detect_event_role("Ngày đặt hàng") == "order"
    assert detect_event_role("Hạn sử dụng") == "expiry"
    assert detect_event_role("Khác") == "unknown"


def test_date_field_profile_reports_parse_failures() -> None:
    rows = [{"ngày đặt": "2025-01-01"}, {"ngày đặt": "not a date"}]
    profiles = profile_date_fields(
        "public_test:biz_x:orders",
        "public_test",
        "biz_x",
        "orders",
        rows,
        ["ngày đặt"],
        2,
    )
    assert profiles[0].valid_n == 1
    assert profiles[0].parse_failure_n == 1
    assert profiles[0].status == "PARTIAL"


def test_time_coverage_counts_active_days() -> None:
    rows = [{"ngày đặt": "2025-01-01"}, {"ngày đặt": "2025-01-01"}]
    profiles = profile_date_fields(
        "public_test:biz_x:orders",
        "public_test",
        "biz_x",
        "orders",
        rows,
        ["ngày đặt"],
        2,
    )
    dates = [date(2025, 1, 1), date(2025, 1, 1)]
    coverage = profile_time_coverage(
        profiles[0],
        daily_counts_from_dates(dates),
        weekday_counts_from_dates(dates),
    )
    assert coverage.active_days == 1
    assert coverage.span_days == 1
