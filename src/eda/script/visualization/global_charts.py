from __future__ import annotations

from collections import Counter
from typing import Any

from common.enums import Status
from cross_business.schema_compare import detect_field_role
from visualization.chart_context import BundleContext
from visualization.chart_data import ChartData

MAX_BUSINESSES = 40
MAX_ROLES = 30


def build_global_charts(context: BundleContext) -> list[ChartData]:
    charts: list[ChartData] = []
    charts.extend(_format_mix_chart(context))
    charts.extend(_role_coverage_chart(context))
    charts.extend(_temporal_coverage_chart(context))
    charts.extend(_quality_risk_chart(context))
    charts.extend(_split_metadata_chart(context))
    charts.extend(_coverage_status_chart(context))
    return charts


def _format_mix_chart(context: BundleContext) -> list[ChartData]:
    manifest = context.bundle.manifest
    if manifest is None:
        return []
    counts: dict[str, Counter] = {}
    for record in manifest.records:
        counts.setdefault(record.business_id, Counter())[record.source_type] += 1
    labels = sorted(counts)[:MAX_BUSINESSES]
    types = sorted({record.source_type for record in manifest.records})
    series = [
        {
            "label": source_type,
            "values": [float(counts[label].get(source_type, 0)) for label in labels],
        }
        for source_type in types
    ]
    return [
        ChartData(
            chart_id="GLOBAL01",
            split=context.split,
            business_id="global",
            kind="grouped_bar",
            payload={"labels": labels, "series": series},
            source_ids=tuple(record.source_id for record in manifest.records),
            population_n=len(manifest.records),
            sample_n=len(labels),
            method="file_count_by_business_and_format",
            unit="file",
            denominator_label="toàn bộ tệp nguồn của split",
            title="Cơ cấu định dạng nguồn giữa các doanh nghiệp",
            x_label="Mã doanh nghiệp",
            y_label="Số tệp",
            limitations=("file count is not a transaction count",),
            metadata={
                "caption": (
                    f"{len(labels)} doanh nghiệp với {len(types)} định dạng nguồn; "
                    f"tổng {len(manifest.records)} tệp."
                )
            },
        )
    ]


def _role_coverage_chart(context: BundleContext) -> list[ChartData]:
    roles_by_business: dict[str, set[str]] = {}
    for entry in context.bundle.column_entries:
        role = detect_field_role(entry.column)
        if role is None:
            continue
        roles_by_business.setdefault(entry.business_id, set()).add(role)
    if not roles_by_business:
        return []
    business_ids = sorted(roles_by_business)[:MAX_BUSINESSES]
    roles = sorted({role for values in roles_by_business.values() for role in values})[
        :MAX_ROLES
    ]
    matrix = [
        [1.0 if role in roles_by_business[business_id] else 0.0 for role in roles]
        for business_id in business_ids
    ]
    return [
        ChartData(
            chart_id="GLOBAL02",
            split=context.split,
            business_id="global",
            kind="heatmap",
            payload={"matrix": matrix, "rows": business_ids, "columns": roles},
            source_ids=tuple(entry.source_id for entry in context.bundle.column_entries),
            population_n=len(business_ids) * len(roles),
            sample_n=len(business_ids),
            method="role_presence_matrix",
            unit="presence",
            denominator_label="cặp doanh nghiệp và vai trò trường",
            title="Ma trận độ phủ vai trò trường ngữ nghĩa",
            x_label="Vai trò trường",
            y_label="Mã doanh nghiệp",
            limitations=(
                "a shared semantic role does not imply an equivalent join key",
                "role detection is name based and confidence graded",
            ),
            metadata={
                "caption": (
                    f"{len(business_ids)} doanh nghiệp với {len(roles)} vai trò trường; "
                    "mọi doanh nghiệp phát hiện được đều xuất hiện trong ma trận."
                )
            },
        )
    ]


def _temporal_coverage_chart(context: BundleContext) -> list[ChartData]:
    coverages = [item for item in context.bundle.coverages if item.min_date and item.max_date]
    if not coverages:
        return []
    by_business: dict[str, tuple[str, str]] = {}
    for item in coverages:
        current = by_business.get(item.business_id)
        if current is None:
            by_business[item.business_id] = (item.min_date, item.max_date)
        else:
            by_business[item.business_id] = (
                min(current[0], item.min_date),
                max(current[1], item.max_date),
            )
    labels = sorted(by_business)
    from datetime import date

    starts = [float(date.fromisoformat(by_business[label][0]).toordinal()) for label in labels]
    ends = [float(date.fromisoformat(by_business[label][1]).toordinal()) for label in labels]
    return [
        ChartData(
            chart_id="GLOBAL03",
            split=context.split,
            business_id="global",
            kind="timeline",
            payload={"rows": labels, "starts": starts, "ends": ends},
            source_ids=tuple(item.source_id for item in coverages),
            population_n=len(coverages),
            sample_n=len(labels),
            method="coverage_interval_per_business",
            unit="date",
            denominator_label="các nguồn có trường ngày hợp lệ",
            title="Phủ thời gian giữa các doanh nghiệp",
            x_label="Ngày (theo số thứ tự lịch)",
            y_label="Mã doanh nghiệp",
            limitations=(
                "each date field keeps its own event role, so windows are not directly comparable",
            ),
            metadata={
                "caption": (
                    f"Khoảng phủ ngày của {len(labels)} doanh nghiệp; các khoảng khớp hồ sơ "
                    "thời gian."
                )
            },
        )
    ]


