from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Mapping, Sequence

from common.enums import Status
from common.visual_contracts import Finding, StoryCard
from reporting.evidence_findings import ProvenanceRef
from reporting.vietnamese_templates import escape_text

STORY_CARD_VERSION = "story_cards.v1"
STEP_ORDER = (
    "Mục tiêu",
    "Bối cảnh",
    "Phương pháp",
    "Bảng thống kê",
    "Biểu đồ",
    "Nhận xét",
    "Ý nghĩa",
    "Hạn chế",
    "Kết luận",
)


@dataclass
class StoryCardSet:
    cards: list[StoryCard] = field(default_factory=list)

    def add(self, card: StoryCard) -> None:
        self.cards.append(card)

    def for_chart(self, chart_id: str) -> list[StoryCard]:
        return [item for item in self.cards if item.chart_id == chart_id]

    def for_split(self, split: str) -> list[StoryCard]:
        return [item for item in self.cards if item.split == split]

    def to_dict(self) -> dict[str, Any]:
        return {
            "story_card_version": STORY_CARD_VERSION,
            "card_count": len(self.cards),
            "cards": [item.to_dict() for item in self.cards],
        }


def _statistics_lines(
    population_n: int | None,
    valid_n: int | None,
    unit: str,
    extra: Sequence[str] = (),
) -> tuple[str, ...]:
    lines: list[str] = []
    if population_n is not None:
        lines.append(f"population_n = {population_n}")
    if valid_n is not None:
        lines.append(f"n_valid = {valid_n}")
    if unit:
        lines.append(f"đơn vị = {unit}")
    lines.extend(extra)
    return tuple(lines)


def _confidence_for(card_findings: Sequence[Finding]) -> str:
    if not card_findings:
        return "NEEDS_REVIEW"
    confidences = {item.confidence for item in card_findings}
    if "NEEDS_REVIEW" in confidences:
        return "NEEDS_REVIEW"
    if confidences == {"VERIFIED"}:
        return "VERIFIED"
    return "PARTIAL"


def build_story_card(
    chart_id: str,
    split: str,
    business_id: str,
    research_question: str,
    context: Mapping[str, Any],
    methodology: Mapping[str, Any],
    statistic_lines: Sequence[str],
    figure_reference: str,
    findings: Sequence[Finding],
    implications: str,
    limitations: Sequence[str],
    conclusion: str,
    evidence_refs: Sequence[str],
) -> StoryCard:
    objective = research_question or "Chưa đủ bằng chứng để đặt câu hỏi nghiên cứu."
    context_text = (
        f"split = {split}; doanh nghiệp = {business_id}; "
        f"nguồn = {context.get('source_ids', '') or 'không có nguồn liên quan'}; "
        f"đơn vị quan sát = {context.get('grain', 'không xác định')}"
    )
    method_text = (
        f"phương pháp = {methodology.get('method', 'không xác định')}; "
        f"quy tắc lọc = {methodology.get('filter', 'không áp dụng')}; "
        f"xử lý giá trị khuyết = {methodology.get('missing_handling', 'không áp dụng')}; "
        f"xử lý ngoại lệ = {methodology.get('outlier_handling', 'giữ và gắn cờ')}"
    )
    observation_lines = tuple(item.claim for item in findings) or (
        "Chưa đủ bằng chứng hoặc điều kiện kiểm chứng để đưa ra nhận xét.",
    )
    limitation_lines = tuple(limitations) or (
        "Chưa đủ bằng chứng để đánh giá hạn chế; mọi phát biểu chỉ mô tả số liệu quan sát.",
    )
    confidence = _confidence_for(findings)
    status = Status.VERIFIED if confidence == "VERIFIED" else Status.PARTIAL
    return StoryCard(
        story_id=f"STORY.{chart_id}.{split}.{business_id}",
        chart_id=chart_id,
        split=split,
        business_id=business_id,
        objective=objective,
        context=context_text,
        methodology=method_text,
        statistics=_statistics_lines(
            context.get("population_n"),
            context.get("valid_n"),
            str(context.get("unit", "")),
            statistic_lines,
        ),
        figure_reference=figure_reference,
        observations=observation_lines,
        implications=implications,
        limitations=limitation_lines,
        conclusion=conclusion,
        evidence_refs=tuple(evidence_refs),
        confidence=confidence,
        status=status,
    )


def render_story_cards(
    cards: Sequence[StoryCard],
    findings_by_chart: Mapping[str, Sequence[Finding]],
    chart_questions: Mapping[str, str],
    provenance: Mapping[str, ProvenanceRef],
) -> StoryCardSet:
    result = StoryCardSet()
    for card in cards:
        card_findings = tuple(findings_by_chart.get(card.chart_id, ()))
        reference = provenance.get(card.chart_id)
        context = {
            "source_ids": reference.source_ids if reference else (),
            "grain": "order",
            "population_n": reference.population_n if reference else None,
            "valid_n": reference.population_n if reference else None,
            "unit": "",
        }
        methodology = {
            "method": reference.method if reference else "chưa xác định",
            "filter": "theo rulebook của split",
            "missing_handling": "loại khỏi phép đo và báo cáo số lượng",
            "outlier_handling": "giữ và gắn cờ thống kê",
        }
        statistic_lines = ()
        if reference is not None:
            statistic_lines = (
                f"phương pháp = {reference.method}",
                f"phiên bản phương pháp = {reference.method_version}",
            )
        evidence_refs = []
        if reference is not None:
            evidence_refs.append(reference.artifact_id)
            evidence_refs.extend(reference.source_hashes)
        rebuilt = build_story_card(
            chart_id=card.chart_id,
            split=card.split,
            business_id=card.business_id,
            research_question=chart_questions.get(card.chart_id, card.objective),
            context=context,
            methodology=methodology,
            statistic_lines=statistic_lines,
            figure_reference=card.figure_reference,
            findings=card_findings,
            implications=card.implications,
            limitations=card.limitations,
            conclusion=card.conclusion,
            evidence_refs=evidence_refs,
        )
        result.add(rebuilt)
    return result


def story_card_markdown(card: StoryCard) -> str:
    lines = [
        f"#### Thẻ chuyện `{card.chart_id}` — {card.business_id} ({card.split})",
        "",
        f"1. **Mục tiêu:** {card.objective}",
        f"2. **Bối cảnh:** {card.context}",
        f"3. **Phương pháp:** {card.methodology}",
        "4. **Bảng thống kê:**",
    ]
    lines.extend(f"   - {item}" for item in card.statistics)
    lines.append(f"5. **Biểu đồ:** {card.figure_reference}")
    lines.append("6. **Nhận xét:**")
    lines.extend(f"   - {escape_text(item)}" for item in card.observations)
    lines.append(f"7. **Ý nghĩa:** {escape_text(card.implications)}")
    lines.append("8. **Hạn chế:**")
    lines.extend(f"   - {escape_text(item)}" for item in card.limitations)
    lines.append(f"9. **Kết luận:** {escape_text(card.conclusion)}")
    lines.append("")
    lines.append(
        f"*Mức tin cậy: {card.confidence}; trạng thái: {card.status.value}.*"
    )
    return "\n".join(lines)
