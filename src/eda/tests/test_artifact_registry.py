from __future__ import annotations

import json
from pathlib import Path

import pytest

from common.enums import Status
from reporting.artifact_registry import ArtifactWriter, load_registry, verify_artifact


def _writer(tmp_path: Path) -> ArtifactWriter:
    return ArtifactWriter(
        run_id="run_test",
        output_root=tmp_path,
        source_hashes={"src_1": "sha256:abc"},
        rule_hash="rule_hash",
        config_hash="config_hash",
    )


def test_t054_manifest_records_lineage(tmp_path: Path) -> None:
    writer = _writer(tmp_path)
    manifest = writer.write_json(
        relative_path="data/out.json",
        payload={"value": 1},
        artifact_id="data.out",
        artifact_kind="data",
        split="train",
        business_id="biz_101",
        source_id="src_1",
        method_name="test.method",
        method_version="test.v1",
        population_size=10,
        observed_n=10,
    )
    assert manifest.source_hash == "sha256:abc"
    assert manifest.rule_hash == "rule_hash"
    assert manifest.config_hash == "config_hash"
    assert manifest.content_checksum.startswith("sha256:")
    assert manifest.status == Status.PASS


def test_t054_checksum_detects_stale_artifact(tmp_path: Path) -> None:
    writer = _writer(tmp_path)
    manifest = writer.write_json(
        relative_path="data/out.json",
        payload={"value": 1},
        artifact_id="data.out",
        artifact_kind="data",
        split="train",
        business_id="biz_101",
        source_id="src_1",
        method_name="test.method",
        method_version="test.v1",
    )
    valid, reason = verify_artifact(tmp_path, manifest)
    assert valid is True
    assert reason == "PASS"
    (tmp_path / manifest.output_relpath).write_text("tampered", encoding="utf-8")
    valid, reason = verify_artifact(tmp_path, manifest)
    assert valid is False
    assert reason == "checksum_mismatch"


def test_t055_failed_run_leaves_partial_manifest(tmp_path: Path) -> None:
    writer = _writer(tmp_path)
    writer.write_json(
        relative_path="data/first.json",
        payload={"value": 1},
        artifact_id="data.first",
        artifact_kind="data",
        split="train",
        business_id="biz_101",
        source_id="src_1",
        method_name="test.method",
        method_version="test.v1",
    )
    with pytest.raises(Exception):
        writer.write_json(
            relative_path="../escape.json",
            payload={"value": 2},
            artifact_id="data.escape",
            artifact_kind="data",
            split="train",
            business_id="biz_101",
            source_id="src_1",
            method_name="test.method",
            method_version="test.v1",
        )
    registry_path = writer.persist_registry()
    assert registry_path.exists()
    payload = json.loads(registry_path.read_text(encoding="utf-8"))
    assert len(payload["entries"]) == 1
    assert payload["entries"][0]["artifact_id"] == "data.first"
    assert not (tmp_path.parent / "escape.json").exists()


def test_registry_round_trip(tmp_path: Path) -> None:
    writer = _writer(tmp_path)
    writer.write_json(
        relative_path="data/out.json",
        payload={"value": 1},
        artifact_id="data.out",
        artifact_kind="data",
        split="train",
        business_id="biz_101",
        source_id="src_1",
        method_name="test.method",
        method_version="test.v1",
    )
    writer.persist_registry()
    registry = load_registry(tmp_path)
    assert registry.run_id == "run_test"
    assert registry.artifact("data.out") is not None
