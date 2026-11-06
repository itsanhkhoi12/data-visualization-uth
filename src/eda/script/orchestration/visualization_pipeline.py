from __future__ import annotations

import hashlib
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Mapping, Sequence

from common.bundles import SplitBundle
from common.enums import Status
from common.visual_contracts import Finding, StoryCard
from reporting.evidence_findings import (
    EvidenceMetric,
    ProvenanceRef,
    create_evidence_findings,
)
from reporting.story_cards import StoryCardSet, build_story_card
from reporting.visualization_registry import (
    ChartEligibilityEntry,
    FigureRecord,
    VisualizationRegistry,
    build_eligibility_ledger,
)
from visualization.business_charts import build_business_charts
from visualization.categorical_charts import (
    build_cardinality_chart,
    build_categorical_charts,
    build_group_category_chart,
)
from visualization.chart_context import BundleContext
from visualization.chart_data import ChartData
from visualization.chart_spec_catalogue import CHART_CATALOGUE_V2, CHART_SPECS_V2_BY_ID
from visualization.global_charts import build_global_charts
from visualization.inventory_charts import build_inventory_charts
from visualization.numeric_charts import build_numeric_charts
from visualization.quality_charts import build_quality_charts
from visualization.relationship_charts import build_relationship_charts
from visualization.scientific_renderer import render_chart_data
from visualization.temporal_charts import build_temporal_charts

FIGURE_ROOT = "figures"
MAX_FIGURES_PER_CHART = 12


@dataclass
class VisualizationRun:
    run_id: str
    output_root: Path
    registry: VisualizationRegistry = field(default_factory=VisualizationRegistry)
    eligibility: list[ChartEligibilityEntry] = field(default_factory=list)
    findings: list[Finding] = field(default_factory=list)
    story_cards: list[StoryCard] = field(default_factory=list)
    provenance: dict[str, ProvenanceRef] = field(default_factory=dict)
    suppressed: list[dict[str, Any]] = field(default_factory=list)

    def figures(self, chart_id: str) -> tuple[FigureRecord, ...]:
        return self.registry.figures_for_chart(chart_id)

    def figure_path(self, chart_id: str, split: str) -> str:
        for record in self.registry.figures:
            if record.chart_id == chart_id and record.split == split:
                return record.png_path
        return ""

    def coverage(self) -> dict[str, Any]:
        grouped = self.registry.by_chart()
        return {
            chart_id: {
                "rendered": sum(
                    1 for item in records if item.status == Status.PASS
                ),
                "not_applicable": sum(
                    1 for item in records if item.status == Status.NOT_APPLICABLE
                ),
                "blocked": sum(
                    1 for item in records if item.status == Status.BLOCKED
                ),
            }
            for chart_id, records in sorted(grouped.items())
        }


def _chart_data_for_split(bundle: SplitBundle) -> list[ChartData]:
    context = BundleContext(split=bundle.split, bundle=bundle)
    charts: list[ChartData] = []
    charts.extend(build_inventory_charts(context))
    charts.extend(build_quality_charts(context))
    charts.extend(build_numeric_charts(context))
    charts.extend(build_categorical_charts(context))
    charts.extend(build_cardinality_chart(context))
    charts.extend(build_group_category_chart(context))
    charts.extend(build_relationship_charts(context))
    charts.extend(build_temporal_charts(context))
    charts.extend(build_business_charts(context))
    charts.extend(build_global_charts(context))
    return charts


def _question_chart_data(bundle: SplitBundle) -> list[ChartData]:
    from visualization.question_charts import build_answer_charts, build_question_charts

    context = BundleContext(split=bundle.split, bundle=bundle)
    charts: list[ChartData] = []
    charts.extend(build_question_charts(context))
    charts.extend(build_answer_charts(context))
    return charts


