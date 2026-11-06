from __future__ import annotations

from pathlib import Path

from common.enums import Status
from html_tables.table_renderer import render_table, render_table_from_rows
from html_tables.table_specs import (
    TABLE_CATALOGUE,
    TABLE_SPECS_BY_ID,
    validate_all_table_specs,
    validate_table_spec,
)
from visualization.chart_specs import (
    CHART_CATALOGUE,
    CHART_SPECS_BY_ID,
    validate_all_chart_specs,
    validate_chart_spec,
)


def test_t048_chart_specs_are_valid() -> None:
    validations = validate_all_chart_specs()
    assert all(item.valid for item in validations)
    assert len(validations) == len(CHART_CATALOGUE)


def test_chart_spec_validation_detects_missing_fields() -> None:
    spec = CHART_CATALOGUE[0]
    broken = type(spec)(
        chart_id=spec.chart_id,
        research_question="",
        chart_type=spec.chart_type,
        x_label="",
        y_label="",
        unit="",
        owner_module="",
        split="both",
        business_id="global",
        inputs=(),
        calculations="",
        output_relpath="",
        caption="",
    )
    validation = validate_chart_spec(broken)
    assert validation.valid is False
    assert validation.status == Status.BLOCKED
    assert "missing_research_question" in validation.reasons


def test_t051_injected_script_is_escaped() -> None:
    spec = TABLE_SPECS_BY_ID["TBL02"]
    rows = [
        {
            "source_id": "<script>alert('x')</script>",
            "split": "train",
            "business_id": "biz_101",
            "source_type": "csv",
            "logical_path": "<img onerror=alert(1)>.csv",
            "size_bytes": 10,
            "content_hash": "sha256:abc",
            "status": "PASS",
        }
    ]
    rendered = render_table_from_rows(rows, spec)
    assert "<script>" not in rendered.html
    assert "onerror=alert" not in rendered.html
    assert "&lt;script&gt;" in rendered.html
    assert rendered.status == Status.PASS


def test_t052_nan_and_infinity_are_bounded() -> None:
    spec = TABLE_SPECS_BY_ID["TBL09"]
    rows = [
        {
            "source_id": "s",
            "field": "f",
            "n_valid": 1,
            "mean": float("nan"),
            "median": float("inf"),
            "std": None,
            "q25": 1.0,
            "q75": 2.0,
            "unit": "VND",
        }
    ]
    rendered = render_table_from_rows(rows, spec)
    assert "nan" not in rendered.html.lower()
    assert "inf" not in rendered.html.lower()


def test_t053_source_frame_is_not_mutated() -> None:
    spec = TABLE_SPECS_BY_ID["TBL09"]
    rows = [
        {
            "source_id": "s",
            "field": "f",
            "n_valid": 1,
            "mean": 1.5,
            "median": 1.5,
            "std": 0.0,
            "q25": 1.5,
            "q75": 1.5,
            "unit": "VND",
        }
    ]
    snapshot = [dict(row) for row in rows]
    render_table_from_rows(rows, spec)
    assert rows == snapshot


def test_t051_table_accessibility_headers() -> None:
    spec = TABLE_SPECS_BY_ID["TBL02"]
    rendered = render_table_from_rows(
        [
            {
                "source_id": "s",
                "split": "train",
                "business_id": "b",
                "source_type": "csv",
                "logical_path": "a.csv",
                "size_bytes": 1,
                "content_hash": "h",
                "status": "PASS",
            }
        ],
        spec,
    )
    assert '<th scope="col">' in rendered.html
    assert "<caption>" in rendered.html


def test_table_specs_are_valid() -> None:
    validations = validate_all_table_specs()
    assert all(item.valid for item in validations)
    assert len(TABLE_CATALOGUE) == 20


def test_table_spec_validation_detects_missing_fields() -> None:
    spec = TABLE_SPECS_BY_ID["TBL01"]
    broken = type(spec)(
        table_id="TBLXX",
        title="",
        subtitle="",
        caption="",
        input_artifact="",
        required_columns=(),
        grain="",
        owner_module="",
    )
    validation = validate_table_spec(broken)
    assert validation.valid is False
    assert "missing_caption" in validation.reasons


def test_table_renderer_bounds_rows() -> None:
    spec = TABLE_SPECS_BY_ID["TBL02"]
    rows = [
        {
            "source_id": f"s{index}",
            "split": "train",
            "business_id": "b",
            "source_type": "csv",
            "logical_path": "a.csv",
            "size_bytes": 1,
            "content_hash": "h",
            "status": "PASS",
        }
        for index in range(20)
    ]
    rendered = render_table_from_rows(rows, spec)
    assert rendered.row_count == 20
    assert rendered.column_count >= 8


def test_chart_renderer_supports_every_chart_type(tmp_path: Path) -> None:
    from visualization.chart_renderer import render_chart

    frames = {
        "bar": {"labels": ["a", "b"], "values": [1.0, 2.0]},
        "grouped_bar": {
            "labels": ["a", "b"],
            "values": [1.0, 2.0],
            "series": [{"label": "s1", "values": [1.0, 2.0]}],
        },
        "horizontal_bar": {"labels": ["a", "b"], "values": [1.0, 2.0]},
        "stacked_bar": {
            "labels": ["a", "b"],
            "values": [1.0, 2.0],
            "series": [{"label": "s1", "values": [1.0, 2.0]}],
        },
        "histogram": {"labels": [], "values": [1.0, 2.0, 3.0], "bins": 3},
        "ecdf": {"labels": [1.0, 2.0], "values": [0.5, 1.0]},
        "boxplot": {
            "labels": ["g1"],
            "values": [1.0, 2.0],
            "groups": [[1.0, 2.0, 3.0]],
        },
        "violin": {
            "labels": ["g1"],
            "values": [1.0, 2.0],
            "groups": [[1.0, 2.0, 3.0]],
        },
        "scatter": {"labels": [], "values": [], "x": [1.0, 2.0], "y": [3.0, 4.0]},
        "heatmap": {
            "matrix": [[1.0, 0.0]],
            "rows": ["r1"],
            "columns": ["c1", "c2"],
        },
        "dot": {"labels": ["a"], "values": [1.0]},
        "line": {"labels": ["a", "b"], "values": [1.0, 2.0]},
        "timeline": {"labels": ["a"], "values": [1.0]},
    }
    rendered_count = 0
    for spec in CHART_CATALOGUE:
        frame = frames.get(spec.chart_type)
        if frame is None:
            continue
        target = tmp_path / f"{spec.chart_id}.png"
        rendered = render_chart(frame, spec, target)
        assert rendered.status == Status.PASS, f"{spec.chart_id}: {rendered.reason}"
        assert target.exists()
        rendered_count += 1
    assert rendered_count >= 10
