"""Operational product taxonomy for M1.

CFPB product names changed over the years (e.g. 2017 and 2023 revisions). We map every
historical name onto one stable operational key so labels stay comparable over time.

Note (Red-Team #1): CFPB product/issue labels are chosen by the consumer when filing. They are a
noisy proxy for truth, not ground truth. The harness reports results with that caveat.
"""

from __future__ import annotations

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


# Synthetic bank: business lines and internal sub-teams (decision 2026-10-09).
# Lines mirror JPMorgan Chase's consumer business (Banking, Home Lending, Card Services & Auto).
# Sub-teams are synthetic, modeled on functions named in regulator actions (e.g. CFPB 2022 Wells Fargo
# order, 2024 Zelle suit) and on dispute rules banks must follow (Reg E, Reg Z, FCRA, Reg X).
SUB_TEAMS: dict[str, tuple[str, str]] = {
    "cb_account_servicing": ("Consumer Banking", "Everyday account servicing: deposits, access, statements, prepaid, other accounts"),
    "cb_fraud_disputes": ("Consumer Banking", "Fraud & error claims: unauthorized transactions and identity theft, including accounts or cards opened in the customer's name; money moved wrongly on debit, prepaid, checking or savings accounts and transfers (double charge, wrong amount)"),
    "cb_opening_onboarding": ("Consumer Banking", "Opening checking or savings accounts, identity checks, onboarding and new-account sign-up bonuses"),
    "cb_fees_overdraft": ("Consumer Banking", "Overdraft, low-balance and account fees"),
    "cb_payments_transfers": ("Consumer Banking", "Money transfers, wires, payment apps, money orders, and transfers that failed or got stuck with no money moved; not paying a credit card bill"),
    "ca_card_personal_loan_servicing": ("Card Services & Auto", "Card and personal-loan servicing: terms, fees, interest, rewards, credit limit changes, and paying the card bill (payments declined, misapplied or not credited)"),
    "ca_card_disputes": ("Card Services & Auto", "Disputed credit card charges: unauthorized or fraudulent charges, billing errors, double or wrong charges"),
    "ca_collections_recoveries": ("Card Services & Auto", "Collections, charge-offs, repossession, hardship on card, auto and unsecured debt"),
    "ca_card_applications": ("Card Services & Auto", "Card applications, approvals and credit decisions"),
    "ca_auto_servicing": ("Card Services & Auto", "Auto loan and lease servicing"),
    "hl_servicing_escrow": ("Home Lending", "Mortgage payments, escrow and servicing"),
    "hl_loss_mitigation": ("Home Lending", "Mortgage hardship, modifications, foreclosure and mortgage debt"),
    "hl_origination": ("Home Lending", "Mortgage applications, refinancing and closing"),
    "sh_closures_restrictions": ("Shared", "Closures, freezes and restrictions of any account (checking, savings or credit card), including closures triggered by suspected fraud"),
    "sh_credit_bureau_disputes": ("Shared", "Disputes that the bank reported wrong information to credit bureaus; not bank decisions that used a credit report"),
}

_BUREAU_ISSUES = {
    "Incorrect information on your report", "Improper use of your report",
    "Problem with fraud alerts or security freezes", "Credit monitoring or identity theft protection services",
    "Unable to get your credit report or credit score",
}


def sub_team_for(product: str, sub_product: str | None, issue: str | None) -> str:
    """Deterministic answer key: CFPB product / sub-product / issue -> synthetic sub-team."""
    issue = issue or ""
    if issue in _BUREAU_ISSUES or product.startswith("Credit reporting"):
        return "sh_credit_bureau_disputes"
    if product == "Checking or savings account":
        return {
            "Opening an account": "cb_opening_onboarding",
            "Closing an account": "sh_closures_restrictions",
            "Problem caused by your funds being low": "cb_fees_overdraft",
            "Problem with a lender or other company charging your account": "cb_fraud_disputes",
        }.get(issue, "cb_account_servicing")
    if product.startswith("Money transfer"):
        fraud = issue in {"Fraud or scam", "Unauthorized transactions or other transaction problem"}
        return "cb_fraud_disputes" if fraud else "cb_payments_transfers"
    if product == "Prepaid card":
        return "cb_fraud_disputes" if ("Fraud" in issue or "Unauthorized" in issue) else "cb_account_servicing"
    if product == "Student loan":
        return "cb_account_servicing"
    if product == "Credit card":
        return {
            "Problem with a purchase shown on your statement": "ca_card_disputes",
            "Problem with a company's investigation into an existing problem": "ca_card_disputes",
            "Getting a credit card": "ca_card_applications",
            "Closing your account": "sh_closures_restrictions",
            "Struggling to pay your bill": "ca_collections_recoveries",
        }.get(issue, "ca_card_personal_loan_servicing")
    if product.startswith("Payday loan"):
        return "ca_card_personal_loan_servicing"
    if product == "Vehicle loan or lease":
        return "ca_collections_recoveries" if issue in {"Repossession", "Struggling to pay your loan"} else "ca_auto_servicing"
    if product == "Mortgage":
        return {
            "Struggling to pay mortgage": "hl_loss_mitigation",
            "Applying for a mortgage or refinancing an existing mortgage": "hl_origination",
            "Closing on a mortgage": "hl_origination",
        }.get(issue, "hl_servicing_escrow")
    if product == "Debt collection":
        return "hl_loss_mitigation" if sub_product == "Mortgage debt" else "ca_collections_recoveries"
    if product == "Debt or credit management":
        return "ca_collections_recoveries"
    raise ValueError(f"No sub-team rule for product {product!r}")


def business_line_probabilities(sub_team_probabilities: dict[str, float]) -> dict[str, float]:
    """Sum sub-team probabilities into business-line probabilities."""
    out: dict[str, float] = {}
    for team, p in sub_team_probabilities.items():
        line = SUB_TEAMS[team][0]
        out[line] = out.get(line, 0.0) + p
    return out
