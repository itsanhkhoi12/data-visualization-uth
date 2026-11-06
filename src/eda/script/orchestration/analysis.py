from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Any, Mapping, Sequence

from business.business_inventory import (
    BusinessProfile,
    BusinessSourceEntry,
    build_business_profile,
)
from business.business_chart_metrics import compute_business_metric_rows
from business.domain_profiles import DomainDiagnostic, profile_business_domain
from business.kpi_catalogue import build_kpi_catalogue
from common.bundles import SplitBundle
from common.config import EdaConfig
from common.contracts import SourceRecord
from common.enums import SemanticType, Status
from common.paths import DatasetContext
from cross_business.schema_compare import detect_field_role
from inventory.file_manifest import FileManifest, build_file_manifest
from inventory.sheet_registry import SheetRegistry, build_sheet_registry
from inventory.sqlite_registry import SqliteRegistry, build_sqlite_registry
from quality.duplicates import DuplicateEntry, profile_duplicates
from quality.findings import compile_findings
from quality.integrity import IntegrityEntry, profile_integrity
from quality.missingness import MissingnessEntry, profile_missingness
from quality.validity import ValidityEntry, profile_validity
from questions.alignment import profile_question_alignment
from questions.answer_profile import profile_train_answers
from questions.question_profile import profile_questions, question_metadata_records
from readers.table_reader import LoadedTable, load_table
from rulebook.rule_registry import RuleRegistry, compile_rule_registry
from schema.column_registry import ColumnRegistryEntry, build_column_registry
from schema.key_candidates import KeyCandidate, best_key_candidate, find_candidate_keys
from schema.relations import RelationEvidence, profile_relation, propose_key_pairs
from schema.type_inference import is_blank, parse_date, parse_datetime
from statistics.categorical import (
    CategoricalProfileRequest,
    profile_categorical,
    top_k_with_others,
)
from statistics.numeric import NumericProfileRequest, profile_numeric
from temporal.calendar_registry import CalendarRegistry, validate_calendar
from temporal.coverage import (
    TemporalCoverage,
    daily_counts_from_dates,
    profile_time_coverage,
    weekday_counts_from_dates,
)
from temporal.date_fields import DateFieldProfile, profile_date_fields

MAX_ANALYSIS_ROWS = 200_000
MAX_RELATION_TABLES = 6
MAX_RELATION_KEY_PAIRS = 2
CHART_SAMPLE_VALUES = 5_000
CHART_SAMPLE_ROWS = 2_000
TOP_K_CATEGORIES = 20
BUSINESS_SUFFIXES = (".xlsx", ".csv", ".sqlite")


@dataclass
class TableAnalysis:
    table: LoadedTable
    column_entries: tuple[ColumnRegistryEntry, ...]
    missing_entries: tuple[MissingnessEntry, ...]
    duplicate_entries: tuple[DuplicateEntry, ...]
    validity_entries: tuple[ValidityEntry, ...]
    key_candidates: tuple[KeyCandidate, ...]
    numeric_stats: tuple[Any, ...]
    categorical_stats: tuple[Any, ...]
    date_profiles: tuple[DateFieldProfile, ...]
    coverages: tuple[TemporalCoverage, ...]
    numeric_samples: dict[str, list[float]]
    daily_counts: dict[str, dict[str, int]]
    row_samples: list[dict[str, Any]]
    row_cap_applied: bool
    business_metrics: tuple[Any, ...]

    @property
    def source_id(self) -> str:
        return self.table.source_id


def _semantic_by_column(
    entries: Sequence[ColumnRegistryEntry],
) -> dict[str, str]:
    return {entry.column: entry.semantic_type for entry in entries}


def _business_source_entries(
    records: Sequence[SourceRecord], business_id: str
) -> list[BusinessSourceEntry]:
    return [
        BusinessSourceEntry(
            logical_path=record.logical_path,
            source_type=record.source_type,
            size_bytes=record.size_bytes,
            content_hash=record.content_hash,
        )
        for record in records
        if record.business_id == business_id
        and Path(record.logical_path).suffix.lower() in BUSINESS_SUFFIXES
    ]


def _objects_of(
    record: SourceRecord,
    sheet_registry: SheetRegistry,
    sqlite_registry: SqliteRegistry,
) -> list[tuple[str | None, str | None]]:
    if record.source_type == "xlsx":
        return [
            (entry.sheet_name, None)
            for entry in sheet_registry.entries
            if entry.source_id.startswith(f"{record.source_id}#sheet=")
        ]
    if record.source_type == "sqlite":
        return [
            (None, entry.object_name)
            for entry in sqlite_registry.entries
            if entry.source_id.startswith(f"{record.source_id}#table=")
            and entry.object_type == "table"
        ]
    return [(None, None)]


