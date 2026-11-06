from __future__ import annotations

from quality.duplicates import profile_duplicates
from quality.findings import compile_findings, findings_summary
from quality.integrity import profile_integrity
from quality.missingness import classify_null_kind, profile_missingness
from quality.validity import mask_value, profile_validity
from readers.table_reader import LoadedTable
from schema.relations import profile_relation


def _table(header, rows, source_id="train:biz_x:orders") -> LoadedTable:
    return LoadedTable(
        source_id=source_id,
        split="train",
        business_id="biz_x",
        object_name="orders",
        header=tuple(header),
        rows=[dict(zip(header, row)) for row in rows],
        total_row_count=len(rows),
        truncated=False,
    )


def test_t022_structural_missing_is_separated() -> None:
    assert classify_null_kind("mã khách lẻ", "identifier") == "structural_missing"
    assert classify_null_kind("ghi chú", "text") == "structural_missing"
    assert classify_null_kind("thành tiền", "amount") == "unknown"


def test_t022_missingness_counts_and_ratio() -> None:
    table = _table(["a", "b"], [[1, "x"], [None, "y"], [3, None]])
    entries = profile_missingness(table, {"a": "measure", "b": "text"})
    by_column = {entry.column: entry for entry in entries}
    assert by_column["a"].n_missing == 1
    assert by_column["a"].n_total == 3
    assert round(by_column["a"].missing_ratio, 4) == round(1 / 3, 4)


def test_t023_exact_and_business_key_duplicates_are_distinct() -> None:
    table = _table(["code", "value"], [["a", 1], ["a", 1], ["a", 2]])
    entries = profile_duplicates(table, ("code",))
    classes = {entry.duplicate_class: entry for entry in entries}
    assert "exact_row" in classes
    assert "business_key" in classes
    assert classes["business_key"].n_duplicate_rows == 2


def test_t024_negative_values_are_not_auto_invalid() -> None:
    table = _table(["thành tiền"], [["-50"], ["100"]])
    entries = profile_validity(table, {"thành tiền": "amount"})
    assert all(entry.rule_id != "VAL.NUM.PARSE" for entry in entries)


def test_t025_status_domain_violation_is_evidenced() -> None:
    table = _table(["trạng thái"], [["ok"], ["broken"], ["ok"]])
    entries = profile_validity(table, {"trạng thái": "categorical"})
    assert all(entry.evidence for entry in entries)


def test_mask_value_hides_interior_characters() -> None:
    assert mask_value("0912345678") == "0********8"
    assert mask_value("ab") == "**"


def test_findings_compile_and_summarize() -> None:
    table = _table(["a"], [[1], [None], [3]])
    missing = profile_missingness(table, {"a": "measure"})
    duplicates = profile_duplicates(table)
    validity = profile_validity(table, {"a": "measure"})
    findings = compile_findings(missing, duplicates, validity, ())
    assert findings
    summary = findings_summary(findings)
    assert summary["total"] == len(findings)
    assert "by_severity" in summary


def test_integrity_reports_fanout_risk() -> None:
    left = _table(["id"], [["1"], ["2"]])
    right = _table(["id"], [["1"], ["1"], ["2"]], "train:biz_x:lines")
    evidence = profile_relation(left, right, ("id",), "train", "biz_x")
    entries = profile_integrity([evidence])
    kinds = {entry.integrity_kind for entry in entries}
    assert "fanout_risk" in kinds
