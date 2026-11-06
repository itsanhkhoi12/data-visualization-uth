from __future__ import annotations

import html
import re
from dataclasses import dataclass
from typing import Any, Mapping, Sequence

from common.contracts import TableSpecification
from common.enums import Status

MAX_CELL_CHARACTERS = 400
MAX_ROWS = 5000
MAX_TOTAL_CHARACTERS = 2_000_000
NON_FINITE_TEXT = ("nan", "inf", "infinity", "-infinity")
EVENT_HANDLER_PATTERN = re.compile(r"\bon([a-zA-Z]+)(\s*)\=")

BASE_CSS = """
.eda-table-wrap { width: 100%; overflow-x: auto; margin: 0 0 1.2em 0; }
.eda-table { border-collapse: collapse; width: 100%; font-family: -apple-system, Segoe UI, Helvetica, Arial, sans-serif; font-size: 12px; color: #1f2733; }
.eda-table caption { caption-side: top; text-align: left; font-weight: 600; font-size: 13px; padding: 0 0 6px 0; color: #1f2733; }
.eda-table caption .eda-table-subtitle { display: block; font-weight: 400; font-size: 11px; color: #55606f; padding-top: 3px; }
.eda-table th, .eda-table td { border: 1px solid #d9dee5; padding: 4px 8px; text-align: left; vertical-align: top; }
.eda-table thead th { background: #eef2f7; font-weight: 600; white-space: nowrap; }
.eda-table tbody tr:nth-child(even) { background: #f8fafc; }
.eda-table td.eda-num { text-align: right; font-variant-numeric: tabular-nums; }
.eda-table td.eda-text { text-align: left; }
.eda-table-caption-note { display: block; font-size: 11px; color: #55606f; padding-top: 6px; }
"""


@dataclass(frozen=True)
class RenderedTable:
    table_id: str
    html: str
    row_count: int
    column_count: int
    truncated: bool
    status: Status
    reason: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "table_id": self.table_id,
            "row_count": self.row_count,
            "column_count": self.column_count,
            "truncated": self.truncated,
            "status": self.status.value,
            "reason": self.reason,
        }


def _format_cell(value: Any, precision: int | None) -> str:
    if value is None:
        return ""
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, float):
        if value != value:
            return ""
        if value in (float("inf"), float("-inf")):
            return ""
        if precision is not None:
            return f"{value:.{precision}f}"
        return f"{value:.6g}"
    if isinstance(value, int):
        return str(value)
    return str(value)


def _cell_class(column: str, values: Sequence[Any]) -> str:
    numeric = sum(
        1 for value in values if isinstance(value, (int, float)) and not isinstance(value, bool)
    )
    if values and numeric == len(values):
        return "eda-num"
    return "eda-text"


def _escape(text: str) -> str:
    return html.escape(text, quote=True)


def _contains_markup(text: str) -> bool:
    return "<" in text or ">" in text


def _neutralize_event_handlers(text: str) -> str:
    return EVENT_HANDLER_PATTERN.sub(lambda match: f"on{match.group(1)}{match.group(2)}&#61;", text)


def _truncate(text: str) -> tuple[str, bool]:
    if len(text) <= MAX_CELL_CHARACTERS:
        return text, False
    return text[: MAX_CELL_CHARACTERS - 3] + "...", True


def render_table(
    frame: Mapping[str, Any],
    spec: TableSpecification,
    include_css: bool = True,
) -> RenderedTable:
    rows = list(frame.get("rows", []))
    columns: list[str] = []
    for candidate in spec.required_columns:
        if candidate in frame:
            columns.append(candidate)
    for candidate in frame:
        if candidate != "rows" and candidate not in columns:
            columns.append(candidate)
    if not columns:
        observed: list[str] = []
        for row in rows:
            for key in row:
                if key not in observed:
                    observed.append(key)
        for candidate in spec.required_columns:
            if candidate not in columns and candidate in observed:
                columns.append(candidate)
        for candidate in observed:
            if candidate not in columns:
                columns.append(candidate)
    truncated = False
    if len(rows) > MAX_ROWS:
        rows = rows[:MAX_ROWS]
        truncated = True
    total_characters = 0
    safe_rows: list[list[str]] = []
    for row in rows:
        cells: list[str] = []
        for column in columns:
            raw = row.get(column)
            text = _format_cell(raw, spec.precision.get(column))
            text = _neutralize_event_handlers(text)
            text, cell_truncated = _truncate(text)
            if cell_truncated:
                truncated = True
            total_characters += len(text)
            cells.append(text)
        safe_rows.append(cells)
    if total_characters > MAX_TOTAL_CHARACTERS:
        keep = max(1, int(len(safe_rows) * MAX_TOTAL_CHARACTERS / total_characters))
        safe_rows = safe_rows[:keep]
        truncated = True
    column_values = {column: [row.get(column) for row in rows] for column in columns}
    header_cells = "".join(
        f'<th scope="col">{_escape(column)}</th>' for column in columns
    )
    body_rows: list[str] = []
    for cells in safe_rows:
        parts: list[str] = []
        for column, text in zip(columns, cells):
            parts.append(
                f'<td class="{_cell_class(column, column_values[column])}">'
                f"{_escape(text)}</td>"
            )
        body_rows.append("<tr>" + "".join(parts) + "</tr>")
    caption_parts = [
        f'<span class="eda-table-title">{_escape(spec.title)}</span>',
    ]
    if spec.subtitle:
        caption_parts.append(
            f'<span class="eda-table-subtitle">{_escape(spec.subtitle)}</span>'
        )
    caption_parts.append(
        f'<span class="eda-table-caption-note">{_escape(spec.caption)}</span>'
    )
    style_block = f"<style>{BASE_CSS}</style>" if include_css else ""
    body = (
        f'<div class="eda-table-wrap"><table class="eda-table">'
        f'<caption>{"".join(caption_parts)}</caption>'
        f"<thead><tr>{header_cells}</tr></thead>"
        f"<tbody>{''.join(body_rows)}</tbody>"
        f"</table></div>"
    )
    payload = style_block + body
    if not columns:
        return RenderedTable(
            table_id=spec.table_id,
            html=payload,
            row_count=0,
            column_count=0,
            truncated=False,
            status=Status.NOT_APPLICABLE,
            reason="no columns resolved",
        )
    if not safe_rows:
        return RenderedTable(
            table_id=spec.table_id,
            html=payload,
            row_count=0,
            column_count=len(columns),
            truncated=False,
            status=Status.PASS,
            reason="no rows available",
        )
    unsafe = any(
        _contains_markup(cell) for row in safe_rows for cell in row
    )
    return RenderedTable(
        table_id=spec.table_id,
        html=payload,
        row_count=len(safe_rows),
        column_count=len(columns),
        truncated=truncated,
        status=Status.PASS,
        reason="rendered_escaped" if unsafe else "rendered",
    )


def render_table_from_rows(
    records: Sequence[Mapping[str, Any]],
    spec: TableSpecification,
    include_css: bool = True,
) -> RenderedTable:
    return render_table({"rows": list(records)}, spec, include_css=include_css)
