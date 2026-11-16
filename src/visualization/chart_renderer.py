from __future__ import annotations

import hashlib
import inspect
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
from common.contracts import ChartSpecification
from common.enums import ChartType, Status

RENDER_WIDTH = 10.0
RENDER_HEIGHT = 6.0
RENDER_DPI = 130
PALETTE = (
    "#1769AA",
    "#087B5A",
    "#A36516",
    "#B32336",
    "#5A4FCF",
    "#66768A",
)
MAX_LABELS = 60


@dataclass(frozen=True)
class RenderedChart:
    chart_id: str
    output_path: Path
    content_hash: str
    status: Status
    reason: str
    row_count: int
    column_count: int
    truncated: bool

    def to_dict(self) -> dict[str, Any]:
        return {
            "chart_id": self.chart_id,
            "output_path": str(self.output_path),
            "content_hash": self.content_hash,
            "status": self.status.value,
            "reason": self.reason,
            "row_count": self.row_count,
            "column_count": self.column_count,
            "truncated": self.truncated,
        }


def _apply_style(axis: Any, spec: ChartSpecification) -> None:
    axis.set_xlabel(spec.x_label)
    axis.set_ylabel(spec.y_label)
    axis.set_title(spec.chart_id)
    axis.grid(axis="y", linestyle=":", linewidth=0.6, alpha=0.6)
    axis.spines["top"].set_visible(False)
    axis.spines["right"].set_visible(False)


def _truncate_labels(
    labels: Sequence[str], values: Sequence[float]
) -> tuple[list[str], list[float], bool]:
    if len(labels) <= MAX_LABELS:
        return list(labels), list(values), False
    order = sorted(range(len(values)), key=lambda index: values[index], reverse=True)
    kept = sorted(order[:MAX_LABELS])
    return [labels[index] for index in kept], [values[index] for index in kept], True


def _boxplot_label_argument(labels: list[str]) -> dict[str, Any]:
    try:
        axis = plt.gca()
        signature = inspect.signature(axis.boxplot)
    except (TypeError, ValueError):
        return {"labels": labels}
    if "tick_labels" in signature.parameters:
        return {"tick_labels": labels}
    if "labels" in signature.parameters:
        return {"labels": labels}
    return {}


