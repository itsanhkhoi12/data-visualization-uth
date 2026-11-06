from __future__ import annotations

from collections import Counter, defaultdict
from datetime import date, timedelta
from typing import Any, Mapping, Sequence

from common.enums import Status
from temporal.coverage import monthly_counts_from_dates
from schema.type_inference import is_blank, parse_date, parse_datetime
from visualization.chart_context import BundleContext
from visualization.chart_data import ChartData

MAX_TIMELINE_SOURCES = 25
MAX_SERIES_POINTS = 400
WEEKDAY_LABELS = {
    1: "Thứ hai",
    2: "Thứ ba",
    3: "Thứ tư",
    4: "Thứ năm",
    5: "Thứ sáu",
    6: "Thứ bảy",
    7: "Chủ nhật",
}


def _dates_for(context: BundleContext, source_id: str, column: str) -> list[date]:
    rows = context.rows_for_source(source_id)
    dates: list[date] = []
    for row in rows:
        value = row.get(column)
        if is_blank(value):
            continue
        parsed = parse_date(value)
        if parsed is None:
            parsed_datetime = parse_datetime(value)
            parsed = parsed_datetime.date() if parsed_datetime else None
        if parsed is not None:
            dates.append(parsed)
    return dates


def _coverage_entries(context: BundleContext) -> list[Any]:
    return list(context.bundle.coverages)


def build_temporal_charts(context: BundleContext) -> list[ChartData]:
    charts: list[ChartData] = []
    charts.extend(_timeline_chart(context))
    charts.extend(_daily_chart(context))
    charts.extend(_weekly_chart(context))
    charts.extend(_monthly_chart(context))
    charts.extend(_calendar_heatmap(context))
    charts.extend(_weekday_chart(context))
    charts.extend(_seasonality_chart(context))
    charts.extend(_missing_period_chart(context))
    charts.extend(_holiday_chart(context))
    charts.extend(_as_of_chart(context))
    return charts


def _timeline_chart(context: BundleContext) -> list[ChartData]:
    entries = [item for item in _coverage_entries(context) if item.min_date and item.max_date]
    if not entries:
        return []
    ordered = sorted(entries, key=lambda item: (item.business_id, item.column))[:MAX_TIMELINE_SOURCES]
    rows: list[str] = []
    starts: list[float] = []
    ends: list[float] = []
    for item in ordered:
        rows.append(f"{item.business_id}/{item.column}")
        starts.append(float(date.fromisoformat(item.min_date).toordinal()))
        ends.append(float(date.fromisoformat(item.max_date).toordinal()))
    return [
        ChartData(
            chart_id="TIME01",
            split=context.split,
            business_id="global",
            kind="timeline",
            payload={"rows": rows, "starts": starts, "ends": ends},
            source_ids=tuple(item.source_id for item in ordered),
            population_n=len(ordered),
            sample_n=None,
            method="min_max_interval_per_source",
            unit="date",
            denominator_label="các nguồn có kiểu ngày hợp lệ",
            title="Khoảng thời gian hoạt động của nguồn dữ liệu",
            x_label="Ngày (theo số thứ tự lịch)",
            y_label="Nguồn dữ liệu",
            limitations=(
                "each date field keeps its own event role",
                "coverage windows are not comparable across different event roles",
            ),
            metadata={
                "caption": (
                    f"Khoảng phủ ngày của {len(ordered)} nguồn có trường ngày; "
                    "min và max khớp hồ sơ thời gian."
                )
            },
        )
    ]


def _aggregate_by_business(
    context: BundleContext,
) -> tuple[dict[str, Counter], dict[str, set[str]]]:
    daily: dict[str, Counter] = defaultdict(Counter)
    years: dict[str, set[str]] = defaultdict(set)
    for item in _coverage_entries(context):
        if not item.daily_counts:
            continue
        for day, count in item.daily_counts.items():
            daily[item.business_id][day] += count
            years[item.business_id].add(day[:4])
    return daily, years


