from __future__ import annotations

import codecs
import csv
import io
from dataclasses import dataclass
from pathlib import Path

ENCODING_CANDIDATES = ("utf-8-sig", "utf-8", "cp1258", "cp1252", "latin-1")
SNIFF_BYTES = 65_536
NULL_TOKENS = {"", "na", "n/a", "nan", "null", "none", "-", "--"}


@dataclass(frozen=True)
class CsvInspection:
    path: Path
    encoding: str
    delimiter: str
    header: tuple[str, ...]
    data_row_count: int
    total_row_count: int
    blank_row_count: int
    repeated_header_count: int
    ragged_row_count: int
    duplicate_header_count: int
    bom_present: bool
    warnings: tuple[str, ...]

    def to_dict(self) -> dict[str, object]:
        return {
            "path": str(self.path),
            "encoding": self.encoding,
            "delimiter": self.delimiter,
            "header": list(self.header),
            "data_row_count": self.data_row_count,
            "total_row_count": self.total_row_count,
            "blank_row_count": self.blank_row_count,
            "repeated_header_count": self.repeated_header_count,
            "ragged_row_count": self.ragged_row_count,
            "duplicate_header_count": self.duplicate_header_count,
            "bom_present": self.bom_present,
            "warnings": list(self.warnings),
        }


def detect_encoding(raw: bytes) -> str:
    for candidate in ENCODING_CANDIDATES:
        try:
            codecs.decode(raw, candidate)
        except (UnicodeDecodeError, LookupError):
            continue
        return candidate
    return "latin-1"


def detect_delimiter(sample: str) -> str:
    try:
        dialect = csv.Sniffer().sniff(sample, delimiters=",;\t|")
        return dialect.delimiter
    except csv.Error:
        counts = {candidate: sample.count(candidate) for candidate in (",", ";", "\t", "|")}
        best = max(counts, key=lambda key: counts[key])
        return best if counts[best] > 0 else ","


def read_text(path: Path, encoding: str | None = None) -> str:
    raw = path.read_bytes()
    resolved = encoding or detect_encoding(raw)
    return raw.decode(resolved, errors="replace")


def is_null_token(value: str) -> bool:
    return value.strip().lower() in NULL_TOKENS


def inspect_csv(path: Path, encoding: str | None = None) -> CsvInspection:
    raw = path.read_bytes()
    bom_present = raw.startswith(codecs.BOM_UTF8)
    resolved_encoding = encoding or detect_encoding(raw)
    text = raw.decode(resolved_encoding, errors="replace")
    delimiter = detect_delimiter(text[:SNIFF_BYTES])
    warnings: list[str] = []
    reader = csv.reader(io.StringIO(text, newline=""), delimiter=delimiter)
    rows: list[list[str]] = []
    for row in reader:
        rows.append(row)
    if not rows:
        return CsvInspection(
            path=path,
            encoding=resolved_encoding,
            delimiter=delimiter,
            header=(),
            data_row_count=0,
            total_row_count=0,
            blank_row_count=0,
            repeated_header_count=0,
            ragged_row_count=0,
            duplicate_header_count=0,
            bom_present=bom_present,
            warnings=("empty_file",),
        )
    header = tuple(cell.strip() for cell in rows[0])
    body = rows[1:]
    blank = sum(1 for row in body if not any(cell.strip() for cell in row))
    repeated = sum(1 for row in body if row and tuple(cell.strip() for cell in row) == header)
    expected = len(header)
    ragged = sum(1 for row in body if row and len(row) != expected)
    duplicate_headers = len(header) - len(set(header))
    if repeated:
        warnings.append("repeated_header_rows_present")
    if ragged:
        warnings.append("ragged_rows_present")
    if duplicate_headers:
        warnings.append("duplicate_header_names")
    if bom_present:
        warnings.append("utf8_bom_present")
    return CsvInspection(
        path=path,
        encoding=resolved_encoding,
        delimiter=delimiter,
        header=header,
        data_row_count=len(body) - blank - repeated,
        total_row_count=len(body),
        blank_row_count=blank,
        repeated_header_count=repeated,
        ragged_row_count=ragged,
        duplicate_header_count=duplicate_headers,
        bom_present=bom_present,
        warnings=tuple(warnings),
    )


def iterate_csv(
    path: Path,
    encoding: str | None = None,
    delimiter: str | None = None,
    chunk_size: int = 50_000,
) -> tuple[tuple[str, ...], list[dict[str, str]]]:
    raw = path.read_bytes()
    resolved_encoding = encoding or detect_encoding(raw)
    text = raw.decode(resolved_encoding, errors="replace")
    resolved_delimiter = delimiter or detect_delimiter(text[:SNIFF_BYTES])
    reader = csv.DictReader(
        io.StringIO(text, newline=""), delimiter=resolved_delimiter
    )
    header = tuple((name or "").strip() for name in (reader.fieldnames or ()))
    rows: list[dict[str, str]] = []
    for record in reader:
        if record is None:
            continue
        cleaned = {key.strip(): value for key, value in record.items() if key is not None}
        if not any((value or "").strip() for value in cleaned.values()):
            continue
        rows.append(cleaned)
        if len(rows) >= chunk_size:
            break
    return header, rows


def read_all_csv_rows(
    path: Path, encoding: str | None = None, delimiter: str | None = None
) -> tuple[tuple[str, ...], list[dict[str, str]]]:
    raw = path.read_bytes()
    resolved_encoding = encoding or detect_encoding(raw)
    text = raw.decode(resolved_encoding, errors="replace")
    resolved_delimiter = delimiter or detect_delimiter(text[:SNIFF_BYTES])
    reader = csv.DictReader(
        io.StringIO(text, newline=""), delimiter=resolved_delimiter
    )
    header = tuple((name or "").strip() for name in (reader.fieldnames or ()))
    rows: list[dict[str, str]] = []
    for record in reader:
        if record is None:
            continue
        cleaned = {key.strip(): value for key, value in record.items() if key is not None}
        if not any((value or "").strip() for value in cleaned.values()):
            continue
        rows.append(cleaned)
    return header, rows
