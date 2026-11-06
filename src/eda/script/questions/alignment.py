from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping, Sequence

from common.enums import Status


@dataclass(frozen=True)
class AlignmentEntry:
    split: str
    business_id: str
    question_count: int
    businesses_without_source: int
    intent_distribution: dict[str, int]
    metadata_only: bool
    label_access: str
    status: Status
    notes: tuple[str, ...] = ()

    def to_dict(self) -> dict[str, Any]:
        return {
            "split": self.split,
            "business_id": self.business_id,
            "question_count": self.question_count,
            "businesses_without_source": self.businesses_without_source,
            "intent_distribution": dict(self.intent_distribution),
            "metadata_only": self.metadata_only,
            "label_access": self.label_access,
            "status": self.status.value,
            "notes": list(self.notes),
        }


def profile_question_alignment(
    split: str,
    question_metadata: Sequence[Mapping[str, Any]],
    available_businesses: Sequence[str],
    has_labels: bool,
) -> tuple[AlignmentEntry, ...]:
    known = set(available_businesses)
    by_business: dict[str, list[Mapping[str, Any]]] = {}
    for record in question_metadata:
        by_business.setdefault(str(record.get("business_id", "")), []).append(record)
    entries: list[AlignmentEntry] = []
    for business_id in sorted(by_business):
        records = by_business[business_id]
        intent_distribution: dict[str, int] = {}
        for record in records:
            intent = str(record.get("intent_candidate", "other"))
            intent_distribution[intent] = intent_distribution.get(intent, 0) + 1
        missing_source = business_id not in known
        notes: list[str] = []
        if missing_source:
            notes.append("no_source_for_business_in_this_split")
        entries.append(
            AlignmentEntry(
                split=split,
                business_id=business_id,
                question_count=len(records),
                businesses_without_source=1 if missing_source else 0,
                intent_distribution=dict(sorted(intent_distribution.items())),
                metadata_only=True,
                label_access="train_reference_available" if has_labels else "no_labels_for_split",
                status=Status.PARTIAL if missing_source else Status.PASS,
                notes=tuple(notes),
            )
        )
    return tuple(entries)
