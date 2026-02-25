"""
Sureify API client for agentOne (book of business and notifications).

Uses the shared API client (api.sureify_client) when SUREIFY_BASE_URL and
SUREIFY_CLIENT_ID / SUREIFY_CLIENT_SECRET are set; agent and API stay consistent
via get_policies() and get_notes(). Policy/Note shapes follow api.sureify_models.
Otherwise returns mock data for Marty McFly so the agent can run without the live API.
"""

from __future__ import annotations

import asyncio
import os
from typing import Any

# ---------------------------------------------------------------------------
# Mock data (used when Sureify API is not configured)
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

# Mock products when Sureify API is not configured (for agentTwo recommendations).
MOCK_PRODUCTS: list[dict[str, Any]] = [
    {
        "ID": "prod-mock-001",
        "productCode": "WL5",
        "name": "Whole Life 5",
        "carrierCode": "SureCo",
        "attributes": [{"name": "RiskProfile", "value": "Moderate"}, {"name": "Liquidity", "value": "Free Partial Withdrawals"}],
        "states": [["AZ", "CA", "OH"]],
    },
    {
        "ID": "prod-mock-002",
        "productCode": "FAP",
        "name": "Fixed Annuity Plus",
        "carrierCode": "SureCo",
        "attributes": [{"name": "RiskProfile", "value": "Conservative"}, {"name": "Liquidity", "value": "10% annually"}],
        "states": [["AZ", "CA", "OH", "TX"]],
    },
    {
        "ID": "prod-mock-003",
        "productCode": "MYGA7",
        "name": "Multi-Year Guarantee Annuity 7",
        "carrierCode": "SureCo",
        "attributes": [{"name": "RiskProfile", "value": "Moderate"}, {"name": "TimeHorizon", "value": "7 years"}],
        "states": [["AZ", "CA", "OH", "TX", "FL"]],
    },
]


def _is_sureify_configured() -> bool:
    """True if we have enough env to use the shared Sureify API client."""
    base = os.environ.get("SUREIFY_BASE_URL")
    client_id = os.environ.get("SUREIFY_CLIENT_ID")
    client_secret = os.environ.get("SUREIFY_CLIENT_SECRET")
    return bool(base and client_id and client_secret)


def _get_authenticated_client():
    """Return an authenticated SureifyClient from api.sureify_client, or None if not configured."""
    if not _is_sureify_configured():
        return None
    try:
        from api.sureify_client import SureifyAuthConfig, SureifyClient
    except ImportError:
        try:
            from api.src.api.sureify_client import SureifyAuthConfig, SureifyClient
        except ImportError:
            return None
    config = SureifyAuthConfig()
    client = SureifyClient(config)
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    loop.run_until_complete(client.authenticate())
    return client


def _model_to_dict(obj: Any) -> dict[str, Any]:
    """Serialize Pydantic model to dict (v1 .dict() or v2 .model_dump(mode='json'))."""
    if isinstance(obj, dict):
        return obj
    if hasattr(obj, "model_dump"):
        return obj.model_dump(mode="json")
    if hasattr(obj, "dict"):
        return obj.dict()
    return dict(obj)


def _policy_to_dict(policy: Any) -> dict[str, Any]:
    """Convert API Policy model to JSON-serializable dict; normalize ID to string for agent logic."""
    d = _model_to_dict(policy)
    # Ensure ID is a plain string for agent logic (logic uses policy.get("ID") or policy.get("policyNumber"))
    if "ID" in d and d["ID"] is not None and not isinstance(d["ID"], str):
        d["ID"] = str(d["ID"])
    return d


def _note_to_notification(note: Any) -> dict[str, Any]:
    """Convert API Note to agent notification shape (type, message, severity for PolicyNotification)."""
    n = _model_to_dict(note)
    message = n.get("title") or n.get("content") or "Note"
    return {"type": "note", "message": message, "severity": "info"}


def _policy_id_from_value(val: Any) -> str | None:
    """Extract string policy ID from API ID type or string."""
    if val is None:
        return None
    if isinstance(val, str):
        return val
    if hasattr(val, "root"):
        return getattr(val, "root", None)
    if hasattr(val, "__root__"):
        return getattr(val, "__root__", None)
    if isinstance(val, dict):
        if "root" in val:
            return val["root"]
        if "__root__" in val:
            return val["__root__"]
    return str(val)


def _product_to_dict(product: Any) -> dict[str, Any]:
    """Convert API Product model to JSON-serializable dict; normalize ID for agent/recommendations."""
    d = _model_to_dict(product)
    if "ID" not in d and "ID_1" in d:
        d["ID"] = d.pop("ID_1", None)
    if d.get("ID") is not None and not isinstance(d["ID"], str):
        d["ID"] = str(d["ID"])
    return d


def get_products(customer_identifier: str) -> list[dict[str, Any]]:
    """
    Fetch products from Sureify /puddle/products.

    Uses api.sureify_client.get_products when Sureify is configured (user_id passed
    as customer_identifier). Otherwise returns mock products for agentTwo recommendations.
    """
    client = _get_authenticated_client()
    if client is not None:
        try:
            from api.sureify_client import get_products as api_get_products
        except ImportError:
            from api.src.api.sureify_client import get_products as api_get_products
        products = api_get_products(client, user_id=customer_identifier)
        return [_product_to_dict(p) for p in products]
    if customer_identifier.lower().replace(" ", "") in ("martymcfly", "marty_mcfly", "marty-mcfly", ""):
        return [dict(p) for p in MOCK_PRODUCTS]
    return []


def get_book_of_business(customer_identifier: str) -> list[dict[str, Any]]:
    """
    Fetch the book of business (all policies) for a customer or advisor.

    Uses api.sureify_client.get_policies when Sureify is configured (SUREIFY_BASE_URL,
    SUREIFY_CLIENT_ID, SUREIFY_CLIENT_SECRET). customer_identifier is passed as user_id.
    Otherwise returns mock data for Marty McFly.
    """
    client = _get_authenticated_client()
    if client is not None:
        try:
            from api.sureify_client import get_policies
        except ImportError:
            from api.src.api.sureify_client import get_policies
        policies = get_policies(client, user_id=customer_identifier)
        return [_policy_to_dict(p) for p in policies]
    # Mock
    if customer_identifier.lower().replace(" ", "") in ("martymcfly", "marty_mcfly", "marty-mcfly"):
        return [dict(p) for p in MOCK_POLICIES]
    return []


def get_notifications_for_policies(
    policy_ids: list[str],
    user_id: str | None = None,
) -> dict[str, list[dict[str, Any]]]:
    """
    Fetch notifications applicable to each of the given policy IDs.

    When Sureify is configured, uses api.sureify_client.get_notes (with user_id
    when provided) and maps notes to policies by policyID. Otherwise returns mock notifications.
    Returns a dict mapping policy_id -> list of { type, message, severity }.
    """
    client = _get_authenticated_client()
    if client is not None:
        try:
            from api.sureify_client import get_notes
        except ImportError:
            from api.src.api.sureify_client import get_notes
        kwargs = {"user_id": user_id} if user_id else {}
        notes = get_notes(client, **kwargs)
        result: dict[str, list[dict[str, Any]]] = {pid: [] for pid in policy_ids}
        for note in notes:
            pid = _policy_id_from_value(getattr(note, "policyID", None))
            if pid and pid in result:
                result[pid].append(_note_to_notification(note))
        return result
    # Mock
    result = {}
    for pid in policy_ids:
        result[pid] = [dict(n) for n in MOCK_NOTIFICATIONS.get(pid, [])]
    return result
