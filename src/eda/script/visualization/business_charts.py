from __future__ import annotations

from collections import Counter
from typing import Any, Mapping, Sequence

from business.business_chart_metrics import BusinessMetricRow
from common.enums import Status
from statistics.histogram_bins import build_bins
from visualization.chart_context import BundleContext
from visualization.chart_data import ChartData

MAX_LABELS = 20
MAX_POINTS = 400
BUSINESS_CHART_IDS = (
    "BUS01",
    "BUS02",
    "BUS03",
    "BUS04",
    "BUS05",
    "BUS06",
    "BUS07",
    "BUS08",
    "BUS09",
    "BUS10",
    "BUS11",
    "BUS12",
    "BUS13",
    "BUS14",
    "BUS15",
)

CHART_TITLES: dict[str, str] = {
    "BUS01": "Phân phối giá trị đơn hàng",
    "BUS02": "Diễn biến doanh thu theo ngày",
    "BUS03": "Số lượng bán theo nhóm sản phẩm",
    "BUS04": "Cơ cấu trạng thái đơn hàng",
    "BUS05": "Phân phối số lượng tồn kho",
    "BUS06": "Giá trị tồn kho theo nhóm sản phẩm",
    "BUS07": "Phân phối số dư công nợ",
    "BUS08": "Cơ cấu trích lập công nợ theo tuổi",
    "BUS09": "Tuổi công nợ theo ngày",
    "BUS10": "Phân phối giá trị nhập hàng",
    "BUS11": "Mức tập trung của nhà cung cấp",
    "BUS12": "Số lượng tồn theo cửa sổ hết hạn",
    "BUS13": "Số mục bảo hành theo mẫu máy",
    "BUS14": "Cơ cấu loại dịch vụ sửa chữa",
    "BUS15": "Cơ cấu nhóm sản phẩm theo thuộc tính khai báo",
}

CHART_AXIS_LABELS: dict[str, tuple[str, str]] = {
    "BUS01": ("Giá trị đơn hàng (VND)", "Số đơn hàng"),
    "BUS02": ("Ngày", "Doanh thu (VND)"),
    "BUS03": ("Nhóm sản phẩm", "Số lượng"),
    "BUS04": ("Trạng thái đơn", "Số đơn"),
    "BUS05": ("Số lượng tồn kho", "Xác suất tích lũy"),
    "BUS06": ("Nhóm sản phẩm", "Giá trị tồn kho (VND)"),
    "BUS07": ("Số dư công nợ (VND)", "Số dòng công nợ"),
    "BUS08": ("Nhóm tuổi nợ", "Giá trị công nợ (VND)"),
    "BUS09": ("Tuổi công nợ (ngày)", "Số dòng công nợ"),
    "BUS10": ("Giá trị nhập hàng (VND)", "Số phiếu nhập"),
    "BUS11": ("Nhà cung cấp", "Giá trị nhập (VND)"),
    "BUS12": ("Cửa sổ hết hạn", "Số lượng tồn"),
    "BUS13": ("Mẫu máy", "Số mục có bảo hành"),
    "BUS14": ("Loại dịch vụ", "Số lượt sửa chữa"),
    "BUS15": ("Nhóm sản phẩm", "Số sản phẩm"),
}

CHART_LIMITATIONS: dict[str, tuple[str, ...]] = {
    "BUS01": (
        "order grain requires a distinct order identifier",
        "revenue eligibility follows the split rulebook status policy",
    ),
    "BUS02": (
        "daily revenue excludes cancelled and returned orders",
        "a day without revenue is not necessarily a day without activity",
    ),
    "BUS03": (
        "quantities are summed in the source unit unless a base-unit column exists",
        "unit conversion tables are not applied unless the source provides them",
    ),
    "BUS04": (
        "status labels are grouped into mutually exclusive classes",
        "an unrecognised status stays in the explicit Other class",
    ),
    "BUS05": (
        "closing stock is a snapshot and not a movement ledger",
        "stock units are not converted to a common base unit",
    ),
    "BUS06": (
        "inventory value uses the unit cost recorded in the same source",
        "cost basis is not recomputed from purchase batches",
    ),
    "BUS07": (
        "only strictly positive balances are counted as outstanding debt",
        "customer debt semantics depend on the split rulebook",
    ),
    "BUS08": (
        "aging uses the recorded due date relative to the evaluation date",
        "the cutoff date is the evaluation day and not the as-of date of a question",
    ),
    "BUS09": (
        "debt age is counted from the order date as defined by the rulebook",
        "rows without an order date are excluded and reported",
    ),
    "BUS10": (
        "purchase grain requires a distinct purchase identifier",
        "cancelled purchase notes are not separated by the source schema",
    ),
    "BUS11": (
        "supplier concentration uses recorded purchase value only",
        "the supplier join is intra-source and never crosses grains",
    ),
    "BUS12": (
        "expiry windows use the evaluation date as the reference point",
        "lot quantities are closing stock and not lifetime sold quantity",
    ),
    "BUS13": (
        "catalogue warranty entries are not warranty service events",
        "device identifiers are never exposed",
    ),
    "BUS14": (
        "one visit is counted once per distinct visit identifier",
        "service classification follows the declared category column",
    ),
    "BUS15": (
        "attributes come from declared catalogue columns and never from product names",
        "products without a declared attribute are excluded and reported",
    ),
}


