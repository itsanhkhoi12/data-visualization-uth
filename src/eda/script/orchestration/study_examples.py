from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from matplotlib.ticker import FuncFormatter, MaxNLocator

from business.business_chart_metrics import (
    CANCEL_LABEL,
    COMPLETE_LABEL,
    RETURN_LABEL,
    TRANSIT_LABEL,
    classify_status,
)


@dataclass(frozen=True)
class OrderStudy:
    business_id: str
    source: str
    orders: pd.DataFrame
    audit: dict[str, int]

    @property
    def sales(self) -> pd.DataFrame:
        return self.orders.loc[self.orders["status"].isin((COMPLETE_LABEL, TRANSIT_LABEL))]


def _prepare_orders(
    raw: pd.DataFrame,
    business_id: str,
    source: str,
    identifiers: tuple[str, str, str, str],
) -> OrderStudy:
    _, key, _, _ = identifiers
    keyed = raw.loc[raw[key].notna() & raw[key].str.strip().ne("")]
    unique = keyed.drop_duplicates()
    frame = unique.loc[:, list(identifiers)].copy()
    frame.columns = ["date", "order_id", "status", "revenue"]
    frame["order_id"] = frame["order_id"].str.strip()
    dates = frame["date"].str.strip()
    dmy = pd.to_datetime(dates, format="%d/%m/%Y", errors="coerce")
    iso = pd.to_datetime(dates, format="%Y-%m-%d %H:%M:%S", errors="coerce")
    frame["date"] = dmy.fillna(iso).dt.normalize()
    frame["status"] = frame["status"].map(lambda value: classify_status(str(value)))
    frame["revenue"] = pd.to_numeric(
        frame["revenue"].str.replace(",", "", regex=False), errors="coerce"
    )

    by_order = frame.groupby("order_id", sort=False)
    counts = by_order.agg(
        dates=("date", "nunique"),
        statuses=("status", "nunique"),
        dates_present=("date", "count"),
        amounts_present=("revenue", "count"),
        lines=("date", "size"),
    )
    orders = by_order.agg(date=("date", "first"), status=("status", "first"))
    orders["revenue"] = by_order["revenue"].sum(min_count=1)
    usable = (
        counts["dates"].eq(1)
        & counts["dates_present"].eq(counts["lines"])
        & counts["statuses"].eq(1)
        & counts["amounts_present"].eq(counts["lines"])
        & orders["status"].isin((COMPLETE_LABEL, CANCEL_LABEL, RETURN_LABEL, TRANSIT_LABEL))
    )
    if business_id == "dev_009":
        usable &= counts["lines"].eq(1)
    verified = orders.loc[usable]
    return OrderStudy(
        business_id,
        source,
        verified.reset_index(drop=True),
        {
            "Dòng đầu vào": len(raw),
            "Dòng thiếu mã đơn": len(raw) - len(keyed),
            "Dòng trùng chính xác": len(keyed) - len(unique),
            "Dòng có ngày không đọc được sau khi lọc mã": int(frame["date"].isna().sum()),
            "Dòng có tiền hàng không đọc được sau khi lọc mã": int(frame["revenue"].isna().sum()),
            "Đơn có dữ liệu thiếu hoặc mâu thuẫn": int((~usable).sum()),
            "Đơn hợp lệ tính vào doanh thu": int(
                verified["status"].isin((COMPLETE_LABEL, TRANSIT_LABEL)).sum()
            ),
        },
    )


def load_order_studies(split_root: Path) -> tuple[OrderStudy, OrderStudy]:
    first = "So_chi_tiet_ban_hang.xlsx"
    second = "danh_sach_hoa_don.csv"
    return (
        _prepare_orders(
            pd.read_excel(split_root / "data" / "dev_001" / first, header=3, dtype="string"),
            "dev_001",
            first,
            ("Ngày", "Mã đơn hàng", "Trạng thái", "Thành tiền"),
        ),
        _prepare_orders(
            pd.read_csv(split_root / "data" / "dev_009" / second, dtype="string"),
            "dev_009",
            second,
            ("Ngày tháng", "Mã hóa đơn", "Trạng thái đơn", "Giá trị hàng"),
        ),
    )


def order_audit(studies: tuple[OrderStudy, ...]) -> pd.DataFrame:
    return pd.DataFrame(
        [study.audit for study in studies],
        index=pd.Index([study.business_id for study in studies], name="Doanh nghiệp"),
    ).T


def common_months(studies: tuple[OrderStudy, ...]) -> list[pd.Period]:
    overlap: set[pd.Period] | None = None
    for study in studies:
        days = study.orders["date"].drop_duplicates()
        seen = days.groupby(days.dt.to_period("M")).size()
        complete = {month for month, count in seen.items() if count == month.days_in_month}
        overlap = complete if overlap is None else overlap & complete
    return sorted(overlap or ())