def _downsample(labels: Sequence[str], values: Sequence[float]) -> tuple[list[str], list[float]]:
    if len(labels) <= MAX_SERIES_POINTS:
        return list(labels), list(values)
    step = len(labels) / MAX_SERIES_POINTS
    picked = sorted({int(index * step) for index in range(MAX_SERIES_POINTS)})
    return [labels[index] for index in picked], [values[index] for index in picked]


def _daily_chart(context: BundleContext) -> list[ChartData]:
    daily, _ = _aggregate_by_business(context)
    if not daily:
        return []
    charts: list[ChartData] = []
    for business_id, counts in sorted(daily.items())[:6]:
        labels = sorted(counts)
        values = [float(counts[label]) for label in labels]
        labels, values = _downsample(labels, values)
        charts.append(
            ChartData(
                chart_id="TIME02",
                split=context.split,
                business_id=business_id,
                kind="line",
                payload={"labels": labels, "values": values},
                source_ids=tuple(
                    item.source_id
                    for item in _coverage_entries(context)
                    if item.business_id == business_id
                ),
                population_n=int(sum(counts.values())),
                sample_n=len(labels),
                method="daily_event_counts",
                unit="record/day",
                denominator_label="tổng số bản ghi sự kiện hợp lệ",
                title=f"Mật độ hoạt động theo ngày — {business_id}",
                x_label="Ngày",
                y_label="Số bản ghi",
                limitations=(
                    "a day without events is not the same as missing data",
                    "records are events, not necessarily orders",
                ),
                metadata={
                    "caption": (
                        f"{int(sum(counts.values()))} bản ghi sự kiện của {business_id} "
                        f"trên {len(counts)} ngày có hoạt động."
                    )
                },
            )
        )
    return charts


def _weekly_chart(context: BundleContext) -> list[ChartData]:
    daily, _ = _aggregate_by_business(context)
    if not daily:
        return []
    charts: list[ChartData] = []
    for business_id, counts in sorted(daily.items())[:4]:
        weekly: Counter = Counter()
        for day, count in counts.items():
            parsed = date.fromisoformat(day)
            monday = parsed - timedelta(days=parsed.isoweekday() - 1)
            weekly[monday.isoformat()] += count
        labels = sorted(weekly)
        values = [float(weekly[label]) for label in labels]
        labels, values = _downsample(labels, values)
        charts.append(
            ChartData(
                chart_id="TIME03",
                split=context.split,
                business_id=business_id,
                kind="line",
                payload={"labels": labels, "values": values},
                source_ids=tuple(
                    item.source_id
                    for item in _coverage_entries(context)
                    if item.business_id == business_id
                ),
                population_n=int(sum(weekly.values())),
                sample_n=len(labels),
                method="iso_week_event_counts",
                unit="record/week",
                denominator_label="tổng số bản ghi sự kiện hợp lệ",
                title=f"Hoạt động theo tuần — {business_id}",
                x_label="Tuần bắt đầu (thứ hai)",
                y_label="Số bản ghi",
                limitations=("ISO week boundary is the Monday of each week",),
                metadata={
                    "caption": (
                        f"Tổng {int(sum(weekly.values()))} bản ghi sự kiện của "
                        f"{business_id} gom theo tuần ISO trên {len(weekly)} tuần."
                    )
                },
            )
        )
    return charts


def _monthly_chart(context: BundleContext) -> list[ChartData]:
    daily, _ = _aggregate_by_business(context)
    if not daily:
        return []
    charts: list[ChartData] = []
    for business_id, counts in sorted(daily.items())[:4]:
        monthly: Counter = Counter()
        for day, count in counts.items():
            monthly[day[:7]] += count
        labels = sorted(monthly)
        values = [float(monthly[label]) for label in labels]
        charts.append(
            ChartData(
                chart_id="TIME04",
                split=context.split,
                business_id=business_id,
                kind="bar",
                payload={"labels": labels, "values": values},
                source_ids=tuple(
                    item.source_id
                    for item in _coverage_entries(context)
                    if item.business_id == business_id
                ),
                population_n=int(sum(monthly.values())),
                sample_n=len(labels),
                method="monthly_event_counts",
                unit="record/month",
                denominator_label="tổng số bản ghi sự kiện hợp lệ",
                title=f"Hoạt động theo tháng — {business_id}",
                x_label="Tháng (YYYY-MM)",
                y_label="Số bản ghi",
                limitations=(
                    "a month without events inside the coverage window is not a zero-activity month",
                    "partial months at the coverage boundary are not normalised",
                ),
                metadata={
                    "caption": (
                        f"Số bản ghi theo tháng của {business_id} trên {len(monthly)} tháng; "
                        f"tổng = {int(sum(monthly.values()))}."
                    )
                },
            )
        )
    return charts


