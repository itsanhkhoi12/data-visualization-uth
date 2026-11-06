from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Mapping, Sequence

from common.enums import Status


class ChartStatus(str, Enum):
    IMPLEMENTED = "IMPLEMENTED"
    REUSED = "REUSED"
    EXTENDED = "EXTENDED"
    APPLICABLE = "APPLICABLE"
    NOT_APPLICABLE = "NOT APPLICABLE"
    BLOCKED = "BLOCKED"
    FAILED = "FAILED"
    UNVERIFIED = "UNVERIFIED"


class EligibilityStatus(str, Enum):
    APPLICABLE = "APPLICABLE"
    NOT_APPLICABLE = "NOT APPLICABLE"
    BLOCKED = "BLOCKED"
    MISSING_INPUT = "MISSING INPUT"
    UNVERIFIED = "UNVERIFIED"


@dataclass(frozen=True)
class DataSliceDescriptor:
    split: str
    business_id: str
    source_id: str
    object_name: str
    field: str
    semantic_role: str
    grain: str
    filters: tuple[str, ...]
    population: str
    source_hash: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "split": self.split,
            "business_id": self.business_id,
            "source_id": self.source_id,
            "object_name": self.object_name,
            "field": self.field,
            "semantic_role": self.semantic_role,
            "grain": self.grain,
            "filters": list(self.filters),
            "population": self.population,
            "source_hash": self.source_hash,
        }


@dataclass(frozen=True)
class StatResult:
    metric_id: str
    split: str
    business_id: str
    source_ids: tuple[str, ...]
    method: str
    method_version: str
    unit: str
    population_n: int | None
    valid_n: int
    missing_n: int
    invalid_n: int
    values: Mapping[str, Any]
    assumptions: tuple[str, ...] = ()
    limitations: tuple[str, ...] = ()
    status: Status = Status.PASS

    def to_dict(self) -> dict[str, Any]:
        return {
            "metric_id": self.metric_id,
            "split": self.split,
            "business_id": self.business_id,
            "source_ids": list(self.source_ids),
            "method": self.method,
            "method_version": self.method_version,
            "unit": self.unit,
            "population_n": self.population_n,
            "valid_n": self.valid_n,
            "missing_n": self.missing_n,
            "invalid_n": self.invalid_n,
            "values": dict(self.values),
            "assumptions": list(self.assumptions),
            "limitations": list(self.limitations),
            "status": self.status.value,
        }


@dataclass(frozen=True)
class ChartSpec:
    chart_id: str
    title: str
    research_question: str
    reason_for_inclusion: str
    analysis_level: str
    applicable_data_type: str
    input_source_ids: tuple[str, ...]
    input_columns: tuple[str, ...]
    preprocessing_prerequisites: tuple[str, ...]
    statistical_method: str
    calculation_or_formula: str
    chart_type: str
    x_axis: str
    y_axis: str
    unit: str
    grouping: str
    sampling_strategy: str
    missing_handling: str
    outlier_handling: str
    expected_interpretation: str
    scientific_limitations: tuple[str, ...]
    module_owner: str
    artifact_output_path: str
    notebook_section: str
    tests: tuple[str, ...]
    acceptance_criteria: str
    status: ChartStatus = ChartStatus.IMPLEMENTED
    reason: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "chart_id": self.chart_id,
            "title": self.title,
            "research_question": self.research_question,
            "reason_for_inclusion": self.reason_for_inclusion,
            "analysis_level": self.analysis_level,
            "applicable_data_type": self.applicable_data_type,
            "input_source_ids": list(self.input_source_ids),
            "input_columns": list(self.input_columns),
            "preprocessing_prerequisites": list(self.preprocessing_prerequisites),
            "statistical_method": self.statistical_method,
            "calculation_or_formula": self.calculation_or_formula,
            "chart_type": self.chart_type,
            "x_axis": self.x_axis,
            "y_axis": self.y_axis,
            "unit": self.unit,
            "grouping": self.grouping,
            "sampling_strategy": self.sampling_strategy,
            "missing_handling": self.missing_handling,
            "outlier_handling": self.outlier_handling,
            "expected_interpretation": self.expected_interpretation,
            "scientific_limitations": list(self.scientific_limitations),
            "module_owner": self.module_owner,
            "artifact_output_path": self.artifact_output_path,
            "notebook_section": self.notebook_section,
            "tests": list(self.tests),
            "acceptance_criteria": self.acceptance_criteria,
            "status": self.status.value,
            "reason": self.reason,
        }