def _metric_rows(context: BundleContext) -> list[BusinessMetricRow]:
    return list(context.bundle.business_metrics)


def _histogram(
    context: BundleContext,
    metric: BusinessMetricRow,
    values: Sequence[float],
    title_suffix: str,
    unit: str,
) -> ChartData:
    bins = build_bins(list(values))
    return ChartData(
        chart_id=metric.metric_id,
        split=context.split,
        business_id=metric.business_id,
        kind="histogram",
        payload={
            "values": list(values),
            "counts": list(bins.counts),
            "edges": list(bins.edges),
            "bins": bins.bin_count,
        },
        source_ids=(metric.source_id,),
        population_n=metric.population_n,
        sample_n=None,
        method=f"{metric.method}_{bins.method}_bins",
        unit=unit,
        denominator_label="toàn bộ quan sát hợp lệ của nhóm nghiệp vụ đã chọn",
        title=f"{CHART_TITLES[metric.metric_id]} — {title_suffix}",
        x_label=CHART_AXIS_LABELS[metric.metric_id][0],
        y_label=CHART_AXIS_LABELS[metric.metric_id][1],
        limitations=CHART_LIMITATIONS[metric.metric_id],
        metadata={
            "caption": (
                f"{CHART_TITLES[metric.metric_id]} của {metric.business_id} "
                f"({metric.object_name}); {len(values)} quan sát hợp lệ, quy tắc bin "
                f"{bins.method}, tổng số đếm trong bin = {sum(bins.counts)}."
            ),
            "bin_count": bins.bin_count,
            "included_n": bins.included_n,
            "metric_method": metric.method,
        },
    )


def _bar(
    context: BundleContext,
    metric: BusinessMetricRow,
    totals: Mapping[str, float],
    kind: str,
    unit: str,
    caption: str,
) -> ChartData:
    ordered = sorted(totals.items(), key=lambda item: (-item[1], item[0]))[:MAX_LABELS]
    labels = [item[0] for item in ordered]
    values = [float(item[1]) for item in ordered]
    return ChartData(
        chart_id=metric.metric_id,
        split=context.split,
        business_id=metric.business_id,
        kind=kind,
        payload={"labels": labels, "values": values},
        source_ids=(metric.source_id,),
        population_n=metric.population_n,
        sample_n=len(labels),
        method=metric.method,
        unit=unit,
        denominator_label="toàn bộ quan sát hợp lệ của nhóm nghiệp vụ đã chọn",
        title=f"{CHART_TITLES[metric.metric_id]} — {metric.business_id}",
        x_label=CHART_AXIS_LABELS[metric.metric_id][0],
        y_label=CHART_AXIS_LABELS[metric.metric_id][1],
        limitations=CHART_LIMITATIONS[metric.metric_id],
        metadata={
            "caption": caption,
            "metric_method": metric.method,
            "metric_status": metric.status.value,
        },
    )