def _gate_status_chart(gates: Sequence[Any]) -> list[ChartData]:
    from visualization.quality_charts import GATE_STATUS_ORDER

    if not gates:
        return []
    by_phase: dict[str, dict[str, int]] = {}
    for item in gates:
        phase = str(item.phase)
        status = item.status.value
        bucket = by_phase.setdefault(phase, {})
        bucket[status] = bucket.get(status, 0) + 1
    phases = sorted(by_phase)
    series = [
        {
            "label": status,
            "values": [float(by_phase[phase].get(status, 0)) for phase in phases],
        }
        for status in GATE_STATUS_ORDER
        if any(status in counts for counts in by_phase.values())
    ]
    return [
        ChartData(
            chart_id="QUAL08",
            split="both",
            business_id="global",
            kind="stacked_bar",
            payload={"labels": phases, "series": series},
            source_ids=tuple(str(item.gate) for item in gates),
            population_n=len(gates),
            sample_n=len(phases),
            method="count_gates_by_status_and_phase",
            unit="gate",
            denominator_label="toàn bộ gate của ledger kiểm định",
            title="Trạng thái gate theo phase kiểm định",
            x_label="Phase kiểm định",
            y_label="Số gate",
            limitations=(
                "a gate status reflects evidence availability, not business performance",
            ),
            metadata={
                "caption": (
                    f"{len(gates)} gate phân bố trên {len(phases)} phase kiểm định; "
                    "trạng thái được giữ nguyên từ ledger kiểm định."
                ),
                "phases": phases,
            },
        )
    ]


def _cross_split_chart_data(
    bundles: Mapping[str, SplitBundle],
    gates: Sequence[Any] = (),
) -> list[ChartData]:
    charts: list[ChartData] = []
    charts.extend(_split_question_feature_chart(bundles))
    charts.extend(_chart_eligibility_matrix_chart(bundles))
    charts.extend(_gate_status_chart(gates))
    return charts


def _split_question_feature_chart(
    bundles: Mapping[str, SplitBundle],
) -> list[ChartData]:
    from visualization.question_charts import question_feature_rates

    rates_by_split: dict[str, dict[str, float]] = {}
    totals: dict[str, int] = {}
    for split, bundle in sorted(bundles.items()):
        rates = question_feature_rates(bundle)
        if not rates:
            continue
        rates_by_split[split] = rates
        totals[split] = len(bundle.question_metadata)
    if len(rates_by_split) < 2:
        return []
    features = sorted({name for rates in rates_by_split.values() for name in rates})
    labels = [features]
    series = [
        {
            "label": split,
            "values": [rates_by_split[split].get(feature, 0.0) for feature in features],
        }
        for split in sorted(rates_by_split)
    ]
    return [
        ChartData(
            chart_id="QNA07",
            split="both",
            business_id="global",
            kind="grouped_bar",
            payload={"labels": features, "series": series},
            source_ids=tuple(
                f"{split}:questions.jsonl" for split in sorted(rates_by_split)
            ),
            population_n=sum(totals.values()),
            sample_n=sum(totals.values()),
            method="normalised_feature_proportions_per_split",
            unit="percent",
            denominator_label="số câu hỏi của từng split",
            title="Đối chiếu đặc trưng câu hỏi giữa các split",
            x_label="Đặc trưng câu hỏi",
            y_label="Tỷ trọng câu hỏi (%)",
            limitations=(
                "the features are heuristic rules and are not human annotation",
                "each split is normalised by its own question count",
                "no reference answer is read from the public test split",
            ),
            metadata={
                "caption": (
                    "Tỷ trọng đặc trưng câu hỏi chuẩn hóa theo từng split: "
                    + "; ".join(
                        f"{split} n={totals[split]}" for split in sorted(totals)
                    )
                    + "."
                ),
                "features": features,
                "totals": totals,
            },
        )
    ]


