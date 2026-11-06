from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass
from datetime import date
from typing import Any, Mapping, Sequence

from common.enums import Status
from readers.table_reader import LoadedTable
from schema.type_inference import is_blank, parse_date, parse_datetime, parse_number

ROLE_TOKEN_MAP: dict[str, tuple[str, ...]] = {
    "order_identifier": (
        "mã hóa đơn",
        "mã hoá đơn",
        "mã đơn hàng",
        "ma don hang",
        "số phiếu",
        "so phieu",
        "mã chứng từ",
        "ma chung tu",
        "ma hoa don",
        "ma don",
        "mã đơn",
    ),
    "order_status": (
        "trạng thái đơn",
        "trạng thái",
        "tình trạng",
        "kết quả",
        "xử lý",
        "tinh trang",
    ),
    "order_date": (
        "ngày đặt",
        "ngày bán",
        "ngày giao dịch",
        "ngay ban",
        "thời gian tạo",
        "ngày tạo",
        "thoi gian lap",
        "ngày",
    ),
    "line_amount": (
        "thành tiền",
        "tổng tiền",
        "tiền hàng",
        "tiền bán",
        "t.tiền",
        "tổng",
        "amount",
        "tri gia",
        "tổng đơn",
    ),
    "unit_price": (
        "giá đơn vị",
        "đơn giá",
        "gia ban",
        "giá bán",
        "gia don vi",
        "giá 1 đv",
        "giá sản phẩm",
    ),
    "quantity": (
        "số lượng",
        "so luong",
        "số lượng lẻ",
        "số lượng sản phẩm",
        "sl quy đổi",
        "sl",
    ),
    "base_quantity": (
        "số lượng quy đổi",
        "quy ra dv lẻ",
        "số lượng lẻ",
        "sl quy doi",
        "slquydoi",
    ),
    "product_name": (
        "tên hàng",
        "tên sản phẩm",
        "mặt hàng",
        "hàng bán",
        "nội dung",
        "tên hàng hóa",
    ),
    "product_group": (
        "nhóm hàng",
        "nhom hang",
        "nhóm hàng hóa",
        "nhóm hàng(3 cấp)",
        "nhóm hàng hóa",
        "danh mục",
        "loại hàng hóa",
        "loại hàng hoa",
        "nhom hh",
    ),
    "product_id": (
        "mã hàng",
        "mã sản phẩm",
        "mã sp",
        "mã hh",
        "ma hang hoa",
        "mã sku",
        "sku",
        "mã hàng hóa",
    ),
    "unit": (
        "đơn vị",
        "don vi",
        "đvt",
        "đơn vị tính",
        "đơn vị cơ bản",
    ),
    "cost_price": (
        "giá vốn",
        "gia von",
        "giá nhập",
        "gia nhap",
        "giá nhập bình quân",
    ),
    "supplier": (
        "nhà cung cấp",
        "nha cung cap",
        "ncc",
        "mã ncc",
        "ma ncc",
    ),
    "purchase_id": (
        "mã nhập hàng",
        "số phiếu nhập",
        "ma phieu nhap",
        "mã phiếu nhập",
    ),
    "purchase_date": (
        "ngày nhập",
        "ngay nhap",
        "ngày phiếu",
    ),
    "purchase_amount": (
        "thành tiền",
        "tổng giá trị nhập",
        "tong gia tri nhap",
        "giá trị",
    ),
    "stock_quantity": (
        "tồn cuối",
        "tồn cuối kỳ",
        "ton cuoi",
        "ton cuoi ky",
        "tồn thực",
        "tồn kho",
        "ton kho",
    ),
    "debt_balance": (
        "còn nợ",
        "con no",
        "dư nợ",
        "du no",
        "phải thu",
        "công nợ",
        "còn lại",
    ),
    "payment_amount": (
        "khách đã trả",
        "da tra",
        "số tiền thu",
        "so tien thu",
        "số tiền trả",
        "so tien tra",
        "tiền",
    ),
    "payment_date": (
        "thời gian thu",
        "ngày thu",
        "thời điểm",
        "thoi diem",
        "ngày nhận",
    ),
    "due_date": (
        "hạn thanh toán",
        "han thanh toan",
        "hạn nợ",
        "han no",
        "hạn trả",
        "số ngày được nợ",
    ),
    "expiry_date": (
        "hạn sử dụng",
        "han su dung",
        "hansudung",
    ),
    "lot_id": (
        "mã lô",
        "ma lo",
        "lô",
        "lo",
    ),
    "warranty": (
        "bảo hành",
        "bao hanh",
    ),
    "model": (
        "mẫu máy",
        "model",
        "mẫu",
    ),
    "service_type": (
        "loại dịch vụ",
        "loai dich vu",
        "hạng mục sửa chữa",
        "dịch vụ",
        "loại công việc",
        "hang muc",
    ),
    "visit_id": (
        "mã lượt",
        "ma luot",
        "lượt",
        "mã phiếu sửa",
    ),
    "attribute": (
        "thuộc tính",
        "thuoc tinh",
    ),
    "customer_id": (
        "mã khách hàng",
        "mã khách",
        "ma khach hang",
        "customer id",
        "mã khách mua",
    ),
}

