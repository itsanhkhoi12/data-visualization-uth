from __future__ import annotations

import re
import zipfile
from dataclasses import dataclass
from datetime import date, datetime, time
from pathlib import Path
from typing import Any, Iterator
from xml.etree.ElementTree import iterparse

MAIN_NS = "http://schemas.openxmlformats.org/spreadsheetml/2006/main"
REL_NS = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
PKG_REL_NS = "http://schemas.openxmlformats.org/package/2006/relationships"
TAG = f"{{{MAIN_NS}}}"
DIMENSION_PATTERN = re.compile(rb'<dimension[^>]*ref="([A-Z0-9:]+)"')
ROW_PATTERN = re.compile(rb"<row[ >]")
MERGE_PATTERN = re.compile(rb"<mergeCell ")
FORMULA_PATTERN = re.compile(rb"<f[ >/]")
CELL_REF_PATTERN = re.compile(r"^([A-Z]+)(\d+)$")
DATE_EPOCH_1900 = datetime(1899, 12, 30)
DATE_EPOCH_1904 = datetime(1904, 1, 1)


@dataclass(frozen=True)
class WorkbookSheetInfo:
    sheet_name: str
    sheet_state: str
    part_path: str
    dimension: str | None
    row_count: int
    max_column: int
    merged_range_count: int
    formula_cell_count: int
    header: tuple[str, ...]
    epoch: str


def column_index_from_ref(reference: str) -> int:
    match = CELL_REF_PATTERN.match(reference)
    if not match:
        return 0
    letters = match.group(1)
    index = 0
    for character in letters:
        index = index * 26 + (ord(character) - ord("A") + 1)
    return index


def column_letters(index: int) -> str:
    letters = ""
    while index > 0:
        index, remainder = divmod(index - 1, 26)
        letters = chr(ord("A") + remainder) + letters
    return letters


def _read_styles(archive: zipfile.ZipFile) -> list[str]:
    if "xl/styles.xml" not in archive.namelist():
        return []
    styles_xml = archive.read("xl/styles.xml").decode("utf-8", errors="replace")
    custom: dict[str, str] = {}
    for match in re.finditer(r"<numFmt\b[^>]*>", styles_xml):
        tag = match.group(0)
        id_match = re.search(r'numFmtId="([^"]+)"', tag)
        code_match = re.search(r'formatCode="([^"]*)"', tag)
        if id_match and code_match:
            custom[id_match.group(1)] = code_match.group(1)
    cell_xfs_block = ""
    match = re.search(r"<cellXfs\b.*?</cellXfs>", styles_xml, re.DOTALL)
    if match:
        cell_xfs_block = match.group(0)
    formats: list[str] = []
    for xf_match in re.finditer(r"<xf\b[^>]*>|<xf\b[^>]*/>", cell_xfs_block):
        tag = xf_match.group(0)
        id_match = re.search(r'numFmtId="([^"]+)"', tag)
        num_fmt_id = id_match.group(1) if id_match else "0"
        formats.append(custom.get(num_fmt_id, num_fmt_id))
    return formats


BUILTIN_DATE_FORMAT_IDS = {
    "14", "15", "16", "17", "18", "19", "20", "21", "22",
    "27", "30", "36", "45", "46", "47", "50", "57",
}
DATE_TOKEN_PATTERN = re.compile(r"[dmyhs]", re.IGNORECASE)


def _is_date_format(format_code: str) -> bool:
    if format_code in BUILTIN_DATE_FORMAT_IDS:
        return True
    if not format_code or format_code == "General":
        return False
    without_literals = re.sub(r'"[^"]*"', "", format_code)
    without_literals = re.sub(r"\[[^\]]*\]", "", without_literals)
    tokens = re.sub(r"[^dmyhsDMYHS]", "", without_literals)
    return bool(tokens) and bool(DATE_TOKEN_PATTERN.search(tokens))


def _read_shared_strings(archive: zipfile.ZipFile) -> list[str]:
    if "xl/sharedStrings.xml" not in archive.namelist():
        return []
    values: list[str] = []
    with archive.open("xl/sharedStrings.xml") as handle:
        for _, element in iterparse(handle, events=("end",)):
            if element.tag == f"{TAG}si":
                values.append(
                    "".join(
                        node.text or ""
                        for node in element.iter(f"{TAG}t")
                    )
                )
                element.clear()
    return values


