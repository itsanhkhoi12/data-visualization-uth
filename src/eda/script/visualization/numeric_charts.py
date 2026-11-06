from __future__ import annotations

from typing import Any, Sequence

from common.enums import Status
from profiling.semantic_eligibility import (
    continuous_density_eligibility,
    numeric_measure_eligibility,
)
from statistics.histogram_bins import build_bins, ecdf_series, kde_series
from statistics.robust_stats import (
    compute_robust_dispersion,
    iqr_outlier_masks,
    quantile_profile,
)
from visualization.chart_context import BundleContext, ColumnView
from visualization.chart_data import ChartData

MAX_FIELDS_PER_BUSINESS = 3
MIN_ECDF_POINTS = 20
MIN_KDE_POINTS = 30


def _eligible_measures(
    context: BundleContext,
) -> list[tuple[ColumnView, list[float], str]]:
    eligible: list[tuple[ColumnView, list[float], str]] = []
    for column in context.measure_columns():
        values = context.numeric_values(column.source_id, column.column)
        if not values:
            continue
        decision = numeric_measure_eligibility(
            field=column.column,
            semantic_type=column.semantic_type,
            n_valid=len(values),
            n_unique=len(set(values)),
        )
        if decision.eligibility not in {"APPLICABLE", "PARTIAL"}:
            continue
        eligible.append((column, values, decision.reason))
    return eligible


def _group_by_business(
    context: BundleContext,
) -> dict[str, list[tuple[ColumnView, list[float], str]]]:
    grouped: dict[str, list[tuple[ColumnView, list[float], str]]] = {}
    for item in _eligible_measures(context):
        grouped.setdefault(item[0].business_id, []).append(item)
    return grouped


def build_numeric_charts(context: BundleContext) -> list[ChartData]:
    charts: list[ChartData] = []
    for business_id, items in sorted(_group_by_business(context).items()):
        selected = items[:MAX_FIELDS_PER_BUSINESS]
        for column, values, eligibility_reason in selected:
            charts.extend(_field_charts(context, business_id, column, values, eligibility_reason))
    return charts


