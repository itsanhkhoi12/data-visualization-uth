from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Mapping, Sequence

from common.enums import Status
from common.provenance import fingerprint_file
from validation.validation_contracts import ValidationCheck, ValidationLedger

NUMERIC_TOLERANCE = 1e-6
REGRESSION_VERSION = "regression_report.v1"


def verify_raw_hashes(baseline_path: Path, raw_root: Path) -> ValidationLedger:
    ledger = ValidationLedger()
    if not baseline_path.exists():
        ledger.add(
            ValidationCheck(
                check_id="RAW-BASELINE-MISSING",
                category="raw_invariance",
                scope=str(raw_root),
                expected="tệp baseline hash của dữ liệu thô tồn tại",
                observed="không tìm thấy baseline",
                status=Status.BLOCKED,
                detail="không thể chứng minh dữ liệu thô bất biến nếu thiếu baseline",
            )
        )
        return ledger
    baseline = json.loads(baseline_path.read_text(encoding="utf-8"))
    current: dict[str, str] = {}
    for path in sorted(raw_root.rglob("*")):
        if not path.is_file():
            continue
        current[path.relative_to(raw_root).as_posix()] = fingerprint_file(path)
    changed: list[str] = []
    added: list[str] = []
    removed: list[str] = []
    for name, digest in baseline.items():
        if name not in current:
            removed.append(name)
        elif current[name] != digest:
            changed.append(name)
    for name in current:
        if name not in baseline:
            added.append(name)
    ok = not changed and not added and not removed
    ledger.add(
        ValidationCheck(
            check_id="RAW-INVARIANCE",
            category="raw_invariance",
            scope=str(raw_root),
            expected="hash mọi tệp nguồn thô không đổi so với baseline",
            observed=(
                f"baseline_files={len(baseline)}, current_files={len(current)}, "
                f"changed={len(changed)}, added={len(added)}, removed={len(removed)}"
            ),
            status=Status.PASS if ok else Status.BLOCKED,
            detail="; ".join(
                [f"changed={changed[:5]}", f"added={added[:5]}", f"removed={removed[:5]}"]
            ).strip("; "),
        )
    )
    return ledger


def compare_runs(
    previous_run_root: Path, current_run_root: Path
) -> ValidationLedger:
    ledger = ValidationLedger()
    previous = _load_json(previous_run_root / "figure_registry.json")
    current = _load_json(current_run_root / "figure_registry.json")
    if not previous or not current:
        ledger.add(
            ValidationCheck(
                check_id="REG-COMPARE-MISSING",
                category="regression",
                scope=f"{previous_run_root} vs {current_run_root}",
                expected="cả hai run đều có figure_registry.json",
                observed="thiếu registry ở một trong hai run",
                status=Status.BLOCKED,
                detail="không thể đối chiếu số liệu giữa hai run",
            )
        )
        return ledger
    previous_map = _figure_map(previous)
    current_map = _figure_map(current)
    shared = sorted(set(previous_map) & set(current_map))
    only_previous = sorted(set(previous_map) - set(current_map))
    only_current = sorted(set(current_map) - set(previous_map))
    for figure_id in shared:
        before = previous_map[figure_id]
        after = current_map[figure_id]
        differences: list[str] = []
        if before["status"] != after["status"]:
            differences.append(f"status {before['status']} → {after['status']}")
        if before["population_n"] != after["population_n"]:
            differences.append(
                f"population_n {before['population_n']} → {after['population_n']}"
            )
        if not _close(before["population_n"], after["population_n"]):
            differences.append("population_n lệch quá dung sai")
        ok = not differences
        ledger.add(
            ValidationCheck(
                check_id=f"REG-FIG-{figure_id}",
                category="regression",
                scope=figure_id,
                expected="trạng thái và population_n không đổi giữa hai run",
                observed="; ".join(differences) or "không đổi",
                status=Status.PASS if ok else Status.BLOCKED,
                detail=f"so sánh {previous_run_root.name} với {current_run_root.name}",
            )
        )
    ledger.add(
        ValidationCheck(
            check_id="REG-FIGURE-SET",
            category="regression",
            scope="figure_registry",
            expected="tập figure giữa hai run được giải thích được",
            observed=(
                f"shared={len(shared)}, removed={len(only_previous)}, "
                f"added={len(only_current)}"
            ),
            status=Status.PASS,
            detail=(
                f"chỉ mới: {only_current[:8]}; chỉ cũ: {only_previous[:8]}"
            ),
        )
    )
    return ledger


def verify_artifact_hashes(run_root: Path) -> ValidationLedger:
    ledger = ValidationLedger()
    registry_path = run_root / "artifact_registry.json"
    if not registry_path.exists():
        ledger.add(
            ValidationCheck(
                check_id="ART-REGISTRY-MISSING",
                category="artifact_integrity",
                scope=str(run_root),
                expected="artifact_registry.json tồn tại",
                observed="không tìm thấy registry",
                status=Status.BLOCKED,
                detail="không thể kiểm tra hash artifact",
            )
        )
        return ledger
    registry = json.loads(registry_path.read_text(encoding="utf-8"))
    entries = registry.get("entries", [])
    for entry in entries:
        relative = entry.get("output_relpath", "")
        expected_hash = entry.get("content_checksum", "")
        if not relative or not expected_hash:
            continue
        if relative == "artifact_registry.json":
            continue
        target = run_root / relative
        if not target.exists():
            ledger.add(
                ValidationCheck(
                    check_id=f"ART-{entry.get('artifact_id', relative)}",
                    category="artifact_integrity",
                    scope=relative,
                    expected="tệp artifact tồn tại",
                    observed="tệp không tồn tại",
                    status=Status.BLOCKED,
                    detail="artifact ghi trong registry nhưng không có trên đĩa",
                )
            )
            continue
        actual = fingerprint_file(target)
        ok = actual == expected_hash
        ledger.add(
            ValidationCheck(
                check_id=f"ART-{entry.get('artifact_id', relative)}",
                category="artifact_integrity",
                scope=relative,
                expected="hash nội dung artifact khớp registry",
                observed=f"expected={expected_hash}, actual={actual}",
                status=Status.PASS if ok else Status.BLOCKED,
                detail="artifact phải bất biến sau khi ghi",
            )
        )
    return ledger


def _load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}


def _figure_map(registry: Mapping[str, Any]) -> dict[str, dict[str, Any]]:
    figures = registry.get("figures", [])
    mapped: dict[str, dict[str, Any]] = {}
    for figure in figures:
        key = str(figure.get("figure_id", ""))
        if not key:
            continue
        mapped[key] = {
            "status": figure.get("status"),
            "population_n": figure.get("population_n"),
        }
    return mapped


def _close(left: Any, right: Any) -> bool:
    if left is None or right is None:
        return left == right
    try:
        return abs(float(left) - float(right)) <= NUMERIC_TOLERANCE * max(
            1.0, abs(float(left))
        )
    except (TypeError, ValueError):
        return left == right
