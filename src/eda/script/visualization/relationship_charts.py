from __future__ import annotations

from typing import Any, Sequence

from common.enums import Status
from schema.join_eligibility import eligible_relations
from statistics.association_profile import correlation_matrix, kendall_tau_b
from statistics.categorical_association import crosstab_association
from statistics.group_comparison import group_value_buckets
from statistics.missing_dependency import co_missing_matrix
from schema.type_inference import is_blank, parse_number
from visualization.chart_context import BundleContext, ColumnView, parse_numeric_rows
from visualization.chart_data import ChartData

MAX_CORRELATION_FIELDS = 6
MAX_PAIRPLOT_FIELDS = 4
MIN_ASSOCIATION_N = 30
MAX_SCATTER_POINTS = 2_000
MAX_CROSSTAB_LEVELS = 12
MAX_DENSITY_BINS = 24
MAX_GROUP_BOXPLOTS = 6
MAX_PAIRPLOT_VARIABLES = 4
MAX_CRAMERS_FIELDS = 5
MAX_CROSSTAB_CHARTS = 4


def _parse(value: Any) -> float | None:
    number = parse_number(value)
    return float(number) if number is not None else None


def _source_rows(context: BundleContext, source_id: str) -> tuple[Any, ...]:
    return context.rows_for_source(source_id)


def _measure_columns_for_source(
    context: BundleContext, source_id: str
) -> list[ColumnView]:
    return [
        column for column in context.measure_columns() if column.source_id == source_id
    ]


def build_relationship_charts(context: BundleContext) -> list[ChartData]:
    charts: list[ChartData] = []
    charts.extend(_approved_scatter_charts(context))
    charts.extend(_correlation_charts(context))
    charts.extend(_crosstab_charts(context))
    charts.extend(_comissing_chart(context))
    charts.extend(_fanout_chart(context))
    charts.extend(_density_charts(context))
    charts.extend(_group_boxplot_charts(context))
    charts.extend(_pairplot_charts(context))
    return charts


def _density_charts(context: BundleContext) -> list[ChartData]:
    charts: list[ChartData] = []
    grouped: dict[str, list[ColumnView]] = {}
    for column in context.measure_columns():
        grouped.setdefault(column.source_id, []).append(column)
    for source_id, columns in sorted(grouped.items()):
        if len(columns) < 2:
            continue
        rows = _source_rows(context, source_id)
        if len(rows) < MIN_ASSOCIATION_N:
            continue
        field_x = columns[0]
        field_y = columns[1]
        pairs: list[tuple[float, float]] = []
        for row in rows:
            left = _parse(row.get(field_x.column))
            right = _parse(row.get(field_y.column))
            if left is None or right is None:
                continue
            pairs.append((left, right))
        if len(pairs) < MIN_ASSOCIATION_N:
            continue
        matrix, x_edges, y_edges = _bin2d_counts(pairs)
        if not matrix:
            continue
        charts.append(
            ChartData(
                chart_id="REL02",
                split=context.split,
                business_id=context.business_of_source(source_id),
                kind="heatmap",
                payload={
                    "matrix": matrix,
                    "rows": [f"{field_y.column} bin {index}" for index in range(len(y_edges) - 1)],
                    "columns": [f"{field_x.column} bin {index}" for index in range(len(x_edges) - 1)],
                },
                source_ids=(source_id,),
                population_n=len(pairs),
                sample_n=len(pairs),
                method="bin2d_counts_same_source",
                unit="count",
                denominator_label="tổng số cặp quan sát hợp lệ trong lưới nhị phân",
                title=(
                    f"Mật độ quan sát trên lưới hai chiều — "
                    f"{context.business_of_source(source_id)}"
                ),
                x_label=f"{field_x.column} (nhị phân)",
                y_label=f"{field_y.column} (nhị phân)",
                limitations=(
                    "bin edges are computed on the observed sample and are not stable across runs",
                    "the grid is computed inside a single source without joins",
                ),
                metadata={
                    "caption": (
                        f"Lưới nhị phân {len(x_edges) - 1}×{len(y_edges) - 1} trên "
                        f"{len(pairs)} cặp quan sát hợp lệ; tổng đếm bằng n."
                    ),
                    "x_edges": x_edges,
                    "y_edges": y_edges,
                },
            )
        )
        if len(charts) >= 3:
            break
    return charts


