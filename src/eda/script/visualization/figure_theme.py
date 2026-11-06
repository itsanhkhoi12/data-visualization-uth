from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt

FIGURE_WIDTH = 11.0
FIGURE_HEIGHT = 6.5
FIGURE_DPI = 130
BASE_FONT_SIZE = 11
TITLE_FONT_SIZE = 13
CAPTION_FONT_SIZE = 9
GRID_ALPHA = 0.55
NEUTRAL_PALETTE = (
    "#1769AA",
    "#087B5A",
    "#A36516",
    "#B32336",
    "#5A4FCF",
    "#66768A",
)
SEVERITY_PALETTE = {
    "critical": "#7A1420",
    "high": "#B32336",
    "medium": "#A36516",
    "low": "#1769AA",
    "info": "#66768A",
}
STATUS_PALETTE = {
    "PASS": "#087B5A",
    "PARTIAL": "#A36516",
    "BLOCKED": "#B32336",
    "NOT APPLICABLE": "#66768A",
}
VIETNAMESE_FONT_CANDIDATES = (
    "DejaVu Sans",
    "Arial",
    "Helvetica",
    "Liberation Sans",
)


@dataclass(frozen=True)
class FigureTheme:
    figure_width: float = FIGURE_WIDTH
    figure_height: float = FIGURE_HEIGHT
    dpi: int = FIGURE_DPI
    base_font_size: int = BASE_FONT_SIZE
    title_font_size: int = TITLE_FONT_SIZE
    caption_font_size: int = CAPTION_FONT_SIZE
    font_family: str = VIETNAMESE_FONT_CANDIDATES[0]

    def to_dict(self) -> dict[str, Any]:
        return {
            "figure_width": self.figure_width,
            "figure_height": self.figure_height,
            "dpi": self.dpi,
            "base_font_size": self.base_font_size,
            "title_font_size": self.title_font_size,
            "caption_font_size": self.caption_font_size,
            "font_family": self.font_family,
        }


def resolve_font_family() -> str:
    from matplotlib import font_manager

    available = {font.name for font in font_manager.fontManager.ttflist}
    for candidate in VIETNAMESE_FONT_CANDIDATES:
        if candidate in available:
            return candidate
    return "sans-serif"


def apply_theme(theme: FigureTheme | None = None) -> FigureTheme:
    resolved = theme or FigureTheme(font_family=resolve_font_family())
    plt.rcParams.update(
        {
            "font.family": resolved.font_family,
            "font.size": resolved.base_font_size,
            "axes.titlesize": resolved.title_font_size,
            "axes.labelsize": resolved.base_font_size,
            "xtick.labelsize": resolved.base_font_size - 1,
            "ytick.labelsize": resolved.base_font_size - 1,
            "legend.fontsize": resolved.base_font_size - 2,
            "axes.unicode_minus": False,
            "figure.autolayout": False,
            "savefig.bbox": "tight",
            "savefig.facecolor": "#FFFFFF",
            "axes.grid": True,
            "grid.linestyle": ":",
            "grid.linewidth": 0.6,
            "grid.alpha": GRID_ALPHA,
            "axes.spines.top": False,
            "axes.spines.right": False,
        }
    )
    return resolved


def style_axes(
    axis: Any,
    title: str,
    x_label: str,
    y_label: str,
    grid_axis: str = "y",
) -> None:
    axis.set_title(title, pad=12, loc="left")
    axis.set_xlabel(x_label)
    axis.set_ylabel(y_label)
    axis.grid(axis=grid_axis, linestyle=":", linewidth=0.6, alpha=GRID_ALPHA)
    axis.spines["top"].set_visible(False)
    axis.spines["right"].set_visible(False)


def add_caption(
    figure: Any,
    caption: str,
    sample_note: str = "",
    source_note: str = "",
    theme: FigureTheme | None = None,
) -> None:
    resolved = theme or FigureTheme()
    lines = [caption]
    if sample_note:
        lines.append(sample_note)
    if source_note:
        lines.append(source_note)
    figure.text(
        0.01,
        0.005,
        "\n".join(lines),
        fontsize=resolved.caption_font_size,
        color="#3B4653",
        ha="left",
        va="bottom",
        wrap=True,
    )


def format_tick_values(values: list[float]) -> list[str]:
    formatted: list[str] = []
    for value in values:
        if abs(value) >= 1_000_000:
            formatted.append(f"{value / 1_000_000:.1f}M")
        elif abs(value) >= 1_000:
            formatted.append(f"{value / 1_000:.1f}k")
        elif float(value).is_integer():
            formatted.append(f"{int(value)}")
        else:
            formatted.append(f"{value:.3g}")
    return formatted


def thousands_axis(axis: Any, axis_name: str = "y") -> None:
    from matplotlib.ticker import FuncFormatter

    formatter = FuncFormatter(lambda value, _: f"{value:,.0f}")
    if axis_name == "x":
        axis.xaxis.set_major_formatter(formatter)
    else:
        axis.yaxis.set_major_formatter(formatter)
