from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src" / "eda" / "script"))

from common.config import load_config
from orchestration.analysis import analyze_split
from orchestration.visualization_pipeline import (
    _chart_data_for_split,
    _cross_split_chart_data,
    _question_chart_data,
)
from rulebook.rule_registry import compile_rule_registry
from common.provenance import fingerprint_file

config = load_config()
bundles = {}
for split in ("train", "public_test"):
    context = config.context_for(split)
    registry = compile_rule_registry(
        context.rulebook_path, split, fingerprint_file(context.rulebook_path)
    )
    bundles[split] = analyze_split(config, split, registry)

from visualization.chart_context import BundleContext

for split, bundle in bundles.items():
    ctx = BundleContext(split=split, bundle=bundle)
    data = _chart_data_for_split(bundle) + _question_chart_data(bundle)
    ids = sorted({d.chart_id for d in data})
    print(split, len(data), ids)

gates = []
cross = _cross_split_chart_data(bundles, gates)
print("cross:", [(d.chart_id, d.split, len(d.payload.get("labels", []) or d.payload.get("rows", []))) for d in cross])
