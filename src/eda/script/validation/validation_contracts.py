from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Mapping, Sequence

from common.enums import Status

QA_LEDGER_VERSION = "validation_ledger.v1"
NUMERIC_TOLERANCE = 1e-9


@dataclass(frozen=True)
class ValidationCheck:
    check_id: str
    category: str
    scope: str
    expected: str
    observed: str
    status: Status
    detail: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "check_id": self.check_id,
            "category": self.category,
            "scope": self.scope,
            "expected": self.expected,
            "observed": self.observed,
            "status": self.status.value,
            "detail": self.detail,
        }


@dataclass
class ValidationLedger:
    checks: list[ValidationCheck] = field(default_factory=list)

    def add(self, check: ValidationCheck) -> None:
        self.checks.append(check)

    def extend(self, checks: Sequence[ValidationCheck]) -> None:
        self.checks.extend(checks)

    def counts(self) -> dict[str, int]:
        counts: dict[str, int] = {}
        for check in self.checks:
            counts[check.status.value] = counts.get(check.status.value, 0) + 1
        return dict(sorted(counts.items()))

    def failures(self) -> tuple[ValidationCheck, ...]:
        return tuple(
            check
            for check in self.checks
            if check.status in {Status.BLOCKED, Status.PARTIAL}
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "validation_ledger_version": QA_LEDGER_VERSION,
            "check_count": len(self.checks),
            "status_counts": self.counts(),
            "checks": [check.to_dict() for check in self.checks],
        }
