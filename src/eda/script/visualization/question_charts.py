from __future__ import annotations

import unicodedata
from typing import Any

from common.enums import Status
from common.bundles import SplitBundle
from visualization.chart_context import BundleContext
from visualization.chart_data import ChartData

MAX_BUCKETS = 20
ABBREVIATION_TOKENS = ("ko", "kh", "vs", "khi", "n/a", "sl", "tb", "tt")


def _diacritic_ratio(text: str) -> bool:
    decomposed = unicodedata.normalize("NFD", text)
    return any(character.isalpha() and unicodedata.combining(character) for character in decomposed)


def _abbreviation_ratio(text: str) -> bool:
    lowered = f" {text.lower()} "
    return any(f" {token} " in lowered for token in ABBREVIATION_TOKENS)


def question_feature_rates(bundle: SplitBundle) -> dict[str, float]:
    metadata_rows = bundle.question_metadata
    if not metadata_rows:
        return {}
    total = len(metadata_rows)
    with_diacritics = 0
    with_abbreviation = 0
    with_time_expression = 0
    list_signal = 0
    boolean_signal = 0
    for record in metadata_rows:
        text = str(record.get("question", ""))
        if _diacritic_ratio(text):
            with_diacritics += 1
        if _abbreviation_ratio(text):
            with_abbreviation += 1
        if record.get("time_expressions"):
            with_time_expression += 1
        if record.get("is_list_signal"):
            list_signal += 1
        if record.get("is_boolean_signal"):
            boolean_signal += 1
    return {
        "Có dấu tiếng Việt": round(with_diacritics / total * 100.0, 6),
        "Có viết tắt": round(with_abbreviation / total * 100.0, 6),
        "Có biểu thức thời gian": round(with_time_expression / total * 100.0, 6),
        "Có tín hiệu trả về danh sách": round(list_signal / total * 100.0, 6),
        "Có tín hiệu trả về đúng/sai": round(boolean_signal / total * 100.0, 6),
    }


def build_question_charts(context: BundleContext) -> list[ChartData]:
    charts: list[ChartData] = []
    charts.extend(_length_chart(context))
    charts.extend(_feature_chart(context))
    charts.extend(_intent_chart(context))
    charts.extend(_time_expression_chart(context))
    return charts


def _length_chart(context: BundleContext) -> list[ChartData]:
    profile = context.bundle.question_profile
    lengths = list(context.bundle.question_lengths)
    if profile is None or not lengths:
        return []
    buckets = sorted(profile.length_buckets)
    return [
        ChartData(
            chart_id="QNA01",
            split=context.split,
            business_id="global",
            kind="boxplot",
            payload={
                "groups": [[float(value) for value in lengths]],
                "labels": [f"{context.split} (n={len(lengths)})"],
            },
            source_ids=(profile.split,),
            population_n=profile.question_count,
            sample_n=len(lengths),
            method="character_length_per_question",
            unit="characters",
            denominator_label="toàn bộ câu hỏi của split",
            title=f"Độ dài câu hỏi — {context.split}",
            x_label="Split",
            y_label="Độ dài câu hỏi (ký tự)",
            limitations=("character count is tokenizer dependent",),
            metadata={
                "caption": (
                    f"Độ dài câu hỏi của {profile.question_count} câu hỏi ở split "
                    f"{context.split}; median {profile.length_characters_median} ký tự."
                ),
                "length_buckets": dict(profile.length_buckets),
                "buckets": buckets,
            },
        )
    ]


