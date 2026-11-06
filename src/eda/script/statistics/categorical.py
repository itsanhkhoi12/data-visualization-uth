from __future__ import annotations

import unicodedata
from dataclasses import dataclass
from typing import Any, Sequence

from common.contracts import CategoricalStats
from common.enums import Status
from schema.type_inference import is_blank

METHOD_VERSION = "categorical.v1"
TOP_K_DEFAULT = 20


@dataclass(frozen=True)
class CategoricalProfileRequest:
    source_id: str
    split: str
    business_id: str
    field: str
    values: Sequence[Any]
    total_n: int
    top_k: int = TOP_K_DEFAULT


def normalize_label(value: str) -> str:
    folded = unicodedata.normalize("NFC", value).strip().lower()
    return " ".join(folded.split())


def profile_categorical(
    request: CategoricalProfileRequest,
) -> tuple[CategoricalStats, ...]:
    counts: dict[str, int] = {}
    null_count = 0
    total = request.total_n or len(request.values)
    for value in request.values:
        if is_blank(value):
            null_count += 1
            continue
        label = str(value).strip()
        counts[label] = counts.get(label, 0) + 1
    variants_by_normalized: dict[str, set[str]] = {}
    for raw in counts:
        variants_by_normalized.setdefault(normalize_label(raw), set()).add(raw)
    alias_candidates = {
        normalized: count
        for normalized, variants in variants_by_normalized.items()
        if len(variants) > 1
        for count in (sum(counts[variant] for variant in variants),)
    }
    ranked = sorted(counts.items(), key=lambda item: (-item[1], item[0]))
    entries: list[CategoricalStats] = []
    denominator = sum(counts.values())
    for rank, (label, count) in enumerate(ranked, start=1):
        entries.append(
            CategoricalStats(
                source_id=request.source_id,
                split=request.split,
                business_id=request.business_id,
                field=request.field,
                category=label,
                count=count,
                share=round(count / denominator, 6) if denominator else 0.0,
                is_null=False,
                rank=rank,
                method=request.method if hasattr(request, "method") else "frequency_full_population",
                method_version=METHOD_VERSION,
                status=Status.PASS,
            )
        )
    if null_count:
        entries.append(
            CategoricalStats(
                source_id=request.source_id,
                split=request.split,
                business_id=request.business_id,
                field=request.field,
                category="__NULL__",
                count=null_count,
                share=round(null_count / total, 6) if total else 0.0,
                is_null=True,
                rank=len(entries) + 1,
                method="frequency_full_population",
                method_version=METHOD_VERSION,
                status=Status.PASS,
            )
        )
    del alias_candidates
    return tuple(entries)


def alias_candidates_for_field(values: Sequence[Any]) -> dict[str, list[str]]:
    raw_by_normalized: dict[str, set[str]] = {}
    for value in values:
        if is_blank(value):
            continue
        label = str(value).strip()
        raw_by_normalized.setdefault(normalize_label(label), set()).add(label)
    return {
        normalized: sorted(variants)
        for normalized, variants in raw_by_normalized.items()
        if len(variants) > 1
    }


def top_k_with_others(
    entries: Sequence[CategoricalStats], top_k: int = TOP_K_DEFAULT
) -> tuple[CategoricalStats, ...]:
    real = [entry for entry in entries if not entry.is_null]
    nulls = [entry for entry in entries if entry.is_null]
    head = real[:top_k]
    tail = real[top_k:]
    if tail:
        head = list(head)
        head.append(
            CategoricalStats(
                source_id=real[0].source_id,
                split=real[0].split,
                business_id=real[0].business_id,
                field=real[0].field,
                category="Others",
                count=sum(entry.count for entry in tail),
                share=round(sum(entry.share for entry in tail), 6),
                is_null=False,
                rank=top_k + 1,
                method=real[0].method,
                method_version=real[0].method_version,
                status=Status.PASS,
            )
        )
    return tuple(head) + tuple(nulls)


def category_cardinality(entries: Sequence[CategoricalStats]) -> int:
    return len({entry.category for entry in entries if not entry.is_null})
