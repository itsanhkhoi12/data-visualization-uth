from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import date, datetime
from typing import Any, Sequence

from common.enums import ColumnType, SemanticType

NUMBER_PATTERN = re.compile(r"^-?(\d{1,3}(,\d{3})*|\d+)(\.\d+)?$")
DECIMAL_COMMA_PATTERN = re.compile(r"^-?\d+,\d+$")
CURRENCY_PATTERN = re.compile(r"^-?[\d.,]+\s*(đ|VND|vnd|%|kg|g|thùng|hộp|lọc)?$")
DATE_PATTERNS = (
    re.compile(r"^\d{4}-\d{2}-\d{2}$"),
    re.compile(r"^\d{2}/\d{2}/\d{4}$"),
    re.compile(r"^\d{1,2}/\d{1,2}/\d{4}$"),
    re.compile(r"^\d{2}-\d{2}-\d{4}$"),
    re.compile(r"^\d{1,2}/\d{1,2}/\d{2}$"),
)
DATETIME_PATTERN = re.compile(r"^\d{4}-\d{2}-\d{2}[ T]\d{1,2}:\d{2}(:\d{2})?")
IDENTIFIER_NAME_PATTERN = re.compile(
    r"(mã|ma|id|code|số chứng từ|so chung tu|bill|invoice|ms|sku|ma khach|ma hang|mã hàng)",
    re.IGNORECASE,
)
MEASURE_NAME_PATTERN = re.compile(
    r"(tiền|tien|tien|giá|gia|gia |số lượng|so luong|sl |sl$|thành tiền|thanh tien|"
    r"tổng|tong|tong |doanh thu|doanh thu|còn nợ|con no|giảm giá|giam gia|"
    r"số khách|so khach|hạn sử dụng|han su dung|thuế|vat|tồn|ton )",
    re.IGNORECASE,
)
DATE_NAME_PATTERN = re.compile(
    r"(ngày|ngay|date|thời gian|thoi gian|thời điểm|hạn|han)", re.IGNORECASE
)
STATUS_NAME_PATTERN = re.compile(
    r"(trạng thái|trang thai|status|tình trạng|tinh trang|loại|loai|nhóm khách|nhom khach)",
    re.IGNORECASE,
)
BOOLEAN_TRUE_TOKENS = {"true", "1", "yes", "có", "y", "đúng", "x", "t"}
BOOLEAN_FALSE_TOKENS = {"false", "0", "no", "không", "n", "sai"}


@dataclass(frozen=True)
class TypeCandidate:
    physical_type: ColumnType
    semantic_type: SemanticType
    confidence: float
    parse_failure_ratio: float
    reason: str


def _text_of(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, (datetime, date)):
        return value.isoformat()
    if isinstance(value, float):
        return repr(value)
    return str(value).strip()


def is_blank(value: Any) -> bool:
    return value is None or (isinstance(value, str) and not value.strip())


def parse_number(value: Any) -> float | None:
    if isinstance(value, bool):
        return None
    if isinstance(value, (int, float)):
        return float(value)
    text = _text_of(value)
    if not text:
        return None
    text = text.replace("\xa0", " ").strip()
    if text.startswith("(") and text.endswith(")"):
        text = f"-{text[1:-1]}"
    if NUMBER_PATTERN.match(text):
        return float(text.replace(",", ""))
    if DECIMAL_COMMA_PATTERN.match(text):
        return float(text.replace(",", "."))
    return None


def parse_date(value: Any) -> date | None:
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value
    text = _text_of(value)
    if not text:
        return None
    for index, pattern in enumerate(DATE_PATTERNS):
        if not pattern.match(text):
            continue
        parts = text.replace("-", "/").split("/")
        try:
            if index == 0:
                return date(int(parts[0]), int(parts[1]), int(parts[2]))
            if index in {1, 4}:
                day, month, year = int(parts[0]), int(parts[1]), int(parts[2])
            else:
                day, month, year = int(parts[0]), int(parts[1]), int(parts[2])
            if year < 100:
                year += 2000
            return date(year, month, day)
        except ValueError:
            return None
    return None


def parse_datetime(value: Any) -> datetime | None:
    if isinstance(value, datetime):
        return value
    text = _text_of(value)
    if not text:
        return None
    if DATETIME_PATTERN.match(text):
        try:
            return datetime.fromisoformat(text.replace("Z", "+00:00"))
        except ValueError:
            return None
    return None


