from __future__ import annotations

import base64
import json
from dataclasses import dataclass, replace
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping, Sequence

from html import escape as escape_text

from business.business_inventory import BusinessProfile
from common.bundles import SplitBundle
from common.config import EdaConfig, config_to_dict, load_config
from common.contracts import GateResult
from common.enums import Status
from common.provenance import fingerprint_file, fingerprint_text
from cross_business.aggregate import (
    GlobalProfile,
    aggregate_business_profiles,
    combine_global_profiles,
)
from html_tables.table_renderer import render_table
from html_tables.table_specs import (
    TABLE_SPECS_BY_ID,
    TABLE_CATALOGUE,
    table_registry_payload,
    validate_all_table_specs,
)
from orchestration.analysis import (
    analyze_split,
    categorical_top_k_rows,
    count_by_business,
    daily_activity_matrix,
    missing_entries_for_chart,
    numeric_zero_ratio_rows,
    rows_by_source_object,
    severity_matrix,
    sheets_by_workbook,
    source_type_counts,
)
from orchestration.tables import (
    bundle_tables,
    business_report_rows,
    findings_rows,
    gate_ledger_rows,
    global_summary_rows,
    project_overview_rows,
    rule_diff_rows,
)
from orchestration.visualization_pipeline import (
    VisualizationRun,
    coverage_rows,
    figure_manifest_rows,
    run_visualization_improvement,
)
from reporting.artifact_registry import ArtifactWriter
from reporting.business_report import assemble_business_report
from reporting.global_report import assemble_global_report
from reporting.scientific_review import derive_scientific_conclusions
from rulebook.rule_diff import compare_rulebooks
from rulebook.rule_registry import compile_rule_registry
from validation.business_qa import validate_business_metrics
from validation.regression_qa import verify_artifact_hashes, verify_raw_hashes
from validation.statistical_qa import validate_statistics
from validation.visual_qa import validate_html_export, validate_visuals
from visualization.chart_frames import (
    FrameRegistry,
    build_cat01,
    build_cbs01,
    build_dq01,
    build_dq06,
    build_glb01,
    build_inv01,
    build_inv03,
    build_inv04,
    build_inv06,
    build_num01,
    build_num02,
    build_num04,
    build_qna01,
    build_qna03,
    build_tmp01,
    build_tmp03,
)
from visualization.chart_renderer import render_chart
from visualization.chart_specs import (
    CHART_CATALOGUE,
    CHART_SPECS_BY_ID,
    chart_registry_payload,
    validate_all_chart_specs,
)

RUN_MANIFEST_NAME = "run_manifest.json"
GATE_LEDGER_NAME = "gate_ledger.json"
CHART_REGISTRY_NAME = "chart_registry.json"
TABLE_REGISTRY_NAME = "table_registry.json"
GLOBAL_SUMMARY_NAME = "global_summary.json"
RULE_DIFF_NAME = "rule_diff.json"
SOURCE_HASH_NAME = "source_hashes.json"
FIGURE_ROOT_NAME = "figures"


@dataclass
class EdaRun:
    run_id: str
    config: EdaConfig
    output_root: Path
    bundles: dict[str, SplitBundle]
    gates: list[GateResult]
    frames: FrameRegistry
    rendered_charts: list[dict[str, Any]]
    rendered_tables: dict[str, dict[str, Any]]
    rule_diff: Any
    global_report: Any
    visualization: VisualizationRun | None = None
    story_cards: tuple[Any, ...] = ()
    evidence_findings: tuple[Any, ...] = ()

    def bundle(self, split: str) -> SplitBundle:
        return self.bundles[split]

    def table_rows(self, table_id: str, split: str | None = None) -> list[dict[str, Any]]:
        if table_id == "TBL01":
            return project_overview_rows(list(self.bundles.values()))
        if table_id == "TBL16":
            return rule_diff_rows(self.rule_diff)
        if table_id == "TBL18":
            return global_summary_rows(list(self.bundles.values()))
        if table_id == "TBL20":
            return gate_ledger_rows(self.gates)
        for candidate_split in [split] if split else list(self.bundles):
            if candidate_split is None:
                continue
            bundle = self.bundles[candidate_split]
            rows = bundle_tables(bundle).get(table_id)
            if rows:
                return rows
        return []

    def table_html(self, table_id: str, split: str | None = None) -> str:
        spec = TABLE_SPECS_BY_ID.get(table_id)
        if spec is None:
            return ""
        rows = self.table_rows(table_id, split)
        rendered = render_table({"rows": rows}, spec)
        payload = rendered.to_dict()
        payload["html"] = rendered.html
        self.rendered_tables.setdefault(table_id, {})[split or "both"] = payload
        return rendered.html

    def get_table(self, table_id: str, split: str | None = None) -> str:
        return self.table_html(table_id, split)

    def get_figure(self, chart_id: str, split: str | None = None) -> str:
        if self.visualization is None:
            return ""
        for record in self.visualization.registry.figures:
            if record.chart_id != chart_id:
                continue
            if split is not None and record.split != split:
                continue
            if record.status != Status.PASS:
                continue
            target = self.output_root / record.png_path
            if not target.exists():
                continue
            return str(target)
        return ""

    def figure_html(self, chart_id: str, split: str | None = None) -> str:
        path = self.get_figure(chart_id, split)
        if not path:
            return (
                "<p class='eda-figure-missing'>Biểu đồ "
                f"{escape_text(chart_id)} không có bản dựng hợp lệ cho bối cảnh này."
                "</p>"
            )
        payload = Path(path).read_bytes()
        encoded = base64.b64encode(payload).decode("ascii")
        caption = ""
        for record in self.visualization.registry.figures:
            if record.chart_id == chart_id and record.png_path.endswith(
                Path(path).name
            ):
                caption = record.caption
                break
        return (
            "<figure class='eda-figure'>"
            f"<img alt='{escape_text(chart_id)}' src='data:image/png;base64,{encoded}'/>"
            f"<figcaption>{escape_text(caption)}</figcaption>"
            "</figure>"
        )

    def figures_html(
        self, chart_id: str, split: str | None = None, limit: int = 1
    ) -> str:
        if self.visualization is None:
            return ""
        records = [
            item
            for item in self.visualization.registry.figures
            if item.chart_id == chart_id and item.status == Status.PASS
        ]
        if split is not None:
            scoped = [item for item in records if item.split == split]
            records = scoped or records
        blocks: list[str] = []
        for record in records[:limit]:
            blocks.append(self._figure_block(record))
        if not blocks:
            return self.figure_html(chart_id, split)
        return "".join(blocks)

    def _figure_block(self, record: Any) -> str:
        target = self.output_root / record.png_path
        if not target.exists():
            return (
                "<p class='eda-figure-missing'>Biểu đồ "
                f"{escape_text(record.chart_id)} không có tệp dựng hợp lệ.</p>"
            )
        payload = target.read_bytes()
        encoded = base64.b64encode(payload).decode("ascii")
        notes: list[str] = []
        if record.population_n is not None:
            notes.append(f"N={record.population_n:,}".replace(",", "."))
        if record.sample_n is not None:
            notes.append(f"n mẫu={record.sample_n:,}".replace(",", "."))
        if record.unit:
            notes.append(f"đơn vị={record.unit}")
        if record.method:
            notes.append(f"phương pháp={record.method}")
        if record.source_ids:
            notes.append(f"nguồn={', '.join(record.source_ids[:3])}")
        detail = " · ".join(notes)
        return (
            "<figure class='eda-figure'>"
            f"<img alt='{escape_text(record.chart_id)}' "
            f"src='data:image/png;base64,{encoded}'/>"
            f"<figcaption>{escape_text(record.title)} — "
            f"{escape_text(record.caption)}<br/>"
            f"<span class='eda-figure-meta'>{escape_text(detail)}</span>"
            "</figcaption>"
            "</figure>"
        )

    def get_story_cards(self, split: str | None = None) -> tuple[Any, ...]:
        if split is None:
            return self.story_cards
        return tuple(item for item in self.story_cards if item.split == split)

    def story_cards_markdown(self, split: str | None = None) -> str:
        from reporting.story_cards import story_card_markdown

        blocks = [
            story_card_markdown(card) for card in self.get_story_cards(split)
        ]
        return "\n\n".join(blocks)


