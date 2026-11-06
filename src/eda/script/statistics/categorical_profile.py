from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Any, Sequence

METHOD_VERSION = "categorical_profile.v1"
DEFAULT_TOP_K = 15


@dataclass(frozen=True)
class CategoryEntry:
    category: str
    count: int
    share: float
    cumulative_share: float
    rank: int
    is_others: bool = False
    is_null: bool = False

    def to_dict(self) -> dict[str, Any]:
        return {
            "category": self.category,
            "count": self.count,
            "share": self.share,
            "cumulative_share": self.cumulative_share,
            "rank": self.rank,
            "is_others": self.is_others,
            "is_null": self.is_null,
        }


@dataclass(frozen=True)
class CategoricalProfile:
    field: str
    n_total: int
    n_valid: int
    n_null: int
    n_unique: int
    top_k: int
    entries: tuple[CategoryEntry, ...]
    entropy_bits: float | None
    max_category_share: float
    imbalance_ratio: float | None
    method: str
    method_version: str
    warnings: tuple[str, ...] = ()

    def to_dict(self) -> dict[str, Any]:
        return {
            "field": self.field,
            "n_total": self.n_total,
            "n_valid": self.n_valid,
            "n_null": self.n_null,
            "n_unique": self.n_unique,
            "top_k": self.top_k,
            "entries": [entry.to_dict() for entry in self.entries],
            "entropy_bits": self.entropy_bits,
            "max_category_share": self.max_category_share,
            "imbalance_ratio": self.imbalance_ratio,
            "method": self.method,
            "method_version": self.method_version,
            "warnings": list(self.warnings),
        }


def shannon_entropy(counts: Sequence[int]) -> float | None:
    total = sum(counts)
    if total <= 0:
        return None
    entropy = 0.0
    for count in counts:
        if count <= 0:
            continue
        probability = count / total
        entropy -= probability * math.log2(probability)
    return entropy


def build_categorical_profile(
    values: Sequence[Any],
    field: str,
    total_n: int | None = None,
    top_k: int = DEFAULT_TOP_K,
) -> CategoricalProfile:
    counts: dict[str, int] = {}
    null_count = 0
    for value in values:
        if value is None:
            null_count += 1
            continue
        if isinstance(value, str) and not value.strip():
            null_count += 1
            continue
        label = str(value).strip()
        counts[label] = counts.get(label, 0) + 1
    total = total_n if total_n is not None else len(values)
    valid = sum(counts.values())
    ranked = sorted(counts.items(), key=lambda item: (-item[1], item[0]))
    entries: list[CategoryEntry] = []
    cumulative = 0.0
    head = ranked[:top_k]
    tail = ranked[top_k:]
    for index, (label, count) in enumerate(head, start=1):
        share = count / valid if valid else 0.0
        cumulative += share
        entries.append(
            CategoryEntry(
                category=label,
                count=count,
                share=share,
                cumulative_share=cumulative,
                rank=index,
            )
        )
    if tail:
        others_count = sum(count for _, count in tail)
        others_share = others_count / valid if valid else 0.0
        cumulative += others_share
        entries.append(
            CategoryEntry(
                category="Others",
                count=others_count,
                share=others_share,
                cumulative_share=cumulative,
                rank=top_k + 1,
                is_others=True,
            )
        )
    if null_count:
        entries.append(
            CategoryEntry(
                category="__NULL__",
                count=null_count,
                share=null_count / total if total else 0.0,
                cumulative_share=1.0 if valid == 0 else cumulative,
                rank=len(entries) + 1,
                is_null=True,
            )
        )
    warnings: list[str] = []
    if valid and null_count / total > 0.2:
        warnings.append("high_null_share")
    if len(counts) > 50:
        warnings.append("high_cardinality")
    max_share = head[0][1] / valid if head and valid else 0.0
    imbalance = None
    if len(ranked) >= 2 and ranked[-1][1] > 0:
        imbalance = ranked[0][1] / ranked[-1][1]
    return CategoricalProfile(
        field=field,
        n_total=total,
        n_valid=valid,
        n_null=null_count,
        n_unique=len(counts),
        top_k=top_k,
        entries=tuple(entries),
        entropy_bits=shannon_entropy([count for _, count in ranked]),
        max_category_share=max_share,
        imbalance_ratio=imbalance,
        method="frequency_full_population_topk_others",
        method_version=METHOD_VERSION,
        warnings=tuple(warnings),
    )


def pareto_entries(profile: CategoricalProfile) -> tuple[CategoryEntry, ...]:
    real = [entry for entry in profile.entries if not entry.is_null]
    if not real:
        return ()
    return real
