from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from common.contracts import SourceRecord
from common.errors import SourceReadError
from readers.csv_reader import read_all_csv_rows
from readers.excel_reader import read_sheet_rows
from readers.sqlite_reader import connect_readonly


@dataclass(frozen=True)
class LoadedTable:
    source_id: str
    split: str
    business_id: str
    object_name: str
    header: tuple[str, ...]
    rows: list[dict[str, Any]]
    total_row_count: int | None
    truncated: bool

    @property
    def row_count(self) -> int:
        return len(self.rows)

    def column(self, name: str) -> list[Any]:
        return [row.get(name) for row in self.rows]

    def values(self, name: str) -> list[Any]:
        return self.column(name)

    def to_dict(self) -> dict[str, Any]:
        return {
            "source_id": self.source_id,
            "split": self.split,
            "business_id": self.business_id,
            "object_name": self.object_name,
            "header": list(self.header),
            "row_count": self.row_count,
            "total_row_count": self.total_row_count,
            "truncated": self.truncated,
        }


def load_csv_table(record: SourceRecord, max_rows: int | None = None) -> LoadedTable:
    path = Path(record.absolute_path)
    header, rows = read_all_csv_rows(path)
    total = len(rows)
    truncated = False
    if max_rows is not None and total > max_rows:
        rows = rows[:max_rows]
        truncated = True
    return LoadedTable(
        source_id=record.source_id,
        split=record.split,
        business_id=record.business_id,
        object_name=path.name,
        header=header,
        rows=rows,
        total_row_count=total,
        truncated=truncated,
    )


def load_excel_table(
    record: SourceRecord, sheet_name: str, max_rows: int | None = None
) -> LoadedTable:
    from readers.xlsx_fast import detect_sheet_header_index, sheet_row_count

    path = Path(record.absolute_path)
    header, rows = read_sheet_rows(path, sheet_name, max_rows=max_rows)
    sheet_rows = sheet_row_count(path, sheet_name)
    header_index = detect_sheet_header_index(path, sheet_name)
    total = max(sheet_rows - header_index - 1, 0) if sheet_rows else None
    truncated = max_rows is not None and total is not None and total > len(rows)
    return LoadedTable(
        source_id=f"{record.source_id}#sheet={sheet_name}",
        split=record.split,
        business_id=record.business_id,
        object_name=sheet_name,
        header=header,
        rows=rows,
        total_row_count=total,
        truncated=truncated,
    )


def load_sqlite_table(
    record: SourceRecord, table_name: str, max_rows: int | None = None
) -> LoadedTable:
    path = Path(record.absolute_path)
    connection = connect_readonly(path)
    try:
        quoted = '"' + table_name.replace('"', '""') + '"'
        columns = tuple(
            str(row[1]) for row in connection.execute(f"PRAGMA table_info({quoted})")
        )
        total = int(connection.execute(f"SELECT COUNT(*) FROM {quoted}").fetchone()[0])
        limit_clause = "" if max_rows is None else f" LIMIT {int(max_rows)}"
        cursor = connection.execute(f"SELECT * FROM {quoted}{limit_clause}")
        rows = [
            {name: value for name, value in zip(columns, record_row)}
            for record_row in cursor.fetchall()
        ]
    finally:
        connection.close()
    truncated = max_rows is not None and total > max_rows
    return LoadedTable(
        source_id=f"{record.source_id}#table={table_name}",
        split=record.split,
        business_id=record.business_id,
        object_name=table_name,
        header=columns,
        rows=rows,
        total_row_count=total,
        truncated=truncated,
    )


def load_table(
    record: SourceRecord,
    sheet_name: str | None = None,
    table_name: str | None = None,
    max_rows: int | None = None,
) -> LoadedTable:
    try:
        if record.source_type == "csv":
            return load_csv_table(record, max_rows=max_rows)
        if record.source_type == "xlsx":
            if sheet_name is None:
                raise SourceReadError(f"sheet name required for {record.source_id}")
            return load_excel_table(record, sheet_name, max_rows=max_rows)
        if record.source_type == "sqlite":
            if table_name is None:
                raise SourceReadError(f"table name required for {record.source_id}")
            return load_sqlite_table(record, table_name, max_rows=max_rows)
    except SourceReadError:
        raise
    except Exception as error:
        raise SourceReadError(
            f"failed to read {record.source_id}: {type(error).__name__}: {error}"
        ) from error
    raise SourceReadError(f"unsupported source type: {record.source_type}")
