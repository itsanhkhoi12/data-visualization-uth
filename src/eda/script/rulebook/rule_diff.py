from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from rulebook.rule_registry import RuleRegistry


@dataclass(frozen=True)
class RuleDifference:
    conflict_id: str
    section: str
    train_rule_id: str | None
    public_rule_id: str | None
    train_text: str | None
    public_text: str | None
    conflict_status: str
    kind: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "conflict_id": self.conflict_id,
            "section": self.section,
            "train_rule_id": self.train_rule_id,
            "public_rule_id": self.public_rule_id,
            "train_text": self.train_text,
            "public_text": self.public_text,
            "conflict_status": self.conflict_status,
            "kind": self.kind,
        }


@dataclass(frozen=True)
class RuleDiffReport:
    train_rule_count: int
    public_rule_count: int
    common_rule_count: int
    train_only: tuple[RuleDifference, ...]
    public_only: tuple[RuleDifference, ...]
    modified: tuple[RuleDifference, ...]
    unchanged_count: int

    def to_dict(self) -> dict[str, Any]:
        return {
            "train_rule_count": self.train_rule_count,
            "public_rule_count": self.public_rule_count,
            "common_rule_count": self.common_rule_count,
            "train_only": [item.to_dict() for item in self.train_only],
            "public_only": [item.to_dict() for item in self.public_only],
            "modified": [item.to_dict() for item in self.modified],
            "unchanged_count": self.unchanged_count,
        }


def _normalize(text: str) -> str:
    return " ".join(text.split()).strip()


def compare_rulebooks(
    train: RuleRegistry, public: RuleRegistry
) -> RuleDiffReport:
    train_map = {rule.rule_label.strip(): rule for rule in train.rules}
    public_map = {rule.rule_label.strip(): rule for rule in public.rules}
    train_only: list[RuleDifference] = []
    public_only: list[RuleDifference] = []
    modified: list[RuleDifference] = []
    unchanged = 0
    for label, train_rule in train_map.items():
        public_rule = public_map.get(label)
        if public_rule is None:
            train_only.append(
                RuleDifference(
                    conflict_id=f"{train.split}.only.{label}",
                    section=train_rule.section,
                    train_rule_id=train_rule.rule_id,
                    public_rule_id=None,
                    train_text=train_rule.rule_text,
                    public_text=None,
                    conflict_status="TRAIN_ONLY",
                    kind="removed_in_public",
                )
            )
            continue
        if _normalize(train_rule.rule_text) == _normalize(public_rule.rule_text):
            unchanged += 1
            continue
        modified.append(
            RuleDifference(
                conflict_id=f"MOD.{label}",
                section=train_rule.section,
                train_rule_id=train_rule.rule_id,
                public_rule_id=public_rule.rule_id,
                train_text=train_rule.rule_text,
                public_text=public_rule.rule_text,
                conflict_status="SPLIT_SPECIFIC",
                kind="modified_text",
            )
        )
    for label, public_rule in public_map.items():
        if label not in train_map:
            public_only.append(
                RuleDifference(
                    conflict_id=f"{public.split}.only.{label}",
                    section=public_rule.section,
                    train_rule_id=None,
                    public_rule_id=public_rule.rule_id,
                    train_text=None,
                    public_text=public_rule.rule_text,
                    conflict_status="PUBLIC_ONLY",
                    kind="added_in_public",
                )
            )
    return RuleDiffReport(
        train_rule_count=len(train.rules),
        public_rule_count=len(public.rules),
        common_rule_count=len(set(train_map) & set(public_map)),
        train_only=tuple(train_only),
        public_only=tuple(public_only),
        modified=tuple(modified),
        unchanged_count=unchanged,
    )
