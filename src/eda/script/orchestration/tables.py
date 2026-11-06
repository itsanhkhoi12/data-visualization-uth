from __future__ import annotations

from typing import Any, Mapping, Sequence

from common.bundles import SplitBundle
from common.contracts import GateResult


def project_overview_rows(bundles: Sequence[SplitBundle]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for bundle in bundles:
        rows.append(
            {
                "split": bundle.split,
                "status": bundle.global_profile.status.value
                if bundle.global_profile
                else "BLOCKED",
                "source_count": len(bundle.manifest.records) if bundle.manifest else 0,
                "business_count": len(bundle.business_profiles),
                "worksheet_count": len(bundle.sheet_registry.entries)
                if bundle.sheet_registry
                else 0,
                "database_object_count": len(bundle.sqlite_registry.entries)
                if bundle.sqlite_registry
                else 0,
            }
        )
    return rows


def source_inventory_rows(bundle: SplitBundle) -> list[dict[str, Any]]:
    if not bundle.manifest:
        return []
    return [
        {
            "source_id": record.source_id,
            "split": record.split,
            "business_id": record.business_id,
            "source_type": record.source_type,
            "logical_path": record.logical_path,
            "size_bytes": record.size_bytes,
            "content_hash": record.content_hash,
            "status": record.status.value,
        }
        for record in bundle.manifest.records
    ]


def sheet_registry_rows(bundle: SplitBundle) -> list[dict[str, Any]]:
    if not bundle.sheet_registry:
        return []
    return [
        {
            "workbook_path": entry.workbook_path,
            "sheet_name": entry.sheet_name,
            "sheet_state": entry.sheet_state,
            "data_row_count": entry.data_row_count,
            "max_column": entry.max_column,
            "header_confidence": entry.header_confidence,
            "has_repeated_header": entry.has_repeated_header,
            "formula_cell_count": entry.formula_cell_count,
        }
        for entry in bundle.sheet_registry.entries
    ]


def sqlite_registry_rows(bundle: SplitBundle) -> list[dict[str, Any]]:
    if not bundle.sqlite_registry:
        return []
    return [
        {
            "database_path": entry.database_path,
            "object_type": entry.object_type,
            "object_name": entry.object_name,
            "primary_key": ", ".join(entry.primary_key) or "none",
            "row_count": entry.row_count if entry.row_count is not None else "unknown",
            "column_count": entry.column_count,
            "foreign_key_count": entry.foreign_key_count,
        }
        for entry in bundle.sqlite_registry.entries
    ]


def column_registry_rows(bundle: SplitBundle) -> list[dict[str, Any]]:
    return [
        {
            "source_id": entry.source_id,
            "business_id": entry.business_id,
            "column": entry.column,
            "physical_type": entry.physical_type,
            "semantic_type": entry.semantic_type,
            "unit": entry.unit or "none",
            "non_null_n": entry.non_null_n,
            "null_n": entry.null_n,
            "distinct_n": entry.distinct_n,
            "parse_failure_n": entry.parse_failure_n,
            "confidence": entry.confidence,
        }
        for entry in bundle.column_entries
    ]


def missing_rows(bundle: SplitBundle) -> list[dict[str, Any]]:
    return [
        {
            "source_id": entry.source_id,
            "business_id": entry.business_id,
            "column": entry.column,
            "n_missing": entry.n_missing,
            "n_total": entry.n_total,
            "missing_ratio": entry.missing_ratio,
            "null_kind": entry.null_kind,
            "co_missing_with": ", ".join(entry.co_missing_with) or "none",
        }
        for entry in bundle.missing_entries
    ]


def duplicate_rows(bundle: SplitBundle) -> list[dict[str, Any]]:
    return [
        {
            "source_id": entry.source_id,
            "business_id": entry.business_id,
            "duplicate_class": entry.duplicate_class,
            "key_columns": ", ".join(entry.key_columns) or "all columns",
            "n_duplicate_rows": entry.n_duplicate_rows,
            "n_distinct_keys": entry.n_distinct_keys,
            "total_n": entry.total_n,
            "explanation": entry.explanation,
        }
        for entry in bundle.duplicate_entries
    ]


def validity_rows(bundle: SplitBundle) -> list[dict[str, Any]]:
    return [
        {
            "source_id": entry.source_id,
            "business_id": entry.business_id,
            "column": entry.column,
            "rule_id": entry.rule_id,
            "invalid_count": entry.invalid_count,
            "denominator": entry.denominator,
            "invalid_ratio": entry.invalid_ratio,
            "severity": entry.severity,
            "evidence": entry.evidence,
            "sample_masked": "; ".join(entry.sample_masked) or "none",
        }
        for entry in bundle.validity_entries
    ]


def numeric_rows(bundle: SplitBundle) -> list[dict[str, Any]]:
    return [
        {
            "source_id": item.source_id,
            "business_id": item.business_id,
            "field": item.field,
            "n_total": item.n_total,
            "n_valid": item.n_valid,
            "n_missing": item.n_missing,
            "n_zero": item.n_zero,
            "mean": item.mean,
            "median": item.median,
            "std": item.std,
            "q25": item.q25,
            "q75": item.q75,
            "min": item.minimum,
            "max": item.maximum,
            "unit": item.unit or "none",
            "status": item.status.value,
        }
        for item in bundle.numeric_stats
    ]


def categorical_rows(bundle: SplitBundle) -> list[dict[str, Any]]:
    return [
        {
            "source_id": item.source_id,
            "business_id": item.business_id,
            "field": item.field,
            "category": item.category,
            "count": item.count,
            "share": item.share,
            "is_null": item.is_null,
            "rank": item.rank,
        }
        for item in bundle.categorical_stats
    ]


def temporal_rows(bundle: SplitBundle) -> list[dict[str, Any]]:
    coverage_by_key = {
        (item.source_id, item.column): item for item in bundle.coverages
    }
    rows: list[dict[str, Any]] = []
    for profile in bundle.date_profiles:
        coverage = coverage_by_key.get((profile.source_id, profile.column))
        rows.append(
            {
                "source_id": profile.source_id,
                "business_id": profile.business_id,
                "column": profile.column,
                "event_role": profile.event_role,
                "valid_n": profile.valid_n,
                "parse_failure_n": profile.parse_failure_n,
                "min_date": profile.min_date or "none",
                "max_date": profile.max_date or "none",
                "distinct_dates": profile.distinct_dates,
                "active_days": coverage.active_days if coverage else 0,
                "span_days": coverage.span_days if coverage else 0,
                "coverage_ratio": coverage.coverage_ratio if coverage else 0.0,
                "missing_months": ", ".join(coverage.missing_months)
                if coverage and coverage.missing_months
                else "none",
                "status": profile.status,
            }
        )
    return rows


def relation_rows(bundle: SplitBundle) -> list[dict[str, Any]]:
    return [
        {
            "relation_id": item.relation_id,
            "left_source": item.left_source,
            "right_source": item.right_source,
            "join_keys": ", ".join(item.join_keys),
            "left_grain": item.left_grain,
            "right_grain": item.right_grain,
            "matched_rows": item.matched_rows,
            "unmatched_left_rows": item.unmatched_left_rows,
            "unmatched_right_rows": item.unmatched_right_rows,
            "duplicate_key_left": item.duplicate_key_left,
            "duplicate_key_right": item.duplicate_key_right,
            "fanout_factor": item.fanout_factor,
            "status": item.status,
            "risk": item.risk or "none",
        }
        for item in bundle.relations
    ]


def business_profile_rows(bundle: SplitBundle) -> list[dict[str, Any]]:
    findings_by_business: dict[str, int] = {}
    for finding in bundle.findings:
        findings_by_business[finding.business_id] = (
            findings_by_business.get(finding.business_id, 0) + 1
        )
    rows: list[dict[str, Any]] = []
    for profile in bundle.business_profiles:
        rows.append(
            {
                "business_id": profile.business_id,
                "split": profile.split,
                "source_count": profile.source_count,
                "readme_present": profile.readme_present,
                "readme_hash": profile.readme_hash or "none",
                "domain_evidence": profile.domain_evidence or "unresolved",
                "findings": findings_by_business.get(profile.business_id, 0),
                "status": profile.status.value,
            }
        )
    return rows


def kpi_rows(bundle: SplitBundle) -> list[dict[str, Any]]:
    return [
        {
            "metric_id": item.metric_id,
            "business_id": item.business_id,
            "name": item.name,
            "grain": item.grain,
            "rule_id": item.rule_id or "unlinked",
            "unit": item.unit,
            "formula_status": item.formula_status.value,
            "status_handling": item.status_handling,
            "null_behavior": item.null_behavior,
        }
        for item in bundle.metrics
    ]


def question_rows(bundle: SplitBundle) -> list[dict[str, Any]]:
    profile = bundle.question_profile
    if not profile:
        return []
    answer = bundle.answer_profile
    return [
        {
            "split": profile.split,
            "question_count": profile.question_count,
            "unique_id_count": profile.unique_id_count,
            "duplicate_id_count": profile.duplicate_id_count,
            "as_of_min": profile.as_of_min or "none",
            "as_of_max": profile.as_of_max or "none",
            "as_of_missing_count": profile.as_of_missing_count,
            "label_access": "train_reference_available"
            if answer is not None
            else "no_labels_for_split",
            "status": profile.status,
        }
    ]


def rule_diff_rows(report: Any) -> list[dict[str, Any]]:
    if not report:
        return []
    rows: list[dict[str, Any]] = []
    for group in ("train_only", "public_only", "modified"):
        for item in getattr(report, group):
            rows.append(
                {
                    "conflict_id": item.conflict_id,
                    "section": item.section,
                    "train_rule_id": item.train_rule_id or "none",
                    "public_rule_id": item.public_rule_id or "none",
                    "conflict_status": item.conflict_status,
                    "kind": item.kind,
                    "train_text": item.train_text or "none",
                    "public_text": item.public_text or "none",
                }
            )
    return rows


def schema_compare_rows(bundle: SplitBundle) -> list[dict[str, Any]]:
    from cross_business.schema_compare import detect_field_role

    rows: list[dict[str, Any]] = []
    for entry in bundle.column_entries:
        role = detect_field_role(entry.column)
        if role is None:
            continue
        rows.append(
            {
                "business_id": entry.business_id,
                "split": entry.split,
                "field_role": role,
                "column": entry.column,
                "semantic_type": entry.semantic_type,
                "presence": "present",
                "confidence": entry.confidence,
                "source_id": entry.source_id,
            }
        )
    return rows


def global_summary_rows(bundles: Sequence[SplitBundle]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for bundle in bundles:
        profile = bundle.global_profile
        if not profile:
            continue
        rows.append(
            {
                "split": bundle.split,
                "business_count": profile.business_count,
                "pass_count": profile.pass_count,
                "partial_count": profile.partial_count,
                "blocked_count": profile.blocked_count,
                "total_findings": profile.total_findings,
                "total_source_files": profile.total_source_files,
                "status": profile.status.value,
                "row_count_disclaimer": profile.row_count_disclaimer,
            }
        )
    return rows


def findings_rows(bundle: SplitBundle) -> list[dict[str, Any]]:
    return [
        {
            "finding_id": item.finding_id,
            "severity": item.severity,
            "domain": item.domain,
            "business_id": item.business_id,
            "source_id": item.source_id,
            "field": item.field or "none",
            "count": item.count,
            "denominator": item.denominator,
            "ratio": item.ratio,
            "evidence": item.evidence,
            "hypothesis": item.hypothesis or "none",
            "alternative_explanation": item.alternative_explanation or "none",
            "verification": item.verification or "none",
            "status": item.status.value,
        }
        for item in bundle.findings
    ]


def gate_ledger_rows(gates: Sequence[GateResult]) -> list[dict[str, Any]]:
    return [
        {
            "phase": gate.phase,
            "gate": gate.gate,
            "status": gate.status.value,
            "reason": gate.reason,
            "owner": gate.owner,
            "artifact": gate.artifact or "none",
        }
        for gate in gates
    ]


def business_report_rows(bundle: SplitBundle) -> list[dict[str, Any]]:
    return [report.to_dict() for report in bundle.business_reports]


def bundle_tables(bundle: SplitBundle) -> dict[str, list[dict[str, Any]]]:
    return {
        "TBL02": source_inventory_rows(bundle),
        "TBL03": sheet_registry_rows(bundle),
        "TBL04": sqlite_registry_rows(bundle),
        "TBL05": column_registry_rows(bundle),
        "TBL06": missing_rows(bundle),
        "TBL07": duplicate_rows(bundle),
        "TBL08": validity_rows(bundle),
        "TBL09": numeric_rows(bundle),
        "TBL10": categorical_rows(bundle),
        "TBL11": temporal_rows(bundle),
        "TBL12": relation_rows(bundle),
        "TBL13": business_profile_rows(bundle),
        "TBL14": kpi_rows(bundle),
        "TBL15": question_rows(bundle),
        "TBL17": schema_compare_rows(bundle),
        "TBL19": findings_rows(bundle),
    }


def mapping_payload(payload: Mapping[str, Any]) -> dict[str, Any]:
    return dict(payload)
