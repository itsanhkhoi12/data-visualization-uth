from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping

from common.contracts import TableSpecification
from common.enums import Status

TABLE_CATALOGUE: tuple[TableSpecification, ...] = (
    TableSpecification(
        table_id="TBL01",
        title="Project Overview",
        subtitle="Split-level source coverage",
        caption="Source and business counts per split; counts are source objects, not transactions.",
        input_artifact="run_manifest",
        required_columns=("split", "status", "source_count", "business_count"),
        grain="split",
        owner_module="cross_business.aggregate",
    ),
    TableSpecification(
        table_id="TBL02",
        title="Source Inventory",
        subtitle="Every file discovered in the split",
        caption="All source files with size, hash and read status.",
        input_artifact="file_manifest",
        required_columns=(
            "source_id",
            "split",
            "business_id",
            "source_type",
            "logical_path",
            "size_bytes",
            "content_hash",
            "status",
        ),
        grain="file",
        owner_module="inventory.file_manifest",
    ),
    TableSpecification(
        table_id="TBL03",
        title="Sheet Registry",
        subtitle="Worksheets found in every workbook",
        caption="One row per worksheet with header confidence and row count.",
        input_artifact="sheet_registry",
        required_columns=(
            "workbook_path",
            "sheet_name",
            "sheet_state",
            "data_row_count",
            "header_confidence",
        ),
        grain="worksheet",
        owner_module="inventory.sheet_registry",
    ),
    TableSpecification(
        table_id="TBL04",
        title="SQLite Registry",
        subtitle="Tables and views in each database",
        caption="One row per database object with key and row count metadata.",
        input_artifact="sqlite_registry",
        required_columns=(
            "database_path",
            "object_type",
            "object_name",
            "primary_key",
            "row_count",
        ),
        grain="database object",
        owner_module="inventory.sqlite_registry",
    ),
    TableSpecification(
        table_id="TBL05",
        title="Column Metadata",
        subtitle="Semantic typing of every column",
        caption="Physical and semantic type per column with parse failure counts.",
        input_artifact="column_registry",
        required_columns=(
            "source_id",
            "column",
            "physical_type",
            "semantic_type",
            "unit",
            "parse_failure_n",
        ),
        grain="column",
        owner_module="schema.column_registry",
    ),
    TableSpecification(
        table_id="TBL06",
        title="Missing Values",
        subtitle="Missingness per column with denominator",
        caption="Missing counts, ratios and null classification per column.",
        input_artifact="missing_registry",
        required_columns=(
            "source_id",
            "column",
            "n_missing",
            "n_total",
            "missing_ratio",
            "null_kind",
        ),
        grain="column",
        owner_module="quality.missingness",
    ),
    TableSpecification(
        table_id="TBL07",
        title="Duplicates",
        subtitle="Exact-row and business-key duplication",
        caption="Duplicate counts per grain; rows are never deleted automatically.",
        input_artifact="duplicate_registry",
        required_columns=(
            "source_id",
            "duplicate_class",
            "n_duplicate_rows",
            "total_n",
            "explanation",
        ),
        grain="duplicate rule",
        owner_module="quality.duplicates",
    ),
    TableSpecification(
        table_id="TBL08",
        title="Invalid Values",
        subtitle="Documented validation rules applied",
        caption="Violation counts per rule with denominator and masked examples.",
        input_artifact="validity_registry",
        required_columns=(
            "source_id",
            "column",
            "rule_id",
            "invalid_count",
            "denominator",
            "evidence",
        ),
        grain="validation rule",
        owner_module="quality.validity",
    ),
    TableSpecification(
        table_id="TBL09",
        title="Numeric Statistics",
        subtitle="Descriptive statistics per measure",
        caption="Full-population descriptive statistics with method and units.",
        input_artifact="numeric_stats",
        required_columns=(
            "source_id",
            "field",
            "n_valid",
            "mean",
            "median",
            "std",
            "q25",
            "q75",
            "unit",
        ),
        grain="measure",
        owner_module="statistics.numeric",
    ),
    TableSpecification(
        table_id="TBL10",
        title="Categorical Statistics",
        subtitle="Category frequencies per field",
        caption="Category counts and shares; totals include null and Others.",
        input_artifact="categorical_stats",
        required_columns=(
            "source_id",
            "field",
            "category",
            "count",
            "share",
            "is_null",
        ),
        grain="field and category",
        owner_module="statistics.categorical",
    ),
    TableSpecification(
        table_id="TBL11",
        title="Temporal Profile",
        subtitle="Date semantics and coverage per source",
        caption="Event role, coverage window and missing periods per date column.",
        input_artifact="temporal_profile",
        required_columns=(
            "source_id",
            "column",
            "event_role",
            "min_date",
            "max_date",
            "active_days",
            "missing_months",
        ),
        grain="source and date column",
        owner_module="temporal.coverage",
    ),
    TableSpecification(
        table_id="TBL12",
        title="Relationship and Fanout",
        subtitle="Join candidates with cardinality evidence",
        caption="Key matching, orphan counts and fanout per candidate relation.",
        input_artifact="relation_evidence",
        required_columns=(
            "left_source",
            "right_source",
            "join_keys",
            "matched_rows",
            "unmatched_left_rows",
            "duplicate_key_left",
            "fanout_factor",
            "status",
        ),
        grain="relation",
        owner_module="schema.relations",
    ),
    TableSpecification(
        table_id="TBL13",
        title="Business Profile",
        subtitle="Per-business source and capability summary",
        caption="One row per business with README evidence and coverage status.",
        input_artifact="business_profile",
        required_columns=(
            "business_id",
            "split",
            "source_count",
            "readme_present",
            "domain_evidence",
            "status",
        ),
        grain="business",
        owner_module="business.business_inventory",
    ),
    TableSpecification(
        table_id="TBL14",
        title="KPI Catalogue",
        subtitle="Rule-aware metric definitions and their status",
        caption="Metric definitions with the split rule ID they depend on.",
        input_artifact="kpi_catalogue",
        required_columns=(
            "metric_id",
            "name",
            "grain",
            "rule_id",
            "unit",
            "formula_status",
        ),
        grain="metric",
        owner_module="business.kpi_catalogue",
    ),
    TableSpecification(
        table_id="TBL15",
        title="Question and Answer Metadata",
        subtitle="Question metadata per split",
        caption="Question counts, intent candidates and time expressions; no answers for public test.",
        input_artifact="question_profile",
        required_columns=(
            "split",
            "question_count",
            "unique_id_count",
            "as_of_min",
            "as_of_max",
            "status",
        ),
        grain="split",
        owner_module="questions.question_profile",
    ),
    TableSpecification(
        table_id="TBL16",
        title="Rulebook Comparison",
        subtitle="Differences between the split rulebooks",
        caption="Rules unique to or modified between train and public test rulebooks.",
        input_artifact="rule_diff",
        required_columns=(
            "conflict_id",
            "section",
            "train_rule_id",
            "public_rule_id",
            "conflict_status",
        ),
        grain="rule conflict",
        owner_module="rulebook.rule_diff",
    ),
    TableSpecification(
        table_id="TBL17",
        title="Cross-business Schema Comparison",
        subtitle="Semantic field-role presence matrix",
        caption="Semantic role presence per business with confidence.",
        input_artifact="schema_compare",
        required_columns=(
            "business_id",
            "split",
            "field_role",
            "column",
            "semantic_type",
            "confidence",
        ),
        grain="business and field role",
        owner_module="cross_business.schema_compare",
    ),
    TableSpecification(
        table_id="TBL18",
        title="Global Summary",
        subtitle="Cross-split coverage and quality summary",
        caption="Business coverage, findings by severity and explicit denominators.",
        input_artifact="global_summary",
        required_columns=(
            "split",
            "business_count",
            "pass_count",
            "partial_count",
            "blocked_count",
            "total_findings",
        ),
        grain="split",
        owner_module="cross_business.aggregate",
    ),
    TableSpecification(
        table_id="TBL19",
        title="Findings and Evidence",
        subtitle="Every classified quality finding",
        caption="Findings with severity, evidence, hypothesis and verification step.",
        input_artifact="quality_findings",
        required_columns=(
            "finding_id",
            "severity",
            "domain",
            "business_id",
            "count",
            "denominator",
            "evidence",
            "status",
        ),
        grain="finding",
        owner_module="quality.findings",
    ),
    TableSpecification(
        table_id="TBL20",
        title="Coverage and Gate Status",
        subtitle="Phase gate ledger",
        caption="One row per phase gate with status and reason.",
        input_artifact="gate_ledger",
        required_columns=("phase", "gate", "status", "reason", "owner", "artifact"),
        grain="phase gate",
        owner_module="orchestration.pipeline",
    ),
)