def _bin2d_counts(
    pairs: Sequence[tuple[float, float]],
) -> tuple[list[list[float]], list[float], list[float]]:
    xs = sorted(value for value, _ in pairs)
    ys = sorted(value for _, value in pairs)
    x_edges = _bin_edges(xs, MAX_DENSITY_BINS)
    y_edges = _bin_edges(ys, MAX_DENSITY_BINS)
    matrix = [
        [0.0 for _ in range(len(x_edges) - 1)] for _ in range(len(y_edges) - 1)
    ]
    for value_x, value_y in pairs:
        column = _bin_index(value_x, x_edges)
        row = _bin_index(value_y, y_edges)
        matrix[row][column] += 1.0
    return matrix, x_edges, y_edges


def _bin_edges(ordered: Sequence[float], maximum_bins: int) -> list[float]:
    if not ordered:
        return [0.0, 1.0]
    minimum = ordered[0]
    maximum = ordered[-1]
    if maximum <= minimum:
        return [minimum, minimum + 1.0]
    span = maximum - minimum
    bins = max(1, min(maximum_bins, int(span ** (1 / 3)) + 1))
    step = span / bins
    return [minimum + step * index for index in range(bins + 1)]


def _bin_index(value: float, edges: Sequence[float]) -> int:
    if len(edges) < 2:
        return 0
    if value >= edges[-1]:
        return len(edges) - 2
    if value <= edges[0]:
        return 0
    for index in range(len(edges) - 1):
        if edges[index] <= value < edges[index + 1]:
            return index
    return len(edges) - 2


def _group_boxplot_charts(context: BundleContext) -> list[ChartData]:
    charts: list[ChartData] = []
    measures_by_source: dict[str, list[ColumnView]] = {}
    for column in context.measure_columns():
        measures_by_source.setdefault(column.source_id, []).append(column)
    categories_by_source: dict[str, list[ColumnView]] = {}
    for column in context.categorical_columns():
        categories_by_source.setdefault(column.source_id, []).append(column)
    for source_id in sorted(measures_by_source):
        if len(charts) >= MAX_GROUP_BOXPLOTS:
            break
        categories = categories_by_source.get(source_id)
        if not categories:
            continue
        rows = _source_rows(context, source_id)
        if len(rows) < MIN_ASSOCIATION_N:
            continue
        group_field = categories[0]
        measure_field = measures_by_source[source_id][0]
        labels, values, total_n, dropped_n = group_value_buckets(
            rows, group_field.column, measure_field.column, _parse
        )
        if len(labels) < 2:
            continue
        groups = [list(item) for item in values]
        display_labels = [
            f"{label} (n={len(values[index])})" for index, label in enumerate(labels)
        ]
        charts.append(
            ChartData(
                chart_id="REL06",
                split=context.split,
                business_id=context.business_of_source(source_id),
                kind="boxplot",
                payload={"groups": groups, "labels": display_labels},
                source_ids=(source_id,),
                population_n=total_n,
                sample_n=sum(len(item) for item in groups),
                method="group_quantiles_boxplot",
                unit="source unit",
                denominator_label="số quan sát hợp lệ theo nhóm phân loại",
                title=(
                    f"Phân phối đo lường theo nhóm phân loại — "
                    f"{context.business_of_source(source_id)}"
                ),
                x_label=group_field.column,
                y_label=f"{measure_field.column} ({measure_field.unit or 'unit'})",
                limitations=(
                    "groups below the minimum observation threshold are excluded",
                    "group differences are descriptive and do not imply causation",
                ),
                metadata={
                    "caption": (
                        f"Median và IQR của {measure_field.column} theo "
                        f"{group_field.column} trên {total_n} quan sát; "
                        f"{dropped_n} quan sát bị loại vì thiếu giá trị hợp lệ."
                    ),
                    "dropped_n": dropped_n,
                },
            )
        )
    return charts


