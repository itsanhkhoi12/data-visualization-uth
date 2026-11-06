from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass
from typing import Any, Sequence

from readers.jsonl_reader import iterate_jsonl
from schema.type_inference import is_blank

DIACRITIC_PATTERN = re.compile(r"[̀-ͯ]")
WHITESPACE_PATTERN = re.compile(r"\s+")
DATE_PATTERN = re.compile(r"\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b")

TIME_KEYWORDS = {
    "today": ("hôm nay", "ngày hôm nay", "riêng ngay", "hom nay"),
    "yesterday": ("hôm qua", "hom qua"),
    "this_week": ("tuần này", "tuan nay", "tuần qua", "tuần trước", "tuần rồi"),
    "this_month": ("tháng này", "thang nay", "tháng trước", "thang truoc", "tháng vừa"),
    "this_year": ("từ đầu năm", "tu dau nam", "năm nay", "nam nay"),
    "last_n_days": ("n gần nhất", "ngay gan nhat", "ngày gần nhất"),
    "absolute_month": ("tháng ", "thang "),
    "quarter": ("quý", "quy"),
    "tet": ("tết", "tet"),
    "shift": ("ca sáng", "ca chiều", "ca sang", "ca chieu"),
    "date_range": ("từ ", "đến ", "từ ngày", "tu ngay"),
    "relative_period": ("kỳ trước", "ky truoc", "so với", "so voi", "cùng kỳ"),
}

METRIC_KEYWORDS = {
    "revenue": ("doanh thu", "tổng giá trị", "tiền bán", "tiền hàng", "tổng tiền"),
    "order_count": ("bao nhiêu đơn", "số đơn", "so don", "đơn hàng"),
    "quantity": ("bán được bao nhiêu", "số lượng", "so luong", "bán chạy"),
    "debt": ("còn nợ", "con no", "công nợ", "thu nợ", "trả nợ"),
    "inventory": ("tồn kho", "ton kho", "còn tồn", "hàng còn"),
    "gross_profit": ("lãi gộp", "lai gop", "lợi nhuận"),
    "customer": ("khách", "khach"),
    "item": ("mặt hàng", "mat hang", "hàng", "sản phẩm", "san pham", "món"),
    "employee": ("nhân viên", "nhan vien", "thợ", "tho"),
    "purchase": ("nhập hàng", "nhap hang", "phiếu nhập"),
    "payment": ("thanh toán", "thanh toan", "tiền mặt", "tien mat"),
}

TIE_BREAK_KEYWORDS = ("nhiều nhất", "nhieu nhat", "cao nhất", "cao nhat", "top", "bán chạy", "bán nhiều")
ROUNDING_KEYWORDS = ("làm tròn", "lam tron", "tròn", "2 chữ số", "chữ số thập phân")
LIST_KEYWORDS = ("những", "nhung", "các", "liệt kê", "liet ke", "bao gồm")
BOOLEAN_KEYWORDS = ("có phải", "co phai", "hay không", "không?", "thì có")


@dataclass(frozen=True)
class QuestionProfile:
    split: str
    question_count: int
    unique_id_count: int
    duplicate_id_count: int
    business_distribution: dict[str, int]
    as_of_min: str | None
    as_of_max: str | None
    as_of_missing_count: int
    length_characters_min: int
    length_characters_max: int
    length_characters_mean: float
    length_characters_median: float
    length_without_diacritics_mean: float
    time_expression_counts: dict[str, int]
    metric_keyword_counts: dict[str, int]
    intent_candidates: dict[str, int]
    length_buckets: dict[str, int]
    requires_join_hint_count: int
    tie_break_hint_count: int
    rounding_hint_count: int
    list_hint_count: int
    boolean_hint_count: int
    malformed_count: int
    status: str
    notes: tuple[str, ...] = ()

    def to_dict(self) -> dict[str, Any]:
        return {
            "split": self.split,
            "question_count": self.question_count,
            "unique_id_count": self.unique_id_count,
            "duplicate_id_count": self.duplicate_id_count,
            "business_distribution": dict(self.business_distribution),
            "as_of_min": self.as_of_min,
            "as_of_max": self.as_of_max,
            "as_of_missing_count": self.as_of_missing_count,
            "length_characters_min": self.length_characters_min,
            "length_characters_max": self.length_characters_max,
            "length_characters_mean": self.length_characters_mean,
            "length_characters_median": self.length_characters_median,
            "length_without_diacritics_mean": self.length_without_diacritics_mean,
            "time_expression_counts": dict(self.time_expression_counts),
            "metric_keyword_counts": dict(self.metric_keyword_counts),
            "intent_candidates": dict(self.intent_candidates),
            "length_buckets": dict(self.length_buckets),
            "requires_join_hint_count": self.requires_join_hint_count,
            "tie_break_hint_count": self.tie_break_hint_count,
            "rounding_hint_count": self.rounding_hint_count,
            "list_hint_count": self.list_hint_count,
            "boolean_hint_count": self.boolean_hint_count,
            "malformed_count": self.malformed_count,
            "status": self.status,
            "notes": list(self.notes),
        }


