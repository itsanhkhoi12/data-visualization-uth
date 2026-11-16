from __future__ import annotations

from pathlib import Path

import pytest

from readers.csv_reader import detect_delimiter, detect_encoding, inspect_csv
from readers.jsonl_reader import iterate_jsonl, profile_json_schema
from readers.markdown_reader import extract_table_rules, parse_markdown
from readers.sqlite_reader import connect_readonly, inspect_sqlite


def test_t007_utf8_bom_roundtrip(tmp_path: Path) -> None:
    path = tmp_path / "bom.csv"
    path.write_text("mã hàng,số lượng\nA01,3\n", encoding="utf-8-sig")
    inspection = inspect_csv(path)
    assert inspection.bom_present is True
    assert inspection.header == ("mã hàng", "số lượng")
    assert detection_is_stable(inspection.encoding)


def detection_is_stable(encoding: str) -> bool:
    return encoding in {"utf-8-sig", "utf-8"}


def test_t008_quoted_commas_and_newlines(tmp_path: Path) -> None:
    path = tmp_path / "quoted.csv"
    path.write_text(
        'name,note\n"A, B","line one\nline two"\n', encoding="utf-8"
    )
    inspection = inspect_csv(path)
    assert inspection.data_row_count == 1
    assert inspection.ragged_row_count == 0


def test_t009_semicolon_and_decimal_comma(tmp_path: Path) -> None:
    path = tmp_path / "locale.csv"
    path.write_text("a;b\n1,5;2\n", encoding="utf-8")
    assert detect_delimiter(path.read_text(encoding="utf-8")) == ";"
    inspection = inspect_csv(path)
    assert inspection.delimiter == ";"


def test_t010_repeated_header_row_is_flagged(tmp_path: Path) -> None:
    path = tmp_path / "repeated.csv"
    path.write_text("a,b\n1,2\na,b\n", encoding="utf-8")
    inspection = inspect_csv(path)
    assert inspection.repeated_header_count == 1
    assert "repeated_header_rows_present" in inspection.warnings


def test_t015_sqlite_is_read_only(tmp_path: Path) -> None:
    import sqlite3

    path = tmp_path / "db.sqlite"
    connection = sqlite3.connect(path)
    connection.execute("CREATE TABLE items (id INTEGER PRIMARY KEY, name TEXT)")
    connection.execute("INSERT INTO items (name) VALUES ('a')")
    connection.commit()
    connection.close()
    readonly = connect_readonly(path)
    try:
        with pytest.raises(sqlite3.OperationalError):
            readonly.execute("INSERT INTO items (name) VALUES ('b')")
    finally:
        readonly.close()


def test_t016_sqlite_registry_lists_keys_and_indexes(tmp_path: Path) -> None:
    import sqlite3

    path = tmp_path / "db2.sqlite"
    connection = sqlite3.connect(path)
    connection.execute(
        "CREATE TABLE orders (id INTEGER PRIMARY KEY, code TEXT UNIQUE)"
    )
    connection.execute("CREATE INDEX idx_code ON orders(code)")
    connection.execute("CREATE TABLE lines (id INTEGER, order_id INTEGER)")
    connection.commit()
    connection.close()
    objects = {item.name: item for item in inspect_sqlite(path)}
    assert "orders" in objects
    assert objects["orders"].primary_key == ("id",)
    assert objects["orders"].index_count >= 1


def test_t043_malformed_jsonl_is_counted(tmp_path: Path) -> None:
    path = tmp_path / "questions.jsonl"
    path.write_text(
        '{"id": "q1"}\nnot json\n{"id": "q2"}\n', encoding="utf-8"
    )
    profile = profile_json_schema(path)
    assert profile.record_count == 2
    assert profile.malformed_line_count == 1
    records = iterate_jsonl(path)
    assert len(records) == 2


def test_markdown_table_rules_are_extracted(tmp_path: Path) -> None:
    path = tmp_path / "rulebook.md"
    path.write_text(
        "# Rules\n\n## Revenue\n\n| Rule | Description |\n|---|---|\n"
        "| R-01 | Revenue equals sum of line totals |\n",
        encoding="utf-8",
    )
    document = parse_markdown(path)
    rules = extract_table_rules(document)
    assert rules
    assert rules[0][1] == "R-01"


def test_encoding_detection_prefers_utf8_sig(tmp_path: Path) -> None:
    path = tmp_path / "enc.csv"
    path.write_bytes("cột,giá\n1,2\n".encode("utf-8-sig"))
    assert detect_encoding(path.read_bytes()) == "utf-8-sig"
