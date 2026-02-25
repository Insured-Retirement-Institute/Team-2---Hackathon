"""
Sureify API client for agentOne (book of business and notifications).

Uses the shared API client (api.sureify_client) when SUREIFY_BASE_URL and
SUREIFY_CLIENT_ID / SUREIFY_CLIENT_SECRET are set; agent and API stay consistent
via get_policies() and get_notes(). Policy/Note shapes follow api.sureify_models.
Otherwise returns mock data for Marty McFly so the agent can run without the live API.
"""

from __future__ import annotations

# UserID header sent to Sureify API for policy/notes/products requests
SUREIFY_USER_ID_HEADER = "1001"

import asyncio
import os
import sys
from datetime import date, timedelta
from pathlib import Path
from typing import Any

# Allow api.sureify_client / api.sureify_models when run from repo root (api lives under api/src)
_api_src = Path(__file__).resolve().parent.parent / "api" / "src"
if _api_src.exists() and str(_api_src) not in sys.path:
    sys.path.insert(0, str(_api_src))

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

def _mock_cd_policies_100k() -> list[dict[str, Any]]:
    """Two CDs maturing in the next 30 days, total 100k (50k + 50k)."""
    base = date.today()
    mat1 = (base + timedelta(days=15)).isoformat()
    mat2 = (base + timedelta(days=22)).isoformat()
    return [
        {
            "ID": "pol-cd100k-001",
            "policyNumber": "CD-2022-001",
            "status": "Inforce",
            "statusCategory": "Inforce",
            "carrier": "SureCo",
            "effectiveDate": "2022-03-15",
            "productSnapshot": {
                "name": "Certificate of Deposit 3Y",
                "productCode": "CD3",
                "type": {"name": "Fixed"},
            },
            "currentValue": {"value": 50000, "currency": "USD"},
            "annuityValue": {"value": 50000, "currency": "USD"},
            "maturityDate": mat1,
            "renewalDate": mat1,
            "currentRate": 4.25,
            "renewalRate": 3.5,
        },
        {
            "ID": "pol-cd100k-002",
            "policyNumber": "CD-2022-002",
            "status": "Inforce",
            "statusCategory": "Inforce",
            "carrier": "SureCo",
            "effectiveDate": "2022-06-01",
            "productSnapshot": {
                "name": "Certificate of Deposit 3Y",
                "productCode": "CD3",
                "type": {"name": "Fixed"},
            },
            "currentValue": {"value": 50000, "currency": "USD"},
            "annuityValue": {"value": 50000, "currency": "USD"},
            "maturityDate": mat2,
            "renewalDate": mat2,
            "currentRate": 4.0,
            "renewalRate": 3.25,
        },
    ]


