from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Mapping, Sequence

from common.enums import Status

SEVERITY_ORDER = ("critical", "high", "medium", "low", "info")
DOMAIN_ORDER = (
    "completeness",
    "uniqueness",
    "validity",
    "referential_integrity",
)


@dataclass(frozen=True)
class PreparedFrame:
    chart_id: str
    split: str
    business_id: str
    frame: Mapping[str, Any]
    source_ids: tuple[str, ...]
    population_n: int | None
    sample_n: int | None
    method: str
    unit: str
    denominator_label: str
    limitations: tuple[str, ...] = ()
    status: Status = Status.PASS
    notes: tuple[str, ...] = ()

    def to_dict(self) -> dict[str, Any]:
        return {
            "chart_id": self.chart_id,
            "split": self.split,
            "business_id": self.business_id,
            "source_ids": list(self.source_ids),
            "population_n": self.population_n,
            "sample_n": self.sample_n,
            "method": self.method,
            "unit": self.unit,
            "denominator_label": self.denominator_label,
            "limitations": list(self.limitations),
            "status": self.status.value,
            "notes": list(self.notes),
        }


@dataclass
class FrameRegistry:
    frames: dict[str, list[PreparedFrame]] = field(default_factory=dict)

    def add(self, frame: PreparedFrame) -> None:
        self.frames.setdefault(frame.chart_id, []).append(frame)

    def for_chart(self, chart_id: str) -> list[PreparedFrame]:
        return list(self.frames.get(chart_id, []))

    def all_frames(self) -> list[PreparedFrame]:
        result: list[PreparedFrame] = []
        for chart_id in sorted(self.frames):
            result.extend(self.frames[chart_id])
        return result


def build_inv01(
    split: str, counts_by_type: Mapping[str, int], source_ids: Sequence[str]
) -> PreparedFrame:
    labels = sorted(counts_by_type)
    values = [float(counts_by_type[label]) for label in labels]
    return PreparedFrame(
        chart_id="INV01",
        split=split,
        business_id="global",
        frame={"labels": labels, "values": values},
        source_ids=tuple(source_ids),
        population_n=int(sum(counts_by_type.values())),
        sample_n=None,
        method="file_manifest_count_by_source_type",
        unit="file",
        denominator_label="all source files in the split",
        limitations=("calendar, README, rulebook and question files are included",),
    )


def build_inv03(
    split: str, counts_by_business: Mapping[str, int], source_ids: Sequence[str]
) -> PreparedFrame:
    labels = sorted(counts_by_business)
    values = [float(counts_by_business[label]) for label in labels]
    return PreparedFrame(
        chart_id="INV03",
        split=split,
        business_id="global",
        frame={"labels": labels, "values": values},
        source_ids=tuple(source_ids),
        population_n=int(sum(counts_by_business.values())),
        sample_n=None,
        method="file_manifest_count_by_business",
        unit="file",
        denominator_label="all source files in the split",
        limitations=("file count does not measure data volume",),
    )


def build_inv04(
    split: str, counts_by_workbook: Mapping[str, int], source_ids: Sequence[str]
) -> PreparedFrame:
    labels = sorted(counts_by_workbook)
    values = [float(counts_by_workbook[label]) for label in labels]
    return PreparedFrame(
        chart_id="INV04",
        split=split,
        business_id="global",
        frame={"labels": labels, "values": values},
        source_ids=tuple(source_ids),
        population_n=int(sum(counts_by_workbook.values())),
        sample_n=None,
        method="sheet_registry_count_by_workbook",
        unit="sheet",
        denominator_label="all worksheets in the split",
        limitations=("formatting-only sheets are still counted",),
    )


def build_inv06(
    split: str,
    objects: Sequence[tuple[str, int, str]],
    source_ids: Sequence[str],
) -> PreparedFrame:
    ordered = sorted(objects, key=lambda item: -item[1])
    labels = [item[0] for item in ordered]
    values = [float(item[1]) for item in ordered]
    return PreparedFrame(
        chart_id="INV06",
        split=split,
        business_id="global",
        frame={"labels": labels, "values": values, "log_x": True},
        source_ids=tuple(source_ids),
        population_n=int(sum(item[1] for item in ordered)),
        sample_n=None,
        method="row_count_per_source_object",
        unit="row",
        denominator_label="data rows of every source object",
        limitations=("rows are not transactions and are never summed across grains",),
    )


