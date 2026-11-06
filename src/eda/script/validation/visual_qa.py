from __future__ import annotations

import re
from pathlib import Path
from typing import Any, Mapping, Sequence

from common.enums import Status
from validation.validation_contracts import ValidationCheck, ValidationLedger

REMOTE_URL_PATTERN = re.compile(
    r"(?:src|href)\s*=\s*[\"']\s*(?:https?:)?//", re.IGNORECASE
)
EVENT_HANDLER_PATTERN = re.compile(r"\son[a-zA-Z]+\s*=\s*[\"']", re.IGNORECASE)
SCRIPT_TAG_PATTERN = re.compile(r"<script", re.IGNORECASE)
PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"
SVG_OPEN = b"<svg"


def validate_visuals(
    registry_figures: Sequence[Any],
    output_root: Path,
) -> ValidationLedger:
    ledger = ValidationLedger()
    ledger.extend(_validate_figure_files(registry_figures, output_root))
    ledger.extend(_validate_figure_metadata(registry_figures))
    ledger.extend(_validate_status_consistency(registry_figures))
    return ledger


def validate_html_export(
    rendered_tables: Mapping[str, Mapping[str, Any]],
) -> ValidationLedger:
    ledger = ValidationLedger()
    ledger.extend(_validate_table_escaping(rendered_tables))
    ledger.extend(_validate_table_offline(rendered_tables))
    ledger.extend(_validate_table_structure(rendered_tables))
    return ledger


def _validate_figure_files(
    registry_figures: Sequence[Any], output_root: Path
) -> list[ValidationCheck]:
    checks: list[ValidationCheck] = []
    for record in registry_figures:
        if record.status != Status.PASS:
            continue
        target = output_root / record.png_path
        if not target.exists():
            checks.append(
                ValidationCheck(
                    check_id=f"VIS-FILE-{record.figure_id}",
                    category="figure_export",
                    scope=record.figure_id,
                    expected="tệp PNG tồn tại và có chữ ký PNG hợp lệ",
                    observed="tệp không tồn tại",
                    status=Status.BLOCKED,
                    detail="figure PASS nhưng không có tệp dựng trên đĩa",
                )
            )
            continue
        payload = target.read_bytes()
        valid_signature = payload.startswith(PNG_SIGNATURE)
        svg_path = record.svg_path
        svg_ok = True
        svg_detail = ""
        if svg_path:
            svg_target = output_root / svg_path
            if not svg_target.exists():
                svg_ok = False
                svg_detail = "tệp SVG không tồn tại"
            else:
                svg_payload = svg_target.read_bytes()
                svg_ok = SVG_OPEN in svg_payload[:2048]
                svg_detail = "SVG mở đầu hợp lệ" if svg_ok else "SVG không mở đầu hợp lệ"
        checks.append(
            ValidationCheck(
                check_id=f"VIS-FILE-{record.figure_id}",
                category="figure_export",
                scope=record.figure_id,
                expected="tệp PNG tồn tại, có chữ ký PNG hợp lệ và SVG đi kèm hợp lệ",
                observed=(
                    f"png_bytes={len(payload)}, "
                    f"png_signature={valid_signature}, {svg_detail}"
                ),
                status=Status.PASS if valid_signature and svg_ok else Status.BLOCKED,
                detail="xuất khung hình offline không phụ thuộc mạng",
            )
        )
    return checks


def _validate_figure_metadata(
    registry_figures: Sequence[Any],
) -> list[ValidationCheck]:
    checks: list[ValidationCheck] = []
    for record in registry_figures:
        if record.status != Status.PASS:
            continue
        missing: list[str] = []
        if not record.title:
            missing.append("title")
        if not record.caption:
            missing.append("caption")
        if not record.method:
            missing.append("method")
        if not record.unit:
            missing.append("unit")
        if not record.source_ids:
            missing.append("source_ids")
        if not record.content_hash:
            missing.append("content_hash")
        checks.append(
            ValidationCheck(
                check_id=f"VIS-META-{record.figure_id}",
                category="figure_provenance",
                scope=record.figure_id,
                expected="tiêu đề, chú thích, phương pháp, đơn vị, nguồn và hash đều có",
                observed=f"thiếu={missing or 'không có'}; population_n={record.population_n}",
                status=Status.PASS if not missing else Status.BLOCKED,
                detail="mỗi hình phải tự mô tả và truy vết được nguồn",
            )
        )
    return checks