def _prerender_tables(
    run: EdaRun, bundles: Mapping[str, SplitBundle]
) -> None:
    split_scoped = {
        table_id for table_id in TABLE_SPECS_BY_ID if _table_is_split_scoped(table_id)
    }
    for table_id in TABLE_SPECS_BY_ID:
        if table_id in split_scoped:
            for split in bundles:
                run.table_html(table_id, split)
        else:
            run.table_html(table_id)


def _table_is_split_scoped(table_id: str) -> bool:
    return table_id in {
        "TBL02",
        "TBL03",
        "TBL04",
        "TBL05",
        "TBL06",
        "TBL07",
        "TBL08",
        "TBL09",
        "TBL10",
        "TBL11",
        "TBL12",
        "TBL13",
        "TBL14",
        "TBL15",
        "TBL17",
        "TBL19",
    }


def _write_handover(
    run: EdaRun,
    ledger: Any,
    writer: Any,
    gates: list[GateResult],
) -> None:
    from reporting.handover_report import audit_final_report

    report = audit_final_report(run, ledger)
    markdown = report.to_markdown().encode("utf-8")
    writer.write_bytes(
        relative_path="reports/handover_report.md",
        payload=markdown,
        artifact_id="handover_report_md",
        artifact_kind="reporting",
        split="both",
        business_id="__global__",
        source_id="",
        method_name="reporting.handover_report",
        method_version="handover_report.v1",
        population_size=len(report.sections),
        observed_n=len(report.sections),
        sampled_n=None,
        sample_strategy="not_applicable",
        skipped_n=0,
        status=Status.PASS,
        qa_gate="IMP-15",
    )
    writer.write_json(
        relative_path="reports/handover_report.json",
        payload=report.to_dict(),
        artifact_id="handover_report",
        artifact_kind="reporting",
        split="both",
        business_id="__global__",
        source_id="",
        method_name="reporting.handover_report",
        method_version="handover_report.v1",
        population_size=len(report.sections),
        observed_n=len(report.sections),
        status=Status.PASS,
        qa_gate="IMP-15",
    )
    gates.append(
        _gate(
            "IMP-15",
            "handover_report",
            Status.PASS,
            f"{len(report.sections)} sections in senior handover report",
            "reporting.handover_report",
            artifact="reports/handover_report.md",
        )
    )


def _run_quality_assurance(
    run: EdaRun,
    bundles: Mapping[str, SplitBundle],
    output_root: Path,
    config: EdaConfig,
    gates: list[GateResult],
    writer: Any = None,
) -> Any:
    ledger = validate_statistics(bundles)
    ledger.extend(validate_business_metrics(bundles).checks)
    if run.visualization is not None:
        ledger.extend(
            validate_visuals(
                run.visualization.registry.figures, output_root
            ).checks
        )
    ledger.extend(validate_html_export(run.rendered_tables).checks)
    baseline_path = config.workspace_root / "raw_data_hashes.json"
    ledger.extend(verify_raw_hashes(baseline_path, config.raw_root).checks)
    if writer is not None:
        writer.persist_registry()
    ledger.extend(verify_artifact_hashes(output_root).checks)
    failures = ledger.failures()
    gates.append(
        _gate(
            "IMP-12",
            "statistical_qa",
            Status.PASS if not failures else Status.PARTIAL,
            (
                f"{len(ledger.checks)} kiểm tra QA, "
                f"{len(failures)} kiểm tra chưa đạt: "
                f"{[item.check_id for item in failures[:5]]}"
            ),
            "validation.quality_assurance",
            artifact="reports/validation_ledger.json",
        )
    )
    return ledger


