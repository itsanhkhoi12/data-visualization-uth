from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any, Mapping

PLACEHOLDER_PATTERN = re.compile(r"\{([a-zA-Z0-9_]+)\}")

TEMPLATE_VERSION = "vietnamese_templates.v1"


@dataclass(frozen=True)
class Template:
    template_id: str
    text: str
    required_fields: tuple[str, ...]
    applies_to: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "template_id": self.template_id,
            "text": self.text,
            "required_fields": list(self.required_fields),
            "applies_to": self.applies_to,
        }


def format_number(value: Any, decimals: int = 2) -> str:
    if value is None:
        return ""
    if isinstance(value, bool):
        return "có" if value else "không"
    if isinstance(value, int):
        return f"{value:,}".replace(",", ".")
    if isinstance(value, float):
        if value != value:
            return ""
        if float(value).is_integer():
            return f"{int(value):,}".replace(",", ".")
        return f"{value:,.{decimals}f}".replace(",", "X").replace(".", ",").replace("X", ".")
    return str(value)


def format_percent(value: Any, decimals: int = 2) -> str:
    if value is None:
        return ""
    try:
        number = float(value)
    except (TypeError, ValueError):
        return ""
    if number != number:
        return ""
    return f"{number:,.{decimals}f}".replace(",", "X").replace(".", ",").replace("X", ".") + "%"


def format_integer(value: Any) -> str:
    if value is None:
        return ""
    try:
        number = int(value)
    except (TypeError, ValueError):
        return ""
    return f"{number:,}".replace(",", ".")