STATUS_CANCEL_TOKENS = (
    "hủy",
    "huy",
    "cancel",
    "không giao được",
    "khong giao duoc",
)
STATUS_RETURN_TOKENS = (
    "trả hàng",
    "tra hang",
    "return",
    "đổi trả",
    "doi tra",
    "hoàn hàng",
    "hoan hang",
)
STATUS_TRANSIT_TOKENS = (
    "đang giao",
    "dang giao",
    "đang xử lý",
    "dang xu ly",
    "đang vận chuyển",
    "in transit",
    "shipping",
)
STATUS_COMPLETE_TOKENS = (
    "hoàn thành",
    "hoan thanh",
    "xong",
    "ok",
    "completed",
    "complete",
    "thành công",
    "thanh cong",
    "success",
    "đã giao",
    "đã nhập hàng",
    "received",
    "delivered",
    "đã lấy",
    "đã hoàn hàng",
)

EXPIRY_WINDOW_DAYS = (30, 60, 90, 180, 365)
AGING_BUCKETS = (
    ("Chưa đến hạn", 0, 30),
    ("Trễ 1-30 ngày", 31, 60),
    ("Trễ 31-60 ngày", 61, 90),
    ("Trễ trên 90 ngày", 91, 10_000),
)
METRIC_LIMITATIONS: dict[str, tuple[str, ...]] = {
    "BUS01": (
        "mỗi đơn hàng được định giá bằng tổng giá trị dòng của mã đơn phân biệt",
        "ngưỡng doanh thu hợp lệ theo rulebook của split được áp dụng trước khi kết luận",
    ),
    "BUS02": (
        "doanh thu ngày loại các đơn đã hủy hoặc trả hàng",
        "một ngày không có doanh thu không đồng nghĩa ngày đó không có hoạt động",
    ),
    "BUS03": (
        "số lượng được cộng theo đơn vị gốc khi nguồn không có cột quy đổi",
        "bảng quy đổi đơn vị không được áp dụng khi nguồn không cung cấp",
    ),
    "BUS04": (
        "nhãn trạng thái được gom thành các lớp loại trừ nhau",
        "trạng thái không nhận diện được giữ ở lớp Khác tường minh",
    ),
    "BUS05": (
        "tồn kho là ảnh chụp cuối kỳ chứ không phải sổ biến động",
        "đơn vị tồn kho không được quy đổi về một đơn vị cơ sở chung",
    ),
    "BUS06": (
        "giá trị tồn kho dùng giá vốn ghi trong cùng nguồn",
        "giá vốn không được tính lại từ các lô nhập hàng",
    ),
    "BUS07": (
        "chỉ số dư dương mới được tính là công nợ còn tồn đọng",
        "ngữ nghĩa công nợ khách hàng phụ thuộc rulebook của split",
    ),
    "BUS08": (
        "tuổi nợ tính theo hạn đã ghi so với ngày đánh giá",
        "ngày cắt là ngày đánh giá chứ không phải ngày as-of của câu hỏi",
    ),
    "BUS09": (
        "tuổi công nợ đếm từ ngày đặt hàng theo định nghĩa của rulebook",
        "dòng thiếu ngày đặt hàng bị loại và được báo cáo riêng",
    ),
    "BUS10": (
        "mỗi phiếu nhập được định giá tại grain phiếu nhập phân biệt",
        "phiếu nhập hủy không được tách riêng theo schema của nguồn",
    ),
    "BUS11": (
        "mức tập trung nhà cung cấp chỉ dùng giá trị nhập hàng đã ghi",
        "liên kết nhà cung cấp là trong cùng nguồn và không vượt grain",
    ),
    "BUS12": (
        "cửa sổ hết hạn dùng ngày đánh giá làm mốc tham chiếu",
        "số lượng theo lô là tồn kho cuối kỳ chứ không phải lượng bán cả đời",
    ),
    "BUS13": (
        "mục bảo hành trong danh mục không phải sự kiện bảo hành",
        "mã thiết bị không bao giờ được hiển thị",
    ),
    "BUS14": (
        "mỗi lượt sửa chữa được đếm một lần theo mã lượt phân biệt",
        "phân loại dịch vụ theo cột nhóm khai báo trong nguồn",
    ),
    "BUS15": (
        "thuộc tính đến từ cột danh mục khai báo chứ không phải tên sản phẩm",
        "sản phẩm không có thuộc tính khai báo bị loại và được báo cáo",
    ),
}
CANCEL_LABEL = "Hủy"
RETURN_LABEL = "Trả hàng"
TRANSIT_LABEL = "Đang giao"
COMPLETE_LABEL = "Hoàn thành"
OTHER_LABEL = "Khác"