def build_dq01(
    split: str,
    entries: Sequence[Mapping[str, Any]],
    source_ids: Sequence[str],
) -> PreparedFrame:
    rows = sorted(entries, key=lambda item: -float(item["missing_ratio"]))
    labels = [str(item["field"]) for item in rows]
    values = [round(float(item["missing_ratio"]) * 100.0, 4) for item in rows]
    denominator = int(rows[0]["n_total"]) if rows else 0
    return PreparedFrame(
        chart_id="DQ01",
        split=split,
        business_id="global",
        frame={"labels": labels, "values": values},
        source_ids=tuple(source_ids),
        population_n=denominator,
        sample_n=None,
        method="missing_n_over_total_n_per_column",
        unit="percent",
        denominator_label="n_total rows of the profiled column",
        limitations=("structural blanks are reported separately from true gaps",),
    )


def build_dq06(
    split: str,
    findings: Sequence[Any],
    source_ids: Sequence[str],
    domains: Sequence[str] | None = None,
    severities: Sequence[str] | None = None,
) -> PreparedFrame:
    rows = list(domains) if domains else [
        domain
        for domain in DOMAIN_ORDER
        if any(item.domain == domain for item in findings)
    ]
    if not rows:
        rows = sorted({item.domain for item in findings})
    columns = list(severities) if severities else list(SEVERITY_ORDER)
    matrix = [
        [
            float(
                sum(
                    1
                    for item in findings
                    if item.domain == domain and item.severity == severity
                )
            )
            for severity in columns
        ]
        for domain in rows
    ]
    return PreparedFrame(
        chart_id="DQ06",
        split=split,
        business_id="global",
        frame={
            "matrix": matrix,
            "rows": rows,
            "columns": columns,
        },
        source_ids=tuple(source_ids),
        population_n=len(findings),
        sample_n=None,
        method="count_findings_by_domain_and_severity",
        unit="finding",
        denominator_label="all quality findings in the split",
        limitations=("severity is evidence-based, not a business impact rating",),
    )


def build_num01(
    split: str,
    business_id: str,
    field: str,
    edges: Sequence[float],
    counts: Sequence[int],
    population_n: int,
    source_id: str,
) -> PreparedFrame:
    if len(edges) == len(counts) and counts:
        labels = [f"{edge:.4g}" for edge in edges]
    elif len(edges) == len(counts) + 1:
        labels = [
            f"{edges[index]:.4g}-{edges[index + 1]:.4g}" for index in range(len(counts))
        ]
    else:
        labels = [f"bin{index}" for index in range(len(counts))]
    return PreparedFrame(
        chart_id="NUM01",
        split=split,
        business_id=business_id,
        frame={
            "labels": labels,
            "values": [float(value) for value in counts],
            "bins": len(counts),
        },
        source_ids=(source_id,),
        population_n=population_n,
        sample_n=None,
        method="equal_width_histogram_full_population",
        unit="business unit",
        denominator_label="all parseable values of the measure",
        limitations=("bins are equal-width; outliers remain inside the last bin",),
    )


def build_num02(
    split: str,
    business_id: str,
    field: str,
    xs: Sequence[float],
    ys: Sequence[float],
    population_n: int,
    source_id: str,
) -> PreparedFrame:
    return PreparedFrame(
        chart_id="NUM02",
        split=split,
        business_id=business_id,
        frame={"labels": list(xs), "values": list(ys)},
        source_ids=(source_id,),
        population_n=population_n,
        sample_n=len(xs),
        method="empirical_cdf_full_population",
        unit="fraction",
        denominator_label="all parseable values of the measure",
        limitations=("missing values are excluded from the population",),
    )


def build_num04(
    split: str,
    business_id: str,
    entries: Sequence[Mapping[str, Any]],
    source_ids: Sequence[str],
) -> PreparedFrame:
    rows = sorted(entries, key=lambda item: -float(item["zero_ratio"]))
    labels = [str(item["field"]) for item in rows]
    values = [round(float(item["zero_ratio"]) * 100.0, 4) for item in rows]
    return PreparedFrame(
        chart_id="NUM04",
        split=split,
        business_id=business_id,
        frame={"labels": labels, "values": values},
        source_ids=tuple(source_ids),
        population_n=int(sum(int(item["n_valid"]) for item in rows)),
        sample_n=None,
        method="zero_n_over_valid_n_per_measure",
        unit="percent",
        denominator_label="n_valid rows of each measure",
        limitations=("a zero can be a legitimate business value",),
    )