def _read_workbook_sheet_order(archive: zipfile.ZipFile) -> list[tuple[str, str, str]]:
    workbook_xml = archive.read("xl/workbook.xml").decode("utf-8", errors="replace")
    relationships: dict[str, str] = {}
    if "xl/_rels/workbook.xml.rels" in archive.namelist():
        rels_xml = archive.read("xl/_rels/workbook.xml.rels").decode(
            "utf-8", errors="replace"
        )
        for match in re.finditer(r"<Relationship\b[^>]*>", rels_xml):
            tag = match.group(0)
            id_match = re.search(r'\bId="([^"]+)"', tag)
            target_match = re.search(r'\bTarget="([^"]+)"', tag)
            if not id_match or not target_match:
                continue
            relationships[id_match.group(1)] = target_match.group(1)
    entries: list[tuple[str, str, str]] = []
    for match in re.finditer(r"<sheet\b[^>]*>", workbook_xml):
        tag = match.group(0)
        name_match = re.search(r'\bname="([^"]*)"', tag)
        state_match = re.search(r'\bstate="([^"]*)"', tag)
        rel_match = re.search(r'r:id="([^"]*)"', tag)
        name = name_match.group(1) if name_match else ""
        state = state_match.group(1) if state_match else "visible"
        rel_id = rel_match.group(1) if rel_match else ""
        entries.append((name, state, _resolve_part_path(relationships.get(rel_id, ""))))
    return entries


def _resolve_part_path(target: str) -> str:
    if not target:
        return ""
    cleaned = target.replace("\\", "/")
    if cleaned.startswith("/"):
        return cleaned.lstrip("/")
    if cleaned.startswith("xl/"):
        return cleaned
    return f"xl/{cleaned}"


def _epoch_of(archive: zipfile.ZipFile) -> str:
    if "xl/workbook.xml" not in archive.namelist():
        return "1900"
    workbook_xml = archive.read("xl/workbook.xml").decode("utf-8", errors="replace")
    match = re.search(r'<workbookPr[^>]*date1904="([^"]+)"', workbook_xml)
    if match and match.group(1) in {"1", "true"}:
        return "1904"
    return "1900"


def _extract_first_row(archive: zipfile.ZipFile, part_path: str, shared: list[str]) -> tuple[str, ...]:
    header: list[str] = []
    with archive.open(part_path) as handle:
        for _, element in iterparse(handle, events=("end",)):
            if element.tag == f"{TAG}row":
                for cell in element.findall(f"{TAG}c"):
                    index = column_index_from_ref(str(cell.get("r") or "")) - 1
                    while len(header) <= index:
                        header.append("")
                    header[index] = _cell_text(cell, shared)
                element.clear()
                break
    return tuple(value.strip() for value in header)


def _detect_header_index_from_part(
    archive: zipfile.ZipFile, part_path: str, shared: list[str]
) -> tuple[str, ...]:
    probe: list[tuple[Any, ...]] = []
    with archive.open(part_path) as handle:
        for _, element in iterparse(handle, events=("end",)):
            if element.tag != f"{TAG}row":
                continue
            cells: list[Any] = []
            for cell in element.findall(f"{TAG}c"):
                index = column_index_from_ref(str(cell.get("r") or "")) - 1
                while len(cells) <= index:
                    cells.append(None)
                cell_type = cell.get("t")
                if cell_type == "inlineStr":
                    node = cell.find(f"{TAG}is")
                    cells[index] = (
                        "".join(text.text or "" for text in node.iter(f"{TAG}t"))
                        if node is not None
                        else None
                    )
                else:
                    value_node = cell.find(f"{TAG}v")
                    raw = value_node.text if value_node is not None else None
                    if raw is None:
                        cells[index] = None
                    elif cell_type == "s":
                        try:
                            cells[index] = shared[int(raw)]
                        except (ValueError, IndexError):
                            cells[index] = None
                    else:
                        cells[index] = raw
            element.clear()
            probe.append(tuple(cells))
            if len(probe) >= HEADER_PROBE_ROWS:
                break
    if not probe:
        return ()
    index = _detect_header_index(probe)
    return tuple(
        "" if cell is None else str(cell).strip() for cell in probe[index]
    )


def _cell_text(cell: Any, shared: list[str]) -> str:
    cell_type = cell.get("t")
    if cell_type == "inlineStr":
        node = cell.find(f"{TAG}is")
        if node is not None:
            return "".join(text.text or "" for text in node.iter(f"{TAG}t"))
    value_node = cell.find(f"{TAG}v")
    if value_node is None or value_node.text is None:
        return ""
    raw = value_node.text
    if cell_type == "s":
        try:
            return shared[int(raw)]
        except (ValueError, IndexError):
            return ""
    return raw


