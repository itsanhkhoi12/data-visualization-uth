from __future__ import annotations

from statistics.bivariate import profile_bivariate
from statistics.categorical import (
    CategoricalProfileRequest,
    alias_candidates_for_field,
    profile_categorical,
    top_k_with_others,
)
from statistics.multivariate import profile_multivariate
from statistics.numeric import (
    NumericProfileRequest,
    empirical_cdf,
    histogram_bins,
    profile_numeric,
)


def _numeric_request(values) -> NumericProfileRequest:
    return NumericProfileRequest(
        source_id="train:biz_x:orders",
        split="train",
        business_id="biz_x",
        field="thành tiền",
        unit="VND",
        values=values,
        total_n=len(values),
    )


def test_t026_numeric_statistics_match_reference() -> None:
    values = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    stats = profile_numeric(_numeric_request(values))
    assert stats.mean == 5.5
    assert stats.median == 5.5
    assert stats.variance is not None
    assert stats.q25 is not None
    assert stats.q75 is not None
    assert stats.n_valid == 10
    assert stats.n_missing == 0


def test_t026_unparseable_values_are_missing_not_zero() -> None:
    stats = profile_numeric(_numeric_request([1, "abc", 3]))
    assert stats.n_valid == 2
    assert stats.n_missing == 1
    assert stats.mean == 2.0


def test_t027_zero_inflation_is_reported() -> None:
    stats = profile_numeric(_numeric_request([0, 0, 0, 0, 5]))
    assert stats.zero_ratio == 0.8
    assert "high_zero_inflation" in stats.warnings


def test_t030_categorical_aliases_are_not_merged() -> None:
    values = ["Cafe", "cafe", "Café", "Tea"]
    entries = profile_categorical(
        CategoricalProfileRequest(
            source_id="train:biz_x:orders",
            split="train",
            business_id="biz_x",
            field="món",
            values=values,
            total_n=len(values),
        )
    )
    labels = {entry.category for entry in entries}
    assert "Cafe" in labels
    assert "cafe" in labels
    assert alias_candidates_for_field(values)


def test_top_k_with_others_keeps_total() -> None:
    values = [f"c{index}" for index in range(30)]
    entries = profile_categorical(
        CategoricalProfileRequest(
            source_id="train:biz_x:orders",
            split="train",
            business_id="biz_x",
            field="món",
            values=values,
            total_n=len(values),
        )
    )
    reduced = top_k_with_others(entries, top_k=5)
    assert len(reduced) == 6
    assert reduced[-1].category == "Others"
    assert sum(entry.count for entry in reduced) == 30


def test_t029_correlation_is_blocked_without_verified_grain() -> None:
    rows = [{"a": 1, "b": 2}, {"a": 2, "b": 4}, {"a": 3, "b": 6}]
    result = profile_bivariate(
        "train:biz_x:orders",
        "train",
        "biz_x",
        "a",
        "b",
        rows,
        grain_verified=False,
    )
    assert result.status.value == "BLOCKED"
    assert result.pearson_r is None


def test_multivariate_requires_two_fields() -> None:
    result = profile_multivariate(
        "train:biz_x:orders", "train", "biz_x", ["a"], [{"a": 1}]
    )
    assert result.status.value == "NOT APPLICABLE"


def test_histogram_and_cdf_cover_the_population() -> None:
    values = [float(index) for index in range(100)]
    edges, counts = histogram_bins(values, 10)
    assert len(edges) == 11
    assert sum(counts) == 100
    xs, ys = empirical_cdf(values)
    assert ys[-1] == 1.0
    assert len(xs) == len(ys) == 100


def test_histogram_of_constant_values_keeps_edge_count_aligned() -> None:
    edges, counts = histogram_bins([5.0, 5.0, 5.0], 20)
    assert len(edges) == len(counts) + 1
    assert sum(counts) == 3


def test_num01_frame_labels_match_bin_count() -> None:
    from visualization.chart_frames import build_num01

    frame = build_num01(
        split="train",
        business_id="biz_101",
        field="thành tiền",
        edges=[5.0, 5.0],
        counts=[3],
        population_n=3,
        source_id="train:biz_101:orders",
    )
    assert len(frame.frame["labels"]) == len(frame.frame["values"])
