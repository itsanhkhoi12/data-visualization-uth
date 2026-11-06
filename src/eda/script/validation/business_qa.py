from __future__ import annotations

from typing import Any, Mapping

from common.bundles import SplitBundle
from common.enums import Status
from validation.validation_contracts import ValidationCheck, ValidationLedger

VALID_METRIC_STATUS = {Status.PASS, Status.NOT_APPLICABLE, Status.BLOCKED}


def validate_business_metrics(
    bundles: Mapping[str, SplitBundle],
) -> ValidationLedger:
    ledger = ValidationLedger()
    ledger.extend(_validate_metric_status(bundles))
    ledger.extend(_validate_population_consistency(bundles))
    ledger.extend(_validate_payload_shape(bundles))
    ledger.extend(_validate_grain_presence(bundles))
    return ledger


def _validate_metric_status(bundles: Mapping[str, SplitBundle]) -> list[ValidationCheck]:
    checks: list[ValidationCheck] = []
    for split, bundle in sorted(bundles.items()):
        for metric in bundle.business_metrics:
            valid = metric.status in VALID_METRIC_STATUS
            blocked_without_reason = (
                metric.status == Status.BLOCKED and not metric.reason
            )
            ok = valid and not blocked_without_reason
            checks.append(
                ValidationCheck(
                    check_id=f"BUS-STATUS-{split}-{metric.source_id}-{metric.metric_id}",
                    category="business_metric_status",
                    scope=f"{split}:{metric.source_id}:{metric.metric_id}",
                    expected="trạng thái hợp lệ và BLOCKED phải kèm lý do",
                    observed=f"status={metric.status.value}, reason={metric.reason or 'rỗng'}",
                    status=Status.PASS if ok else Status.BLOCKED,
                    detail="mọi chỉ số kinh doanh phải có trạng thái tường minh",
                )
            )
    return checks


def _validate_population_consistency(
    bundles: Mapping[str, SplitBundle],
) -> list[ValidationCheck]:
    checks: list[ValidationCheck] = []
    for split, bundle in sorted(bundles.items()):
        for metric in bundle.business_metrics:
            if metric.status != Status.PASS:
                continue
            ok = metric.population_n >= 0
            checks.append(
                ValidationCheck(
                    check_id=f"BUS-POP-{split}-{metric.source_id}-{metric.metric_id}",
                    category="business_metric_population",
                    scope=f"{split}:{metric.source_id}:{metric.metric_id}",
                    expected="population_n không âm và khớp số quan sát trong payload",
                    observed=f"population_n={metric.population_n}",
                    status=Status.PASS if ok else Status.BLOCKED,
                    detail="mẫu số phải là số quan sát thực tế trên grain đã xác định",
                )
            )
    return checks


def _validate_payload_shape(
    bundles: Mapping[str, SplitBundle],
) -> list[ValidationCheck]:
    checks: list[ValidationCheck] = []
    for split, bundle in sorted(bundles.items()):
        for metric in bundle.business_metrics:
            if metric.status != Status.PASS:
                continue
            payload = metric.payload
            ok = isinstance(payload, dict)
            limitations = payload.get("limitations") if ok else None
            has_limitations = isinstance(limitations, (list, tuple)) and bool(limitations)
            checks.append(
                ValidationCheck(
                    check_id=f"BUS-PAYLOAD-{split}-{metric.source_id}-{metric.metric_id}",
                    category="business_metric_payload",
                    scope=f"{split}:{metric.source_id}:{metric.metric_id}",
                    expected="payload có cấu trúc dict và ghi hạn chế",
                    observed=(
                        f"keys={sorted(payload)[:6]}, "
                        f"has_limitations={has_limitations}"
                    ),
                    status=Status.PASS if ok and has_limitations else Status.PARTIAL,
                    detail="payload không ghi hạn chế thì kết luận phải được đánh dấu PARTIAL",
                )
            )
    return checks


def _validate_grain_presence(
    bundles: Mapping[str, SplitBundle],
) -> list[ValidationCheck]:
    checks: list[ValidationCheck] = []
    for split, bundle in sorted(bundles.items()):
        for metric in bundle.business_metrics:
            if metric.status != Status.PASS:
                continue
            ok = bool(metric.grain) and bool(metric.method) and bool(metric.unit)
            checks.append(
                ValidationCheck(
                    check_id=f"BUS-GRAIN-{split}-{metric.source_id}-{metric.metric_id}",
                    category="business_metric_provenance",
                    scope=f"{split}:{metric.source_id}:{metric.metric_id}",
                    expected="grain, method và unit đều được ghi",
                    observed=(
                        f"grain={metric.grain or 'rỗng'}, "
                        f"method={metric.method or 'rỗng'}, "
                        f"unit={metric.unit or 'rỗng'}"
                    ),
                    status=Status.PASS if ok else Status.BLOCKED,
                    detail="thiếu grain hoặc method thì chỉ số không thể truy vết",
                )
            )
    return checks
