from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Mapping, Sequence

from common.enums import EvidenceStatus, Status


@dataclass(frozen=True)
class SourceRecord:
    source_id: str
    split: str
    business_id: str
    source_type: str
    logical_path: str
    absolute_path: str
    size_bytes: int
    content_hash: str
    status: Status = Status.PASS
    evidence: EvidenceStatus = EvidenceStatus.FILESYSTEM_VERIFIED
    sheet_name: str | None = None
    table_name: str | None = None
    row_count: int | None = None
    column_count: int | None = None
    warnings: tuple[str, ...] = ()

    def to_dict(self) -> dict[str, Any]:
        payload = {
            "source_id": self.source_id,
            "split": self.split,
            "business_id": self.business_id,
            "source_type": self.source_type,
            "logical_path": self.logical_path,
            "absolute_path": self.absolute_path,
            "size_bytes": self.size_bytes,
            "content_hash": self.content_hash,
            "status": self.status.value,
            "evidence": self.evidence.value,
            "sheet_name": self.sheet_name,
            "table_name": self.table_name,
            "row_count": self.row_count,
            "column_count": self.column_count,
            "warnings": list(self.warnings),
        }
        return payload


@dataclass(frozen=True)
class StatResult:
    metric_id: str
    split: str
    business_id: str
    source_ids: tuple[str, ...]
    method: str
    method_version: str
    row_grain: str
    population_n: int | None
    processed_n: int
    sample_n: int | None
    unit: str | None
    status: Status
    values: Mapping[str, Any]
    evidence: tuple[str, ...] = ()
    warnings: tuple[str, ...] = ()
    limitations: tuple[str, ...] = ()
    rule_id: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "metric_id": self.metric_id,
            "split": self.split,
            "business_id": self.business_id,
            "source_ids": list(self.source_ids),
            "method": self.method,
            "method_version": self.method_version,
            "row_grain": self.row_grain,
            "population_n": self.population_n,
            "processed_n": self.processed_n,
            "sample_n": self.sample_n,
            "unit": self.unit,
            "status": self.status.value,
            "values": dict(self.values),
            "evidence": list(self.evidence),
            "warnings": list(self.warnings),
            "limitations": list(self.limitations),
            "rule_id": self.rule_id,
        }


@dataclass(frozen=True)
class GateResult:
    phase: str
    gate: str
    status: Status
    reason: str
    owner: str
    artifact: str | None = None
    checks: tuple[Mapping[str, Any], ...] = ()

    def to_dict(self) -> dict[str, Any]:
        return {
            "phase": self.phase,
            "gate": self.gate,
            "status": self.status.value,
            "reason": self.reason,
            "owner": self.owner,
            "artifact": self.artifact,
            "checks": [dict(check) for check in self.checks],
        }


@dataclass(frozen=True)
class ColumnProfile:
    source_id: str
    split: str
    business_id: str
    column: str
    physical_type: str
    semantic_type: str
    unit: str | None
    non_null_n: int
    null_n: int
    distinct_n: int
    parse_failure_n: int
    confidence: float
    sample_values: tuple[str, ...] = ()
    status: Status = Status.PASS

    def to_dict(self) -> dict[str, Any]:
        return {
            "source_id": self.source_id,
            "split": self.split,
            "business_id": self.business_id,
            "column": self.column,
            "physical_type": self.physical_type,
            "semantic_type": self.semantic_type,
            "unit": self.unit,
            "non_null_n": self.non_null_n,
            "null_n": self.null_n,
            "distinct_n": self.distinct_n,
            "parse_failure_n": self.parse_failure_n,
            "confidence": self.confidence,
            "sample_values": list(self.sample_values),
            "status": self.status.value,
        }


@dataclass(frozen=True)
class RelationEvidence:
    relation_id: str
    split: str
    business_id: str
    left_source: str
    right_source: str
    join_keys: tuple[str, ...]
    left_grain: str
    right_grain: str
    status: str
    left_rows: int
    right_rows: int
    matched_rows: int
    unmatched_left_rows: int
    unmatched_right_rows: int
    key_null_left: int
    key_null_right: int
    duplicate_key_left: int
    duplicate_key_right: int
    fanout_factor: float
    expected_invariant: str
    evidence: tuple[str, ...] = ()
    risk: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "relation_id": self.relation_id,
            "split": self.split,
            "business_id": self.business_id,
            "left_source": self.left_source,
            "right_source": self.right_source,
            "join_keys": list(self.join_keys),
            "left_grain": self.left_grain,
            "right_grain": self.right_grain,
            "status": self.status,
            "left_rows": self.left_rows,
            "right_rows": self.right_rows,
            "matched_rows": self.matched_rows,
            "unmatched_left_rows": self.unmatched_left_rows,
            "unmatched_right_rows": self.unmatched_right_rows,
            "key_null_left": self.key_null_left,
            "key_null_right": self.key_null_right,
            "duplicate_key_left": self.duplicate_key_left,
            "duplicate_key_right": self.duplicate_key_right,
            "fanout_factor": self.fanout_factor,
            "expected_invariant": self.expected_invariant,
            "evidence": list(self.evidence),
            "risk": self.risk,
        }