def _pareto(
    context: BundleContext,
    metric: BusinessMetricRow,
    totals: Mapping[str, float],
    caption: str,
) -> ChartData:
    ordered = sorted(totals.items(), key=lambda item: (-item[1], item[0]))[:MAX_LABELS]
    labels = [item[0] for item in ordered]
    values = [float(item[1]) for item in ordered]
    total = sum(values)
    cumulative: list[float] = []
    running = 0.0
    for value in values:
        running += value
        cumulative.append(round(running / total * 100.0, 6) if total else 0.0)
    return ChartData(
        chart_id=metric.metric_id,
        split=context.split,
        business_id=metric.business_id,
        kind="pareto",
        payload={
            "labels": labels,
            "values": values,
            "cumulative": cumulative,
        },
        source_ids=(metric.source_id,),
        population_n=metric.population_n,
        sample_n=len(labels),
        method=metric.method,
        unit="VND",
        denominator_label="tổng giá trị nhập hàng của nhóm nghiệp vụ đã chọn",
        title=f"{CHART_TITLES[metric.metric_id]} — {metric.business_id}",
        x_label=CHART_AXIS_LABELS[metric.metric_id][0],
        y_label=CHART_AXIS_LABELS[metric.metric_id][1],
        limitations=CHART_LIMITATIONS[metric.metric_id],
        metadata={
            "caption": caption,
            "cumulative_last": cumulative[-1] if cumulative else 0.0,
            "metric_method": metric.method,
        },
    )


def _status_chart(context: BundleContext, metric: BusinessMetricRow) -> ChartData:
    counts: Counter[str] = Counter(metric.payload.get("counts", {}))
    labels = sorted(counts)
    values = [float(counts[label]) for label in labels]
    series = [
        {"label": label, "values": [float(counts[label])]} for label in labels
    ]
    return ChartData(
        chart_id="BUS04",
        split=context.split,
        business_id=metric.business_id,
        kind="stacked_bar",
        payload={"labels": [metric.business_id], "series": series},
        source_ids=(metric.source_id,),
        population_n=metric.population_n,
        sample_n=len(labels),
        method=metric.method,
        unit="order",
        denominator_label="toàn bộ mã đơn hàng phân biệt được của nguồn",
        title=f"{CHART_TITLES['BUS04']} — {metric.business_id}",
        x_label="Doanh nghiệp",
        y_label="Số đơn",
        limitations=CHART_LIMITATIONS["BUS04"],
        metadata={
            "caption": (
                f"Phân bố trạng thái đơn của {metric.business_id} theo "
                f"{metric.population_n} mã đơn phân biệt được; các nhóm là loại trừ nhau."
            ),
            "counts": dict(counts),
            "metric_method": metric.method,
        },
    )


def _revenue_chart(context: BundleContext, metric: BusinessMetricRow) -> ChartData:
    daily: Mapping[str, float] = metric.payload.get("daily", {})
    labels = sorted(daily)[:MAX_POINTS]
    values = [float(daily[label]) for label in labels]
    return ChartData(
        chart_id="BUS02",
        split=context.split,
        business_id=metric.business_id,
        kind="line",
        payload={"labels": labels, "values": values},
        source_ids=(metric.source_id,),
        population_n=metric.population_n,
        sample_n=len(labels),
        method=metric.method,
        unit="VND",
        denominator_label="các dòng đơn hợp lệ theo bộ lọc trạng thái của rulebook",
        title=f"{CHART_TITLES['BUS02']} — {metric.business_id}",
        x_label=CHART_AXIS_LABELS["BUS02"][0],
        y_label=CHART_AXIS_LABELS["BUS02"][1],
        limitations=CHART_LIMITATIONS["BUS02"],
        metadata={
            "caption": (
                f"Doanh thu theo ngày của {metric.business_id} trên {metric.population_n} "
                f"dòng đơn hợp lệ; tổng doanh thu = {sum(values):,.0f} VND.".replace(",", ".")
            ),
            "revenue_total": sum(values),
            "metric_method": metric.method,
        },
    )


def _stock_ecdf(context: BundleContext, metric: BusinessMetricRow) -> ChartData:
    quantities = sorted(float(value) for value in metric.payload.get("quantities", []))
    total = len(quantities)
    xs = quantities
    ys = [round((index + 1) / total, 6) for index in range(total)]
    return ChartData(
        chart_id="BUS05",
        split=context.split,
        business_id=metric.business_id,
        kind="ecdf",
        payload={"x": xs, "y": ys},
        source_ids=(metric.source_id,),
        population_n=metric.population_n,
        sample_n=None,
        method=metric.method,
        unit="source unit",
        denominator_label="toàn bộ số lượng tồn cuối kỳ đọc được",
        title=f"{CHART_TITLES['BUS05']} — {metric.business_id}",
        x_label=CHART_AXIS_LABELS["BUS05"][0],
        y_label=CHART_AXIS_LABELS["BUS05"][1],
        limitations=CHART_LIMITATIONS["BUS05"],
        metadata={
            "caption": (
                f"Hàm phân phối tích lũy thực nghiệm của số lượng tồn cuối kỳ của "
                f"{metric.business_id} trên n={total} quan sát hợp lệ."
            ),
            "metric_method": metric.method,
        },
    )