def _field_charts(
    context: BundleContext,
    business_id: str,
    column: ColumnView,
    values: Sequence[float],
    eligibility_reason: str,
) -> list[ChartData]:
    charts: list[ChartData] = []
    source_id = column.source_id
    label = column.field_label
    unit = column.unit or "source unit"
    dispersion = compute_robust_dispersion(values, total_n=column.n_total)
    stats = context.numeric_stat_for(source_id, column.column)
    common_limitations = (
        "outliers are flagged and retained, never removed automatically",
        "association is not causation",
    )
    bins = build_bins(values)
    charts.append(
        ChartData(
            chart_id="NUM01",
            split=context.split,
            business_id=business_id,
            kind="histogram",
            payload={
                "values": list(values),
                "counts": list(bins.counts),
                "edges": list(bins.edges),
                "bins": bins.bin_count,
            },
            source_ids=(source_id,),
            population_n=dispersion.n_valid,
            sample_n=None,
            method=f"histogram_{bins.method}",
            unit=unit,
            denominator_label="toàn bộ giá trị hợp lệ của biến đo lường",
            title=f"Phân phối tần suất — {label}",
            x_label=f"{column.column} ({unit})",
            y_label="Số quan sát",
            limitations=common_limitations,
            metadata={
                "caption": f"Phân phối tần suất của {label} với quy tắc bin {bins.method}.",
                "eligibility_reason": eligibility_reason,
                "bin_count": bins.bin_count,
                "included_n": bins.included_n,
            },
        )
    )
    density_status, density_reason = continuous_density_eligibility(
        n_valid=dispersion.n_valid,
            n_unique=len(set(values)),
    )
    if density_status == "APPLICABLE":
        xs, ys, bandwidth = kde_series(values)
        charts.append(
            ChartData(
                chart_id="NUM02",
                split=context.split,
                business_id=business_id,
                kind="line",
                payload={"labels": xs, "values": ys},
                source_ids=(source_id,),
                population_n=dispersion.n_valid,
                sample_n=None,
                method="gaussian_kernel_density_estimate",
                unit=f"{unit}^-1",
                denominator_label="toàn bộ giá trị hợp lệ của biến đo lường",
                title=f"Mật độ ước lượng kernel — {label}",
                x_label=f"{column.column} ({unit})",
                y_label="Mật độ",
                limitations=common_limitations,
                metadata={
                    "caption": (
                        f"Ước lượng mật độ kernel của {label}; bandwidth "
                        f"{bandwidth:.6g}, mật độ chuẩn hóa trên toàn bộ quan sát hợp lệ."
                    ),
                    "bandwidth": bandwidth,
                },
            )
        )
    else:
        charts.append(
            ChartData(
                chart_id="NUM02",
                split=context.split,
                business_id=business_id,
                kind="line",
                payload={"labels": [], "values": []},
                source_ids=(source_id,),
                population_n=dispersion.n_valid,
                sample_n=None,
                method="gaussian_kernel_density_estimate",
                unit=f"{unit}^-1",
                denominator_label="toàn bộ giá trị hợp lệ của biến đo lường",
                title=f"Mật độ ước lượng kernel — {label}",
                x_label=f"{column.column} ({unit})",
                y_label="Mật độ",
                status=Status.NOT_APPLICABLE,
                reason=density_reason,
                limitations=common_limitations,
                metadata={"caption": f"Không dựng được mật độ kernel cho {label}."},
            )
        )
    charts.append(
        ChartData(
            chart_id="NUM03",
            split=context.split,
            business_id=business_id,
            kind="boxplot",
            payload={
                "groups": [list(values)],
                "labels": [f"{column.column} (n={dispersion.n_valid})"],
            },
            source_ids=(source_id,),
            population_n=dispersion.n_valid,
            sample_n=None,
            method="median_q1_q3_whiskers_iqr_1_5",
            unit=unit,
            denominator_label="toàn bộ giá trị hợp lệ của biến đo lường",
            title=f"Phân vị và phạm vi ngoại lệ — {label}",
            x_label=column.column,
            y_label=f"Giá trị ({unit})",
            limitations=common_limitations,
            metadata={
                "caption": (
                    f"Hộp phân vị của {label}: median {dispersion.median:.6g}, "
                    f"IQR {dispersion.iqr:.6g} {unit}; whiskers theo quy ước 1.5*IQR."
                ),
                "q1": dispersion.q25,
                "q3": dispersion.q75,
                "median": dispersion.median,
                "iqr": dispersion.iqr,
            },
        )
    )
    charts.append(
        ChartData(
            chart_id="NUM05",
            split=context.split,
            business_id=business_id,
            kind="ecdf",
            payload={
                "x": list(values),
                "y": [index / len(values) for index in range(1, len(values) + 1)],
            },
            source_ids=(source_id,),
            population_n=dispersion.n_valid,
            sample_n=None,
            method="empirical_cdf_full_population",
            unit="fraction",
            denominator_label="toàn bộ giá trị hợp lệ của biến đo lường",
            title=f"Hàm phân phối tích lũy thực nghiệm — {label}",
            x_label=f"{column.column} ({unit})",
            y_label="Xác suất tích lũy",
            limitations=common_limitations,
            metadata={
                "caption": (
                    f"ECDF của {label}; F_n(x)=count(x_i<=x)/n trên n={dispersion.n_valid} "
                    "quan sát hợp lệ."
                )
            },
        )
    )
    profile = quantile_profile(values)
    charts.append(
        ChartData(
            chart_id="NUM06",
            split=context.split,
            business_id=business_id,
            kind="line",
            payload={
                "labels": [f"{item['percentile']:.4g}%" for item in profile],
                "values": [float(item["value"]) for item in profile],
            },
            source_ids=(source_id,),
            population_n=dispersion.n_valid,
            sample_n=None,
            method="linear_interpolation_quantiles",
            unit=unit,
            denominator_label="toàn bộ giá trị hợp lệ của biến đo lường",
            title=f"Hồ sơ phân vị — {label}",
            x_label="Phân vị (%)",
            y_label=f"Giá trị ({unit})",
            limitations=common_limitations,
            metadata={
                "caption": (
                    f"Hồ sơ phân vị của {label} (nộ suy tuyến tính); các phân vị "
                    "đơn điệu tăng theo phương pháp nộ suy tuyến tính."
                )
            },
        )
    )
    lower_fence, upper_fence, flags, degenerate = iqr_outlier_masks(values)
    outlier_n = sum(1 for flag in flags if flag)
    charts.append(
        ChartData(
            chart_id="NUM07",
            split=context.split,
            business_id=business_id,
            kind="scatter",
            payload={
                "x": [float(index) for index in range(len(values))],
                "y": [float(value) for value in values],
                "flags": flags,
            },
            source_ids=(source_id,),
            population_n=dispersion.n_valid,
            sample_n=None,
            method="iqr_fence_flags",
            unit=unit,
            denominator_label="toàn bộ giá trị hợp lệ của biến đo lường",
            title=f"Cờ ngoại lệ theo ngưỡng IQR — {label}",
            x_label="Thứ tự quan sát",
            y_label=f"Giá trị ({unit})",
            limitations=common_limitations,
            metadata={
                "caption": (
                    f"Cờ thống kê theo ngưỡng IQR 1.5 cho {label}: {outlier_n} quan sát "
                    "nằm ngoài khoảng fence. Đây là cờ thống kê, không phải bản ghi sai."
                ),
                "outlier_n": outlier_n,
                "lower_fence": lower_fence,
                "upper_fence": upper_fence,
                "degenerate_iqr": degenerate,
            },
        )
    )
    positive_only = all(value > 0 for value in values)
    if positive_only and dispersion.n_valid > 0:
        charts.append(
            ChartData(
                chart_id="NUM08",
                split=context.split,
                business_id=business_id,
                kind="histogram",
                payload={
                    "values": list(values),
                    "counts": list(bins.counts),
                    "edges": list(bins.edges),
                    "bins": bins.bin_count,
                    "log_x": True,
                },
                source_ids=(source_id,),
                population_n=dispersion.n_valid,
                sample_n=None,
                method="same_population_log_scale_histogram",
                unit=unit,
                denominator_label="toàn bộ giá trị hợp lệ dương của biến đo lường",
                title=f"Hiển thị thang log — {label}",
                x_label=f"{column.column} (thang log, {unit})",
                y_label="Số quan sát",
                limitations=common_limitations,
                metadata={
                    "caption": (
                        f"Cùng một tập {dispersion.n_valid} quan sát hợp lệ của {label} "
                        "hiển thị trên thang log; không có giá trị nào bị loại bỏ."
                    )
                },
            )
        )
    else:
        charts.append(
            ChartData(
                chart_id="NUM08",
                split=context.split,
                business_id=business_id,
                kind="histogram",
                payload={"values": [], "counts": [], "edges": [], "bins": 0},
                source_ids=(source_id,),
                population_n=dispersion.n_valid,
                sample_n=None,
                method="same_population_log_scale_histogram",
                unit=unit,
                denominator_label="toàn bộ giá trị hợp lệ dương của biến đo lường",
                title=f"Hiển thị thang log — {label}",
                x_label=f"{column.column} (thang log, {unit})",
                y_label="Số quan sát",
                status=Status.NOT_APPLICABLE,
                reason="log_scale_requires_strictly_positive_values",
                limitations=common_limitations,
                metadata={
                    "caption": (
                        f"{label} có giá trị không dương nên không thể hiển thị trên "
                        "thang log mà không loại bỏ dữ liệu."
                    )
                },
            )
        )
    charts.append(
        ChartData(
            chart_id="NUM04",
            split=context.split,
            business_id=business_id,
            kind="violin",
            payload={"groups": [], "labels": []},
            source_ids=(source_id,),
            population_n=dispersion.n_valid,
            sample_n=None,
            method="kernel_density_per_group",
            unit=unit,
            denominator_label="nhóm phân loại cùng grain với biến đo lường",
            title=f"So sánh mật độ theo nhóm — {label}",
            x_label="Nhóm phân loại",
            y_label=f"Giá trị ({unit})",
            status=Status.NOT_APPLICABLE,
            reason="no_same_grain_categorical_group_available_for_this_measure",
            limitations=common_limitations,
            metadata={
                "caption": (
                    f"Không tìm thấy biến phân loại cùng grain với {label} để so sánh mật độ."
                )
            },
        )
    )
    del stats
    return charts