def _pairplot_charts(context: BundleContext) -> list[ChartData]:
    charts: list[ChartData] = []
    grouped: dict[str, list[ColumnView]] = {}
    for column in context.measure_columns():
        grouped.setdefault(column.source_id, []).append(column)
    for source_id, columns in sorted(grouped.items()):
        if len(charts) >= 2:
            break
        usable = columns[:MAX_PAIRPLOT_VARIABLES]
        if len(usable) < 2:
            continue
        rows = _source_rows(context, source_id)
        if len(rows) < MIN_ASSOCIATION_N:
            continue
        fields = [column.column for column in usable]
        parsed, _dropped = parse_numeric_rows(rows, fields)
        charts.append(
            ChartData(
                chart_id="REL09",
                split=context.split,
                business_id=context.business_of_source(source_id),
                kind="heatmap",
                payload={
                    "matrix": _pearson_matrix(parsed),
                    "rows": fields,
                    "columns": fields,
                },
                source_ids=(source_id,),
                population_n=len(rows),
                sample_n=len(rows),
                method="selected_pairplot_correlation_matrix",
                unit="unitless",
                denominator_label="cặp quan sát hoàn chỉnh trong cùng nguồn",
                title=(
                    f"Pairplot chọn lọc các đo lường — "
                    f"{context.business_of_source(source_id)}"
                ),
                x_label="Biến",
                y_label="Biến",
                limitations=(
                    "the pairplot is limited to a bounded number of selected measures",
                    "correlation does not imply causation",
                ),
                metadata={
                    "caption": (
                        f"Ma trận phân tán của {len(fields)} đo lường được chọn trong "
                        f"nguồn {source_id} trên {len(rows)} dòng."
                    ),
                    "fields": fields,
                },
            )
        )
    return charts


def _pearson_matrix(parsed: dict[str, list[float]]) -> list[list[float]]:
    fields = list(parsed)
    size = len(fields)
    matrix = [[0.0] * size for _ in range(size)]
    for index_x in range(size):
        matrix[index_x][index_x] = 1.0
        for index_y in range(index_x + 1, size):
            value = _pearson(parsed[fields[index_x]], parsed[fields[index_y]])
            matrix[index_x][index_y] = value
            matrix[index_y][index_x] = value
    return matrix


def _pearson(xs: Sequence[float], ys: Sequence[float]) -> float:
    count = min(len(xs), len(ys))
    if count < 2:
        return 0.0
    mean_x = sum(xs[:count]) / count
    mean_y = sum(ys[:count]) / count
    covariance = sum(
        (xs[index] - mean_x) * (ys[index] - mean_y) for index in range(count)
    )
    variance_x = sum((value - mean_x) ** 2 for value in xs[:count])
    variance_y = sum((value - mean_y) ** 2 for value in ys[:count])
    if variance_x <= 0 or variance_y <= 0:
        return 0.0
    return round(covariance / (variance_x**0.5 * variance_y**0.5), 6)


def _approved_scatter_charts(context: BundleContext) -> list[ChartData]:
    charts: list[ChartData] = []
    eligibilities = eligible_relations(context.bundle.relations)
    approved = [item for item in eligibilities if item.eligible]
    for eligibility in approved[:4]:
        left_source = eligibility.left_source
        right_source = eligibility.right_source
        left_columns = _measure_columns_for_source(context, left_source)
        right_columns = _measure_columns_for_source(context, right_source)
        if not left_columns or not right_columns:
            continue
        left_field = left_columns[0]
        right_field = right_columns[0]
        left_rows = _source_rows(context, left_source)
        right_rows = _source_rows(context, right_source)
        joined = _join_on_keys(
            left_rows, right_rows, eligibility.join_keys
        )
        if len(joined) < MIN_ASSOCIATION_N:
            continue
        xs: list[float] = []
        ys: list[float] = []
        for left_row, right_row in joined:
            left_value = _parse(left_row.get(left_field.column))
            right_value = _parse(right_row.get(right_field.column))
            if left_value is None or right_value is None:
                continue
            xs.append(left_value)
            ys.append(right_value)
        if len(xs) < MIN_ASSOCIATION_N:
            continue
        if len(xs) > MAX_SCATTER_POINTS:
            step = len(xs) / MAX_SCATTER_POINTS
            xs = [xs[int(index * step)] for index in range(MAX_SCATTER_POINTS)]
            ys = [ys[int(index * step)] for index in range(MAX_SCATTER_POINTS)]
        tau = kendall_tau_b(xs, ys)
        charts.append(
            ChartData(
                chart_id="REL01",
                split=context.split,
                business_id=eligibility.business_id,
                kind="scatter",
                payload={"x": xs, "y": ys},
                source_ids=(left_source, right_source),
                population_n=len(joined),
                sample_n=len(xs),
                method="paired_scatter_on_approved_join",
                unit="source unit",
                denominator_label="cặp quan sát hoàn chỉnh trên phép nối đã phê duyệt",
                title=f"Phân tán hai đo lường cùng grain — {eligibility.business_id}",
                x_label=f"{left_field.column} ({left_field.unit or 'unit'})",
                y_label=f"{right_field.column} ({right_field.unit or 'unit'})",
                limitations=(
                    "correlation does not imply causation",
                    "join is restricted to relations with approval status and no fanout",
                ),
                metadata={
                    "caption": (
                        f"{len(xs)} cặp quan sát hoàn chỉnh trên phép nối được phê "
                        f"duyệt giữa {left_source} và {right_source}; "
                        f"Kendall tau-b = {tau:.6g}." if tau is not None else
                        f"{len(xs)} cặp quan sát hoàn chỉnh trên phép nối được phê duyệt."
                    ),
                    "kendall_tau_b": tau,
                    "join_keys": list(eligibility.join_keys),
                },
            )
        )
    return charts


