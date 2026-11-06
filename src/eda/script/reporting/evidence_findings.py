from __future__ import annotations

import hashlib
from dataclasses import dataclass, field
from typing import Any, Mapping, Sequence

from common.enums import Status
from common.visual_contracts import Finding
from reporting.vietnamese_templates import (
    TEMPLATES_BY_ID,
    escape_text,
    format_integer,
    format_number,
    format_percent,
    render_template,
)


@dataclass(frozen=True)
class ProvenanceRef:
    artifact_id: str
    artifact_path: str
    source_ids: tuple[str, ...]
    source_hashes: tuple[str, ...]
    method: str
    method_version: str
    population_n: int | None
    run_id: str
    split: str
    business_id: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "artifact_id": self.artifact_id,
            "artifact_path": self.artifact_path,
            "source_ids": list(self.source_ids),
            "source_hashes": list(self.source_hashes),
            "method": self.method,
            "method_version": self.method_version,
            "population_n": self.population_n,
            "run_id": self.run_id,
            "split": self.split,
            "business_id": self.business_id,
        }


@dataclass(frozen=True)
class EvidenceMetric:
    metric_id: str
    label: str
    value: Any
    unit: str
    population_n: int | None
    valid_n: int | None
    method: str
    extra: Mapping[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "metric_id": self.metric_id,
            "label": self.label,
            "value": self.value,
            "unit": self.unit,
            "population_n": self.population_n,
            "valid_n": self.valid_n,
            "method": self.method,
            "extra": dict(self.extra),
        }


@dataclass
class FindingSet:
    findings: list[Finding] = field(default_factory=list)
    suppressed: list[dict[str, Any]] = field(default_factory=list)

    def add(self, finding: Finding) -> None:
        self.findings.append(finding)

    def suppress(self, reason: str, context: Mapping[str, Any]) -> None:
        self.suppressed.append({"reason": reason, **dict(context)})

    def to_dict(self) -> dict[str, Any]:
        return {
            "finding_count": len(self.findings),
            "findings": [item.to_dict() for item in self.findings],
            "suppressed": list(self.suppressed),
        }


def evidence_hash(provenance: ProvenanceRef, metric_ids: Sequence[str]) -> str:
    parts = [
        provenance.artifact_id,
        provenance.method,
        provenance.method_version,
        str(provenance.population_n),
        ",".join(sorted(metric_ids)),
        ",".join(sorted(provenance.source_hashes)),
    ]
    return f"sha256:{hashlib.sha256('|'.join(parts).encode('utf-8')).hexdigest()}"


def _finding_id(
    template_id: str, split: str, business_id: str, metric_id: str
) -> str:
    digest = hashlib.sha256(
        f"{template_id}|{split}|{business_id}|{metric_id}".encode("utf-8")
    ).hexdigest()[:12]
    return f"FND.{template_id}.{digest}"


def _numeric_values(metric: EvidenceMetric) -> dict[str, Any]:
    values: dict[str, Any] = {}
    for key, value in metric.extra.items():
        values[key] = value
    values.setdefault("value", metric.value)
    values.setdefault("unit", metric.unit)
    values.setdefault("population_n", metric.population_n)
    return values


def _confidence(
    metric: EvidenceMetric, provenance: ProvenanceRef
) -> str:
    if metric.population_n is None or metric.population_n == 0:
        return "NEEDS_REVIEW"
    if not provenance.source_hashes:
        return "NEEDS_REVIEW"
    return "VERIFIED"