def infer_semantic_type(
    column: str,
    values: Sequence[Any],
    physical_type: ColumnType,
) -> TypeCandidate:
    non_null = [value for value in values if not is_blank(value)]
    total = len(values)
    if not non_null:
        return TypeCandidate(
            physical_type=physical_type,
            semantic_type=SemanticType.UNKNOWN,
            confidence=0.0,
            parse_failure_ratio=1.0,
            reason="no_non_null_values",
        )
    text_values = [_text_of(value) for value in non_null]
    numeric_hits = sum(1 for value in non_null if parse_number(value) is not None)
    date_hits = sum(1 for value in non_null if parse_date(value) is not None)
    datetime_hits = sum(1 for value in non_null if parse_datetime(value) is not None)
    boolean_hits = sum(
        1
        for value in text_values
        if value.lower() in BOOLEAN_TRUE_TOKENS or value.lower() in BOOLEAN_FALSE_TOKENS
    )
    sample_n = len(non_null)
    numeric_ratio = numeric_hits / sample_n
    date_ratio = date_hits / sample_n
    datetime_ratio = datetime_hits / sample_n
    boolean_ratio = boolean_hits / sample_n
    distinct_ratio = len(set(text_values)) / sample_n
    name_is_identifier = bool(IDENTIFIER_NAME_PATTERN.search(column))
    name_is_measure = bool(MEASURE_NAME_PATTERN.search(column))
    name_is_date = bool(DATE_NAME_PATTERN.search(column))
    name_is_status = bool(STATUS_NAME_PATTERN.search(column))
    if datetime_ratio >= 0.9:
        return TypeCandidate(
            physical_type=ColumnType.DATETIME,
            semantic_type=SemanticType.DATETIME,
            confidence=round(datetime_ratio, 4),
            parse_failure_ratio=round(1 - datetime_ratio, 4),
            reason="datetime_parse_ratio",
        )
    if date_ratio >= 0.9:
        confidence = round(date_ratio, 4)
        semantic = SemanticType.DATE
        if name_is_measure:
            semantic = SemanticType.UNKNOWN
            confidence = round(confidence * 0.5, 4)
        return TypeCandidate(
            physical_type=ColumnType.DATE,
            semantic_type=semantic,
            confidence=confidence,
            parse_failure_ratio=round(1 - date_ratio, 4),
            reason="date_parse_ratio",
        )
    if boolean_ratio >= 0.95 and distinct_ratio <= 0.05:
        return TypeCandidate(
            physical_type=ColumnType.BOOLEAN,
            semantic_type=SemanticType.BOOLEAN,
            confidence=round(boolean_ratio, 4),
            parse_failure_ratio=round(1 - boolean_ratio, 4),
            reason="boolean_token_ratio",
        )
    if numeric_ratio >= 0.9:
        if name_is_identifier:
            return TypeCandidate(
                physical_type=ColumnType.INTEGER,
                semantic_type=SemanticType.IDENTIFIER,
                confidence=round(numeric_ratio * 0.9, 4),
                parse_failure_ratio=round(1 - numeric_ratio, 4),
                reason="numeric_but_identifier_name",
            )
        semantic = SemanticType.MEASURE
        if name_is_measure:
            semantic = SemanticType.AMOUNT
        elif distinct_ratio <= 0.05 and sample_n > 1:
            semantic = SemanticType.UNKNOWN
        return TypeCandidate(
            physical_type=(
                ColumnType.DECIMAL
                if any("." in _text_of(value) for value in non_null[:50])
                else ColumnType.INTEGER
            ),
            semantic_type=semantic,
            confidence=round(numeric_ratio, 4),
            parse_failure_ratio=round(1 - numeric_ratio, 4),
            reason="numeric_parse_ratio",
        )
    if name_is_status:
        return TypeCandidate(
            physical_type=ColumnType.CATEGORY,
            semantic_type=SemanticType.CATEGORICAL,
            confidence=round(min(distinct_ratio, 1.0), 4),
            parse_failure_ratio=0.0,
            reason="status_column_name",
        )
    if distinct_ratio <= 0.2:
        return TypeCandidate(
            physical_type=ColumnType.CATEGORY,
            semantic_type=SemanticType.CATEGORICAL,
            confidence=round(distinct_ratio, 4),
            parse_failure_ratio=0.0,
            reason="low_cardinality_ratio",
        )
    return TypeCandidate(
        physical_type=ColumnType.TEXT,
        semantic_type=SemanticType.TEXT,
        confidence=round(1 - numeric_ratio, 4),
        parse_failure_ratio=round(numeric_ratio, 4),
        reason="text_default",
    )


def infer_physical_type(values: Sequence[Any]) -> ColumnType:
    non_null = [value for value in values if not is_blank(value)]
    if not non_null:
        return ColumnType.UNKNOWN
    if all(isinstance(value, bool) for value in non_null):
        return ColumnType.BOOLEAN
    if all(isinstance(value, datetime) for value in non_null):
        return ColumnType.DATETIME
    if all(isinstance(value, date) for value in non_null):
        return ColumnType.DATE
    if all(isinstance(value, int) and not isinstance(value, bool) for value in non_null):
        return ColumnType.INTEGER
    if all(isinstance(value, (int, float)) and not isinstance(value, bool) for value in non_null):
        return ColumnType.DECIMAL
    return ColumnType.TEXT
