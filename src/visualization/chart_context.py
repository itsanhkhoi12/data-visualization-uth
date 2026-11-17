from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping, Sequence

from common.bundles import SplitBundle
from common.enums import SemanticType
from schema.type_inference import is_blank, parse_number

MEASURE_SEMANTICS = (
    SemanticType.MEASURE.value,
    SemanticType.AMOUNT.value,
    SemanticType.QUANTITY.value,
)
CATEGORICAL_SEMANTICS = (
    SemanticType.CATEGORICAL.value,
    SemanticType.BOOLEAN.value,
)
DATE_SEMANTICS = (
    SemanticType.DATE.value,
    SemanticType.DATETIME.value,
)


@dataclass(frozen=True)
class ColumnView:
    source_id: str
    business_id: str
    object_name: str
    column: str
    semantic_type: str
    unit: str | None
    non_null_n: int
    null_n: int
    distinct_n: int

    @property
    def field_label(self) -> str:
        return f"{self.business_id}/{self.object_name}/{self.column}"

    @property
    def n_total(self) -> int:
        return self.non_null_n + self.null_n


@dataclass(frozen=True)
class BundleContext:
    split: str
    bundle: SplitBundle

    def business_ids(self) -> tuple[str, ...]:
        return tuple(sorted({profile.business_id for profile in self.bundle.business_profiles}))

    def columns(self) -> tuple[ColumnView, ...]:
        views: list[ColumnView] = []
        for entry in self.bundle.column_entries:
            views.append(
                ColumnView(
                    source_id=entry.source_id,
                    business_id=entry.business_id,
                    object_name=entry.object_name,
                    column=entry.column,
                    semantic_type=entry.semantic_type,
                    unit=entry.unit,
                    non_null_n=entry.non_null_n,
                    null_n=entry.null_n,
                    distinct_n=entry.distinct_n,
                )
            )
        return tuple(views)

    def columns_for_source(self, source_id: str) -> tuple[ColumnView, ...]:
        return tuple(item for item in self.columns() if item.source_id == source_id)

    def measure_columns(self) -> tuple[ColumnView, ...]:
        return tuple(item for item in self.columns() if item.semantic_type in MEASURE_SEMANTICS)

    def categorical_columns(self) -> tuple[ColumnView, ...]:
        return tuple(
            item for item in self.columns() if item.semantic_type in CATEGORICAL_SEMANTICS
        )

    def date_columns(self) -> tuple[ColumnView, ...]:
        return tuple(item for item in self.columns() if item.semantic_type in DATE_SEMANTICS)

    def business_of_source(self, source_id: str) -> str:
        for entry in self.bundle.column_entries:
            if entry.source_id == source_id:
                return entry.business_id
        return "unknown"

    def numeric_values(self, source_id: str, column: str) -> list[float]:
        samples = self.bundle.numeric_samples.get(source_id, {})
        return [float(value) for value in samples.get(column, [])]

    def rows_for_source(self, source_id: str) -> tuple[Mapping[str, Any], ...]:
        return tuple(self.bundle.row_samples.get(source_id, ()))

    def object_names_for_source(self, source_id: str) -> str:
        for entry in self.bundle.column_entries:
            if entry.source_id == source_id:
                return entry.object_name
        return source_id

    def numeric_stat_for(self, source_id: str, column: str) -> Any:
        for item in self.bundle.numeric_stats:
            if item.source_id == source_id and item.field == column:
                return item
        return None

    def categorical_entries(self, source_id: str, column: str) -> tuple[Any, ...]:
        return tuple(
            item
            for item in self.bundle.categorical_stats
            if item.source_id == source_id and item.field == column
        )

    def coverage_for(self, source_id: str, column: str) -> Any:
        for item in self.bundle.coverages:
            if item.source_id == source_id and item.column == column:
                return item
        return None


def parse_numeric_rows(
    rows: Sequence[Mapping[str, Any]], columns: Sequence[str]
) -> tuple[dict[str, list[float]], int]:
    parsed: dict[str, list[float]] = {column: [] for column in columns}
    dropped = 0
    for row in rows:
        values: list[float] = []
        for column in columns:
            number = parse_number(row.get(column))
            values.append(float(number) if number is not None else float("nan"))
        if any(value != value for value in values):
            dropped += 1
            continue
        for column, value in zip(columns, values):
            parsed[column].append(value)
    return parsed, dropped


def is_blank_category(value: Any) -> bool:
    return is_blank(value)