def create_evidence_findings(
    metrics: Sequence[EvidenceMetric],
    provenance: Mapping[str, ProvenanceRef],
    run_id: str = "",
    split: str = "",
) -> FindingSet:
    result = FindingSet()
    for metric in metrics:
        reference = provenance.get(metric.metric_id)
        if reference is None:
            result.suppress(
                "missing_provenance_reference",
                {"metric_id": metric.metric_id, "label": metric.label},
            )
            continue
        template_id = metric.extra.get("template_id")
        if not isinstance(template_id, str) or template_id not in TEMPLATES_BY_ID:
            result.suppress(
                "unknown_or_missing_template_id",
                {"metric_id": metric.metric_id, "template_id": template_id},
            )
            continue
        payload: dict[str, Any] = {
            "business_id": reference.business_id,
            "split": reference.split,
            "artifact_id": reference.artifact_id,
        }
        for key, value in _numeric_values(metric).items():
            if value is None:
                continue
            payload[key] = value
        payload["template_id"] = template_id
        claim = render_template(template_id, payload)
        if claim is None:
            result.suppress(
                "insufficient_metric_fields_for_template",
                {
                    "metric_id": metric.metric_id,
                    "template_id": template_id,
                    "required_fields": list(
                        TEMPLATES_BY_ID[template_id].required_fields
                    ),
                },
            )
            continue
        limitations = tuple(metric.extra.get("limitations", ())) or (
            "kết luận chỉ mô tả số liệu quan sát, không suy ra quan hệ nhân quả",
        )
        result.add(
            Finding(
                finding_id=_finding_id(
                    template_id, reference.split, reference.business_id, metric.metric_id
                ),
                chart_id=str(metric.extra.get("chart_id", "")),
                split=reference.split,
                business_id=reference.business_id,
                claim=claim,
                evidence=(
                    f"metric={metric.metric_id}; method={reference.method}; "
                    f"method_version={reference.method_version}; "
                    f"evidence_hash={evidence_hash(reference, [metric.metric_id])}"
                ),
                metric_refs=(metric.metric_id,),
                unit=metric.unit,
                population_n=metric.population_n,
                method=reference.method,
                limitations=limitations,
                confidence=_confidence(metric, reference),
                status=Status.VERIFIED,
            )
        )
    return result


def metric_from_numeric_profile(
    metric_id: str,
    field_label: str,
    dispersion: Any,
    unit: str,
    outlier_n: int,
    method: str,
    chart_id: str,
    limitations: Sequence[str] = (),
) -> EvidenceMetric:
    return EvidenceMetric(
        metric_id=metric_id,
        label=field_label,
        value=dispersion.median,
        unit=unit,
        population_n=dispersion.n_valid,
        valid_n=dispersion.n_valid,
        method=method,
        extra={
            "template_id": "NUM_DISTRIBUTION",
            "field_label": field_label,
            "n_valid": format_integer(dispersion.n_valid),
            "n_total": format_integer(dispersion.n_total),
            "median": format_number(dispersion.median),
            "q1": format_number(dispersion.q25),
            "q3": format_number(dispersion.q75),
            "iqr": format_number(dispersion.iqr),
            "outlier_n": format_integer(outlier_n),
            "method": method,
            "unit": unit,
            "chart_id": chart_id,
            "limitations": tuple(limitations),
        },
    )


def metric_from_business_payload(
    metric_id: str,
    label: str,
    business_id: str,
    value: Any,
    unit: str,
    population_n: int,
    grain: str,
    method: str,
    chart_id: str,
    status_filter: str = "theo quy tắc trạng thái của rulebook split",
    limitations: Sequence[str] = (),
) -> EvidenceMetric:
    return EvidenceMetric(
        metric_id=metric_id,
        label=label,
        value=value,
        unit=unit,
        population_n=population_n,
        valid_n=population_n,
        method=method,
        extra={
            "template_id": "BUSINESS_KPI",
            "business_id": business_id,
            "metric_label": label,
            "value": format_number(value),
            "unit": unit,
            "population_n": format_integer(population_n),
            "grain": grain,
            "method": method,
            "status_filter": status_filter,
            "chart_id": chart_id,
            "limitations": tuple(limitations),
        },
    )


