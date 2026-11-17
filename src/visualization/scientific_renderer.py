from __future__ import annotations

import hashlib
import os
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping, Sequence

os.environ.setdefault(
    "MPLCONFIGDIR", os.path.join(tempfile.gettempdir(), "megaxis_eda_mplconfig")
)

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt

from common.enums import Status
from visualization.chart_data import ChartData, is_renderable
from visualization.figure_theme import (
    FigureTheme,
    apply_theme,
    add_caption,
    format_tick_values,
    resolve_font_family,
    style_axes,
    thousands_axis,
)

MAX_LABELS = 60
HEATMAP_MAX_ROWS = 60
HEATMAP_MAX_COLUMNS = 40
SERIES_COLORS = (
    "#1769AA",
    "#087B5A",
    "#A36516",
    "#B32336",
    "#5A4FCF",
    "#66768A",
)


@dataclass(frozen=True)
class RenderedFigure:
    figure_id: str
    chart_id: str
    split: str
    business_id: str
    png_path: Path
    content_hash: str
    status: Status
    reason: str
    population_n: int | None
    sample_n: int | None
    method: str
    unit: str
    byte_size: int

    def to_dict(self) -> dict[str, Any]:
        return {
            "figure_id": self.figure_id,
            "chart_id": self.chart_id,
            "split": self.split,
            "business_id": self.business_id,
            "png_path": str(self.png_path),
            "content_hash": self.content_hash,
            "status": self.status.value,
            "reason": self.reason,
            "population_n": self.population_n,
            "sample_n": self.sample_n,
            "method": self.method,
            "unit": self.unit,
            "byte_size": self.byte_size,
        }


def _truncate_labels(
    labels: Sequence[str], values: Sequence[float]
) -> tuple[list[str], list[float]]:
    if len(labels) <= MAX_LABELS:
        return list(labels), list(values)
    order = sorted(range(len(values)), key=lambda index: values[index], reverse=True)
    kept = sorted(order[:MAX_LABELS])
    return [labels[index] for index in kept], [values[index] for index in kept]


def _short(text: str, limit: int = 34) -> str:
    if len(text) <= limit:
        return text
    return text[: limit - 1] + "…"


def _heatmap_extent(
    matrix: Sequence[Sequence[float]], rows: Sequence[str], columns: Sequence[str]
) -> tuple[list[str], list[str], list[list[float]]]:
    trimmed_rows = list(rows[:HEATMAP_MAX_ROWS])
    trimmed_columns = list(columns[:HEATMAP_MAX_COLUMNS])
    trimmed_matrix = [
        [float(value) for value in row[:HEATMAP_MAX_COLUMNS]]
        for row in matrix[:HEATMAP_MAX_ROWS]
    ]
    return trimmed_rows, trimmed_columns, trimmed_matrix


def _draw_heatmap(axis: Any, data: ChartData) -> None:
    payload = data.payload
    rows, columns, matrix = _heatmap_extent(
        payload.get("matrix", []), payload.get("rows", []), payload.get("columns", [])
    )
    image = axis.imshow(matrix, aspect="auto", cmap="Blues")
    axis.set_xticks(range(len(columns)))
    axis.set_xticklabels([_short(str(item), 18) for item in columns], rotation=45, ha="right", fontsize=7)
    axis.set_yticks(range(len(rows)))
    axis.set_yticklabels([_short(str(item), 26) for item in rows], fontsize=7)
    style_axes(axis, data.title, data.x_label, data.y_label, grid_axis="both")
    axis.figure.colorbar(image, ax=axis, fraction=0.03, pad=0.02)


def _draw_grouped_or_stacked(axis: Any, data: ChartData) -> None:
    payload = data.payload
    labels = [str(item) for item in payload.get("labels", [])]
    series = list(payload.get("series", []))
    if not series:
        values = [float(item) for item in payload.get("values", [])]
        axis.bar(labels, values, color=SERIES_COLORS[0], edgecolor="none")
    elif data.kind == "stacked_bar":
        bottom = [0.0] * len(labels)
        for index, item in enumerate(series):
            values = [float(value) for value in item.get("values", [])]
            axis.bar(
                labels,
                values,
                bottom=bottom,
                label=str(item.get("label", "")),
                color=SERIES_COLORS[index % len(SERIES_COLORS)],
                edgecolor="none",
            )
            bottom = [base + value for base, value in zip(bottom, values)]
    else:
        width = 0.8 / max(len(series), 1)
        positions = list(range(len(labels)))
        for index, item in enumerate(series):
            values = [float(value) for value in item.get("values", [])]
            offsets = [
                position + (index - (len(series) - 1) / 2) * width
                for position in positions
            ]
            axis.bar(
                offsets,
                values,
                width=width,
                label=str(item.get("label", "")),
                color=SERIES_COLORS[index % len(SERIES_COLORS)],
                edgecolor="none",
            )
        axis.set_xticks(positions)
        axis.set_xticklabels(labels)
    style_axes(axis, data.title, data.x_label, data.y_label)
    if series:
        axis.legend(frameon=False, fontsize=8)


