"""
Strands agent: Sureify book of business for Marty McFly.

Scans Sureify APIs (or mock), lists all policies as JSON using frontend-relevant
shapes, attaches notifications, and applies business logic (replacements,
data quality, income activation, scheduled-meeting recommendation).

Run from repo root: PYTHONPATH=. uv run python -m agents.agent_one

Environment & endpoints (load from repo root .env):
  Puddle Data API (Sureify): SUREIFY_BASE_URL + SUREIFY_BEARER_TOKEN or client credentials.
    Endpoints (agents.sureify_client): GET {base}/puddle/policyData, /puddle/suitabilityData,
    /puddle/disclosureItem, /puddle/productOption, /puddle/visualizationProduct, /puddle/clientProfile,
    /puddle/notes. Schema: agents/puddle_api_spec.yaml (OpenAPI 1.0.0).
  IRI API (alerts/dashboard/compare/action): IRI_API_BASE_URL.
    Endpoints: GET/POST/PUT under {base}/alerts, {base}/dashboard/stats, {base}/clients/{id}/profile.
"""

from __future__ import annotations

import json
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path

_repo_root = Path(__file__).resolve().parent.parent.parent
if str(_repo_root) not in sys.path:
    sys.path.insert(0, str(_repo_root))

_env_file = _repo_root / ".env"
if _env_file.exists():
    try:
        from dotenv import load_dotenv
        load_dotenv(_env_file)
    except ImportError:
        pass

import os as _os
_os.environ.pop("AWS_BEARER_TOKEN_BEDROCK", None)

from strands import Agent, tool

from agents.iri_client import (
    dismiss_iri_alert as iri_dismiss,
    get_iri_alert_by_id as iri_get_alert,
    get_iri_alerts as iri_get_alerts,
    get_iri_client_profile as iri_get_client_profile,
    get_iri_dashboard_stats as iri_get_stats,
    map_book_of_business_to_iri_alerts,
    run_iri_comparison as iri_run_comparison,
    save_iri_client_profile as iri_save_client_profile,
    save_iri_disclosures as iri_save_disclosures,
    save_iri_suitability as iri_save_suitability,
    submit_iri_transaction as iri_submit_transaction,
    snooze_iri_alert as iri_snooze,
)
from agents.audit_writer import persist_agent_one_book_of_business, persist_event
from agents.logic import RENEWAL_NOTIFICATION_DAYS, apply_business_logic
from agents.responsible_ai_schemas import AgentId, AgentRunEvent
from agents.schemas import BookOfBusinessOutput, PolicyNotification, PolicyOutput
from agents.sureify_client import (
    get_book_of_business as fetch_policies,
    get_client_profiles as fetch_client_profiles,
    get_disclosure_items as fetch_disclosure_items,
    get_notifications_for_policies as fetch_notifications,
    get_product_options as fetch_product_options,
    get_suitability_data as fetch_suitability_data,
    get_visualization_products as fetch_visualization_products,
)


@tool
def get_book_of_business(customer_identifier: str) -> str:
    """Get the book of business (all policies) for a customer or advisor from Sureify."""
    policies = fetch_policies(customer_identifier)
    return json.dumps(policies, default=str, indent=2)


@tool
def get_notifications_for_policies(policy_ids: str) -> str:
    """Get notifications applicable to the given policies."""
    try:
        ids = json.loads(policy_ids)
    except json.JSONDecodeError:
        return json.dumps({"error": "policy_ids must be a JSON array of strings"})
    if not isinstance(ids, list):
        return json.dumps({"error": "policy_ids must be a JSON array"})
    result = fetch_notifications(ids)
    return json.dumps(result, default=str, indent=2)


@tool
def get_puddle_suitability_data() -> str:
    """Get all suitability assessments from the Puddle Data API (GET /puddle/suitabilityData)."""
    data = fetch_suitability_data()
    return json.dumps(data, default=str, indent=2)


@tool
def get_puddle_disclosure_items() -> str:
    """Get all disclosure items from the Puddle Data API (GET /puddle/disclosureItem)."""
    data = fetch_disclosure_items()
    return json.dumps(data, default=str, indent=2)


@tool
def get_puddle_product_options() -> str:
    """Get all product options from the Puddle Data API (GET /puddle/productOption)."""
    data = fetch_product_options()
    return json.dumps(data, default=str, indent=2)


@tool
def get_puddle_visualization_products() -> str:
    """Get all visualization products from the Puddle Data API (GET /puddle/visualizationProduct)."""
    data = fetch_visualization_products()
    return json.dumps(data, default=str, indent=2)


