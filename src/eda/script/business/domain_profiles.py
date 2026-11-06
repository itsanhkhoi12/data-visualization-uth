from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Sequence

from business.business_inventory import BusinessProfile
from common.enums import Status


@dataclass(frozen=True)
class DomainDiagnostic:
    business_id: str
    split: str
    domain: str | None
    diagnostic_id: str
    description: str
    status: Status
    evidence: str
    limitations: tuple[str, ...] = ()

    def to_dict(self) -> dict[str, Any]:
        return {
            "business_id": self.business_id,
            "split": self.split,
            "domain": self.domain,
            "diagnostic_id": self.diagnostic_id,
            "description": self.description,
            "status": self.status.value,
            "evidence": self.evidence,
            "limitations": list(self.limitations),
        }


DOMAIN_DIAGNOSTICS = {
    "pharmacy": (
        "lot and expiry tracking requires a lot identifier and an expiry date column",
        "stock position per lot is not derivable without lot-level stock events",
    ),
    "cafe_restaurant": (
        "topping co-located in the item cell must be split before item ranking",
        "shift boundaries depend on order creation time",
    ),
    "materials": (
        "quantities across heterogeneous units cannot be summed without a per-SKU base unit",
        "price units differ from quantity units",
    ),
    "phone_retail": (
        "trade-in value is not revenue and must be excluded from revenue aggregation",
        "instalment payments are debt repayment, not revenue",
    ),
    "motor_repair": (
        "a warranty ticket is a repair visit but not a revenue event",
        "vehicle identity depends on licence plate normalisation",
    ),
    "mother_baby": (
        "size and milk-number attributes come from the product catalogue, not from sale rows",
        "voucher value is positive-signed and belongs to the invoice date",
    ),
    "retail_grocery": (
        "base-unit quantity requires the unit conversion table",
        "walk-in customers are excluded from customer-level rankings",
    ),
    "retail_pos": (
        "a flat sales file without an order identifier cannot support order-level "
        "counts, cancel rates or customer rankings",
        "walk-in customers are excluded from customer-level rankings",
    ),
}


def profile_business_domain(
    profile: BusinessProfile, extra_diagnostics: Sequence[DomainDiagnostic] = ()
) -> tuple[DomainDiagnostic, ...]:
    diagnostics: list[DomainDiagnostic] = list(extra_diagnostics)
    domain = profile.domain_evidence
    if domain is None:
        diagnostics.append(
            DomainDiagnostic(
                business_id=profile.business_id,
                split=profile.split,
                domain=None,
                diagnostic_id=f"{profile.business_id}.domain_unresolved",
                description=(
                    "no industry classification could be established from README evidence; "
                    "filename-based inference is not accepted"
                ),
                status=Status.BLOCKED,
                evidence="README scanned without matching domain vocabulary",
                limitations=("domain-specific diagnostics are not applicable",),
            )
        )
        return tuple(diagnostics)
    description, limitation = DOMAIN_DIAGNOSTICS.get(
        domain, ("no specialised diagnostic available", "")
    )
    diagnostics.append(
        DomainDiagnostic(
            business_id=profile.business_id,
            split=profile.split,
            domain=domain,
            diagnostic_id=f"{profile.business_id}.{domain}",
            description=description,
            status=Status.PARTIAL,
            evidence=(
                f"README of {profile.business_id} matched domain vocabulary "
                f"for '{domain}'"
            ),
            limitations=(limitation,) if limitation else (),
        )
    )
    return tuple(diagnostics)