def _aging_bar(context: BundleContext, metric: BusinessMetricRow) -> ChartData:
    totals: Mapping[str, float] = metric.payload.get("totals", {})
    order = (
        "Chưa đến hạn",
        "Trễ 1-30 ngày",
        "Trễ 31-60 ngày",
        "Trễ trên 90 ngày",
    )
    labels = [name for name in order if name in totals]
    labels.extend(
        name for name in sorted(totals) if name not in order
    )
    values = [float(totals.get(name, 0.0)) for name in labels]
    return ChartData(
        chart_id="BUS08",
        split=context.split,
        business_id=metric.business_id,
        kind="bar",
        payload={"labels": labels, "values": values},
        source_ids=(metric.source_id,),
        population_n=metric.population_n,
        sample_n=len(labels),
        method=metric.method,
        unit="VND",
        denominator_label="tổng số dư công nợ còn phải thu của nhóm nghiệp vụ đã chọn",
        title=f"{CHART_TITLES['BUS08']} — {metric.business_id}",
        x_label=CHART_AXIS_LABELS["BUS08"][0],
        y_label=CHART_AXIS_LABELS["BUS08"][1],
        limitations=CHART_LIMITATIONS["BUS08"],
        metadata={
            "caption": (
                f"Tổng số dư công nợ theo nhóm tuổi của {metric.business_id}; tổng các "
                f"nhóm = {sum(values):,.0f} VND.".replace(",", ".")
            ),
            "metric_method": metric.method,
        },
    )


def _expiry_bar(context: BundleContext, metric: BusinessMetricRow) -> ChartData:
    totals: Mapping[str, float] = metric.payload.get("totals", {})
    order = (
        "Đã quá hạn",
        "Trong 30 ngày",
        "Trong 60 ngày",
        "Trong 90 ngày",
        "Trong 180 ngày",
        "Trong 365 ngày",
        "Trên 365 ngày",
    )
    labels = [name for name in order if name in totals]
    labels.extend(name for name in sorted(totals) if name not in order)
    values = [float(totals.get(name, 0.0)) for name in labels]
    as_of = metric.payload.get("as_of", "")
    return ChartData(
        chart_id="BUS12",
        split=context.split,
        business_id=metric.business_id,
        kind="bar",
        payload={"labels": labels, "values": values},
        source_ids=(metric.source_id,),
        population_n=metric.population_n,
        sample_n=len(labels),
        method=metric.method,
        unit="source unit",
        denominator_label="tổng số lượng tồn của các lô còn tồn tại thời điểm chốt",
        title=f"{CHART_TITLES['BUS12']} — {metric.business_id}",
        x_label=CHART_AXIS_LABELS["BUS12"][0],
        y_label=CHART_AXIS_LABELS["BUS12"][1],
        limitations=CHART_LIMITATIONS["BUS12"],
        metadata={
            "caption": (
                f"Số lượng tồn theo cửa sổ hết hạn của {metric.business_id}, mốc chốt "
                f"{as_of}; tổng số lượng = {sum(values):,.0f}.".replace(",", ".")
            ),
            "as_of_date": as_of,
            "metric_method": metric.method,
        },
    )


def _attribute_chart(context: BundleContext, metric: BusinessMetricRow) -> ChartData:
    counts: Mapping[str, int] = metric.payload.get("counts", {})
    ordered = sorted(counts.items(), key=lambda item: (-item[1], item[0]))[:MAX_LABELS]
    labels = [item[0] for item in ordered]
    values = [float(item[1]) for item in ordered]
    series = [{"label": "Số sản phẩm", "values": values}]
    return ChartData(
        chart_id="BUS15",
        split=context.split,
        business_id=metric.business_id,
        kind="stacked_bar",
        payload={"labels": labels, "series": series},
        source_ids=(metric.source_id,),
        population_n=metric.population_n,
        sample_n=len(labels),
        method=metric.method,
        unit="product",
        denominator_label="số sản phẩm trong danh mục có khai báo thuộc tính",
        title=f"{CHART_TITLES['BUS15']} — {metric.business_id}",
        x_label=CHART_AXIS_LABELS["BUS15"][0],
        y_label=CHART_AXIS_LABELS["BUS15"][1],
        limitations=CHART_LIMITATIONS["BUS15"],
        metadata={
            "caption": (
                f"Số sản phẩm theo nhóm của {metric.business_id} được đếm từ cột thuộc "
                f"tính khai báo, không suy diễn từ tên sản phẩm."
            ),
            "metric_method": metric.method,
        },
    )