def _load_object(
    record: SourceRecord,
    sheet_name: str | None,
    table_name: str | None,
    max_rows: int,
) -> LoadedTable | None:
    try:
        return load_table(
            record,
            sheet_name=sheet_name,
            table_name=table_name,
            max_rows=max_rows,
        )
    except Exception:
        return None


def _collect_dates(
    table: LoadedTable, date_columns: Sequence[str]
) -> dict[str, list[date]]:
    collected: dict[str, list[date]] = {}
    for column in date_columns:
        values: list[date] = []
        for row in table.rows:
            value = row.get(column)
            if is_blank(value):
                continue
            parsed = parse_date(value)
            if parsed is None:
                parsed_datetime = parse_datetime(value)
                parsed = parsed_datetime.date() if parsed_datetime else None
            if parsed is not None:
                values.append(parsed)
        collected[column] = values
    return collected


def analyze_table(
    table: LoadedTable,
    split: str,
    calendar: CalendarRegistry | None,
) -> TableAnalysis:
    column_entries = build_column_registry(table, sample_limit=5_000)
    semantic_by_column = _semantic_by_column(column_entries)
    missing_entries = profile_missingness(table, semantic_by_column)
    validity_entries = profile_validity(table, semantic_by_column)
    key_candidates = find_candidate_keys(table)
    best_key = best_key_candidate(key_candidates)
    key_columns = best_key.key_columns if best_key else ()
    duplicate_entries = profile_duplicates(table, key_columns if key_columns else None)
    numeric_stats: list[Any] = []
    categorical_stats: list[Any] = []
    numeric_samples: dict[str, list[float]] = {}
    measure_columns = [
        entry.column
        for entry in column_entries
        if entry.semantic_type
        in {SemanticType.MEASURE.value, SemanticType.AMOUNT.value, SemanticType.QUANTITY.value}
    ]
    categorical_columns = [
        entry.column
        for entry in column_entries
        if entry.semantic_type
        in {SemanticType.CATEGORICAL.value, SemanticType.BOOLEAN.value}
    ]
    date_columns = [
        entry.column
        for entry in column_entries
        if entry.semantic_type
        in {SemanticType.DATE.value, SemanticType.DATETIME.value}
    ]
    for column in measure_columns:
        values = [row.get(column) for row in table.rows]
        request = NumericProfileRequest(
            source_id=table.source_id,
            split=split,
            business_id=table.business_id,
            field=column,
            unit=next(
                (
                    entry.unit
                    for entry in column_entries
                    if entry.column == column
                ),
                None,
            ),
            values=values,
            total_n=len(table.rows),
        )
        numeric_stats.append(profile_numeric(request))
        parsed = []
        for value in values:
            from schema.type_inference import parse_number

            number = parse_number(value)
            if number is not None:
                parsed.append(number)
        numeric_samples[column] = parsed[:CHART_SAMPLE_VALUES]
    for column in categorical_columns:
        request = CategoricalProfileRequest(
            source_id=table.source_id,
            split=split,
            business_id=table.business_id,
            field=column,
            values=[row.get(column) for row in table.rows],
            total_n=len(table.rows),
            top_k=TOP_K_CATEGORIES,
        )
        categorical_stats.extend(top_k_with_others(profile_categorical(request)))
    date_profiles = profile_date_fields(
        source_id=table.source_id,
        split=split,
        business_id=table.business_id,
        object_name=table.object_name,
        rows=table.rows,
        date_columns=date_columns,
        total_n=len(table.rows),
    )
    dates_by_column = _collect_dates(table, date_columns)
    coverages: list[TemporalCoverage] = []
    daily_counts: dict[str, dict[str, int]] = {}
    calendar_start = None
    calendar_end = None
    if calendar and calendar.min_date and calendar.max_date:
        calendar_start = date.fromisoformat(calendar.min_date)
        calendar_end = date.fromisoformat(calendar.max_date)
    for profile in date_profiles:
        dates = dates_by_column.get(profile.column, [])
        day_counts = daily_counts_from_dates(dates)
        weekday_counts = weekday_counts_from_dates(dates)
        daily_counts[profile.column] = day_counts
        coverages.append(
            profile_time_coverage(
                profile, day_counts, weekday_counts, calendar_start, calendar_end
            )
        )
    return TableAnalysis(
        table=table,
        column_entries=column_entries,
        missing_entries=missing_entries,
        duplicate_entries=duplicate_entries,
        validity_entries=validity_entries,
        key_candidates=key_candidates,
        numeric_stats=tuple(numeric_stats),
        categorical_stats=tuple(categorical_stats),
        date_profiles=tuple(date_profiles),
        coverages=tuple(coverages),
        numeric_samples=numeric_samples,
        daily_counts=daily_counts,
        row_samples=[dict(row) for row in table.rows[:CHART_SAMPLE_ROWS]],
        row_cap_applied=table.truncated,
        business_metrics=compute_business_metric_rows(table),
    )


