from __future__ import annotations

from dataclasses import replace
from pathlib import Path
from types import SimpleNamespace

from common.bundles import SplitBundle
from common.enums import Status
from html_tables.table_renderer import render_table, render_table_from_rows
from html_tables.table_specs import (
    TABLE_CATALOGUE,
    TABLE_SPECS_BY_ID,
    validate_all_table_specs,
    validate_table_spec,
)
from orchestration.pipeline import _render_charts
from orchestration.visualization_pipeline import VisualizationRun, _render_chart_data
from reporting.artifact_registry import ArtifactWriter
from reporting.visualization_registry import VisualizationRegistry
from validation.visual_qa import validate_html_export, validate_visuals
from visualization.chart_data import ChartData
from visualization.chart_frames import FrameRegistry, build_num01
from visualization.chart_specs import (
    CHART_CATALOGUE,
    CHART_SPECS_BY_ID,
    validate_all_chart_specs,
    validate_chart_spec,
)


def test_rendered_variants_preserve_distinct_files_and_hashes(tmp_path: Path) -> None:
    legacy_path = tmp_path / "figures/example/public_test/dev_001/NUM01.png"
    legacy_path.parent.mkdir(parents=True)
    legacy_path.write_bytes(b"legacy figure")
    data = ChartData(
        chart_id="NUM01",
        split="public_test",
        business_id="dev_001",
        kind="bar",
        payload={"labels": ["A"], "values": [2]},
        source_ids=("file:first",),
        population_n=2,
        sample_n=None,
        method="count",
        unit="row",
        denominator_label="rows",
        title="First field",
        x_label="Group",
        y_label="Rows",
        metadata={"caption": "First field"},
    )
    run = VisualizationRun("example", tmp_path, VisualizationRegistry(run_id="example"))
    bundle = SplitBundle(split="public_test")
    first = _render_chart_data(run, bundle, data)
    second = _render_chart_data(
        run, bundle, replace(data, title="Second field", source_ids=("file:second",))
    )
    assert first.figure_id != second.figure_id
    assert first.png_path != second.png_path
    assert first.svg_path != second.svg_path
    assert legacy_path.read_bytes() == b"legacy figure"
    assert not validate_visuals((first, second), tmp_path).failures()

    (tmp_path / first.png_path).write_bytes((tmp_path / second.png_path).read_bytes())
    failures = validate_visuals((first, second), tmp_path).failures()
    assert [item.check_id for item in failures] == [f"VIS-FILE-{first.figure_id}"]


def test_legacy_chart_variants_have_distinct_manifest_files(tmp_path: Path) -> None:
    frames = FrameRegistry()
    for field in ("first", "second"):
        frames.add(build_num01("public_test", "dev_001", field, [0, 1], [2], 2, field))
    run = SimpleNamespace(
        run_id="example", output_root=tmp_path, frames=frames, rendered_charts=[]
    )
    writer = ArtifactWriter("example", tmp_path, {}, "", "")
    _render_charts(run, writer)
    manifest = tmp_path / "chart_manifest/example/public_test/dev_001"
    assert {file.name for file in manifest.glob("*.json")} == {"NUM01.json", "NUM01-2.json"}
    assert len({entry.artifact_id for entry in writer.entries}) == 2


def test_empty_table_shows_status_and_passes_structure_check() -> None:
    table = render_table_from_rows([], TABLE_CATALOGUE[0])
    assert "<table" not in table.html
    assert "Không có dữ liệu cho bảng này." in table.html
    payload = {**table.to_dict(), "html": table.html}
    assert not validate_html_export({table.table_id: {"public_test": payload}}).failures()


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
    assert len(TABLE_CATALOGUE) == 19


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
