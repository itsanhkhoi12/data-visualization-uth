from __future__ import annotations

import zipfile
from pathlib import Path

import pytest

from common.errors import LabelLeakageError, UnsafeOutputPath
from common.paths import (
    DatasetContext,
    assert_not_in_raw,
    assert_safe_output,
    resolve_source,
)
from readers.zip_reader import is_unsafe_member, list_zip_members, verify_archive


def _make_zip(path: Path, members: dict[str, bytes]) -> Path:
    with zipfile.ZipFile(path, "w") as archive:
        for name, payload in members.items():
            archive.writestr(name, payload)
    return path


def test_t001_corrupt_central_directory_is_rejected(tmp_path: Path) -> None:
    archive_path = _make_zip(tmp_path / "broken.zip", {"a.txt": b"payload"})
    payload = bytearray(archive_path.read_bytes())
    payload[-6:-2] = b"\x00\x00\x00\x00"
    archive_path.write_bytes(bytes(payload))
    with pytest.raises(Exception):
        verify_archive(archive_path)


def test_t002_unsafe_member_is_rejected(tmp_path: Path) -> None:
    assert is_unsafe_member("../escape.txt") is True
    assert is_unsafe_member("/absolute.txt") is True
    assert is_unsafe_member("safe/file.txt") is False
    archive_path = _make_zip(tmp_path / "slip.zip", {"../escape.txt": b"x"})
    verification = verify_archive(archive_path)
    assert verification.status == "FAIL"
    assert verification.unsafe_members == ("../escape.txt",)


def test_t002_list_zip_members_returns_names(tmp_path: Path) -> None:
    archive_path = _make_zip(tmp_path / "ok.zip", {"a.txt": b"a", "b/c.txt": b"c"})
    members = list_zip_members(archive_path)
    names = {member.member_name for member in members}
    assert "a.txt" in names
    assert "b/c.txt" in names
    verification = verify_archive(archive_path)
    assert verification.status == "PASS"
    assert verification.file_member_count == 2


def test_t003_output_inside_raw_root_is_blocked(tmp_path: Path) -> None:
    raw_root = tmp_path / "raw_data"
    raw_root.mkdir()
    with pytest.raises(UnsafeOutputPath):
        assert_not_in_raw(raw_root, raw_root / "output.json")
    allowed = tmp_path / "artifacts"
    assert assert_not_in_raw(raw_root, allowed / "run" / "x.json") == (
        allowed / "run" / "x.json"
    )


def test_t003_output_escaping_output_root_is_blocked(tmp_path: Path) -> None:
    root = tmp_path / "artifacts"
    root.mkdir()
    with pytest.raises(UnsafeOutputPath):
        assert_safe_output(root, tmp_path / "outside.json")
    assert assert_safe_output(root, root / "inside.json") == root / "inside.json"


def test_t004_workspace_root_must_contain_raw_and_src(tmp_path: Path) -> None:
    from common.config import discover_workspace_root

    with pytest.raises(Exception):
        discover_workspace_root(tmp_path)


def test_resolve_source_rejects_escape(tmp_path: Path) -> None:
    root = tmp_path / "split"
    root.mkdir()
    context = DatasetContext(
        split="train",
        root=root,
        rulebook_path=root / "rulebook.md",
        calendar_path=root / "calendar.csv",
        questions_path=root / "questions.jsonl",
        answers_path=None,
    )
    assert resolve_source(context, "data/biz_101/a.csv").name == "a.csv"
    with pytest.raises(UnsafeOutputPath):
        resolve_source(context, "../../escape.csv")


def test_t044_public_labels_are_forbidden(tmp_path: Path) -> None:
    root = tmp_path / "split"
    root.mkdir()
    context = DatasetContext(
        split="public_test",
        root=root,
        rulebook_path=root / "rulebook.md",
        calendar_path=root / "calendar.csv",
        questions_path=root / "questions.jsonl",
        answers_path=None,
    )
    assert context.has_labels is False
    with pytest.raises(LabelLeakageError):
        context.require_labels()
