from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping, Sequence

from common.contracts import ChartSpecification
from common.enums import ChartType, Status

CHART_CATALOGUE: tuple[ChartSpecification, ...] = (
    ChartSpecification(
        chart_id="INV01",
        research_question="Which source formats dominate each split?",
        chart_type=ChartType.GROUPED_BAR.value,
        x_label="source format",
        y_label="number of business data files",
        unit="file",
        owner_module="inventory.file_manifest",
        split="both",
        business_id="global",
        inputs=("file_manifest",),
        calculations="count business data files by split and extension",
        groups="split",
        output_relpath="figures/{run_id}/{split}/global/INV01.png",
        caption="Business data files per split by format.",
        interpretation="Shows the storage-format mix of each evaluation split.",
        limitations=("calendar, README, rulebook and question files are excluded",),
    ),
    ChartSpecification(
        chart_id="INV03",
        research_question="How many source files does each business contribute?",
        chart_type=ChartType.HORIZONTAL_BAR.value,
        x_label="business id",
        y_label="number of source files",
        unit="file",
        owner_module="inventory.file_manifest",
        split="both",
        business_id="global",
        inputs=("file_manifest",),
        calculations="count all files per business",
        groups="split",
        output_relpath="figures/{run_id}/{split}/global/INV03.png",
        caption="Source file count per business.",
        interpretation="Business complexity proxy; not a table or transaction count.",
        limitations=("file count does not measure data volume",),
    ),
    ChartSpecification(
        chart_id="INV04",
        research_question="Which workbooks contain the most worksheets?",
        chart_type=ChartType.HORIZONTAL_BAR.value,
        x_label="workbook",
        y_label="number of worksheets",
        unit="sheet",
        owner_module="inventory.sheet_registry",
        split="both",
        business_id="global",
        inputs=("sheet_registry",),
        calculations="count worksheets per workbook",
        groups="split",
        output_relpath="figures/{run_id}/{split}/global/INV04.png",
        caption="Worksheet count per workbook.",
        interpretation="Highlights workbooks holding several independent tables.",
        limitations=("formatting-only sheets are still counted",),
    ),
    ChartSpecification(
        chart_id="INV06",
        research_question="Where is the largest volume of rows located?",
        chart_type=ChartType.DOT.value,
        x_label="row count (log scale)",
        y_label="source object",
        unit="row",
        owner_module="inventory.sheet_registry",
        split="both",
        business_id="global",
        inputs=("sheet_registry", "sqlite_registry"),
        calculations="row count per sheet or table",
        groups="source kind",
        output_relpath="figures/{run_id}/{split}/global/INV06.png",
        caption="Row count per source object on a log scale.",
        interpretation="Identifies the objects that dominate runtime and memory.",
        limitations=("rows are not transactions and are never summed across grains",),
    ),
    ChartSpecification(
        chart_id="DQ01",
        research_question="Which fields lose the most values?",
        chart_type=ChartType.HORIZONTAL_BAR.value,
        x_label="field",
        y_label="missing ratio",
        unit="percent",
        owner_module="quality.missingness",
        split="both",
        business_id="global",
        inputs=("missing_registry",),
        calculations="missing_n divided by total_n per column",
        groups="business",
        output_relpath="figures/{run_id}/{split}/global/DQ01.png",
        caption="Missing-value ratio per field with its denominator.",
        interpretation="Ranks fields whose absence limits downstream analysis.",
        limitations=("structural blanks are reported separately from true gaps",),
    ),
    ChartSpecification(
        chart_id="DQ06",
        research_question="How do quality findings distribute over domain and severity?",
        chart_type=ChartType.HEATMAP.value,
        x_label="finding domain",
        y_label="severity",
        unit="finding",
        owner_module="quality.findings",
        split="both",
        business_id="global",
        inputs=("quality_findings",),
        calculations="count findings by domain and severity",
        groups="split",
        output_relpath="figures/{run_id}/{split}/global/DQ06.png",
        caption="Quality findings by domain and severity.",
        interpretation="Shows which data-quality dimensions dominate.",
        limitations=("severity is evidence-based, not a business impact rating",),
    ),
    ChartSpecification(
        chart_id="NUM01",
        research_question="What is the shape of each numeric measure?",
        chart_type=ChartType.HISTOGRAM.value,
        x_label="measure value",
        y_label="row count",
        unit="business unit",
        owner_module="statistics.numeric",
        split="both",
        business_id="global",
        inputs=("numeric_stats",),
        calculations="empirical histogram with documented bin rule",
        groups="business",
        output_relpath="figures/{run_id}/{split}/{business_id}/NUM01.png",
        caption="Empirical distribution of a numeric measure.",
        interpretation="Reveals skew, zero mass and tail behaviour.",
        limitations=("bins are equal-width; outliers remain inside the last bin",),
    ),
    ChartSpecification(
        chart_id="NUM02",
        research_question="What is the quantile profile of the measure?",
        chart_type=ChartType.ECDF.value,
        x_label="measure value",
        y_label="cumulative fraction of rows",
        unit="fraction",
        owner_module="statistics.numeric",
        split="both",
        business_id="global",
        inputs=("numeric_stats",),
        calculations="empirical cumulative distribution",
        groups="business",
        output_relpath="figures/{run_id}/{split}/{business_id}/NUM02.png",
        caption="Empirical CDF of a numeric measure.",
        interpretation="Shows the median, tail mass and zero fraction.",
        limitations=("missing values are excluded from the population",),
    ),
    ChartSpecification(
        chart_id="NUM04",
        research_question="Which measures are heavily zero-inflated?",
        chart_type=ChartType.HORIZONTAL_BAR.value,
        x_label="metric",
        y_label="zero share of valid rows",
        unit="percent",
        owner_module="statistics.numeric",
        split="both",
        business_id="global",
        inputs=("numeric_stats",),
        calculations="n_zero divided by n_valid",
        groups="business",
        output_relpath="figures/{run_id}/{split}/{business_id}/NUM04.png",
        caption="Zero share of valid rows per measure.",
        interpretation="Separates structural zeros from continuous variation.",
        limitations=("a zero can be a legitimate business value",),
    ),
    ChartSpecification(
        chart_id="CAT01",
        research_question="Which categories dominate a categorical field?",
        chart_type=ChartType.HORIZONTAL_BAR.value,
        x_label="category",
        y_label="row count",
        unit="row",
        owner_module="statistics.categorical",
        split="both",
        business_id="global",
        inputs=("categorical_stats",),
        calculations="top-k categories with an explicit Others bucket",
        groups="business",
        output_relpath="figures/{run_id}/{split}/{business_id}/CAT01.png",
        caption="Category frequency including the Others bucket.",
        interpretation="Shows category concentration and long-tail structure.",
        limitations=("aliases are not merged without README evidence",),
    ),
    ChartSpecification(
        chart_id="TMP01",
        research_question="On which days does the source record activity?",
        chart_type=ChartType.HEATMAP.value,
        x_label="calendar day",
        y_label="business id",
        unit="row",
        owner_module="temporal.coverage",
        split="both",
        business_id="global",
        inputs=("temporal_profile",),
        calculations="event count per calendar day",
        groups="split",
        output_relpath="figures/{run_id}/{split}/global/TMP01.png",
        caption="Daily activity coverage across the calendar window.",
        interpretation="Reveals active periods and silent stretches.",
        limitations=("a day without events is not necessarily missing data",),
    ),
    ChartSpecification(
        chart_id="TMP03",
        research_question="Which months have no recorded events?",
        chart_type=ChartType.HEATMAP.value,
        x_label="month",
        y_label="business id",
        unit="month",
        owner_module="temporal.coverage",
        split="both",
        business_id="global",
        inputs=("temporal_profile",),
        calculations="observed month index versus the covered range",
        groups="split",
        output_relpath="figures/{run_id}/{split}/global/TMP03.png",
        caption="Presence or absence of records per month.",
        interpretation="Highlights coverage gaps within each business period.",
        limitations=("absence of events is distinct from absence of source data",),
    ),
    ChartSpecification(
        chart_id="QNA01",
        research_question="How long are the questions in each split?",
        chart_type=ChartType.BOXPLOT.value,
        x_label="split",
        y_label="question length",
        unit="characters",
        owner_module="questions.question_profile",
        split="both",
        business_id="global",
        inputs=("question_registry",),
        calculations="character length distribution per split",
        groups="split",
        output_relpath="figures/{run_id}/{split}/global/QNA01.png",
        caption="Question length distribution per split.",
        interpretation="Compares question complexity between splits.",
        limitations=("character count is tokenizer dependent",),
    ),
    ChartSpecification(
        chart_id="QNA03",
        research_question="Which time expressions dominate the questions?",
        chart_type=ChartType.HORIZONTAL_BAR.value,
        x_label="time expression",
        y_label="question count",
        unit="question",
        owner_module="questions.question_profile",
        split="both",
        business_id="global",
        inputs=("question_registry",),
        calculations="keyword-annotated time expression counts",
        groups="split",
        output_relpath="figures/{run_id}/{split}/global/QNA03.png",
        caption="Relative time expressions found in the question text.",
        interpretation="Indicates how much temporal reasoning is required.",
        limitations=("multi-label; the same question may carry several expressions",),
    ),
    ChartSpecification(
        chart_id="CBS01",
        research_question="How heterogeneous are the business schemas?",
        chart_type=ChartType.HEATMAP.value,
        x_label="semantic field role",
        y_label="business id",
        unit="presence",
        owner_module="cross_business.schema_compare",
        split="both",
        business_id="global",
        inputs=("schema_compare",),
        calculations="presence of each semantic field role per business",
        groups="split",
        output_relpath="figures/{run_id}/{split}/global/CBS01.png",
        caption="Semantic field-role presence per business.",
        interpretation="Shows structural heterogeneity across businesses.",
        limitations=("a shared role does not imply an equivalent join key",),
    ),
    ChartSpecification(
        chart_id="GLB01",
        research_question="Is every business covered by a report?",
        chart_type=ChartType.HORIZONTAL_BAR.value,
        x_label="business id",
        y_label="coverage status",
        unit="business",
        owner_module="cross_business.aggregate",
        split="both",
        business_id="global",
        inputs=("coverage_ledger",),
        calculations="coverage status per business",
        groups="split",
        output_relpath="figures/{run_id}/{split}/global/GLB01.png",
        caption="Per-business coverage status.",
        interpretation="Makes partial or blocked coverage explicit.",
        limitations=("coverage status is not a data-quality score",),
    ),
)


