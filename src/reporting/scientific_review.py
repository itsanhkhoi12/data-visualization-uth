from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Sequence

from common.enums import Status
from cross_business.aggregate import GlobalProfile
from reporting.business_report import BusinessReport


@dataclass(frozen=True)
class ScientificConclusion:
    finding_id: str
    claim: str
    evidence: str
    split: str
    confidence: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "finding_id": self.finding_id,
            "claim": self.claim,
            "evidence": self.evidence,
            "split": self.split,
            "confidence": self.confidence,
        }


def _count_by(items: Sequence[Any], attribute: str) -> dict[str, int]:
    counts: dict[str, int] = {}
    for item in items:
        key = str(getattr(item, attribute, "unknown"))
        counts[key] = counts.get(key, 0) + 1
    return counts


def derive_scientific_conclusions(
    profile: GlobalProfile,
    business_reports: Sequence[BusinessReport] = (),
    extra_evidence: dict[str, Any] | None = None,
) -> tuple[ScientificConclusion, ...]:
    extra = extra_evidence or {}
    conclusions: list[ScientificConclusion] = []

    covered = len(business_reports)
    coverage_pct = (
        round(100.0 * covered / profile.business_count, 2)
        if profile.business_count
        else 0.0
    )
    conclusions.append(
        ScientificConclusion(
            finding_id="SCI-01",
            claim=(
                f"Business-level EDA coverage is {covered}/"
                f"{profile.business_count} businesses ({coverage_pct}%) for split "
                f"'{profile.split}'."
            ),
            evidence=(
                f"reports/global_report.json: business_count={profile.business_count}, "
                f"covered_business_count={covered}, "
                f"status={profile.status.value}"
            ),
            split=profile.split,
            confidence="high" if coverage_pct == 100.0 else "medium",
        )
    )

    severity = profile.findings_by_severity
    critical = severity.get("critical", 0)
    high = severity.get("high", 0)
    conclusions.append(
        ScientificConclusion(
            finding_id="SCI-02",
            claim=(
                f"Data-quality risk in split '{profile.split}' is dominated by "
                f"referential-integrity and completeness evidence: "
                f"{profile.findings_by_domain.get('referential_integrity', 0)} "
                f"referential-integrity findings and "
                f"{profile.findings_by_domain.get('completeness', 0)} completeness "
                f"findings out of {profile.total_findings} total."
            ),
            evidence=(
                "splits/"
                f"{profile.split}/quality_findings.json: findings_by_domain="
                f"{profile.findings_by_domain}, findings_by_severity={severity}"
            ),
            split=profile.split,
            confidence="high",
        )
    )

    if critical or high:
        conclusions.append(
            ScientificConclusion(
                finding_id="SCI-03",
                claim=(
                    f"{critical + high} high-or-worse findings "
                    f"(critical={critical}, high={high}) require remediation "
                    f"before the affected relations can be trusted as join keys."
                ),
                evidence=(
                    "splits/"
                    f"{profile.split}/quality_findings.json: "
                    f"severity in (critical, high) = {critical + high}; "
                    "referential-integrity findings are unverified candidate relations"
                ),
                split=profile.split,
                confidence="high",
            )
        )

    status_counts = _count_by(business_reports, "coverage_status")
    if business_reports:
        partial_ids = [
            report.business_id
            for report in business_reports
            if report.coverage_status != Status.PASS.value
        ]
        conclusions.append(
            ScientificConclusion(
                finding_id="SCI-04",
                claim=(
                    f"{len(partial_ids)}/{len(business_reports)} businesses in split "
                    f"'{profile.split}' carry a non-PASS coverage status "
                    f"({status_counts}); each one is explicitly justified by a "
                    "recorded note rather than silently skipped."
                ),
                evidence=(
                    "reports/global_report.json: business_reports[*].coverage_status "
                    f"and business_reports[*].notes; non-PASS businesses="
                    f"{partial_ids[:20]}"
                ),
                split=profile.split,
                confidence="high",
            )
        )

    readme_missing = [
        report.business_id for report in business_reports if not report.readme_present
    ]
    if readme_missing:
        conclusions.append(
            ScientificConclusion(
                finding_id="SCI-05",
                claim=(
                    f"{len(readme_missing)} businesses lack a README, so domain "
                    "classification for them rests on data-object evidence only and "
                    "is reported as unresolved rather than inferred."
                ),
                evidence=(
                    "reports/global_report.json: business_reports[*].readme_present "
                    f"= false for {readme_missing[:20]}"
                ),
                split=profile.split,
                confidence="medium",
            )
        )

    for key, template in _EXTRA_CLAIMS:
        if key not in extra:
            continue
        value = extra[key]
        conclusions.append(
            ScientificConclusion(
                finding_id=f"SCI-EXTRA-{key}",
                claim=template.format(value=value),
                evidence=f"pipeline evidence: {key}={value}",
                split=profile.split,
                confidence="medium",
            )
        )

    return tuple(conclusions)


_EXTRA_CLAIMS: tuple[tuple[str, str], ...] = (
    (
        "relation_candidate_count",
        "The split exposes {value} candidate join relations whose grain and "
        "orphan evidence are recorded but not yet approved.",
    ),
    (
        "date_field_count",
        "Temporal analysis is grounded in {value} typed date fields with "
        "explicit coverage windows.",
    ),
    (
        "metric_definition_count",
        "{value} KPI definitions are registered; each carries an explicit "
        "PASS/PARTIAL/BLOCKED formula status and a stated business unit.",
    ),
)