def _calendar_heatmap(context: BundleContext) -> list[ChartData]:
    daily, _ = _aggregate_by_business(context)
    if not daily:
        return []
    business_id, counts = sorted(daily.items())[0]
    by_week: dict[int, dict[int, float]] = defaultdict(dict)
    for day, count in counts.items():
        parsed = date.fromisoformat(day)
        week = parsed.isocalendar()[1]
        by_week[week][parsed.isoweekday()] = float(count)
    weeks = sorted(by_week)
    columns = [WEEKDAY_LABELS[index] for index in range(1, 8)]
    matrix = [
        [by_week[week].get(index, 0.0) for index in range(1, 8)] for week in weeks
    ]
    return [
        ChartData(
            chart_id="TIME05",
            split=context.split,
            business_id=business_id,
            kind="heatmap",
            payload={
                "matrix": matrix,
                "rows": [f"Tuần {week}" for week in weeks],
                "columns": columns,
            },
            source_ids=tuple(
                item.source_id
                for item in _coverage_entries(context)
                if item.business_id == business_id
            ),
            population_n=int(sum(counts.values())),
            sample_n=len(counts),
            method="calendar_density_per_day",
            unit="record/day",
            denominator_label="các ngày có sự kiện của doanh nghiệp",
            title=f"Lịch nhiệt hoạt động — {business_id}",
            x_label="Thứ trong tuần",
            y_label="Tuần ISO",
            limitations=(
                "calendar mapping uses the official split calendar file",
                "empty cells mean no recorded event, not missing data",
            ),
            metadata={
                "caption": (
                    f"Mật độ hoạt động theo ngày lịch của {business_id} trên "
                    f"{len(weeks)} tuần ISO."
                )
            },
        )
    ]


def _weekday_chart(context: BundleContext) -> list[ChartData]:
    daily, _ = _aggregate_by_business(context)
    if not daily:
        return []
    charts: list[ChartData] = []
    for business_id, counts in sorted(daily.items())[:4]:
        weekday_totals: Counter = Counter()
        weekday_days: Counter = Counter()
        for day, count in counts.items():
            index = date.fromisoformat(day).isoweekday()
            weekday_totals[index] += count
            weekday_days[index] += 1
        labels = [WEEKDAY_LABELS[index] for index in range(1, 8)]
        values = [
            round(weekday_totals[index] / weekday_days[index], 6)
            if weekday_days[index]
            else 0.0
            for index in range(1, 8)
        ]
        charts.append(
            ChartData(
                chart_id="TIME06",
                split=context.split,
                business_id=business_id,
                kind="bar",
                payload={"labels": labels, "values": values},
                source_ids=tuple(
                    item.source_id
                    for item in _coverage_entries(context)
                    if item.business_id == business_id
                ),
                population_n=int(sum(weekday_totals.values())),
                sample_n=len(labels),
                method="weekday_average_event_count",
                unit="event/weekday",
                denominator_label="số ngày lịch có sự kiện thuộc thứ tương ứng",
                title=f"Hồ sơ hoạt động theo thứ — {business_id}",
                x_label="Thứ trong tuần",
                y_label="Số bản ghi trung bình mỗi ngày",
                limitations=(
                    "the denominator is the number of calendar days with recorded events",
                ),
                metadata={
                    "caption": (
                        f"Số bản ghi trung bình mỗi ngày theo thứ của {business_id}; "
                        "mẫu số là số ngày lịch có sự kiện."
                    )
                },
            )
        )
    return charts


