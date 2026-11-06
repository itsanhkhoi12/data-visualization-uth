from __future__ import annotations

from typing import Any, Mapping, Sequence

from common.bundles import SplitBundle
from common.enums import Status
from statistics.categorical_association import crosstab_association
from statistics.robust_stats import (
    compute_robust_dispersion,
    iqr_outlier_masks,
    median_of,
    quantile_of,
)
from validation.validation_contracts import ValidationCheck, ValidationLedger

MIN_SAMPLE = 5


def validate_statistics(
    bundles: Mapping[str, SplitBundle],
) -> ValidationLedger:
    ledger = ValidationLedger()
    ledger.extend(_validate_robust_stats(bundles))
    ledger.extend(_validate_quantile_monotonicity(bundles))
    ledger.extend(_validate_outlier_flags(bundles))
    ledger.extend(_validate_categorical_reconciliation(bundles))
    ledger.extend(_validate_association_bounds(bundles))
    return ledger


def _validate_robust_stats(bundles: Mapping[str, SplitBundle]) -> list[ValidationCheck]:
    checks: list[ValidationCheck] = []
    for split, bundle in sorted(bundles.items()):
        for entry in bundle.numeric_stats:
            values = bundle.numeric_samples.get(entry.source_id, {}).get(entry.field, [])
            if len(values) < MIN_SAMPLE:
                continue
            dispersion = compute_robust_dispersion(values, total_n=entry.n_total)
            if dispersion is None:
                checks.append(
                    ValidationCheck(
                        check_id=f"STAT-ROBUST-{split}-{entry.source_id}-{entry.field}",
                        category="robust_statistics",
                        scope=f"{split}:{entry.source_id}:{entry.field}",
                        expected="median trong khoảng q25 và q75",
                        observed="không tính được dispersion",
                        status=Status.BLOCKED,
                        detail="mẫu định lượng không đủ điều kiện tính dispersion",
                    )
                )
                continue
            ordered = sorted(float(value) for value in values)
            expected_median = median_of(ordered)
            expected_q25 = quantile_of(ordered, 0.25)
            expected_q75 = quantile_of(ordered, 0.75)
            ok = (
                abs(dispersion.median - expected_median) <= 1e-6
                and abs(dispersion.q25 - expected_q25) <= 1e-6
                and abs(dispersion.q75 - expected_q75) <= 1e-6
                and dispersion.q25 <= dispersion.median <= dispersion.q75
            )
            checks.append(
                ValidationCheck(
                    check_id=f"STAT-ROBUST-{split}-{entry.source_id}-{entry.field}",
                    category="robust_statistics",
                    scope=f"{split}:{entry.source_id}:{entry.field}",
                    expected="median, q25, q75 khớp giá trị tái tính trên cùng mẫu",
                    observed=(
                        f"median={dispersion.median}, q25={dispersion.q25}, "
                        f"q75={dispersion.q75}, n_valid={dispersion.n_valid}"
                    ),
                    status=Status.PASS if ok else Status.BLOCKED,
                    detail="tái tính độc lập từ mẫu định lượng đã lưu",
                )
            )
    return checks


def _validate_quantile_monotonicity(
    bundles: Mapping[str, SplitBundle],
) -> list[ValidationCheck]:
    checks: list[ValidationCheck] = []
    for split, bundle in sorted(bundles.items()):
        for entry in bundle.numeric_stats:
            values = bundle.numeric_samples.get(entry.source_id, {}).get(entry.field, [])
            if len(values) < MIN_SAMPLE:
                continue
            ordered = sorted(float(value) for value in values)
            levels = [0.01, 0.05, 0.10, 0.25, 0.50, 0.75, 0.90, 0.95, 0.99]
            computed = [quantile_of(ordered, level) for level in levels]
            monotonic = all(
                computed[index] <= computed[index + 1]
                for index in range(len(computed) - 1)
            )
            checks.append(
                ValidationCheck(
                    check_id=f"STAT-QUANTILE-{split}-{entry.source_id}-{entry.field}",
                    category="robust_statistics",
                    scope=f"{split}:{entry.source_id}:{entry.field}",
                    expected="các quantile tăng đơn điệu từ q01 đến q99",
                    observed="; ".join(
                        f"q{int(level * 100)}={value:.6g}"
                        for level, value in zip(levels, computed)
                    ),
                    status=Status.PASS if monotonic else Status.BLOCKED,
                    detail="kiểm tra đơn điệu của hàm phân phối thực nghiệm",
                )
            )
    return checks


