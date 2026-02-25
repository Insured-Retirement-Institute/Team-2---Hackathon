"""
IRI Annuity Renewal Intelligence API client and mapping from book-of-business.

- When IRI_API_BASE_URL is set, calls the live API (getAlerts, getAlertById, snooze, dismiss, getDashboardStats).
- Maps BookOfBusinessOutput (Sureify + agent logic) to RenewalAlert[] and DashboardStats per the OpenAPI spec.
"""

from __future__ import annotations

import json
import os
import re
from typing import Any

from agents.iri_schemas import AlertType, DashboardStats, Priority, RenewalAlert, Status
from agents.schemas import BookOfBusinessOutput, PolicyOutput


def _get_nested(data: dict[str, Any], *keys: str) -> Any:
    for k in keys:
        if isinstance(data, dict) and k in data:
            data = data[k]
        else:
            return None
    return data


def _format_currency(value: int | float | None) -> str:
    if value is None:
        return "$0"
    return f"${int(value):,}"


def _parse_currency_formatted(s: str) -> float:
    """Parse '$180,000' or '3.8%' (returns 0 for %) to numeric."""
    if not s or s == "N/A":
        return 0.0
    digits = re.sub(r"[^\d.]", "", s)
    if not digits:
        return 0.0
    try:
        return float(digits)
    except ValueError:
        return 0.0


def _policy_numeric_value(policy: dict[str, Any]) -> float:
    """Extract a single numeric value for totalValue (currentValue, annuityValue, cashValue, etc.)."""
    for key in ("currentValue", "annuityValue", "cashValue", "faceAmount", "deathBenefit"):
        v = _get_nested(policy, key, "value")
        if v is not None:
            try:
                return float(v)
            except (TypeError, ValueError):
                pass
    return 0.0


def _policy_rate_or_na(policy: dict[str, Any], rate_key: str) -> str:
    """Get rate from policy if present, else 'N/A'."""
    v = policy.get(rate_key) or _get_nested(policy, "rates", rate_key)
    if v is not None:
        if isinstance(v, (int, float)):
            return f"{v}%"
        if isinstance(v, str) and "%" not in v:
            return f"{v}%"
        return str(v)
    return "N/A"


def _policy_renewal_days(policy: dict[str, Any]) -> int:
    """Days until renewal or next material date; 0 if unknown."""
    # Could integrate with a date library; for now return 0 or a placeholder from mock
    due = policy.get("nextPremiumDueDate") or policy.get("coveredUntilDate")
    if due:
        return 30  # Placeholder
    return 0


def _build_alert_types_and_primary(
    policy_out: PolicyOutput,
) -> tuple[list[AlertType], AlertType, str]:
    """Build alertTypes list, primary alertType, and alertDescription from PolicyOutput."""
    types: list[AlertType] = []
    desc_parts: list[str] = []

    if policy_out.replacement_opportunity:
        types.append(AlertType.replacement_opportunity)
        if policy_out.replacement_reason:
            desc_parts.append(policy_out.replacement_reason)
        else:
            desc_parts.append("Replacement opportunity")
    if policy_out.data_quality_issues:
        types.append(AlertType.missing_info)
        desc_parts.append("Data quality: " + "; ".join(policy_out.data_quality_issues[:3]))
    if policy_out.income_activation_eligible:
        types.append(AlertType.income_planning)
        if policy_out.income_activation_reason:
            desc_parts.append(policy_out.income_activation_reason)
        else:
            desc_parts.append("Income activation eligible")
    if policy_out.schedule_meeting and AlertType.suitability_review not in types:
        types.append(AlertType.suitability_review)
        if policy_out.schedule_meeting_reason:
            desc_parts.append(policy_out.schedule_meeting_reason)

    if not types:
        types = [AlertType.suitability_review]
        desc_parts = ["Review recommended"]

    primary = types[0]
    alert_description = "; ".join(desc_parts) if desc_parts else primary.value.replace("_", " ").title()

    return types, primary, alert_description


def _priority_from_severity(
    severity: str | None, has_replacement: bool, has_urgent_notif: bool
) -> Priority:
    if severity == "high" or has_urgent_notif:
        return Priority.high
    if severity == "medium" or has_replacement:
        return Priority.medium
    return Priority.low