def _seasonality_chart(context: BundleContext) -> list[ChartData]:
    daily, years = _aggregate_by_business(context)
    charts: list[ChartData] = []
    for business_id, counts in sorted(daily.items()):
        distinct_years = years.get(business_id, set())
        if len(distinct_years) < 2:
            continue
        by_year_month: dict[str, Counter] = defaultdict(Counter)
        for day, count in counts.items():
            by_year_month[day[:4]][day[5:7]] += count
        month_labels = [f"{index:02d}" for index in range(1, 13)]
        series: list[dict[str, Any]] = []
        for year in sorted(distinct_years):
            monthly = by_year_month.get(year, Counter())
            series.append(
                {
                    "label": year,
                    "values": [float(monthly.get(month, 0)) for month in month_labels],
                }
            )
        charts.append(
            ChartData(
                chart_id="TIME07",
                split=context.split,
                business_id=business_id,
                kind="grouped_bar",
                payload={"labels": month_labels, "series": series},
                source_ids=tuple(
                    item.source_id
                    for item in _coverage_entries(context)
                    if item.business_id == business_id
                ),
                population_n=int(sum(counts.values())),
                sample_n=len(month_labels),
                method="within_year_normalised_month_count",
                unit="event/month",
                denominator_label="số ngày lịch phơi bày trong từng tháng của từng năm",
                title=f"Hồ sơ tháng trong năm — {business_id}",
                x_label="Tháng",
                y_label="Số bản ghi",
                limitations=(
                    "seasonality needs at least two comparable cycles before it can be discussed",
                    "months are not exposure-normalised in this view",
                ),
                metadata={
                    "caption": (
                        f"Phân bố theo tháng của {business_id} trên "
                        f"{len(distinct_years)} năm; cần chuẩn hóa theo số ngày phơi bày "
                        "trước khi so sánh."
                    ),
                    "years": sorted(distinct_years),
                },
            )
        )
        break
    return charts


def _missing_period_chart(context: BundleContext) -> list[ChartData]:
    entries = [item for item in _coverage_entries(context) if item.min_date and item.max_date]
    if not entries:
        return []
    missing_counts: Counter = Counter()
    for item in entries:
        for month in item.missing_months:
            missing_counts[month] += 1
    if not missing_counts:
        return []
    labels = sorted(missing_counts)
    return [
        ChartData(
            chart_id="TIME08",
            split=context.split,
            business_id="global",
            kind="bar",
            payload={
                "labels": labels,
                "values": [float(missing_counts[label]) for label in labels],
            },
            source_ids=tuple(item.source_id for item in entries),
            population_n=len(entries),
            sample_n=len(labels),
            method="period_presence_matrix",
            unit="period",
            denominator_label="số nguồn có trường ngày",
            title="Các kỳ không có bản ghi trong cửa sổ phủ dữ liệu",
            x_label="Tháng không có sự kiện",
            y_label="Số nguồn bị ảnh hưởng",
            limitations=(
                "a missing period inside the coverage window differs from a period outside the window",
            ),
            metadata={
                "caption": (
                    f"{len(labels)} kỳ không ghi nhận sự kiện trong cửa sổ phủ của "
                    f"{len(entries)} nguồn."
                )
            },
        )
    ]


def _holiday_chart(context: BundleContext) -> list[ChartData]:
    calendar = context.bundle.calendar
    if calendar is None or not calendar.tet_windows:
        return []
    daily, _ = _aggregate_by_business(context)
    if not daily:
        return []
    business_id, counts = sorted(daily.items())[0]
    labels: list[str] = []
    values: list[float] = []
    for window_start, window_end in calendar.tet_windows:
        start = date.fromisoformat(window_start)
        end = date.fromisoformat(window_end)
        span = (end - start).days + 1
        total = 0
        for offset in range(span):
            key = (start + timedelta(days=offset)).isoformat()
            total += counts.get(key, 0)
        labels.append(f"{window_start} → {window_end}")
        values.append(round(total / span, 6))
    if not labels:
        return []
    return [
        ChartData(
            chart_id="TIME10",
            split=context.split,
            business_id=business_id,
            kind="bar",
            payload={"labels": labels, "values": values},
            source_ids=tuple(
                item.source_id
                for item in _coverage_entries(context)
                if item.business_id == business_id
            ),
            population_n=int(sum(counts.values())),
            sample_n=len(labels),
            method="holiday_window_event_average",
            unit="event/day",
            denominator_label="số ngày trong cửa sổ lễ theo lịch chính thức của split",
            title=f"Hoạt động quanh kỳ lễ và Tết — {business_id}",
            x_label="Cửa sổ lễ (theo lịch âm)",
            y_label="Số bản ghi trung bình mỗi ngày",
            limitations=(
                "holiday windows are taken from the official split calendar file",
                "a window average does not prove a seasonal effect",
            ),
            metadata={
                "caption": (
                    f"{len(labels)} cửa sổ lễ được đánh dấu từ calendar.csv của split; "
                    f"số bản ghi trung bình mỗi ngày của {business_id}."
                )
            },
        )
    ]