def _strip_marks(text: str) -> str:
    text = text.replace("đ", "d").replace("Đ", "D")
    decomposed = unicodedata.normalize("NFD", text)
    return "".join(ch for ch in decomposed if not unicodedata.combining(ch))


def _normalize(text: str) -> str:
    lowered = _strip_marks(str(text).lower())
    spaced = re.sub(r"(?<=[a-z0-9])(?=[A-Z])", " ", lowered)
    return " ".join(spaced.replace("_", " ").split())


def _match_role(column: str) -> str | None:
    normalized = f" {_normalize(column)} "
    best_role: str | None = None
    best_length = 0
    for role, tokens in ROLE_TOKEN_MAP.items():
        for token in tokens:
            normalized_token = _normalize(token)
            if not normalized_token:
                continue
            if f" {normalized_token} " in normalized and len(normalized_token) > best_length:
                best_role = role
                best_length = len(normalized_token)
    return best_role


def _find_column(header: Sequence[str], role: str) -> str | None:
    matched = [name for name in header if name and _match_role(name) == role]
    if not matched:
        return None
    return matched[0]


def _find_columns(header: Sequence[str], role: str) -> tuple[str, ...]:
    return tuple(name for name in header if name and _match_role(name) == role)


def _value(row: Mapping[str, Any], column: str | None) -> Any:
    if not column:
        return None
    return row.get(column)


def _number(row: Mapping[str, Any], column: str | None) -> float | None:
    if not column:
        return None
    raw = row.get(column)
    if is_blank(raw):
        return None
    parsed = parse_number(raw)
    return float(parsed) if parsed is not None else None


def _text(row: Mapping[str, Any], column: str | None) -> str:
    if not column:
        return ""
    raw = row.get(column)
    if is_blank(raw):
        return ""
    return str(raw).strip()


def _day(value: Any) -> date | None:
    if is_blank(value):
        return None
    parsed = parse_date(value)
    if parsed is not None:
        return parsed
    parsed_datetime = parse_datetime(value)
    return parsed_datetime.date() if parsed_datetime else None


def classify_status(raw: str) -> str:
    lowered = _normalize(raw)
    if not lowered:
        return OTHER_LABEL
    for token in STATUS_CANCEL_TOKENS:
        if _normalize(token) in lowered:
            return CANCEL_LABEL
    for token in STATUS_RETURN_TOKENS:
        if _normalize(token) in lowered:
            return RETURN_LABEL
    for token in STATUS_TRANSIT_TOKENS:
        if _normalize(token) in lowered:
            return TRANSIT_LABEL
    for token in STATUS_COMPLETE_TOKENS:
        if _normalize(token) in lowered:
            return COMPLETE_LABEL
    return OTHER_LABEL