def metric_from_missingness(
    metric_id: str,
    field_label: str,
    business_id: str,
    n_missing: int,
    n_total: int,
    missing_ratio: float,
    chart_id: str,
    limitations: Sequence[str] = (),
) -> EvidenceMetric:
    return EvidenceMetric(
        metric_id=metric_id,
        label=field_label,
        value=missing_ratio,
        unit="ratio",
        population_n=n_total,
        valid_n=n_total - n_missing,
        method="missingness_profile",
        extra={
            "template_id": "QUALITY_MISSING",
            "business_id": business_id,
            "field_label": field_label,
            "n_missing": format_integer(n_missing),
            "n_total": format_integer(n_total),
            "missing_ratio": format_percent(missing_ratio),
            "chart_id": chart_id,
            "limitations": tuple(limitations),
        },
    )


def metric_from_temporal_coverage(
    metric_id: str,
    field_label: str,
    business_id: str,
    n_valid: int,
    min_date: str,
    max_date: str,
    active_days: int,
    chart_id: str,
    limitations: Sequence[str] = (),
) -> EvidenceMetric:
    return EvidenceMetric(
        metric_id=metric_id,
        label=field_label,
        value=n_valid,
        unit="timestamp",
        population_n=n_valid,
        valid_n=n_valid,
        method="temporal_coverage_profile",
        extra={
            "template_id": "TEMPORAL_COVERAGE",
            "business_id": business_id,
            "field_label": field_label,
            "n_valid": format_integer(n_valid),
            "min_date": min_date,
            "max_date": max_date,
            "active_days": format_integer(active_days),
            "chart_id": chart_id,
            "limitations": tuple(limitations),
        },
    )


def metric_from_global_coverage(
    metric_id: str,
    split: str,
    business_count: int,
    pass_count: int,
    partial_count: int,
    blocked_count: int,
    source_file_count: int,
    chart_id: str,
    limitations: Sequence[str] = (),
) -> EvidenceMetric:
    return EvidenceMetric(
        metric_id=metric_id,
        label="global_coverage",
        value=business_count,
        unit="business",
        population_n=business_count,
        valid_n=business_count,
        method="cross_business_aggregate",
        extra={
            "template_id": "GLOBAL_COVERAGE",
            "split": split,
            "business_count": format_integer(business_count),
            "pass_count": format_integer(pass_count),
            "partial_count": format_integer(partial_count),
            "blocked_count": format_integer(blocked_count),
            "source_file_count": format_integer(source_file_count),
            "chart_id": chart_id,
            "limitations": tuple(limitations),
        },
    )


def metric_from_question_profile(
    metric_id: str,
    split: str,
    question_count: int,
    median_length: float,
    intent_count: int,
    time_expression_count: int,
    chart_id: str,
    limitations: Sequence[str] = (),
) -> EvidenceMetric:
    return EvidenceMetric(
        metric_id=metric_id,
        label="question_profile",
        value=question_count,
        unit="question",
        population_n=question_count,
        valid_n=question_count,
        method="questions_question_profile",
        extra={
            "template_id": "QUESTION_PROFILE",
            "split": split,
            "question_count": format_integer(question_count),
            "median_length": format_number(median_length),
            "intent_count": format_integer(intent_count),
            "time_expression_count": format_integer(time_expression_count),
            "chart_id": chart_id,
            "limitations": tuple(limitations),
        },
    )


def not_applicable_finding(
    chart_id: str,
    business_id: str,
    split: str,
    reason: str,
) -> Finding:
    payload = {
        "chart_id": chart_id,
        "business_id": business_id,
        "split": split,
        "reason": reason,
    }
    claim = render_template("NOT_APPLICABLE", payload) or escape_text(reason)
    return Finding(
        finding_id=_finding_id("NOT_APPLICABLE", split, business_id, chart_id),
        chart_id=chart_id,
        split=split,
        business_id=business_id,
        claim=claim,
        evidence="no eligible evidence for this chart in this business",
        metric_refs=(),
        unit="not applicable",
        population_n=None,
        method="eligibility_gate",
        limitations=("biểu đồ không được thay thế bằng dữ liệu khác điều kiện",),
        confidence="NEEDS_REVIEW",
        status=Status.NOT_APPLICABLE,
    )
