"""Operational product taxonomy for M1.

CFPB product names changed over the years (e.g. 2017 and 2023 revisions). We map every
historical name onto one stable operational key so labels stay comparable over time.

Note (Red-Team #1): CFPB product/issue labels are chosen by the consumer when filing. They are a
noisy proxy for truth, not ground truth. The harness reports results with that caveat.
"""

from __future__ import annotations

# key -> description shown to the model (Jev Choice criteria)
PRODUCTS: dict[str, str] = {
    "credit_reporting": "Credit reports, credit scores, consumer reporting agencies, errors on a credit file, identity theft on a report",
    "debt_collection": "Collection of a debt: collector calls, letters, threats, debts not owed, validation of a debt",
    "credit_card": "Credit cards or store cards: charges, fees, rewards, disputes, card account management",
    "bank_account": "Checking or savings accounts: deposits, withdrawals, overdrafts, account opening or closing, bank fees",
    "mortgage": "Home loans: mortgage servicing, payments, escrow, modification, foreclosure, applying for a mortgage",
    "money_transfer": "Money transfers, wires, payment apps, remittances, virtual currency, money services",
    "vehicle_loan": "Auto loans or leases: payments, repossession, loan terms",
    "student_loan": "Federal or private student loans: servicing, repayment plans, forgiveness",
    "personal_loan": "Payday loans, title loans, installment or personal loans, cash advances",
    "debt_management": "Debt settlement, credit repair or debt management services",
    "prepaid_card": "Prepaid or gift cards, payroll or government benefit cards",
}

# Historical and current CFPB product names -> operational key
CFPB_PRODUCT_MAP: dict[str, str] = {
    "Credit reporting or other personal consumer reports": "credit_reporting",
    "Credit reporting, credit repair services, or other personal consumer reports": "credit_reporting",
    "Credit reporting": "credit_reporting",
    "Debt collection": "debt_collection",
    "Credit card": "credit_card",
    "Credit card or prepaid card": "credit_card",
    "Checking or savings account": "bank_account",
    "Bank account or service": "bank_account",
    "Mortgage": "mortgage",
    "Money transfer, virtual currency, or money service": "money_transfer",
    "Money transfers": "money_transfer",
    "Virtual currency": "money_transfer",
    "Vehicle loan or lease": "vehicle_loan",
    "Consumer Loan": "vehicle_loan",
    "Student loan": "student_loan",
    "Payday loan, title loan, personal loan, or advance loan": "personal_loan",
    "Payday loan, title loan, or personal loan": "personal_loan",
    "Payday loan": "personal_loan",
    "Debt or credit management": "debt_management",
    "Credit repair services": "debt_management",
    "Prepaid card": "prepaid_card",
}


def map_product(cfpb_product: str | None, cfpb_sub_product: str | None = None) -> str | None:
    """Return the operational product key, or None if unmappable."""
    if not cfpb_product:
        return None
    # The 2017-2022 combined category splits on sub-product.
    if cfpb_product == "Credit card or prepaid card" and cfpb_sub_product:
        if "prepaid" in cfpb_sub_product.lower() or "gift" in cfpb_sub_product.lower():
            return "prepaid_card"
    return CFPB_PRODUCT_MAP.get(cfpb_product.strip())


# Operational routing groups (ADR-007). Products that consumers often confuse share a group,
# so routing is judged on the decision an operations team actually acts on.
GROUPS: dict[str, tuple[str, ...]] = {
    "collections_credit": ("debt_collection", "credit_reporting", "debt_management"),
    "deposits_payments": ("bank_account", "money_transfer", "prepaid_card"),
    "cards": ("credit_card",),
    "home_lending": ("mortgage",),
    "consumer_lending": ("vehicle_loan", "student_loan", "personal_loan"),
}
GROUP_OF: dict[str, str] = {p: g for g, ps in GROUPS.items() for p in ps}


def group_probabilities(product_probabilities: dict[str, float]) -> dict[str, float]:
    """Sum product probabilities into routing-group probabilities."""
    out = {g: 0.0 for g in GROUPS}
    for p, v in product_probabilities.items():
        out[GROUP_OF[p]] += v
    return out