@dataclass(frozen=True)
class FigureArtifact:
    figure_id: str
    chart_id: str
    run_id: str
    split: str
    business_id: str
    source_ids: tuple[str, ...]
    spec_version: str
    output_path: str
    artifact_hash: str
    status: Status
    reason: str = ""
    population_n: int | None = None
    sample_n: int | None = None
    method: str = ""
    unit: str = ""
    limitations: tuple[str, ...] = ()
    findings: tuple[str, ...] = ()

    def to_dict(self) -> dict[str, Any]:
        return {
            "figure_id": self.figure_id,
            "chart_id": self.chart_id,
            "run_id": self.run_id,
            "split": self.split,
            "business_id": self.business_id,
            "source_ids": list(self.source_ids),
            "spec_version": self.spec_version,
            "output_path": self.output_path,
            "artifact_hash": self.artifact_hash,
            "status": self.status.value,
            "reason": self.reason,
            "population_n": self.population_n,
            "sample_n": self.sample_n,
            "method": self.method,
            "unit": self.unit,
            "limitations": list(self.limitations),
            "findings": list(self.findings),
        }


@dataclass(frozen=True)
class Finding:
    finding_id: str
    chart_id: str
    split: str
    business_id: str
    claim: str
    evidence: str
    metric_refs: tuple[str, ...]
    unit: str
    population_n: int | None
    method: str
    limitations: tuple[str, ...]
    confidence: str
    status: Status = Status.VERIFIED

    def to_dict(self) -> dict[str, Any]:
        return {
            "finding_id": self.finding_id,
            "chart_id": self.chart_id,
            "split": self.split,
            "business_id": self.business_id,
            "claim": self.claim,
            "evidence": self.evidence,
            "metric_refs": list(self.metric_refs),
            "unit": self.unit,
            "population_n": self.population_n,
            "method": self.method,
            "limitations": list(self.limitations),
            "confidence": self.confidence,
            "status": self.status.value,
        }


@dataclass(frozen=True)
class EligibilityDecision:
    chart_id: str
    split: str
    business_id: str
    status: EligibilityStatus
    reason: str
    required_evidence: tuple[str, ...] = ()
    available_evidence: tuple[str, ...] = ()
    source_ids: tuple[str, ...] = ()

    def to_dict(self) -> dict[str, Any]:
        return {
            "chart_id": self.chart_id,
            "split": self.split,
            "business_id": self.business_id,
            "status": self.status.value,
            "reason": self.reason,
            "required_evidence": list(self.required_evidence),
            "available_evidence": list(self.available_evidence),
            "source_ids": list(self.source_ids),
        }


@dataclass(frozen=True)
class StoryCard:
    story_id: str
    chart_id: str
    split: str
    business_id: str
    objective: str
    context: str
    methodology: str
    statistics: tuple[str, ...]
    figure_reference: str
    observations: tuple[str, ...]
    implications: str
    limitations: tuple[str, ...]
    conclusion: str
    evidence_refs: tuple[str, ...]
    confidence: str
    status: Status = Status.VERIFIED

    def to_dict(self) -> dict[str, Any]:
        return {
            "story_id": self.story_id,
            "chart_id": self.chart_id,
            "split": self.split,
            "business_id": self.business_id,
            "objective": self.objective,
            "context": self.context,
            "methodology": self.methodology,
            "statistics": list(self.statistics),
            "figure_reference": self.figure_reference,
            "observations": list(self.observations),
            "implications": self.implications,
            "limitations": list(self.limitations),
            "conclusion": self.conclusion,
            "evidence_refs": list(self.evidence_refs),
            "confidence": self.confidence,
            "status": self.status.value,
        }


@dataclass(frozen=True)
class ChartCoverage:
    chart_id: str
    family: str
    status: ChartStatus
    reason: str
    rendered_count: int = 0
    applicable_count: int = 0
    blocked_count: int = 0
    not_applicable_count: int = 0
    notebook_section: str = ""
    details: Mapping[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "chart_id": self.chart_id,
            "family": self.family,
            "status": self.status.value,
            "reason": self.reason,
            "rendered_count": self.rendered_count,
            "applicable_count": self.applicable_count,
            "blocked_count": self.blocked_count,
            "not_applicable_count": self.not_applicable_count,
            "notebook_section": self.notebook_section,
            "details": dict(self.details),
        }


def chart_families(specs: Sequence[ChartSpec]) -> dict[str, list[str]]:
    families: dict[str, list[str]] = {}
    for spec in specs:
        families.setdefault(spec.chart_id[:4].rstrip("0123456789"), []).append(
            spec.chart_id
        )
    return families