def _chart_eligibility_matrix_chart(
    bundles: Mapping[str, SplitBundle],
) -> list[ChartData]:
    families = (
        "INV",
        "QUAL",
        "NUM",
        "CAT",
        "REL",
        "TIME",
        "BUS",
        "QNA",
        "GLOBAL",
    )
    requirements: dict[str, tuple[str, ...]] = {
        "INV": (),
        "QUAL": ("measure", "amount", "quantity", "categorical", "boolean", "date"),
        "NUM": ("measure", "amount", "quantity"),
        "CAT": ("categorical", "boolean"),
        "REL": ("measure", "amount", "quantity", "categorical", "boolean"),
        "TIME": ("date", "datetime"),
        "BUS": ("measure", "amount", "quantity"),
        "QNA": ("categorical", "boolean"),
        "GLOBAL": ("measure", "amount", "quantity", "categorical", "boolean"),
    }
    business_ids = sorted(
        {
            profile.business_id
            for bundle in bundles.values()
            for profile in bundle.business_profiles
        }
    )
    if not business_ids:
        return []
    semantic_by_business: dict[str, set[str]] = {}
    for bundle in bundles.values():
        for entry in bundle.column_entries:
            semantic_by_business.setdefault(entry.business_id, set()).add(
                entry.semantic_type
            )
    matrix: list[list[float]] = []
    for business_id in business_ids:
        available = semantic_by_business.get(business_id, set())
        row: list[float] = []
        for family in families:
            required = requirements.get(family, ())
            if not required:
                row.append(1.0)
                continue
            row.append(1.0 if available & set(required) else 0.0)
        matrix.append(row)
    population_n = len(business_ids) * len(families)
    return [
        ChartData(
            chart_id="GLOBAL05",
            split="both",
            business_id="global",
            kind="heatmap",
            payload={
                "matrix": matrix,
                "rows": business_ids,
                "columns": list(families),
            },
            source_ids=tuple(
                entry.source_id
                for bundle in bundles.values()
                for entry in bundle.column_entries
            ),
            population_n=population_n,
            sample_n=len(business_ids),
            method="eligibility_state_matrix",
            unit="state",
            denominator_label="cặp doanh nghiệp và nhóm biểu đồ",
            title="Ma trận độ đủ điều kiện của biểu đồ theo doanh nghiệp",
            x_label="Nhóm biểu đồ",
            y_label="Mã doanh nghiệp",
            limitations=(
                "eligibility reflects schema availability, not chart rendering success",
                "a shared field type does not imply an equivalent business definition",
                "the INV and GLOBAL families only require the presence of a source object",
            ),
            metadata={
                "caption": (
                    f"Ma trận trạng thái đủ điều kiện của {len(business_ids)} doanh nghiệp "
                    f"theo {len(families)} nhóm biểu đồ; ô trắng nghĩa là doanh nghiệp "
                    "không có cột phù hợp theo loại ngữ nghĩa."
                ),
                "families": list(families),
            },
        )
    ]


def _relative_figure_path(
    run_id: str, split: str, business_id: str, chart_id: str
) -> str:
    return f"{FIGURE_ROOT}/{run_id}/{split}/{business_id}/{chart_id}.png"


def _relative_svg_path(
    run_id: str, split: str, business_id: str, chart_id: str
) -> str:
    return f"{FIGURE_ROOT}/{run_id}/{split}/{business_id}/{chart_id}.svg"


def _render_chart_data(
    run: VisualizationRun,
    bundle: SplitBundle,
    data: ChartData,
) -> FigureRecord:
    run.registry.add_chart_data(data)
    relative = _relative_figure_path(run.run_id, data.split, data.business_id, data.chart_id)
    svg_relative = _relative_svg_path(
        run.run_id, data.split, data.business_id, data.chart_id
    )
    png_target = run.output_root / relative
    svg_target = run.output_root / svg_relative
    try:
        rendered = render_chart_data(data, png_target, svg_path=svg_target)
    except Exception as error:
        rendered = None
        reason = f"render_failed:{type(error).__name__}"
        record = FigureRecord(
            figure_id=f"{data.chart_id}.{data.split}.{data.business_id}",
            chart_id=data.chart_id,
            split=data.split,
            business_id=data.business_id,
            png_path=relative,
            svg_path=svg_relative,
            content_hash="",
            status=Status.BLOCKED,
            reason=reason,
            population_n=data.population_n,
            sample_n=data.sample_n,
            method=data.method,
            unit=data.unit,
            title=data.title,
            caption=str(data.metadata.get("caption", "")),
            source_ids=data.source_ids,
            byte_size=0,
            limitations=data.limitations,
        )
        run.registry.add_figure(record)
        return record
    svg_hash = ""
    svg_size = 0
    if svg_target.exists():
        svg_payload = svg_target.read_bytes()
        svg_hash = f"sha256:{hashlib.sha256(svg_payload).hexdigest()}"
        svg_size = len(svg_payload)
    record = FigureRecord(
        figure_id=rendered.figure_id,
        chart_id=data.chart_id,
        split=data.split,
        business_id=data.business_id,
        png_path=relative,
        svg_path=svg_relative if svg_hash else "",
        content_hash=rendered.content_hash,
        status=rendered.status,
        reason=rendered.reason,
        population_n=data.population_n,
        sample_n=data.sample_n,
        method=data.method,
        unit=data.unit,
        title=data.title,
        caption=str(data.metadata.get("caption", "")),
        source_ids=data.source_ids,
        byte_size=rendered.byte_size + svg_size,
        limitations=data.limitations,
    )
    run.registry.add_figure(record)
    return record


