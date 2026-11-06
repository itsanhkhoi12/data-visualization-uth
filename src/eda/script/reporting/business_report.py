from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Sequence

from business.business_inventory import BusinessProfile
from business.domain_profiles import DomainDiagnostic
from common.contracts import MetricDefinition, QualityFinding
from common.enums import Status

BLOCKING_SEVERITIES = ("critical", "high")


@dataclass(frozen=True)
class BusinessReport:
    business_id: str
    split: str
    source_count: int
    worksheet_count: int
    database_object_count: int
    column_count: int
    readme_present: bool
    readme_hash: str
    domain: str | None
    domain_status: str
    kpi_pass_count: int
    kpi_partial_count: int
    kpi_blocked_count: int
    finding_count: int
    critical_finding_count: int
    high_finding_count: int
    max_missing_ratio: float
    coverage_status: str
    notes: tuple[str, ...]

    def to_dict(self) -> dict[str, Any]:
        return {
            "business_id": self.business_id,
            "split": self.split,
            "source_count": self.source_count,
            "worksheet_count": self.worksheet_count,
            "database_object_count": self.database_object_count,
            "column_count": self.column_count,
            "readme_present": self.readme_present,
            "readme_hash": self.readme_hash,
            "domain": self.domain,
            "domain_status": self.domain_status,
            "kpi_pass_count": self.kpi_pass_count,
            "kpi_partial_count": self.kpi_partial_count,
            "kpi_blocked_count": self.kpi_blocked_count,
            "finding_count": self.finding_count,
            "critical_finding_count": self.critical_finding_count,
            "high_finding_count": self.high_finding_count,
            "max_missing_ratio": self.max_missing_ratio,
            "coverage_status": self.coverage_status,
            "notes": list(self.notes),
        }


def assemble_business_report(
    profile: BusinessProfile,
    worksheet_count: int = 0,
    database_object_count: int = 0,
    column_count: int = 0,
    metrics: Sequence[MetricDefinition] = (),
    findings: Sequence[QualityFinding] = (),
    diagnostics: Sequence[DomainDiagnostic] = (),
    max_missing_ratio: float = 0.0,
) -> BusinessReport:
    notes: list[str] = []
    kpi_pass = 0
    kpi_partial = 0
    kpi_blocked = 0
    for metric in metrics:
        if metric.formula_status == Status.PASS:
            kpi_pass += 1
        elif metric.formula_status == Status.PARTIAL:
            kpi_partial += 1
        else:
            kpi_blocked += 1
    critical = sum(1 for item in findings if item.severity == "critical")
    high = sum(1 for item in findings if item.severity == "high")
    domain_status = "NOT_APPLICABLE"
    domain: str | None = profile.domain_evidence
    if diagnostics:
        domain_status = diagnostics[-1].status.value
    else:
        domain_status = profile.status.value
    coverage = Status.PASS
    if not profile.readme_present:
        coverage = Status.PARTIAL
        notes.append("readme_missing_domain_unresolved")
    if critical:
        coverage = Status.PARTIAL
        notes.append("critical_findings_present")
    if kpi_blocked and kpi_pass == 0 and kpi_partial == 0:
        coverage = Status.PARTIAL
        notes.append("no_supported_kpi_definition")
    if profile.status == Status.BLOCKED:
        coverage = Status.BLOCKED
    return BusinessReport(
        business_id=profile.business_id,
        split=profile.split,
        source_count=profile.source_count,
        worksheet_count=worksheet_count,
        database_object_count=database_object_count,
        column_count=column_count,
        readme_present=profile.readme_present,
        readme_hash=profile.readme_hash,
        domain=domain,
        domain_status=domain_status,
        kpi_pass_count=kpi_pass,
        kpi_partial_count=kpi_partial,
        kpi_blocked_count=kpi_blocked,
        finding_count=len(findings),
        critical_finding_count=critical,
        high_finding_count=high,
        max_missing_ratio=round(max_missing_ratio, 6),
        coverage_status=coverage.value,
        notes=tuple(notes),
    )