def build_business_charts(context: BundleContext) -> list[ChartData]:
    charts: list[ChartData] = []
    rows = _metric_rows(context)
    by_metric: dict[str, list[BusinessMetricRow]] = {}
    for row in rows:
        by_metric.setdefault(row.metric_id, []).append(row)
    for chart_id in BUSINESS_CHART_IDS:
        candidates = by_metric.get(chart_id, [])
        if not candidates:
            charts.append(_not_applicable(context, chart_id, "no_matching_business_metric_row"))
            continue
        applicable = [item for item in candidates if item.status == Status.PASS]
        if not applicable:
            blocked = sorted(candidates, key=lambda item: (-item.population_n, item.source_id))
            charts.append(_not_applicable(context, chart_id, blocked[0].reason or "not applicable"))
            continue
        by_business: dict[str, list[BusinessMetricRow]] = {}
        for item in applicable:
            by_business.setdefault(item.business_id, []).append(item)
        for business_id in sorted(by_business):
            business_rows = sorted(
                by_business[business_id],
                key=lambda item: (-item.population_n, item.source_id),
            )
            charts.append(_chart_for(context, business_rows[0]))
    return charts


def _chart_for(context: BundleContext, metric: BusinessMetricRow) -> ChartData:
    chart_id = metric.metric_id
    if metric.status != Status.PASS:
        return _not_applicable(context, chart_id, metric.reason or metric.status.value)
    if chart_id == "BUS01":
        return _histogram(
            context,
            metric,
            [float(value) for value in metric.payload.get("amounts", [])],
            metric.business_id,
            "VND",
        )
    if chart_id == "BUS02":
        return _revenue_chart(context, metric)
    if chart_id == "BUS03":
        return _bar(
            context,
            metric,
            metric.payload.get("totals", {}),
            "bar",
            metric.unit,
            (
                f"Tổng số lượng theo nhóm sản phẩm của {metric.business_id}; tổng = "
                f"{sum(float(v) for v in metric.payload.get('totals', {}).values()):,.0f} "
                f"{metric.unit}.".replace(",", ".")
            ),
        )
    if chart_id == "BUS04":
        return _status_chart(context, metric)
    if chart_id == "BUS05":
        return _stock_ecdf(context, metric)
    if chart_id == "BUS06":
        return _bar(
            context,
            metric,
            metric.payload.get("totals", {}),
            "bar",
            "VND",
            (
                f"Giá trị tồn kho theo nhóm sản phẩm của {metric.business_id}; tổng = "
                f"{sum(float(v) for v in metric.payload.get('totals', {}).values()):,.0f} "
                "VND.".replace(",", ".")
            ),
        )
    if chart_id == "BUS07":
        return _histogram(
            context,
            metric,
            [float(value) for value in metric.payload.get("balances", [])],
            metric.business_id,
            "VND",
        )
    if chart_id == "BUS08":
        return _aging_bar(context, metric)
    if chart_id == "BUS09":
        return _histogram(
            context,
            metric,
            [float(value) for value in metric.payload.get("ages", [])],
            metric.business_id,
            "day",
        )
    if chart_id == "BUS10":
        return _histogram(
            context,
            metric,
            [float(value) for value in metric.payload.get("totals", [])],
            metric.business_id,
            "VND",
        )
    if chart_id == "BUS11":
        return _pareto(
            context,
            metric,
            metric.payload.get("totals", {}),
            (
                f"Giá trị nhập hàng theo nhà cung cấp của {metric.business_id}; tỷ trọng "
                "tích lũy cuối cùng = "
                f"{metric.payload.get('totals') and 100.0 or 0.0:.0f}%."
            ),
        )
    if chart_id == "BUS12":
        return _expiry_bar(context, metric)
    if chart_id == "BUS13":
        return _bar(
            context,
            metric,
            metric.payload.get("counts", {}),
            "bar",
            "product",
            (
                f"Số mục danh mục có khai báo bảo hành theo mẫu máy của "
                f"{metric.business_id}; định danh thiết bị không được hiển thị."
            ),
        )
    if chart_id == "BUS14":
        return _bar(
            context,
            metric,
            metric.payload.get("counts", {}),
            "bar",
            "visit",
            (
                f"Số lượt sửa chữa theo loại dịch vụ của {metric.business_id}; mỗi lượt "
                "chỉ được đếm một lần."
            ),
        )
    if chart_id == "BUS15":
        return _attribute_chart(context, metric)
    return _not_applicable(context, chart_id, "unsupported_business_chart_id")


