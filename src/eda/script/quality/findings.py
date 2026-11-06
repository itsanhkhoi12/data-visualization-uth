from __future__ import annotations

from typing import Any, Sequence

from common.contracts import QualityFinding
from common.enums import Status
from quality.duplicates import DuplicateEntry
from quality.integrity import IntegrityEntry
from quality.missingness import MissingnessEntry
from quality.validity import ValidityEntry

SEVERITY_ORDER = {"critical": 0, "high": 1, "medium": 2, "low": 3, "info": 4}
HIGH_RATIO_THRESHOLD = 0.2
MEDIUM_RATIO_THRESHOLD = 0.05


def _severity_for_ratio(ratio: float, prevalence: int) -> str:
    if prevalence == 0:
        return "info"
    if ratio >= HIGH_RATIO_THRESHOLD:
        return "high"
    if ratio >= MEDIUM_RATIO_THRESHOLD:
        return "medium"
    return "low"


def compile_findings(
    missingness: Sequence[MissingnessEntry],
    duplicates: Sequence[DuplicateEntry],
    validity: Sequence[ValidityEntry],
    integrity: Sequence[IntegrityEntry],
) -> tuple[QualityFinding, ...]:
    findings: list[QualityFinding] = []
    for entry in missingness:
        severity = _severity_for_ratio(entry.missing_ratio, entry.n_missing)
        if entry.null_kind == "structural_missing":
            severity = "info"
        findings.append(
            QualityFinding(
                finding_id=f"MISS.{entry.source_id}.{entry.column}",
                severity=severity,
                domain="completeness",
                split=entry.split,
                business_id=entry.business_id,
                source_id=entry.source_id,
                field=entry.column,
                count=entry.n_missing,
                denominator=entry.n_total,
                ratio=entry.missing_ratio,
                status=Status.PARTIAL,
                evidence=(
                    f"{entry.n_missing}/{entry.n_total} values blank; "
                    f"null_kind={entry.null_kind}"
                ),
                hypothesis="source omits this attribute for some records",
                alternative_explanation=(
                    "structural blank by business design"
                    if entry.null_kind == "structural_missing"
                    else "extraction or format failure"
                ),
                verification="compare against README field contract",
                owner="quality.missingness",
            )
        )
    for entry in duplicates:
        if entry.n_duplicate_rows == 0:
            continue
        ratio = (
            round(entry.n_duplicate_rows / entry.total_n, 6) if entry.total_n else 0.0
        )
        findings.append(
            QualityFinding(
                finding_id=f"DUP.{entry.source_id}.{entry.duplicate_class}",
                severity=_severity_for_ratio(ratio, entry.n_duplicate_rows),
                domain="uniqueness",
                split=entry.split,
                business_id=entry.business_id,
                source_id=entry.source_id,
                field=",".join(entry.key_columns) or None,
                count=entry.n_duplicate_rows,
                denominator=entry.total_n,
                ratio=ratio,
                status=Status.PARTIAL,
                evidence=(
                    f"{entry.duplicate_class} duplicates={entry.n_duplicate_rows} "
                    f"distinct_keys={entry.n_distinct_keys}"
                ),
                hypothesis="repeated events at a finer grain than the table suggests",
                alternative_explanation=entry.explanation,
                verification="confirm row grain against README before any aggregation",
                owner="quality.duplicates",
            )
        )
    for entry in validity:
        findings.append(
            QualityFinding(
                finding_id=f"VAL.{entry.source_id}.{entry.column}.{entry.rule_id}",
                severity=entry.severity,
                domain="validity",
                split=entry.split,
                business_id=entry.business_id,
                source_id=entry.source_id,
                field=entry.column,
                count=entry.invalid_count,
                denominator=entry.denominator,
                ratio=entry.invalid_ratio,
                status=entry.status,
                evidence=entry.evidence,
                hypothesis=entry.hypothesis,
                alternative_explanation=entry.alternative_explanation,
                verification=f"rule_id={entry.rule_id}",
                owner="quality.validity",
            )
        )
    for entry in integrity:
        findings.append(
            QualityFinding(
                finding_id=f"INT.{entry.relation_id}.{entry.integrity_kind}",
                severity=entry.severity,
                domain="referential_integrity",
                split=entry.split,
                business_id=entry.business_id,
                source_id=entry.source_id,
                field=entry.integrity_kind,
                count=entry.affected_count,
                denominator=entry.denominator,
                ratio=entry.ratio,
                status=entry.status,
                evidence=entry.evidence,
                hypothesis="the two tables do not share the same key semantics",
                alternative_explanation="the candidate join is simply the wrong key",
                verification="validate join keys against README entity definitions",
                owner="quality.integrity",
            )
        )
    findings.sort(key=lambda item: (SEVERITY_ORDER.get(item.severity, 9), item.finding_id))
    return tuple(findings)


def findings_summary(findings: Sequence[QualityFinding]) -> dict[str, Any]:
    by_severity: dict[str, int] = {}
    by_domain: dict[str, int] = {}
    by_business: dict[str, int] = {}
    for finding in findings:
        by_severity[finding.severity] = by_severity.get(finding.severity, 0) + 1
        by_domain[finding.domain] = by_domain.get(finding.domain, 0) + 1
        by_business[finding.business_id] = by_business.get(finding.business_id, 0) + 1
    return {
        "total": len(findings),
        "by_severity": by_severity,
        "by_domain": by_domain,
        "by_business": by_business,
    }