def _validate_outlier_flags(bundles: Mapping[str, SplitBundle]) -> list[ValidationCheck]:
    checks: list[ValidationCheck] = []
    for split, bundle in sorted(bundles.items()):
        for entry in bundle.numeric_stats:
            values = bundle.numeric_samples.get(entry.source_id, {}).get(entry.field, [])
            if len(values) < MIN_SAMPLE:
                continue
            lower, upper, flags, degenerate = iqr_outlier_masks(values)
            ordered = sorted(float(value) for value in values)
            q25 = quantile_of(ordered, 0.25)
            q75 = quantile_of(ordered, 0.75)
            if degenerate:
                consistent = not any(flags)
            else:
                expected = sum(
                    1 for value in ordered if value < lower or value > upper
                )
                consistent = expected == sum(1 for flag in flags if flag)
            checks.append(
                ValidationCheck(
                    check_id=f"STAT-IQR-{split}-{entry.source_id}-{entry.field}",
                    category="outlier_handling",
                    scope=f"{split}:{entry.source_id}:{entry.field}",
                    expected="số cờ ngoại lệ khớp ngưỡng IQR 1.5",
                    observed=(
                        f"lower={lower:.6g}, upper={upper:.6g}, "
                        f"outlier_n={sum(1 for flag in flags if flag)}, "
                        f"q25={q25:.6g}, q75={q75:.6g}"
                    ),
                    status=Status.PASS if consistent else Status.BLOCKED,
                    detail=(
                        "IQR bằng không thì mọi quan sát được giữ và không gắn cờ"
                        if degenerate
                        else "ngưỡng ngoại lệ không loại bỏ quan sát khỏi mẫu"
                    ),
                )
            )
    return checks


def _validate_categorical_reconciliation(
    bundles: Mapping[str, SplitBundle],
) -> list[ValidationCheck]:
    checks: list[ValidationCheck] = []
    for split, bundle in sorted(bundles.items()):
        for entry in bundle.categorical_stats:
            counts = getattr(entry, "counts", None) or {}
            total = sum(int(value) for value in counts.values())
            valid_n = int(getattr(entry, "valid_n", 0) or 0)
            difference = abs(total - valid_n)
            ok = difference <= max(1, int(valid_n * 0.001))
            checks.append(
                ValidationCheck(
                    check_id=f"STAT-CATEGORY-{split}-{entry.source_id}-{entry.field}",
                    category="categorical_reconciliation",
                    scope=f"{split}:{entry.source_id}:{entry.field}",
                    expected="tổng số đếm theo nhóm bằng số giá trị hợp lệ",
                    observed=f"sum_counts={total}, valid_n={valid_n}",
                    status=Status.PASS if ok else Status.BLOCKED,
                    detail="sai số cho phép là 0.1% số giá trị hợp lệ",
                )
            )
    return checks


def _validate_association_bounds(
    bundles: Mapping[str, SplitBundle],
) -> list[ValidationCheck]:
    checks: list[ValidationCheck] = []
    for split, bundle in sorted(bundles.items()):
        for entry in bundle.relations:
            status = getattr(entry, "status", "")
            if str(status).endswith("APPROVED") and getattr(entry, "fanout_factor", 0) > 1:
                checks.append(
                    ValidationCheck(
                        check_id=f"STAT-JOIN-{split}-{getattr(entry, 'relation_id', '')}",
                        category="join_gate",
                        scope=f"{split}:{getattr(entry, 'relation_id', '')}",
                        expected="quan hệ được phê duyệt không có nhân bản",
                        observed=f"fanout_factor={entry.fanout_factor}",
                        status=Status.BLOCKED,
                        detail="phép nối có hệ số nhân bản vượt ngưỡng không được dùng",
                    )
                )
    for split, bundle in sorted(bundles.items()):
        for source_id in sorted(bundle.row_samples)[:4]:
            rows = bundle.row_samples[source_id]
            if len(rows) < 20:
                continue
            fields = sorted({key for row in rows[:100] for key in row})[:4]
            if len(fields) < 2:
                continue
            association = crosstab_association(rows, fields[0], fields[1])
            if association.cramers_v is None:
                continue
            bounded = 0.0 <= association.cramers_v <= 1.0
            checks.append(
                ValidationCheck(
                    check_id=f"STAT-CRAMER-{split}-{source_id}",
                    category="association_bounds",
                    scope=f"{split}:{source_id}",
                    expected="Cramér V nằm trong khoảng [0, 1]",
                    observed=f"cramers_v={association.cramers_v}, n={association.total_n}",
                    status=Status.PASS if bounded else Status.BLOCKED,
                    detail="kiểm tra biên của chỉ số liên hệ phân loại",
                )
            )
    return checks