def inspect_workbook_fast(path: Path) -> list[WorkbookSheetInfo]:
    results: list[WorkbookSheetInfo] = []
    with zipfile.ZipFile(path) as archive:
        shared = _read_shared_strings(archive)
        epoch = _epoch_of(archive)
        for name, state, part_path in _read_workbook_sheet_order(archive):
            if not part_path or part_path not in archive.namelist():
                continue
            payload = archive.read(part_path)
            dimension_match = DIMENSION_PATTERN.search(payload)
            dimension = dimension_match.group(1).decode("ascii") if dimension_match else None
            row_count = len(ROW_PATTERN.findall(payload))
            merged_count = len(MERGE_PATTERN.findall(payload))
            formula_count = len(FORMULA_PATTERN.findall(payload))
            max_column = 0
            if dimension and ":" in dimension:
                tail = dimension.split(":")[-1]
                max_column = column_index_from_ref(tail)
            header = _detect_header_index_from_part(archive, part_path, shared)
            results.append(
                WorkbookSheetInfo(
                    sheet_name=name,
                    sheet_state=state,
                    part_path=part_path,
                    dimension=dimension,
                    row_count=row_count,
                    max_column=max_column,
                    merged_range_count=merged_count,
                    formula_cell_count=formula_count,
                    header=header,
                    epoch=epoch,
                )
            )
    return results


def _convert_number(raw: str, epoch: str, is_date_format: bool) -> Any:
    try:
        value = float(raw)
    except ValueError:
        return raw
    if not is_date_format:
        if value.is_integer() and abs(value) < 1e15:
            return int(value)
        return value
    base = DATE_EPOCH_1904 if epoch == "1904" else DATE_EPOCH_1900
    if 1 <= value <= 2958465:
        return base + __import__("datetime").timedelta(days=value)
    return value


def iter_sheet_rows(
    path: Path,
    sheet_name: str,
    max_rows: int | None = None,
    skip_rows: int = 0,
) -> Iterator[tuple[Any, ...]]:
    with zipfile.ZipFile(path) as archive:
        shared = _read_shared_strings(archive)
        epoch = _epoch_of(archive)
        formats = _read_styles(archive)
        target_part = ""
        for name, _state, part_path in _read_workbook_sheet_order(archive):
            if name == sheet_name:
                target_part = part_path
                break
        if not target_part:
            return
        emitted = 0
        skipped = 0
        with archive.open(target_part) as handle:
            for _, element in iterparse(handle, events=("end",)):
                if element.tag != f"{TAG}row":
                    continue
                if skipped < skip_rows:
                    skipped += 1
                    element.clear()
                    continue
                cells: list[Any] = []
                for cell in element.findall(f"{TAG}c"):
                    reference = str(cell.get("r") or "")
                    index = column_index_from_ref(reference) - 1
                    while len(cells) <= index:
                        cells.append(None)
                    cell_type = cell.get("t")
                    if cell_type == "inlineStr":
                        node = cell.find(f"{TAG}is")
                        cells[index] = (
                            "".join(text.text or "" for text in node.iter(f"{TAG}t"))
                            if node is not None
                            else None
                        )
                        continue
                    value_node = cell.find(f"{TAG}v")
                    if value_node is None or value_node.text is None:
                        cells[index] = None
                        continue
                    raw = value_node.text
                    if cell_type == "s":
                        try:
                            cells[index] = shared[int(raw)]
                        except (ValueError, IndexError):
                            cells[index] = None
                    elif cell_type == "str":
                        cells[index] = raw
                    elif cell_type == "b":
                        cells[index] = raw == "1"
                    elif cell_type == "e":
                        cells[index] = raw
                    else:
                        style_index = cell.get("s")
                        date_format = False
                        if style_index is not None:
                            try:
                                format_code = formats[int(style_index)]
                            except (ValueError, IndexError):
                                format_code = ""
                            date_format = _is_date_format(format_code)
                        cells[index] = _convert_number(raw, epoch, date_format)
                element.clear()
                yield tuple(cells)
                emitted += 1
                if max_rows is not None and emitted >= max_rows:
                    return


HEADER_PROBE_ROWS = 8


def _row_texts(raw_row: tuple[Any, ...]) -> tuple[str, ...]:
    return tuple("" if cell is None else str(cell).strip() for cell in raw_row)