TABLE_SPECS_BY_ID = {spec.table_id: spec for spec in TABLE_CATALOGUE}


@dataclass(frozen=True)
class TableValidation:
    table_id: str
    valid: bool
    status: Status
    reasons: tuple[str, ...]

    def to_dict(self) -> dict[str, Any]:
        return {
            "table_id": self.table_id,
            "valid": self.valid,
            "status": self.status.value,
            "reasons": list(self.reasons),
        }


def validate_table_spec(spec: TableSpecification) -> TableValidation:
    reasons: list[str] = []
    if not spec.title:
        reasons.append("missing_title")
    if not spec.caption:
        reasons.append("missing_caption")
    if not spec.required_columns:
        reasons.append("missing_required_columns")
    if not spec.grain:
        reasons.append("missing_grain")
    if not spec.input_artifact:
        reasons.append("missing_input_artifact")
    if not spec.owner_module:
        reasons.append("missing_owner_module")
    valid = not reasons
    return TableValidation(
        table_id=spec.table_id,
        valid=valid,
        status=Status.PASS if valid else Status.BLOCKED,
        reasons=tuple(reasons),
    )


def validate_all_table_specs(
    specs: tuple[TableSpecification, ...] = TABLE_CATALOGUE,
) -> tuple[TableValidation, ...]:
    return tuple(validate_table_spec(spec) for spec in specs)


def table_registry_payload(
    specs: tuple[TableSpecification, ...] = TABLE_CATALOGUE,
    validations: tuple[TableValidation, ...] | None = None,
) -> Mapping[str, Any]:
    validations = validations or validate_all_table_specs(specs)
    validation_map = {item.table_id: item for item in validations}
    return {
        "tables": [
            {**spec.to_dict(), "validation": validation_map[spec.table_id].to_dict()}
            for spec in specs
        ],
        "table_count": len(specs),
        "valid_count": sum(1 for item in validations if item.valid),
    }