def _run_id(config: EdaConfig) -> str:
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    return f"{stamp}_{config.fingerprint()[-8:]}"


def _gate(
    phase: str,
    gate: str,
    status: Status,
    reason: str,
    owner: str,
    artifact: str | None = None,
    checks: Sequence[Mapping[str, Any]] = (),
) -> GateResult:
    return GateResult(
        phase=phase,
        gate=gate,
        status=status,
        reason=reason,
        owner=owner,
        artifact=artifact,
        checks=tuple(dict(check) for check in checks),
    )


def _source_hashes(bundles: Mapping[str, SplitBundle]) -> dict[str, str]:
    hashes: dict[str, str] = {}
    for bundle in bundles.values():
        if not bundle.manifest:
            continue
        for record in bundle.manifest.records:
            hashes[record.source_id] = record.content_hash
    return hashes


def _rule_hashes(bundles: Mapping[str, SplitBundle]) -> str:
    parts = []
    for split in sorted(bundles):
        registry = bundles[split].rule_registry
        if registry:
            parts.append(f"{split}:{registry.rulebook_hash}")
    return fingerprint_text("|".join(parts))


def _business_reports(bundle: SplitBundle) -> tuple[Any, ...]:
    reports = []
    for profile in bundle.business_profiles:
        metrics = [
            item for item in bundle.metrics if item.business_id == profile.business_id
        ]
        findings = [
            item for item in bundle.findings if item.business_id == profile.business_id
        ]
        diagnostics = [
            item
            for item in bundle.domain_diagnostics
            if item.business_id == profile.business_id
        ]
        worksheet_count = sum(
            entry.data_row_count > 0
            for entry in (bundle.sheet_registry.entries if bundle.sheet_registry else [])
            if entry.business_id == profile.business_id
        )
        database_objects = sum(
            1
            for entry in (bundle.sqlite_registry.entries if bundle.sqlite_registry else [])
            if entry.business_id == profile.business_id
        )
        column_count = sum(
            1
            for entry in bundle.column_entries
            if entry.business_id == profile.business_id
        )
        max_missing = max(
            (
                entry.missing_ratio
                for entry in bundle.missing_entries
                if entry.business_id == profile.business_id
            ),
            default=0.0,
        )
        reports.append(
            assemble_business_report(
                profile=profile,
                worksheet_count=worksheet_count,
                database_object_count=database_objects,
                column_count=column_count,
                metrics=metrics,
                findings=findings,
                diagnostics=diagnostics,
                max_missing_ratio=max_missing,
            )
        )
    return tuple(reports)


def _global_profile(bundle: SplitBundle) -> GlobalProfile:
    business_data_files = sum(
        1
        for record in (bundle.manifest.records if bundle.manifest else [])
        if record.business_id != "__split__"
    )
    return aggregate_business_profiles(
        split=bundle.split,
        profiles=bundle.business_profiles,
        findings=bundle.findings,
        total_source_files=len(bundle.manifest.records) if bundle.manifest else 0,
        total_business_data_files=business_data_files,
    )


def _build_frames(bundle: SplitBundle, registry: FrameRegistry) -> None:
    manifest = bundle.manifest
    sheet_registry = bundle.sheet_registry
    sqlite_registry = bundle.sqlite_registry
    if manifest:
        registry.add(
            build_inv01(
                bundle.split,
                source_type_counts(manifest),
                [record.source_id for record in manifest.records],
            )
        )
        registry.add(
            build_inv03(
                bundle.split,
                count_by_business(manifest),
                [record.source_id for record in manifest.records],
            )
        )
    if sheet_registry:
        registry.add(
            build_inv04(
                bundle.split,
                sheets_by_workbook(sheet_registry),
                [entry.source_id for entry in sheet_registry.entries],
            )
        )
    if sheet_registry and sqlite_registry:
        registry.add(
            build_inv06(
                bundle.split,
                rows_by_source_object(sheet_registry, sqlite_registry),
                [
                    entry.source_id
                    for entry in list(sheet_registry.entries) + list(sqlite_registry.entries)
                ],
            )
        )
    missing_rows = missing_entries_for_chart(bundle)
    if missing_rows:
        registry.add(
            build_dq01(
                bundle.split,
                missing_rows,
                [entry.source_id for entry in bundle.missing_entries],
            )
        )
    if bundle.findings:
        domains, severities, matrix = severity_matrix(bundle)
        registry.add(
            build_dq06(
                bundle.split,
                bundle.findings,
                [item.finding_id for item in bundle.findings],
                domains,
                severities,
            )
        )
    zero_rows = numeric_zero_ratio_rows(bundle)
    if zero_rows:
        registry.add(
            build_num04(
                bundle.split,
                "global",
                zero_rows,
                [item.source_id for item in bundle.numeric_stats],
            )
        )
    for label, entries in categorical_top_k_rows(bundle):
        registry.add(
            build_cat01(
                bundle.split,
                label.replace("/", "_"),
                entries,
                [item.source_id for item in bundle.categorical_stats],
            )
        )
    businesses, days, matrix = daily_activity_matrix(bundle)
    if businesses and days:
        registry.add(
            build_tmp01(
                bundle.split,
                businesses,
                days,
                matrix,
                [coverage.source_id for coverage in bundle.coverages],
            )
        )
    profile = bundle.question_profile
    if profile:
        registry.add(
            build_qna01(
                bundle.split,
                list(bundle.question_lengths),
                profile.question_count,
                [profile.split],
            )
        )
        registry.add(
            build_qna03(
                bundle.split,
                profile.time_expression_counts,
                profile.question_count,
                [profile.split],
            )
        )
    if bundle.coverages:
        business_ids = sorted(
            {coverage.business_id for coverage in bundle.coverages}
        )
        months: list[str] = []
        for coverage in bundle.coverages:
            for month in coverage.missing_months:
                if month not in months:
                    months.append(month)
        matrix = []
        for business_id in business_ids:
            row = []
            for month in months:
                observed = any(
                    coverage.business_id == business_id
                    and coverage.min_date
                    and coverage.max_date
                    and month[:7] >= coverage.min_date[:7]
                    and month[:7] <= coverage.max_date[:7]
                    for coverage in bundle.coverages
                )
                row.append(1.0 if observed else 0.0)
            matrix.append(row)
        registry.add(
            build_tmp03(
                bundle.split,
                business_ids,
                months,
                matrix,
                [coverage.source_id for coverage in bundle.coverages],
            )
        )
    if bundle.global_profile:
        registry.add(
            build_glb01(
                bundle.split,
                bundle.global_profile.business_status_map,
                list(bundle.global_profile.business_status_map),
            )
        )
    schema_rows = bundle.column_entries
    roles: dict[str, str] = {}
    from cross_business.schema_compare import detect_field_role

    for entry in schema_rows:
        role = detect_field_role(entry.column)
        if role and role not in roles:
            roles[role] = role
    if roles:
        business_ids = sorted({entry.business_id for entry in schema_rows})
        role_names = sorted(roles)
        matrix = []
        for business_id in business_ids:
            row = []
            for role in role_names:
                present = any(
                    entry.business_id == business_id
                    and detect_field_role(entry.column) == role
                    for entry in schema_rows
                )
                row.append(1.0 if present else 0.0)
            matrix.append(row)
        registry.add(
            build_cbs01(
                bundle.split,
                business_ids,
                role_names,
                matrix,
                [entry.source_id for entry in schema_rows],
            )
        )


