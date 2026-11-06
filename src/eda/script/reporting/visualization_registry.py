from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Mapping

from common.enums import Status
from visualization.chart_data import ChartData


@dataclass(frozen=True)
class FigureRecord:
    figure_id: str
    chart_id: str
    split: str
    business_id: str
    png_path: str
    svg_path: str
    content_hash: str
    status: Status
    reason: str
    population_n: int | None
    sample_n: int | None
    method: str
    unit: str
    title: str
    caption: str
    source_ids: tuple[str, ...]
    byte_size: int
    limitations: tuple[str, ...] = ()

    def to_dict(self) -> dict[str, Any]:
        return {
            "figure_id": self.figure_id,
            "chart_id": self.chart_id,
            "split": self.split,
            "business_id": self.business_id,
            "png_path": self.png_path,
            "svg_path": self.svg_path,
            "content_hash": self.content_hash,
            "status": self.status.value,
            "reason": self.reason,
            "population_n": self.population_n,
            "sample_n": self.sample_n,
            "method": self.method,
            "unit": self.unit,
            "title": self.title,
            "caption": self.caption,
            "source_ids": list(self.source_ids),
            "byte_size": self.byte_size,
            "limitations": list(self.limitations),
        }


@dataclass
class VisualizationRegistry:
    run_id: str
    figures: list[FigureRecord] = field(default_factory=list)
    chart_data: list[ChartData] = field(default_factory=list)

    def add_figure(self, record: FigureRecord) -> None:
        self.figures.append(record)

    def add_chart_data(self, item: ChartData) -> None:
        self.chart_data.append(item)

    def figure_ids_for_chart(self, chart_id: str) -> tuple[str, ...]:
        return tuple(
            record.figure_id
            for record in self.figures
            if record.chart_id == chart_id and record.status == Status.PASS
        )

    def figures_for_chart(self, chart_id: str) -> tuple[FigureRecord, ...]:
        return tuple(record for record in self.figures if record.chart_id == chart_id)

    def by_chart(self) -> dict[str, list[FigureRecord]]:
        grouped: dict[str, list[FigureRecord]] = {}
        for record in self.figures:
            grouped.setdefault(record.chart_id, []).append(record)
        return grouped

    def status_counts(self) -> dict[str, int]:
        counts: dict[str, int] = {}
        for record in self.figures:
            counts[record.status.value] = counts.get(record.status.value, 0) + 1
        return dict(sorted(counts.items()))

    def to_dict(self) -> dict[str, Any]:
        return {
            "run_id": self.run_id,
            "figure_count": len(self.figures),
            "status_counts": self.status_counts(),
            "figures": [record.to_dict() for record in self.figures],
        }


@dataclass(frozen=True)
class ChartEligibilityEntry:
    chart_id: str
    family: str
    split: str
    business_id: str
    status: str
    reason: str
    population_n: int | None
    method: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "chart_id": self.chart_id,
            "family": self.family,
            "split": self.split,
            "business_id": self.business_id,
            "status": self.status,
            "reason": self.reason,
            "population_n": self.population_n,
            "method": self.method,
        }


def family_of(chart_id: str) -> str:
    prefix = chart_id.rstrip("0123456789")
    return prefix or chart_id


def build_eligibility_ledger(
    chart_data: list[ChartData],
) -> list[ChartEligibilityEntry]:
    entries: list[ChartEligibilityEntry] = []
    for item in chart_data:
        entries.append(
            ChartEligibilityEntry(
                chart_id=item.chart_id,
                family=family_of(item.chart_id),
                split=item.split,
                business_id=item.business_id,
                status=item.status.value,
                reason=item.reason,
                population_n=item.population_n,
                method=item.method,
            )
        )
    return entries


def eligibility_summary(entries: list[ChartEligibilityEntry]) -> dict[str, Any]:
    by_chart: dict[str, dict[str, int]] = {}
    for entry in entries:
        bucket = by_chart.setdefault(entry.chart_id, {})
        bucket[entry.status] = bucket.get(entry.status, 0) + 1
    return {
        "chart_count": len({entry.chart_id for entry in entries}),
        "by_chart": {
            chart_id: dict(sorted(statuses.items()))
            for chart_id, statuses in sorted(by_chart.items())
        },
    }


def registry_payload(registry: VisualizationRegistry) -> Mapping[str, Any]:
    return registry.to_dict()