def revenue_eligible(raw_status: str) -> bool:
    return classify_status(raw_status) in {COMPLETE_LABEL, TRANSIT_LABEL}


@dataclass(frozen=True)
class BusinessMetricRow:
    split: str
    business_id: str
    source_id: str
    object_name: str
    metric_id: str
    kind: str
    payload: Mapping[str, Any]
    population_n: int
    method: str
    status: Status
    reason: str
    grain: str
    unit: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "split": self.split,
            "business_id": self.business_id,
            "source_id": self.source_id,
            "object_name": self.object_name,
            "metric_id": self.metric_id,
            "kind": self.kind,
            "payload": dict(self.payload),
            "population_n": self.population_n,
            "method": self.method,
            "status": self.status.value,
            "reason": self.reason,
            "grain": self.grain,
            "unit": self.unit,
        }


def _row(
    table: LoadedTable,
    metric_id: str,
    kind: str,
    payload: Mapping[str, Any],
    population_n: int,
    method: str,
    status: Status,
    reason: str,
    grain: str,
    unit: str,
) -> BusinessMetricRow:
    enriched = dict(payload)
    enriched.setdefault("limitations", list(METRIC_LIMITATIONS.get(metric_id, ())))
    return BusinessMetricRow(
        split=table.split,
        business_id=table.business_id,
        source_id=table.source_id,
        object_name=table.object_name,
        metric_id=metric_id,
        kind=kind,
        payload=enriched,
        population_n=population_n,
        method=method,
        status=status,
        reason=reason,
        grain=grain,
        unit=unit,
    )


def _order_metrics(table: LoadedTable) -> list[BusinessMetricRow]:
    header = table.header
    order_column = _find_column(header, "order_identifier")
    status_column = _find_column(header, "order_status")
    amount_column = _find_column(header, "line_amount")
    date_column = _find_column(header, "order_date")
    group_column = _find_column(header, "product_group")
    quantity_column = _find_column(header, "quantity")
    base_quantity_column = _find_column(header, "base_quantity")
    rows = table.rows
    results: list[BusinessMetricRow] = []
    if order_column and amount_column:
        totals: dict[str, float] = {}
        status_by_order: dict[str, str] = {}
        dates_by_order: dict[str, str] = {}
        for row in rows:
            key = _text(row, order_column)
            if not key:
                continue
            amount = _number(row, amount_column)
            if amount is not None:
                totals[key] = totals.get(key, 0.0) + amount
            if key not in status_by_order:
                status_by_order[key] = _text(row, status_column)
                dates_by_order[key] = _text(row, date_column)
        amounts = [round(value, 6) for value in totals.values()]
        results.append(
            _row(
                table,
                "BUS01",
                "order_amounts",
                {"amounts": amounts},
                len(totals),
                "sum_line_amount_per_order_identifier",
                Status.PASS if amounts else Status.BLOCKED,
                "" if amounts else "no_valid_order_amount",
                "order",
                "VND",
            )
        )
    else:
        results.append(
            _row(
                table,
                "BUS01",
                "order_amounts",
                {"amounts": []},
                0,
                "sum_line_amount_per_order_identifier",
                Status.NOT_APPLICABLE,
                "missing_order_identifier_or_amount_column",
                "order",
                "VND",
            )
        )
    if status_column and order_column:
        counts: dict[str, int] = {}
        seen: set[str] = set()
        for row in rows:
            key = _text(row, order_column)
            if not key or key in seen:
                continue
            seen.add(key)
            label = classify_status(_text(row, status_column))
            counts[label] = counts.get(label, 0) + 1
        results.append(
            _row(
                table,
                "BUS04",
                "status_counts",
                {"counts": counts},
                len(seen),
                "one_status_label_per_distinct_order_identifier",
                Status.PASS if counts else Status.BLOCKED,
                "" if counts else "no_valid_order_status",
                "order",
                "order",
            )
        )
    else:
        results.append(
            _row(
                table,
                "BUS04",
                "status_counts",
                {"counts": {}},
                0,
                "one_status_label_per_distinct_order_identifier",
                Status.NOT_APPLICABLE,
                "missing_order_identifier_or_status_column",
                "order",
                "order",
            )
        )
    if date_column and amount_column and status_column:
        daily: dict[str, float] = {}
        counted = 0
        for row in rows:
            day = _day(row.get(date_column))
            if day is None:
                continue
            amount = _number(row, amount_column)
            if amount is None:
                continue
            if not revenue_eligible(_text(row, status_column)):
                continue
            key = day.isoformat()
            daily[key] = round(daily.get(key, 0.0) + amount, 6)
            counted += 1
        results.append(
            _row(
                table,
                "BUS02",
                "daily_revenue",
                {"daily": daily},
                counted,
                "rulebook_revenue_excluding_cancelled_and_returned_by_order_date",
                Status.PASS if daily else Status.BLOCKED,
                "" if daily else "no_revenue_eligible_rows_with_valid_date",
                "order_line",
                "VND",
            )
        )
    else:
        results.append(
            _row(
                table,
                "BUS02",
                "daily_revenue",
                {"daily": {}},
                0,
                "rulebook_revenue_excluding_cancelled_and_returned_by_order_date",
                Status.NOT_APPLICABLE,
                "missing_order_date_or_amount_or_status_column",
                "order_line",
                "VND",
            )
        )
    quantity_target = base_quantity_column or quantity_column
    if group_column and quantity_target:
        totals: dict[str, float] = {}
        counted = 0
        for row in rows:
            group = _text(row, group_column)
            quantity = _number(row, quantity_target)
            if not group or quantity is None:
                continue
            totals[group] = round(totals.get(group, 0.0) + quantity, 6)
            counted += 1
        results.append(
            _row(
                table,
                "BUS03",
                "quantity_by_product_group",
                {"totals": totals},
                counted,
                "sum_base_or_raw_quantity_per_product_group",
                Status.PASS if totals else Status.BLOCKED,
                ""
                if totals
                else (
                    "no_base_unit_quantity_column_available"
                    if base_quantity_column is None
                    else "no_valid_quantity_rows"
                ),
                "order_line",
                "base unit" if base_quantity_column else "source unit",
            )
        )
    else:
        results.append(
            _row(
                table,
                "BUS03",
                "quantity_by_product_group",
                {"totals": {}},
                0,
                "sum_base_or_raw_quantity_per_product_group",
                Status.NOT_APPLICABLE,
                "missing_product_group_or_quantity_column",
                "order_line",
                "source unit",
            )
        )
    return results


