from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Sequence

from common.enums import Status
from cross_business.aggregate import GlobalProfile
from reporting.business_report import BusinessReport
from reporting.scientific_review import ScientificConclusion

SCIENCE_LIMITATIONS = (
    "file, sheet and table counts are source object counts and never represent "
    "transaction counts",
    "row counts are never summed across objects with different grains",
    "train and public test populations differ, so only metadata-level comparison "
    "is scientifically valid",
    "public test reference answers do not exist in this snapshot and were never "
    "accessed or inferred",
    "business domain classification relies on README vocabulary evidence only",
    "candidate join relations remain unverified until grain and orphan evidence "
    "support approval",
)


@dataclass(frozen=True)
class GlobalReport:
    split: str
    business_count: int
    covered_business_count: int
    pass_count: int
    partial_count: int
    blocked_count: int
    total_findings: int
    findings_by_severity: dict[str, int]
    findings_by_domain: dict[str, int]
    business_reports: tuple[BusinessReport, ...]
    science_limitations: tuple[str, ...]
    conclusions: tuple[str, ...]
    status: Status
    notes: tuple[str, ...]
    scientific_conclusions: tuple[ScientificConclusion, ...] = ()

    def to_dict(self) -> dict[str, Any]:
        return {
            "split": self.split,
            "business_count": self.business_count,
            "covered_business_count": self.covered_business_count,
            "pass_count": self.pass_count,
            "partial_count": self.partial_count,
            "blocked_count": self.blocked_count,
            "total_findings": self.total_findings,
            "findings_by_severity": dict(self.findings_by_severity),
            "findings_by_domain": dict(self.findings_by_domain),
            "business_reports": [item.to_dict() for item in self.business_reports],
            "science_limitations": list(self.science_limitations),
            "conclusions": list(self.conclusions),
            "scientific_conclusions": [
                item.to_dict() for item in self.scientific_conclusions
            ],
            "status": self.status.value,
            "notes": list(self.notes),
        }


def assemble_global_report(
    profile: GlobalProfile,
    business_reports: Sequence[BusinessReport] = (),
    conclusions: Sequence[str] = (),
    scientific_conclusions: Sequence[ScientificConclusion] = (),
) -> GlobalReport:
    covered = len(business_reports)
    notes: list[str] = []
    if covered != profile.business_count:
        notes.append("business_report_coverage_incomplete")
    status = profile.status
    if covered != profile.business_count and status == Status.PASS:
        status = Status.PARTIAL
    return GlobalReport(
        split=profile.split,
        business_count=profile.business_count,
        covered_business_count=covered,
        pass_count=profile.pass_count,
        partial_count=profile.partial_count,
        blocked_count=profile.blocked_count,
        total_findings=profile.total_findings,
        findings_by_severity=dict(profile.findings_by_severity),
        findings_by_domain=dict(profile.findings_by_domain),
        business_reports=tuple(business_reports),
        science_limitations=SCIENCE_LIMITATIONS,
        conclusions=tuple(conclusions),
        status=status,
        notes=tuple(notes),
        scientific_conclusions=tuple(scientific_conclusions),
    )