def _draw_timeline(axis: Any, data: ChartData) -> None:
    payload = data.payload
    rows = [str(item) for item in payload.get("rows", [])]
    starts = [float(item) for item in payload.get("starts", [])]
    ends = [float(item) for item in payload.get("ends", [])]
    positions = list(range(len(rows)))
    for position, start, end in zip(positions, starts, ends):
        axis.barh(position, max(end - start, 0.0), left=start, height=0.6, color=SERIES_COLORS[0])
    axis.set_yticks(positions)
    axis.set_yticklabels([_short(item, 26) for item in rows], fontsize=7)
    style_axes(axis, data.title, data.x_label, data.y_label, grid_axis="x")


def _draw_pareto(axis: Any, data: ChartData) -> None:
    payload = data.payload
    labels = [str(item) for item in payload.get("labels", [])]
    values = [float(item) for item in payload.get("values", [])]
    cumulative = [float(item) for item in payload.get("cumulative", [])]
    positions = list(range(len(labels)))
    axis.bar(positions, values, color=SERIES_COLORS[0], edgecolor="none", label="Số dòng")
    axis.set_xticks(positions)
    axis.set_xticklabels([_short(item, 16) for item in labels], rotation=45, ha="right", fontsize=7)
    twin = axis.twinx()
    twin.plot(positions, cumulative, color=SERIES_COLORS[3], marker="o", linewidth=1.6, label="Tỷ trọng tích lũy")
    twin.set_ylim(0, 105)
    twin.set_ylabel("Tỷ trọng tích lũy (%)")
    twin.grid(False)
    style_axes(axis, data.title, data.x_label, data.y_label)
    handles_left, labels_left = axis.get_legend_handles_labels()
    handles_right, labels_right = twin.get_legend_handles_labels()
    axis.legend(handles_left + handles_right, labels_left + labels_right, frameon=False, fontsize=8)


def _draw_scatter(axis: Any, data: ChartData) -> None:
    payload = data.payload
    xs = [float(item) for item in payload.get("x", [])]
    ys = [float(item) for item in payload.get("y", [])]
    axis.scatter(xs, ys, s=10, alpha=0.5, color=SERIES_COLORS[0], edgecolor="none")
    style_axes(axis, data.title, data.x_label, data.y_label, grid_axis="both")


def _draw_hexbin(axis: Any, data: ChartData) -> None:
    payload = data.payload
    xs = [float(item) for item in payload.get("x", [])]
    ys = [float(item) for item in payload.get("y", [])]
    image = axis.hexbin(xs, ys, gridsize=35, cmap="Blues", mincnt=1)
    style_axes(axis, data.title, data.x_label, data.y_label, grid_axis="both")
    axis.figure.colorbar(image, ax=axis, fraction=0.03, pad=0.02)


def _draw_box_violin(axis: Any, data: ChartData) -> None:
    payload = data.payload
    groups = [[float(value) for value in group] for group in payload.get("groups", [])]
    labels = [str(item) for item in payload.get("labels", [])]
    if data.kind == "violin":
        axis.violinplot(groups, showmedians=True, showextrema=False)
    else:
        axis.boxplot(groups, showfliers=False)
    axis.set_xticks(range(1, len(labels) + 1))
    axis.set_xticklabels([_short(item, 18) for item in labels], fontsize=8)
    style_axes(axis, data.title, data.x_label, data.y_label)


def _draw_ecdf(axis: Any, data: ChartData) -> None:
    payload = data.payload
    xs = [float(item) for item in payload.get("x", [])]
    ys = [float(item) for item in payload.get("y", [])]
    axis.plot(xs, ys, color=SERIES_COLORS[0], linewidth=1.8)
    axis.set_ylim(0, 1.02)
    style_axes(axis, data.title, data.x_label, data.y_label, grid_axis="both")


def _draw_histogram(axis: Any, data: ChartData) -> None:
    payload = data.payload
    values = [float(item) for item in payload.get("values", [])]
    edges = payload.get("edges")
    bins = int(payload.get("bins") or 0)
    if edges and len(edges) == bins + 1:
        axis.bar(
            list(edges[:-1]),
            [float(count) for count in payload.get("counts", [])],
            width=(float(edges[1]) - float(edges[0])) if bins else 1.0,
            align="edge",
            color=SERIES_COLORS[0],
            edgecolor="white",
            linewidth=0.4,
        )
    else:
        axis.hist(values, bins=bins or 20, color=SERIES_COLORS[0], edgecolor="white", linewidth=0.4)
    style_axes(axis, data.title, data.x_label, data.y_label)