def _join_on_keys(
    left_rows: Sequence[Any],
    right_rows: Sequence[Any],
    join_keys: Sequence[str],
) -> list[tuple[dict[str, Any], dict[str, Any]]]:
    if not join_keys:
        return []
    def key_of(row: Any) -> tuple[str, ...] | None:
        values = tuple(str(row.get(column, "")).strip() for column in join_keys)
        if any(value == "" for value in values):
            return None
        return values

    index: dict[tuple[str, ...], dict[str, Any]] = {}
    for row in right_rows:
        key = key_of(row)
        if key is not None and key not in index:
            index[key] = dict(row)
    pairs: list[tuple[dict[str, Any], dict[str, Any]]] = []
    for row in left_rows:
        key = key_of(row)
        if key is None:
            continue
        match = index.get(key)
        if match is not None:
            pairs.append((dict(row), match))
    return pairs


def _correlation_charts(context: BundleContext) -> list[ChartData]:
    charts: list[ChartData] = []
    grouped: dict[str, list[ColumnView]] = {}
    for column in context.measure_columns():
        grouped.setdefault(column.source_id, []).append(column)
    for source_id, columns in sorted(grouped.items()):
        usable = columns[:MAX_CORRELATION_FIELDS]
        if len(usable) < 2:
            continue
        rows = _source_rows(context, source_id)
        if len(rows) < MIN_ASSOCIATION_N:
            continue
        fields = [column.column for column in usable]
        for chart_id, method in (
            ("REL03", "pearson"),
            ("REL04", "spearman"),
            ("REL05", "kendall"),
        ):
            if method == "kendall":
                matrix = _kendall_matrix(fields, rows)
            else:
                names, values, notes = correlation_matrix(
                    fields, rows, _parse, method=method
                )
                matrix = [[0.0 if item is None else float(item) for item in row] for row in values]
            if not matrix:
                continue
            charts.append(
                ChartData(
                    chart_id=chart_id,
                    split=context.split,
                    business_id=context.business_of_source(source_id),
                    kind="heatmap",
                    payload={
                        "matrix": matrix,
                        "rows": fields,
                        "columns": fields,
                    },
                    source_ids=(source_id,),
                    population_n=len(rows),
                    sample_n=None,
                    method=f"{method}_correlation_matrix_same_source",
                    unit="unitless",
                    denominator_label="cặp quan sát hoàn chỉnh trong cùng một nguồn",
                    title=(
                        f"Ma trận tương quan {method.capitalize()} — "
                        f"{context.business_of_source(source_id)}"
                    ),
                    x_label="Biến",
                    y_label="Biến",
                    limitations=(
                        "correlation does not imply causation",
                        "constant columns are excluded and reported as null",
                    ),
                    metadata={
                        "caption": (
                            f"Ma trận tương quan {method} của {len(fields)} đo lường "
                            f"trong cùng nguồn {source_id}; n={len(rows)} dòng mẫu."
                        ),
                        "fields": fields,
                    },
                )
            )
    return charts