def strip_diacritics(text: str) -> str:
    normalized = unicodedata.normalize("NFD", text)
    return DIACRITIC_PATTERN.sub("", normalized)


def normalize_question(text: str) -> str:
    return WHITESPACE_PATTERN.sub(" ", text.strip().lower())


def classify_time_expression(text: str) -> tuple[str, ...]:
    lowered = text.lower()
    found: list[str] = []
    for label, keywords in TIME_KEYWORDS.items():
        for keyword in keywords:
            if keyword in lowered:
                found.append(label)
                break
    return tuple(found)


def classify_metric(text: str) -> tuple[str, ...]:
    lowered = text.lower()
    found: list[str] = []
    for label, keywords in METRIC_KEYWORDS.items():
        for keyword in keywords:
            if keyword in lowered:
                found.append(label)
                break
    return tuple(found)


def infer_intent(text: str) -> str:
    lowered = text.lower()
    if not lowered.strip():
        return "other"
    if any(keyword in lowered for keyword in BOOLEAN_KEYWORDS):
        return "boolean"
    if any(keyword in lowered for keyword in LIST_KEYWORDS) and any(
        keyword in lowered for keyword in ("nào", "nao", "gì", "gi")
    ):
        return "list_or_enum"
    if any(keyword in lowered for keyword in TIE_BREAK_KEYWORDS):
        return "ranking"
    if (
        "khi nào" in lowered
        or "bao giờ" in lowered
        or "ngày nào" in lowered
        or "ngay nao" in lowered
    ):
        return "point_in_time"
    if (
        "bao nhiêu" in lowered
        or "bao nhieu" in lowered
        or "tỷ lệ" in lowered
        or "ty le" in lowered
        or "tỉ lệ" in lowered
        or "ti le" in lowered
    ):
        return "aggregate"
    if classify_metric(lowered):
        return "aggregate"
    if classify_time_expression(lowered) or DATE_PATTERN.search(lowered):
        return "temporal"
    return "other"


