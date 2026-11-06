from __future__ import annotations

from typing import Any, Sequence

from common.enums import Status
from statistics.categorical_profile import build_categorical_profile, pareto_entries
from visualization.chart_context import BundleContext, ColumnView
from visualization.chart_data import ChartData

MAX_FIELDS_PER_BUSINESS = 3
TOP_K = 15
MAX_DISTINCT_FOR_CARDINALITY = 5_000


def _field_rows(context: BundleContext, column: ColumnView) -> list[Any]:
    rows = context.rows_for_source(column.source_id)
    values = [row.get(column.column) for row in rows]
    if not values:
        return []
    return list(values)


def _grouped_fields(context: BundleContext) -> dict[str, list[ColumnView]]:
    grouped: dict[str, list[ColumnView]] = {}
    for column in context.categorical_columns():
        grouped.setdefault(column.business_id, []).append(column)
    return grouped


def build_categorical_charts(context: BundleContext) -> list[ChartData]:
    charts: list[ChartData] = []
    for business_id, columns in sorted(_grouped_fields(context).items()):
        selected = columns[:MAX_FIELDS_PER_BUSINESS]
        for column in selected:
            charts.extend(_field_charts(context, business_id, column))
    return charts


def _field_charts(
    context: BundleContext, business_id: str, column: ColumnView
) -> list[ChartData]:
    charts: list[ChartData] = []
    values = _field_rows(context, column)
    label = column.field_label
    if not values:
        return charts
    profile = build_categorical_profile(
        values=values,
        field=column.field_label,
        total_n=column.n_total,
        top_k=TOP_K,
    )
    entries = list(profile.entries)
    if not entries:
        return charts
    null_entry = next((entry for entry in entries if entry.is_null), None)
    valid_entries = [entry for entry in entries if not entry.is_null]
    limitations = (
        "alias categories are not merged without README evidence",
        "top-k bucketing is reported with the preserved Others bucket",
    )
    charts.append(
        ChartData(
            chart_id="CAT01",
            split=context.split,
            business_id=business_id,
            kind="horizontal_bar",
            payload={
                "labels": [entry.category for entry in valid_entries],
                "values": [float(entry.count) for entry in valid_entries],
            },
            source_ids=(column.source_id,),
            population_n=profile.n_valid,
            sample_n=None,
            method="category_frequency_full_population",
            unit="row",
            denominator_label="số dòng hợp lệ của trường phân loại",
            title=f"Tần suất giá trị phân loại — {label}",
            x_label="Số dòng",
            y_label="Giá trị phân loại",
            limitations=limitations,
            metadata={
                "caption": (
                    f"Tần suất {len(valid_entries)} giá trị phân loại của {label}; "
                    f"tổng = {profile.n_valid} dòng hợp lệ."
                ),
                "n_valid": profile.n_valid,
                "n_unique": profile.n_unique,
            },
        )
    )
    top_entries = valid_entries[:TOP_K]
    others_count = sum(entry.count for entry in valid_entries[TOP_K:])
    top_labels = [entry.category for entry in top_entries]
    top_values = [float(entry.count) for entry in top_entries]
    if others_count:
        top_labels.append("Others")
        top_values.append(float(others_count))
    charts.append(
        ChartData(
            chart_id="CAT02",
            split=context.split,
            business_id=business_id,
            kind="horizontal_bar",
            payload={"labels": top_labels, "values": top_values},
            source_ids=(column.source_id,),
            population_n=profile.n_valid,
            sample_n=None,
            method="top_k_with_others_bucket",
            unit="row",
            denominator_label="số dòng hợp lệ của trường phân loại",
            title=f"Top-{TOP_K} danh mục và nhóm Others — {label}",
            x_label="Số dòng",
            y_label="Danh mục",
            limitations=limitations,
            metadata={
                "caption": (
                    f"Top-{TOP_K} danh mục của {label} cộng nhóm Others; "
                    f"tổng = {profile.n_valid} dòng hợp lệ."
                ),
                "others_count": others_count,
            },
        )
    )
    charts.append(
        ChartData(
            chart_id="CAT03",
            split=context.split,
            business_id=business_id,
            kind="stacked_bar",
            payload={
                "labels": [column.field_label],
                "series": [
                    {
                        "label": entry.category,
                        "values": [round(entry.share * 100.0, 6)],
                    }
                    for entry in valid_entries
                ],
            },
            source_ids=(column.source_id,),
            population_n=profile.n_valid,
            sample_n=None,
            method="category_share_of_valid",
            unit="percent",
            denominator_label="số dòng hợp lệ của trường phân loại",
            title=f"Tỷ trọng thành phần danh mục — {label}",
            x_label=column.field_label,
            y_label="Tỷ trọng (%)",
            limitations=limitations,
            metadata={
                "caption": (
                    f"Tỷ trọng từng danh mục của {label} với mẫu số "
                    f"{profile.n_valid} dòng hợp lệ."
                )
            },
        )
    )
    pareto = pareto_entries(profile)
    charts.append(
        ChartData(
            chart_id="CAT04",
            split=context.split,
            business_id=business_id,
            kind="pareto",
            payload={
                "labels": [entry.category for entry in pareto],
                "values": [float(entry.count) for entry in pareto],
                "cumulative": [
                    round(entry.cumulative_share * 100.0, 6) for entry in pareto
                ],
            },
            source_ids=(column.source_id,),
            population_n=profile.n_valid,
            sample_n=None,
            method="pareto_cumulative_share",
            unit="row",
            denominator_label="số dòng hợp lệ của trường phân loại",
            title=f"Phân tích Pareto danh mục — {label}",
            x_label="Danh mục",
            y_label="Số dòng",
            limitations=limitations,
            metadata={
                "caption": (
                    f"Phân tích Pareto của {label}; tỷ trọng tích lũy cuối cùng "
                    f"đạt {round(pareto[-1].cumulative_share * 100.0, 2)}%."
                )
            },
        )
    )
    charts.append(
        ChartData(
            chart_id="CAT06",
            split=context.split,
            business_id=business_id,
            kind="horizontal_bar",
            payload={
                "labels": [column.field_label],
                "values": [round(profile.max_category_share * 100.0, 6)],
            },
            source_ids=(column.source_id,),
            population_n=profile.n_valid,
            sample_n=None,
            method="max_category_share",
            unit="percent",
            denominator_label="số dòng hợp lệ của trường phân loại",
            title=f"Mức mất cân bằng danh mục — {label}",
            x_label="Tỷ trọng nhóm lớn nhất (%)",
            y_label=column.field_label,
            limitations=limitations,
            metadata={
                "caption": (
                    f"Nhóm lớn nhất của {label} chiếm "
                    f"{round(profile.max_category_share * 100.0, 2)}% số dòng hợp lệ; "
                    f"entropy = {profile.entropy_bits:.4f} bit."
                    if profile.entropy_bits is not None
                    else f"Nhóm lớn nhất của {label} chiếm "
                    f"{round(profile.max_category_share * 100.0, 2)}% số dòng hợp lệ."
                ),
                "max_category_share": profile.max_category_share,
                "entropy_bits": profile.entropy_bits,
            },
        )
    )
    status_labels: list[str] = []
    status_values: list[float] = []
    if null_entry is not None:
        status_labels.append("null")
        status_values.append(round(null_entry.count / max(profile.n_total, 1) * 100.0, 6))
    status_labels.append("valid")
    status_values.append(round(profile.n_valid / max(profile.n_total, 1) * 100.0, 6))
    charts.append(
        ChartData(
            chart_id="CAT08",
            split=context.split,
            business_id=business_id,
            kind="stacked_bar",
            payload={
                "labels": [column.field_label],
                "series": [
                    {"label": label_text, "values": [value]}
                    for label_text, value in zip(status_labels, status_values)
                ],
            },
            source_ids=(column.source_id,),
            population_n=profile.n_total,
            sample_n=None,
            method="mutually_exclusive_status_counts",
            unit="percent",
            denominator_label="tổng số dòng của trường phân loại",
            title=f"Trạng thái thiếu giá trị — {label}",
            x_label=column.field_label,
            y_label="Tỷ trọng trạng thái (%)",
            limitations=limitations,
            metadata={
                "caption": (
                    f"Trạng thái null và valid của {label} là loại trừ nhau; "
                    f"tổng = {profile.n_total} dòng."
                ),
                "n_null": profile.n_null,
                "n_valid": profile.n_valid,
            },
        )
    )
    return charts