def _relation_candidates(
    analyses: Sequence[TableAnalysis],
    split: str,
) -> tuple[RelationEvidence, ...]:
    relations: list[RelationEvidence] = []
    selected = list(analyses)[:MAX_RELATION_TABLES]
    for index, left in enumerate(selected):
        for right in selected[index + 1 :]:
            pairs = propose_key_pairs(left.table, right.table)
            for join_keys in pairs[:MAX_RELATION_KEY_PAIRS]:
                relations.append(
                    profile_relation(
                        left.table,
                        right.table,
                        join_keys,
                        split,
                        left.table.business_id,
                    )
                )
    return tuple(relations)


def analyze_split(
    config: EdaConfig, split: str, rule_registry: RuleRegistry | None = None
) -> SplitBundle:
    context: DatasetContext = config.context_for(split)
    manifest: FileManifest = build_file_manifest(context, config.business_filter)
    sheet_registry = build_sheet_registry(manifest.records, split)
    sqlite_registry = build_sqlite_registry(manifest.records, split)
    calendar = validate_calendar(context.calendar_path, split)
    business_profiles: list[BusinessProfile] = []
    analyses: list[TableAnalysis] = []
    for business_id in manifest.business_ids:
        readme_path = context.business_root_path(business_id) / "README.md"
        readme_hash = ""
        if readme_path.exists():
            from common.provenance import fingerprint_file

            readme_hash = fingerprint_file(readme_path)
        profile = build_business_profile(
            business_id=business_id,
            split=split,
            sources=_business_source_entries(manifest.records, business_id),
            readme_path=readme_path,
            readme_hash=readme_hash,
        )
        business_profiles.append(profile)
    for record in manifest.records:
        if record.business_id == "__split__":
            continue
        if record.source_type not in {"csv", "xlsx", "sqlite"}:
            continue
        for sheet_name, table_name in _objects_of(
            record, sheet_registry, sqlite_registry
        ):
            table = _load_object(
                record, sheet_name, table_name, MAX_ANALYSIS_ROWS
            )
            if table is None or not table.rows:
                continue
            analyses.append(analyze_table(table, split, calendar))
    by_business: dict[str, list[TableAnalysis]] = {}
    for analysis in analyses:
        by_business.setdefault(analysis.table.business_id, []).append(analysis)
    relations: list[RelationEvidence] = []
    for business_analyses in by_business.values():
        relations.extend(_relation_candidates(business_analyses, split))
    integrity_entries: tuple[IntegrityEntry, ...] = profile_integrity(relations)
    all_missing: list[MissingnessEntry] = []
    all_duplicates: list[DuplicateEntry] = []
    all_validity: list[ValidityEntry] = []
    all_columns: list[ColumnRegistryEntry] = []
    all_numeric: list[Any] = []
    all_categorical: list[Any] = []
    all_dates: list[DateFieldProfile] = []
    all_coverages: list[TemporalCoverage] = []
    all_keys: list[KeyCandidate] = []
    business_metrics: list[Any] = []
    numeric_samples: dict[str, dict[str, Any]] = {}
    daily_counts: dict[str, dict[str, int]] = {}
    row_samples: dict[str, tuple[Mapping[str, Any], ...]] = {}
    source_row_counts: dict[str, int] = {}
    source_total_row_counts: dict[str, int] = {}
    source_truncated: dict[str, bool] = {}
    for analysis in analyses:
        all_missing.extend(analysis.missing_entries)
        all_duplicates.extend(analysis.duplicate_entries)
        all_validity.extend(analysis.validity_entries)
        all_columns.extend(analysis.column_entries)
        all_numeric.extend(analysis.numeric_stats)
        all_categorical.extend(analysis.categorical_stats)
        all_dates.extend(analysis.date_profiles)
        all_coverages.extend(analysis.coverages)
        all_keys.extend(analysis.key_candidates)
        business_metrics.extend(analysis.business_metrics)
        for column, values in analysis.numeric_samples.items():
            numeric_samples.setdefault(analysis.source_id, {})[column] = values
        for column, counts in analysis.daily_counts.items():
            daily_counts.setdefault(analysis.source_id, {})[column] = counts
        if analysis.row_samples:
            row_samples.setdefault(
                analysis.source_id, tuple(analysis.row_samples)
            )
        source_row_counts[analysis.source_id] = analysis.table.row_count
        source_total_row_counts[analysis.source_id] = (
            analysis.table.total_row_count
            if analysis.table.total_row_count is not None
            else analysis.table.row_count
        )
        source_truncated[analysis.source_id] = analysis.table.truncated
    findings = compile_findings(
        all_missing, all_duplicates, all_validity, integrity_entries
    )
    diagnostics: list[DomainDiagnostic] = []
    metrics: list[Any] = []
    for profile in business_profiles:
        diagnostics.extend(profile_business_domain(profile))
        evidence = sorted(
            {
                role
                for entry in all_columns
                if entry.business_id == profile.business_id
                for role in [detect_field_role(entry.column)]
                if role
            }
        )
        metrics.extend(
            build_kpi_catalogue(
                split=split,
                business_id=profile.business_id,
                available_evidence=evidence,
                rule_registry=rule_registry,
            )
        )
    question_profile = profile_questions(context.questions_path, split)
    metadata = question_metadata_records(context.questions_path, split)
    question_lengths = tuple(
        int(record["question_length_characters"]) for record in metadata
    )
    answer_profile = None
    if context.has_labels:
        answer_profile = profile_train_answers(
            context.require_labels(), context.questions_path, split
        )
    alignment = profile_question_alignment(
        split=split,
        question_metadata=metadata,
        available_businesses=manifest.business_ids,
        has_labels=context.has_labels,
    )
    notes: list[str] = []
    capped = [item for item in analyses if item.row_cap_applied]
    if capped:
        notes.append(
            f"row_cap_applied_to_{len(capped)}_source_objects_at_{MAX_ANALYSIS_ROWS}_rows"
        )
    if sheet_registry.error_paths:
        notes.append(f"sheet_registry_errors_{len(sheet_registry.error_paths)}")
    if sqlite_registry.error_paths:
        notes.append(f"sqlite_registry_errors_{len(sqlite_registry.error_paths)}")
    return SplitBundle(
        split=split,
        manifest=manifest,
        sheet_registry=sheet_registry,
        sqlite_registry=sqlite_registry,
        business_profiles=tuple(business_profiles),
        column_entries=tuple(all_columns),
        missing_entries=tuple(all_missing),
        duplicate_entries=tuple(all_duplicates),
        validity_entries=tuple(all_validity),
        integrity_entries=integrity_entries,
        relations=tuple(relations),
        key_candidates=tuple(all_keys),
        numeric_stats=tuple(all_numeric),
        categorical_stats=tuple(all_categorical),
        date_profiles=tuple(all_dates),
        coverages=tuple(all_coverages),
        findings=findings,
        domain_diagnostics=tuple(diagnostics),
        metrics=tuple(metrics),
        question_profile=question_profile,
        answer_profile=answer_profile,
        alignment=tuple(alignment),
        calendar=calendar,
        rule_registry=rule_registry,
        numeric_samples=numeric_samples,
        daily_counts=daily_counts,
        row_samples=row_samples,
        source_row_counts=source_row_counts,
        source_total_row_counts=source_total_row_counts,
        source_truncated=source_truncated,
        question_metadata=tuple(metadata),
        question_lengths=question_lengths,
        business_metrics=tuple(business_metrics),
        notes=tuple(notes),
    )