def map_book_of_business_to_iri_alerts(book: BookOfBusinessOutput) -> tuple[list[RenewalAlert], DashboardStats]:
    """
    Map BookOfBusinessOutput to IRI API shape: list of RenewalAlert and DashboardStats.

    One RenewalAlert per policy. Fills required IRI fields; uses N/A and 0 where
    policy data does not provide rate/renewal details.
    """
    alerts: list[RenewalAlert] = []
    total_value = 0.0
    high_count = 0
    urgent_count = 0

    for i, policy_out in enumerate(book.policies):
        policy = policy_out.policy
        policy_id = policy.get("ID") or policy.get("policyNumber") or f"policy-{i}"
        carrier = policy.get("carrier") or "N/A"
        current_value_fmt = _format_currency(_policy_numeric_value(policy))
        total_value += _policy_numeric_value(policy)
        # Use schema renewal fields when set (e.g. from logic), else derive from policy
        days_until = (
            policy_out.days_until_renewal
            if getattr(policy_out, "days_until_renewal", None) is not None
            else _policy_renewal_days(policy)
        )
        if days_until is None:
            days_until = 0
        if days_until <= 30:
            urgent_count += 1

        alert_types, primary_type, alert_description = _build_alert_types_and_primary(policy_out)
        has_data_exception = bool(policy_out.data_quality_issues)
        missing_fields = policy_out.data_quality_issues if has_data_exception else None
        priority = _priority_from_severity(
            policy_out.data_quality_severity,
            policy_out.replacement_opportunity,
            any(getattr(n, "severity", None) == "urgent" for n in policy_out.notifications),
        )
        if priority == Priority.high:
            high_count += 1

        renewal_date_str = f"{days_until} Days" if days_until > 0 else "N/A"
        current_rate = _policy_rate_or_na(policy, "currentRate")
        renewal_rate = _policy_rate_or_na(policy, "renewalRate")
        is_min_rate = policy.get("isMinRate", False)

        alert = RenewalAlert(
            id=f"alert-{policy_id}-renewal",
            policyId=policy_id,
            clientName=book.customer_identifier,
            carrier=carrier,
            renewalDate=renewal_date_str,
            daysUntilRenewal=days_until,
            currentRate=current_rate,
            renewalRate=renewal_rate,
            currentValue=current_value_fmt,
            isMinRate=is_min_rate,
            priority=priority,
            hasDataException=has_data_exception,
            status=Status.pending,
            alertType=primary_type,
            alertDescription=alert_description,
            missingFields=missing_fields,
            alertTypes=alert_types,
        )
        alerts.append(alert)

    stats = DashboardStats(
        total=len(alerts),
        high=high_count,
        urgent=urgent_count,
        totalValue=round(total_value, 2),
    )
    return alerts, stats


# ---------------------------------------------------------------------------
# IRI API HTTP client (when IRI_API_BASE_URL is set)
# ---------------------------------------------------------------------------

def _get_iri_base_url() -> str | None:
    return os.environ.get("IRI_API_BASE_URL") or None


def _request(
    method: str,
    path: str,
    *,
    params: dict[str, str] | None = None,
    json_body: dict | None = None,
) -> dict | list:
    base = _get_iri_base_url()
    if not base:
        return {"error": "IRI_API_BASE_URL not set", "message": "Configure IRI API base URL to call alerts API."}
    try:
        import urllib.request
        import urllib.error

        url = f"{base.rstrip('/')}{path}"
        if params:
            from urllib.parse import urlencode
            url += "?" + urlencode(params)
        data = json.dumps(json_body).encode() if json_body else None
        req = urllib.request.Request(url, data=data, method=method)
        req.add_header("Content-Type", "application/json")
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read().decode())
    except Exception as e:
        return {"error": "IRI_REQUEST_ERROR", "message": str(e)}


def get_iri_alerts(status: str | None = None, priority: str | None = None, carrier: str | None = None) -> list[dict] | dict:
    """GET /alerts with optional filters. Returns list of alerts or error dict."""
    params: dict[str, str] = {}
    if status:
        params["status"] = status
    if priority:
        params["priority"] = priority
    if carrier:
        params["carrier"] = carrier
    out = _request("GET", "/alerts", params=params or None)
    if isinstance(out, dict) and out.get("error"):
        return out
    return out if isinstance(out, list) else []


