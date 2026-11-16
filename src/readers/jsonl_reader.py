from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class JsonlProfile:
    path: Path
    record_count: int
    blank_line_count: int
    malformed_line_count: int
    malformed_line_numbers: tuple[int, ...]
    key_types: dict[str, str]
    key_presence: dict[str, int]
    id_values: tuple[str, ...]
    duplicate_id_count: int
    sample_records: tuple[dict[str, Any], ...]
    warnings: tuple[str, ...]

    def to_dict(self) -> dict[str, Any]:
        return {
            "path": str(self.path),
            "record_count": self.record_count,
            "blank_line_count": self.blank_line_count,
            "malformed_line_count": self.malformed_line_count,
            "malformed_line_numbers": list(self.malformed_line_numbers),
            "key_types": dict(self.key_types),
            "key_presence": dict(self.key_presence),
            "id_values": list(self.id_values),
            "duplicate_id_count": self.duplicate_id_count,
            "sample_records": [dict(record) for record in self.sample_records],
            "warnings": list(self.warnings),
        }


def _type_name(value: Any) -> str:
    if value is None:
        return "null"
    if isinstance(value, bool):
        return "boolean"
    if isinstance(value, int):
        return "integer"
    if isinstance(value, float):
        return "number"
    if isinstance(value, str):
        return "string"
    if isinstance(value, list):
        return "array"
    if isinstance(value, dict):
        return "object"
    return "unknown"


def iterate_jsonl(path: Path, limit: int | None = None) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, start=1):
            stripped = line.strip()
            if not stripped:
                continue
            try:
                payload = json.loads(stripped)
            except json.JSONDecodeError:
                continue
            if isinstance(payload, dict):
                records.append(payload)
            if limit is not None and len(records) >= limit:
                break
    return records


def profile_json_schema(path: Path, sample_size: int = 5) -> JsonlProfile:
    record_count = 0
    blank_lines = 0
    malformed: list[int] = []
    key_types: dict[str, str] = {}
    key_presence: dict[str, int] = {}
    samples: list[dict[str, Any]] = []
    id_values: list[str] = []
    with path.open("r", encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, start=1):
            stripped = line.strip()
            if not stripped:
                blank_lines += 1
                continue
            try:
                payload = json.loads(stripped)
            except json.JSONDecodeError:
                malformed.append(line_number)
                continue
            if not isinstance(payload, dict):
                malformed.append(line_number)
                continue
            record_count += 1
            if len(samples) < sample_size:
                samples.append(payload)
            for key, value in payload.items():
                key_presence[key] = key_presence.get(key, 0) + 1
                observed = _type_name(value)
                if key not in key_types:
                    key_types[key] = observed
                elif key_types[key] != observed:
                    key_types[key] = "mixed"
            identifier = payload.get("id")
            if identifier is not None:
                id_values.append(str(identifier))
    duplicate_ids = len(id_values) - len(set(id_values))
    warnings: list[str] = []
    if malformed:
        warnings.append("malformed_lines_present")
    if duplicate_ids:
        warnings.append("duplicate_ids_present")
    for key, presence in key_presence.items():
        if presence != record_count:
            warnings.append(f"optional_key:{key}")
    return JsonlProfile(
        path=path,
        record_count=record_count,
        blank_line_count=blank_lines,
        malformed_line_count=len(malformed),
        malformed_line_numbers=tuple(malformed[:20]),
        key_types=key_types,
        key_presence=key_presence,
        id_values=tuple(id_values),
        duplicate_id_count=duplicate_ids,
        sample_records=tuple(samples),
        warnings=tuple(warnings),
    )
