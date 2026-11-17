from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Sequence

from common.contracts import RelationEvidence
from common.enums import Status


@dataclass(frozen=True)
class IntegrityEntry:
    source_id: str
    split: str
    business_id: str
    relation_id: str
    integrity_kind: str
    affected_count: int
    denominator: int
    ratio: float
    severity: str
    status: Status
    evidence: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "source_id": self.source_id,
            "split": self.split,
            "business_id": self.business_id,
            "relation_id": self.relation_id,
            "integrity_kind": self.integrity_kind,
            "affected_count": self.affected_count,
            "denominator": self.denominator,
            "ratio": self.ratio,
            "severity": self.severity,
            "status": self.status.value,
            "evidence": self.evidence,
        }


def profile_integrity(
    relations: Sequence[RelationEvidence],
) -> tuple[IntegrityEntry, ...]:
    entries: list[IntegrityEntry] = []
    for relation in relations:
        if relation.unmatched_left_rows:
            entries.append(
                IntegrityEntry(
                    source_id=relation.left_source,
                    split=relation.split,
                    business_id=relation.business_id,
                    relation_id=relation.relation_id,
                    integrity_kind="orphan_left_keys",
                    affected_count=relation.unmatched_left_rows,
                    denominator=relation.left_rows,
                    ratio=round(
                        relation.unmatched_left_rows / relation.left_rows, 6
                    )
                    if relation.left_rows
                    else 0.0,
                    severity="high" if relation.unmatched_left_rows > 0 else "low",
                    status=Status.PARTIAL,
                    evidence=(
                        f"{relation.unmatched_left_rows} distinct left keys have no right match "
                        f"on {list(relation.join_keys)}"
                    ),
                )
            )
        if relation.unmatched_right_rows:
            entries.append(
                IntegrityEntry(
                    source_id=relation.right_source,
                    split=relation.split,
                    business_id=relation.business_id,
                    relation_id=relation.relation_id,
                    integrity_kind="orphan_right_keys",
                    affected_count=relation.unmatched_right_rows,
                    denominator=relation.right_rows,
                    ratio=round(
                        relation.unmatched_right_rows / relation.right_rows, 6
                    )
                    if relation.right_rows
                    else 0.0,
                    severity="medium",
                    status=Status.PARTIAL,
                    evidence=(
                        f"{relation.unmatched_right_rows} distinct right keys are not referenced "
                        f"by the left table"
                    ),
                )
            )
        if relation.duplicate_key_left or relation.duplicate_key_right:
            entries.append(
                IntegrityEntry(
                    source_id=relation.left_source,
                    split=relation.split,
                    business_id=relation.business_id,
                    relation_id=relation.relation_id,
                    integrity_kind="fanout_risk",
                    affected_count=relation.duplicate_key_left
                    + relation.duplicate_key_right,
                    denominator=relation.left_rows + relation.right_rows,
                    ratio=round(relation.fanout_factor, 6),
                    severity="high",
                    status=Status.PARTIAL,
                    evidence=(
                        "duplicate keys on either side; a join multiplies rows and inflates "
                        "any measure aggregated after it"
                    ),
                )
            )
        if relation.key_null_left or relation.key_null_right:
            entries.append(
                IntegrityEntry(
                    source_id=relation.left_source,
                    split=relation.split,
                    business_id=relation.business_id,
                    relation_id=relation.relation_id,
                    integrity_kind="null_join_key",
                    affected_count=relation.key_null_left + relation.key_null_right,
                    denominator=relation.left_rows + relation.right_rows,
                    ratio=round(
                        (relation.key_null_left + relation.key_null_right)
                        / max(relation.left_rows + relation.right_rows, 1),
                        6,
                    ),
                    severity="medium",
                    status=Status.PARTIAL,
                    evidence="rows with null join keys are silently excluded from the join",
                )
            )
    return tuple(entries)
