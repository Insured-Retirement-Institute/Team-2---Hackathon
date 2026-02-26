"""
Sureify API client for agents (book of business and notifications).

Uses the shared API client (api.sureify_client) when SUREIFY_BASE_URL and
SUREIFY_CLIENT_ID / SUREIFY_CLIENT_SECRET are set. The new Puddle Data API
provides PolicyData, ProductOption, SuitabilityData, etc.

Otherwise returns mock data for Marty McFly so the agent can run without the live API.
"""

from __future__ import annotations

import asyncio
import os
from typing import Any

from agents.logging_config import get_logger

logger = get_logger(__name__)

# ---------------------------------------------------------------------------
# Mock data (used when Sureify API is not configured)
# ---------------------------------------------------------------------------

MOCK_POLICIES: list[dict[str, Any]] = [
    {
        "ID": "pol-marty-001",
        "clientId": "CLT-2024-00100",
        "contractId": "ANN-2020-5621",
        "clientName": "Marty McFly",
        "carrier": "Integrity Life Insurance",
        "productName": "SecureChoice Multi-Year Guarantee Annuity",
        "issueDate": "03/15/2018",
        "currentValue": "$180,000",
        "surrenderValue": "$176,400",
        "currentRate": "3.80%",
        "renewalRate": "1.50%",
        "guaranteedMinRate": "1.50%",
        "renewalDate": "03/15/2026",
        "isMinRateRenewal": True,
        "suitabilityStatus": "complete",
        "eligibilityStatus": "eligible",
        "features": {
            "surrenderCharge": "2.5% (Year 7 of 10)",
            "withdrawalAllowance": "10% annually penalty-free",
            "mvaPenalty": "-3.8% if surrendered today",
            "rateGuarantee": "5 years remaining",
        },
    },
    {
        "ID": "pol-marty-002",
        "clientId": "CLT-2024-00100",
        "contractId": "FA-2020-042",
        "clientName": "Marty McFly",
        "carrier": "SureCo",
        "productName": "Fixed Annuity Plus",
        "issueDate": "06/01/2020",
        "currentValue": "$185,000",
        "surrenderValue": "$180,000",
        "currentRate": "3.25%",
        "renewalRate": "2.00%",
        "guaranteedMinRate": "2.00%",
        "renewalDate": "06/01/2025",
        "isMinRateRenewal": True,
        "suitabilityStatus": "incomplete",
        "eligibilityStatus": "eligible",
        "features": {
            "surrenderCharge": "3% (Year 5 of 7)",
            "withdrawalAllowance": "10% annually penalty-free",
        },
    },
]

MOCK_NOTIFICATIONS: dict[str, list[dict[str, Any]]] = {
    "pol-marty-001": [
        {"type": "renewal_alert", "message": "Rate renewal coming up - may drop to minimum rate", "severity": "warning"},
        {"type": "replacement_opportunity", "message": "New product may offer better rate guarantee", "severity": "info"},
    ],
    "pol-marty-002": [
        {"type": "suitability_incomplete", "message": "Suitability assessment not complete", "severity": "warning"},
        {"type": "data_quality", "message": "Beneficiary contact info may be outdated", "severity": "warning"},
    ],
}