def _stock_metrics(table: LoadedTable) -> list[BusinessMetricRow]:
    header = table.header
    stock_column = _find_column(header, "stock_quantity")
    group_column = _find_column(header, "product_group")
    cost_column = _find_column(header, "cost_price")
    expiry_column = _find_column(header, "expiry_date")
    lot_column = _find_column(header, "lot_id")
    quantity_column = _find_column(header, "quantity")
    rows = table.rows
    results: list[BusinessMetricRow] = []
    if stock_column:
        quantities: list[float] = []
        for row in rows:
            value = _number(row, stock_column)
            if value is not None:
                quantities.append(value)
        results.append(
            _row(
                table,
                "BUS05",
                "stock_quantities",
                {"quantities": quantities},
                len(quantities),
                "closing_stock_quantity_per_snapshot_row",
                Status.PASS if quantities else Status.BLOCKED,
                "" if quantities else "no_valid_stock_quantity",
                "snapshot",
                "source unit",
            )
        )
    else:
        results.append(
            _row(
                table,
                "BUS05",
                "stock_quantities",
                {"quantities": []},
                0,
                "closing_stock_quantity_per_snapshot_row",
                Status.NOT_APPLICABLE,
                "missing_stock_quantity_column",
                "snapshot",
                "source unit",
            )
        )
    if stock_column and cost_column and group_column:
        totals: dict[str, float] = {}
        counted = 0
        for row in rows:
            quantity = _number(row, stock_column)
            cost = _number(row, cost_column)
            group = _text(row, group_column)
            if quantity is None or cost is None or not group:
                continue
            totals[group] = round(totals.get(group, 0.0) + quantity * cost, 6)
            counted += 1
        results.append(
            _row(
                table,
                "BUS06",
                "inventory_value_by_group",
                {"totals": totals},
                counted,
                "sum_closing_stock_quantity_times_unit_cost_per_product_group",
                Status.PASS if totals else Status.BLOCKED,
                "" if totals else "no_valid_stock_cost_rows",
                "snapshot",
                "VND",
            )
        )
    else:
        results.append(
            _row(
                table,
                "BUS06",
                "inventory_value_by_group",
                {"totals": {}},
                0,
                "sum_closing_stock_quantity_times_unit_cost_per_product_group",
                Status.NOT_APPLICABLE,
                "missing_stock_quantity_or_cost_or_product_group_column",
                "snapshot",
                "VND",
            )
        )
    if expiry_column and (stock_column or quantity_column):
        quantities_by_window: dict[str, float] = {}
        lot_count = 0
        for row in rows:
            expiry = _day(row.get(expiry_column))
            if expiry is None:
                continue
            quantity = _number(row, stock_column or quantity_column)
            if quantity is None:
                continue
            remaining = (expiry - date.today()).days
            label = "Đã quá hạn"
            for window in EXPIRY_WINDOW_DAYS:
                if 0 <= remaining <= window:
                    label = f"Trong {window} ngày"
                    break
            else:
                if remaining > EXPIRY_WINDOW_DAYS[-1]:
                    label = f"Trên {EXPIRY_WINDOW_DAYS[-1]} ngày"
            quantities_by_window[label] = round(
                quantities_by_window.get(label, 0.0) + quantity, 6
            )
            if lot_column and _text(row, lot_column):
                lot_count += 1
        results.append(
            _row(
                table,
                "BUS12",
                "expiry_window_quantities",
                {
                    "totals": quantities_by_window,
                    "lot_row_n": lot_count,
                    "as_of": date.today().isoformat(),
                },
                sum(1 for row in rows if _day(row.get(expiry_column))),
                "closing_stock_quantity_bucketed_by_remaining_shelf_life_days",
                Status.PASS if quantities_by_window else Status.BLOCKED,
                "" if quantities_by_window else "no_valid_expiry_rows",
                "lot_stock",
                "source unit",
            )
        )
    else:
        results.append(
            _row(
                table,
                "BUS12",
                "expiry_window_quantities",
                {"totals": {}, "lot_row_n": 0, "as_of": date.today().isoformat()},
                0,
                "closing_stock_quantity_bucketed_by_remaining_shelf_life_days",
                Status.NOT_APPLICABLE,
                "missing_expiry_date_or_stock_quantity_column",
                "lot_stock",
                "source unit",
            )
        )
    return results