def _feature_chart(context: BundleContext) -> list[ChartData]:
    profile = context.bundle.question_profile
    if profile is None or not profile.question_count:
        return []
    metadata_rows = context.bundle.question_metadata
    if not metadata_rows:
        return []
    total = len(metadata_rows)
    rates = question_feature_rates(context.bundle)
    labels = list(rates)
    values = [rates[name] for name in labels]
    return [
        ChartData(
            chart_id="QNA02",
            split=context.split,
            business_id="global",
            kind="bar",
            payload={"labels": labels, "values": values},
            source_ids=(profile.split,),
            population_n=total,
            sample_n=total,
            method="heuristic_text_feature_rates",
            unit="percent",
            denominator_label="toàn bộ câu hỏi của split",
            title=f"Đặc trưng văn phong câu hỏi — {context.split}",
            x_label="Đặc trưng",
            y_label="Tỷ trọng câu hỏi (%)",
            limitations=(
                "the features are heuristic rules and are not human annotation",
                "a question may carry several features at once",
            ),
            metadata={
                "caption": (
                    f"Tỷ trọng câu hỏi theo đặc trưng heuristic ở split {context.split}; "
                    f"mẫu số {total} câu hỏi."
                )
            },
        )
    ]


def _intent_chart(context: BundleContext) -> list[ChartData]:
    profile = context.bundle.question_profile
    if profile is None or not profile.intent_candidates:
        return []
    ordered = sorted(
        profile.intent_candidates.items(), key=lambda item: (-item[1], item[0])
    )
    labels = [item[0] for item in ordered]
    values = [float(item[1]) for item in ordered]
    return [
        ChartData(
            chart_id="QNA03",
            split=context.split,
            business_id="global",
            kind="bar",
            payload={"labels": labels, "values": values},
            source_ids=(profile.split,),
            population_n=profile.question_count,
            sample_n=len(labels),
            method="rule_based_intent_distribution",
            unit="question",
            denominator_label="toàn bộ câu hỏi của split",
            title=f"Phân phối ý định câu hỏi — {context.split}",
            x_label="Ý định (nhãn suy ra bằng luật)",
            y_label="Số câu hỏi",
            limitations=(
                "intent labels are rule-based heuristics, not human annotation",
                "the unclassified bucket is part of the population",
            ),
            metadata={
                "caption": (
                    f"Phân phối ý định suy ra bằng luật cho {profile.question_count} câu hỏi ở "
                    f"split {context.split}; nhóm chưa phân loại được giữ nguyên trong mẫu số."
                )
            },
        )
    ]


def _time_expression_chart(context: BundleContext) -> list[ChartData]:
    profile = context.bundle.question_profile
    if profile is None or not profile.time_expression_counts:
        return []
    ordered = sorted(
        profile.time_expression_counts.items(), key=lambda item: (-item[1], item[0])
    )[:MAX_BUCKETS]
    labels = [item[0] for item in ordered]
    values = [float(item[1]) for item in ordered]
    return [
        ChartData(
            chart_id="QNA03",
            split=context.split,
            business_id="global",
            kind="bar",
            payload={"labels": labels, "values": values},
            source_ids=(profile.split,),
            population_n=profile.question_count,
            sample_n=len(labels),
            method="keyword_annotated_time_expression_counts",
            unit="question",
            denominator_label="toàn bộ câu hỏi của split",
            title=f"Biểu thức thời gian trong câu hỏi — {context.split}",
            x_label="Biểu thức thời gian",
            y_label="Số câu hỏi",
            limitations=("multi-label: one question may carry several expressions",),
            metadata={
                "caption": (
                    "Số câu hỏi chứa từng biểu thức thời gian; đây là gắn nhãn nhiều nhãn."
                )
            },
        )
    ]


