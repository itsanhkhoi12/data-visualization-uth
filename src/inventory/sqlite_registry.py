from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from common.contracts import SourceRecord
from common.enums import Status
from readers.sqlite_reader import inspect_sqlite


@dataclass(frozen=True)
class SqliteRegistryEntry:
    source_id: str
    split: str
    business_id: str
    database_path: str
    database_hash: str
    object_type: str
    object_name: str
    column_count: int
    column_names: tuple[str, ...]
    primary_key: tuple[str, ...]
    foreign_key_count: int
    index_count: int
    row_count: int | None
    status: Status
    integrity: str

    def to_dict(self) -> dict[str, object]:
        return {
            "source_id": self.source_id,
            "split": self.split,
            "business_id": self.business_id,
            "database_path": self.database_path,
            "database_hash": self.database_hash,
            "object_type": self.object_type,
            "object_name": self.object_name,
            "column_count": self.column_count,
            "column_names": list(self.column_names),
            "primary_key": list(self.primary_key),
            "foreign_key_count": self.foreign_key_count,
            "index_count": self.index_count,
            "row_count": self.row_count,
            "status": self.status.value,
            "integrity": self.integrity,
        }


@dataclass(frozen=True)
class SqliteRegistry:
    split: str
    entries: tuple[SqliteRegistryEntry, ...]
    database_count: int
    table_count: int
    view_count: int
    error_paths: tuple[str, ...]

    def to_dict(self) -> dict[str, object]:
        return {
            "split": self.split,
            "entries": [entry.to_dict() for entry in self.entries],
            "database_count": self.database_count,
            "table_count": self.table_count,
            "view_count": self.view_count,
            "error_paths": list(self.error_paths),
        }


def build_sqlite_registry(records: tuple[SourceRecord, ...], split: str) -> SqliteRegistry:
    entries: list[SqliteRegistryEntry] = []
    errors: list[str] = []
    database_count = 0
    for record in records:
        if record.source_type != "sqlite":
            continue
        database_count += 1
        path = Path(record.absolute_path)
        try:
            objects = inspect_sqlite(path)
        except Exception as error:
            errors.append(f"{record.logical_path}:{type(error).__name__}")
            continue
        for database_object in objects:
            entries.append(
                SqliteRegistryEntry(
                    source_id=f"{record.source_id}#table={database_object.name}",
                    split=split,
                    business_id=record.business_id,
                    database_path=record.logical_path,
                    database_hash=record.content_hash,
                    object_type=database_object.object_type,
                    object_name=database_object.name,
                    column_count=len(database_object.columns),
                    column_names=tuple(
                        str(column["name"]) for column in database_object.columns
                    ),
                    primary_key=database_object.primary_key,
                    foreign_key_count=database_object.foreign_key_count,
                    index_count=database_object.index_count,
                    row_count=database_object.row_count,
                    status=Status.PASS,
                    integrity="not_checked",
                )
            )
    return SqliteRegistry(
        split=split,
        entries=tuple(entries),
        database_count=database_count,
        table_count=sum(1 for entry in entries if entry.object_type == "table"),
        view_count=sum(1 for entry in entries if entry.object_type == "view"),
        error_paths=tuple(errors),
    )
