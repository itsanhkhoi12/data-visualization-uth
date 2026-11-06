from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from common.errors import UnsafeOutputPath


@dataclass(frozen=True)
class DatasetContext:
    split: str
    root: Path
    rulebook_path: Path
    calendar_path: Path
    questions_path: Path
    answers_path: Path | None
    read_only: bool = True

    @property
    def business_root(self) -> Path:
        return self.root / "data"

    @property
    def has_labels(self) -> bool:
        return self.answers_path is not None and self.answers_path.exists()

    def require_labels(self) -> Path:
        if self.answers_path is None or not self.answers_path.exists():
            from common.errors import LabelLeakageError

            raise LabelLeakageError(
                f"split '{self.split}' has no reference answers; label access is forbidden"
            )
        return self.answers_path

    def business_ids(self) -> list[str]:
        if not self.business_root.exists():
            return []
        return sorted(path.name for path in self.business_root.iterdir() if path.is_dir())

    def business_root_path(self, business_id: str) -> Path:
        candidate = (self.business_root / business_id).resolve()
        base = self.business_root.resolve()
        if base not in candidate.parents and candidate != base:
            raise UnsafeOutputPath(f"business path escapes split root: {business_id}")
        return candidate


def resolve_source(context: DatasetContext, relative_path: str) -> Path:
    candidate = (context.root / relative_path).resolve()
    root = context.root.resolve()
    if root not in candidate.parents and candidate != root:
        raise UnsafeOutputPath(f"source path escapes split root: {relative_path}")
    return candidate


def assert_safe_output(output_root: Path, candidate: Path) -> Path:
    resolved_root = output_root.resolve()
    resolved_candidate = candidate.resolve()
    if resolved_root == resolved_candidate:
        raise UnsafeOutputPath(f"output path equals root: {candidate}")
    if resolved_root not in resolved_candidate.parents:
        raise UnsafeOutputPath(f"output path escapes allowed root: {candidate}")
    return resolved_candidate


def assert_not_in_raw(raw_root: Path, candidate: Path) -> Path:
    resolved_raw = raw_root.resolve()
    resolved_candidate = candidate.resolve()
    if resolved_raw == resolved_candidate or resolved_raw in resolved_candidate.parents:
        raise UnsafeOutputPath(f"output path is inside raw data root: {candidate}")
    return resolved_candidate