@dataclass(frozen=True)
class QualityFinding:
    finding_id: str
    severity: str
    domain: str
    split: str
    business_id: str
    source_id: str
    field: str | None
    count: int
    denominator: int
    ratio: float
    status: Status
    evidence: str
    hypothesis: str | None = None
    alternative_explanation: str | None = None
    verification: str | None = None
    owner: str = "quality"

    def to_dict(self) -> dict[str, Any]:
        return {
            "finding_id": self.finding_id,
            "severity": self.severity,
            "domain": self.domain,
            "split": self.split,
            "business_id": self.business_id,
            "source_id": self.source_id,
            "field": self.field,
            "count": self.count,
            "denominator": self.denominator,
            "ratio": self.ratio,
            "status": self.status.value,
            "evidence": self.evidence,
            "hypothesis": self.hypothesis,
            "alternative_explanation": self.alternative_explanation,
            "verification": self.verification,
            "owner": self.owner,
        }


@dataclass(frozen=True)
class MetricDefinition:
    metric_id: str
    split: str
    business_id: str
    name: str
    grain: str
    numerator: str
    denominator: str | None
    filters: tuple[str, ...]
    status_handling: str
    as_of_semantics: str
    unit: str
    rounding: str
    null_behavior: str
    join_path: tuple[str, ...]
    rule_id: str | None
    source_columns: tuple[str, ...]
    formula_status: Status

    def to_dict(self) -> dict[str, Any]:
        return {
            "metric_id": self.metric_id,
            "split": self.split,
            "business_id": self.business_id,
            "name": self.name,
            "grain": self.grain,
            "numerator": self.numerator,
            "denominator": self.denominator,
            "filters": list(self.filters),
            "status_handling": self.status_handling,
            "as_of_semantics": self.as_of_semantics,
            "unit": self.unit,
            "rounding": self.rounding,
            "null_behavior": self.null_behavior,
            "join_path": list(self.join_path),
            "rule_id": self.rule_id,
            "source_columns": list(self.source_columns),
            "formula_status": self.formula_status.value,
        }


@dataclass(frozen=True)
class ChartSpecification:
    chart_id: str
    research_question: str
    chart_type: str
    x_label: str
    y_label: str
    unit: str
    owner_module: str
    split: str
    business_id: str
    inputs: tuple[str, ...]
    calculations: str
    groups: str | None = None
    sample_strategy: str = "full_population"
    output_relpath: str = ""
    caption: str = ""
    interpretation: str = ""
    limitations: tuple[str, ...] = ()
    status: Status = Status.PASS

    def to_dict(self) -> dict[str, Any]:
        return {
            "chart_id": self.chart_id,
            "research_question": self.research_question,
            "chart_type": self.chart_type,
            "x_label": self.x_label,
            "y_label": self.y_label,
            "unit": self.unit,
            "owner_module": self.owner_module,
            "split": self.split,
            "business_id": self.business_id,
            "inputs": list(self.inputs),
            "calculations": self.calculations,
            "groups": self.groups,
            "sample_strategy": self.sample_strategy,
            "output_relpath": self.output_relpath,
            "caption": self.caption,
            "interpretation": self.interpretation,
            "limitations": list(self.limitations),
            "status": self.status.value,
        }


@dataclass(frozen=True)
class TableSpecification:
    table_id: str
    title: str
    subtitle: str
    caption: str
    input_artifact: str
    required_columns: tuple[str, ...]
    grain: str
    owner_module: str
    column_units: Mapping[str, str] = field(default_factory=dict)
    precision: Mapping[str, int] = field(default_factory=dict)
    max_width: str = "100%"
    status: Status = Status.PASS

    def to_dict(self) -> dict[str, Any]:
        return {
            "table_id": self.table_id,
            "title": self.title,
            "subtitle": self.subtitle,
            "caption": self.caption,
            "input_artifact": self.input_artifact,
            "required_columns": list(self.required_columns),
            "grain": self.grain,
            "owner_module": self.owner_module,
            "column_units": dict(self.column_units),
            "precision": dict(self.precision),
            "max_width": self.max_width,
            "status": self.status.value,
        }


