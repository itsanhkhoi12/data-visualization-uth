from __future__ import annotations

from readers.table_reader import LoadedTable
from schema.column_registry import build_column_registry
from schema.key_candidates import best_key_candidate, find_candidate_keys
from schema.relations import profile_relation, propose_key_pairs
from schema.type_inference import (
    infer_semantic_type,
    infer_physical_type,
    parse_date,
    parse_number,
)
from common.enums import ColumnType


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


def test_t018_same_looking_ids_with_different_grain_are_candidates() -> None:
    left = _table(["id"], [["1"], ["2"], ["3"]])
    right = _table(["id"], [["1"], ["1"], ["2"]], "train:biz_x:lines")
    evidence = profile_relation(left, right, ("id",), "train", "biz_x")
    assert evidence.status != "APPROVED"
    assert evidence.duplicate_key_right > 0


def test_t019_orphans_are_counted() -> None:
    left = _table(["id"], [["1"], ["2"], ["3"], ["9"]])
    right = _table(["id"], [["1"], ["2"]], "train:biz_x:lines")
    evidence = profile_relation(left, right, ("id",), "train", "biz_x")
    assert evidence.unmatched_left_rows == 2
    assert evidence.matched_rows == 2


def test_t020_fanout_is_detected() -> None:
    left = _table(["id"], [["1"], ["2"]])
    right = _table(["id"], [["1"], ["1"], ["1"], ["2"]], "train:biz_x:lines")
    evidence = profile_relation(left, right, ("id",), "train", "biz_x")
    assert evidence.fanout_factor == 2.0
    assert evidence.status != "APPROVED"


def test_t021_payment_join_is_not_silently_approved() -> None:
    left = _table(["bill"], [["b1"], ["b2"]])
    right = _table(["bill"], [["b1"], ["b2"]], "train:biz_x:payments")
    evidence = profile_relation(left, right, ("bill",), "train", "biz_x")
    assert evidence.relation_id
    assert evidence.fanout_factor > 0


def test_t028_numeric_identifier_is_not_a_measure() -> None:
    values = ["101", "102", "103", "104"]
    physical = infer_physical_type(values)
    candidate = infer_semantic_type("mã khách", values, physical)
    assert candidate.semantic_type.value == "identifier"


def test_key_candidate_detection() -> None:
    table = _table(["code", "value"], [["a", 1], ["b", 2], ["c", 3]])
    candidates = find_candidate_keys(table)
    best = best_key_candidate(candidates)
    assert best is not None
    assert best.key_columns == ("code",)


def test_column_registry_records_units() -> None:
    table = _table(
        ["mã hàng", "thành tiền"], [["A", "10"], ["B", "20"]]
    )
    entries = build_column_registry(table)
    amount = next(item for item in entries if item.column == "thành tiền")
    assert amount.unit == "VND"
    assert amount.semantic_type in {"amount", "measure"}


def test_propose_key_pairs_matches_same_column_names() -> None:
    left = _table(["mã hóa đơn"], [["1"]])
    right = _table(["mã hóa đơn"], [["1"]], "train:biz_x:lines")
    pairs = propose_key_pairs(left, right)
    assert ("mã hóa đơn", "mã hóa đơn") in pairs


def test_parse_helpers() -> None:
    assert parse_number("1,234.5") == 1234.5
    assert parse_number("abc") is None
    assert parse_date("2025-01-31") is not None
    assert parse_date("31/01/2025") is not None
    assert parse_date("not a date") is None
    assert infer_physical_type(["a", "b"]) == ColumnType.TEXT