def escape_text(text: Any) -> str:
    return (
        str(text)
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


TEMPLATES: tuple[Template, ...] = (
    Template(
        template_id="NUM_DISTRIBUTION",
        text=(
            "Trong `{business_id}` thuộc split `{split}`, biến `{field_label}` có "
            "`{n_valid}` quan sát hợp lệ trên tổng `{n_total}` quan sát; trung vị "
            "`{median}` `{unit}`, khoảng tứ phân vị `{q1}`–`{q3}` với IQR `{iqr}`. "
            "Có `{outlier_n}` quan sát nằm ngoài ngưỡng IQR theo phương pháp "
            "`{method}`. Đây là cờ thống kê, chưa được xác định là bản ghi sai. "
            "Nguồn: `{artifact_id}`."
        ),
        required_fields=(
            "business_id",
            "split",
            "field_label",
            "n_valid",
            "n_total",
            "median",
            "q1",
            "q3",
            "iqr",
            "outlier_n",
            "method",
            "unit",
            "artifact_id",
        ),
        applies_to="numeric_distribution",
    ),
    Template(
        template_id="CAT_DISTRIBUTION",
        text=(
            "Trong `{business_id}` thuộc split `{split}`, trường phân loại "
            "`{field_label}` có `{n_valid}` quan sát hợp lệ trên `{n_total}`; "
            "`{top_category}` chiếm `{top_share}` với `{top_count}` quan sát, "
            "`{distinct_n}` giá trị khác nhau và entropy Shannon `{entropy}` bit. "
            "Nhóm ký hiệu `{others_label}` gộp các giá trị ngoài nhóm hiển thị. "
            "Nguồn: `{artifact_id}`."
        ),
        required_fields=(
            "business_id",
            "split",
            "field_label",
            "n_valid",
            "n_total",
            "top_category",
            "top_share",
            "top_count",
            "distinct_n",
            "entropy",
            "others_label",
            "artifact_id",
        ),
        applies_to="categorical_distribution",
    ),
    Template(
        template_id="BUSINESS_KPI",
        text=(
            "Trong `{business_id}` thuộc split `{split}`, chỉ số `{metric_label}` có "
            "giá trị `{value}` `{unit}` trên `{population_n}` quan sát ở grain "
            "`{grain}` theo phương pháp `{method}`. Bộ lọc trạng thái áp dụng: "
            "`{status_filter}`. Nguồn: `{artifact_id}`."
        ),
        required_fields=(
            "business_id",
            "split",
            "metric_label",
            "value",
            "unit",
            "population_n",
            "grain",
            "method",
            "status_filter",
            "artifact_id",
        ),
        applies_to="business_metric",
    ),
    Template(
        template_id="TEMPORAL_COVERAGE",
        text=(
            "Trong `{business_id}` thuộc split `{split}`, trường thời gian "
            "`{field_label}` ghi nhận `{n_valid}` mốc thời gian hợp lệ trong khoảng "
            "từ `{min_date}` đến `{max_date}`, trải trên `{active_days}` ngày có dữ "
            "liệu. Lịch tham chiếu lấy từ `calendar.csv` của split `{split}`. "
            "Nguồn: `{artifact_id}`."
        ),
        required_fields=(
            "business_id",
            "split",
            "field_label",
            "n_valid",
            "min_date",
            "max_date",
            "active_days",
            "artifact_id",
        ),
        applies_to="temporal_coverage",
    ),
    Template(
        template_id="QUALITY_MISSING",
        text=(
            "Trong `{business_id}` thuộc split `{split}`, trường `{field_label}` thiếu "
            "`{n_missing}` giá trị trên tổng `{n_total}`, tỷ lệ thiếu `{missing_ratio}`. "
            "Ô trống kế thừa trong nhóm dòng được xử lý theo quy ước của rulebook "
            "`{split}` và không được diễn giải là khách lẻ hay đơn hoàn thành. "
            "Nguồn: `{artifact_id}`."
        ),
        required_fields=(
            "business_id",
            "split",
            "field_label",
            "n_missing",
            "n_total",
            "missing_ratio",
            "artifact_id",
        ),
        applies_to="quality_missing",
    ),
    Template(
        template_id="RELATION_ASSOCIATION",
        text=(
            "Trong `{business_id}` thuộc split `{split}`, mức tương quan "
            "`{method}` giữa `{left_field}` và `{right_field}` là `{coefficient}` "
            "trên `{n_pairs}` cặp quan sát hợp lệ tại grain `{grain}`. Quan hệ này "
            "là tương quan, không phải quan hệ nhân quả; phép nối chỉ được dùng khi "
            "đã vượt qua kiểm soát fanout và orphan. Nguồn: `{artifact_id}`."
        ),
        required_fields=(
            "business_id",
            "split",
            "method",
            "left_field",
            "right_field",
            "coefficient",
            "n_pairs",
            "grain",
            "artifact_id",
        ),
        applies_to="relationship_association",
    ),
    Template(
        template_id="GLOBAL_COVERAGE",
        text=(
            "Trong split `{split}`, tổng số doanh nghiệp là `{business_count}` với "
            "`{pass_count}` trạng thái PASS, `{partial_count}` PARTIAL và "
            "`{blocked_count}` BLOCKED; `{source_file_count}` tệp nguồn đã được "
            "kiểm kê bằng hash nội dung. Số tệp và số đối tượng bảng không phải số "
            "giao dịch. Nguồn: `{artifact_id}`."
        ),
        required_fields=(
            "split",
            "business_count",
            "pass_count",
            "partial_count",
            "blocked_count",
            "source_file_count",
            "artifact_id",
        ),
        applies_to="global_coverage",
    ),
    Template(
        template_id="QUESTION_PROFILE",
        text=(
            "Split `{split}` chứa `{question_count}` câu hỏi với độ dài trung vị "
            "`{median_length}` ký tự; `{intent_count}` nhóm ý định được nhận diện "
            "và `{time_expression_count}` biểu thức thời gian được ghi nhận. Đây là "
            "siêu dữ liệu của câu hỏi; split public_test không có đáp án tham chiếu "
            "và không có đáp án nào được suy ra. Nguồn: `{artifact_id}`."
        ),
        required_fields=(
            "split",
            "question_count",
            "median_length",
            "intent_count",
            "time_expression_count",
            "artifact_id",
        ),
        applies_to="question_profile",
    ),
    Template(
        template_id="NOT_APPLICABLE",
        text=(
            "Biểu đồ `{chart_id}` không được dựng cho `{business_id}` thuộc split "
            "`{split}` vì `{reason}`. Không có biểu đồ nào được thay thế bằng dữ "
            "liệu không cùng điều kiện kiểm chứng."
        ),
        required_fields=("chart_id", "business_id", "split", "reason"),
        applies_to="not_applicable",
    ),
)

TEMPLATES_BY_ID: dict[str, Template] = {item.template_id: item for item in TEMPLATES}


def required_fields_for(template_id: str) -> tuple[str, ...]:
    template = TEMPLATES_BY_ID.get(template_id)
    return template.required_fields if template else ()


def render_template(
    template_id: str, values: Mapping[str, Any]
) -> str | None:
    template = TEMPLATES_BY_ID.get(template_id)
    if template is None:
        return None
    resolved: dict[str, str] = {}
    for field in template.required_fields:
        raw = values.get(field)
        if raw is None:
            return None
        text = str(raw).strip()
        if not text:
            return None
        resolved[field] = escape_text(text)
    rendered = template.text
    for field, text in resolved.items():
        rendered = rendered.replace("{" + field + "}", text)
    leftover = PLACEHOLDER_PATTERN.search(rendered)
    if leftover:
        return None
    return rendered


def template_ids() -> tuple[str, ...]:
    return tuple(item.template_id for item in TEMPLATES)
