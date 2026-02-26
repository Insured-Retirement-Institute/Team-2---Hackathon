"""
Business logic for book-of-business agent: replacements, data quality,
income activation eligibility, and scheduled-meeting recommendation.

Applied to each policy after fetching from Sureify; results are attached
to PolicyOutput for the frontend.
"""

from __future__ import annotations

from datetime import date, datetime, timezone
from typing import Any


def _get_nested(data: dict[str, Any], *keys: str) -> Any:
    for k in keys:
        if isinstance(data, dict) and k in data:
            data = data[k]
        else:
            return None
    return data


# Policies renewing within this many days get a replacement notification.
RENEWAL_NOTIFICATION_DAYS = 30


def get_renewal_info(policy: dict[str, Any]) -> tuple[str | None, int | None]:
    """
    Extract renewal/maturity date and days until renewal from policy.
    Looks for renewalDate, maturityDate, nextPremiumDueDate, coveredUntilDate.
    Returns (renewal_date_str, days_until_renewal); (None, None) if unknown.
    """
    today = date.today()
    raw = (
        policy.get("renewalDate")
        or policy.get("maturityDate")
        or policy.get("nextPremiumDueDate")
        or policy.get("coveredUntilDate")
    )
    if not raw:
        return None, None
    if isinstance(raw, (int, float)):
        # Could be epoch ms
        try:
            d = datetime.fromtimestamp(raw / 1000.0, tz=timezone.utc).date()
        except (ValueError, OSError):
            return str(raw), None
        delta = (d - today).days
        return d.isoformat(), delta if delta >= 0 else None
    if isinstance(raw, str):
        for fmt in ("%Y-%m-%d", "%Y/%m/%d", "%m/%d/%Y", "%d-%b-%Y"):
            try:
                d = datetime.strptime(raw.strip()[:10], fmt).date()
                delta = (d - today).days
                return d.isoformat(), delta if delta >= 0 else None
            except ValueError:
                continue
        return raw, None
    return None, None


def check_replacement_opportunity(
    policy: dict[str, Any],
    days_until_renewal: int | None = None,
) -> tuple[bool, str | None]:
    """
    Determine if a replacement opportunity exists for this policy.
    If renewal_date is in the next 30 days, generates a replacement notification.
    Returns (replacement_opportunity: bool, reason: str | None).
    """
    product_name = _get_nested(policy, "productSnapshot", "name") or ""
    product_code = _get_nested(policy, "productSnapshot", "productCode") or ""
    status = (policy.get("status") or "").lower()

    if status != "inforce":
        return False, None

    # Renewal/maturity in next 30 days → replacement opportunity (CD/annuity renewal)
    if days_until_renewal is not None and 1 <= days_until_renewal <= RENEWAL_NOTIFICATION_DAYS:
        return True, "Policy maturing in next 30 days; consider replacement options"

    # Heuristic: fixed or older product types may have replacement options
    if "fixed" in product_name.lower() or "term" in product_name.lower():
        return True, "Fixed/term product may have replacement options for better value"
    if product_code and product_code.startswith("T"):  # Term
        return True, "Term policy; conversion or replacement may be beneficial"

    return False, None


def check_data_quality(policy: dict[str, Any]) -> tuple[list[str], str | None]:
    """
    Check for data quality issues (missing/invalid key fields).
    Returns (list of issue descriptions, overall severity: 'low'|'medium'|'high'|None).
    """
    issues: list[str] = []

    # Policy-level required fields
    if not policy.get("policyNumber"):
        issues.append("Missing policy number")
    if not policy.get("carrier"):
        issues.append("Missing carrier")
    if not policy.get("effectiveDate"):
        issues.append("Missing effective date")

    # Owner/contact info would come from roles/contacts in full API response
    # For mock we only have policy dict; in real flow we'd check roles/contacts
    roles = policy.get("roles") or []
    contacts = policy.get("contacts") or []
    if not roles and not policy.get("ID"):
        pass  # Mock may not have roles; don't flag
    if isinstance(roles, list) and len(roles) == 0 and isinstance(contacts, list) and len(contacts) == 0:
        # Only flag if we explicitly expect roles and have none
        if policy.get("ID") and "roles" in policy:
            issues.append("Missing roles/contacts")

    if not issues:
        return [], None
    if len(issues) >= 3:
        severity = "high"
    elif len(issues) >= 1:
        severity = "medium"
    else:
        severity = "low"
    return issues, severity


def check_income_activation_eligible(policy: dict[str, Any]) -> tuple[bool, str | None]:
    """
    Determine if the policy is eligible for income activation (e.g. annuity
    in accumulation phase, or RMD/withdrawal not yet started).
    Returns (eligible: bool, reason: str | None).
    """
    product_type = _get_nested(policy, "productSnapshot", "type", "name")
    if isinstance(product_type, dict):
        product_type = product_type.get("name")
    product_type = (product_type or "").lower()
    status = (policy.get("status") or "").lower()

    if status != "inforce":
        return False, None

    # Annuity without payout schedule is often in accumulation phase
    if "annuity" in product_type:
        payout = policy.get("payoutSchedule")
        if not payout:
            return True, "Annuity in accumulation phase; eligible for income activation or RMD"
        return True, "Annuity with payout; income options may apply"

    # Life with cash value might have loan/withdrawal options (simplified)
    if "life" in product_type and policy.get("cashValue"):
        return False, None

    return False, None


def recommend_schedule_meeting(
    replacement: bool,
    data_quality_issues: list[str],
    income_eligible: bool,
) -> tuple[bool, str | None]:
    """
    Recommend whether to schedule a meeting based on replacement opportunity,
    data quality issues, or income activation eligibility.
    Returns (schedule_meeting: bool, reason: str | None).
    """
    reasons: list[str] = []
    if replacement:
        reasons.append("Replacement opportunity")
    if data_quality_issues:
        reasons.append("Data quality issues to resolve")
    if income_eligible:
        reasons.append("Income activation eligible")

    if not reasons:
        return False, None
    return True, "; ".join(reasons)


def apply_business_logic(policy: dict[str, Any]) -> dict[str, Any]:
    """
    Apply all business rules to a single policy dict and return a dict
    with the added fields: renewal_date, days_until_renewal, replacement_opportunity,
    replacement_reason, data_quality_issues, data_quality_severity,
    income_activation_eligible, income_activation_reason, schedule_meeting, schedule_meeting_reason.
    """
    renewal_date_str, days_until_renewal = get_renewal_info(policy)
    repl, repl_reason = check_replacement_opportunity(policy, days_until_renewal)
    dq_issues, dq_severity = check_data_quality(policy)
    inc_eligible, inc_reason = check_income_activation_eligible(policy)
    schedule, schedule_reason = recommend_schedule_meeting(repl, dq_issues, inc_eligible)

    return {
        "renewal_date": renewal_date_str,
        "days_until_renewal": days_until_renewal,
        "replacement_opportunity": repl,
        "replacement_reason": repl_reason,
        "data_quality_issues": dq_issues,
        "data_quality_severity": dq_severity,
        "income_activation_eligible": inc_eligible,
        "income_activation_reason": inc_reason,
        "schedule_meeting": schedule,
        "schedule_meeting_reason": schedule_reason,
    }
