from __future__ import annotations

import json
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src" / "eda" / "script"))

from common.config import load_config
from orchestration.pipeline import run_eda

started = time.time()
config = load_config()
run = run_eda(config, splits=("train", "public_test"))
elapsed = time.time() - started
figures = run.visualization.registry.figures if run.visualization else []
payload = {
    "run_id": run.run_id,
    "elapsed_seconds": round(elapsed, 3),
    "figure_count": len(figures),
    "chart_ids": sorted({item.chart_id for item in figures}),
    "statuses": {},
    "output_root": str(run.output_root),
}
for item in figures:
    key = item.status.value
    payload["statuses"][key] = payload["statuses"].get(key, 0) + 1
print(json.dumps(payload, ensure_ascii=False, indent=2))