def _kendall_matrix(
    fields: Sequence[str], rows: Sequence[Any]
) -> list[list[float]]:
    size = len(fields)
    matrix = [[0.0] * size for _ in range(size)]
    for index_x in range(size):
        matrix[index_x][index_x] = 1.0
        for index_y in range(index_x + 1, size):
            xs: list[float] = []
            ys: list[float] = []
            for row in rows:
                left = _parse(row.get(fields[index_x]))
                right = _parse(row.get(fields[index_y]))
                if left is None or right is None:
                    continue
                xs.append(left)
                ys.append(right)
            tau = kendall_tau_b(xs, ys)
            value = 0.0 if tau is None else float(tau)
            matrix[index_x][index_y] = value
            matrix[index_y][index_x] = value
    return matrix


def _crosstab_charts(context: BundleContext) -> list[ChartData]:
    charts: list[ChartData] = []
    grouped: dict[str, list[ColumnView]] = {}
    for column in context.categorical_columns():
        grouped.setdefault(column.source_id, []).append(column)
    for source_id, columns in sorted(grouped.items()):
        if len(charts) >= MAX_CROSSTAB_CHARTS:
            break
        if len(columns) < 2:
            continue
        rows = _source_rows(context, source_id)
        if len(rows) < MIN_ASSOCIATION_N:
            continue
        pair = _select_categorical_pair(rows, columns)
        if pair is None:
            continue
        field_x, field_y, association = pair
        charts.append(
            ChartData(
                chart_id="REL07",
                split=context.split,
                business_id=context.business_of_source(source_id),
                kind="heatmap",
                payload={
                    "matrix": [[float(value) for value in row] for row in association.counts],
                    "rows": list(association.x_labels),
                    "columns": list(association.y_labels),
                },
                source_ids=(source_id,),
                population_n=association.total_n,
                sample_n=None,
                method="crosstab_counts_same_source",
                unit="count",
                denominator_label="tổng số quan sát hợp lệ của bảng chéo",
                title=(
                    f"Ma trận liên hệ hai trường phân loại — "
                    f"{context.business_of_source(source_id)}"
                ),
                x_label=field_y.column,
                y_label=field_x.column,
                limitations=(
                    "association does not imply causation",
                    "crosstab is computed inside a single source without joins",
                ),
                metadata={
                    "caption": (
                        f"Bảng chéo giữa {field_x.column} và {field_y.column}; "
                        f"tổng = {association.total_n} quan sát."
                    ),
                    "cramers_v": association.cramers_v,
                    "chi_square": association.chi_square,
                    "min_expected_count": association.min_expected_count,
                    "status": association.status,
                    "reason": association.reason,
                },
            )
        )
    charts.extend(_cramers_v_matrix_charts(context))
    return charts


def _select_categorical_pair(
    rows: Sequence[Any],
    columns: Sequence[ColumnView],
) -> tuple[ColumnView, ColumnView, Any] | None:
    candidates: list[tuple[int, int, ColumnView, ColumnView]] = []
    for index_x in range(len(columns)):
        for index_y in range(index_x + 1, len(columns)):
            candidates.append(
                (
                    columns[index_x].distinct_n + columns[index_y].distinct_n,
                    index_y - index_x,
                    columns[index_x],
                    columns[index_y],
                )
            )
    for _cardinality, _gap, field_x, field_y in sorted(
        candidates, key=lambda item: (item[0], item[1])
    ):
        association = crosstab_association(rows, field_x.column, field_y.column)
        if association.status == "NOT_APPLICABLE":
            continue
        if len(association.x_labels) > MAX_CROSSTAB_LEVELS or len(
            association.y_labels
        ) > MAX_CROSSTAB_LEVELS:
            continue
        return field_x, field_y, association
    return None