@tool
def get_puddle_client_profiles() -> str:
    """Get all client profiles from the Puddle Data API (GET /puddle/clientProfile)."""
    data = fetch_client_profiles()
    return json.dumps(data, default=str, indent=2)


@tool
def get_book_of_business_with_notifications_and_flags(customer_identifier: str) -> str:
    """Get the full book of business with notifications and business logic flags."""
    policies = fetch_policies(customer_identifier)
    if not policies:
        out = BookOfBusinessOutput(customer_identifier=customer_identifier, policies=[])
        return out.model_dump_json(indent=2)

    policy_ids = [p.get("ID") or p.get("policyNumber") or "" for p in policies]
    policy_ids = [x for x in policy_ids if x]
    notif_by_policy = fetch_notifications(policy_ids, customer_identifier)

    outputs: list[PolicyOutput] = []
    for p in policies:
        pid = p.get("ID") or p.get("policyNumber") or ""
        logic = apply_business_logic(p)
        notifs = notif_by_policy.get(pid) or []
        notifications = [
            PolicyNotification(
                notification_type=n.get("type", "unknown"),
                message=n.get("message", ""),
                policy_id=pid or None,
                severity=n.get("severity"),
            )
            for n in notifs
        ]
        # Generate replacement notification when policy renews in next 30 days
        days_until = logic.get("days_until_renewal")
        if days_until is not None and 1 <= days_until <= RENEWAL_NOTIFICATION_DAYS:
            notifications.append(
                PolicyNotification(
                    notification_type="renewal_in_30_days",
                    message=f"Policy maturing in {days_until} days; consider replacement options",
                    policy_id=pid or None,
                    severity="warning",
                )
            )
        outputs.append(
            PolicyOutput(
                policy=p,
                notifications=notifications,
                replacement_opportunity=logic["replacement_opportunity"],
                replacement_reason=logic["replacement_reason"],
                data_quality_issues=logic["data_quality_issues"],
                data_quality_severity=logic["data_quality_severity"],
                income_activation_eligible=logic["income_activation_eligible"],
                income_activation_reason=logic["income_activation_reason"],
                schedule_meeting=logic["schedule_meeting"],
                schedule_meeting_reason=logic["schedule_meeting_reason"],
                renewal_date=logic.get("renewal_date"),
                days_until_renewal=logic.get("days_until_renewal"),
            )
        )

    out = BookOfBusinessOutput(customer_identifier=customer_identifier, policies=outputs)
    payload_dict = out.model_dump(mode="json", exclude_none=True)
    run_id = str(uuid.uuid4())
    created_at = datetime.now(timezone.utc).isoformat()
    persist_agent_one_book_of_business(
        run_id=run_id,
        created_at=created_at,
        customer_identifier=customer_identifier,
        payload=payload_dict,
    )
    return json.dumps(payload_dict, indent=2, default=str)


@tool
def get_book_of_business_json_schema() -> str:
    """Return the JSON schema for the book-of-business output."""
    schema = BookOfBusinessOutput.model_json_schema(mode="serialization")
    return json.dumps(schema, indent=2)


@tool
def get_book_of_business_as_iri_alerts(customer_identifier: str) -> str:
    """Get the book of business in IRI API format: RenewalAlert list + DashboardStats."""
    raw = get_book_of_business_with_notifications_and_flags(customer_identifier)
    book = BookOfBusinessOutput.model_validate_json(raw)
    alerts, stats = map_book_of_business_to_iri_alerts(book)
    return json.dumps(
        {
            "alerts": [a.model_dump(mode="json", exclude_none=True) for a in alerts],
            "dashboardStats": stats.model_dump(mode="json"),
        },
        indent=2,
    )


@tool
def get_iri_alerts(status: str = "", priority: str = "", carrier: str = "") -> str:
    """Get renewal alerts from the IRI API (GET /alerts)."""
    result = iri_get_alerts(status=status or None, priority=priority or None, carrier=carrier or None)
    return json.dumps(result, default=str, indent=2)


@tool
def get_iri_alert_by_id(alert_id: str) -> str:
    """Get full alert detail from the IRI API (GET /alerts/{alertId})."""
    result = iri_get_alert(alert_id)
    return json.dumps(result, default=str, indent=2)


@tool
def snooze_iri_alert(alert_id: str, snooze_days: int, reason: str = "") -> str:
    """Snooze an IRI alert (POST /alerts/{alertId}/snooze)."""
    result = iri_snooze(alert_id, snooze_days, reason or None)
    return json.dumps(result, default=str, indent=2)