def _not_applicable(context: BundleContext, chart_id: str, reason: str) -> ChartData:
    x_label, y_label = CHART_AXIS_LABELS.get(chart_id, ("", ""))
    return ChartData(
        chart_id=chart_id,
        split=context.split,
        business_id="global",
        kind="bar",
        payload={"labels": [], "values": []},
        source_ids=(),
        population_n=0,
        sample_n=None,
        method="business_metric_not_applicable",
        unit="not applicable",
        denominator_label="không áp dụng",
        title=f"{CHART_TITLES.get(chart_id, chart_id)} — không áp dụng",
        x_label=x_label,
        y_label=y_label,
        status=Status.NOT_APPLICABLE,
        reason=reason,
        limitations=(
            "the source does not carry the fields required by this business chart",
        ),
        metadata={
            "caption": (
                f"Chưa đủ dữ liệu hoặc điều kiện kiểm chứng để dựng {chart_id}: {reason}."
            )
        },
    )


def business_coverage_rows(context: BundleContext) -> list[dict[str, Any]]:
    rows = _metric_rows(context)
    coverage: dict[str, dict[str, Any]] = {}
    for row in rows:
        entry = coverage.setdefault(
            row.business_id,
            {
                "business_id": row.business_id,
                "split": context.split,
                "applicable_charts": [],
                "not_applicable_charts": [],
                "blocked_charts": [],
                "source_count": 0,
            },
        )
        entry["source_ids"] = sorted(
            set(entry.get("source_ids", []) + [row.source_id])
        )
        entry["source_count"] = len(entry["source_ids"])
        if row.status == Status.PASS:
            if row.metric_id not in entry["applicable_charts"]:
                entry["applicable_charts"].append(row.metric_id)
        elif row.status == Status.BLOCKED:
            if row.metric_id not in entry["blocked_charts"]:
                entry["blocked_charts"].append(row.metric_id)
        else:
            if row.metric_id not in entry["not_applicable_charts"]:
                entry["not_applicable_charts"].append(row.metric_id)
    output: list[dict[str, Any]] = []
    for business_id in sorted(coverage):
        entry = coverage[business_id]
        output.append(
            {
                "business_id": business_id,
                "split": entry["split"],
                "source_count": entry["source_count"],
                "applicable_count": len(entry["applicable_charts"]),
                "not_applicable_count": len(entry["not_applicable_charts"]),
                "blocked_count": len(entry["blocked_charts"]),
                "applicable_charts": ", ".join(sorted(entry["applicable_charts"])),
                "not_applicable_charts": ", ".join(
                    sorted(entry["not_applicable_charts"])
                ),
                "blocked_charts": ", ".join(sorted(entry["blocked_charts"])),
            }
        )
    return output


def business_chart_summary_rows(context: BundleContext) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for metric in _metric_rows(context):
        rows.append(
            {
                "business_id": metric.business_id,
                "source_id": metric.source_id,
                "object_name": metric.object_name,
                "chart_id": metric.metric_id,
                "status": metric.status.value,
                "reason": metric.reason,
                "population_n": metric.population_n,
                "grain": metric.grain,
                "unit": metric.unit,
                "method": metric.method,
            }
        )
    return rows


def status_class_distribution(context: BundleContext) -> dict[str, int]:
    counts: Counter[str] = Counter()
    for metric in context.bundle.business_metrics:
        if metric.metric_id != "BUS04":
            continue
        for label, value in metric.payload.get("counts", {}).items():
            counts[label] += int(value)
    return dict(counts)