def _build_provenance(
    run: VisualizationRun,
    bundle: SplitBundle,
    record: FigureRecord,
) -> ProvenanceRef:
    source_hashes: list[str] = []
    if bundle.manifest:
        by_id = {item.source_id: item.content_hash for item in bundle.manifest.records}
        for source_id in record.source_ids:
            if source_id in by_id:
                source_hashes.append(by_id[source_id])
    artifact_id = f"figure.{record.chart_id}.{record.split}.{record.business_id}"
    return ProvenanceRef(
        artifact_id=artifact_id,
        artifact_path=record.png_path,
        source_ids=record.source_ids,
        source_hashes=tuple(source_hashes),
        method=record.method,
        method_version="scientific_renderer.v1",
        population_n=record.population_n,
        run_id=run.run_id,
        split=record.split,
        business_id=record.business_id,
    )


def _chart_questions() -> dict[str, str]:
    return {spec.chart_id: spec.research_question for spec in CHART_CATALOGUE_V2}


def _numeric_metrics_for_findings(
    bundle: SplitBundle,
) -> list[EvidenceMetric]:
    from reporting.evidence_findings import metric_from_numeric_profile
    from statistics.robust_stats import compute_robust_dispersion, iqr_outlier_masks

    metrics: list[EvidenceMetric] = []
    for entry in bundle.numeric_stats:
        values = bundle.numeric_samples.get(entry.source_id, {}).get(entry.field, [])
        if not values:
            continue
        dispersion = compute_robust_dispersion(values, total_n=entry.n_total)
        _lower, _upper, flags, _degenerate = iqr_outlier_masks(values)
        unit = entry.unit or "source unit"
        metrics.append(
            metric_from_numeric_profile(
                metric_id=f"numeric.{entry.source_id}.{entry.field}",
                field_label=f"{entry.business_id}/{entry.field}",
                dispersion=dispersion,
                unit=unit,
                outlier_n=sum(1 for flag in flags if flag),
                method=entry.method or "statistics.numeric",
                chart_id="NUM01",
                limitations=(
                    "giá trị ngoại lệ được gắn cờ và giữ lại, không tự động loại bỏ",
                ),
            )
        )
    return metrics