def count_by_business(manifest: FileManifest) -> dict[str, int]:
    counts: dict[str, int] = {}
    for record in manifest.records:
        counts[record.business_id] = counts.get(record.business_id, 0) + 1
    return counts


def sheets_by_workbook(sheet_registry: SheetRegistry) -> dict[str, int]:
    counts: dict[str, int] = {}
    for entry in sheet_registry.entries:
        counts[entry.workbook_path] = counts.get(entry.workbook_path, 0) + 1
    return counts


def rows_by_source_object(
    sheet_registry: SheetRegistry, sqlite_registry: SqliteRegistry
) -> list[tuple[str, int, str]]:
    objects: list[tuple[str, int, str]] = []
    for entry in sheet_registry.entries:
        objects.append(
            (
                f"{entry.business_id}/{Path(entry.workbook_path).stem}#{entry.sheet_name}",
                int(entry.data_row_count),
                "worksheet",
            )
        )
    for entry in sqlite_registry.entries:
        objects.append(
            (
                f"{entry.business_id}/{Path(entry.database_path).stem}#{entry.object_name}",
                int(entry.row_count or 0),
                "database table",
            )
        )
    return objects


def source_type_counts(manifest: FileManifest) -> dict[str, int]:
    return dict(sorted(manifest.counts_by_type.items()))


