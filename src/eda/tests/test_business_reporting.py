from __future__ import annotations

from pathlib import Path

import pytest

from business.business_inventory import BusinessProfile
from business.business_chart_metrics import compute_business_metric_rows
from business.domain_profiles import profile_business_domain
from business.kpi_catalogue import build_kpi_catalogue
from business.unit_mapping import validate_unit_mapping
from common.enums import Status
from cross_business.aggregate import aggregate_business_profiles, combine_global_profiles
from cross_business.schema_compare import compare_schemas, detect_field_role
from common.contracts import ColumnProfile
from readers.table_reader import LoadedTable
from reporting.business_report import assemble_business_report
from reporting.global_report import assemble_global_report


def _profile(business_id: str = "biz_101") -> BusinessProfile:
    from business.business_inventory import BusinessSourceEntry

    return BusinessProfile(
        business_id=business_id,
        split="train",
        source_count=1,
        sources=(
            BusinessSourceEntry(
                logical_path="a.csv",
                source_type="csv",
                size_bytes=1,
                content_hash="h",
            ),
        ),
        readme_present=True,
        readme_title="Biz",
        readme_line_count=10,
        readme_hash="h",
        documented_files=("a.csv",),
        documented_conventions=(),
        domain_evidence="retail_grocery",
        status=Status.PASS,
    )


def test_business_report_counts_and_status() -> None:
    report = assemble_business_report(
        profile=_profile(),
        worksheet_count=2,
        database_object_count=1,
        column_count=5,
        metrics=(),
        findings=(),
        diagnostics=(),
        max_missing_ratio=0.25,
    )
    assert report.coverage_status == "PASS"
    assert report.max_missing_ratio == 0.25
    assert report.worksheet_count == 2


def test_business_report_is_partial_without_readme() -> None:
    profile = _profile()
    profile = type(profile)(**{**profile.__dict__, "readme_present": False})
    report = assemble_business_report(profile=profile)
    assert report.coverage_status == "PARTIAL"
    assert "readme_missing_domain_unresolved" in report.notes


def test_domain_profile_requires_readme_evidence() -> None:
    diagnostics = profile_business_domain(_profile())
    assert diagnostics
    assert diagnostics[-1].domain == "retail_grocery"


def test_kpi_catalogue_blocks_unsupported_metrics() -> None:
    metrics = build_kpi_catalogue(
        split="train",
        business_id="biz_101",
        available_evidence=("order_header",),
        rule_registry=None,
    )
    blocked = [item for item in metrics if item.formula_status == Status.BLOCKED]
    assert blocked


def test_unit_mapping_detects_conflicts() -> None:
    registry = validate_unit_mapping(
        split="train",
        business_id="biz_101",
        rows=[
            {"item": "A", "source_unit": "kg", "base_unit": "kg"},
            {"item": "A", "source_unit": "tấn", "base_unit": "kg"},
        ],
        item_column="item",
        source_unit_column="source_unit",
        base_unit_column="base_unit",
    )
    assert registry.status == Status.PARTIAL
    assert registry.conflicting_items == ("A",)


def test_t046_missing_business_report_is_partial() -> None:
    profiles = [_profile("biz_101"), _profile("biz_102")]
    global_profile = aggregate_business_profiles(
        split="train",
        profiles=profiles,
        findings=(),
        total_source_files=2,
        total_business_data_files=2,
    )
    report = assemble_global_report(global_profile, ())
    assert report.covered_business_count == 0
    assert report.status == Status.PARTIAL
    assert "business_report_coverage_incomplete" in report.notes


def test_global_profile_denominator_reconciliation() -> None:
    profiles = [_profile("biz_101"), _profile("biz_102")]
    global_profile = aggregate_business_profiles(
        split="train",
        profiles=profiles,
        findings=(),
        total_source_files=10,
        total_business_data_files=8,
    )
    assert global_profile.business_count == 2
    assert (
        global_profile.pass_count
        + global_profile.partial_count
        + global_profile.blocked_count
        + global_profile.not_applicable_count
        == global_profile.business_count
    )


def test_combine_global_profiles_keeps_boundary_statement() -> None:
    train = aggregate_business_profiles(
        "train", (_profile(),), (), 1, 1
    )
    public = aggregate_business_profiles(
        "public_test", (_profile("dev_001"),), (), 1, 1
    )
    combined = combine_global_profiles(train, public)
    assert "cross_split_boundary" in combined
    assert combined["train"]["business_count"] == 1
    assert combined["public_test"]["business_count"] == 1


def test_combine_global_profiles_single_split() -> None:
    public = aggregate_business_profiles(
        "public_test", (_profile("dev_001"),), (), 1, 1
    )
    combined = combine_global_profiles(profiles={"public_test": public})
    assert "public_test" in combined
    assert combined["public_test"]["business_count"] == 1
    assert "cross_split_boundary" not in combined


def test_t047_same_name_different_grain_is_not_comparable() -> None:
    profiles = (
        ColumnProfile(
            source_id="train:biz_101:orders",
            split="train",
            business_id="biz_101",
            column="mã hóa đơn",
            physical_type="text",
            semantic_type="identifier",
            unit=None,
            non_null_n=10,
            null_n=0,
            distinct_n=10,
            parse_failure_n=0,
            confidence=1.0,
        ),
    )
    entries = compare_schemas(profiles)
    assert entries
    assert entries[0].field_role == "order_identifier"


