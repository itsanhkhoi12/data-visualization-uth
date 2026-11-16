from __future__ import annotations

import sqlite3
from dataclasses import dataclass
from pathlib import Path
from typing import Any

READ_ONLY_TIMEOUT_SECONDS = 30.0


@dataclass(frozen=True)
class SqliteObject:
    database: str
    object_type: str
    name: str
    sql: str | None
    columns: tuple[dict[str, Any], ...]
    primary_key: tuple[str, ...]
    foreign_keys: tuple[dict[str, Any], ...]
    indexes: tuple[dict[str, Any], ...]
    row_count: int | None
    index_count: int = 0
    column_count: int = 0
    foreign_key_count: int = 0

    def to_dict(self) -> dict[str, Any]:
        return {
            "database": self.database,
            "object_type": self.object_type,
            "name": self.name,
            "sql": self.sql,
            "columns": list(self.columns),
            "primary_key": list(self.primary_key),
            "foreign_keys": list(self.foreign_keys),
            "indexes": list(self.indexes),
            "row_count": self.row_count,
            "index_count": self.index_count,
            "column_count": self.column_count,
            "foreign_key_count": self.foreign_key_count,
        }


def connect_readonly(path: Path) -> sqlite3.Connection:
    uri = f"file:{path.resolve().as_posix()}?mode=ro"
    connection = sqlite3.connect(uri, uri=True, timeout=READ_ONLY_TIMEOUT_SECONDS)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA query_only=ON")
    return connection


def quote_identifier(name: str) -> str:
    return '"' + name.replace('"', '""') + '"'


def inspect_sqlite(path: Path, count_rows: bool = True) -> list[SqliteObject]:
    connection = connect_readonly(path)
    try:
        cursor = connection.execute(
            "SELECT type, name, sql FROM sqlite_master "
            "WHERE name NOT LIKE 'sqlite_%' ORDER BY type, name"
        )
        results: list[SqliteObject] = []
        for object_type, name, sql in cursor.fetchall():
            quoted = quote_identifier(name)
            columns = tuple(
                dict(row)
                for row in connection.execute(f"PRAGMA table_info({quoted})").fetchall()
            )
            primary_key = tuple(
                str(column["name"])
                for column in sorted(
                    columns, key=lambda item: item.get("pk") or 0
                )
                if column.get("pk")
            )
            foreign_keys = tuple(
                dict(row)
                for row in connection.execute(
                    f"PRAGMA foreign_key_list({quoted})"
                ).fetchall()
            )
            indexes = tuple(
                dict(row)
                for row in connection.execute(f"PRAGMA index_list({quoted})").fetchall()
            )
            row_count: int | None = None
            if count_rows and object_type == "table":
                row_count = int(
                    connection.execute(
                        f"SELECT COUNT(*) FROM {quoted}"
                    ).fetchone()[0]
                )
            results.append(
                SqliteObject(
                    database=str(path),
                    object_type=object_type,
                    name=name,
                    sql=sql,
                    columns=columns,
                    primary_key=primary_key,
                    foreign_keys=foreign_keys,
                    indexes=indexes,
                    row_count=row_count,
                    index_count=len(indexes),
                    column_count=len(columns),
                    foreign_key_count=len(foreign_keys),
                )
            )
        return results
    finally:
        connection.close()


def query_readonly(
    path: Path, sql: str, parameters: tuple[Any, ...] = ()
) -> list[dict[str, Any]]:
    connection = connect_readonly(path)
    try:
        cursor = connection.execute(sql, parameters)
        return [dict(row) for row in cursor.fetchall()]
    finally:
        connection.close()


def integrity_check(path: Path) -> str:
    connection = connect_readonly(path)
    try:
        row = connection.execute("PRAGMA integrity_check").fetchone()
        return str(row[0]) if row else "unknown"
    finally:
        connection.close()
