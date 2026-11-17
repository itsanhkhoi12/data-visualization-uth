from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass
from typing import Any, Sequence

from common.contracts import ColumnProfile


@dataclass(frozen=True)
class SchemaComparisonEntry:
    business_id: str
    split: str
    field_role: str
    column: str
    semantic_type: str
    presence: str
    confidence: float
    source_id: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "business_id": self.business_id,
            "split": self.split,
            "field_role": self.field_role,
            "column": self.column,
            "semantic_type": self.semantic_type,
            "presence": self.presence,
            "confidence": self.confidence,
            "source_id": self.source_id,
        }


ROLE_TOKENS: dict[str, tuple[str, ...]] = {
    "order_identifier": (
        "mã hóa đơn",
        "mã hoá đơn",
        "ma hoa don",
        "ma hoadon",
        "ma bill",
        "mã bill",
        "bill",
        "mã đơn",
        "ma don",
        "mã đơn hàng",
        "ma don hang",
        "số phiếu",
        "so phieu",
        "số chứng từ",
        "ma chung tu",
    ),
    "order_date": (
        "ngày đặt",
        "ngày tạo",
        "thời gian tạo",
        "ngày bán",
        "ngay ban",
        "ngày giao dịch",
        "ngay giao dich",
        "ngay lap",
        "ngày",
        "ngay",
    ),
    "order_status": (
        "trạng thái đơn",
        "trang thai don",
        "trạng thái",
        "trang thai",
        "tình trạng",
        "tinh trang",
        "kết quả",
        "ket qua",
    ),
    "item_name": (
        "tên hàng",
        "ten hang",
        "mặt hàng",
        "mat hang",
        "sản phẩm",
        "san pham",
        "nội dung",
        "noi dung",
        "hàng bán",
        "hang ban",
        "tên hàng hóa",
    ),
    "item_identifier": (
        "mã hàng",
        "ma hang",
        "mã sản phẩm",
        "ma san pham",
        "sku",
        "mã hàng hóa",
        "ma hang hoa",
        "mã hàng bán",
        "ma hang ban",
    ),
    "quantity": (
        "số lượng",
        "so luong",
        "số lượng lẻ",
        "sl",
        "s.l",
    ),
    "unit": (
        "đơn vị",
        "don vi",
        "dvt",
    ),
    "amount": (
        "thành tiền",
        "tổng tiền",
        "tong tien",
        "giá bán",
        "gia ban",
        "đơn giá",
        "don gia",
        "thanh tien",
        "tiền hàng",
        "tien hang",
        "tổng tiền hàng",
        "tong tien hang",
        "giá 1 đv",
        "gia 1 dv",
    ),
    "customer_identifier": (
        "mã khách",
        "ma khach",
        "mã khách hàng",
        "ma khach hang",
        "mã khách mua",
        "ma khach mua",
        "customer id",
    ),
    "customer_name": (
        "khách hàng",
        "khach hang",
        "tên khách",
        "ten khach",
        "khách mua",
        "khach mua",
        "bên mua",
        "ben mua",
    ),
    "payment_amount": (
        "khách đã trả",
        "khach da tra",
        "số tiền thu",
        "so tien thu",
        "đã trả",
        "da tra",
        "số tiền trả",
        "so tien tra",
    ),
    "debt_balance": (
        "còn nợ",
        "con no",
        "dư nợ",
        "du no",
        "phải thu",
        "phai thu",
        "công nợ",
        "cong no",
    ),
    "expiry_date": (
        "hạn sử dụng",
        "han su dung",
    ),
    "lot_identifier": (
        "mã lô",
        "ma lo",
        "lô",
    ),
    "employee_identifier": (
        "nhân viên",
        "nhan vien",
        "mã nhân viên",
        "ma nhan vien",
        "thợ",
        "tho",
    ),
    "discount": (
        "giảm giá",
        "giam gia",
        "chiết khấu",
        "chiet khau",
    ),
}


def _strip_marks(text: str) -> str:
    text = text.replace("đ", "d").replace("Đ", "D")
    decomposed = unicodedata.normalize("NFD", text)
    return "".join(ch for ch in decomposed if not unicodedata.combining(ch))


def _normalize(text: str) -> str:
    lowered = _strip_marks(text.lower())
    spaced = re.sub(r"(?<=[a-z])(?=[A-Z])", " ", text)
    lowered = _strip_marks(spaced.lower())
    return " ".join(lowered.replace("_", " ").split())


def detect_field_role(column: str) -> str | None:
    normalized = _normalize(column)
    padded = f" {normalized} "
    for role, tokens in ROLE_TOKENS.items():
        for token in tokens:
            normalized_token = _normalize(token)
            if not normalized_token:
                continue
            if f" {normalized_token} " in padded:
                return role
    return None


def compare_schemas(
    column_profiles: Sequence[ColumnProfile],
) -> tuple[SchemaComparisonEntry, ...]:
    entries: list[SchemaComparisonEntry] = []
    for profile in column_profiles:
        role = detect_field_role(profile.column)
        if role is None:
            continue
        entries.append(
            SchemaComparisonEntry(
                business_id=profile.business_id,
                split=profile.split,
                field_role=role,
                column=profile.column,
                semantic_type=profile.semantic_type,
                presence="present",
                confidence=profile.confidence,
                source_id=profile.source_id,
            )
        )
    return tuple(entries)


def role_presence_matrix(
    entries: Sequence[SchemaComparisonEntry],
) -> dict[str, dict[str, str]]:
    matrix: dict[str, dict[str, str]] = {}
    for entry in entries:
        matrix.setdefault(entry.business_id, {})[entry.field_role] = entry.column
    return matrix