def _export_figure(fig: plt.Figure, output: Path, name: str) -> plt.Figure:
    output.mkdir(parents=True, exist_ok=True)
    fig.savefig(output / name, dpi=300, bbox_inches="tight")
    plt.close(fig)
    return fig


def order_value_figure(
    study: OrderStudy, output: Path
) -> tuple[plt.Figure, pd.DataFrame]:
    sales = study.sales
    values = sales["revenue"]
    q1, median, q3 = values.quantile([0.25, 0.5, 0.75])
    iqr = q3 - q1
    low, high = q1 - 1.5 * iqr, q3 + 1.5 * iqr
    flagged = (~values.between(low, high)).sum()
    summary = pd.DataFrame(
        {"Giá trị": [q1, median, q3, low, high, flagged]},
        index=["Q1 (đ)", "Trung vị (đ)", "Q3 (đ)", "Ngưỡng dưới (đ)", "Ngưỡng trên (đ)", "Đơn ngoài ngưỡng"],
    )
    with sns.axes_style("whitegrid"), sns.plotting_context("talk", font_scale=.85):
        fig, ax = plt.subplots(figsize=(10, 3.3))
        fig.subplots_adjust(left=.08, right=.97, top=.84, bottom=.31)
        sns.boxplot(x=values, ax=ax, color="#729995", flierprops={"markersize": 2, "alpha": .4})
        ax.set_title(f"Trung vị giá trị đơn tại {study.business_id} là {median:,.0f} đ".replace(",", "."),
                     loc="left")
        ax.set_xlabel("Giá trị tiền hàng trên một đơn (triệu đồng)")
        ax.xaxis.set_major_locator(MaxNLocator(nbins=5))
        ax.xaxis.set_major_formatter(FuncFormatter(lambda value, _: f"{value / 1_000_000:g}".replace(".", ",")))
        ax.grid(axis="x", color="#e3e7e7", linewidth=.7)
        fig.text(.08, .07,
                 f"Nguồn: {study.source} · {sales['date'].min():%d/%m/%Y} – "
                 f"{sales['date'].max():%d/%m/%Y} · {len(sales):,} đơn hợp lệ".replace(",", "."),
                 fontsize=10)
        sns.despine(ax=ax, left=True)
    return _export_figure(fig, output, "phan-phoi-gia-tri-don.png"), summary


def weekly_activity_figure(
    studies: tuple[OrderStudy, ...], output: Path
) -> tuple[plt.Figure | None, pd.DataFrame]:
    months = common_months(studies)
    if not months:
        return None, pd.DataFrame()
    calendar = pd.DatetimeIndex(
        [day for month in months for day in pd.date_range(month.start_time, periods=month.days_in_month)]
    )
    weekdays = ["T2", "T3", "T4", "T5", "T6", "T7", "CN"]
    denominators = pd.Series(calendar.dayofweek).value_counts().reindex(range(7))
    summary = pd.DataFrame({"Số ngày lịch": denominators.to_numpy()}, index=weekdays)
    with sns.axes_style("whitegrid"), sns.plotting_context("talk", font_scale=.85):
        fig, axes = plt.subplots(1, len(studies), figsize=(11, 4.1), sharey=True)
        fig.subplots_adjust(left=.10, right=.98, top=.73, bottom=.23, wspace=.17)
        peak_labels: list[str] = []
        for study, ax in zip(studies, axes, strict=True):
            sales = study.sales
            sales = sales.loc[sales["date"].dt.to_period("M").isin(months)]
            counts = sales["date"].dt.dayofweek.value_counts().reindex(range(7), fill_value=0)
            averages = counts / denominators
            summary[f"{study.business_id}: số đơn"] = counts.to_numpy()
            summary[f"{study.business_id}: đơn/ngày"] = averages.to_numpy()
            peak = averages.idxmax()
            peak_labels.append(f"{weekdays[peak]} ở {study.business_id}")
            ax.bar(weekdays, averages, color=["#00665e" if i == peak else "#b9c1c1" for i in range(7)])
            ax.set_title(f"{study.business_id} · {len(sales):,} đơn".replace(",", "."), loc="left")
            ax.set_ylim(bottom=0)
            ax.grid(False, axis="x")
            ax.grid(axis="y", color="#e3e7e7", linewidth=.7)
            sns.despine(ax=ax)
        axes[0].set_ylabel("Đơn hợp lệ trung bình/ngày")
        fig.suptitle("Bình quân cao nhất vào " + " và ".join(peak_labels), ha="left", x=.10)
        fig.text(.10, .08,
                 f"{len(months)} tháng đủ ngày chung trong khoảng {months[0]:%m/%Y}–{months[-1]:%m/%Y}.",
                 fontsize=10)
        fig.text(.10, .03,
                 "Nguồn: Sổ chi tiết bán hàng dev_001 và Danh sách hóa đơn dev_009.",
                 fontsize=10)
    summary.attrs["months"] = ", ".join(f"{month:%m/%Y}" for month in months)
    return _export_figure(fig, output, "nhip-ban-theo-thu.png"), summary