@tool
def dismiss_iri_alert(alert_id: str, reason: str) -> str:
    """Dismiss an IRI alert (POST /alerts/{alertId}/dismiss)."""
    result = iri_dismiss(alert_id, reason)
    return json.dumps(result, default=str, indent=2)


@tool
def get_iri_dashboard_stats() -> str:
    """Get dashboard statistics from the IRI API (GET /dashboard/stats)."""
    result = iri_get_stats()
    return json.dumps(result, default=str, indent=2)


@tool
def run_iri_comparison(alert_id: str) -> str:
    """Run comparison analysis for an alert (POST /alerts/{alertId}/compare)."""
    result = iri_run_comparison(alert_id)
    return json.dumps(result, default=str, indent=2)


@tool
def get_iri_client_profile(client_id: str) -> str:
    """Get client profile from the IRI API (GET /clients/{clientId}/profile)."""
    result = iri_get_client_profile(client_id)
    return json.dumps(result, default=str, indent=2)


@tool
def save_iri_client_profile(client_id: str, parameters_json: str) -> str:
    """Save client profile (PUT /clients/{clientId}/profile)."""
    try:
        params = json.loads(parameters_json)
    except json.JSONDecodeError:
        return json.dumps({"error": "Invalid JSON", "message": "parameters_json must be valid JSON"})
    result = iri_save_client_profile(client_id, params)
    return json.dumps(result, default=str, indent=2)


@tool
def save_iri_suitability(alert_id: str, suitability_json: str) -> str:
    """Save suitability data for an alert (PUT /alerts/{alertId}/suitability)."""
    try:
        data = json.loads(suitability_json)
    except json.JSONDecodeError:
        return json.dumps({"error": "Invalid JSON", "message": "suitability_json must be valid JSON"})
    result = iri_save_suitability(alert_id, data)
    return json.dumps(result, default=str, indent=2)


@tool
def save_iri_disclosures(alert_id: str, acknowledged_ids_json: str) -> str:
    """Save disclosure acknowledgments (PUT /alerts/{alertId}/disclosures)."""
    try:
        ids = json.loads(acknowledged_ids_json)
    except json.JSONDecodeError:
        return json.dumps({"error": "Invalid JSON", "message": "acknowledged_ids_json must be a JSON array"})
    if not isinstance(ids, list):
        return json.dumps({"error": "Invalid input", "message": "acknowledged_ids must be an array"})
    result = iri_save_disclosures(alert_id, ids)
    return json.dumps(result, default=str, indent=2)


@tool
def submit_iri_transaction(alert_id: str, transaction_type: str, rationale: str, client_statement: str) -> str:
    """Submit transaction for an alert (POST /alerts/{alertId}/transaction)."""
    result = iri_submit_transaction(alert_id, transaction_type, rationale, client_statement)
    return json.dumps(result, default=str, indent=2)


BOOK_OF_BUSINESS_SYSTEM_PROMPT = """You are an assistant that uses the **Puddle Data API** (Sureify) and **IRI API** to produce the book of business and related data for a given customer.

**Puddle Data API** (OpenAPI 1.0.0, agents/puddle_api_spec.yaml): All endpoints use UserID header 1001 and optional persona=agent. When configured, use:
- **Policy data:** `get_book_of_business` / `get_book_of_business_with_notifications_and_flags` (GET /puddle/policyData) for annuity policies with values, rates, renewal status, features.
- **Suitability:** `get_puddle_suitability_data` (GET /puddle/suitabilityData) for suitability assessments (objectives, risk, score).
- **Disclosures:** `get_puddle_disclosure_items` (GET /puddle/disclosureItem) for required/optional disclosure documents.
- **Products:** `get_puddle_product_options` (GET /puddle/productOption) and `get_puddle_visualization_products` (GET /puddle/visualizationProduct) for product options and comparison/chart data.
- **Clients:** `get_puddle_client_profiles` (GET /puddle/clientProfile) for client profiles and comparison parameters.

Your main task is to produce the **book of business** for **Marty McFly** (or the customer identifier you are given):
1. Use `get_book_of_business_with_notifications_and_flags` to get policies with notifications and business logic flags (replacement_opportunity, data_quality_issues, income_activation_eligible, schedule_meeting, etc.).
2. Optionally use the Puddle tools above when the user asks for suitability, disclosures, product options, visualization data, or client profiles.
3. Output the full JSON with "customer_identifier" and "policies" array; the frontend consumes this as-is.

When the user asks for a JSON schema for table design, call `get_book_of_business_json_schema`.

**IRI API:** For renewal alerts and dashboard format use `get_book_of_business_as_iri_alerts`. For direct IRI operations use: `get_iri_alerts`, `get_iri_alert_by_id`, `snooze_iri_alert`, `dismiss_iri_alert`, `get_iri_dashboard_stats`, `run_iri_comparison`, `get_iri_client_profile`, `save_iri_client_profile`, `save_iri_suitability`, `save_iri_disclosures`, `submit_iri_transaction`.
"""


