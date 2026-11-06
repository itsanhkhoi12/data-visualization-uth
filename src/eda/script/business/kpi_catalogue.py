from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Sequence

from common.contracts import MetricDefinition
from common.enums import Status


@dataclass(frozen=True)
class KpiCandidate:
    metric_id: str
    name: str
    required_evidence: tuple[str, ...]
    applicability: str
    status: Status
    reason: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "metric_id": self.metric_id,
            "name": self.name,
            "required_evidence": list(self.required_evidence),
            "applicability": self.applicability,
            "status": self.status.value,
            "reason": self.reason,
        }


REQUIRED_EVIDENCE = {
    "revenue": ("order_identifier", "order_status", "order_date", "amount"),
    "order_count": ("order_identifier", "order_status", "order_date"),
    "quantity_sold": ("quantity", "item_identifier", "order_status"),
    "debt_balance": ("debt_balance", "payment_amount"),
    "inventory_balance": ("item_identifier", "quantity"),
    "gross_profit": ("amount", "item_identifier"),
    "purchase_value": ("amount", "item_identifier"),
    "customer_ranking": ("customer_identifier", "order_identifier"),
    "employee_ranking": ("employee_identifier", "order_identifier"),
    "item_ranking": ("item_identifier", "quantity"),
    "cancel_rate": ("order_identifier", "order_status"),
    "return_rate": ("order_identifier", "order_status"),
    "lot_expiry": ("lot_identifier", "expiry_date"),
    "receivable_aging": ("order_date", "debt_balance", "payment_amount"),
    "shift_cash_report": ("payment_amount",),
    "weekday_average": ("order_identifier", "order_date"),
}

GRAIN_REQUIREMENTS = {
    "revenue": ("order_line",),
    "order_count": ("order",),
    "quantity_sold": ("order_line",),
    "debt_balance": ("snapshot",),
    "inventory_balance": ("snapshot",),
    "gross_profit": ("order_line",),
    "purchase_value": ("purchase",),
    "customer_ranking": ("order",),
    "employee_ranking": ("order",),
    "item_ranking": ("order_line",),
    "cancel_rate": ("order",),
    "return_rate": ("order",),
    "lot_expiry": ("item",),
    "receivable_aging": ("snapshot",),
    "shift_cash_report": ("payment",),
    "weekday_average": ("order",),
}

RULE_ANCHORS = {
    "revenue": ("doanh thu",),
    "order_count": ("so don", "so luong don"),
    "quantity_sold": ("so luong", "ban chay"),
    "debt_balance": ("cong no", "con no"),
    "inventory_balance": ("ton kho", "ton cuoi"),
    "gross_profit": ("lai gop", "gia von"),
    "purchase_value": ("nhap hang", "phieu nhap"),
    "customer_ranking": ("xac dinh khach", "khach mua", "khach hang"),
    "employee_ranking": ("nhan vien ban gioi nhat", "nhan vien"),
    "item_ranking": ("mat hang", "ban chay", "xep hang hang"),
    "cancel_rate": ("ty le huy don", "ty le huy", "don huy"),
    "return_rate": ("don tra hang", "tra hang"),
    "lot_expiry": ("lo hang", "han su dung"),
    "receivable_aging": ("tuoi no", "cong no"),
    "shift_cash_report": ("ca sang", "tien mat", "ca lam viec"),
    "weekday_average": ("thu bo", "trung binh moi ngay"),
}


def build_kpi_catalogue(
    split: str,
    business_id: str,
    available_evidence: Sequence[str],
    rule_registry: Any,
    capability_by_metric: dict[str, bool] | None = None,
) -> tuple[MetricDefinition, ...]:
    capability_by_metric = capability_by_metric or {}
    available = {item.lower() for item in available_evidence}
    definitions: list[MetricDefinition] = []
    for metric_id, requirements in REQUIRED_EVIDENCE.items():
        rule_id = _match_rule(rule_registry, RULE_ANCHORS.get(metric_id, ()))
        supported = capability_by_metric.get(metric_id)
        if supported is None:
            supported = all(
                any(_token_matches(token, item) for item in available)
                for token in requirements
            )
        if supported and rule_id:
            status = Status.PASS
        elif supported:
            status = Status.PARTIAL
        else:
            status = Status.BLOCKED
        definitions.append(
            MetricDefinition(
                metric_id=f"{split}.{business_id}.{metric_id}",
                split=split,
                business_id=business_id,
                name=metric_id.replace("_", " "),
                grain="order_line" if "order_lines" in requirements else "document",
                numerator="defined in rulebook",
                denominator="explicit in rulebook",
                filters=requirements,
                status_handling="per split rulebook status policy",
                as_of_semantics="as_of_date from questions.jsonl",
                unit="VND" if "money" in metric_id or metric_id == "revenue" else "count",
                rounding="per split rulebook",
                null_behavior="excluded from denominator and reported",
                join_path=(),
                rule_id=rule_id,
                source_columns=tuple(requirements),
                formula_status=status,
            )
        )
    return tuple(definitions)


import unicodedata


VIETNAMESE_STROKES = {
    "đ": "d",
    "Đ": "D",
}


def _strip_marks(text: str) -> str:
    for stroke, plain in VIETNAMESE_STROKES.items():
        text = text.replace(stroke, plain)
    decomposed = unicodedata.normalize("NFD", text)
    return "".join(ch for ch in decomposed if not unicodedata.combining(ch))


def _normalize(text: str) -> str:
    lowered = _strip_marks(text.lower().replace("_", " "))
    return " ".join(lowered.split())


def _match_rule(rule_registry: Any, anchors: Sequence[str]) -> str | None:
    if rule_registry is None:
        return None
    normalized_anchors = [_normalize(anchor) for anchor in anchors]
    for rule in rule_registry.rules:
        haystack = _normalize(f"{rule.rule_label} {rule.rule_text}")
        for anchor in normalized_anchors:
            if anchor and anchor in haystack:
                return rule.rule_id
    return None


def _token_matches(token: str, candidate: str) -> bool:
    token = _normalize(token)
    candidate = _normalize(candidate)
    return token in candidate or candidate in token