def profile_questions(path: Path, split: str) -> QuestionProfile:
    records = iterate_jsonl(path)
    notes: list[str] = []
    business_counts: dict[str, int] = {}
    as_of_values: list[str] = []
    as_of_missing = 0
    identifiers: list[str] = []
    lengths: list[int] = []
    stripped_lengths: list[int] = []
    time_counts: dict[str, int] = {}
    metric_counts: dict[str, int] = {}
    intent_counts: dict[str, int] = {}
    length_buckets: dict[str, int] = {}
    join_hints = 0
    tie_break_hints = 0
    rounding_hints = 0
    list_hints = 0
    boolean_hints = 0
    for record in records:
        identifier = str(record.get("id", ""))
        if identifier:
            identifiers.append(identifier)
        business_id = str(record.get("business_id", "__unknown__"))
        business_counts[business_id] = business_counts.get(business_id, 0) + 1
        as_of = record.get("as_of_date")
        if is_blank(as_of):
            as_of_missing += 1
        else:
            as_of_values.append(str(as_of))
        question = str(record.get("question", ""))
        length = len(question)
        lengths.append(length)
        stripped_lengths.append(len(strip_diacritics(question)))
        bucket = (
            "0-30" if length <= 30 else "31-60" if length <= 60 else "61-100" if length <= 100 else "101+"
        )
        length_buckets[bucket] = length_buckets.get(bucket, 0) + 1
        lowered = question.lower()
        for label in classify_time_expression(question):
            time_counts[label] = time_counts.get(label, 0) + 1
        for label in classify_metric(question):
            metric_counts[label] = metric_counts.get(label, 0) + 1
        intent = infer_intent(question)
        intent_counts[intent] = intent_counts.get(intent, 0) + 1
        if any(token in lowered for token in ("và", "va ", "kết hợp", "kết hợp với", "so với", "so voi")):
            join_hints += 1
        if any(token in lowered for token in TIE_BREAK_KEYWORDS):
            tie_break_hints += 1
        if any(token in lowered for token in ROUNDING_KEYWORDS):
            rounding_hints += 1
        if any(token in lowered for token in LIST_KEYWORDS):
            list_hints += 1
        if any(token in lowered for token in BOOLEAN_KEYWORDS):
            boolean_hints += 1
    count = len(records)
    if as_of_missing:
        notes.append("as_of_date_missing_on_some_questions")
    ordered_lengths = sorted(lengths)
    median = (
        ordered_lengths[len(ordered_lengths) // 2]
        if ordered_lengths and len(ordered_lengths) % 2
        else (
            (
                ordered_lengths[len(ordered_lengths) // 2 - 1]
                + ordered_lengths[len(ordered_lengths) // 2]
            )
            / 2
            if ordered_lengths
            else 0.0
        )
    )
    return QuestionProfile(
        split=split,
        question_count=count,
        unique_id_count=len(set(identifiers)),
        duplicate_id_count=len(identifiers) - len(set(identifiers)),
        business_distribution=dict(sorted(business_counts.items())),
        as_of_min=min(as_of_values) if as_of_values else None,
        as_of_max=max(as_of_values) if as_of_values else None,
        as_of_missing_count=as_of_missing,
        length_characters_min=min(lengths) if lengths else 0,
        length_characters_max=max(lengths) if lengths else 0,
        length_characters_mean=round(sum(lengths) / count, 4) if count else 0.0,
        length_characters_median=median,
        length_without_diacritics_mean=round(sum(stripped_lengths) / count, 4) if count else 0.0,
        time_expression_counts=dict(sorted(time_counts.items())),
        metric_keyword_counts=dict(sorted(metric_counts.items())),
        intent_candidates=dict(sorted(intent_counts.items())),
        length_buckets=dict(sorted(length_buckets.items())),
        requires_join_hint_count=join_hints,
        tie_break_hint_count=tie_break_hints,
        rounding_hint_count=rounding_hints,
        list_hint_count=list_hints,
        boolean_hint_count=boolean_hints,
        malformed_count=0,
        status="PASS" if count else "BLOCKED",
        notes=tuple(notes),
    )


def question_metadata_records(path: Path, split: str) -> list[dict[str, Any]]:
    records = iterate_jsonl(path)
    output: list[dict[str, Any]] = []
    for record in records:
        question = str(record.get("question", ""))
        output.append(
            {
                "split": split,
                "id": str(record.get("id", "")),
                "business_id": str(record.get("business_id", "")),
                "as_of_date": str(record.get("as_of_date", "")),
                "question_length_characters": len(question),
                "question_length_without_diacritics": len(strip_diacritics(question)),
                "time_expressions": ",".join(classify_time_expression(question)),
                "metric_keywords": ",".join(classify_metric(question)),
                "intent_candidate": infer_intent(question),
                "has_tie_break_signal": any(
                    token in question.lower() for token in TIE_BREAK_KEYWORDS
                ),
                "has_rounding_signal": any(
                    token in question.lower() for token in ROUNDING_KEYWORDS
                ),
                "is_list_signal": any(token in question.lower() for token in LIST_KEYWORDS),
                "is_boolean_signal": any(
                    token in question.lower() for token in BOOLEAN_KEYWORDS
                ),
            }
        )
    return output


def sequence_lengths(values: Sequence[int]) -> list[int]:
    return sorted(values)