def numeric_summary_rows(context: BundleContext) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for column in context.measure_columns():
        values = context.numeric_values(column.source_id, column.column)
        if not values:
            continue
        dispersion = compute_robust_dispersion(values, total_n=column.n_total)
        rows.append(
            {
                "field": column.field_label,
                "n_total": dispersion.n_total,
                "n_valid": dispersion.n_valid,
                "n_missing": dispersion.n_missing,
                "n_zero": dispersion.n_zero,
                "median": round(dispersion.median, 6),
                "q1": round(dispersion.q25, 6),
                "q3": round(dispersion.q75, 6),
                "iqr": round(dispersion.iqr, 6),
                "mad": round(dispersion.mad, 6),
                "normalized_mad": round(dispersion.normalized_mad, 6),
                "skewness": (
                    round(dispersion.skewness, 6)
                    if dispersion.skewness is not None
                    else None
                ),
                "kurtosis": (
                    round(dispersion.kurtosis, 6)
                    if dispersion.kurtosis is not None
                    else None
                ),
                "zero_ratio": round(dispersion.zero_ratio, 6),
                "negative_ratio": round(dispersion.negative_ratio, 6),
                "outlier_ratio": round(dispersion.outlier_ratio, 6),
                "unit": column.unit or "",
            }
        )
    return rows


def quantile_summary_rows(context: BundleContext) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for column in context.measure_columns():
        values = context.numeric_values(column.source_id, column.column)
        if not values:
            continue
        for item in quantile_profile(values):
            rows.append(
                {
                    "field": column.field_label,
                    "percentile": item["percentile"],
                    "value": round(float(item["value"]), 6),
                    "unit": column.unit or "",
                }
            )
    return rows
