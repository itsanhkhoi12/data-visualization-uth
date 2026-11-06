from __future__ import annotations

import json
from dataclasses import dataclass, field, replace
from pathlib import Path
from typing import Any

from common.enums import DatasetSplit
from common.errors import SourceMissing
from common.paths import DatasetContext, assert_not_in_raw


@dataclass(frozen=True)
class EdaConfig:
    workspace_root: Path
    raw_root: Path
    output_root: Path
    splits: tuple[str, ...] = (DatasetSplit.TRAIN.value, DatasetSplit.PUBLIC_TEST.value)
    business_filter: tuple[str, ...] = ()
    read_only: bool = True
    sampling_seed: int = 20261027
    read_chunk_size: int = 50_000
    max_render_rows: int = 200
    time_budget_seconds: float = 3600.0
    max_memory_mb: int = 8192
    plot_theme: str = "default"
    cache_policy: str = "content_hash_v1"
    run_id: str | None = None

    def with_run_id(self, run_id: str) -> "EdaConfig":
        return replace(self, run_id=run_id)

    def fingerprint(self) -> str:
        from common.provenance import fingerprint_mapping

        return fingerprint_mapping(
            {
                "raw_root": str(self.raw_root),
                "output_root": str(self.output_root),
                "splits": list(self.splits),
                "business_filter": list(self.business_filter),
                "read_only": self.read_only,
                "sampling_seed": self.sampling_seed,
                "read_chunk_size": self.read_chunk_size,
                "max_render_rows": self.max_render_rows,
                "time_budget_seconds": self.time_budget_seconds,
                "max_memory_mb": self.max_memory_mb,
                "plot_theme": self.plot_theme,
                "cache_policy": self.cache_policy,
            }
        )

    def split_root(self, split: str) -> Path:
        return self.raw_root / split

    def context_for(self, split: str) -> DatasetContext:
        root = self.split_root(split)
        if not root.exists():
            raise SourceMissing(f"split root not found: {root}")
        rulebook = root / "rulebook.md"
        calendar = root / "calendar.csv"
        questions = root / "questions.jsonl"
        answers = root / "answers.jsonl"
        if not rulebook.exists():
            raise SourceMissing(f"rulebook missing for split '{split}': {rulebook}")
        if not calendar.exists():
            raise SourceMissing(f"calendar missing for split '{split}': {calendar}")
        if not questions.exists():
            raise SourceMissing(f"questions missing for split '{split}': {questions}")
        return DatasetContext(
            split=split,
            root=root,
            rulebook_path=rulebook,
            calendar_path=calendar,
            questions_path=questions,
            answers_path=answers if answers.exists() else None,
            read_only=self.read_only,
        )


def discover_workspace_root(start: Path | None = None) -> Path:
    candidate = (start or Path(__file__).resolve()).resolve()
    for directory in [candidate, *candidate.parents]:
        if (directory / "raw_data").is_dir() and (directory / "src").is_dir():
            return directory
    raise SourceMissing(
        "workspace root not found: expected a directory containing raw_data/ and src/"
    )


def load_config(workspace_root: Path | None = None) -> EdaConfig:
    root = (workspace_root or discover_workspace_root()).resolve()
    raw_root = root / "raw_data"
    if not raw_root.is_dir():
        raise SourceMissing(f"raw_data root not found: {raw_root}")
    output_root = root / "src" / "eda" / "artifacts"
    assert_not_in_raw(raw_root, output_root)
    return EdaConfig(workspace_root=root, raw_root=raw_root, output_root=output_root)


def config_to_dict(config: EdaConfig) -> dict[str, Any]:
    payload = {
        "workspace_root": str(config.workspace_root),
        "raw_root": str(config.raw_root),
        "output_root": str(config.output_root),
        "splits": list(config.splits),
        "business_filter": list(config.business_filter),
        "read_only": config.read_only,
        "sampling_seed": config.sampling_seed,
        "read_chunk_size": config.read_chunk_size,
        "max_render_rows": config.max_render_rows,
        "time_budget_seconds": config.time_budget_seconds,
        "max_memory_mb": config.max_memory_mb,
        "plot_theme": config.plot_theme,
        "cache_policy": config.cache_policy,
        "run_id": config.run_id,
    }
    return payload


def write_config_snapshot(config: EdaConfig, target: Path) -> Path:
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(
        json.dumps(config_to_dict(config), ensure_ascii=False, indent=2), encoding="utf-8"
    )
    return target