@dataclass(frozen=True)
class ArtifactManifest:
    run_id: str
    artifact_id: str
    split: str
    business_id: str
    source_id: str
    source_hash: str
    rule_hash: str
    config_hash: str
    method_name: str
    method_version: str
    population_size: int | None
    observed_n: int
    sampled_n: int | None
    sample_strategy: str
    skipped_n: int
    status: Status
    generation_ts: str
    output_relpath: str
    evidence_refs: tuple[str, ...]
    parent_artifact_ids: tuple[str, ...]
    privacy_classification: str
    content_checksum: str
    qa_gate: str
    artifact_kind: str = "artifact"

    def to_dict(self) -> dict[str, Any]:
        return {
            "run_id": self.run_id,
            "artifact_id": self.artifact_id,
            "artifact_kind": self.artifact_kind,
            "split": self.split,
            "business_id": self.business_id,
            "source_id": self.source_id,
            "source_hash": self.source_hash,
            "rule_hash": self.rule_hash,
            "config_hash": self.config_hash,
            "method_name": self.method_name,
            "method_version": self.method_version,
            "population_size": self.population_size,
            "observed_n": self.observed_n,
            "sampled_n": self.sampled_n,
            "sample_strategy": self.sample_strategy,
            "skipped_n": self.skipped_n,
            "status": self.status.value,
            "generation_ts": self.generation_ts,
            "output_relpath": self.output_relpath,
            "evidence_refs": list(self.evidence_refs),
            "parent_artifact_ids": list(self.parent_artifact_ids),
            "privacy_classification": self.privacy_classification,
            "content_checksum": self.content_checksum,
            "qa_gate": self.qa_gate,
        }


@dataclass(frozen=True)
class EvidenceRef:
    evidence_id: str
    split: str
    business_id: str
    source_id: str
    source_hash: str
    method: str
    method_version: str
    locator: str
    detail: str
    status: EvidenceStatus = EvidenceStatus.DATA_VERIFIED

    def to_dict(self) -> dict[str, Any]:
        return {
            "evidence_id": self.evidence_id,
            "split": self.split,
            "business_id": self.business_id,
            "source_id": self.source_id,
            "source_hash": self.source_hash,
            "method": self.method,
            "method_version": self.method_version,
            "locator": self.locator,
            "detail": self.detail,
            "status": self.status.value,
        }


@dataclass(frozen=True)
class NumericStats:
    source_id: str
    split: str
    business_id: str
    field: str
    unit: str | None
    n_total: int
    n_valid: int
    n_missing: int
    n_zero: int
    mean: float | None
    median: float | None
    std: float | None
    variance: float | None
    minimum: float | None
    maximum: float | None
    q25: float | None
    q75: float | None
    iqr: float | None
    mad: float | None
    skewness: float | None
    kurtosis: float | None
    zero_ratio: float
    method: str
    method_version: str
    status: Status
    warnings: tuple[str, ...] = ()

    def to_dict(self) -> dict[str, Any]:
        return {
            "source_id": self.source_id,
            "split": self.split,
            "business_id": self.business_id,
            "field": self.field,
            "unit": self.unit,
            "n_total": self.n_total,
            "n_valid": self.n_valid,
            "n_missing": self.n_missing,
            "n_zero": self.n_zero,
            "mean": self.mean,
            "median": self.median,
            "std": self.std,
            "variance": self.variance,
            "minimum": self.minimum,
            "maximum": self.maximum,
            "q25": self.q25,
            "q75": self.q75,
            "iqr": self.iqr,
            "mad": self.mad,
            "skewness": self.skewness,
            "kurtosis": self.kurtosis,
            "zero_ratio": self.zero_ratio,
            "method": self.method,
            "method_version": self.method_version,
            "status": self.status.value,
            "warnings": list(self.warnings),
        }


@dataclass(frozen=True)
class CategoricalStats:
    source_id: str
    split: str
    business_id: str
    field: str
    category: str
    count: int
    share: float
    is_null: bool
    rank: int
    method: str
    method_version: str
    status: Status

    def to_dict(self) -> dict[str, Any]:
        return {
            "source_id": self.source_id,
            "split": self.split,
            "business_id": self.business_id,
            "field": self.field,
            "category": self.category,
            "count": self.count,
            "share": self.share,
            "is_null": self.is_null,
            "rank": self.rank,
            "method": self.method,
            "method_version": self.method_version,
            "status": self.status.value,
        }


def records_to_dicts(records: Sequence[Any]) -> list[dict[str, Any]]:
    return [record.to_dict() for record in records]