def _debt_metrics(table: LoadedTable) -> list[BusinessMetricRow]:
    header = table.header
    debt_column = _find_column(header, "debt_balance")
    due_column = _find_column(header, "due_date")
    date_column = _find_column(header, "order_date")
    rows = table.rows
    results: list[BusinessMetricRow] = []
    if debt_column:
        balances: list[float] = []
        for row in rows:
            value = _number(row, debt_column)
            if value is not None and value > 0:
                balances.append(round(value, 6))
        results.append(
            _row(
                table,
                "BUS07",
                "debt_balances",
                {"balances": balances},
                len(balances),
                "positive_outstanding_balance_per_row",
                Status.PASS if balances else Status.BLOCKED,
                "" if balances else "no_positive_outstanding_balance",
                "snapshot",
                "VND",
            )
        )
    else:
        results.append(
            _row(
                table,
                "BUS07",
                "debt_balances",
                {"balances": []},
                0,
                "positive_outstanding_balance_per_row",
                Status.NOT_APPLICABLE,
                "missing_debt_balance_column",
                "snapshot",
                "VND",
            )
        )
    if debt_column and due_column:
        buckets: dict[str, float] = {}
        counted = 0
        for row in rows:
            balance = _number(row, debt_column)
            if balance is None or balance <= 0:
                continue
            due = _day(row.get(due_column))
            if due is None:
                continue
            age = (date.today() - due).days
            label = AGING_BUCKETS[0][0]
            for name, lower, upper in AGING_BUCKETS:
                if lower <= age <= upper:
                    label = name
                    break
            else:
                label = AGING_BUCKETS[-1][0]
            buckets[label] = round(buckets.get(label, 0.0) + balance, 6)
            counted += 1
        results.append(
            _row(
                table,
                "BUS08",
                "debt_aging_buckets",
                {"totals": buckets},
                counted,
                "outstanding_balance_summed_by_due_date_aging_bucket",
                Status.PASS if buckets else Status.BLOCKED,
                "" if buckets else "no_valid_debt_with_due_date",
                "snapshot",
                "VND",
            )
        )
    else:
        results.append(
            _row(
                table,
                "BUS08",
                "debt_aging_buckets",
                {"totals": {}},
                0,
                "outstanding_balance_summed_by_due_date_aging_bucket",
                Status.NOT_APPLICABLE,
                "missing_debt_balance_or_due_date_column",
                "snapshot",
                "VND",
            )
        )
    if date_column and debt_column and due_column:
        ages: list[int] = []
        for row in rows:
            balance = _number(row, debt_column)
            if balance is None or balance <= 0:
                continue
            ordered = _day(row.get(date_column))
            if ordered is None:
                continue
            ages.append((date.today() - ordered).days)
        results.append(
            _row(
                table,
                "BUS09",
                "debt_age_days",
                {"ages": ages},
                len(ages),
                "days_from_order_date_to_evaluation_date_for_outstanding_balance",
                Status.PASS if ages else Status.BLOCKED,
                "" if ages else "no_outstanding_balance_with_order_date",
                "snapshot",
                "day",
            )
        )
    else:
        results.append(
            _row(
                table,
                "BUS09",
                "debt_age_days",
                {"ages": []},
                0,
                "days_from_order_date_to_evaluation_date_for_outstanding_balance",
                Status.NOT_APPLICABLE,
                "missing_order_date_or_debt_balance_column",
                "snapshot",
                "day",
            )
        )
    return results