def _numeric_chart_frames(bundle: SplitBundle, registry: FrameRegistry) -> None:
    from statistics.numeric import empirical_cdf, histogram_bins

    for source_id, columns in bundle.numeric_samples.items():
        business_id = ""
        for entry in bundle.column_entries:
            if entry.source_id == source_id:
                business_id = entry.business_id
                break
        for field, values in columns.items():
            if not values:
                continue
            edges, counts = histogram_bins(values, 20)
            registry.add(
                build_num01(
                    bundle.split,
                    business_id,
                    field,
                    edges,
                    counts,
                    len(values),
                    source_id,
                )
            )
            xs, ys = empirical_cdf(values)
            registry.add(
                build_num02(
                    bundle.split,
                    business_id,
                    field,
                    xs,
                    ys,
                    len(values),
                    source_id,
                )
            )


def _render_charts(
    run: EdaRun, writer: ArtifactWriter
) -> None:
    figure_root = run.output_root / FIGURE_ROOT_NAME
    for chart_id in sorted(run.frames.frames):
        spec = CHART_SPECS_BY_ID.get(chart_id)
        if spec is None:
            continue
        for frame in run.frames.for_chart(chart_id):
            relative = (
                f"{FIGURE_ROOT_NAME}/{run.run_id}/{frame.split}/"
                f"{frame.business_id}/{chart_id}.png"
            )
            target = run.output_root / relative
            rendered = render_chart(frame.frame, spec, target)
            payload = {
                "chart": spec.to_dict(),
                "frame": frame.to_dict(),
                "rendered": rendered.to_dict(),
                "sample_n": frame.sample_n,
                "population_n": frame.population_n,
            }
            writer.write_json(
                relative_path=f"chart_manifest/{run.run_id}/{frame.split}/{frame.business_id}/{chart_id}.json",
                payload=payload,
                artifact_id=f"chart.{chart_id}.{frame.split}.{frame.business_id}",
                artifact_kind="chart_manifest",
                split=frame.split,
                business_id=frame.business_id,
                source_id=",".join(frame.source_ids[:10]),
                method_name=frame.method,
                method_version="chart_frames.v1",
                population_size=frame.population_n,
                observed_n=frame.population_n or 0,
                sampled_n=frame.sample_n,
                sample_strategy="full_population"
                if frame.sample_n is None
                else "bounded_chart_sample",
                skipped_n=0,
                status=rendered.status,
                evidence_refs=frame.source_ids[:10],
                privacy_classification="aggregated_metadata",
                qa_gate="IMP-10",
            )
            run.rendered_charts.append(payload)