def test_detect_field_role() -> None:
    assert detect_field_role("Mã hóa đơn") == "order_identifier"
    assert detect_field_role("Số lượng") == "quantity"
    assert detect_field_role("cột ngẫu nhiên") is None


def test_global_report_has_science_limitations() -> None:
    train = aggregate_business_profiles("train", (_profile(),), (), 1, 1)
    report = assemble_global_report(train, (assemble_business_report(_profile()),))
    assert report.science_limitations
    assert any("transaction" in item for item in report.science_limitations)


def test_scientific_conclusions_cite_evidence() -> None:
    from reporting.scientific_review import derive_scientific_conclusions

    train = aggregate_business_profiles("train", (_profile(),), (), 1, 1)
    business_reports = (assemble_business_report(_profile()),)
    conclusions = derive_scientific_conclusions(
        train,
        business_reports,
        extra_evidence={"relation_candidate_count": 12},
    )
    assert conclusions
    for item in conclusions:
        assert item.claim
        assert item.evidence
        assert item.split == "train"
        assert item.finding_id.startswith("SCI")
    ids = [item.finding_id for item in conclusions]
    assert len(ids) == len(set(ids))


def test_global_report_exposes_scientific_conclusions() -> None:
    from reporting.scientific_review import derive_scientific_conclusions

    train = aggregate_business_profiles("train", (_profile(),), (), 1, 1)
    business_reports = (assemble_business_report(_profile()),)
    scientific = derive_scientific_conclusions(train, business_reports)
    report = assemble_global_report(
        train,
        business_reports,
        conclusions=[item.claim for item in scientific],
        scientific_conclusions=scientific,
    )
    payload = report.to_dict()
    assert payload["conclusions"]
    assert payload["scientific_conclusions"]
    assert payload["scientific_conclusions"][0]["evidence"]


def test_kpi_catalogue_matches_diacritic_rulebook_labels() -> None:
    from business.kpi_catalogue import _match_rule

    class _Rule:
        rule_id = "train.x"
        rule_label = "Số đơn"
        rule_text = "chỉ tính đơn không huỷ"

    class _Registry:
        rules = (_Rule(),)

    assert _match_rule(_Registry(), ("so don",)) == "train.x"


def test_kpi_catalogue_uses_real_role_vocabulary() -> None:
    metrics = build_kpi_catalogue(
        split="train",
        business_id="biz_101",
        available_evidence=(
            "order_identifier",
            "order_status",
            "order_date",
            "amount",
            "quantity",
            "item_identifier",
        ),
        rule_registry=None,
    )
    by_id = {item.metric_id.rsplit(".", 1)[-1]: item for item in metrics}
    assert by_id["revenue"].formula_status != Status.BLOCKED
    assert by_id["order_count"].formula_status != Status.BLOCKED


def test_detect_field_role_handles_unaccented_camel_case_headers() -> None:
    assert detect_field_role("MaHoaDon") == "order_identifier"
    assert detect_field_role("TinhTrang") == "order_status"
    assert detect_field_role("TongTienHang") == "amount"
    assert detect_field_role("MaHangHoa") == "item_identifier"
    assert detect_field_role("NgayLap") == "order_date"
    assert detect_field_role("DonViTinh") == "unit"


def test_detect_field_role_requires_token_boundaries() -> None:
    assert detect_field_role("cột ngẫu nhiên") is None
    assert detect_field_role("Mô tả sản phẩm") != "order_identifier"


def test_revenue_deduplicates_lines_and_filters_entire_orders() -> None:
    header = ("Mã đơn hàng", "Ngày", "Trạng thái", "Thành tiền")
    rows = [
        dict(zip(header, values))
        for values in (
            ("A", "01/05/2026", "Hoàn thành", 100),
            ("A", "01/05/2026", "Hoàn thành", 100),
            ("B", "01/05/2026", "Đã hủy đơn", 500),
            ("C", "01/05/2026", "Hoàn thành", 40),
            ("C", "01/05/2026", "Đã trả hàng", 50),
            ("D", "01/05/2026", "Đang giao hàng", 20),
            ("D", "", "", 30),
            ("E", "01/05/2026", "Hoàn thành", None),
            ("", "01/05/2026", "Hoàn thành", 900),
        )
    ]
    table = LoadedTable("fixture", "public_test", "dev_001", "sales", header, rows, len(rows), False)
    metrics = {row.metric_id: row for row in compute_business_metric_rows(table)}
    assert metrics["BUS01"].payload["amounts"] == [100, 50]
    assert metrics["BUS02"].payload["daily"] == {"2026-05-01": 150}
    assert metrics["BUS02"].population_n == 2
    assert metrics["BUS04"].population_n == 5


def test_invoice_summary_uses_merchandise_value() -> None:
    rows = [
        {
            "Mã hóa đơn": "A",
            "Ngày tháng": "2026-05-01 00:00:00",
            "Trạng thái đơn": "Xong",
            "TongTien": 999,
            "Giá trị hàng": 100,
        }
    ]
    table = LoadedTable(
        "fixture", "public_test", "dev_009", "danh_sach_hoa_don.csv",
        tuple(rows[0]), rows, 1, False,
    )
    metrics = {row.metric_id: row for row in compute_business_metric_rows(table)}
    assert metrics["BUS01"].payload["amounts"] == [100]
    assert metrics["BUS02"].payload["daily"] == {"2026-05-01": 100}