def get_iri_alert_by_id(alert_id: str) -> dict:
    """GET /alerts/{alertId} (getAlertDetail). Returns full AlertDetail or error dict."""
    out = _request("GET", f"/alerts/{alert_id}")
    return out if isinstance(out, dict) else {"error": "INVALID_RESPONSE", "message": "Expected object"}


def snooze_iri_alert(alert_id: str, snooze_days: int, reason: str | None = None) -> dict:
    """POST /alerts/{alertId}/snooze. Returns success object or error dict."""
    body = {"snoozeDays": snooze_days}
    if reason is not None:
        body["reason"] = reason
    out = _request("POST", f"/alerts/{alert_id}/snooze", json_body=body)
    return out if isinstance(out, dict) else {"error": "INVALID_RESPONSE", "message": "Expected object"}


def dismiss_iri_alert(alert_id: str, reason: str) -> dict:
    """POST /alerts/{alertId}/dismiss. Returns success object or error dict."""
    out = _request("POST", f"/alerts/{alert_id}/dismiss", json_body={"reason": reason})
    return out if isinstance(out, dict) else {"error": "INVALID_RESPONSE", "message": "Expected object"}


def get_iri_dashboard_stats() -> dict:
    """GET /dashboard/stats. Returns DashboardStats or error dict."""
    out = _request("GET", "/dashboard/stats")
    return out if isinstance(out, dict) else {"error": "INVALID_RESPONSE", "message": "Expected object"}


def run_iri_comparison(alert_id: str) -> dict:
    """POST /alerts/{alertId}/compare (runComparison). Returns ComparisonResult or error dict."""
    out = _request("POST", f"/alerts/{alert_id}/compare", json_body={})
    return out if isinstance(out, dict) else {"error": "INVALID_RESPONSE", "message": "Expected object"}


def get_iri_client_profile(client_id: str) -> dict:
    """GET /clients/{clientId}/profile (getClientProfile). Returns ClientProfile or error dict."""
    out = _request("GET", f"/clients/{client_id}/profile")
    return out if isinstance(out, dict) else {"error": "INVALID_RESPONSE", "message": "Expected object"}


def save_iri_client_profile(client_id: str, parameters: dict) -> dict:
    """PUT /clients/{clientId}/profile (saveClientProfile). Body = ComparisonParameters. Returns success or error dict."""
    out = _request("PUT", f"/clients/{client_id}/profile", json_body=parameters)
    return out if isinstance(out, dict) else {"error": "INVALID_RESPONSE", "message": "Expected object"}


def save_iri_suitability(alert_id: str, suitability_data: dict) -> dict:
    """PUT /alerts/{alertId}/suitability (saveSuitability). Body = SuitabilityData. Returns success or error dict."""
    out = _request("PUT", f"/alerts/{alert_id}/suitability", json_body=suitability_data)
    return out if isinstance(out, dict) else {"error": "INVALID_RESPONSE", "message": "Expected object"}


def save_iri_disclosures(alert_id: str, acknowledged_ids: list[str]) -> dict:
    """PUT /alerts/{alertId}/disclosures (saveDisclosures). Body = { acknowledgedIds }. Returns success or error dict."""
    out = _request("PUT", f"/alerts/{alert_id}/disclosures", json_body={"acknowledgedIds": acknowledged_ids})
    return out if isinstance(out, dict) else {"error": "INVALID_RESPONSE", "message": "Expected object"}


def submit_iri_transaction(alert_id: str, transaction_type: str, rationale: str, client_statement: str) -> dict:
    """POST /alerts/{alertId}/transaction (submitTransaction). type in [renew, replace]. Returns SubmissionData or error dict."""
    out = _request(
        "POST",
        f"/alerts/{alert_id}/transaction",
        json_body={
            "type": transaction_type,
            "rationale": rationale,
            "clientStatement": client_statement,
        },
    )
    return out if isinstance(out, dict) else {"error": "INVALID_RESPONSE", "message": "Expected object"}