def _mock_cd_policies_1m() -> list[dict[str, Any]]:
    """One CD maturing in the next 30 days, value 1M."""
    base = date.today()
    mat = (base + timedelta(days=10)).isoformat()
    return [
        {
            "ID": "pol-cd1m-001",
            "policyNumber": "CD-2021-100",
            "status": "Inforce",
            "statusCategory": "Inforce",
            "carrier": "SureCo",
            "effectiveDate": "2021-04-01",
            "productSnapshot": {
                "name": "Certificate of Deposit 5Y",
                "productCode": "CD5",
                "type": {"name": "Fixed"},
            },
            "currentValue": {"value": 1_000_000, "currency": "USD"},
            "annuityValue": {"value": 1_000_000, "currency": "USD"},
            "maturityDate": mat,
            "renewalDate": mat,
            "currentRate": 4.5,
            "renewalRate": 3.75,
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
    # CD 100k customer: renewal notification added by logic when maturity in 30 days
    "pol-cd100k-001": [
        {"type": "cd_maturity", "message": "CD maturing in 15 days; consider replacement options", "severity": "warning"},
    ],
    "pol-cd100k-002": [
        {"type": "cd_maturity", "message": "CD maturing in 22 days; consider replacement options", "severity": "warning"},
    ],
    "pol-cd1m-001": [
        {"type": "cd_maturity", "message": "CD maturing in 10 days ($1M); consider replacement options", "severity": "warning"},
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
    """True if we have enough env to use the shared Sureify API client (base URL + bearer token or client credentials)."""
    base = os.environ.get("SUREIFY_BASE_URL")
    if not base:
        return False
    if os.environ.get("SUREIFY_BEARER_TOKEN"):
        return True
    return bool(os.environ.get("SUREIFY_CLIENT_ID") and os.environ.get("SUREIFY_CLIENT_SECRET"))


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


def _product_option_to_canonical(p: dict[str, Any]) -> dict[str, Any]:
    """
    Normalize Puddle Data API ProductOption (GET /puddle/productOption) or legacy mock shape
    to canonical shape for agentTwo: product_id, name, carrier, rate, term, surrenderPeriod,
    freeWithdrawal, guaranteedMinRate, risk_profile (optional).
    """
    product_id = str(p.get("productId") or p.get("ID") or p.get("productCode") or "")
    name = str(p.get("name") or "Unknown")
    carrier = str(p.get("carrier") or p.get("carrierCode") or "")
    rate = p.get("rate")
    if rate is None and p.get("attributes"):
        for a in p.get("attributes") or []:
            if isinstance(a, dict) and (a.get("name") or a.get("key") or "").lower() == "rate":
                rate = a.get("value") or a.get("val")
                break
    if rate is None:
        rate = "N/A"
    if rate != "N/A" and isinstance(rate, (int, float)):
        rate = f"{rate}%"
    attrs = p.get("attributes") or []
    attr_map = {}
    for a in attrs:
        if isinstance(a, dict):
            k = (a.get("name") or a.get("key") or "").strip().lower()
            if k:
                attr_map[k] = a.get("value") or a.get("val")
    risk_profile = attr_map.get("riskprofile") or attr_map.get("risk_profile")
    return {
        "product_id": product_id,
        "name": name,
        "carrier": carrier,
        "rate": rate,
        "term": p.get("term"),
        "surrenderPeriod": p.get("surrenderPeriod"),
        "freeWithdrawal": p.get("freeWithdrawal"),
        "guaranteedMinRate": p.get("guaranteedMinRate"),
        "risk_profile": risk_profile,
        "attributes_map": attr_map,
        "states": p.get("states"),
    }


def get_products(customer_identifier: str) -> list[dict[str, Any]]:
    """
    Fetch product options from Sureify Puddle Data API (GET /puddle/productOption).

    Uses api.sureify_client.get_product_options when Sureify is configured (Puddle Data API
    schema). Returns canonical shape for agentTwo recommendations. Otherwise returns mock
    products.
    """
    client = _get_authenticated_client()
    if client is not None:
        try:
            from api.sureify_client import get_product_options as api_get_product_options
        except ImportError:
            from api.src.api.sureify_client import get_product_options as api_get_product_options
        options = api_get_product_options(client, user_id=customer_identifier or SUREIFY_USER_ID_HEADER)
        return [_product_option_to_canonical(o) for o in options]
    if customer_identifier.lower().replace(" ", "") in ("martymcfly", "marty_mcfly", "marty-mcfly", ""):
        return [_product_option_to_canonical(dict(p)) for p in MOCK_PRODUCTS]
    return []


def get_book_of_business(customer_identifier: str) -> list[dict[str, Any]]:
    """
    Fetch the book of business (all policies) for a customer or advisor.

    Uses api.sureify_client.get_policies when Sureify is configured (SUREIFY_BASE_URL,
    SUREIFY_CLIENT_ID, SUREIFY_CLIENT_SECRET). Sends UserID header 1001.
    Otherwise returns mock data for Marty McFly.
    """
    client = _get_authenticated_client()
    if client is not None:
        try:
            from api.sureify_client import get_policies
        except ImportError:
            from api.src.api.sureify_client import get_policies
        policies = get_policies(client, user_id=SUREIFY_USER_ID_HEADER)
        return [_policy_to_dict(p) for p in policies]
    # Mock: Marty McFly (default), Jane Doe (2 CDs 100k maturing in 30 days), John Smith (1 CD 1M maturing in 30 days)
    key = customer_identifier.lower().replace(" ", "").replace("-", "").replace("_", "")
    if key in ("martymcfly", "marty_mcfly", "marty"):
        return [dict(p) for p in MOCK_POLICIES]
    if key in ("janedoe", "jane_doe", "jane"):
        return [dict(p) for p in _mock_cd_policies_100k()]
    if key in ("johnsmith", "john_smith", "john"):
        return [dict(p) for p in _mock_cd_policies_1m()]
    return []


def get_notifications_for_policies(
    policy_ids: list[str],
    user_id: str | None = None,
) -> dict[str, list[dict[str, Any]]]:
    """
    Fetch notifications applicable to each of the given policy IDs.

    When Sureify is configured, uses api.sureify_client.get_notes with UserID header 1001
    and maps notes to policies by policyID. Otherwise returns mock notifications.
    Returns a dict mapping policy_id -> list of { type, message, severity }.
    """
    client = _get_authenticated_client()
    if client is not None:
        try:
            from api.sureify_client import get_notes
        except ImportError:
            from api.src.api.sureify_client import get_notes
        try:
            notes = get_notes(client, user_id=SUREIFY_USER_ID_HEADER)
        except Exception:
            notes = []
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


def get_suitability_data(customer_identifier: str | None = None) -> list[dict[str, Any]]:
    """Fetch suitability assessments from Puddle Data API (GET /puddle/suitabilityData). Returns [] when not configured. Pass customer_identifier as UserID when provided."""
    client = _get_authenticated_client()
    if client is None:
        return []
    try:
        from api.sureify_client import get_suitability_data as api_get_suitability
    except ImportError:
        from api.src.api.sureify_client import get_suitability_data as api_get_suitability
    user_id = (customer_identifier or "").strip() or SUREIFY_USER_ID_HEADER
    return api_get_suitability(client, user_id=user_id)


def get_disclosure_items() -> list[dict[str, Any]]:
    """Fetch disclosure items from Puddle Data API (GET /puddle/disclosureItem). Returns [] when not configured."""
    client = _get_authenticated_client()
    if client is None:
        return []
    try:
        from api.sureify_client import get_disclosure_items as api_get_disclosures
    except ImportError:
        from api.src.api.sureify_client import get_disclosure_items as api_get_disclosures
    return api_get_disclosures(client, user_id=SUREIFY_USER_ID_HEADER)


def get_product_options() -> list[dict[str, Any]]:
    """Fetch product options from Puddle Data API (GET /puddle/productOption). Returns [] when not configured."""
    client = _get_authenticated_client()
    if client is None:
        return []
    try:
        from api.sureify_client import get_product_options as api_get_product_options
    except ImportError:
        from api.src.api.sureify_client import get_product_options as api_get_product_options
    return api_get_product_options(client, user_id=SUREIFY_USER_ID_HEADER)


def get_visualization_products() -> list[dict[str, Any]]:
    """Fetch visualization products from Puddle Data API (GET /puddle/visualizationProduct). Returns [] when not configured."""
    client = _get_authenticated_client()
    if client is None:
        return []
    try:
        from api.sureify_client import get_visualization_products as api_get_viz
    except ImportError:
        from api.src.api.sureify_client import get_visualization_products as api_get_viz
    return api_get_viz(client, user_id=SUREIFY_USER_ID_HEADER)


def get_client_profiles(customer_identifier: str | None = None) -> list[dict[str, Any]]:
    """Fetch client profiles from Puddle Data API (GET /puddle/clientProfile). Returns [] when not configured. Pass customer_identifier as UserID when provided."""
    client = _get_authenticated_client()
    if client is None:
        return []
    try:
        from api.sureify_client import get_client_profiles as api_get_profiles
    except ImportError:
        from api.src.api.sureify_client import get_client_profiles as api_get_profiles
    user_id = (customer_identifier or "").strip() or SUREIFY_USER_ID_HEADER
    return api_get_profiles(client, user_id=user_id)
