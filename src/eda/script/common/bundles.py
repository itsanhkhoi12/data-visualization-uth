from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Mapping


@dataclass(frozen=True)
class SplitBundle:
    split: str
    manifest: Any = None
    sheet_registry: Any = None
    sqlite_registry: Any = None
    business_profiles: tuple[Any, ...] = ()
    column_entries: tuple[Any, ...] = ()
    missing_entries: tuple[Any, ...] = ()
    duplicate_entries: tuple[Any, ...] = ()
    validity_entries: tuple[Any, ...] = ()
    integrity_entries: tuple[Any, ...] = ()
    relations: tuple[Any, ...] = ()
    key_candidates: tuple[Any, ...] = ()
    numeric_stats: tuple[Any, ...] = ()
    categorical_stats: tuple[Any, ...] = ()
    date_profiles: tuple[Any, ...] = ()
    coverages: tuple[Any, ...] = ()
    findings: tuple[Any, ...] = ()
    domain_diagnostics: tuple[Any, ...] = ()
    metrics: tuple[Any, ...] = ()
    question_profile: Any = None
    answer_profile: Any = None
    alignment: tuple[Any, ...] = ()
    calendar: Any = None
    rule_registry: Any = None
    business_reports: tuple[Any, ...] = ()
    global_profile: Any = None
    numeric_samples: Mapping[str, Mapping[str, Any]] = field(default_factory=dict)
    daily_counts: Mapping[str, Mapping[str, int]] = field(default_factory=dict)
    row_samples: Mapping[str, tuple[Mapping[str, Any], ...]] = field(default_factory=dict)
    source_row_counts: Mapping[str, int] = field(default_factory=dict)
    source_total_row_counts: Mapping[str, int] = field(default_factory=dict)
    source_truncated: Mapping[str, bool] = field(default_factory=dict)
    question_metadata: tuple[Mapping[str, Any], ...] = ()
    question_lengths: tuple[int, ...] = ()
    business_metrics: tuple[Any, ...] = ()
    notes: tuple[str, ...] = ()

    def to_dict(self) -> dict[str, Any]:
        return {
            "split": self.split,
            "source_file_count": len(self.manifest.records) if self.manifest else 0,
            "business_count": len(self.business_profiles),
            "worksheet_count": (
                len(self.sheet_registry.entries) if self.sheet_registry else 0
            ),
            "database_object_count": (
                len(self.sqlite_registry.entries) if self.sqlite_registry else 0
            ),
            "column_count": len(self.column_entries),
            "missing_entry_count": len(self.missing_entries),
            "duplicate_entry_count": len(self.duplicate_entries),
            "validity_entry_count": len(self.validity_entries),
            "integrity_entry_count": len(self.integrity_entries),
            "relation_count": len(self.relations),
            "key_candidate_count": len(self.key_candidates),
            "numeric_stat_count": len(self.numeric_stats),
            "categorical_stat_count": len(self.categorical_stats),
            "date_field_count": len(self.date_profiles),
            "coverage_count": len(self.coverages),
            "finding_count": len(self.findings),
            "metric_count": len(self.metrics),
            "notes": list(self.notes),
        }
