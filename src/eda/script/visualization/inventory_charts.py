from __future__ import annotations

from pathlib import Path
from typing import Any, Sequence

from common.enums import Status
from visualization.chart_context import BundleContext
from visualization.chart_data import ChartData

MAX_BUSINESSES = 30
MIB = 1024.0 * 1024.0


def build_inventory_charts(context: BundleContext) -> list[ChartData]:
    charts: list[ChartData] = []
    charts.extend(_format_chart(context))
    charts.extend(_size_chart(context))
    charts.extend(_sheet_chart(context))
    charts.extend(_database_chart(context))
    return charts


def _format_chart(context: BundleContext) -> list[ChartData]:
    manifest = context.bundle.manifest
    if manifest is None:
        return []
    counts: dict[str, int] = {}
    for record in manifest.records:
        counts[record.source_type] = counts.get(record.source_type, 0) + 1
    labels = sorted(counts)
    values = [float(counts[label]) for label in labels]
    return [
        ChartData(
            chart_id="INV01",
            split=context.split,
            business_id="global",
            kind="bar",
            payload={"labels": labels, "values": values},
            source_ids=tuple(record.source_id for record in manifest.records),
            population_n=int(sum(counts.values())),
            sample_n=None,
            method="file_manifest_count_by_source_type",
            unit="file",
            denominator_label="toàn bộ tệp nguồn của split",
            title="Tỷ trọng định dạng nguồn dữ liệu theo split",
            x_label="Định dạng nguồn",
            y_label="Số tệp dữ liệu",
            limitations=(
                "calendar, README, rulebook and question files are included in the manifest",
            ),
            metadata={
                "caption": (
                    f"{len(counts)} định dạng nguồn với tổng {sum(counts.values())} tệp "
                    "trong manifest của split."
                )
            },
        )
    ]


def _size_chart(context: BundleContext) -> list[ChartData]:
    manifest = context.bundle.manifest
    if manifest is None:
        return []
    sizes: dict[str, float] = {}
    for record in manifest.records:
        if record.business_id == "__split__":
            continue
        sizes[record.business_id] = sizes.get(record.business_id, 0.0) + record.size_bytes
    if not sizes:
        return []
    ordered = sorted(sizes.items(), key=lambda item: -item[1])[:MAX_BUSINESSES]
    labels = [item[0] for item in ordered]
    values = [round(item[1] / MIB, 4) for item in ordered]
    return [
        ChartData(
            chart_id="INV02",
            split=context.split,
            business_id="global",
            kind="horizontal_bar",
            payload={"labels": labels, "values": values},
            source_ids=tuple(record.source_id for record in manifest.records),
            population_n=int(sum(sizes.values())),
            sample_n=None,
            method="sum_size_bytes_per_business",
            unit="MiB",
            denominator_label="tổng dung lượng tệp nguồn của doanh nghiệp",
            title="Dung lượng nguồn dữ liệu theo doanh nghiệp",
            x_label="Dung lượng (MiB)",
            y_label="Mã doanh nghiệp",
            limitations=("file size is not a measure of row count or business value",),
            metadata={
                "caption": (
                    f"Dung lượng nguồn của {len(ordered)} doanh nghiệp; tổng "
                    f"{round(sum(sizes.values()) / MIB, 2)} MiB."
                )
            },
        )
    ]


def _sheet_chart(context: BundleContext) -> list[ChartData]:
    registry = context.bundle.sheet_registry
    if registry is None or not registry.entries:
        return []
    counts: dict[str, int] = {}
    for entry in registry.entries:
        counts[entry.workbook_path] = counts.get(entry.workbook_path, 0) + 1
    ordered = sorted(counts.items(), key=lambda item: -item[1])[:MAX_BUSINESSES]
    labels = [Path(item[0]).stem for item in ordered]
    values = [float(item[1]) for item in ordered]
    return [
        ChartData(
            chart_id="INV03",
            split=context.split,
            business_id="global",
            kind="horizontal_bar",
            payload={"labels": labels, "values": values},
            source_ids=tuple(entry.source_id for entry in registry.entries),
            population_n=len(registry.entries),
            sample_n=len(labels),
            method="sheet_registry_count_by_workbook",
            unit="sheet",
            denominator_label="toàn bộ worksheet trong split",
            title="Số worksheet trên mỗi workbook",
            x_label="Số worksheet",
            y_label="Workbook",
            limitations=("formatting-only sheets are still counted",),
            metadata={
                "caption": (
                    f"Tổng {len(registry.entries)} worksheet trên {len(ordered)} workbook "
                    "được hiển thị."
                )
            },
        )
    ]


def _database_chart(context: BundleContext) -> list[ChartData]:
    registry = context.bundle.sqlite_registry
    if registry is None or not registry.entries:
        return []
    objects = [
        (entry, int(entry.row_count or 0))
        for entry in registry.entries
        if entry.object_type == "table"
    ]
    if not objects:
        return []
    ordered = sorted(objects, key=lambda item: -item[1])[:MAX_BUSINESSES]
    labels = [f"{item[0].business_id}/{item[0].object_name}" for item in ordered]
    values = [float(item[1]) for item in ordered]
    return [
        ChartData(
            chart_id="INV04",
            split=context.split,
            business_id="global",
            kind="horizontal_bar",
            payload={"labels": labels, "values": values},
            source_ids=tuple(item[0].source_id for item in ordered),
            population_n=int(sum(item[1] for item in ordered)),
            sample_n=len(labels),
            method="row_count_per_sqlite_table",
            unit="row",
            denominator_label="số dòng của các bảng SQLite trong split",
            title="Phân bố số dòng theo bảng SQLite",
            x_label="Số dòng",
            y_label="Bảng dữ liệu",
            limitations=(
                "rows are source object counts and never transaction counts",
            ),
            metadata={
                "caption": (
                    f"{len(labels)} bảng SQLite với tổng "
                    f"{int(sum(item[1] for item in ordered))} dòng; số dòng không phải "
                    "số giao dịch."
                )
            },
        )
    ]


def inventory_not_applicable(
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
        unit="file",
        denominator_label="không áp dụng",
        title="Biểu đồ không áp dụng",
        x_label="",
        y_label="",
        status=Status.NOT_APPLICABLE,
        reason=reason,
        metadata={"caption": reason},
    )


def inventory_rows(context: BundleContext) -> list[dict[str, Any]]:
    manifest = context.bundle.manifest
    if manifest is None:
        return []
    return [
        {
            "source_id": record.source_id,
            "split": record.split,
            "business_id": record.business_id,
            "source_type": record.source_type,
            "logical_path": record.logical_path,
            "size_bytes": record.size_bytes,
            "size_mib": round(record.size_bytes / MIB, 4),
            "row_count": record.row_count if record.row_count is not None else "",
            "content_hash": record.content_hash,
        }
        for record in manifest.records
    ]


def _sequence(values: Sequence[Any]) -> list[Any]:
    return list(values)