def build_cardinality_chart(context: BundleContext) -> list[ChartData]:
    columns = [
        column
        for column in context.categorical_columns()
        if column.distinct_n <= MAX_DISTINCT_FOR_CARDINALITY
    ]
    if not columns:
        return []
    ordered = sorted(columns, key=lambda item: -item.distinct_n)[:40]
    labels = [column.field_label for column in ordered]
    values = [float(column.distinct_n) for column in ordered]
    return [
        ChartData(
            chart_id="CAT05",
            split=context.split,
            business_id="global",
            kind="horizontal_bar",
            payload={"labels": labels, "values": values},
            source_ids=tuple(column.source_id for column in ordered),
            population_n=sum(column.distinct_n for column in ordered),
            sample_n=None,
            method="distinct_count_per_categorical_field",
            unit="category",
            denominator_label="số giá trị duy nhất của từng trường phân loại",
            title="Hồ sơ số giá trị duy nhất theo trường phân loại",
            x_label="Số giá trị duy nhất",
            y_label="Trường phân loại",
            limitations=("field names are schema metadata, not personal data",),
            metadata={
                "caption": (
                    f"Số giá trị duy nhất của {len(ordered)} trường phân loại; "
                    "tên trường là siêu dữ liệu schema."
                )
            },
        )
    ]