CHART_SPECS_BY_ID = {spec.chart_id: spec for spec in CHART_CATALOGUE}


@dataclass(frozen=True)
class ChartValidation:
    chart_id: str
    valid: bool
    status: Status
    reasons: tuple[str, ...]

    def to_dict(self) -> dict[str, Any]:
        return {
            "chart_id": self.chart_id,
            "valid": self.valid,
            "status": self.status.value,
            "reasons": list(self.reasons),
        }


def validate_chart_spec(spec: ChartSpecification) -> ChartValidation:
    reasons: list[str] = []
    if not spec.research_question:
        reasons.append("missing_research_question")
    if spec.chart_type not in {item.value for item in ChartType}:
        reasons.append("unknown_chart_type")
    if not spec.x_label or not spec.y_label:
        reasons.append("missing_axis_label")
    if not spec.unit:
        reasons.append("missing_unit")
    if not spec.owner_module:
        reasons.append("missing_owner_module")
    if not spec.output_relpath:
        reasons.append("missing_output_path")
    if not spec.caption:
        reasons.append("missing_caption")
    if not spec.limitations:
        reasons.append("missing_limitations")
    valid = not reasons
    return ChartValidation(
        chart_id=spec.chart_id,
        valid=valid,
        status=Status.PASS if valid else Status.BLOCKED,
        reasons=tuple(reasons),
    )


def validate_all_chart_specs(
    specs: Sequence[ChartSpecification] = CHART_CATALOGUE,
) -> tuple[ChartValidation, ...]:
    return tuple(validate_chart_spec(spec) for spec in specs)


def chart_registry_payload(
    specs: Sequence[ChartSpecification], validations: Sequence[ChartValidation]
) -> dict[str, Any]:
    validation_map = {item.chart_id: item for item in validations}
    return {
        "charts": [
            {
                **spec.to_dict(),
                "validation": validation_map[spec.chart_id].to_dict(),
            }
            for spec in specs
        ],
        "chart_count": len(specs),
        "valid_count": sum(1 for item in validations if item.valid),
    }


def chart_owner_map() -> Mapping[str, str]:
    return {spec.chart_id: spec.owner_module for spec in CHART_CATALOGUE}
