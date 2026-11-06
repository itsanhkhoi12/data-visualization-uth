from __future__ import annotations

import json
import os
import tempfile
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Sequence

from common.contracts import ArtifactManifest
from common.enums import Status
from common.paths import assert_safe_output
from common.provenance import fingerprint_bytes

REGISTRY_FILENAME = "artifact_registry.json"
MANIFEST_FILENAME = "run_manifest.json"


@dataclass(frozen=True)
class ArtifactRegistry:
    run_id: str
    output_root: Path
    entries: tuple[ArtifactManifest, ...]

    def to_dict(self) -> dict[str, Any]:
        return {
            "run_id": self.run_id,
            "output_root": str(self.output_root),
            "entries": [entry.to_dict() for entry in self.entries],
        }

    def artifact(self, artifact_id: str) -> ArtifactManifest | None:
        for entry in self.entries:
            if entry.artifact_id == artifact_id:
                return entry
        return None


class ArtifactWriter:
    def __init__(
        self,
        run_id: str,
        output_root: Path,
        source_hashes: dict[str, str],
        rule_hash: str,
        config_hash: str,
    ) -> None:
        self.run_id = run_id
        self.output_root = output_root.resolve()
        self.source_hashes = source_hashes
        self.rule_hash = rule_hash
        self.config_hash = config_hash
        self.entries: list[ArtifactManifest] = []

    def target_path(self, relative_path: str) -> Path:
        candidate = (self.output_root / relative_path).resolve()
        return assert_safe_output(self.output_root, candidate)

    def write_bytes(
        self,
        relative_path: str,
        payload: bytes,
        artifact_id: str,
        artifact_kind: str,
        split: str,
        business_id: str,
        source_id: str,
        method_name: str,
        method_version: str,
        population_size: int | None,
        observed_n: int,
        sampled_n: int | None,
        sample_strategy: str,
        skipped_n: int,
        status: Status,
        evidence_refs: Sequence[str] = (),
        parent_artifact_ids: Sequence[str] = (),
        privacy_classification: str = "aggregated_metadata",
        qa_gate: str = "IMP-13",
    ) -> ArtifactManifest:
        target = self.target_path(relative_path)
        target.parent.mkdir(parents=True, exist_ok=True)
        with tempfile.NamedTemporaryFile(
            dir=target.parent, delete=False
        ) as handle:
            handle.write(payload)
            temporary = Path(handle.name)
        os.replace(temporary, target)
        manifest = ArtifactManifest(
            run_id=self.run_id,
            artifact_id=artifact_id,
            split=split,
            business_id=business_id,
            source_id=source_id,
            source_hash=self.source_hashes.get(source_id, ""),
            rule_hash=self.rule_hash,
            config_hash=self.config_hash,
            method_name=method_name,
            method_version=method_version,
            population_size=population_size,
            observed_n=observed_n,
            sampled_n=sampled_n,
            sample_strategy=sample_strategy,
            skipped_n=skipped_n,
            status=status,
            generation_ts=datetime.now(timezone.utc).isoformat(),
            output_relpath=str(target.relative_to(self.output_root)),
            evidence_refs=tuple(evidence_refs),
            parent_artifact_ids=tuple(parent_artifact_ids),
            privacy_classification=privacy_classification,
            content_checksum=fingerprint_bytes(payload),
            qa_gate=qa_gate,
            artifact_kind=artifact_kind,
        )
        self.entries.append(manifest)
        return manifest

    def write_json(
        self,
        relative_path: str,
        payload: Any,
        artifact_id: str,
        artifact_kind: str,
        split: str,
        business_id: str,
        source_id: str,
        method_name: str,
        method_version: str,
        population_size: int | None = None,
        observed_n: int = 0,
        sampled_n: int | None = None,
        sample_strategy: str = "not_applicable",
        skipped_n: int = 0,
        status: Status = Status.PASS,
        evidence_refs: Sequence[str] = (),
        parent_artifact_ids: Sequence[str] = (),
        privacy_classification: str = "aggregated_metadata",
        qa_gate: str = "IMP-13",
    ) -> ArtifactManifest:
        serialized = json.dumps(payload, ensure_ascii=False, indent=2, default=str)
        return self.write_bytes(
            relative_path=relative_path,
            payload=serialized.encode("utf-8"),
            artifact_id=artifact_id,
            artifact_kind=artifact_kind,
            split=split,
            business_id=business_id,
            source_id=source_id,
            method_name=method_name,
            method_version=method_version,
            population_size=population_size,
            observed_n=observed_n,
            sampled_n=sampled_n,
            sample_strategy=sample_strategy,
            skipped_n=skipped_n,
            status=status,
            evidence_refs=evidence_refs,
            parent_artifact_ids=parent_artifact_ids,
            privacy_classification=privacy_classification,
            qa_gate=qa_gate,
        )

    def persist_registry(self) -> Path:
        entries = [
            entry for entry in self.entries if entry.artifact_id != "artifact_registry"
        ]
        registry = ArtifactRegistry(
            run_id=self.run_id, output_root=self.output_root, entries=tuple(entries)
        )
        self.write_json(
            relative_path=REGISTRY_FILENAME,
            payload=registry.to_dict(),
            artifact_id="artifact_registry",
            artifact_kind="registry",
            split="both",
            business_id="__global__",
            source_id="",
            method_name="artifact_registry.persist",
            method_version="artifact_registry.v1",
            status=Status.PASS,
        )
        return self.target_path(REGISTRY_FILENAME)


def load_registry(run_root: Path) -> ArtifactRegistry:
    registry_path = run_root / REGISTRY_FILENAME
    if not registry_path.exists():
        return ArtifactRegistry(run_id="", output_root=run_root, entries=())
    payload = json.loads(registry_path.read_text(encoding="utf-8"))
    entries = tuple(
        ArtifactManifest(
            run_id=entry["run_id"],
            artifact_id=entry["artifact_id"],
            artifact_kind=entry.get("artifact_kind", "artifact"),
            split=entry["split"],
            business_id=entry["business_id"],
            source_id=entry["source_id"],
            source_hash=entry["source_hash"],
            rule_hash=entry["rule_hash"],
            config_hash=entry["config_hash"],
            method_name=entry["method_name"],
            method_version=entry["method_version"],
            population_size=entry["population_size"],
            observed_n=entry["observed_n"],
            sampled_n=entry["sampled_n"],
            sample_strategy=entry["sample_strategy"],
            skipped_n=entry["skipped_n"],
            status=Status(entry["status"]),
            generation_ts=entry["generation_ts"],
            output_relpath=entry["output_relpath"],
            evidence_refs=tuple(entry["evidence_refs"]),
            parent_artifact_ids=tuple(entry["parent_artifact_ids"]),
            privacy_classification=entry["privacy_classification"],
            content_checksum=entry["content_checksum"],
            qa_gate=entry["qa_gate"],
        )
        for entry in payload.get("entries", [])
    )
    return ArtifactRegistry(
        run_id=payload.get("run_id", ""), output_root=run_root, entries=entries
    )


def verify_artifact(
    run_root: Path, manifest: ArtifactManifest
) -> tuple[bool, str]:
    target = run_root / manifest.output_relpath
    if not target.exists():
        return False, "missing_file"
    payload = target.read_bytes()
    checksum = fingerprint_bytes(payload)
    if checksum != manifest.content_checksum:
        return False, "checksum_mismatch"
    return True, "PASS"
