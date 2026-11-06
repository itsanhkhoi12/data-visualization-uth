from __future__ import annotations

import json
from pathlib import Path

from common.provenance import fingerprint_file

WORKSPACE_ROOT = Path(__file__).resolve().parents[4]
RAW_ROOT = WORKSPACE_ROOT / "raw_data"
BASELINE_PATH = WORKSPACE_ROOT / "raw_data_hashes.json"


def build_raw_data_baseline() -> dict[str, str]:
    hashes: dict[str, str] = {}
    for path in sorted(RAW_ROOT.rglob("*")):
        if not path.is_file():
            continue
        hashes[path.relative_to(RAW_ROOT).as_posix()] = fingerprint_file(path)
    return hashes


def write_baseline() -> Path:
    BASELINE_PATH.write_text(
        json.dumps(build_raw_data_baseline(), ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    return BASELINE_PATH


if __name__ == "__main__":
    path = write_baseline()
    payload = json.loads(path.read_text(encoding="utf-8"))
    print(json.dumps({"path": str(path), "file_count": len(payload)}))