def _purchase_metrics(table: LoadedTable) -> list[BusinessMetricRow]:
    header = table.header
    purchase_column = _find_column(header, "purchase_id")
    amount_column = _find_column(header, "purchase_amount")
    supplier_column = _find_column(header, "supplier")
    rows = table.rows
    results: list[BusinessMetricRow] = []
    if purchase_column and amount_column:
        totals: dict[str, float] = {}
        for row in rows:
            key = _text(row, purchase_column)
            amount = _number(row, amount_column)
            if not key or amount is None:
                continue
            totals[key] = round(totals.get(key, 0.0) + amount, 6)
        results.append(
            _row(
                table,
                "BUS10",
                "purchase_totals",
                {"totals": list(totals.values())},
                len(totals),
                "sum_purchase_amount_per_purchase_identifier",
                Status.PASS if totals else Status.BLOCKED,
                "" if totals else "no_valid_purchase_amount",
                "purchase",
                "VND",
            )
        )
    else:
        results.append(
            _row(
                table,
                "BUS10",
                "purchase_totals",
                {"totals": []},
                0,
                "sum_purchase_amount_per_purchase_identifier",
                Status.NOT_APPLICABLE,
                "missing_purchase_identifier_or_amount_column",
                "purchase",
                "VND",
            )
        )
    if supplier_column and amount_column and purchase_column:
        totals: dict[str, float] = {}
        for row in rows:
            supplier = _text(row, supplier_column)
            amount = _number(row, amount_column)
            if not supplier or amount is None:
                continue
            totals[supplier] = round(totals.get(supplier, 0.0) + amount, 6)
        results.append(
            _row(
                table,
                "BUS11",
                "supplier_purchase_totals",
                {"totals": totals},
                len(totals),
                "sum_purchase_amount_per_supplier",
                Status.PASS if totals else Status.BLOCKED,
                "" if totals else "no_valid_supplier_amount_rows",
                "purchase",
                "VND",
            )
        )
    else:
        results.append(
            _row(
                table,
                "BUS11",
                "supplier_purchase_totals",
                {"totals": {}},
                0,
                "sum_purchase_amount_per_supplier",
                Status.NOT_APPLICABLE,
                "missing_supplier_or_purchase_amount_column",
                "purchase",
                "VND",
            )
        )
    return results