def _as_of_chart(context: BundleContext) -> list[ChartData]:
    profile = context.bundle.question_profile
    if profile is None or not profile.as_of_min or not profile.as_of_max:
        return []
    daily, _ = _aggregate_by_business(context)
    rows: list[str] = []
    starts: list[float] = []
    ends: list[float] = []
    for business_id, counts in sorted(daily.items()):
        if not counts:
            continue
        rows.append(business_id)
        starts.append(float(date.fromisoformat(min(counts)).toordinal()))
        ends.append(float(date.fromisoformat(max(counts)).toordinal()))
    if not rows:
        return []
    rows.append("câu hỏi (as_of)")
    starts.append(float(date.fromisoformat(profile.as_of_min).toordinal()))
    ends.append(float(date.fromisoformat(profile.as_of_max).toordinal()))
    return [
        ChartData(
            chart_id="TIME09",
            split=context.split,
            business_id="global",
            kind="timeline",
            payload={"rows": rows, "starts": starts, "ends": ends},
            source_ids=tuple(
                item.source_id
                for item in _coverage_entries(context)
            ),
            population_n=len(rows),
            sample_n=None,
            method="question_as_of_versus_source_coverage",
            unit="date",
            denominator_label="nguồn có trường ngày và khoảng as_of của câu hỏi",
            title="Phủ phạm vi ngày chốt dữ liệu của câu hỏi so với nguồn dữ liệu",
            x_label="Ngày (theo số thứ tự lịch)",
            y_label="Nguồn / phạm vi",
            limitations=(
                "as_of semantics follow the split rulebook",
                "a question date outside the data window is a risk signal, not a proof",
            ),
            metadata={
                "caption": (
                    f"Khoảng as_of của câu hỏi {profile.as_of_min} → {profile.as_of_max} "
                    f"so với khoảng phủ của {len(rows) - 1} nguồn."
                )
            },
        )
    ]


def temporal_summary_rows(context: BundleContext) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for item in _coverage_entries(context):
        monthly = monthly_counts_from_dates(
            [date.fromisoformat(day) for day in item.daily_counts]
        )
        rows.append(
            {
                "business_id": item.business_id,
                "source_id": item.source_id,
                "object_name": item.object_name,
                "column": item.column,
                "event_role": item.event_role,
                "min_date": item.min_date or "",
                "max_date": item.max_date or "",
                "active_days": item.active_days,
                "span_days": item.span_days,
                "coverage_ratio": item.coverage_ratio,
                "missing_month_count": len(item.missing_months),
                "distinct_month_count": len(monthly),
                "status": item.status,
            }
        )
    return rows


def temporal_not_applicable(
    context: BundleContext, chart_id: str, reason: str
) -> ChartData:
    return ChartData(
        chart_id=chart_id,
        split=context.split,
        business_id="global",
        kind="bar",
        payload={"labels": [], "values": []},
        source_ids=(),
        population_n=0,
        sample_n=None,
        method="not_applicable",
        unit="record/day",
        denominator_label="không áp dụng",
        title="Biểu đồ không áp dụng",
        x_label="",
        y_label="",
        status=Status.NOT_APPLICABLE,
        reason=reason,
        metadata={"caption": reason},
    )


def monthly_counts_for_source(
    context: BundleContext, source_id: str, column: str
) -> Mapping[str, int]:
    return monthly_counts_from_dates(_dates_for(context, source_id, column))
