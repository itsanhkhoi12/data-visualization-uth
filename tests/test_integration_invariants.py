from __future__ import annotations

import ast
import importlib
import unicodedata
from pathlib import Path

import pytest

from common.enums import Status
from common.provenance import fingerprint_file

WORKSPACE_ROOT = Path(__file__).resolve().parents[1]
SCRIPT_ROOT = WORKSPACE_ROOT / "src"
RAW_ROOT = WORKSPACE_ROOT / "raw_data" if (WORKSPACE_ROOT / "raw_data").is_dir() else WORKSPACE_ROOT / "data"

LAYER_ORDER = (
    "common",
    "readers",
    "inventory",
    "schema",
    "profiling",
    "quality",
    "eda_statistics",
    "temporal",
    "rulebook",
    "business",
    "questions",
    "cross_business",
    "visualization",
    "html_tables",
    "validation",
    "reporting",
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
    local_paths = {
        unicodedata.normalize("NFC", path.relative_to(RAW_ROOT).as_posix()): path
        for path in (RAW_ROOT / "public_test").rglob("*")
        if path.is_file()
    }
    changed: list[str] = []
    for relative, expected in recorded.items():
        path = local_paths.get(unicodedata.normalize("NFC", relative))
        if path is None:
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
    public_root = RAW_ROOT / "public_test" / "data"
    if not public_root.exists():
        pytest.skip("raw data not available")
    public_businesses = sorted(
        path.name for path in public_root.iterdir() if path.is_dir()
    )
    assert len(public_businesses) == 14


def test_t060_train_split_is_not_required() -> None:
    from common.config import load_config
    from common.enums import DatasetSplit

    assert tuple(split.value for split in DatasetSplit) == ("public_test",)
    assert load_config().splits == ("public_test",)


def test_t060_public_test_has_no_answers_file() -> None:
    answers = RAW_ROOT / "public_test" / "answers.jsonl"
    assert not answers.exists()


def test_operating_data_scope_excludes_competition_files(tmp_path: Path) -> None:
    from common.config import EdaConfig
    from inventory.file_manifest import build_file_manifest
    from validation.regression_qa import verify_raw_hashes

    raw = tmp_path / "raw_data"
    split = raw / "public_test"
    business = split / "data" / "dev_001"
    business.mkdir(parents=True)
    for name in ("rulebook.md", "calendar.csv"):
        (split / name).touch()
    for name in ("questions.jsonl", "answers.jsonl"):
        (split / name).write_bytes(b"{invalid benchmark data")
    (business / "orders.csv").touch()
    train = raw / "train"
    train.mkdir()
    (train / "unrelated.csv").touch()

    config = EdaConfig(tmp_path, raw, tmp_path / "artifacts")
    context = config.context_for("public_test")
    records = build_file_manifest(context).records
    assert {item.logical_path for item in records} == {
        "rulebook.md",
        "calendar.csv",
        "data/dev_001/orders.csv",
    }
    baseline = tmp_path / "baseline.json"
    import json

    baseline.write_text(json.dumps({
        f"public_test/{item.logical_path}": item.content_hash for item in records
    }), encoding="utf-8")
    assert not verify_raw_hashes(baseline, raw).failures()


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


def test_public_test_only_architecture() -> None:
    from common.config import load_config
    from common.enums import DatasetSplit

    config = load_config()
    assert config.splits == ("public_test",)
    assert tuple(split.value for split in DatasetSplit) == ("public_test",)
    assert (config.raw_root / "public_test").is_dir()