def _cramers_v_matrix_charts(context: BundleContext) -> list[ChartData]:
    charts: list[ChartData] = []
    grouped: dict[str, list[ColumnView]] = {}
    for column in context.categorical_columns():
        grouped.setdefault(column.source_id, []).append(column)
    for source_id, columns in sorted(grouped.items()):
        if len(charts) >= 2:
            break
        fields = [column.column for column in columns[:MAX_CRAMERS_FIELDS]]
        if len(fields) < 2:
            continue
        rows = _source_rows(context, source_id)
        if len(rows) < MIN_ASSOCIATION_N:
            continue
        matrix: list[list[float]] = []
        pairs: list[str] = []
        for index_x in range(len(fields)):
            row_values: list[float] = []
            for index_y in range(len(fields)):
                if index_x == index_y:
                    row_values.append(1.0)
                    continue
                association = crosstab_association(rows, fields[index_x], fields[index_y])
                if association.cramers_v is None:
                    row_values.append(0.0)
                    continue
                row_values.append(float(association.cramers_v))
            matrix.append(row_values)
        pairs = [f"{fields[index_x]} × {fields[index_y]}" for index_x in range(len(fields))]
        charts.append(
            ChartData(
                chart_id="REL08",
                split=context.split,
                business_id=context.business_of_source(source_id),
                kind="heatmap",
                payload={"matrix": matrix, "rows": fields, "columns": fields},
                source_ids=(source_id,),
                population_n=len(rows),
                sample_n=None,
                method="cramers_v_matrix_same_source",
                unit="unitless",
                denominator_label="tổng số quan sát hợp lệ của từng bảng chéo",
                title=(
                    f"Ma trận Cramér V giữa các cặp phân loại — "
                    f"{context.business_of_source(source_id)}"
                ),
                x_label="Trường phân loại",
                y_label="Trường phân loại",
                limitations=(
                    "association does not imply causation",
                    "small expected cell counts reduce reliability",
                    "pairs that cannot be computed are reported as zero",
                ),
                metadata={
                    "caption": (
                        f"Cramér V giữa {len(fields)} trường phân loại trong nguồn "
                        f"{source_id}; giá trị 1 trên đường chéo là quy ước."
                    ),
                    "fields": fields,
                    "pairs": pairs,
                },
            )
        )
    return charts


def _comissing_chart(context: BundleContext) -> list[ChartData]:
    charts: list[ChartData] = []
    for source_id in sorted(context.bundle.row_samples):
        rows = context.rows_for_source(source_id)
        if not rows:
            continue
        fields = sorted({key for row in rows[:200] for key in row})
        masks: dict[str, list[bool]] = {}
        for field in fields[:24]:
            masks[field] = [is_blank(row.get(field)) for row in rows]
        if len(masks) < 2:
            continue
        names, matrix, notes = co_missing_matrix(masks)
        if not matrix:
            continue
        charts.append(
            ChartData(
                chart_id="REL10",
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
                method="pairwise_co_missing_ratio",
                unit="percent",
                denominator_label="số dòng mẫu của nguồn",
                title=f"Ma trận thiếu giá trị đồng kiện — {context.business_of_source(source_id)}",
                x_label="Trường",
                y_label="Trường",
                limitations=(
                    "co-missingness is computed on a bounded row sample",
                    "constant missing masks are reported as null cells",
                ),
                metadata={
                    "caption": (
                        f"Tỷ trọng thiếu đồng kiện giữa {len(names)} trường của nguồn "
                        f"{source_id} trên {len(rows)} dòng mẫu."
                    ),
                    "notes": list(notes),
                },
            )
        )
        break
    return charts


def _fanout_chart(context: BundleContext) -> list[ChartData]:
    eligibilities = eligible_relations(context.bundle.relations)
    if not eligibilities:
        return []
    xs: list[float] = []
    ys: list[float] = []
    statuses: list[str] = []
    for item in eligibilities:
        xs.append(float(item.fanout_factor))
        total = item.matched_rows + item.unmatched_left_rows + item.unmatched_right_rows
        ys.append(
            round(
                (item.unmatched_left_rows + item.unmatched_right_rows) / total * 100.0, 6
            )
            if total
            else 0.0
        )
        statuses.append(item.status.value)
    return [
        ChartData(
            chart_id="QUAL07",
            split=context.split,
            business_id="global",
            kind="scatter",
            payload={"x": xs, "y": ys},
            source_ids=tuple(item.relation_id for item in eligibilities),
            population_n=len(eligibilities),
            sample_n=len(eligibilities),
            method="fanout_factor_versus_orphan_share",
            unit="factor",
            denominator_label="tổng số khóa khớp và khóa lệch của quan hệ",
            title="Rủi ro nhân bản khi nối bảng",
            x_label="Hệ số nhân bản (fanout)",
            y_label="Tỷ lệ khóa không khớp (%)",
            limitations=(
                "candidate joins are displayed for risk only and never used for KPI",
                "approval status of each relation is preserved unchanged",
            ),
            metadata={
                "caption": (
                    f"{len(eligibilities)} quan hệ ứng viên/đã phê duyệt với hệ số "
                    "nhân bản và tỷ lệ khóa lệch; trạng thái phê duyệt được giữ nguyên."
                ),
                "statuses": statuses,
            },
        )
    ]
