from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Mapping, Sequence

from common.enums import Status

CHART_DATA_VERSION = "chart_data.v1"
SUPPORTED_PAYLOAD_KINDS = (
    "bar",
    "grouped_bar",
    "stacked_bar",
    "horizontal_bar",
    "histogram",
    "line",
    "scatter",
    "hexbin",
    "heatmap",
    "boxplot",
    "violin",
    "ecdf",
    "timeline",
    "dot",
    "pareto",
)


@dataclass(frozen=True)
class ChartData:
    chart_id: str
    split: str
    business_id: str
    kind: str
    payload: Mapping[str, Any]
    source_ids: tuple[str, ...]
    population_n: int | None
    sample_n: int | None
    method: str
    unit: str
    denominator_label: str
    title: str
    x_label: str
    y_label: str
    limitations: tuple[str, ...] = ()
    status: Status = Status.PASS
    reason: str = ""
    notes: tuple[str, ...] = ()
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "chart_data_version": CHART_DATA_VERSION,
            "chart_id": self.chart_id,
            "split": self.split,
            "business_id": self.business_id,
            "kind": self.kind,
            "payload": dict(self.payload),
            "source_ids": list(self.source_ids),
            "population_n": self.population_n,
            "sample_n": self.sample_n,
            "method": self.method,
            "unit": self.unit,
            "denominator_label": self.denominator_label,
            "title": self.title,
            "x_label": self.x_label,
            "y_label": self.y_label,
            "limitations": list(self.limitations),
            "status": self.status.value,
            "reason": self.reason,
            "notes": list(self.notes),
            "metadata": dict(self.metadata),
        }


@dataclass(frozen=True)
class ChartDataBatch:
    items: tuple[ChartData, ...]

    def for_chart(self, chart_id: str) -> tuple[ChartData, ...]:
        return tuple(item for item in self.items if item.chart_id == chart_id)

    def by_chart(self) -> dict[str, list[ChartData]]:
        grouped: dict[str, list[ChartData]] = {}
        for item in self.items:
            grouped.setdefault(item.chart_id, []).append(item)
        return grouped

    def blocked(self) -> tuple[ChartData, ...]:
        return tuple(item for item in self.items if item.status != Status.PASS)

    def to_dict(self) -> dict[str, Any]:
        return {
            "chart_data_version": CHART_DATA_VERSION,
            "count": len(self.items),
            "items": [item.to_dict() for item in self.items],
        }


def empty_payload(kind: str) -> dict[str, Any]:
    if kind == "heatmap":
        return {"matrix": [], "rows": [], "columns": []}
    if kind in {"boxplot", "violin"}:
        return {"groups": [], "labels": []}
    if kind in {"scatter", "hexbin"}:
        return {"x": [], "y": []}
    if kind == "timeline":
        return {"rows": [], "starts": [], "ends": []}
    if kind == "histogram":
        return {"values": [], "bins": 0}
    return {"labels": [], "values": [], "series": []}


def is_renderable(item: ChartData) -> bool:
    payload = item.payload
    kind = item.kind
    if kind == "heatmap":
        return bool(payload.get("matrix"))
    if kind in {"boxplot", "violin"}:
        return bool(payload.get("groups"))
    if kind in {"scatter", "hexbin"}:
        return bool(payload.get("x")) and bool(payload.get("y"))
    if kind == "timeline":
        return bool(payload.get("rows"))
    if kind == "histogram":
        return bool(payload.get("values"))
    if kind == "ecdf":
        return bool(payload.get("x")) and bool(payload.get("y"))
    if kind in {"stacked_bar", "grouped_bar"}:
        return bool(payload.get("labels")) and bool(payload.get("series"))
    return bool(payload.get("labels")) and bool(payload.get("values"))


def sequence_lengths(payload: Mapping[str, Any]) -> Sequence[int]:
    return (len(payload.get("labels", [])), len(payload.get("values", [])))