def _draw_bar(axis: Any, data: ChartData) -> None:
    payload = data.payload
    labels = [str(item) for item in payload.get("labels", [])]
    values = [float(item) for item in payload.get("values", [])]
    if data.kind == "horizontal_bar":
        kept_labels, kept_values = _truncate_labels(labels, values)
        axis.barh(kept_labels, kept_values, color=SERIES_COLORS[0], edgecolor="none")
        style_axes(axis, data.title, data.y_label, data.x_label, grid_axis="x")
    else:
        axis.bar(labels, values, color=SERIES_COLORS[0], edgecolor="none")
        style_axes(axis, data.title, data.x_label, data.y_label)


def _draw_line(axis: Any, data: ChartData) -> None:
    payload = data.payload
    labels = [str(item) for item in payload.get("labels", [])]
    values = [float(item) for item in payload.get("values", [])]
    axis.plot(labels, values, color=SERIES_COLORS[0], linewidth=1.6)
    if payload.get("log_x"):
        axis.set_xscale("log")
    style_axes(axis, data.title, data.x_label, data.y_label, grid_axis="both")


def render_chart_data(
    data: ChartData,
    output_path: Path,
    theme: FigureTheme | None = None,
    svg_path: Path | None = None,
) -> RenderedFigure:
    resolved_theme = theme or FigureTheme(font_family=resolve_font_family())
    apply_theme(resolved_theme)
    if data.status != Status.PASS:
        return RenderedFigure(
            figure_id=f"{data.chart_id}.{data.split}.{data.business_id}",
            chart_id=data.chart_id,
            split=data.split,
            business_id=data.business_id,
            png_path=output_path,
            content_hash="",
            status=data.status,
            reason=data.reason or "chart_data_not_pass",
            population_n=data.population_n,
            sample_n=data.sample_n,
            method=data.method,
            unit=data.unit,
            byte_size=0,
        )
    if not is_renderable(data):
        return RenderedFigure(
            figure_id=f"{data.chart_id}.{data.split}.{data.business_id}",
            chart_id=data.chart_id,
            split=data.split,
            business_id=data.business_id,
            png_path=output_path,
            content_hash="",
            status=Status.BLOCKED,
            reason="chart_payload_has_no_usable_observation",
            population_n=data.population_n,
            sample_n=data.sample_n,
            method=data.method,
            unit=data.unit,
            byte_size=0,
        )
    output_path.parent.mkdir(parents=True, exist_ok=True)
    figure, axis = plt.subplots(
        figsize=(resolved_theme.figure_width, resolved_theme.figure_height)
    )
    try:
        kind = data.kind
        if kind == "heatmap":
            _draw_heatmap(axis, data)
        elif kind in {"grouped_bar", "stacked_bar"}:
            _draw_grouped_or_stacked(axis, data)
        elif kind == "timeline":
            _draw_timeline(axis, data)
        elif kind == "pareto":
            _draw_pareto(axis, data)
        elif kind == "scatter":
            _draw_scatter(axis, data)
        elif kind == "hexbin":
            _draw_hexbin(axis, data)
        elif kind in {"boxplot", "violin"}:
            _draw_box_violin(axis, data)
        elif kind == "ecdf":
            _draw_ecdf(axis, data)
        elif kind == "histogram":
            _draw_histogram(axis, data)
        elif kind == "horizontal_bar":
            _draw_bar(axis, data)
        elif kind == "bar":
            _draw_bar(axis, data)
        elif kind == "dot":
            _draw_bar(axis, data)
        elif kind == "line":
            _draw_line(axis, data)
        else:
            raise ValueError(f"unsupported chart data kind: {kind}")
        sample_note = ""
        if data.sample_n is not None and data.population_n is not None:
            sample_note = (
                f"Sample n={data.sample_n:,} trên population N={data.population_n:,}; "
                f"mẫu số: {data.denominator_label}"
            ).replace(",", ".")
        elif data.population_n is not None:
            sample_note = (
                f"N={data.population_n:,}; mẫu số: {data.denominator_label}"
            ).replace(",", ".")
        source_note = f"Nguồn: {', '.join(data.source_ids[:4])}" if data.source_ids else ""
        add_caption(figure, data.metadata.get("caption", "") or data.title, sample_note, source_note, resolved_theme)
        figure.tight_layout(rect=(0, 0.04, 1, 1))
        figure.savefig(output_path, dpi=resolved_theme.dpi)
        if svg_path is not None:
            svg_path.parent.mkdir(parents=True, exist_ok=True)
            figure.savefig(svg_path, format="svg")
    finally:
        plt.close(figure)
    payload = output_path.read_bytes()
    return RenderedFigure(
        figure_id=f"{data.chart_id}.{data.split}.{data.business_id}",
        chart_id=data.chart_id,
        split=data.split,
        business_id=data.business_id,
        png_path=output_path,
        content_hash=f"sha256:{hashlib.sha256(payload).hexdigest()}",
        status=Status.PASS,
        reason="rendered",
        population_n=data.population_n,
        sample_n=data.sample_n,
        method=data.method,
        unit=data.unit,
        byte_size=len(payload),
    )