def _validate_status_consistency(
    registry_figures: Sequence[Any],
) -> list[ValidationCheck]:
    checks: list[ValidationCheck] = []
    for record in registry_figures:
        needs_reason = record.status != Status.PASS
        ok = (not needs_reason) or bool(record.reason)
        checks.append(
            ValidationCheck(
                check_id=f"VIS-STATUS-{record.figure_id}",
                category="figure_status",
                scope=record.figure_id,
                expected="mọi hình không PASS phải ghi lý do",
                observed=f"status={record.status.value}, reason={record.reason or 'rỗng'}",
                status=Status.PASS if ok else Status.BLOCKED,
                detail="trạng thái BLOCKED hoặc NOT APPLICABLE phải nêu lý do",
            )
        )
    return checks


def _validate_table_escaping(
    rendered_tables: Mapping[str, Mapping[str, Any]],
) -> list[ValidationCheck]:
    checks: list[ValidationCheck] = []
    for table_id, rendered in sorted(rendered_tables.items()):
        for scope, payload in sorted(rendered.items()):
            html = str(payload.get("html", "")) if isinstance(payload, dict) else ""
            if not html:
                continue
            has_event_handler = bool(EVENT_HANDLER_PATTERN.search(html))
            has_script = bool(SCRIPT_TAG_PATTERN.search(html))
            ok = not has_event_handler and not has_script
            checks.append(
                ValidationCheck(
                    check_id=f"HTML-SAFE-{table_id}-{scope}",
                    category="html_escaping",
                    scope=f"{table_id}:{scope}",
                    expected="không có thẻ script hay thuộc tính sự kiện nội tuyến",
                    observed=(
                        f"event_handler={has_event_handler}, script_tag={has_script}"
                    ),
                    status=Status.PASS if ok else Status.BLOCKED,
                    detail="nội dung bảng phải được escape trước khi nhúng",
                )
            )
    return checks


def _validate_table_offline(
    rendered_tables: Mapping[str, Mapping[str, Any]],
) -> list[ValidationCheck]:
    checks: list[ValidationCheck] = []
    for table_id, rendered in sorted(rendered_tables.items()):
        for scope, payload in sorted(rendered.items()):
            html = str(payload.get("html", "")) if isinstance(payload, dict) else ""
            if not html:
                continue
            remote = bool(REMOTE_URL_PATTERN.search(html))
            checks.append(
                ValidationCheck(
                    check_id=f"HTML-OFFLINE-{table_id}-{scope}",
                    category="html_offline",
                    scope=f"{table_id}:{scope}",
                    expected="không tham chiếu tài nguyên từ xa",
                    observed=f"remote_reference={remote}",
                    status=Status.PASS if not remote else Status.BLOCKED,
                    detail="bảng HTML phải đọc được khi ngoại tuyến",
                )
            )
    return checks


def _validate_table_structure(
    rendered_tables: Mapping[str, Mapping[str, Any]],
) -> list[ValidationCheck]:
    checks: list[ValidationCheck] = []
    for table_id, rendered in sorted(rendered_tables.items()):
        for scope, payload in sorted(rendered.items()):
            if not isinstance(payload, dict):
                continue
            row_count = int(payload.get("row_count", 0) or 0)
            column_count = int(payload.get("column_count", 0) or 0)
            html = str(payload.get("html", ""))
            has_table_tag = "<table" in html
            ok = has_table_tag and column_count > 0
            checks.append(
                ValidationCheck(
                    check_id=f"HTML-STRUCT-{table_id}-{scope}",
                    category="html_structure",
                    scope=f"{table_id}:{scope}",
                    expected="bảng có thẻ table và ít nhất một cột",
                    observed=(
                        f"rows={row_count}, columns={column_count}, "
                        f"table_tag={has_table_tag}, "
                        f"truncated={payload.get('truncated')}"
                    ),
                    status=Status.PASS if ok else Status.BLOCKED,
                    detail="bảng rỗng phải ghi trạng thái chứ không dựng khung rỗng",
                )
            )
    return checks