def _quality_risk_chart(context: BundleContext) -> list[ChartData]:
    findings = list(context.bundle.findings)
    if not findings:
        return []
    counts: dict[str, int] = Counter()
    for item in findings:
        counts[item.business_id] += 1
    total = sum(counts.values())
    labels = sorted(counts, key=lambda key: -counts[key])[:MAX_BUSINESSES]
    values = [round(counts[label] / total * 100.0, 6) for label in labels]
    return [
        ChartData(
            chart_id="GLOBAL04",
            split=context.split,
            business_id="global",
            kind="horizontal_bar",
            payload={"labels": labels, "values": values},
            source_ids=tuple(item.finding_id for item in findings),
            population_n=total,
            sample_n=len(labels),
            method="finding_share_per_business",
            unit="percent",
            denominator_label="tổng số phát hiện chất lượng của split",
            title="Rủi ro chất lượng dữ liệu theo doanh nghiệp",
            x_label="Tỷ trọng phát hiện (%)",
            y_label="Mã doanh nghiệp",
            limitations=(
                "the denominator is the number of findings, not the data volume",
            ),
            metadata={
                "caption": (
                    f"Tỷ trọng {total} phát hiện chất lượng theo doanh nghiệp; số đếm khớp "
                    "registry phát hiện."
                )
            },
        )
    ]


def _split_metadata_chart(context: BundleContext) -> list[ChartData]:
    manifest = context.bundle.manifest
    if manifest is None:
        return []
    labels = [
        "Tệp nguồn",
        "Doanh nghiệp",
        "Worksheet",
        "Đối tượng CSDL",
        "Cột đã kiểm tra",
        "Phát hiện chất lượng",
    ]
    values = [
        float(len(manifest.records)),
        float(len(context.bundle.business_profiles)),
        float(
            len(context.bundle.sheet_registry.entries)
            if context.bundle.sheet_registry
            else 0
        ),
        float(
            len(context.bundle.sqlite_registry.entries)
            if context.bundle.sqlite_registry
            else 0
        ),
        float(len(context.bundle.column_entries)),
        float(len(context.bundle.findings)),
    ]
    return [
        ChartData(
            chart_id="GLOBAL06",
            split=context.split,
            business_id="global",
            kind="bar",
            payload={"labels": labels, "values": values},
            source_ids=tuple(record.source_id for record in manifest.records),
            population_n=len(manifest.records),
            sample_n=len(labels),
            method="metadata_counts_per_split",
            unit="object",
            denominator_label="đối tượng siêu dữ liệu đã kiểm kê của split",
            title="Đối chiếu siêu dữ liệu split",
            x_label="Chỉ số siêu dữ liệu",
            y_label="Số lượng",
            limitations=(
                "each metric counts a different object kind and is not summed across kinds",
            ),
            metadata={
                "caption": (
                    "Số lượng đối tượng siêu dữ liệu của split; mỗi chỉ số đếm một loại "
                    "đối tượng khác nhau."
                )
            },
        )
    ]


def _coverage_status_chart(context: BundleContext) -> list[ChartData]:
    profile = context.bundle.global_profile
    if profile is None:
        return []
    statuses = ("PASS", "PARTIAL", "BLOCKED")
    counts = Counter(profile.business_status_map.values())
    series = [
        {"label": status, "values": [float(counts.get(status, 0))]} for status in statuses
    ]
    return [
        ChartData(
            chart_id="GLOBAL07",
            split=context.split,
            business_id="global",
            kind="grouped_bar",
            payload={"labels": [context.split], "series": series},
            source_ids=tuple(sorted(profile.business_status_map)),
            population_n=profile.business_count,
            sample_n=1,
            method="business_count_by_coverage_status",
            unit="business",
            denominator_label="số doanh nghiệp của split",
            title="Trạng thái phủ dữ liệu toàn cục",
            x_label="Split",
            y_label="Số doanh nghiệp",
            limitations=("coverage status is not a data-quality score",),
            metadata={
                "caption": (
                    f"{profile.business_count} doanh nghiệp của split {context.split}: "
                    f"{counts.get('PASS', 0)} PASS, {counts.get('PARTIAL', 0)} PARTIAL, "
                    f"{counts.get('BLOCKED', 0)} BLOCKED."
                )
            },
        )
    ]


def global_not_applicable(
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
        unit="object",
        denominator_label="không áp dụng",
        title="Biểu đồ không áp dụng",
        x_label="",
        y_label="",
        status=Status.NOT_APPLICABLE,
        reason=reason,
        metadata={"caption": reason},
    )
