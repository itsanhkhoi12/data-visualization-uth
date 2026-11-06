from __future__ import annotations

from collections import Counter
from typing import Any

from common.enums import Status
from schema.type_inference import is_blank
from statistics.missing_dependency import co_missing_matrix
from visualization.chart_context import BundleContext
from visualization.chart_data import ChartData

MAX_FIELDS = 30
MAX_BUSINESSES = 30
MAX_MISSING_FIELDS = 24
SEVERITY_ORDER = ("critical", "high", "medium", "low", "info")
GATE_STATUS_ORDER = ("PASS", "PARTIAL", "BLOCKED", "NOT APPLICABLE")


def build_quality_charts(context: BundleContext) -> list[ChartData]:
    charts: list[ChartData] = []
    charts.extend(_missing_field_chart(context))
    charts.extend(_missing_business_chart(context))
    charts.extend(_duplicate_chart(context))
    charts.extend(_validity_chart(context))
    charts.extend(_severity_chart(context))
    charts.extend(_co_missing_matrix_chart(context))
    return charts


def _co_missing_matrix_chart(context: BundleContext) -> list[ChartData]:
    for source_id in sorted(context.bundle.row_samples):
        rows = context.rows_for_source(source_id)
        if len(rows) < 20:
            continue
        fields = sorted({key for row in rows[:200] for key in row})[:MAX_MISSING_FIELDS]
        if len(fields) < 2:
            continue
        masks = {field: [is_blank(row.get(field)) for row in rows] for field in fields}
        names, matrix, notes = co_missing_matrix(masks)
        if not matrix:
            continue
        return [
            ChartData(
                chart_id="QUAL02",
                split=context.split,
                business_id=context.business_of_source(source_id),
                kind="heatmap",
                payload={
                    "matrix": [
                        [0.0 if item is None else float(item) for item in row]
                        for row in matrix
                    ],
                    "rows": list(names),
                    "columns": list(names),
                },
                source_ids=(source_id,),
                population_n=len(rows),
                sample_n=len(rows),
                method="binary_missing_indicator_on_bounded_row_sample",
                unit="binary",
                denominator_label="số dòng mẫu của nguồn",
                title=(
                    f"Ma trận đồng thiếu giá trị — "
                    f"{context.business_of_source(source_id)}"
                ),
                x_label="Trường",
                y_label="Trường",
                limitations=(
                    "the missing mask is computed on a bounded row sample",
                    "a constant mask is reported as a null cell",
                ),
                metadata={
                    "caption": (
                        f"Mặt nạ thiếu nhị phân của {len(names)} trường trên "
                        f"{len(rows)} dòng mẫu của nguồn {source_id}."
                    ),
                    "notes": list(notes),
                },
            )
        ]
    return []


def _missing_field_chart(context: BundleContext) -> list[ChartData]:
    entries = list(context.bundle.missing_entries)
    if not entries:
        return []
    ordered = sorted(entries, key=lambda item: -item.missing_ratio)[:MAX_FIELDS]
    labels = [
        f"{item.business_id}/{item.object_name}/{item.column}" for item in ordered
    ]
    values = [round(item.missing_ratio * 100.0, 6) for item in ordered]
    return [
        ChartData(
            chart_id="QUAL01",
            split=context.split,
            business_id="global",
            kind="horizontal_bar",
            payload={"labels": labels, "values": values},
            source_ids=tuple(item.source_id for item in ordered),
            population_n=sum(item.n_total for item in ordered),
            sample_n=len(labels),
            method="missing_n_over_total_n_per_column",
            unit="percent",
            denominator_label="n_total của từng cột được hồ sơ",
            title="Tỷ lệ thiếu giá trị theo trường",
            x_label="Tỷ lệ thiếu (%)",
            y_label="Trường",
            limitations=(
                "structural blanks are reported separately from true gaps",
                "the denominator is the profiled column row count",
            ),
            metadata={
                "caption": (
                    f"{len(labels)} trường được xếp theo tỷ lệ thiếu; mẫu số là n_total "
                    "của từng cột."
                )
            },
        )
    ]


def _missing_business_chart(context: BundleContext) -> list[ChartData]:
    entries = list(context.bundle.missing_entries)
    if not entries:
        return []
    totals: dict[str, int] = {}
    missing: dict[str, int] = {}
    for item in entries:
        totals[item.business_id] = totals.get(item.business_id, 0) + item.n_total
        missing[item.business_id] = missing.get(item.business_id, 0) + item.n_missing
    ordered = sorted(totals, key=lambda key: -(missing[key] / totals[key] if totals[key] else 0))
    ordered = ordered[:MAX_BUSINESSES]
    labels = ordered
    values = [
        round(missing[key] / totals[key] * 100.0, 6) if totals[key] else 0.0
        for key in ordered
    ]
    return [
        ChartData(
            chart_id="QUAL03",
            split=context.split,
            business_id="global",
            kind="horizontal_bar",
            payload={"labels": labels, "values": values},
            source_ids=tuple(item.source_id for item in entries),
            population_n=sum(totals.values()),
            sample_n=len(labels),
            method="weighted_missing_ratio_per_business",
            unit="percent",
            denominator_label="tổng số ô của các trường được hồ sơ trong mỗi doanh nghiệp",
            title="Tỷ lệ thiếu giá trị theo doanh nghiệp",
            x_label="Tỷ lệ thiếu (%)",
            y_label="Mã doanh nghiệp",
            limitations=(
                "the business universe is the set of profiled columns, which differs across businesses",
            ),
            metadata={
                "caption": (
                    f"Tỷ lệ thiếu có trọng số của {len(labels)} doanh nghiệp; mẫu số là "
                    "tổng số ô của các trường được hồ sơ."
                )
            },
        )
    ]


