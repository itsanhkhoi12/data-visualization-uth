from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Sequence

from common.contracts import RelationEvidence
from common.enums import RelationStatus, Status

METHOD_VERSION = "join_eligibility.v1"
MAX_FANOUT = 1.0
APPROVED_STATUS = RelationStatus.APPROVED.value


@dataclass(frozen=True)
class JoinEligibility:
    relation_id: str
    split: str
    business_id: str
    left_source: str
    right_source: str
    join_keys: tuple[str, ...]
    eligible: bool
    status: Status
    reason: str
    fanout_factor: float
    duplicate_key_left: int
    duplicate_key_right: int
    key_null_left: int
    key_null_right: int
    unmatched_left_rows: int
    unmatched_right_rows: int
    matched_rows: int
    evidence: tuple[str, ...] = ()

    def to_dict(self) -> dict[str, Any]:
        return {
            "relation_id": self.relation_id,
            "split": self.split,
            "business_id": self.business_id,
            "left_source": self.left_source,
            "right_source": self.right_source,
            "join_keys": list(self.join_keys),
            "eligible": self.eligible,
            "status": self.status.value,
            "reason": self.reason,
            "fanout_factor": self.fanout_factor,
            "duplicate_key_left": self.duplicate_key_left,
            "duplicate_key_right": self.duplicate_key_right,
            "key_null_left": self.key_null_left,
            "key_null_right": self.key_null_right,
            "unmatched_left_rows": self.unmatched_left_rows,
            "unmatched_right_rows": self.unmatched_right_rows,
            "matched_rows": self.matched_rows,
            "evidence": list(self.evidence),
        }


def evaluate_join(evidence: RelationEvidence) -> JoinEligibility:
    reasons: list[str] = []
    if evidence.status != APPROVED_STATUS:
        reasons.append(f"relation_status_is_{evidence.status}")
    if evidence.duplicate_key_left or evidence.duplicate_key_right:
        reasons.append("duplicate_keys_may_cause_fanout")
    if evidence.key_null_left or evidence.key_null_right:
        reasons.append("null_join_keys_present")
    if evidence.fanout_factor > MAX_FANOUT:
        reasons.append("fanout_above_one_row")
    if evidence.unmatched_left_rows or evidence.unmatched_right_rows:
        reasons.append("unmatched_keys_present")
    eligible = not reasons
    return JoinEligibility(
        relation_id=evidence.relation_id,
        split=evidence.split,
        business_id=evidence.business_id,
        left_source=evidence.left_source,
        right_source=evidence.right_source,
        join_keys=tuple(evidence.join_keys),
        eligible=eligible,
        status=Status.PASS if eligible else Status.BLOCKED,
        reason=(
            "approved_join_without_fanout_or_orphan_evidence"
            if eligible
            else ";".join(reasons)
        ),
        fanout_factor=evidence.fanout_factor,
        duplicate_key_left=evidence.duplicate_key_left,
        duplicate_key_right=evidence.duplicate_key_right,
        key_null_left=evidence.key_null_left,
        key_null_right=evidence.key_null_right,
        unmatched_left_rows=evidence.unmatched_left_rows,
        unmatched_right_rows=evidence.unmatched_right_rows,
        matched_rows=evidence.matched_rows,
        evidence=tuple(evidence.evidence),
    )


def eligible_relations(
    evidences: Sequence[RelationEvidence],
) -> tuple[JoinEligibility, ...]:
    return tuple(evaluate_join(item) for item in evidences)


def blocked_reason_summary(
    eligibilities: Sequence[JoinEligibility],
) -> dict[str, int]:
    counts: dict[str, int] = {}
    for item in eligibilities:
        if item.eligible:
            continue
        for reason in item.reason.split(";"):
            if reason:
                counts[reason] = counts.get(reason, 0) + 1
    return dict(sorted(counts.items()))
