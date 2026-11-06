from __future__ import annotations

import ast
from pathlib import Path

import pytest

from business.business_inventory import build_business_profile
from common.enums import Status
from questions.alignment import profile_question_alignment
from questions.answer_profile import profile_train_answers, public_answers_are_forbidden
from questions.question_profile import (
    infer_intent,
    profile_questions,
    question_metadata_records,
)

FORBIDDEN_CALLS = {
    "groupby",
    "merge",
    "pivot_table",
    "read_csv",
    "read_excel",
    "execute",
    "cursor",
    "sql",
    "drop_duplicates",
    "fillna",
    "applymap",
    "corr",
    "describe",
}


def _write_questions(path: Path, count: int) -> None:
    lines = []
    for index in range(count):
        lines.append(
            '{"id": "q%d", "business_id": "biz_101", '
            '"question": "Doanh thu ngay 01/01/2025 la bao nhieu?", '
            '"as_of_date": "2025-01-31"}' % index
        )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def test_t043_question_profile_counts(tmp_path: Path) -> None:
    path = tmp_path / "questions.jsonl"
    _write_questions(path, 5)
    profile = profile_questions(path, "train")
    assert profile.question_count == 5
    assert profile.unique_id_count == 5
    assert profile.duplicate_id_count == 0
    assert profile.status == "PASS"


def test_question_metadata_records_are_split_scoped(tmp_path: Path) -> None:
    path = tmp_path / "questions.jsonl"
    _write_questions(path, 3)
    records = question_metadata_records(path, "public_test")
    assert all(record["split"] == "public_test" for record in records)
    assert all("question_length_characters" in record for record in records)


def test_t045_answer_type_counts_sum_to_total(tmp_path: Path) -> None:
    questions = tmp_path / "questions.jsonl"
    answers = tmp_path / "answers.jsonl"
    _write_questions(questions, 4)
    answers.write_text(
        '{"id": "q0", "type": "number", "answer": 1}\n'
        '{"id": "q1", "type": "string", "answer": "a"}\n'
        '{"id": "q2", "type": "number", "answer": 2}\n'
        '{"id": "q3", "type": "list", "answer": [1, 2]}\n',
        encoding="utf-8",
    )
    profile = profile_train_answers(answers, questions, "train")
    assert profile.answer_count == 4
    assert sum(profile.type_distribution.values()) == 4
    assert profile.unmatched_question_ids == 0


def test_t044_public_answers_are_forbidden(tmp_path: Path) -> None:
    from common.paths import DatasetContext

    root = tmp_path / "public_test"
    root.mkdir()
    context = DatasetContext(
        split="public_test",
        root=root,
        rulebook_path=root / "rulebook.md",
        calendar_path=root / "calendar.csv",
        questions_path=root / "questions.jsonl",
        answers_path=None,
    )
    assert public_answers_are_forbidden(context) is True


def test_alignment_flags_missing_business_source() -> None:
    entries = profile_question_alignment(
        split="train",
        question_metadata=[
            {"business_id": "biz_101", "intent_candidate": "revenue"},
            {"business_id": "biz_999", "intent_candidate": "revenue"},
        ],
        available_businesses=("biz_101",),
        has_labels=True,
    )
    by_business = {entry.business_id: entry for entry in entries}
    assert by_business["biz_101"].status == Status.PASS
    assert by_business["biz_999"].status == Status.PARTIAL
    assert by_business["biz_999"].businesses_without_source == 1


def test_intent_inference() -> None:
    assert infer_intent("doanh thu ngay 01/01/2025") != "other"
    assert infer_intent("") == "other"


def test_business_profile_without_readme_is_partial() -> None:
    profile = build_business_profile(
        business_id="biz_101",
        split="train",
        sources=(),
        readme_path=None,
        readme_hash="",
    )
    assert profile.status == Status.PARTIAL
    assert profile.domain_evidence is None


def test_t057_notebook_cells_have_no_heavy_processing() -> None:
    notebook_path = Path(__file__).resolve().parents[1] / "notebook" / "eda.ipynb"
    if not notebook_path.exists():
        pytest.skip("notebook not generated yet")
    import json

    notebook = json.loads(notebook_path.read_text(encoding="utf-8"))
    for cell in notebook["cells"]:
        if cell["cell_type"] != "code":
            continue
        source = cell["source"]
        if isinstance(source, list):
            source = "".join(source)
        tree = ast.parse(source)
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                function = node.func
                name = getattr(function, "attr", None) or getattr(function, "id", None)
                assert name not in FORBIDDEN_CALLS


def test_t056_notebook_has_seventeen_sections() -> None:
    from orchestration.notebook_builder import SECTIONS

    assert len(SECTIONS) == 17
    assert SECTIONS[0]["id"] == "00"
    assert SECTIONS[-1]["id"] == "16"