def _duplicate_chart(context: BundleContext) -> list[ChartData]:
    entries = list(context.bundle.duplicate_entries)
    if not entries:
        return []
    by_business: dict[str, Counter] = {}
    for item in entries:
        by_business.setdefault(item.business_id, Counter())[item.duplicate_class] += (
            item.n_duplicate_rows
        )
    labels = sorted(by_business)
    classes = sorted({item.duplicate_class for item in entries})
    series = [
        {
            "label": class_name,
            "values": [float(by_business[label].get(class_name, 0)) for label in labels],
        }
        for class_name in classes
    ]
    return [
        ChartData(
            chart_id="QUAL04",
            split=context.split,
            business_id="global",
            kind="stacked_bar",
            payload={"labels": labels, "series": series},
            source_ids=tuple(item.source_id for item in entries),
            population_n=sum(item.total_n for item in entries),
            sample_n=len(labels),
            method="count_duplicate_rows_by_class",
            unit="row",
            denominator_label="tổng số dòng của các nguồn có kiểm tra trùng lặp",
            title="Phân bố lớp trùng lặp theo doanh nghiệp",
            x_label="Mã doanh nghiệp",
            y_label="Số dòng bị trùng",
            limitations=(
                "duplicate classes can overlap and are not additive evidence of invalid rows",
            ),
            metadata={
                "caption": (
                    f"{len(classes)} lớp trùng lặp phân bố trên {len(labels)} doanh nghiệp; "
                    "số đếm khớp registry trùng lặp."
                )
            },
        )
    ]


def _validity_chart(context: BundleContext) -> list[ChartData]:
    entries = list(context.bundle.validity_entries)
    if not entries:
        return []
    aggregated: dict[str, tuple[int, int]] = {}
    for item in entries:
        invalid, denominator = aggregated.get(item.rule_id, (0, 0))
        aggregated[item.rule_id] = (invalid + item.invalid_count, denominator + item.denominator)
    ordered = sorted(
        aggregated,
        key=lambda key: -(aggregated[key][0] / aggregated[key][1] if aggregated[key][1] else 0),
    )[:MAX_FIELDS]
    labels = ordered
    values = [
        round(aggregated[key][0] / aggregated[key][1] * 100.0, 6)
        if aggregated[key][1]
        else 0.0
        for key in ordered
    ]
    return [
        ChartData(
            chart_id="QUAL05",
            split=context.split,
            business_id="global",
            kind="horizontal_bar",
            payload={"labels": labels, "values": values},
            source_ids=tuple(item.source_id for item in entries),
            population_n=sum(item.denominator for item in entries),
            sample_n=len(labels),
            method="invalid_count_over_denominator_per_rule",
            unit="percent",
            denominator_label="mẫu số đã kiểm tra của từng quy tắc",
            title="Tỷ lệ vi phạm quy tắc kiểm tra giá trị",
            x_label="Tỷ lệ vi phạm (%)",
            y_label="Quy tắc",
            limitations=("only validated constraints are counted",),
            metadata={
                "caption": (
                    f"{len(labels)} quy tắc được kiểm chứng; tỷ lệ vi phạm khớp registry "
                    "kiểm tra giá trị."
                )
            },
        )
    ]


def _severity_chart(context: BundleContext) -> list[ChartData]:
    findings = list(context.bundle.findings)
    if not findings:
        return []
    by_business: dict[str, Counter] = {}
    for item in findings:
        by_business.setdefault(item.business_id, Counter())[item.severity] += 1
    labels = sorted(by_business)
    series = [
        {
            "label": severity,
            "values": [float(by_business[label].get(severity, 0)) for label in labels],
        }
        for severity in SEVERITY_ORDER
        if any(item.severity == severity for item in findings)
    ]
    return [
        ChartData(
            chart_id="QUAL06",
            split=context.split,
            business_id="global",
            kind="stacked_bar",
            payload={"labels": labels, "series": series},
            source_ids=tuple(item.finding_id for item in findings),
            population_n=len(findings),
            sample_n=len(labels),
            method="count_findings_by_severity",
            unit="finding",
            denominator_label="toàn bộ phát hiện chất lượng của split",
            title="Phân bố mức độ phát hiện chất lượng theo doanh nghiệp",
            x_label="Mã doanh nghiệp",
            y_label="Số phát hiện",
            limitations=("severity is evidence-based, not a business impact rating",),
            metadata={
                "caption": (
                    f"{len(findings)} phát hiện chất lượng phân bố theo mức độ trên "
                    f"{len(labels)} doanh nghiệp."
                )
            },
        )
    ]


def quality_summary_rows(context: BundleContext) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for item in context.bundle.findings:
        rows.append(
            {
                "finding_id": item.finding_id,
                "severity": item.severity,
                "domain": item.domain,
                "business_id": item.business_id,
                "source_id": item.source_id,
                "field": item.field or "",
                "count": item.count,
                "denominator": item.denominator,
                "ratio": round(item.ratio, 6),
                "status": item.status.value,
                "evidence": item.evidence,
            }
        )
    return rows


def quality_not_applicable(
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
        unit="percent",
        denominator_label="không áp dụng",
        title="Biểu đồ không áp dụng",
        x_label="",
        y_label="",
        status=Status.NOT_APPLICABLE,
        reason=reason,
        metadata={"caption": reason},
    )