def render_chart(
    prepared_frame: Mapping[str, Any],
    spec: ChartSpecification,
    output_path: Path,
) -> RenderedChart:
    chart_type = spec.chart_type
    labels: Sequence[str] = prepared_frame.get("labels", [])
    values: Sequence[float] = prepared_frame.get("values", [])
    series: Sequence[Mapping[str, Any]] = prepared_frame.get("series", [])
    if chart_type == ChartType.HISTOGRAM.value:
        if not values:
            return _blocked(spec, output_path, "prepared frame has no values", 0)
    elif chart_type in {ChartType.BOXPLOT.value, ChartType.VIOLIN.value}:
        if not prepared_frame.get("groups"):
            return _blocked(spec, output_path, "prepared frame has no groups", 0)
    elif chart_type == ChartType.HEATMAP.value:
        if not prepared_frame.get("matrix"):
            return _blocked(spec, output_path, "heatmap matrix is empty", 0)
    elif chart_type == ChartType.SCATTER.value:
        if not prepared_frame.get("x") or not prepared_frame.get("y"):
            return _blocked(spec, output_path, "prepared frame has no points", 0)
    elif not labels or not values:
        return _blocked(spec, output_path, "prepared frame has no rows", 0)
    if (
        chart_type
        not in {
            ChartType.BOXPLOT.value,
            ChartType.VIOLIN.value,
            ChartType.HISTOGRAM.value,
        }
        and len(labels) != len(values)
    ):
        return _blocked(
            spec, output_path, "label and value lengths differ", len(labels)
        )
    output_path.parent.mkdir(parents=True, exist_ok=True)
    figure, axis = plt.subplots(figsize=(RENDER_WIDTH, RENDER_HEIGHT))
    truncated = False
    try:
        if chart_type == ChartType.BAR.value:
            axis.bar(list(labels), list(values), color=PALETTE[0], edgecolor="none")
            _apply_style(axis, spec)
        elif chart_type == ChartType.GROUPED_BAR.value:
            if series:
                width = 0.8 / max(len(series), 1)
                positions = list(range(len(labels)))
                for series_index, item in enumerate(series):
                    offsets = [
                        position + (series_index - (len(series) - 1) / 2) * width
                        for position in positions
                    ]
                    axis.bar(
                        offsets,
                        list(item["values"]),
                        width=width,
                        label=str(item["label"]),
                        color=PALETTE[series_index % len(PALETTE)],
                        edgecolor="none",
                    )
                axis.set_xticks(positions)
                axis.set_xticklabels(list(labels))
                axis.legend(frameon=False, fontsize=8)
            else:
                axis.bar(list(labels), list(values), color=PALETTE[0], edgecolor="none")
            _apply_style(axis, spec)
        elif chart_type == ChartType.HORIZONTAL_BAR.value:
            kept_labels, kept_values, truncated = _truncate_labels(labels, values)
            axis.barh(
                list(kept_labels), list(kept_values), color=PALETTE[0], edgecolor="none"
            )
            axis.set_xlabel(spec.y_label)
            axis.set_ylabel(spec.x_label)
            axis.set_title(spec.chart_id)
            axis.grid(axis="x", linestyle=":", linewidth=0.6, alpha=0.6)
        elif chart_type == ChartType.STACKED_BAR.value:
            bottom = [0.0] * len(values)
            for series_index, item in enumerate(series):
                axis.bar(
                    list(labels),
                    list(item["values"]),
                    bottom=bottom,
                    label=str(item["label"]),
                    color=PALETTE[series_index % len(PALETTE)],
                    edgecolor="none",
                )
                bottom = [
                    base + value for base, value in zip(bottom, item["values"])
                ]
            if series:
                axis.legend(frameon=False, fontsize=8)
            _apply_style(axis, spec)
        elif chart_type == ChartType.HISTOGRAM.value:
            axis.hist(
                list(values), bins=int(prepared_frame.get("bins", 20)), color=PALETTE[0]
            )
            _apply_style(axis, spec)
        elif chart_type == ChartType.ECDF.value:
            axis.plot(list(labels), list(values), color=PALETTE[0], linewidth=1.6)
            axis.set_ylim(0, 1.02)
            axis.set_xlabel(spec.x_label)
            axis.set_ylabel(spec.y_label)
            axis.set_title(spec.chart_id)
        elif chart_type == ChartType.BOXPLOT.value:
            groups: Sequence[Sequence[float]] = prepared_frame.get("groups", [])
            if not groups:
                groups = [list(values)]
                labels = ["value"]
            axis.boxplot(
                [list(group) for group in groups],
                **_boxplot_label_argument(list(labels)),
            )
            _apply_style(axis, spec)
        elif chart_type == ChartType.VIOLIN.value:
            groups = prepared_frame.get("groups", [])
            if not groups:
                groups = [list(values)]
                labels = ["value"]
            axis.violinplot([list(group) for group in groups], showmedians=True)
            axis.set_xticks(range(1, len(labels) + 1))
            axis.set_xticklabels(list(labels))
            _apply_style(axis, spec)
        elif chart_type == ChartType.SCATTER.value:
            axis.scatter(
                list(prepared_frame.get("x", [])),
                list(prepared_frame.get("y", [])),
                s=8,
                alpha=0.55,
                color=PALETTE[0],
                edgecolor="none",
            )
            axis.set_xlabel(spec.x_label)
            axis.set_ylabel(spec.y_label)
            axis.set_title(spec.chart_id)
        elif chart_type == ChartType.HEATMAP.value:
            matrix = prepared_frame.get("matrix", [])
            rows = list(prepared_frame.get("rows", []))
            columns = list(prepared_frame.get("columns", []))
            if not matrix:
                return _blocked(spec, output_path, "heatmap matrix is empty", 0)
            image = axis.imshow(matrix, aspect="auto", cmap="Blues")
            axis.set_xticks(range(len(columns)))
            axis.set_xticklabels(columns, rotation=45, ha="right", fontsize=8)
            axis.set_yticks(range(len(rows)))
            axis.set_yticklabels(rows, fontsize=7)
            axis.set_title(spec.chart_id)
            figure.colorbar(image, ax=axis)
        elif chart_type == ChartType.DOT.value:
            kept_labels, kept_values, truncated = _truncate_labels(labels, values)
            positions = list(range(len(kept_labels)))
            axis.scatter(list(kept_values), positions, s=18, color=PALETTE[0])
            axis.set_yticks(positions)
            axis.set_yticklabels(list(kept_labels), fontsize=7)
            axis.set_xlabel(spec.x_label)
            axis.set_title(spec.chart_id)
            axis.grid(axis="x", linestyle=":", linewidth=0.6, alpha=0.6)
            if prepared_frame.get("log_x"):
                axis.set_xscale("log")
        elif chart_type == ChartType.LINE.value:
            axis.plot(list(labels), list(values), color=PALETTE[0], linewidth=1.6)
            _apply_style(axis, spec)
        elif chart_type == ChartType.TIMELINE.value:
            axis.barh(list(labels), list(values), color=PALETTE[0], edgecolor="none")
            axis.set_xlabel(spec.x_label)
            axis.set_ylabel(spec.y_label)
            axis.set_title(spec.chart_id)
        else:
            raise ValueError(f"unsupported chart type: {chart_type}")
        figure.tight_layout()
        figure.savefig(output_path, dpi=RENDER_DPI)
    finally:
        plt.close(figure)
    payload = output_path.read_bytes()
    return RenderedChart(
        chart_id=spec.chart_id,
        output_path=output_path,
        content_hash=f"sha256:{hashlib.sha256(payload).hexdigest()}",
        status=Status.PASS,
        reason="rendered",
        row_count=len(labels),
        column_count=len(prepared_frame.get("columns", [])),
        truncated=truncated,
    )


def _blocked(
    spec: ChartSpecification, output_path: Path, reason: str, row_count: int
) -> RenderedChart:
    return RenderedChart(
        chart_id=spec.chart_id,
        output_path=output_path,
        content_hash="",
        status=Status.BLOCKED,
        reason=reason,
        row_count=row_count,
        column_count=0,
        truncated=False,
    )
