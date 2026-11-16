from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Sequence

from common.enums import SemanticType

METHOD_VERSION = "semantic_eligibility.v1"
MIN_CONTINUOUS_N = 30
MAX_CONTINUOUS_UNIQUE_RATIO = 0.5
MAX_CATEGORICAL_CARDINALITY = 100
MIN_CATEGORICAL_N = 20


@dataclass(frozen=True)
class SemanticEligibility:
    field: str
    semantic_type: str
    eligibility: str
    reason: str
    n_valid: int
    n_unique: int
    unique_ratio: float

    def to_dict(self) -> dict[str, Any]:
        return {
            "field": self.field,
            "semantic_type": self.semantic_type,
            "eligibility": self.eligibility,
            "reason": self.reason,
            "n_valid": self.n_valid,
            "n_unique": self.n_unique,
            "unique_ratio": self.unique_ratio,
        }


def numeric_measure_eligibility(
    field: str,
    semantic_type: str,
    n_valid: int,
    n_unique: int,
) -> SemanticEligibility:
    unique_ratio = n_unique / n_valid if n_valid else 0.0
    if semantic_type == SemanticType.IDENTIFIER.value:
        return SemanticEligibility(
            field=field,
            semantic_type=semantic_type,
            eligibility="NOT_APPLICABLE",
            reason="identifier_fields_are_excluded_from_distributional_statistics",
            n_valid=n_valid,
            n_unique=n_unique,
            unique_ratio=unique_ratio,
        )
    if semantic_type not in {
        SemanticType.MEASURE.value,
        SemanticType.AMOUNT.value,
        SemanticType.QUANTITY.value,
    }:
        return SemanticEligibility(
            field=field,
            semantic_type=semantic_type,
            eligibility="NOT_APPLICABLE",
            reason="semantic_type_is_not_a_quantitative_measure",
            n_valid=n_valid,
            n_unique=n_unique,
            unique_ratio=unique_ratio,
        )
    if n_valid < 3:
        return SemanticEligibility(
            field=field,
            semantic_type=semantic_type,
            eligibility="BLOCKED",
            reason="fewer_than_three_valid_observations",
            n_valid=n_valid,
            n_unique=n_unique,
            unique_ratio=unique_ratio,
        )
    if unique_ratio > MAX_CONTINUOUS_UNIQUE_RATIO and n_valid >= MIN_CONTINUOUS_N:
        return SemanticEligibility(
            field=field,
            semantic_type=semantic_type,
            eligibility="PARTIAL",
            reason="high_unique_ratio_suggests_identifier_like_values",
            n_valid=n_valid,
            n_unique=n_unique,
            unique_ratio=unique_ratio,
        )
    return SemanticEligibility(
        field=field,
        semantic_type=semantic_type,
        eligibility="APPLICABLE",
        reason="quantitative_measure_with_usable_population",
        n_valid=n_valid,
        n_unique=n_unique,
        unique_ratio=unique_ratio,
    )


def continuous_density_eligibility(
    n_valid: int,
    n_unique: int,
    distinct_integer_ratio: float = 0.0,
) -> tuple[str, str]:
    if n_valid < MIN_CONTINUOUS_N:
        return (
            "NOT_APPLICABLE",
            f"kernel_density_requires_at_least_{MIN_CONTINUOUS_N}_observations",
        )
    if n_unique == n_valid:
        return (
            "NOT_APPLICABLE",
            "every_observation_is_unique_identifier_like_values",
        )
    if distinct_integer_ratio > 0.9 and n_unique < 12:
        return (
            "NOT_APPLICABLE",
            "discrete_low_cardinality_values_are_not_suitable_for_kernel_density",
        )
    return "APPLICABLE", "continuous_density_conditions_met"


def categorical_eligibility(
    n_valid: int,
    n_unique: int,
) -> SemanticEligibility:
    if n_valid < 3:
        return SemanticEligibility(
            field="",
            semantic_type=SemanticType.CATEGORICAL.value,
            eligibility="BLOCKED",
            reason="fewer_than_three_valid_observations",
            n_valid=n_valid,
            n_unique=n_unique,
            unique_ratio=0.0,
        )
    if n_unique > MAX_CATEGORICAL_CARDINALITY:
        return SemanticEligibility(
            field="",
            semantic_type=SemanticType.CATEGORICAL.value,
            eligibility="PARTIAL",
            reason="high_cardinality_requires_top_k_bucketing",
            n_valid=n_valid,
            n_unique=n_unique,
            unique_ratio=n_unique / n_valid if n_valid else 0.0,
        )
    if n_valid < MIN_CATEGORICAL_N:
        return SemanticEligibility(
            field="",
            semantic_type=SemanticType.CATEGORICAL.value,
            eligibility="PARTIAL",
            reason="small_sample_categories_are_descriptive_only",
            n_valid=n_valid,
            n_unique=n_unique,
            unique_ratio=n_unique / n_valid if n_valid else 0.0,
        )
    return SemanticEligibility(
        field="",
        semantic_type=SemanticType.CATEGORICAL.value,
        eligibility="APPLICABLE",
        reason="categorical_conditions_met",
        n_valid=n_valid,
        n_unique=n_unique,
        unique_ratio=n_unique / n_valid if n_valid else 0.0,
    )


def eligible_numeric_fields(
    entries: Sequence[Any],
) -> tuple[str, ...]:
    from schema.type_inference import parse_number

    eligible: list[str] = []
    for entry in entries:
        values = entry.values
        parsed = [parse_number(value) for value in values]
        valid = [value for value in parsed if value is not None]
        decision = numeric_measure_eligibility(
            field=entry.field,
            semantic_type=entry.semantic_type,
            n_valid=len(valid),
            n_unique=len(set(valid)),
        )
        if decision.eligibility in {"APPLICABLE", "PARTIAL"}:
            eligible.append(entry.field)
    return tuple(eligible)
