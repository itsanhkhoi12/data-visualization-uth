from __future__ import annotations

import hashlib
import os
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from common.enums import Status
from common.paths import assert_safe_output


@dataclass(frozen=True)
class ExportedFigure:
    figure_id: str
    chart_id: str
    png_path: str
    svg_path: str
    png_hash: str
    svg_hash: str
    status: Status
    reason: str
    byte_size: int

    def to_dict(self) -> dict[str, Any]:
        return {
            "figure_id": self.figure_id,
            "chart_id": self.chart_id,
            "png_path": self.png_path,
            "svg_path": self.svg_path,
            "png_hash": self.png_hash,
            "svg_hash": self.svg_hash,
            "status": self.status.value,
            "reason": self.reason,
            "byte_size": self.byte_size,
        }


def _hash_bytes(payload: bytes) -> str:
    return f"sha256:{hashlib.sha256(payload).hexdigest()}"


def _atomic_write(target: Path, payload: bytes) -> None:
    target.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(dir=target.parent, delete=False) as handle:
        handle.write(payload)
        temporary = Path(handle.name)
    os.replace(temporary, target)


def export_figure(
    figure: Any,
    output_root: Path,
    relative_directory: str,
    chart_id: str,
    run_id: str,
    include_svg: bool = True,
) -> ExportedFigure:
    png_target = (output_root / relative_directory / f"{chart_id}.png").resolve()
    svg_target = (output_root / relative_directory / f"{chart_id}.svg").resolve()
    png_target = assert_safe_output(output_root.resolve(), png_target)
    svg_target = assert_safe_output(output_root.resolve(), svg_target)
    png_target.parent.mkdir(parents=True, exist_ok=True)
    figure.savefig(png_target, dpi=figure.dpi if hasattr(figure, "dpi") else 130)
    png_payload = png_target.read_bytes()
    _atomic_write(png_target, png_payload)
    svg_hash = ""
    if include_svg:
        figure.savefig(svg_target, format="svg")
        svg_payload = svg_target.read_bytes()
        _atomic_write(svg_target, svg_payload)
        svg_hash = _hash_bytes(svg_payload)
    return ExportedFigure(
        figure_id=f"{run_id}.{chart_id}",
        chart_id=chart_id,
        png_path=str(png_target.relative_to(output_root.resolve())),
        svg_path=(
            str(svg_target.relative_to(output_root.resolve())) if include_svg else ""
        ),
        png_hash=_hash_bytes(png_payload),
        svg_hash=svg_hash,
        status=Status.PASS,
        reason="exported_offline_png_and_svg",
        byte_size=len(png_payload),
    )