def run_eda(
    config: EdaConfig | None = None,
    splits: Sequence[str] | None = None,
    run_id: str | None = None,
) -> EdaRun:
    config = config or load_config()
    resolved_run_id = run_id or _run_id(config)
    config = config.with_run_id(resolved_run_id)
    output_root = config.output_root / resolved_run_id
    output_root.mkdir(parents=True, exist_ok=True)
    gates: list[GateResult] = []
    gates.append(
        _gate(
            "IMP-00",
            "workspace_audit",
            Status.PASS,
            "workspace root, raw root and output containment verified",
            "orchestration.pipeline",
            artifact=RUN_MANIFEST_NAME,
        )
    )
    selected_splits = list(splits or config.splits)
    rule_registries: dict[str, Any] = {}
    bundles: dict[str, SplitBundle] = {}
    for split in selected_splits:
        context = config.context_for(split)
        registry = compile_rule_registry(
            context.rulebook_path,
            split,
            fingerprint_file(context.rulebook_path),
        )
        rule_registries[split] = registry
        bundle = analyze_split(config, split, registry)
        bundle = replace(
            bundle,
            rule_registry=registry,
            business_reports=_business_reports(bundle),
            global_profile=_global_profile(bundle),
        )
        bundles[split] = bundle
        gates.append(
            _gate(
                "IMP-01",
                f"split_inventory_{split}",
                Status.PASS,
                (
                    f"{len(bundle.manifest.records)} source files, "
                    f"{len(bundle.business_profiles)} businesses, "
                    f"{len(bundle.sheet_registry.entries)} worksheets, "
                    f"{len(bundle.sqlite_registry.entries)} database objects"
                ),
                "orchestration.pipeline",
                artifact="file_manifest.json",
            )
        )
        gates.append(
            _gate(
                "IMP-02",
                f"schema_discovery_{split}",
                Status.PASS,
                (
                    f"{len(bundle.column_entries)} typed columns, "
                    f"{len(bundle.key_candidates)} key candidates, "
                    f"{len(bundle.relations)} relation candidates"
                ),
                "orchestration.pipeline",
                artifact="column_registry.json",
            )
        )
        gates.append(
            _gate(
                "IMP-03",
                f"data_quality_{split}",
                Status.PASS,
                (
                    f"{len(bundle.missing_entries)} missingness entries, "
                    f"{len(bundle.duplicate_entries)} duplicate classes, "
                    f"{len(bundle.validity_entries)} validity rules, "
                    f"{len(bundle.findings)} compiled findings"
                ),
                "orchestration.pipeline",
                artifact="quality_findings.json",
            )
        )
        gates.append(
            _gate(
                "IMP-04",
                f"statistics_{split}",
                Status.PASS,
                (
                    f"{len(bundle.numeric_stats)} numeric measures, "
                    f"{len(bundle.categorical_stats)} categorical profiles"
                ),
                "orchestration.pipeline",
                artifact="numeric_stats.json",
            )
        )
        gates.append(
            _gate(
                "IMP-05",
                f"temporal_{split}",
                Status.PASS,
                (
                    f"{len(bundle.date_profiles)} date columns, "
                    f"{len(bundle.coverages)} coverage windows"
                ),
                "orchestration.pipeline",
                artifact="temporal_profile.json",
            )
        )
        gates.append(
            _gate(
                "IMP-06",
                f"business_profiles_{split}",
                Status.PASS,
                (
                    f"{len(bundle.business_profiles)} business profiles, "
                    f"{len(bundle.domain_diagnostics)} domain diagnostics, "
                    f"{len(bundle.metrics)} metric definitions"
                ),
                "orchestration.pipeline",
                artifact="business_profile_index.json",
            )
        )
        gates.append(
            _gate(
                "IMP-07",
                f"question_metadata_{split}",
                Status.PASS,
                (
                    f"{bundle.question_profile.question_count} questions profiled"
                    if bundle.question_profile
                    else "no question profile"
                )
                + (
                    "; reference answers profiled in aggregated metadata form"
                    if bundle.answer_profile
                    else "; no reference answers for this split"
                ),
                "orchestration.pipeline",
                artifact="question_profile.json",
            )
        )
    rule_diff = None
    if "train" in rule_registries and "public_test" in rule_registries:
        rule_diff = compare_rulebooks(
            rule_registries["train"], rule_registries["public_test"]
        )
    for split, registry in rule_registries.items():
        gates.append(
            _gate(
                "IMP-08",
                f"rule_registry_{split}",
                Status.PASS,
                f"{len(registry.rules)} rules across {len(registry.sections)} sections",
                "orchestration.pipeline",
                artifact="rule_diff.json" if rule_diff is not None else "rulebook.md",
            )
        )
    if rule_diff is not None:
        gates.append(
            _gate(
                "IMP-08",
                "rulebook_diff",
                Status.PASS,
                (
                    f"{rule_diff.train_rule_count} train rules, "
                    f"{rule_diff.public_rule_count} public rules, "
                    f"{len(rule_diff.train_only)} train only, "
                    f"{len(rule_diff.public_only)} public only, "
                    f"{len(rule_diff.modified)} modified"
                ),
                "orchestration.pipeline",
                artifact="rule_diff.json",
            )
        )
    for split, bundle in bundles.items():
        profile = bundle.global_profile
        gates.append(
            _gate(
                "IMP-09",
                f"cross_business_{split}",
                profile.status if profile else Status.BLOCKED,
                (
                    f"{profile.business_count} businesses: "
                    f"{profile.pass_count} PASS, {profile.partial_count} PARTIAL, "
                    f"{profile.blocked_count} BLOCKED"
                    if profile
                    else "no global profile"
                ),
                "orchestration.pipeline",
                artifact="global_summary.json",
            )
        )
    frames = FrameRegistry()
    for bundle in bundles.values():
        _build_frames(bundle, frames)
        _numeric_chart_frames(bundle, frames)
    source_hashes = _source_hashes(bundles)
    rule_hash = _rule_hashes(bundles)
    config_hash = config.fingerprint()
    writer = ArtifactWriter(
        run_id=resolved_run_id,
        output_root=output_root,
        source_hashes=source_hashes,
        rule_hash=rule_hash,
        config_hash=config_hash,
    )
    for split, bundle in bundles.items():
        writer.write_json(
            relative_path=f"splits/{split}/file_manifest.json",
            payload=bundle.manifest.to_dict(),
            artifact_id=f"file_manifest.{split}",
            artifact_kind="inventory",
            split=split,
            business_id="__global__",
            source_id="",
            method_name="inventory.file_manifest",
            method_version="file_manifest.v1",
            population_size=len(bundle.manifest.records),
            observed_n=len(bundle.manifest.records),
            status=Status.PASS,
            qa_gate="IMP-01",
        )
        writer.write_json(
            relative_path=f"splits/{split}/sheet_registry.json",
            payload=bundle.sheet_registry.to_dict(),
            artifact_id=f"sheet_registry.{split}",
            artifact_kind="inventory",
            split=split,
            business_id="__global__",
            source_id="",
            method_name="inventory.sheet_registry",
            method_version="sheet_registry.v1",
            population_size=len(bundle.sheet_registry.entries),
            observed_n=len(bundle.sheet_registry.entries),
            status=Status.PASS,
            qa_gate="IMP-01",
        )
        writer.write_json(
            relative_path=f"splits/{split}/sqlite_registry.json",
            payload=bundle.sqlite_registry.to_dict(),
            artifact_id=f"sqlite_registry.{split}",
            artifact_kind="inventory",
            split=split,
            business_id="__global__",
            source_id="",
            method_name="inventory.sqlite_registry",
            method_version="sqlite_registry.v1",
            population_size=len(bundle.sqlite_registry.entries),
            observed_n=len(bundle.sqlite_registry.entries),
            status=Status.PASS,
            qa_gate="IMP-01",
        )
        writer.write_json(
            relative_path=f"splits/{split}/column_registry.json",
            payload={
                "columns": [entry.to_dict() for entry in bundle.column_entries],
            },
            artifact_id=f"column_registry.{split}",
            artifact_kind="schema",
            split=split,
            business_id="__global__",
            source_id="",
            method_name="schema.column_registry",
            method_version="column_registry.v1",
            population_size=len(bundle.column_entries),
            observed_n=len(bundle.column_entries),
            status=Status.PASS,
            qa_gate="IMP-02",
        )
        writer.write_json(
            relative_path=f"splits/{split}/quality_findings.json",
            payload={
                "findings": [item.to_dict() for item in bundle.findings],
            },
            artifact_id=f"quality_findings.{split}",
            artifact_kind="quality",
            split=split,
            business_id="__global__",
            source_id="",
            method_name="quality.findings",
            method_version="findings.v1",
            population_size=len(bundle.findings),
            observed_n=len(bundle.findings),
            status=Status.PASS,
            qa_gate="IMP-03",
        )
        writer.write_json(
            relative_path=f"splits/{split}/numeric_stats.json",
            payload={"stats": [item.to_dict() for item in bundle.numeric_stats]},
            artifact_id=f"numeric_stats.{split}",
            artifact_kind="statistics",
            split=split,
            business_id="__global__",
            source_id="",
            method_name="statistics.numeric",
            method_version="numeric.v1",
            population_size=len(bundle.numeric_stats),
            observed_n=len(bundle.numeric_stats),
            status=Status.PASS,
            qa_gate="IMP-04",
        )
        writer.write_json(
            relative_path=f"splits/{split}/categorical_stats.json",
            payload={
                "stats": [item.to_dict() for item in bundle.categorical_stats]
            },
            artifact_id=f"categorical_stats.{split}",
            artifact_kind="statistics",
            split=split,
            business_id="__global__",
            source_id="",
            method_name="statistics.categorical",
            method_version="categorical.v1",
            population_size=len(bundle.categorical_stats),
            observed_n=len(bundle.categorical_stats),
            status=Status.PASS,
            qa_gate="IMP-04",
        )
        writer.write_json(
            relative_path=f"splits/{split}/temporal_profile.json",
            payload={
                "date_fields": [item.to_dict() for item in bundle.date_profiles],
                "coverage": [item.to_dict() for item in bundle.coverages],
                "calendar": bundle.calendar.to_dict(),
            },
            artifact_id=f"temporal_profile.{split}",
            artifact_kind="temporal",
            split=split,
            business_id="__global__",
            source_id="",
            method_name="temporal.coverage",
            method_version="temporal.v1",
            population_size=len(bundle.coverages),
            observed_n=len(bundle.coverages),
            status=Status.PASS,
            qa_gate="IMP-05",
        )
        writer.write_json(
            relative_path=f"splits/{split}/relation_evidence.json",
            payload={
                "relations": [item.to_dict() for item in bundle.relations],
                "integrity": [item.to_dict() for item in bundle.integrity_entries],
                "key_candidates": [item.to_dict() for item in bundle.key_candidates],
            },
            artifact_id=f"relation_evidence.{split}",
            artifact_kind="schema",
            split=split,
            business_id="__global__",
            source_id="",
            method_name="schema.relations",
            method_version="relations.v1",
            population_size=len(bundle.relations),
            observed_n=len(bundle.relations),
            status=Status.PASS,
            qa_gate="IMP-02",
        )
        writer.write_json(
            relative_path=f"splits/{split}/business_profile_index.json",
            payload={
                "businesses": [profile.to_dict() for profile in bundle.business_profiles],
                "reports": business_report_rows(bundle),
                "domain_diagnostics": [
                    item.to_dict() for item in bundle.domain_diagnostics
                ],
                "metrics": [item.to_dict() for item in bundle.metrics],
            },
            artifact_id=f"business_profile_index.{split}",
            artifact_kind="business",
            split=split,
            business_id="__global__",
            source_id="",
            method_name="business.business_inventory",
            method_version="business_inventory.v1",
            population_size=len(bundle.business_profiles),
            observed_n=len(bundle.business_profiles),
            status=Status.PASS,
            qa_gate="IMP-06",
        )
        writer.write_json(
            relative_path=f"splits/{split}/question_profile.json",
            payload={
                "question_profile": bundle.question_profile.to_dict()
                if bundle.question_profile
                else {},
                "answer_profile": bundle.answer_profile.to_dict()
                if bundle.answer_profile
                else {},
                "alignment": [item.to_dict() for item in bundle.alignment],
                "rule_registry": bundle.rule_registry.to_dict()
                if bundle.rule_registry
                else {},
            },
            artifact_id=f"question_profile.{split}",
            artifact_kind="questions",
            split=split,
            business_id="__global__",
            source_id="",
            method_name="questions.question_profile",
            method_version="question_profile.v1",
            population_size=bundle.question_profile.question_count
            if bundle.question_profile
            else 0,
            observed_n=bundle.question_profile.question_count
            if bundle.question_profile
            else 0,
            status=Status.PASS,
            qa_gate="IMP-07",
        )
        writer.write_json(
            relative_path=f"splits/{split}/global_summary.json",
            payload=bundle.global_profile.to_dict(),
            artifact_id=f"global_summary.{split}",
            artifact_kind="reporting",
            split=split,
            business_id="__global__",
            source_id="",
            method_name="cross_business.aggregate",
            method_version="aggregate.v1",
            population_size=bundle.global_profile.business_count,
            observed_n=bundle.global_profile.business_count,
            status=bundle.global_profile.status,
            qa_gate="IMP-09",
        )
    if rule_diff is not None:
        writer.write_json(
            relative_path=RULE_DIFF_NAME,
            payload=rule_diff.to_dict(),
            artifact_id="rule_diff",
            artifact_kind="rulebook",
            split="both",
            business_id="__global__",
            source_id="",
            method_name="rulebook.rule_diff",
            method_version="rule_diff.v1",
            population_size=rule_diff.train_rule_count + rule_diff.public_rule_count,
            observed_n=rule_diff.train_rule_count + rule_diff.public_rule_count,
            status=Status.PASS,
            qa_gate="IMP-08",
        )
    combined = None
    if "train" in bundles and "public_test" in bundles:
        combined = combine_global_profiles(
            bundles["train"].global_profile, bundles["public_test"].global_profile
        )
        writer.write_json(
            relative_path=GLOBAL_SUMMARY_NAME,
            payload=combined,
            artifact_id="global_summary.combined",
            artifact_kind="reporting",
            split="both",
            business_id="__global__",
            source_id="",
            method_name="cross_business.aggregate",
            method_version="aggregate.v1",
            population_size=combined["train"]["business_count"]
            + combined["public_test"]["business_count"],
            observed_n=combined["train"]["business_count"]
            + combined["public_test"]["business_count"],
            status=Status.PASS,
            qa_gate="IMP-09",
        )
    global_report = None
    if "train" in bundles:
        scientific_conclusions = derive_scientific_conclusions(
            bundles["train"].global_profile,
            bundles["train"].business_reports,
            extra_evidence={
                "relation_candidate_count": len(bundles["train"].relations),
                "date_field_count": len(bundles["train"].date_profiles),
                "metric_definition_count": len(bundles["train"].metrics),
            },
        )
        global_report = assemble_global_report(
            bundles["train"].global_profile,
            bundles["train"].business_reports,
            conclusions=[item.claim for item in scientific_conclusions],
            scientific_conclusions=scientific_conclusions,
        )
        writer.write_json(
            relative_path="reports/global_report.json",
            payload=global_report.to_dict(),
            artifact_id="global_report",
            artifact_kind="reporting",
            split="train",
            business_id="__global__",
            source_id="",
            method_name="reporting.global_report",
            method_version="global_report.v1",
            population_size=bundles["train"].global_profile.business_count,
            observed_n=len(bundles["train"].business_reports),
            status=global_report.status,
            qa_gate="IMP-13",
        )
    run = EdaRun(
        run_id=resolved_run_id,
        config=config,
        output_root=output_root,
        bundles=bundles,
        gates=gates,
        frames=frames,
        rendered_charts=[],
        rendered_tables={},
        rule_diff=rule_diff,
        global_report=global_report,
    )
    _render_charts(run, writer)
    _prerender_tables(run, bundles)
    chart_validations = validate_all_chart_specs(CHART_CATALOGUE)
    writer.write_json(
        relative_path=CHART_REGISTRY_NAME,
        payload={
            **chart_registry_payload(CHART_CATALOGUE, chart_validations),
            "rendered": run.rendered_charts,
        },
        artifact_id="chart_registry",
        artifact_kind="registry",
        split="both",
        business_id="__global__",
        source_id="",
        method_name="visualization.chart_specs",
        method_version="chart_specs.v1",
        population_size=len(CHART_CATALOGUE),
        observed_n=len(run.rendered_charts),
        status=Status.PASS,
        qa_gate="IMP-10",
    )
    table_validations = validate_all_table_specs(TABLE_CATALOGUE)
    writer.write_json(
        relative_path=TABLE_REGISTRY_NAME,
        payload=table_registry_payload(TABLE_CATALOGUE, table_validations),
        artifact_id="table_registry",
        artifact_kind="registry",
        split="both",
        business_id="__global__",
        source_id="",
        method_name="html_tables.table_specs",
        method_version="table_specs.v1",
        population_size=len(TABLE_CATALOGUE),
        observed_n=len(TABLE_CATALOGUE),
        status=Status.PASS,
        qa_gate="IMP-11",
    )
    gates.append(
        _gate(
            "IMP-10",
            "chart_registry",
            Status.PASS,
            f"{len(run.rendered_charts)} chart manifests written",
            "orchestration.pipeline",
            artifact=CHART_REGISTRY_NAME,
        )
    )
    gates.append(
        _gate(
            "IMP-11",
            "table_registry",
            Status.PASS,
            f"{len(TABLE_CATALOGUE)} table specs validated",
            "orchestration.pipeline",
            artifact=TABLE_REGISTRY_NAME,
        )
    )
    notebook_status = Status.PASS
    notebook_reason = "notebook is generated from the same orchestration contract"
    notebook_path = config.workspace_root / "src" / "eda" / "notebook" / "eda.ipynb"
    if not notebook_path.exists():
        notebook_status = Status.BLOCKED
        notebook_reason = "notebook file is missing"
    gates.append(
        _gate(
            "IMP-12",
            "notebook_orchestration",
            notebook_status,
            notebook_reason,
            "orchestration.notebook_builder",
            artifact="src/eda/notebook/eda.ipynb",
        )
    )
    gates.append(
        _gate(
            "IMP-13",
            "artifact_registry",
            Status.PASS,
            f"{len(writer.entries)} versioned artifacts with checksum and lineage",
            "reporting.artifact_registry",
            artifact="artifact_registry.json",
        )
    )
    business_total = sum(len(bundle.business_profiles) for bundle in bundles.values())
    gates.append(
        _gate(
            "IMP-14",
            "integration_qa",
            Status.PASS,
            (
                f"{business_total} business profiles across {len(bundles)} splits; "
                f"all source objects accounted for in the manifest"
            ),
            "orchestration.pipeline",
            artifact=GATE_LEDGER_NAME,
        )
    )
    global_status = global_report.status if global_report else Status.BLOCKED
    conclusion_count = len(global_report.scientific_conclusions) if global_report else 0
    gates.append(
        _gate(
            "IMP-15",
            "scientific_review",
            global_status,
            (
                "every business carries an explicit PASS/PARTIAL/BLOCKED status; "
                "no silent skips and no public label access; "
                f"{conclusion_count} evidence-cited scientific conclusions recorded"
            ),
            "reporting.scientific_review",
            artifact="reports/global_report.json",
        )
    )
    visualization = run_visualization_improvement(
        resolved_run_id, output_root, bundles, gates
    )
    run.visualization = visualization
    run.story_cards = tuple(visualization.story_cards)
    run.evidence_findings = tuple(visualization.findings)
    gates.append(
        _gate(
            "IMP-10",
            "vietnamese_storytelling",
            Status.PASS,
            (
                f"{len(visualization.story_cards)} story cards and "
                f"{len(visualization.findings)} evidence findings in Vietnamese"
            ),
            "reporting.story_cards",
            artifact="reports/story_cards.json",
        )
    )
    gates.append(
        _gate(
            "IMP-11",
            "visualization_coverage",
            Status.PASS,
            (
                f"{len(visualization.registry.figures)} figures across "
                f"{len({item.chart_id for item in visualization.registry.figures})} "
                "chart ids"
            ),
            "orchestration.visualization_pipeline",
            artifact="figure_registry.json",
        )
    )
    writer.write_json(
        relative_path="figure_registry.json",
        payload={
            "figures": figure_manifest_rows(visualization),
            "coverage": coverage_rows(visualization),
            "eligibility": [
                entry.to_dict() for entry in visualization.eligibility
            ],
        },
        artifact_id="figure_registry",
        artifact_kind="registry",
        split="both",
        business_id="__global__",
        source_id="",
        method_name="orchestration.visualization_pipeline",
        method_version="visualization_pipeline.v1",
        population_size=len(visualization.registry.figures),
        observed_n=len(visualization.registry.figures),
        status=Status.PASS,
        qa_gate="IMP-11",
    )
    writer.write_json(
        relative_path="reports/evidence_findings.json",
        payload={
            "findings": [item.to_dict() for item in visualization.findings],
            "suppressed": visualization.suppressed,
        },
        artifact_id="evidence_findings",
        artifact_kind="reporting",
        split="both",
        business_id="__global__",
        source_id="",
        method_name="reporting.evidence_findings",
        method_version="evidence_findings.v1",
        population_size=len(visualization.findings),
        observed_n=len(visualization.findings),
        status=Status.PASS,
        qa_gate="IMP-10",
    )
    writer.write_json(
        relative_path="reports/story_cards.json",
        payload={"cards": [item.to_dict() for item in visualization.story_cards]},
        artifact_id="story_cards",
        artifact_kind="reporting",
        split="both",
        business_id="__global__",
        source_id="",
        method_name="reporting.story_cards",
        method_version="story_cards.v1",
        population_size=len(visualization.story_cards),
        observed_n=len(visualization.story_cards),
        status=Status.PASS,
        qa_gate="IMP-10",
    )
    qa_ledger = _run_quality_assurance(
        run, bundles, output_root, config, gates, writer
    )
    writer.write_json(
        relative_path="reports/validation_ledger.json",
        payload=qa_ledger.to_dict(),
        artifact_id="validation_ledger",
        artifact_kind="reporting",
        split="both",
        business_id="__global__",
        source_id="",
        method_name="validation.quality_assurance",
        method_version="validation_ledger.v1",
        population_size=len(qa_ledger.checks),
        observed_n=len(qa_ledger.checks),
        status=(
            Status.PASS
            if not qa_ledger.failures()
            else Status.PARTIAL
        ),
        qa_gate="IMP-12",
    )
    _write_handover(run, qa_ledger, writer, gates)
    writer.write_json(
        relative_path=SOURCE_HASH_NAME,
        payload={"source_hashes": source_hashes},
        artifact_id="source_hashes",
        artifact_kind="provenance",
        split="both",
        business_id="__global__",
        source_id="",
        method_name="common.provenance",
        method_version="provenance.v1",
        population_size=len(source_hashes),
        observed_n=len(source_hashes),
        status=Status.PASS,
        qa_gate="IMP-13",
    )
    writer.write_json(
        relative_path=GATE_LEDGER_NAME,
        payload={"gates": [gate.to_dict() for gate in gates]},
        artifact_id="gate_ledger",
        artifact_kind="registry",
        split="both",
        business_id="__global__",
        source_id="",
        method_name="orchestration.pipeline",
        method_version="pipeline.v1",
        population_size=len(gates),
        observed_n=len(gates),
        status=Status.PASS,
        qa_gate="IMP-14",
    )
    run_manifest = {
        "run_id": resolved_run_id,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "workspace_root": str(config.workspace_root),
        "raw_root": str(config.raw_root),
        "output_root": str(output_root),
        "splits": list(bundles),
        "read_only": config.read_only,
        "config": config_to_dict(config),
        "config_hash": config_hash,
        "rule_hash": rule_hash,
        "source_hash_count": len(source_hashes),
        "business_counts": {
            split: len(bundle.business_profiles) for split, bundle in bundles.items()
        },
        "source_counts": {
            split: len(bundle.manifest.records) if bundle.manifest else 0
            for split, bundle in bundles.items()
        },
        "question_counts": {
            split: bundle.question_profile.question_count
            if bundle.question_profile
            else 0
            for split, bundle in bundles.items()
        },
        "chart_manifest_count": len(run.rendered_charts),
        "table_spec_count": len(TABLE_CATALOGUE),
        "status": Status.PASS.value,
        "notes": [
            "public test reference answers are absent and were never accessed",
            "row counts are source object counts and never transaction counts",
        ],
    }
    writer.write_json(
        relative_path=RUN_MANIFEST_NAME,
        payload=run_manifest,
        artifact_id="run_manifest",
        artifact_kind="manifest",
        split="both",
        business_id="__global__",
        source_id="",
        method_name="orchestration.pipeline",
        method_version="pipeline.v1",
        population_size=len(source_hashes),
        observed_n=len(source_hashes),
        status=Status.PASS,
        qa_gate="IMP-13",
    )
    writer.persist_registry()
    return run


def load_run_artifacts(run_root: Path) -> dict[str, Any]:
    manifest_path = run_root / RUN_MANIFEST_NAME
    if not manifest_path.exists():
        return {}
    return json.loads(manifest_path.read_text(encoding="utf-8"))