def create_agent() -> Agent:
    """Create the Strands agent with book-of-business tools and system prompt."""
    return Agent(
        tools=[
            get_book_of_business,
            get_notifications_for_policies,
            get_book_of_business_with_notifications_and_flags,
            get_book_of_business_json_schema,
            get_book_of_business_as_iri_alerts,
            get_puddle_suitability_data,
            get_puddle_disclosure_items,
            get_puddle_product_options,
            get_puddle_visualization_products,
            get_puddle_client_profiles,
            get_iri_alerts,
            get_iri_alert_by_id,
            snooze_iri_alert,
            dismiss_iri_alert,
            get_iri_dashboard_stats,
            run_iri_comparison,
            get_iri_client_profile,
            save_iri_client_profile,
            save_iri_suitability,
            save_iri_disclosures,
            submit_iri_transaction,
        ],
        system_prompt=BOOK_OF_BUSINESS_SYSTEM_PROMPT,
    )


def _emit_agent_one_event(
    run_id: str,
    input_summary: dict,
    success: bool,
    error_message: str | None = None,
    explanation_summary: str | None = None,
) -> None:
    event = AgentRunEvent(
        event_id=str(uuid.uuid4()),
        timestamp=datetime.now(timezone.utc).isoformat(),
        agent_id=AgentId.agent_one,
        run_id=run_id,
        client_id_scope="Marty McFly",
        input_summary=input_summary,
        success=success,
        error_message=error_message,
        explanation_summary=explanation_summary,
        input_validation_passed=True,
        guardrail_triggered=None,
    )
    persist_event(event)


def main() -> None:
    import os
    run_id = str(uuid.uuid4())
    if os.environ.get("SUREIFY_AGENT_SCHEMA_ONLY"):
        print(get_book_of_business_json_schema())
        _emit_agent_one_event(
            run_id,
            {"customer_identifier_scope": "Marty McFly", "tools_used": ["get_book_of_business_json_schema"]},
            True,
            explanation_summary="JSON schema returned",
        )
        return
    if os.environ.get("SUREIFY_AGENT_TOOL_ONLY"):
        try:
            json_out = get_book_of_business_with_notifications_and_flags("Marty McFly")
            print(json_out)
            _emit_agent_one_event(
                run_id,
                {"customer_identifier_scope": "Marty McFly", "tools_used": ["get_book_of_business_with_notifications_and_flags"]},
                True,
                explanation_summary="Book of business produced with notifications and flags",
            )
        except Exception as e:
            _emit_agent_one_event(
                run_id,
                {"customer_identifier_scope": "Marty McFly", "tools_used": ["get_book_of_business_with_notifications_and_flags"]},
                False,
                error_message=str(e),
            )
            raise
        return
    if os.environ.get("SUREIFY_AGENT_IRI_ONLY"):
        try:
            print(get_book_of_business_as_iri_alerts("Marty McFly"))
            _emit_agent_one_event(
                run_id,
                {"customer_identifier_scope": "Marty McFly", "tools_used": ["get_book_of_business_as_iri_alerts"]},
                True,
                explanation_summary="Book of business as IRI alerts",
            )
        except Exception as e:
            _emit_agent_one_event(
                run_id,
                {"customer_identifier_scope": "Marty McFly", "tools_used": ["get_book_of_business_as_iri_alerts"]},
                False,
                error_message=str(e),
            )
            raise
        return
    try:
        agent = create_agent()
        user_message = "Produce the book of business for Marty McFly. List all policies as JSON with notifications and which ones should have a scheduled meeting with the customer."
        result = agent(user_message)
        print(result.get("output", result) if isinstance(result, dict) else result)
        _emit_agent_one_event(
            run_id,
            {"customer_identifier_scope": "Marty McFly", "tools_used": ["agent_run"]},
            True,
            explanation_summary="Book of business produced with notifications and flags",
        )
    except Exception as e:
        _emit_agent_one_event(
            run_id,
            {"customer_identifier_scope": "Marty McFly", "tools_used": ["agent_run"]},
            False,
            error_message=str(e),
        )
        raise


if __name__ == "__main__":
    main()
