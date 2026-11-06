from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Sequence

METHOD_VERSION = "missing_dependency.v1"


@dataclass(frozen=True)
class CoMissingEntry:
    field_x: str
    field_y: str
    both_missing_n: int
    union_missing_n: int
    co_missing_ratio: float | None
    x_missing_n: int
    y_missing_n: int
    total_n: int

    def to_dict(self) -> dict[str, Any]:
        return {
            "field_x": self.field_x,
            "field_y": self.field_y,
            "both_missing_n": self.both_missing_n,
            "union_missing_n": self.union_missing_n,
            "co_missing_ratio": self.co_missing_ratio,
            "x_missing_n": self.x_missing_n,
            "y_missing_n": self.y_missing_n,
            "total_n": self.total_n,
        }


def co_missing_matrix(
    missing_masks: dict[str, Sequence[bool]], max_fields: int = 30
) -> tuple[tuple[str, ...], tuple[tuple[float | None, ...], ...], tuple[str, ...]]:
    fields = sorted(missing_masks)[:max_fields]
    size = len(fields)
    matrix: list[tuple[float | None, ...]] = []
    notes: list[str] = []
    for index_x in range(size):
        row_values: list[float | None] = []
        mask_x = missing_masks[fields[index_x]]
        for index_y in range(size):
            if index_x == index_y:
                row_values.append(1.0)
                continue
            mask_y = missing_masks[fields[index_y]]
            both = sum(
                1 for flag_x, flag_y in zip(mask_x, mask_y) if flag_x and flag_y
            )
            union = sum(
                1 for flag_x, flag_y in zip(mask_x, mask_y) if flag_x or flag_y
            )
            if union == 0:
                row_values.append(None)
                if "constant_mask_handled" not in notes:
                    notes.append("constant_mask_handled")
                continue
            row_values.append(round(both / union, 6))
        matrix.append(tuple(row_values))
    return tuple(fields), tuple(matrix), tuple(notes)