def build_answer_charts(context: BundleContext) -> list[ChartData]:
    charts: list[ChartData] = []
    profile = context.bundle.answer_profile
    if profile is None:
        return charts
    if profile.type_distribution:
        ordered = sorted(
            profile.type_distribution.items(), key=lambda item: (-item[1], item[0])
        )
        charts.append(
            ChartData(
                chart_id="QNA04",
                split=context.split,
                business_id="global",
                kind="bar",
                payload={
                    "labels": [item[0] for item in ordered],
                    "values": [float(item[1]) for item in ordered],
                },
                source_ids=(profile.split,),
                population_n=profile.answer_count,
                sample_n=len(ordered),
                method="answer_type_counts",
                unit="answer",
                denominator_label="toàn bộ đáp án tham chiếu của split train",
                title="Cơ cấu kiểu đáp án tham chiếu Train",
                x_label="Kiểu đáp án",
                y_label="Số đáp án",
                limitations=(
                    "reference answers exist only for the train split",
                    "no raw answer content is exposed",
                ),
                metadata={
                    "caption": (
                        f"{profile.answer_count} đáp án tham chiếu train phân bố theo kiểu; "
                        "chỉ siêu dữ liệu tổng hợp được hiển thị."
                    )
                },
            )
        )
    if profile.answer_shape_distribution:
        ordered = sorted(
            profile.answer_shape_distribution.items(), key=lambda item: (-item[1], item[0])
        )
        charts.append(
            ChartData(
                chart_id="QNA05",
                split=context.split,
                business_id="global",
                kind="bar",
                payload={
                    "labels": [item[0] for item in ordered],
                    "values": [float(item[1]) for item in ordered],
                },
                source_ids=(profile.split,),
                population_n=profile.answer_count,
                sample_n=len(ordered),
                method="structured_answer_shape_distribution",
                unit="answer",
                denominator_label="toàn bộ đáp án tham chiếu của split train",
                title="Cỡ hình dạng cấu trúc đáp án Train",
                x_label="Hình dạng đáp án",
                y_label="Số đáp án",
                limitations=("no raw answer content is exposed",),
                metadata={
                    "caption": (
                        f"Phân phối hình dạng cấu trúc của {profile.answer_count} đáp án tham "
                        "chiếu train; nội dung thô không được hiển thị."
                    )
                },
            )
        )
    labels = ["Có bí danh", "Số đáp án"]
    values = [float(profile.alias_presence_count), float(profile.answer_count)]
    charts.append(
        ChartData(
            chart_id="QNA06",
            split=context.split,
            business_id="global",
            kind="bar",
            payload={"labels": labels, "values": values},
            source_ids=(profile.split,),
            population_n=profile.answer_count,
            sample_n=len(labels),
            method="alias_and_answer_counts",
            unit="answer",
            denominator_label="toàn bộ đáp án tham chiếu của split train",
            title="Phân bố bí danh và số đáp án Train",
            x_label="Loại đếm",
            y_label="Số đáp án",
            limitations=(
                "no answer lookup by question id is constructed",
                "reference answers are used for metadata only",
            ),
            metadata={
                "caption": (
                    f"{profile.alias_presence_count} đáp án có bí danh trong tổng "
                    f"{profile.answer_count} đáp án tham chiếu train."
                )
            },
        )
    )
    return charts


def question_summary_rows(context: BundleContext) -> list[dict[str, Any]]:
    profile = context.bundle.question_profile
    if profile is None:
        return []
    rows: list[dict[str, Any]] = []
    for business_id, count in profile.business_distribution.items():
        rows.append(
            {
                "business_id": business_id,
                "question_count": count,
                "split": context.split,
                "share_of_split": round(
                    count / profile.question_count if profile.question_count else 0.0, 6
                ),
            }
        )
    return rows


def question_not_applicable(
    context: BundleContext, chart_id: str, reason: str
) -> ChartData:
    return ChartData(
        chart_id=chart_id,
        split=context.split,
        business_id="global",
        kind="bar",
        payload={"labels": [], "values": []},
        source_ids=(),
        population_n=0,
        sample_n=None,
        method="not_applicable",
        unit="question",
        denominator_label="không áp dụng",
        title="Biểu đồ không áp dụng",
        x_label="",
        y_label="",
        status=Status.NOT_APPLICABLE,
        reason=reason,
        metadata={"caption": reason},
    )
