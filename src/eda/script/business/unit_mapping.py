from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Sequence

from common.enums import Status
from schema.type_inference import is_blank, parse_number


@dataclass(frozen=True)
class UnitMappingEntry:
    source_id: str
    split: str
    business_id: str
    object_name: str
    item_key: str
    source_unit: str
    base_unit: str
    conversion_factor: float | None
    status: Status
    evidence: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "source_id": self.source_id,
            "split": self.split,
            "business_id": self.business_id,
            "object_name": self.object_name,
            "item_key": self.item_key,
            "source_unit": self.source_unit,
            "base_unit": self.base_unit,
            "conversion_factor": self.conversion_factor,
            "status": self.status.value,
            "evidence": self.evidence,
        }


@dataclass(frozen=True)
class UnitRegistry:
    split: str
    business_id: str
    entries: tuple[UnitMappingEntry, ...]
    conflicting_items: tuple[str, ...]
    items_without_base_unit: tuple[str, ...]
    distinct_base_units: tuple[str, ...]
    status: Status

    def to_dict(self) -> dict[str, Any]:
        return {
            "split": self.split,
            "business_id": self.business_id,
            "entries": [entry.to_dict() for entry in self.entries],
            "conflicting_items": list(self.conflicting_items),
            "items_without_base_unit": list(self.items_without_base_unit),
            "distinct_base_units": list(self.distinct_base_units),
            "status": self.status.value,
        }


def validate_unit_mapping(
    split: str,
    business_id: str,
    rows: Sequence[dict[str, Any]],
    item_column: str,
    source_unit_column: str,
    base_unit_column: str,
    factor_column: str | None = None,
) -> UnitRegistry:
    entries: list[UnitMappingEntry] = []
    by_item: dict[str, set[tuple[str, str]]] = {}
    missing_base: list[str] = []
    for row in rows:
        item = str(row.get(item_column, "")).strip()
        source_unit = str(row.get(source_unit_column, "")).strip()
        base_unit = str(row.get(base_unit_column, "")).strip()
        if not item:
            continue
        if not base_unit:
            missing_base.append(item)
        factor = None
        if factor_column:
            factor = parse_number(row.get(factor_column))
        by_item.setdefault(item, set()).add((source_unit, base_unit))
        entries.append(
            UnitMappingEntry(
                source_id="",
                split=split,
                business_id=business_id,
                object_name="",
                item_key=item,
                source_unit=source_unit,
                base_unit=base_unit,
                conversion_factor=factor,
                status=Status.PASS if base_unit else Status.PARTIAL,
                evidence=(
                    f"source_unit={source_unit};base_unit={base_unit};"
                    f"factor={factor}"
                ),
            )
        )
    conflicting = tuple(
        item for item, variants in by_item.items() if len(variants) > 1
    )
    base_units = tuple(
        sorted({base for variants in by_item.values() for _source, base in variants if base})
    )
    status = Status.PASS
    if conflicting:
        status = Status.PARTIAL
    return UnitRegistry(
        split=split,
        business_id=business_id,
        entries=tuple(entries),
        conflicting_items=conflicting,
        items_without_base_unit=tuple(sorted(set(missing_base))),
        distinct_base_units=base_units,
        status=status,
    )


def unit_dimension_conflict(
    units_a: Sequence[str], units_b: Sequence[str]
) -> bool:
    return bool(set(units_a) & set(units_b))
