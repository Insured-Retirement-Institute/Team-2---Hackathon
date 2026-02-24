"""
Sureify API client for book of business and notifications.

Reads SUREIFY_BASE_URL and SUREIFY_API_KEY from environment.
When base URL is not set, returns mock data for Marty McFly so the agent
and tools can be developed and tested without the live API.
"""

from __future__ import annotations

import os
from typing import Any

# ---------------------------------------------------------------------------
# Mock data for Marty McFly (used when SUREIFY_BASE_URL is not set)
# ---------------------------------------------------------------------------

MOCK_POLICIES: list[dict[str, Any]] = [
    {
        "ID": "pol-marty-001",
        "policyNumber": "WL-2024-001",
        "status": "Inforce",
        "statusCategory": "Inforce",
        "carrier": "SureCo",
        "effectiveDate": "2024-01-15",
        "productSnapshot": {
            "name": "Whole Life 5",
            "productCode": "WL5",
            "type": {"name": "Life"},
        },
        "deathBenefit": {"value": 500000, "currency": "USD"},
        "cashValue": {"value": 25000, "currency": "USD"},
        "modalPremium": {"value": 35000, "currency": "USD"},
        "paymentMode": "Monthly",
        "nextPremiumDueDate": "2025-03-01",
    },
    {
        "ID": "pol-marty-002",
        "policyNumber": "FA-2020-042",
        "status": "Inforce",
        "statusCategory": "Inforce",
        "carrier": "SureCo",
        "effectiveDate": "2020-06-01",
        "productSnapshot": {
            "name": "Fixed Annuity Plus",
            "productCode": "FAP",
            "type": {"name": "Annuity"},
        },
        "annuityValue": {"value": 180000, "currency": "USD"},
        "currentValue": {"value": 185000, "currency": "USD"},
        "payoutSchedule": None,
        "qualificationType": "Qualified",
    },
    {
        "ID": "pol-marty-003",
        "policyNumber": "TL-2019-100",
        "status": "Inforce",
        "statusCategory": "Inforce",
        "carrier": "SureCo",
        "effectiveDate": "2019-09-01",
        "productSnapshot": {
            "name": "Term 20",
            "productCode": "T20",
            "type": {"name": "Life"},
        },
        "faceAmount": {"value": 250000, "currency": "USD"},
        "coveredUntilDate": "2039-09-01",
        "modalPremium": {"value": 2800, "currency": "USD"},
        "paymentMode": "Annual",
    },
]

MOCK_NOTIFICATIONS: dict[str, list[dict[str, Any]]] = {
    "pol-marty-001": [
        {"type": "premium_due", "message": "Premium due in 30 days (Mar 1, 2025)", "severity": "info"},
        {"type": "replacement_opportunity", "message": "New product may offer better cash value growth", "severity": "info"},
    ],
    "pol-marty-002": [
        {"type": "income_activation", "message": "Eligible for income activation; RMD not yet started", "severity": "info"},
        {"type": "data_quality", "message": "Beneficiary contact info may be outdated", "severity": "warning"},
    ],
    "pol-marty-003": [
        {"type": "term_conversion", "message": "Term conversion window opens in 6 months", "severity": "info"},
    ],
}


def _get_base_url() -> str | None:
    return os.environ.get("SUREIFY_BASE_URL") or None


def _get_api_key() -> str | None:
    return os.environ.get("SUREIFY_API_KEY") or None


def get_book_of_business(customer_identifier: str) -> list[dict[str, Any]]:
    """
    Fetch the book of business (all policies) for a customer or advisor.

    Uses mock data when SUREIFY_BASE_URL is not set; otherwise calls the Sureify API.
    """
    base_url = _get_base_url()
    if not base_url:
        # Mock: return policies for Marty McFly (or any identifier for demo)
        if customer_identifier.lower().replace(" ", "") in ("martymcfly", "marty_mcfly", "marty-mcfly"):
            return [dict(p) for p in MOCK_POLICIES]
        return []

    # TODO: real API call when base_url and SUREIFY_API_KEY are set
    # headers = {"Authorization": f"Bearer {_get_api_key()}"}
    # response = requests.get(f"{base_url.rstrip('/')}/book-of-business", params={"customer": customer_identifier}, headers=headers)
    # return response.json().get("policies", [])
    return []


def get_notifications_for_policies(policy_ids: list[str]) -> dict[str, list[dict[str, Any]]]:
    """
    Fetch notifications applicable to each of the given policy IDs.

    Returns a dict mapping policy_id -> list of notification dicts
    (each with type, message, severity).
    """
    base_url = _get_base_url()
    if not base_url:
        result: dict[str, list[dict[str, Any]]] = {}
        for pid in policy_ids:
            result[pid] = [dict(n) for n in MOCK_NOTIFICATIONS.get(pid, [])]
        return result

    # TODO: real API call
    # response = requests.post(f"{base_url.rstrip('/')}/notifications/bulk", json={"policyIds": policy_ids}, headers=...)
    # return response.json()
    return {pid: [] for pid in policy_ids}
