from __future__ import annotations

import ast
import importlib
from pathlib import Path

import pytest

from common.enums import Status
from common.provenance import fingerprint_file

SCRIPT_ROOT = Path(__file__).resolve().parents[1] / "script"
WORKSPACE_ROOT = Path(__file__).resolve().parents[3]
RAW_ROOT = WORKSPACE_ROOT / "raw_data"

LAYER_ORDER = (
    "common",
    "readers",
    "inventory",
    "schema",
    "quality",
    "statistics",
    "temporal",
    "rulebook",
    "business",
    "questions",
    "cross_business",
    "reporting",
    "visualization",
    "html_tables",
    "orchestration",
)


def _module_files() -> list[Path]:
    return sorted(path for path in SCRIPT_ROOT.rglob("*.py") if path.name != "__init__.py")


def test_t058_all_modules_import() -> None:
    for path in _module_files():
        relative = path.relative_to(SCRIPT_ROOT).with_suffix("")
        name = ".".join(relative.parts)
        importlib.import_module(name)


def test_import_direction_is_respected() -> None:
    for path in _module_files():
        relative = path.relative_to(SCRIPT_ROOT).with_suffix("")
        parts = relative.parts
        layer = parts[0]
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            modules: list[str] = []
            if isinstance(node, ast.ImportFrom) and node.module:
                modules.append(node.module.split(".")[0])
            elif isinstance(node, ast.Import):
                modules.extend(alias.name.split(".")[0] for alias in node.names)
            for module in modules:
                if module not in LAYER_ORDER:
                    continue
                assert LAYER_ORDER.index(module) <= LAYER_ORDER.index(layer), (
                    f"{relative} imports downstream layer {module}"
                )


def test_t059_raw_sources_are_not_modified() -> None:
    if not RAW_ROOT.exists():
        pytest.skip("raw data not available")
    baseline = WORKSPACE_ROOT / "raw_data_hashes.json"
    if not baseline.exists():
        pytest.skip("no baseline manifest available")
    import json

    recorded = json.loads(baseline.read_text(encoding="utf-8"))
    changed: list[str] = []
    for relative, expected in recorded.items():
        path = RAW_ROOT / relative
        if not path.exists():
            changed.append(f"{relative}:missing")
            continue
        if fingerprint_file(path) != expected:
            changed.append(f"{relative}:changed")
    assert not changed


def test_no_comments_or_docstrings_in_source() -> None:
    offenders: list[str] = []
    for path in _module_files():
        relative = path.relative_to(SCRIPT_ROOT)
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                if ast.get_docstring(node):
                    offenders.append(f"{relative}:{node.name}")
            if isinstance(node, ast.Expr) and isinstance(node.value, ast.Constant):
                value = node.value.value
                if isinstance(value, str) and len(value.strip()) > 0:
                    offenders.append(f"{relative}:{node.lineno}")
    assert not offenders


def test_t060_ledger_has_expected_business_counts() -> None:
    train_root = RAW_ROOT / "train" / "data"
    public_root = RAW_ROOT / "public_test" / "data"
    if not train_root.exists() or not public_root.exists():
        pytest.skip("raw data not available")
    train_businesses = sorted(
        path.name for path in train_root.iterdir() if path.is_dir()
    )
    public_businesses = sorted(
        path.name for path in public_root.iterdir() if path.is_dir()
    )
    assert len(train_businesses) == 30
    assert len(public_businesses) == 14
    assert len(train_businesses) + len(public_businesses) == 44


def test_t060_public_test_has_no_answers_file() -> None:
    answers = RAW_ROOT / "public_test" / "answers.jsonl"
    assert not answers.exists()


def test_status_enum_values_are_stable() -> None:
    assert Status.PASS.value == "PASS"
    assert Status.BLOCKED.value == "BLOCKED"
    assert Status.NOT_APPLICABLE.value == "NOT APPLICABLE"


def test_gate_ledger_covers_every_implementation_phase() -> None:
    from orchestration.pipeline import _gate

    phases = {
        "IMP-00",
        "IMP-01",
        "IMP-02",
        "IMP-03",
        "IMP-04",
        "IMP-05",
        "IMP-06",
        "IMP-07",
        "IMP-08",
        "IMP-09",
        "IMP-10",
        "IMP-11",
        "IMP-12",
        "IMP-13",
        "IMP-14",
        "IMP-15",
    }
    source = (SCRIPT_ROOT / "orchestration" / "pipeline.py").read_text(encoding="utf-8")
    tree = ast.parse(source)
    declared = {
        node.args[0].value
        for node in ast.walk(tree)
        if isinstance(node, ast.Call)
        and isinstance(node.func, ast.Name)
        and node.func.id == "_gate"
        and node.args
        and isinstance(node.args[0], ast.Constant)
    }
    assert phases <= declared, sorted(phases - declared)


def test_notebook_builder_declares_seventeen_sections() -> None:
    from orchestration.notebook_builder import SECTIONS

    assert len(SECTIONS) == 17
    assert [section["id"] for section in SECTIONS] == [
        f"{index:02d}" for index in range(17)
    ]
