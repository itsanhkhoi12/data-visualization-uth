from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Sequence

from common.enums import Status
from readers.table_reader import LoadedTable
from schema.type_inference import is_blank, parse_date, parse_number


@dataclass(frozen=True)
class ValidityEntry:
    source_id: str
    split: str
    business_id: str
    object_name: str
    column: str
    rule: str
    rule_id: str
    invalid_count: int
    denominator: int
    invalid_ratio: float
    severity: str
    status: Status
    evidence: str
    sample_masked: tuple[str, ...]
    hypothesis: str | None = None
    alternative_explanation: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "source_id": self.source_id,
            "split": self.split,
            "business_id": self.business_id,
            "object_name": self.object_name,
            "column": self.column,
            "rule": self.rule,
            "rule_id": self.rule_id,
            "invalid_count": self.invalid_count,
            "denominator": self.denominator,
            "invalid_ratio": self.invalid_ratio,
            "severity": self.severity,
            "status": self.status.value,
            "evidence": self.evidence,
            "sample_masked": list(self.sample_masked),
            "hypothesis": self.hypothesis,
            "alternative_explanation": self.alternative_explanation,
        }


def mask_value(value: Any) -> str:
    text = str(value).strip()
    if not text:
        return ""
    if len(text) <= 3:
        return "*" * len(text)
    return f"{text[0]}{'*' * (len(text) - 2)}{text[-1]}"


def profile_validity(
    table: LoadedTable,
    semantic_by_column: dict[str, str],
    allowed_values: dict[str, tuple[str, ...]] | None = None,
) -> tuple[ValidityEntry, ...]:
    allowed_values = allowed_values or {}
    entries: list[ValidityEntry] = []
    for column in [name for name in table.header if name]:
        semantic = semantic_by_column.get(column, "unknown")
        if semantic in {"measure", "amount", "quantity"}:
            invalid = 0
            denominator = 0
            samples: list[str] = []
            for row in table.rows:
                value = row.get(column)
                if is_blank(value):
                    continue
                denominator += 1
                if parse_number(value) is None:
                    invalid += 1
                    if len(samples) < 5:
                        samples.append(mask_value(value))
            if invalid:
                entries.append(
                    ValidityEntry(
                        source_id=table.source_id,
                        split=table.split,
                        business_id=table.business_id,
                        object_name=table.object_name,
                        column=column,
                        rule="value_must_parse_as_number",
                        rule_id="VAL.NUM.PARSE",
                        invalid_count=invalid,
                        denominator=denominator,
                        invalid_ratio=round(invalid / denominator, 6) if denominator else 0.0,
                        severity="medium",
                        status=Status.PARTIAL,
                        evidence=(
                            "non-numeric token found in a column typed as a numeric measure"
                        ),
                        sample_masked=tuple(samples),
                        hypothesis="text-formatted numbers with thousands separators or units",
                        alternative_explanation="column mixes measures with notes",
                    )
                )
        elif semantic == "date":
            invalid = 0
            denominator = 0
            samples = []
            for row in table.rows:
                value = row.get(column)
                if is_blank(value):
                    continue
                denominator += 1
                if parse_date(value) is None:
                    invalid += 1
                    if len(samples) < 5:
                        samples.append(mask_value(value))
            if invalid:
                entries.append(
                    ValidityEntry(
                        source_id=table.source_id,
                        split=table.split,
                        business_id=table.business_id,
                        object_name=table.object_name,
                        column=column,
                        rule="value_must_parse_as_date",
                        rule_id="VAL.DATE.PARSE",
                        invalid_count=invalid,
                        denominator=denominator,
                        invalid_ratio=round(invalid / denominator, 6) if denominator else 0.0,
                        severity="medium",
                        status=Status.PARTIAL,
                        evidence="value could not be interpreted as a calendar date",
                        sample_masked=tuple(samples),
                        hypothesis="mixed date formats across source systems",
                        alternative_explanation="free-text date remarks",
                    )
                )
        if column in allowed_values:
            permitted = set(allowed_values[column])
            invalid = 0
            denominator = 0
            samples = []
            for row in table.rows:
                value = row.get(column)
                if is_blank(value):
                    continue
                denominator += 1
                if str(value).strip() not in permitted:
                    invalid += 1
                    if len(samples) < 5:
                        samples.append(mask_value(value))
            if invalid:
                entries.append(
                    ValidityEntry(
                        source_id=table.source_id,
                        split=table.split,
                        business_id=table.business_id,
                        object_name=table.object_name,
                        column=column,
                        rule="value_must_be_in_documented_domain",
                        rule_id="VAL.CATEGORY.DOMAIN",
                        invalid_count=invalid,
                        denominator=denominator,
                        invalid_ratio=round(invalid / denominator, 6) if denominator else 0.0,
                        severity="low",
                        status=Status.PARTIAL,
                        evidence="value outside the documented status taxonomy",
                        sample_masked=tuple(samples),
                        hypothesis="documented taxonomy is incomplete for this business",
                        alternative_explanation="a newer status label not covered by the rulebook",
                    )
                )
    return tuple(entries)


def profile_negative_values(
    table: LoadedTable, semantic_by_column: dict[str, str]
) -> tuple[ValidityEntry, ...]:
    entries: list[ValidityEntry] = []
    for column in [name for name in table.header if name]:
        if semantic_by_column.get(column) not in {"measure", "amount", "quantity"}:
            continue
        negative = 0
        denominator = 0
        samples: list[str] = []
        for row in table.rows:
            value = row.get(column)
            if is_blank(value):
                continue
            denominator += 1
            number = parse_number(value)
            if number is not None and number < 0:
                negative += 1
                if len(samples) < 5:
                    samples.append(mask_value(value))
        if negative:
            entries.append(
                ValidityEntry(
                    source_id=table.source_id,
                    split=table.split,
                    business_id=table.business_id,
                    object_name=table.object_name,
                    column=column,
                    rule="negative_value_requires_business_justification",
                    rule_id="VAL.NUM.NEGATIVE",
                    invalid_count=negative,
                    denominator=denominator,
                    invalid_ratio=round(negative / denominator, 6) if denominator else 0.0,
                    severity="low",
                    status=Status.PARTIAL,
                    evidence="negative values observed in a measure column",
                    sample_masked=tuple(samples),
                    hypothesis="refund, return or reversal line items",
                    alternative_explanation="data entry sign convention",
                )
            )
    return tuple(entries)