def _catalogue_metrics(table: LoadedTable) -> list[BusinessMetricRow]:
    header = table.header
    group_column = _find_column(header, "product_group")
    attribute_column = _find_column(header, "attribute")
    warranty_column = _find_column(header, "warranty")
    model_column = _find_column(header, "model")
    rows = table.rows
    results: list[BusinessMetricRow] = []
    if group_column and attribute_column:
        counts: dict[str, int] = {}
        counted = 0
        for row in rows:
            group = _text(row, group_column)
            attribute = _text(row, attribute_column)
            if not group or not attribute:
                continue
            counts[group] = counts.get(group, 0) + 1
            counted += 1
        results.append(
            _row(
                table,
                "BUS15",
                "product_attribute_counts",
                {"counts": counts},
                counted,
                "product_rows_with_declared_attribute_per_product_group",
                Status.PASS if counts else Status.BLOCKED,
                "" if counts else "no_product_rows_with_declared_attribute",
                "product",
                "product",
            )
        )
    else:
        results.append(
            _row(
                table,
                "BUS15",
                "product_attribute_counts",
                {"counts": {}},
                0,
                "product_rows_with_declared_attribute_per_product_group",
                Status.NOT_APPLICABLE,
                "missing_product_group_or_attribute_column",
                "product",
                "product",
            )
        )
    if warranty_column and model_column:
        counts: dict[str, int] = {}
        for row in rows:
            model = _text(row, model_column)
            warranty = _text(row, warranty_column)
            if not model or not warranty:
                continue
            counts[model] = counts.get(model, 0) + 1
        results.append(
            _row(
                table,
                "BUS13",
                "warranty_entries_by_model",
                {"counts": counts},
                sum(counts.values()),
                "catalogue_rows_with_declared_warranty_per_model",
                Status.PASS if counts else Status.BLOCKED,
                "" if counts else "no_catalogue_rows_with_warranty",
                "product",
                "product",
            )
        )
    else:
        results.append(
            _row(
                table,
                "BUS13",
                "warranty_entries_by_model",
                {"counts": {}},
                0,
                "catalogue_rows_with_declared_warranty_per_model",
                Status.NOT_APPLICABLE,
                "missing_model_or_warranty_column",
                "product",
                "product",
            )
        )
    return results


def _repair_metrics(table: LoadedTable) -> list[BusinessMetricRow]:
    header = table.header
    service_column = _find_column(header, "service_type")
    visit_column = _find_column(header, "visit_id")
    order_column = _find_column(header, "order_identifier")
    rows = table.rows
    results: list[BusinessMetricRow] = []
    key_column = visit_column or order_column
    if service_column and key_column:
        counts: dict[str, int] = {}
        seen: set[str] = set()
        for row in rows:
            key = _text(row, key_column)
            if not key or key in seen:
                continue
            seen.add(key)
            service = _text(row, service_column)
            if not service:
                continue
            counts[service] = counts.get(service, 0) + 1
        results.append(
            _row(
                table,
                "BUS14",
                "repair_service_counts",
                {"counts": counts},
                len(seen),
                "one_service_label_per_distinct_visit_identifier",
                Status.PASS if counts else Status.BLOCKED,
                "" if counts else "no_valid_repair_service_rows",
                "visit",
                "visit",
            )
        )
    else:
        results.append(
            _row(
                table,
                "BUS14",
                "repair_service_counts",
                {"counts": {}},
                0,
                "one_service_label_per_distinct_visit_identifier",
                Status.NOT_APPLICABLE,
                "missing_service_type_or_visit_identifier_column",
                "visit",
                "visit",
            )
        )
    return results


def compute_business_metric_rows(table: LoadedTable) -> tuple[BusinessMetricRow, ...]:
    rows: list[BusinessMetricRow] = []
    rows.extend(_order_metrics(table))
    rows.extend(_stock_metrics(table))
    rows.extend(_debt_metrics(table))
    rows.extend(_purchase_metrics(table))
    rows.extend(_catalogue_metrics(table))
    rows.extend(_repair_metrics(table))
    return tuple(rows)


def column_roles(header: Sequence[str]) -> Mapping[str, str]:
    mapping: dict[str, str] = {}
    for name in header:
        if not name:
            continue
        role = _match_role(name)
        if role:
            mapping[name] = role
    return mapping


def role_columns(header: Sequence[str], role: str) -> tuple[str, ...]:
    return _find_columns(header, role)