def _header_score(texts: tuple[str, ...]) -> float:
    filled = [text for text in texts if text]
    if len(filled) < 2:
        return 0.0
    distinct = len({text.lower() for text in filled})
    numeric_like = sum(
        1 for text in filled if _looks_numeric(text)
    )
    date_like = sum(
        1 for text in filled if _looks_like_date(text)
    )
    metadata_like = sum(
        1 for text in filled if _looks_like_metadata(text)
    )
    score = 0.55 * (len(filled) / max(len(texts), 1))
    score += 0.45 * (distinct / len(filled))
    score -= 0.30 * (numeric_like / len(filled))
    score -= 0.35 * (date_like / len(filled))
    score -= 0.60 * (metadata_like / len(filled))
    return score


def _looks_numeric(text: str) -> bool:
    if not text:
        return False
    stripped = text.replace(".", "").replace(",", "").replace("-", "").strip()
    if not stripped:
        return False
    return stripped.isdigit()


_DATE_SEPARATORS = ("/", "-", ".")


def _looks_like_date(text: str) -> bool:
    if not text:
        return False
    parts = text.split()
    if len(parts) != 1:
        return False
    token = parts[0]
    for separator in _DATE_SEPARATORS:
        if separator in token:
            chunks = token.split(separator)
            if len(chunks) in (2, 3) and all(chunk.isdigit() for chunk in chunks):
                return True
    return False


def _looks_like_metadata(text: str) -> bool:
    if not text:
        return False
    lowered = text.lower()
    if ":" in text or "=" in text:
        return True
    markers = (
        "kỳ báo cáo",
        "ky bao cao",
        "kênh bán",
        "kenh ban",
        "tất cả",
        "tat ca",
        "lựa chọn",
        "bộ lọc",
        "đơn vị: ",
        "từ ngày",
        "đến ngày",
    )
    return any(marker in lowered for marker in markers)


def _detect_header_index(rows: list[tuple[Any, ...]]) -> int:
    best_index = 0
    best_score = -1.0
    for index, row in enumerate(rows[:HEADER_PROBE_ROWS]):
        score = _header_score(_row_texts(row))
        if score > best_score:
            best_score = score
            best_index = index
    return best_index


def read_sheet_rows_fast(
    path: Path, sheet_name: str, max_rows: int | None = None
) -> tuple[tuple[str, ...], list[dict[str, Any]], int]:
    iterator = iter_sheet_rows(path, sheet_name)
    probe: list[tuple[Any, ...]] = []
    try:
        for raw_row in iterator:
            probe.append(raw_row)
            if len(probe) >= HEADER_PROBE_ROWS:
                break
    except StopIteration:
        pass
    if not probe:
        return (), [], 0
    header_index = _detect_header_index(probe)
    header = tuple(
        "" if cell is None else str(cell).strip() for cell in probe[header_index]
    )
    if not any(header):
        return (), [], 0
    rows: list[dict[str, Any]] = []
    for raw_row in probe[header_index + 1 :]:
        _append_row(rows, header, raw_row)
        if max_rows is not None and len(rows) >= max_rows:
            return header, rows, len(rows)
    for raw_row in iterator:
        _append_row(rows, header, raw_row)
        if max_rows is not None and len(rows) >= max_rows:
            break
    return header, rows, len(rows)


def _append_row(
    rows: list[dict[str, Any]], header: tuple[str, ...], raw_row: tuple[Any, ...]
) -> None:
    if all(cell is None or str(cell).strip() == "" for cell in raw_row):
        return
    record: dict[str, Any] = {}
    for index, name in enumerate(header):
        if not name:
            continue
        record[name] = raw_row[index] if index < len(raw_row) else None
    rows.append(record)


def sheet_row_count(path: Path, sheet_name: str) -> int:
    for info in inspect_workbook_fast(path):
        if info.sheet_name == sheet_name:
            return info.row_count
    return 0


def detect_sheet_header_index(path: Path, sheet_name: str) -> int:
    iterator = iter_sheet_rows(path, sheet_name)
    probe: list[tuple[Any, ...]] = []
    for raw_row in iterator:
        probe.append(raw_row)
        if len(probe) >= HEADER_PROBE_ROWS:
            break
    if not probe:
        return 0
    return _detect_header_index(probe)


def to_python_date(value: Any) -> date | None:
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value
    if isinstance(value, time):
        return None
    return None
