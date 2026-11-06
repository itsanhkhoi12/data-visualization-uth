from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Sequence

from business.business_inventory import BusinessProfile
from common.enums import Status
from quality.findings import QualityFinding


@dataclass(frozen=True)
class GlobalProfile:
    split: str
    business_count: int
    pass_count: int
    partial_count: int
    blocked_count: int
    not_applicable_count: int
    total_source_files: int
    total_business_data_files: int
    total_findings: int
    findings_by_severity: dict[str, int]
    findings_by_domain: dict[str, int]
    business_status_map: dict[str, str]
    row_count_disclaimer: str
    status: Status
    notes: tuple[str, ...] = ()

    def to_dict(self) -> dict[str, Any]:
        return {
            "split": self.split,
            "business_count": self.business_count,
            "pass_count": self.pass_count,
            "partial_count": self.partial_count,
            "blocked_count": self.blocked_count,
            "not_applicable_count": self.not_applicable_count,
            "total_source_files": self.total_source_files,
            "total_business_data_files": self.total_business_data_files,
            "total_findings": self.total_findings,
            "findings_by_severity": dict(self.findings_by_severity),
            "findings_by_domain": dict(self.findings_by_domain),
            "business_status_map": dict(self.business_status_map),
            "row_count_disclaimer": self.row_count_disclaimer,
            "status": self.status.value,
            "notes": list(self.notes),
        }


def aggregate_business_profiles(
    split: str,
    profiles: Sequence[BusinessProfile],
    findings: Sequence[QualityFinding],
    total_source_files: int,
    total_business_data_files: int,
) -> GlobalProfile:
    status_map: dict[str, str] = {}
    counts = {"PASS": 0, "PARTIAL": 0, "BLOCKED": 0, "NOT APPLICABLE": 0}
    for profile in profiles:
        value = profile.status.value
        status_map[profile.business_id] = value
        counts[value] = counts.get(value, 0) + 1
    severity_counts: dict[str, int] = {}
    domain_counts: dict[str, int] = {}
    for finding in findings:
        severity_counts[finding.severity] = severity_counts.get(finding.severity, 0) + 1
        domain_counts[finding.domain] = domain_counts.get(finding.domain, 0) + 1
    notes: list[str] = []
    overall = Status.PASS
    if counts.get("BLOCKED", 0):
        overall = Status.PARTIAL
        notes.append("some_businesses_are_blocked")
    if counts.get("PARTIAL", 0):
        overall = Status.PARTIAL if overall == Status.PASS else overall
        notes.append("some_businesses_are_partial")
    return GlobalProfile(
        split=split,
        business_count=len(profiles),
        pass_count=counts.get("PASS", 0),
        partial_count=counts.get("PARTIAL", 0),
        blocked_count=counts.get("BLOCKED", 0),
        not_applicable_count=counts.get("NOT APPLICABLE", 0),
        total_source_files=total_source_files,
        total_business_data_files=total_business_data_files,
        total_findings=len(findings),
        findings_by_severity=dict(sorted(severity_counts.items())),
        findings_by_domain=dict(sorted(domain_counts.items())),
        business_status_map=dict(sorted(status_map.items())),
        row_count_disclaimer=(
            "file, sheet and table counts are source object counts; rows are never "
            "summed across objects of different grain and are not transaction counts"
        ),
        status=overall,
        notes=tuple(notes),
    )


def combine_global_profiles(
    train: GlobalProfile, public: GlobalProfile
) -> dict[str, Any]:
    return {
        "train": train.to_dict(),
        "public_test": public.to_dict(),
        "cross_split_boundary": (
            "populations differ between splits; only metadata-level comparison is valid"
        ),
    }