MOCK_PRODUCTS: list[dict[str, Any]] = [
    {
        "ID": "prod-001",
        "productId": "PROD-FLEXGROWTH-P-7",
        "name": "FlexGrowth Plus MYGA",
        "carrier": "Great American",
        "rate": "4.25%",
        "term": "7 years",
        "premiumBonus": "3.0%",
        "surrenderPeriod": "7",
        "surrenderCharge": "7% (declining 1% annually)",
        "freeWithdrawal": "10%",
        "deathBenefit": "Enhanced -- return of premium plus interest",
        "guaranteedMinRate": "2.50%",
        "riders": ["Guaranteed Lifetime Withdrawal Benefit", "Nursing Home Confinement Waiver"],
        "features": ["Tax-deferred accumulation", "Penalty-free systematic withdrawals"],
        "liquidity": "10% annual free withdrawal; full liquidity after surrender period",
        "mvaPenalty": "Subject to MVA during surrender period",
        "licensingApproved": True,
    },
    {
        "ID": "prod-002",
        "productId": "PROD-SAFEHARBOR-F-5",
        "name": "SafeHarbor Fixed Annuity",
        "carrier": "Athene",
        "rate": "3.75%",
        "term": "5 years",
        "premiumBonus": None,
        "surrenderPeriod": "5",
        "surrenderCharge": "5% (declining 1% annually)",
        "freeWithdrawal": "10%",
        "deathBenefit": "Standard -- accumulated contract value",
        "guaranteedMinRate": "2.00%",
        "riders": ["Nursing Home Confinement Waiver"],
        "features": ["Tax-deferred accumulation", "No market value adjustment"],
        "liquidity": "10% annual free withdrawal; RMD-friendly",
        "mvaPenalty": None,
        "licensingApproved": False,
        "licensingDetails": "Appointment with Athene required -- apply at carrier portal",
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
        logger.debug("Sureify API not configured, using mock data")
        return None
    try:
        from api.sureify_client import SureifyAuthConfig, SureifyClient
    except ImportError:
        try:
            from api.src.api.sureify_client import SureifyAuthConfig, SureifyClient
        except ImportError:
            logger.error("Sureify client import failed - api.sureify_client not found")
            return None
    try:
        config = SureifyAuthConfig()
        client = SureifyClient(config)
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        loop.run_until_complete(client.authenticate())
        logger.info("Sureify API client authenticated successfully")
        return client
    except Exception:
        logger.exception("Sureify API authentication failed")
        return None


def _model_to_dict(obj: Any) -> dict[str, Any]:
    """Serialize Pydantic model to dict (v1 .dict() or v2 .model_dump(mode='json'))."""
    if isinstance(obj, dict):
        return obj
    if hasattr(obj, "model_dump"):
        return obj.model_dump(mode="json")
    if hasattr(obj, "dict"):
        return obj.dict()
    return dict(obj)


def _run_async(coro):
    """Run an async coroutine synchronously."""
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    return loop.run_until_complete(coro)


def get_products(customer_identifier: str) -> list[dict[str, Any]]:
    """
    Fetch product options from Sureify /puddle/productOption.

    Uses api.sureify_client.get_product_options when Sureify is configured.
    Otherwise returns mock products for agent recommendations.
    """
    client = _get_authenticated_client()
    if client is not None:
        try:
            products = _run_async(client.get_product_options())
            logger.info("get_products: fetched %d products from Sureify API", len(products))
            return [_model_to_dict(p) for p in products]
        except Exception:
            logger.exception("get_products: Sureify API call failed")
            return []
    if customer_identifier.lower().replace(" ", "") in ("martymcfly", "marty_mcfly", "marty-mcfly", ""):
        logger.debug("get_products: using mock data for %s", customer_identifier)
        return [dict(p) for p in MOCK_PRODUCTS]
    logger.debug("get_products: no products for unknown customer %s", customer_identifier)
    return []


def get_book_of_business(customer_identifier: str) -> list[dict[str, Any]]:
    """
    Fetch the book of business (all policies) for a customer or advisor.

    Uses api.sureify_client.get_policy_data when Sureify is configured.
    Otherwise returns mock data for Marty McFly.
    """
    client = _get_authenticated_client()
    if client is not None:
        try:
            policies = _run_async(client.get_policy_data())
            logger.info("get_book_of_business: fetched %d policies from Sureify API for %s", len(policies), customer_identifier)
            return [_model_to_dict(p) for p in policies]
        except Exception:
            logger.exception("get_book_of_business: Sureify API call failed for %s", customer_identifier)
            return []
    # Mock
    if customer_identifier.lower().replace(" ", "") in ("martymcfly", "marty_mcfly", "marty-mcfly"):
        logger.debug("get_book_of_business: using mock data for %s", customer_identifier)
        return [dict(p) for p in MOCK_POLICIES]
    logger.debug("get_book_of_business: no policies for unknown customer %s", customer_identifier)
    return []


def get_notifications_for_policies(
    policy_ids: list[str],
    user_id: str | None = None,
) -> dict[str, list[dict[str, Any]]]:
    """
    Get notifications applicable to each of the given policy IDs.

    The new Puddle API doesn't have a separate notifications endpoint.
    Notifications are derived from policy data (suitabilityStatus, isMinRateRenewal, etc.).
    When Sureify is configured, we fetch policy data and generate notifications based on status.
    Otherwise returns mock notifications.
    """
    client = _get_authenticated_client()
    if client is not None:
        try:
            policies = _run_async(client.get_policy_data())
            result: dict[str, list[dict[str, Any]]] = {pid: [] for pid in policy_ids}
            for policy in policies:
                pid = policy.ID
                if pid not in result:
                    continue
                notifications = []
                # Generate notifications based on policy status
                if policy.isMinRateRenewal:
                    notifications.append({
                        "type": "renewal_alert",
                        "message": f"Rate renewal on {policy.renewalDate} will drop to minimum rate ({policy.guaranteedMinRate})",
                        "severity": "warning",
                    })
                if policy.suitabilityStatus.value != "complete":
                    notifications.append({
                        "type": "suitability_incomplete",
                        "message": f"Suitability assessment is {policy.suitabilityStatus.value}",
                        "severity": "warning",
                    })
                if policy.eligibilityStatus.value == "restricted":
                    notifications.append({
                        "type": "eligibility_restricted",
                        "message": "Policy has restricted eligibility for renewal/exchange",
                        "severity": "info",
                    })
                result[pid] = notifications
            logger.debug("get_notifications_for_policies: generated notifications for %d policies from Sureify", len(policy_ids))
            return result
        except Exception:
            logger.exception("get_notifications_for_policies: Sureify API call failed")
            return {pid: [] for pid in policy_ids}
    # Mock
    logger.debug("get_notifications_for_policies: using mock data for %d policies", len(policy_ids))
    result = {}
    for pid in policy_ids:
        result[pid] = [dict(n) for n in MOCK_NOTIFICATIONS.get(pid, [])]
    return result