def categorical_top_k_rows(bundle: SplitBundle) -> list[tuple[str, list[dict[str, Any]]]]:
    grouped: dict[tuple[str, str], list[dict[str, Any]]] = {}
    for item in bundle.categorical_stats:
        key = (item.business_id, item.field)
        grouped.setdefault(key, []).append(
            {
                "category": item.category,
                "count": item.count,
                "share": item.share,
                "is_null": item.is_null,
                "rank": item.rank,
            }
        )
    rows: list[tuple[str, list[dict[str, Any]]]] = []
    for (business_id, field), entries in sorted(grouped.items()):
        if not any(entry["count"] > 0 for entry in entries):
            continue
        rows.append((f"{business_id}/{field}", entries))
    return rows


def daily_activity_matrix(
    bundle: SplitBundle,
) -> tuple[list[str], list[str], list[list[float]]]:
    counts_by_business: dict[str, dict[str, int]] = {}
    for source_id, columns in bundle.daily_counts.items():
        business_id = "unknown"
        for entry in bundle.column_entries:
            if entry.source_id == source_id:
                business_id = entry.business_id
                break
        for day_counts in columns.values():
            target = counts_by_business.setdefault(business_id, {})
            for day, count in day_counts.items():
                target[day] = target.get(day, 0) + count
    if not counts_by_business:
        return [], [], []
    days = sorted({day for counts in counts_by_business.values() for day in counts})
    businesses = sorted(counts_by_business)
    matrix: list[list[float]] = []
    for business_id in businesses:
        counts = counts_by_business[business_id]
        matrix.append([float(counts.get(day, 0)) for day in days])
    return businesses, days, matrix


def missing_entries_for_chart(
    bundle: SplitBundle, business_id: str = "global"
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for entry in bundle.missing_entries:
        if business_id != "global" and entry.business_id != business_id:
            continue
        rows.append(
            {
                "field": f"{entry.business_id}/{entry.object_name}/{entry.column}",
                "missing_ratio": entry.missing_ratio,
                "n_missing": entry.n_missing,
                "n_total": entry.n_total,
            }
        )
    return rows


def severity_matrix(bundle: SplitBundle) -> tuple[list[str], list[str], list[list[float]]]:
    from visualization.chart_frames import DOMAIN_ORDER, SEVERITY_ORDER

    domains = [
        domain
        for domain in DOMAIN_ORDER
        if any(item.domain == domain for item in bundle.findings)
    ]
    if not domains:
        domains = sorted({item.domain for item in bundle.findings})
    matrix = [
        [
            float(
                sum(
                    1
                    for item in bundle.findings
                    if item.domain == domain and item.severity == severity
                )
            )
            for severity in SEVERITY_ORDER
        ]
        for domain in domains
    ]
    return domains, list(SEVERITY_ORDER), matrix


def categorical_frequency(
    bundle: SplitBundle, business_id: str, field: str
) -> list[dict[str, Any]]:
    return [
        {
            "category": item.category,
            "count": item.count,
            "share": item.share,
        }
        for item in bundle.categorical_stats
        if item.business_id == business_id and item.field == field
    ]


def numeric_zero_ratio_rows(bundle: SplitBundle) -> list[dict[str, Any]]:
    return [
        {
            "field": f"{item.business_id}/{item.field}",
            "zero_ratio": item.zero_ratio,
            "n_valid": item.n_valid,
        }
        for item in bundle.numeric_stats
        if item.n_valid
    ]


def counter_to_mapping(counter: Counter) -> dict[str, int]:
    return dict(sorted(counter.items()))


def mapping_get(mapping: Mapping[str, Any], key: str, default: Any = None) -> Any:
    return mapping.get(key, default)


def status_value(status: Status) -> str:
    return status.value