def build_cat01(
    split: str,
    business_id: str,
    entries: Sequence[Mapping[str, Any]],
    source_ids: Sequence[str],
) -> PreparedFrame:
    labels = [str(item["category"]) for item in entries]
    values = [float(item["count"]) for item in entries]
    return PreparedFrame(
        chart_id="CAT01",
        split=split,
        business_id=business_id,
        frame={"labels": labels, "values": values},
        source_ids=tuple(source_ids),
        population_n=int(sum(values)),
        sample_n=None,
        method="top_k_with_others_full_population",
        unit="row",
        denominator_label="all rows of the profiled field",
        limitations=("aliases are not merged without README evidence",),
    )


def build_tmp01(
    split: str,
    rows: Sequence[str],
    columns: Sequence[str],
    matrix: Sequence[Sequence[float]],
    source_ids: Sequence[str],
) -> PreparedFrame:
    return PreparedFrame(
        chart_id="TMP01",
        split=split,
        business_id="global",
        frame={
            "matrix": [list(row) for row in matrix],
            "rows": list(rows),
            "columns": list(columns),
        },
        source_ids=tuple(source_ids),
        population_n=len(rows) * len(columns),
        sample_n=None,
        method="event_count_per_calendar_day",
        unit="row",
        denominator_label="calendar days covered by the split calendar",
        limitations=("a day without events is not necessarily missing data",),
    )


def build_tmp03(
    split: str,
    rows: Sequence[str],
    columns: Sequence[str],
    matrix: Sequence[Sequence[float]],
    source_ids: Sequence[str],
) -> PreparedFrame:
    return PreparedFrame(
        chart_id="TMP03",
        split=split,
        business_id="global",
        frame={
            "matrix": [list(row) for row in matrix],
            "rows": list(rows),
            "columns": list(columns),
        },
        source_ids=tuple(source_ids),
        population_n=len(rows) * len(columns),
        sample_n=None,
        method="observed_month_index_versus_covered_range",
        unit="month",
        denominator_label="months between the earliest and latest observed event",
        limitations=("absence of events is distinct from absence of source data",),
    )


def build_qna01(
    split: str,
    lengths: Sequence[int],
    population_n: int,
    source_ids: Sequence[str],
) -> PreparedFrame:
    return PreparedFrame(
        chart_id="QNA01",
        split=split,
        business_id="global",
        frame={
            "labels": [split],
            "values": [float(value) for value in lengths],
            "groups": [list(lengths)],
        },
        source_ids=tuple(source_ids),
        population_n=population_n,
        sample_n=len(lengths),
        method="character_length_per_question",
        unit="characters",
        denominator_label="all questions of the split",
        limitations=("character count is tokenizer dependent",),
    )


def build_qna03(
    split: str,
    counts: Mapping[str, int],
    population_n: int,
    source_ids: Sequence[str],
) -> PreparedFrame:
    labels = sorted(counts)
    values = [float(counts[label]) for label in labels]
    return PreparedFrame(
        chart_id="QNA03",
        split=split,
        business_id="global",
        frame={"labels": labels, "values": values},
        source_ids=tuple(source_ids),
        population_n=population_n,
        sample_n=None,
        method="keyword_annotated_time_expression_counts",
        unit="question",
        denominator_label="all questions of the split",
        limitations=("multi-label; the same question may carry several expressions",),
    )


def build_cbs01(
    split: str,
    rows: Sequence[str],
    columns: Sequence[str],
    matrix: Sequence[Sequence[float]],
    source_ids: Sequence[str],
) -> PreparedFrame:
    return PreparedFrame(
        chart_id="CBS01",
        split=split,
        business_id="global",
        frame={
            "matrix": [list(row) for row in matrix],
            "rows": list(rows),
            "columns": list(columns),
        },
        source_ids=tuple(source_ids),
        population_n=len(rows) * len(columns),
        sample_n=None,
        method="semantic_role_presence_per_business",
        unit="presence",
        denominator_label="business and semantic role combinations",
        limitations=("a shared role does not imply an equivalent join key",),
    )


def build_glb01(
    split: str,
    status_by_business: Mapping[str, str],
    source_ids: Sequence[str],
) -> PreparedFrame:
    labels = sorted(status_by_business)
    values = [float(status_by_business[label] == "PASS") for label in labels]
    return PreparedFrame(
        chart_id="GLB01",
        split=split,
        business_id="global",
        frame={"labels": labels, "values": values},
        source_ids=tuple(source_ids),
        population_n=len(labels),
        sample_n=None,
        method="coverage_status_per_business",
        unit="business",
        denominator_label="all businesses of the split",
        limitations=("coverage status is not a data-quality score",),
    )
