from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from readers.jsonl_reader import iterate_jsonl


@dataclass(frozen=True)
class TrainAnswerProfile:
    split: str
    answer_count: int
    unique_id_count: int
    duplicate_id_count: int
    unmatched_question_ids: int
    type_distribution: dict[str, int]
    alias_presence_count: int
    answer_shape_distribution: dict[str, int]
    numeric_sample_count: int
    percent_sample_count: int
    status: str
    notes: tuple[str, ...] = ()

    def to_dict(self) -> dict[str, Any]:
        return {
            "split": self.split,
            "answer_count": self.answer_count,
            "unique_id_count": self.unique_id_count,
            "duplicate_id_count": self.duplicate_id_count,
            "unmatched_question_ids": self.unmatched_question_ids,
            "type_distribution": dict(self.type_distribution),
            "alias_presence_count": self.alias_presence_count,
            "answer_shape_distribution": dict(self.answer_shape_distribution),
            "numeric_sample_count": self.numeric_sample_count,
            "percent_sample_count": self.percent_sample_count,
            "status": self.status,
            "notes": list(self.notes),
        }


def _shape_of(value: Any) -> str:
    if value is None:
        return "null"
    if isinstance(value, bool):
        return "boolean"
    if isinstance(value, (int, float)):
        return "scalar_number"
    if isinstance(value, str):
        return "scalar_string"
    if isinstance(value, list):
        if not value:
            return "empty_list"
        if all(isinstance(item, (int, float)) for item in value):
            return "numeric_list"
        if all(isinstance(item, str) for item in value):
            return "string_list"
        return "mixed_list"
    if isinstance(value, dict):
        return "object"
    return "unknown"


def profile_train_answers(
    answers_path: Path, questions_path: Path, split: str = "train"
) -> TrainAnswerProfile:
    answers = iterate_jsonl(answers_path)
    questions = iterate_jsonl(questions_path)
    question_ids = {str(record.get("id", "")) for record in questions}
    identifiers: list[str] = []
    type_distribution: dict[str, int] = {}
    shape_distribution: dict[str, int] = {}
    alias_presence = 0
    unmatched = 0
    numeric_samples = 0
    percent_samples = 0
    notes: list[str] = []
    for record in answers:
        identifier = str(record.get("id", ""))
        if identifier:
            identifiers.append(identifier)
        if identifier not in question_ids:
            unmatched += 1
        answer_type = str(record.get("type", "unknown"))
        type_distribution[answer_type] = type_distribution.get(answer_type, 0) + 1
        answer = record.get("answer")
        shape = _shape_of(answer)
        shape_distribution[shape] = shape_distribution.get(shape, 0) + 1
        alias = record.get("alias")
        if alias:
            alias_presence += 1
        if answer_type == "number":
            numeric_samples += 1
        elif answer_type == "percent":
            percent_samples += 1
    if unmatched:
        notes.append("answers_without_matching_question")
    return TrainAnswerProfile(
        split=split,
        answer_count=len(answers),
        unique_id_count=len(set(identifiers)),
        duplicate_id_count=len(identifiers) - len(set(identifiers)),
        unmatched_question_ids=unmatched,
        type_distribution=dict(sorted(type_distribution.items())),
        alias_presence_count=alias_presence,
        answer_shape_distribution=dict(sorted(shape_distribution.items())),
        numeric_sample_count=numeric_samples,
        percent_sample_count=percent_samples,
        status="PASS" if answers else "BLOCKED",
        notes=tuple(notes),
    )


def public_answers_are_forbidden(context: Any) -> bool:
    return not context.has_labels