def build_group_category_chart(context: BundleContext) -> list[ChartData]:
    charts: list[ChartData] = []
    grouped: dict[str, list[tuple[ColumnView, list[Any]]]] = {}
    for column in context.categorical_columns():
        values = _field_rows(context, column)
        if not values:
            continue
        grouped.setdefault(column.business_id, []).append((column, values))
    for business_id, items in sorted(grouped.items()):
        if len(items) < 2:
            continue
        column, values = items[0]
        profile = build_categorical_profile(
            values=values,
            field=column.field_label,
            total_n=column.n_total,
            top_k=TOP_K,
        )
        valid = [entry for entry in profile.entries if not entry.is_null]
        if len(valid) < 2:
            continue
        charts.append(
            ChartData(
                chart_id="CAT07",
                split=context.split,
                business_id=business_id,
                kind="grouped_bar",
                payload={
                    "labels": [entry.category for entry in valid],
                    "series": [
                        {
                            "label": column.field_label,
                            "values": [round(entry.share * 100.0, 6) for entry in valid],
                        }
                    ],
                },
                source_ids=(column.source_id,),
                population_n=profile.n_valid,
                sample_n=None,
                method="category_share_within_group",
                unit="percent",
                denominator_label="số dòng hợp lệ của nhóm",
                title=f"Phân bố danh mục theo nhóm — {business_id}",
                x_label="Danh mục",
                y_label="Tỷ trọng danh mục (%)",
                limitations=(
                    "group comparison requires the same semantic category definition",
                ),
                metadata={
                    "caption": (
                        f"Tỷ trọng danh mục của {column.field_label} trong nhóm "
                        f"{business_id}; tổng mỗi nhóm bằng 100%."
                    )
                },
            )
        )
    return charts


def categorical_summary_rows(context: BundleContext) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for column in context.categorical_columns():
        values = _field_rows(context, column)
        if not values:
            continue
        profile = build_categorical_profile(
            values=values,
            field=column.field_label,
            total_n=column.n_total,
            top_k=TOP_K,
        )
        for entry in profile.entries:
            rows.append(
                {
                    "field": column.field_label,
                    "category": entry.category,
                    "count": entry.count,
                    "share": round(entry.share, 6),
                    "cumulative_share": round(entry.cumulative_share, 6),
                    "rank": entry.rank,
                    "is_null": entry.is_null,
                    "is_others": entry.is_others,
                    "n_valid": profile.n_valid,
                    "n_null": profile.n_null,
                }
            )
    return rows


def blocked_categorical_notice(
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
        unit="row",
        denominator_label="không áp dụng",
        title="Biểu đồ không áp dụng",
        x_label="",
        y_label="",
        status=Status.NOT_APPLICABLE,
        reason=reason,
        metadata={"caption": reason},
    )