def _business_metrics_for_findings(bundle: SplitBundle) -> list[EvidenceMetric]:
    from reporting.evidence_findings import metric_from_business_payload

    metrics: list[EvidenceMetric] = []
    for metric in bundle.business_metrics:
        if metric.status != Status.PASS:
            continue
        payload = metric.payload
        value: Any = None
        if metric.metric_id in {"BUS01", "BUS05", "BUS07", "BUS09", "BUS10"}:
            values = payload.get("amounts") or payload.get("quantities") or payload.get(
                "balances"
            ) or payload.get("ages") or payload.get("totals") or []
            if not values:
                continue
            ordered = sorted(float(item) for item in values)
            value = ordered[len(ordered) // 2]
        elif metric.metric_id in {"BUS03", "BUS06", "BUS08", "BUS11"}:
            totals = payload.get("totals", {})
            if not totals:
                continue
            value = float(max(totals.values()))
        elif metric.metric_id in {"BUS04", "BUS13", "BUS14", "BUS15"}:
            counts = payload.get("counts", {})
            if not counts:
                continue
            value = float(max(counts.values()))
        elif metric.metric_id == "BUS02":
            daily = payload.get("daily", {})
            if not daily:
                continue
            value = float(sum(daily.values()))
        elif metric.metric_id == "BUS12":
            totals = payload.get("totals", {})
            if not totals:
                continue
            value = float(sum(totals.values()))
        if value is None:
            continue
        metrics.append(
            metric_from_business_payload(
                metric_id=f"business.{metric.source_id}.{metric.metric_id}",
                label=f"{metric.metric_id} — {metric.object_name}",
                business_id=metric.business_id,
                value=value,
                unit=metric.unit,
                population_n=metric.population_n,
                grain=metric.grain,
                method=metric.method,
                chart_id=metric.metric_id,
                limitations=tuple(metric.payload.get("limitations", ()))
                or (
                    "chỉ số được tính trên grain đã xác định và không vượt qua ranh giới "
                    "bảng",
                ),
            )
        )
    return metrics


def _global_metrics_for_findings(bundle: SplitBundle) -> list[EvidenceMetric]:
    from reporting.evidence_findings import metric_from_global_coverage

    profile = bundle.global_profile
    if profile is None:
        return []
    return [
        metric_from_global_coverage(
            metric_id=f"global.{bundle.split}.coverage",
            split=bundle.split,
            business_count=profile.business_count,
            pass_count=profile.pass_count,
            partial_count=profile.partial_count,
            blocked_count=profile.blocked_count,
            source_file_count=len(bundle.manifest.records) if bundle.manifest else 0,
            chart_id="GLOBAL07",
            limitations=(
                "số tệp và số đối tượng bảng không phải số giao dịch",
            ),
        )
    ]


def _question_metrics_for_findings(bundle: SplitBundle) -> list[EvidenceMetric]:
    from reporting.evidence_findings import metric_from_question_profile

    profile = bundle.question_profile
    if profile is None:
        return []
    return [
        metric_from_question_profile(
            metric_id=f"questions.{bundle.split}.profile",
            split=bundle.split,
            question_count=profile.question_count,
            median_length=profile.length_characters_median,
            intent_count=len(profile.intent_candidates),
            time_expression_count=len(profile.time_expression_counts),
            chart_id="QNA01",
            limitations=(
                "chỉ là siêu dữ liệu câu hỏi; không suy ra đáp án của câu hỏi",
            ),
        )
    ]


def _build_findings(
    run: VisualizationRun,
    bundles: Mapping[str, SplitBundle],
) -> None:
    provenance: dict[str, ProvenanceRef] = {}
    for split, bundle in bundles.items():
        for record in run.registry.figures:
            if record.split != split:
                continue
            reference = _build_provenance(run, bundle, record)
            provenance[record.chart_id] = reference
            run.provenance[record.chart_id] = reference
    metrics: list[EvidenceMetric] = []
    for split, bundle in bundles.items():
        metrics.extend(_numeric_metrics_for_findings(bundle))
        metrics.extend(_business_metrics_for_findings(bundle))
        metrics.extend(_global_metrics_for_findings(bundle))
        metrics.extend(_question_metrics_for_findings(bundle))
    metric_provenance: dict[str, ProvenanceRef] = {}
    for metric in metrics:
        reference = _metric_provenance(run, metric)
        if reference is not None:
            metric_provenance[metric.metric_id] = reference
    finding_set = create_evidence_findings(metrics, metric_provenance)
    run.findings.extend(finding_set.findings)
    run.suppressed.extend(finding_set.suppressed)


def _metric_provenance(
    run: VisualizationRun, metric: EvidenceMetric
) -> ProvenanceRef | None:
    chart_id = str(metric.extra.get("chart_id", ""))
    reference = run.provenance.get(chart_id)
    if reference is None:
        return None
    return ProvenanceRef(
        artifact_id=f"finding.{chart_id}.{reference.business_id}",
        artifact_path=reference.artifact_path,
        source_ids=reference.source_ids,
        source_hashes=reference.source_hashes,
        method=reference.method,
        method_version=reference.method_version,
        population_n=metric.population_n,
        run_id=reference.run_id,
        split=reference.split,
        business_id=reference.business_id,
    )


def _build_story_cards(run: VisualizationRun) -> None:
    questions = _chart_questions()
    findings_by_chart: dict[str, list[Finding]] = {}
    for finding in run.findings:
        findings_by_chart.setdefault(finding.chart_id, []).append(finding)
    rendered_charts = {
        record.chart_id for record in run.registry.figures if record.status == Status.PASS
    }
    for chart_id in sorted(rendered_charts):
        spec = CHART_SPECS_V2_BY_ID.get(chart_id)
        if spec is None:
            continue
        records = run.registry.figures_for_chart(chart_id)
        if not records:
            continue
        primary = records[0]
        card_findings = tuple(findings_by_chart.get(chart_id, ()))
        reference = run.provenance.get(chart_id)
        card = build_story_card(
            chart_id=chart_id,
            split=primary.split,
            business_id=primary.business_id,
            research_question=spec.research_question,
            context={
                "source_ids": primary.source_ids,
                "grain": spec.grouping,
                "population_n": primary.population_n,
                "valid_n": primary.population_n,
                "unit": primary.unit,
            },
            methodology={
                "method": spec.statistical_method,
                "filter": spec.calculation_or_formula,
                "missing_handling": spec.missing_handling,
                "outlier_handling": spec.outlier_handling,
            },
            statistic_lines=(
                f"phương pháp = {spec.statistical_method}",
                f"công thức = {spec.calculation_or_formula}",
                f"lấy mẫu = {spec.sampling_strategy}",
            ),
            figure_reference=primary.png_path,
            findings=card_findings,
            implications=spec.reason_for_inclusion,
            limitations=spec.scientific_limitations,
            conclusion=spec.expected_interpretation,
            evidence_refs=(reference.artifact_id,) if reference else (),
        )
        run.story_cards.append(card)


def run_visualization_improvement(
    run_id: str,
    output_root: Path,
    bundles: Mapping[str, SplitBundle],
    gates: Sequence[Any] = (),
) -> VisualizationRun:
    run = VisualizationRun(
        run_id=run_id,
        output_root=output_root,
        registry=VisualizationRegistry(run_id=run_id),
    )
    for split, bundle in bundles.items():
        for data in _chart_data_for_split(bundle):
            _render_chart_data(run, bundle, data)
        for data in _question_chart_data(bundle):
            _render_chart_data(run, bundle, data)
    if bundles:
        anchor_split = "train" if "train" in bundles else sorted(bundles)[0]
        for data in _cross_split_chart_data(bundles, gates):
            _render_chart_data(run, bundles[anchor_split], data)
    run.eligibility = build_eligibility_ledger(run.registry.chart_data)
    _build_findings(run, bundles)
    _build_story_cards(run)
    return run


def coverage_rows(run: VisualizationRun) -> list[dict[str, Any]]:
    grouped = run.registry.by_chart()
    rows: list[dict[str, Any]] = []
    for chart_id in sorted(grouped):
        records = grouped[chart_id]
        spec = CHART_SPECS_V2_BY_ID.get(chart_id)
        rows.append(
            {
                "chart_id": chart_id,
                "notebook_section": spec.notebook_section if spec else "",
                "module_owner": spec.module_owner if spec else "",
                "figure_count": len(records),
                "rendered_count": sum(
                    1 for item in records if item.status == Status.PASS
                ),
                "not_applicable_count": sum(
                    1 for item in records if item.status == Status.NOT_APPLICABLE
                ),
                "blocked_count": sum(
                    1 for item in records if item.status == Status.BLOCKED
                ),
                "business_count": len({item.business_id for item in records}),
            }
        )
    return rows


def figure_manifest_rows(run: VisualizationRun) -> list[dict[str, Any]]:
    return [record.to_dict() for record in run.registry.figures]
